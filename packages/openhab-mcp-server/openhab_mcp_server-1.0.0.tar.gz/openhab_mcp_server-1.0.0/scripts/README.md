# Build and Installation Scripts

This directory contains scripts for building, installing, verifying, and releasing the openHAB MCP Server package.

## Scripts

### `build.py`
Builds wheel and source distributions for the package.

```bash
python scripts/build.py
```

This script:
- Cleans previous build artifacts
- Installs build dependencies
- Creates wheel and source distributions in `dist/`
- Lists the generated files

### `install_verify.py`
Verifies package installation in a clean virtual environment.

```bash
python scripts/install_verify.py
```

This script:
- Creates a temporary virtual environment
- Installs the built wheel package
- Tests package import functionality
- Verifies CLI and MCP server entry points
- Cleans up automatically

**Note**: Run `build.py` first to generate the wheel file.

### `dev_install.py`
Sets up the development environment with editable installation.

```bash
python scripts/dev_install.py
```

This script:
- Installs the package in editable mode (`pip install -e .`)
- Installs all development dependencies (dev, test, lint)
- Verifies the installation
- Provides next steps for development

### `release.py`
Automates the complete release process for publishing to PyPI.

```bash
# Dry run (recommended first)
python scripts/release.py 1.0.1 --dry-run

# Release to TestPyPI
python scripts/release.py 1.0.1 --test-pypi

# Release to PyPI
python scripts/release.py 1.0.1
```

**Options:**
- `--dry-run`: Perform all steps except publishing and tagging
- `--test-pypi`: Publish to TestPyPI instead of PyPI
- `--skip-tests`: Skip running the test suite
- `--skip-validation`: Skip environment validation

This script:
- Validates environment and git status
- Updates version in pyproject.toml
- Runs complete test suite (unit tests, type checking, linting)
- Builds and validates package
- Tests installation in clean environment
- Creates git tag and commits changes
- Publishes to PyPI or TestPyPI
- Pushes changes to git repository

## Usage Workflow

### For Development
```bash
# Set up development environment
python scripts/dev_install.py

# Set environment variables
export OPENHAB_URL=http://localhost:8080
export OPENHAB_TOKEN=your-api-token

# Run tests
python -m pytest tests/

# Start the server
openhab-mcp-server
```

### For Distribution
```bash
# Build the package
python scripts/build.py

# Verify the build
python scripts/install_verify.py

# Upload to PyPI (manual step)
python -m twine upload dist/*
```

### For Releases
```bash
# Test the release process
python scripts/release.py 1.0.1 --dry-run

# Release to TestPyPI first
python scripts/release.py 1.0.1 --test-pypi

# If everything looks good, release to PyPI
python scripts/release.py 1.0.1
```

## Requirements

- Python 3.8+
- pip
- Virtual environment support (venv module)

## Environment Variables

The following environment variables should be set for proper operation:

- `OPENHAB_URL`: URL of your openHAB server (default: http://localhost:8080)
- `OPENHAB_TOKEN`: API token for openHAB authentication
- `OPENHAB_TIMEOUT`: Request timeout in seconds (default: 30)