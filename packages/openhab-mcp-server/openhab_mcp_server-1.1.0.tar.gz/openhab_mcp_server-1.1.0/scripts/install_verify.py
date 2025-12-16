#!/usr/bin/env python3
"""
Installation verification script for openHAB MCP Server.
"""

import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def run_command(cmd: list[str], description: str, cwd=None) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        print(f"✓ {description} completed successfully")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False, e.stderr


def verify_installation():
    """Verify package installation in a clean virtual environment."""
    print("\n" + "="*60)
    print("Verifying openHAB MCP Server Installation")
    print("="*60)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        venv_path = temp_path / "test_venv"
        
        print(f"Creating test virtual environment at {venv_path}")
        
        # Create virtual environment
        venv.create(venv_path, with_pip=True)
        
        # Determine python executable path
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
        
        # Upgrade pip
        success, _ = run_command([
            str(python_exe), "-m", "pip", "install", "--upgrade", "pip"
        ], "Upgrading pip in test environment")
        
        if not success:
            return False
        
        # Find the built wheel file
        dist_dir = Path("dist")
        wheel_files = list(dist_dir.glob("*.whl"))
        
        if not wheel_files:
            print("✗ No wheel file found in dist/ directory")
            print("Run the build script first: python scripts/build.py")
            return False
        
        wheel_file = wheel_files[0]  # Use the first wheel file
        print(f"Installing wheel: {wheel_file}")
        
        # Install the package
        success, _ = run_command([
            str(pip_exe), "install", str(wheel_file.absolute())
        ], f"Installing {wheel_file.name}")
        
        if not success:
            return False
        
        # Test package import
        success, output = run_command([
            str(python_exe), "-c", 
            "import openhab_mcp_server; print(f'Package version: {openhab_mcp_server.__version__}')"
        ], "Testing package import")
        
        if not success:
            return False
        
        # Test CLI entry point
        success, output = run_command([
            str(python_exe), "-m", "openhab_mcp_server.cli", "--help"
        ], "Testing CLI entry point")
        
        if not success:
            return False
        
        # Test MCP server entry point
        success, output = run_command([
            str(python_exe), "-c",
            "from openhab_mcp_server.server import main; print('MCP server entry point accessible')"
        ], "Testing MCP server entry point")
        
        if not success:
            return False
        
        print("\n✓ All installation verification tests passed!")
        return True


def main():
    """Main verification function."""
    if not verify_installation():
        print("\n✗ Installation verification failed!")
        sys.exit(1)
    
    print("\n🎉 Installation verification completed successfully!")


if __name__ == "__main__":
    main()