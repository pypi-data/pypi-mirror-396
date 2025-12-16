# Changelog

All notable changes to the openHAB MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of openHAB MCP Server
- MCP tools for item control, thing management, and rule operations
- MCP resources for documentation and system state access
- Comprehensive security features with input validation
- Property-based testing for correctness validation
- CLI interface for easy server execution
- Python package distribution support

### Security
- Input validation and sanitization for all parameters
- Secure authentication token handling
- Protection against injection attacks
- Security event logging
- Credential protection in logs and responses

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