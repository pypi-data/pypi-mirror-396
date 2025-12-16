#!/usr/bin/env python3
"""
Build script for generating wheel and source distributions.
"""

import subprocess
import sys
import shutil
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("Cleaning build artifacts...")
    
    artifacts = [
        "build",
        "dist", 
        "src/openhab_mcp_server.egg-info",
        "*.egg-info"
    ]
    
    for artifact in artifacts:
        path = Path(artifact)
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed directory: {path}")
            else:
                path.unlink()
                print(f"Removed file: {path}")


def build_package():
    """Build wheel and source distributions."""
    print("\n" + "="*50)
    print("Building openHAB MCP Server Package")
    print("="*50)
    
    # Clean previous builds
    clean_build_artifacts()
    
    # Install build dependencies
    if not run_command([
        sys.executable, "-m", "pip", "install", "--upgrade", 
        "build", "wheel", "setuptools", "setuptools-scm"
    ], "Installing build dependencies"):
        return False
    
    # Build the package
    if not run_command([
        sys.executable, "-m", "build"
    ], "Building package distributions"):
        return False
    
    # List built files
    dist_dir = Path("dist")
    if dist_dir.exists():
        print(f"\n✓ Built distributions in {dist_dir}:")
        for file in dist_dir.iterdir():
            print(f"  - {file.name} ({file.stat().st_size} bytes)")
    
    print("\n✓ Package build completed successfully!")
    return True


def main():
    """Main build function."""
    if not build_package():
        sys.exit(1)


if __name__ == "__main__":
    main()