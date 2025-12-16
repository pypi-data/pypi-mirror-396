# Changelog

All notable changes to the openHAB MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.1] - 2024-12-13

### Fixed
- Updated CLI version display to show correct version number (1.1.1)

## [1.1.0] - 2024-12-13

### Added
- Comprehensive VSCode integration documentation and configuration
- Claude Desktop integration guide with step-by-step setup instructions
- Pre-configured VSCode workspace settings for optimal development experience
- Debug configurations for MCP server and test debugging
- Task automation for build, test, and quality checks
- VSCode extensions recommendations for Python and MCP development
- Complete troubleshooting guide for VSCode integration issues
- Multiple openHAB instance configuration examples
- Security best practices for Claude Desktop integration
- Advanced configuration options for remote openHAB servers

### Documentation
- Enhanced README with VSCode and Claude Desktop setup sections
- Detailed configuration examples for different deployment scenarios
- Natural language interaction examples for Claude Desktop
- Comprehensive troubleshooting guides for common integration issues
- Security considerations and best practices documentation

### Infrastructure
- VSCode workspace configuration files (.vscode/settings.json, launch.json, tasks.json)
- Extensions recommendations file for automatic VSCode setup
- Improved development workflow with automated code quality tools

## [1.0.0] - 2024-01-15

### Added
- Model Context Protocol server implementation
- openHAB REST API integration with async HTTP client
- Item control tools (get state, send commands, list items)
- Thing management tools (status, configuration, discovery)
- Rule operations tools (list, execute, create rules)
- Documentation resources with search functionality
- System state resources for monitoring
- Comprehensive error handling and timeout management
- Structured logging and diagnostics
- Configuration management via environment variables
- MCP server registration for Kiro integration
- Type hints and Pydantic models for data validation
- Async/await patterns for all API operations
- Security features for authentication and input validation
- Property-based testing with Hypothesis
- Unit tests for all components
- CLI interface with argument parsing
- Python packaging with setuptools and pyproject.toml
- Distribution support for PyPI publishing

### Documentation
- Comprehensive README with installation and usage instructions
- Configuration guide for different deployment scenarios
- Distribution and publishing documentation
- API documentation for all tools and resources
- Development setup and contribution guidelines

### Infrastructure
- GitHub Actions workflow for automated publishing
- Pre-commit hooks for code quality
- Comprehensive test suite with pytest
- Code formatting with Black and linting with Ruff
- Type checking with mypy
- Package build and verification scripts