# openHAB MCP Server

A Model Context Protocol (MCP) server that bridges AI assistants with openHAB home automation systems.

## Overview

This MCP server provides structured access to openHAB's documentation, APIs, and operational capabilities, enabling AI assistants to help users configure, troubleshoot, and optimize their openHAB installations.

## Features

- **Documentation Access**: Searchable openHAB documentation and tutorials
- **System Monitoring**: Real-time item states, thing status, and system health
- **Configuration Management**: Item definitions, thing configurations, and rule management
- **Troubleshooting Support**: Log analysis, binding diagnostics, and common issue resolution
- **Addon Management**: Install, uninstall, and configure openHAB addons
- **Script Execution**: Secure Python script execution with openHAB API access
- **Link Management**: Create and manage connections between items and channels
- **Transformation Management**: Configure and test data transformations
- **Main UI Management**: Create and manage openHAB Main UI pages and widgets
- **Docker Support**: Containerized deployment with health monitoring

## Installation

### For End Users (Recommended)

Install directly from PyPI using pip:

```bash
pip install openhab-mcp-server
```

### Docker Installation

The openHAB MCP Server provides comprehensive Docker support for containerized deployments:

#### Quick Start
```bash
# Pull and run the latest image
docker pull gbicskei/openhab-mcp-server:latest

# Basic deployment
docker run -d \
  --name openhab-mcp-server \
  -e OPENHAB_URL=http://your-openhab-host:8080 \
  -e OPENHAB_TOKEN=your-api-token \
  -p 8000:8000 \
  gbicskei/openhab-mcp-server:latest
```

#### Production Deployment
```bash
# Production deployment with full configuration
docker run -d \
  --name openhab-mcp-server \
  --restart unless-stopped \
  -e OPENHAB_URL=http://openhab:8080 \
  -e OPENHAB_TOKEN=your-api-token \
  -e SCRIPT_SECURITY_LEVEL=STRICT \
  -e METRICS_ENABLED=true \
  -p 8000:8000 \
  -v ./config:/app/config:ro \
  -v ./logs:/app/logs \
  gbicskei/openhab-mcp-server:latest
```

#### Docker Compose
```bash
# Use docker-compose for multi-service deployment
docker-compose up -d

# View logs
docker-compose logs -f openhab-mcp-server
```

#### Container Features
- **Security**: Non-root execution, minimal Alpine Linux base
- **Monitoring**: Built-in health checks and Prometheus metrics
- **Orchestration**: Kubernetes and Docker Swarm support
- **Multi-Architecture**: AMD64, ARM64, and ARM/v7 support

See the [Docker Deployment](#docker-deployment) section for comprehensive deployment options.

### For Development

1. Clone the repository:
   ```bash
   git clone https://github.com/gbicskei/openhab-mcp-server.git
   cd openhab-mcp-server
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

   Or install dependencies manually:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Set the following environment variables:

- `OPENHAB_URL`: openHAB server URL (default: http://localhost:8080)
- `OPENHAB_TOKEN`: API token for authentication (required)
- `OPENHAB_TIMEOUT`: Request timeout in seconds (default: 30)
- `LOG_LEVEL`: Logging level (default: INFO)

## Usage

### openHAB API Token Setup

To get an API token from openHAB:

1. Open the openHAB web interface (usually http://localhost:8080)
2. Go to Settings → API Security
3. Create a new API token
4. Copy the token and set it as the `OPENHAB_TOKEN` environment variable

### Running the MCP Server

#### Using the CLI (Recommended)

After installation, you can run the server using the command-line interface:

```bash
openhab-mcp-server
```

You can also specify configuration options:

```bash
openhab-mcp-server --host localhost --port 8000
```

#### Using Python Module

If you installed from source or want to run directly:

```bash
python -m openhab_mcp_server.cli
```

For development (from source directory):

```bash
python -m src.openhab_mcp_server.cli
```

### MCP Client Integration

To integrate with MCP clients, add the server to your client configuration:

#### For Installed Package (Recommended)

After installing with `pip install openhab-mcp-server`, add to your MCP client configuration:

```json
{
  "mcpServers": {
    "openhab": {
      "command": "openhab-mcp-server",
      "env": {
        "OPENHAB_URL": "http://localhost:8080",
        "OPENHAB_TOKEN": "your-api-token",
        "OPENHAB_TIMEOUT": "30",
        "LOG_LEVEL": "INFO"
      },
      "disabled": false
    }
  }
}
```

#### For Development Installation

If you're developing or running from source, add to your MCP client configuration:

```json
{
  "mcpServers": {
    "openhab": {
      "command": "python",
      "args": ["-m", "openhab_mcp_server.cli"],
      "env": {
        "OPENHAB_URL": "http://localhost:8080",
        "OPENHAB_TOKEN": "your-api-token",
        "OPENHAB_TIMEOUT": "30",
        "LOG_LEVEL": "INFO"
      },
      "disabled": false
    }
  }
}
```

## Available Tools

### Item Control
- `get_item_state(name)`: Get current state of an item
- `send_item_command(name, command)`: Send command to an item
- `list_items(item_type?)`: List all items or filter by type

### Thing Management
- `get_thing_status(uid)`: Get thing status and configuration
- `update_thing_config(uid, configuration)`: Update thing configuration
- `discover_things(binding_id)`: Discover new things for a binding
- `list_things()`: List all things

### Rule Operations
- `list_rules(status_filter?)`: List automation rules
- `execute_rule(uid)`: Execute a rule manually
- `create_rule(rule_definition)`: Create a new rule

### System Information
- `get_system_info()`: Get openHAB system information
- `list_bindings()`: List installed bindings
- `get_health_status()`: Get system health status
- `get_diagnostics()`: Get comprehensive diagnostics
- `get_metrics_summary()`: Get performance metrics

### Addon Management
- `list_addons(addon_type?)`: List available and installed addons
- `install_addon(addon_id)`: Install an addon from the registry
- `uninstall_addon(addon_id)`: Uninstall an installed addon
- `update_addon_config(addon_id, configuration)`: Update addon configuration

### Script Execution
- `execute_script(script_code, context?)`: Execute Python scripts securely
- `validate_script(script_code)`: Validate script syntax and security

### Link Management
- `list_links(item_name?, channel_uid?)`: List item-channel links
- `create_link(item_name, channel_uid, configuration?)`: Create new links
- `update_link(item_name, channel_uid, configuration)`: Update link configuration
- `delete_link(item_name, channel_uid)`: Remove links

### Transformation Management
- `list_transformations()`: List available transformation addons
- `create_transformation(type, configuration)`: Create transformations
- `test_transformation(transformation_id, sample_data)`: Test transformations
- `update_transformation(transformation_id, configuration)`: Update transformations
- `get_transformation_usage(transformation_id)`: Get transformation usage

### Main UI Management
- `list_ui_pages()`: List Main UI pages
- `create_ui_page(page_config)`: Create new UI pages
- `update_ui_widget(page_id, widget_id, properties)`: Update widgets
- `manage_ui_layout(page_id, layout_config)`: Manage page layouts
- `export_ui_config(page_ids?)`: Export UI configuration

### Documentation and Examples
- `get_operation_examples(operation_type?)`: Get usage examples
- `get_api_documentation(section?)`: Get API documentation

## Available Resources

### Documentation
- `openhab://docs/setup`: Setup and installation guide
- `openhab://docs/configuration`: Configuration guide
- `openhab://docs/troubleshooting`: Troubleshooting guide
- `openhab://docs/search`: Documentation search functionality

### System State
- `openhab://system/status`: System status and health
- `openhab://system/items`: All configured items
- `openhab://system/things`: All configured things
- `openhab://system/bindings`: Binding status information
- `openhab://system/connectivity`: Connectivity status

### Diagnostics
- `openhab://diagnostics/health`: Health status and metrics
- `openhab://diagnostics/metrics`: Performance metrics
- `openhab://diagnostics/config`: Configuration validation

## Security Features

The MCP server includes comprehensive security:

- Input validation and sanitization for all parameters
- Secure authentication token handling
- Protection against injection attacks
- Security event logging
- Credential protection in logs and responses

### Script Execution Security

Script execution includes comprehensive security measures to protect the host system while providing safe access to openHAB functionality:

#### Security Architecture
- **Multi-Layer Defense**: Multiple security controls prevent system compromise
- **Sandboxed Environment**: Scripts run in an isolated Python environment with restricted capabilities
- **Resource Monitoring**: Real-time monitoring of CPU, memory, and execution time
- **Code Analysis**: Static analysis detects potentially dangerous code patterns
- **Audit Logging**: Complete execution history with security event tracking

#### Security Constraints
- **File System Isolation**: No access to host file system or directory traversal
- **Network Restrictions**: No direct network access except through openHAB API context
- **Process Isolation**: No subprocess execution or system command access
- **Module Control**: Only whitelisted Python modules available for import
- **Function Restrictions**: Dangerous built-in functions are disabled or restricted
- **Resource Limits**: Configurable execution time (default: 30s) and memory limits (default: 128MB)

#### Security Levels
- **STRICT**: Maximum security with minimal module access (recommended for production)
- **NORMAL**: Balanced security and functionality for development
- **PERMISSIVE**: Reduced restrictions for advanced use cases (use with caution)

#### Monitoring and Compliance
- **Real-time Monitoring**: Active monitoring of script execution and resource usage
- **Security Events**: Automatic detection and logging of security violations
- **Compliance Reporting**: Detailed audit trails for security compliance
- **Threat Detection**: Pattern matching for malicious code attempts

## Troubleshooting

### Connection Issues
1. Verify openHAB is running and accessible
2. Check the `OPENHAB_URL` environment variable
3. Ensure the API token is valid and has proper permissions
4. Check network connectivity and firewall settings

### Authentication Errors
1. Verify the `OPENHAB_TOKEN` is set correctly
2. Check that the token hasn't expired
3. Ensure the token has the necessary permissions in openHAB

### Performance Issues
1. Use `get_diagnostics()` to check system health
2. Use `get_metrics_summary()` to monitor performance
3. Adjust the `OPENHAB_TIMEOUT` if needed
4. Check openHAB server performance and logs

## Docker Deployment

### Quick Start with Docker

```bash
# Run with environment variables
docker run -d \
  --name openhab-mcp-server \
  -e OPENHAB_URL=http://your-openhab-host:8080 \
  -e OPENHAB_TOKEN=your-api-token \
  -p 8000:8000 \
  gbicskei/openhab-mcp-server:latest
```

### Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  openhab-mcp-server:
    image: gbicskei/openhab-mcp-server:latest
    container_name: openhab-mcp-server
    environment:
      - OPENHAB_URL=http://openhab:8080
      - OPENHAB_TOKEN=${OPENHAB_TOKEN}
      - OPENHAB_TIMEOUT=30
      - LOG_LEVEL=INFO
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    depends_on:
      - openhab

  openhab:
    image: openhab/openhab:latest
    container_name: openhab
    ports:
      - "8080:8080"
    volumes:
      - openhab_addons:/openhab/addons
      - openhab_conf:/openhab/conf
      - openhab_userdata:/openhab/userdata
    environment:
      - EXTRA_JAVA_OPTS=-Duser.timezone=America/New_York
    restart: unless-stopped

volumes:
  openhab_addons:
  openhab_conf:
  openhab_userdata:
```

Then run:

```bash
# Set your API token
export OPENHAB_TOKEN=your-api-token-here

# Start services
docker-compose up -d

# View logs
docker-compose logs -f openhab-mcp-server
```

### Advanced Docker Deployment

#### Production Docker Compose

For production deployments with enhanced security and monitoring:

```yaml
version: '3.8'

services:
  openhab-mcp-server:
    image: gbicskei/openhab-mcp-server:latest
    container_name: openhab-mcp-server
    environment:
      - OPENHAB_URL=http://openhab:8080
      - OPENHAB_TOKEN_FILE=/run/secrets/openhab_token
      - OPENHAB_TIMEOUT=30
      - LOG_LEVEL=INFO
      - MCP_MAX_CONNECTIONS=100
      - SCRIPT_TIMEOUT_SECONDS=30
      - SCRIPT_MEMORY_LIMIT_MB=128
      - SCRIPT_SECURITY_LEVEL=STRICT
      - HEALTH_CHECK_INTERVAL=30
      - METRICS_ENABLED=true
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
    secrets:
      - openhab_token
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    depends_on:
      openhab:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M

secrets:
  openhab_token:
    file: ./secrets/openhab_token.txt
```

#### Container Security Features

- **Non-root execution**: Runs as unprivileged user (UID 1000)
- **Read-only filesystem**: Root filesystem is read-only where possible
- **Minimal attack surface**: Alpine Linux base with minimal packages
- **Security scanning**: Regular vulnerability scanning and updates
- **Capability dropping**: Unnecessary Linux capabilities are dropped

#### Monitoring Endpoints

- **Health Check**: `http://localhost:8000/health`
- **Liveness Probe**: `http://localhost:8000/health/live`
- **Readiness Probe**: `http://localhost:8000/health/ready`
- **Metrics**: `http://localhost:8000/metrics` (Prometheus format)
- **Status**: `http://localhost:8000/status` (detailed system status)

### Configuration Options

#### Environment Variables

- `OPENHAB_URL`: openHAB server URL (required)
- `OPENHAB_TOKEN`: API token for authentication (required)
- `OPENHAB_TIMEOUT`: Request timeout in seconds (default: 30)
- `LOG_LEVEL`: Logging level (default: INFO)
- `MCP_HOST`: MCP server host (default: 0.0.0.0)
- `MCP_PORT`: MCP server port (default: 8000)

#### Volume Mounts

- `/app/config`: Configuration files (optional)
- `/app/logs`: Log files (optional)

#### Health Checks

The container includes built-in health checks:

- **Endpoint**: `http://localhost:8000/health`
- **Liveness**: `http://localhost:8000/health/live`
- **Readiness**: `http://localhost:8000/health/ready`
- **Metrics**: `http://localhost:8000/metrics`

### Container Orchestration

#### Kubernetes

Example Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openhab-mcp-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: openhab-mcp-server
  template:
    metadata:
      labels:
        app: openhab-mcp-server
    spec:
      containers:
      - name: openhab-mcp-server
        image: gbicskei/openhab-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENHAB_URL
          value: "http://openhab-service:8080"
        - name: OPENHAB_TOKEN
          valueFrom:
            secretKeyRef:
              name: openhab-secrets
              key: api-token
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: openhab-mcp-server-service
spec:
  selector:
    app: openhab-mcp-server
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
```

### Building Custom Images

To build your own Docker image:

```bash
# Clone the repository
git clone https://github.com/gbicskei/openhab-mcp-server.git
cd openhab-mcp-server

# Build the image
docker build -t my-openhab-mcp-server .

# Run your custom image
docker run -d \
  --name my-openhab-mcp-server \
  -e OPENHAB_URL=http://localhost:8080 \
  -e OPENHAB_TOKEN=your-token \
  -p 8000:8000 \
  my-openhab-mcp-server
```

## CLI Options

The `openhab-mcp-server` command supports the following options:

```bash
openhab-mcp-server --help
```

Available options:
- `--host`: Server host (default: localhost)
- `--port`: Server port (default: 8000)
- `--config`: Configuration file path
- `--version`: Show version information

## Development

### Setting Up Development Environment

1. Clone the repository and install in development mode:
   ```bash
   git clone https://github.com/gbicskei/openhab-mcp-server.git
   cd openhab-mcp-server
   pip install -e ".[dev]"
   ```

2. Set up pre-commit hooks (optional):
   ```bash
   pre-commit install
   ```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Type checking
mypy src/
```

### Testing

```bash
# Run tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run property-based tests
python -m pytest tests/test_property_*.py -v
```

### Building and Distribution

```bash
# Build the package
python -m build

# Install locally from built wheel
pip install dist/openhab_mcp_server-*.whl

# Verify installation
openhab-mcp-server --version
```

## Architecture

The server follows a layered architecture:

- **MCP Interface Layer**: Handles MCP protocol communication
- **Tool Layer**: Implements write operations (control items, modify configs)
- **Resource Layer**: Provides read-only access to system state and documentation
- **Utility Layer**: Shared services for HTTP client, configuration, and validation
- **openHAB Integration Layer**: Direct communication with openHAB REST API

## Support

For issues, questions, or contributions:

- **Issues**: Open an issue in the [GitHub repository](https://github.com/gbicskei/openhab-mcp-server/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/gbicskei/openhab-mcp-server/discussions) for questions and community support
- **Maintainer**: Gabor Bicskei (gbicskei@gmail.com)

## License

MIT License - see LICENSE file for details.