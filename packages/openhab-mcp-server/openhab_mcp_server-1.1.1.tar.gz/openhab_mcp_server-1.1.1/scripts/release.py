#!/usr/bin/env python3
"""
Release script for openHAB MCP Server.

This script helps automate the release process by:
1. Validating the current state
2. Building the package
3. Running tests
4. Creating git tags
5. Publishing to PyPI
"""

import argparse
import subprocess
import sys
from pathlib import Path
import re
import json


def run_command(cmd, check=True, capture_output=False):
    """Run a shell command."""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd, shell=True, check=check, capture_output=capture_output, text=True
    )
    if capture_output:
        return result.stdout.strip()
    return result.returncode == 0


def get_current_version():
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")
    
    content = pyproject_path.read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Version not found in pyproject.toml")
    
    return match.group(1)


def update_version(new_version):
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    
    # Update version
    content = re.sub(
        r'version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        content
    )
    
    pyproject_path.write_text(content)
    print(f"Updated version to {new_version}")


def validate_environment():
    """Validate that the environment is ready for release."""
    print("Validating environment...")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        raise FileNotFoundError("Not in project root (pyproject.toml not found)")
    
    # Check if git is clean
    result = subprocess.run(
        ["git", "status", "--porcelain"], 
        capture_output=True, text=True
    )
    if result.stdout.strip():
        raise RuntimeError("Git working directory is not clean")
    
    # Check if we're on main branch
    branch = run_command("git branch --show-current", capture_output=True)
    if branch != "main":
        print(f"Warning: Not on main branch (currently on {branch})")
    
    print("Environment validation passed")


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    
    # Run unit tests
    if not run_command("python -m pytest tests/ -v", check=False):
        raise RuntimeError("Unit tests failed")
    
    # Run type checking
    if not run_command("mypy src/", check=False):
        raise RuntimeError("Type checking failed")
    
    # Run linting
    if not run_command("ruff check src/ tests/", check=False):
        raise RuntimeError("Linting failed")
    
    print("All tests passed")


def build_package():
    """Build the package."""
    print("Building package...")
    
    # Clean previous builds
    run_command("rm -rf dist/ build/ src/*.egg-info/")
    
    # Build package
    if not run_command("python -m build"):
        raise RuntimeError("Package build failed")
    
    # Check package
    if not run_command("python -m twine check dist/*"):
        raise RuntimeError("Package check failed")
    
    print("Package built successfully")


def test_installation():
    """Test package installation."""
    print("Testing package installation...")
    
    # Create test environment
    run_command("python -m venv test-env")
    
    try:
        # Install package
        if sys.platform == "win32":
            pip_cmd = "test-env\\Scripts\\pip"
            python_cmd = "test-env\\Scripts\\python"
        else:
            pip_cmd = "test-env/bin/pip"
            python_cmd = "test-env/bin/python"
        
        # Find wheel file
        wheel_files = list(Path("dist").glob("*.whl"))
        if not wheel_files:
            raise FileNotFoundError("No wheel file found in dist/")
        
        wheel_file = wheel_files[0]
        
        # Install and test
        run_command(f"{pip_cmd} install {wheel_file}")
        run_command(f"{python_cmd} -c 'import openhab_mcp_server; print(\"Import successful\")'")
        
        print("Package installation test passed")
    
    finally:
        # Cleanup
        run_command("rm -rf test-env", check=False)


def create_git_tag(version):
    """Create git tag for the release."""
    print(f"Creating git tag v{version}...")
    
    # Add changes
    run_command("git add .")
    run_command(f'git commit -m "Release version {version}"')
    
    # Create tag
    run_command(f"git tag v{version}")
    
    print(f"Created tag v{version}")


def publish_package(test_pypi=False):
    """Publish package to PyPI."""
    if test_pypi:
        print("Publishing to TestPyPI...")
        repository = "--repository testpypi"
    else:
        print("Publishing to PyPI...")
        repository = ""
    
    if not run_command(f"python -m twine upload {repository} dist/*"):
        raise RuntimeError("Package upload failed")
    
    print("Package published successfully")


def main():
    parser = argparse.ArgumentParser(description="Release openHAB MCP Server")
    parser.add_argument("version", help="New version number (e.g., 1.0.1)")
    parser.add_argument("--test-pypi", action="store_true", 
                       help="Publish to TestPyPI instead of PyPI")
    parser.add_argument("--skip-tests", action="store_true",
                       help="Skip running tests")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip environment validation")
    parser.add_argument("--dry-run", action="store_true",
                       help="Perform all steps except publishing and tagging")
    
    args = parser.parse_args()
    
    try:
        # Validate version format
        if not re.match(r'^\d+\.\d+\.\d+(?:[a-z]+\d*)?$', args.version):
            raise ValueError("Invalid version format. Use semantic versioning (e.g., 1.0.1)")
        
        current_version = get_current_version()
        print(f"Current version: {current_version}")
        print(f"New version: {args.version}")
        
        if not args.skip_validation:
            validate_environment()
        
        # Update version
        update_version(args.version)
        
        if not args.skip_tests:
            run_tests()
        
        build_package()
        test_installation()
        
        if not args.dry_run:
            create_git_tag(args.version)
            publish_package(test_pypi=args.test_pypi)
            
            # Push changes
            run_command("git push origin main")
            run_command(f"git push origin v{args.version}")
            
            print(f"Release {args.version} completed successfully!")
        else:
            print("Dry run completed successfully!")
            print("To complete the release, run without --dry-run")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()