#!/usr/bin/env python3
"""
Development installation script for openHAB MCP Server.
"""

import subprocess
import sys
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


def install_development_environment():
    """Install the package in development mode with all dependencies."""
    print("\n" + "="*60)
    print("Setting up openHAB MCP Server Development Environment")
    print("="*60)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("✗ pyproject.toml not found. Please run this script from the project root.")
        return False
    
    # Upgrade pip and build tools
    if not run_command([
        sys.executable, "-m", "pip", "install", "--upgrade", 
        "pip", "setuptools", "wheel"
    ], "Upgrading pip and build tools"):
        return False
    
    # Install package in editable mode with all optional dependencies
    if not run_command([
        sys.executable, "-m", "pip", "install", "-e", ".[dev,test,lint]"
    ], "Installing package in editable mode with dev dependencies"):
        return False
    
    # Verify installation
    if not run_command([
        sys.executable, "-c", 
        "import openhab_mcp_server; print(f'Development installation successful')"
    ], "Verifying development installation"):
        return False
    
    # Test CLI
    if not run_command([
        sys.executable, "-m", "openhab_mcp_server.cli", "--help"
    ], "Testing CLI functionality"):
        return False
    
    print("\n✓ Development environment setup completed!")
    print("\nNext steps:")
    print("1. Set environment variables:")
    print("   export OPENHAB_URL=http://localhost:8080")
    print("   export OPENHAB_TOKEN=your-api-token")
    print("2. Run tests: python -m pytest tests/")
    print("3. Start the MCP server: openhab-mcp-server")
    
    return True


def main():
    """Main installation function."""
    if not install_development_environment():
        print("\n✗ Development installation failed!")
        sys.exit(1)
    
    print("\n🎉 Development environment ready!")


if __name__ == "__main__":
    main()