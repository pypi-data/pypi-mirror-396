# Distribution and Publishing Guide

This document describes the build, release, and publishing process for the openHAB MCP Server.

## Overview

The openHAB MCP Server is distributed through multiple channels:

1. **Python Package**: Available on PyPI for pip installation
2. **Docker Images**: Available on Docker Hub for containerized deployment
3. **Source Code**: Available on GitHub for development and building

This document covers all distribution methods.

## Prerequisites

### Required Tools

#### For Python Package Distribution
- Python 3.8 or higher
- `build` package for building distributions
- `twine` package for uploading to PyPI
- `setuptools` and `wheel` for packaging

Install build tools:

```bash
pip install build twine setuptools wheel
```

#### For Docker Distribution
- Docker Engine 20.10 or higher
- Docker Buildx for multi-platform builds
- Docker Hub account for publishing

Install Docker tools:

```bash
# Install Docker (platform-specific)
# Enable buildx
docker buildx create --use
```

### PyPI Account

For publishing to PyPI, you'll need:

1. A PyPI account (https://pypi.org/account/register/)
2. API token for authentication (recommended over username/password)

## Build Process

### 1. Prepare for Build

Ensure your environment is clean:

```bash
# Clean previous builds
rm -rf dist/ build/ src/*.egg-info/

# Ensure you're in the project root
ls pyproject.toml  # Should exist
```

### 2. Build Distributions

Build both wheel and source distributions:

```bash
python -m build
```

This creates:
- `dist/openhab_mcp_server-*.whl` (wheel distribution)
- `dist/openhab-mcp-server-*.tar.gz` (source distribution)

### 3. Verify Build

Check the built distributions:

```bash
# List built files
ls -la dist/

# Check wheel contents
python -m zipfile -l dist/openhab_mcp_server-*.whl

# Check source distribution contents
tar -tzf dist/openhab-mcp-server-*.tar.gz
```

### 4. Test Installation

Test the built package in a clean environment:

```bash
# Create test environment
python -m venv test-env
source test-env/bin/activate  # Linux/Mac
# or
test-env\Scripts\activate  # Windows

# Install from wheel
pip install dist/openhab_mcp_server-*.whl

# Test CLI
openhab-mcp-server --version

# Test import
python -c "import openhab_mcp_server; print('Import successful')"

# Cleanup
deactivate
rm -rf test-env
```

## Release Process

### 1. Version Management

Update version in `pyproject.toml`:

```toml
[project]
version = "1.0.1"  # Update this
```

### 2. Update Changelog

Create or update `CHANGELOG.md`:

```markdown
# Changelog

## [1.0.1] - 2024-01-15

### Added
- New feature description

### Changed
- Changed feature description

### Fixed
- Bug fix description

### Removed
- Removed feature description
```

### 3. Create Git Tag

Tag the release:

```bash
git add .
git commit -m "Release version 1.0.1"
git tag v1.0.1
git push origin main
git push origin v1.0.1
```

### 4. Build Release

Build the release distributions:

```bash
# Clean previous builds
rm -rf dist/ build/

# Build new distributions
python -m build

# Verify build
python -m twine check dist/*
```

## Publishing to PyPI

### 1. Test on TestPyPI (Recommended)

First, test on TestPyPI:

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ openhab-mcp-server
```

### 2. Publish to PyPI

Once tested, publish to the main PyPI:

```bash
python -m twine upload dist/*
```

### 3. Verify Publication

Check that the package is available:

```bash
# Install from PyPI
pip install openhab-mcp-server

# Verify version
openhab-mcp-server --version
```

## Automated Publishing (GitHub Actions)

### Setup

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    
    - name: Install build tools
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

### Required Secrets

Add to GitHub repository secrets:
- `PYPI_API_TOKEN`: Your PyPI API token

## Version Management Guidelines

### Semantic Versioning

Follow semantic versioning (semver.org):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backward compatible

### Pre-release Versions

For development versions:

- **Alpha**: `1.0.0a1`, `1.0.0a2`
- **Beta**: `1.0.0b1`, `1.0.0b2`
- **Release Candidate**: `1.0.0rc1`, `1.0.0rc2`

### Development Versions

For development snapshots:

- **Development**: `1.0.0.dev1`, `1.0.0.dev2`

## Quality Checks

### Pre-release Checklist

Before each release:

- [ ] All tests pass (`pytest tests/`)
- [ ] Code is formatted (`black src/ tests/`)
- [ ] Code is linted (`ruff check src/ tests/`)
- [ ] Type checking passes (`mypy src/`)
- [ ] Documentation is updated
- [ ] Version is updated in `pyproject.toml`
- [ ] Changelog is updated
- [ ] Package builds successfully (`python -m build`)
- [ ] Package installs and works (`pip install dist/*.whl`)

### Automated Checks

Run all checks:

```bash
# Format and lint
black src/ tests/
ruff check src/ tests/ --fix

# Type checking
mypy src/

# Run tests
pytest tests/ -v

# Build and check
python -m build
python -m twine check dist/*
```

## Distribution Files

### What Gets Included

The distribution includes:

- Source code from `src/openhab_mcp_server/`
- `README.md`
- `LICENSE`
- `pyproject.toml`
- Package metadata

### What Gets Excluded

The distribution excludes:

- Tests (`tests/`)
- Development files (`.hypothesis/`, `__pycache__/`)
- Git files (`.git/`, `.gitignore`)
- IDE files (`.vscode/`, `.idea/`)
- Build artifacts (`build/`, `dist/`)

### Customizing Distribution

Edit `MANIFEST.in` to control what gets included:

```
include README.md
include LICENSE
include pyproject.toml
recursive-include src/openhab_mcp_server *.py *.typed
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
exclude .hypothesis
exclude tests
```

## Troubleshooting

### Common Build Issues

1. **Missing files in distribution**
   - Check `MANIFEST.in`
   - Verify `pyproject.toml` configuration

2. **Import errors after installation**
   - Check package structure
   - Verify `__init__.py` files exist

3. **CLI not working**
   - Check entry points in `pyproject.toml`
   - Verify CLI module exists

### Common Publishing Issues

1. **Authentication failed**
   - Check PyPI API token
   - Verify token permissions

2. **Package already exists**
   - Version already published
   - Increment version number

3. **Upload failed**
   - Check package size limits
   - Verify distribution format

## Docker Distribution

### Building Docker Images

#### 1. Build Local Image

Build for local testing:

```bash
# Build for current platform
docker build -t openhab-mcp-server:local .

# Test the image
docker run --rm \
  -e OPENHAB_URL=http://localhost:8080 \
  -e OPENHAB_TOKEN=test-token \
  openhab-mcp-server:local --version
```

#### 2. Multi-Platform Build

Build for multiple architectures:

```bash
# Create and use buildx builder
docker buildx create --name multiarch --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  --tag gbicskei/openhab-mcp-server:latest \
  --push .
```

#### 3. Build with Version Tags

Build with specific version tags:

```bash
# Set version
VERSION=1.0.1

# Build and tag
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  --tag gbicskei/openhab-mcp-server:latest \
  --tag gbicskei/openhab-mcp-server:${VERSION} \
  --tag gbicskei/openhab-mcp-server:v${VERSION} \
  --push .
```

### Docker Image Structure

The Docker image includes:

- **Base**: Alpine Linux (minimal footprint)
- **Python**: Python 3.11 runtime
- **Application**: openHAB MCP Server package
- **Health Checks**: Built-in health monitoring
- **Security**: Non-root user execution

### Publishing to Docker Hub

#### 1. Login to Docker Hub

```bash
docker login
```

#### 2. Tag Images

```bash
# Tag for Docker Hub
docker tag openhab-mcp-server:local gbicskei/openhab-mcp-server:latest
docker tag openhab-mcp-server:local gbicskei/openhab-mcp-server:1.0.1
```

#### 3. Push Images

```bash
# Push all tags
docker push gbicskei/openhab-mcp-server:latest
docker push gbicskei/openhab-mcp-server:1.0.1
```

### Automated Docker Publishing

#### GitHub Actions Workflow

Create `.github/workflows/docker.yml`:

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: docker.io
  IMAGE_NAME: gbicskei/openhab-mcp-server

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Docker Hub
      if: github.event_name != 'pull_request'
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=semver,pattern={{major}}
          type=raw,value=latest,enable={{is_default_branch}}

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        platforms: linux/amd64,linux/arm64,linux/arm/v7
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

#### Required Secrets

Add to GitHub repository secrets:
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password or access token

### Docker Image Testing

#### 1. Automated Testing

Test Docker images in CI:

```yaml
- name: Test Docker image
  run: |
    docker run --rm \
      -e OPENHAB_URL=http://localhost:8080 \
      -e OPENHAB_TOKEN=test-token \
      ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest \
      --version
```

#### 2. Security Scanning

Scan images for vulnerabilities:

```bash
# Install trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan image
trivy image gbicskei/openhab-mcp-server:latest
```

#### 3. Image Size Optimization

Monitor image size:

```bash
# Check image size
docker images gbicskei/openhab-mcp-server

# Analyze layers
docker history gbicskei/openhab-mcp-server:latest
```

### Docker Compose for Development

#### Development Compose File

Create `docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  openhab-mcp-server:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: openhab-mcp-server-dev
    environment:
      - OPENHAB_URL=http://openhab:8080
      - OPENHAB_TOKEN=${OPENHAB_TOKEN}
      - LOG_LEVEL=DEBUG
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src:ro
      - ./config:/app/config:ro
    depends_on:
      - openhab
    restart: unless-stopped

  openhab:
    image: openhab/openhab:4.1.0
    container_name: openhab-dev
    ports:
      - "8080:8080"
    volumes:
      - openhab_addons:/openhab/addons
      - openhab_conf:/openhab/conf
      - openhab_userdata:/openhab/userdata
    environment:
      - EXTRA_JAVA_OPTS=-Duser.timezone=UTC
    restart: unless-stopped

volumes:
  openhab_addons:
  openhab_conf:
  openhab_userdata:
```

#### Usage

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f openhab-mcp-server

# Stop environment
docker-compose -f docker-compose.dev.yml down
```

## Support

For issues with distribution or publishing:

1. **Python Package**: Check the [Python Packaging Guide](https://packaging.python.org/)
2. **PyPI**: Review [PyPI documentation](https://pypi.org/help/)
3. **Docker**: Check [Docker documentation](https://docs.docker.com/)
4. **Docker Hub**: Review [Docker Hub documentation](https://docs.docker.com/docker-hub/)
5. **Issues**: Open an issue in the [project repository](https://github.com/gbicskei/openhab-mcp-server/issues)
