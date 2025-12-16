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

### Claude Desktop Integration

The openHAB MCP Server integrates seamlessly with Claude Desktop, allowing you to control and monitor your openHAB system directly through conversations with Claude.

#### Prerequisites

1. **Install Claude Desktop**: Download from [Claude.ai](https://claude.ai/download)
2. **Install openHAB MCP Server**:
   ```bash
   pip install openhab-mcp-server
   ```
3. **Get openHAB API Token**: Follow the [openHAB API Token Setup](#openhab-api-token-setup) section above

#### Configuration Steps

1. **Locate Claude Desktop Configuration File**:

   **Windows**:
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

   **macOS**:
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

   **Linux**:
   ```
   ~/.config/Claude/claude_desktop_config.json
   ```

2. **Create or Edit Configuration File**:

   If the file doesn't exist, create it. Add the openHAB MCP Server configuration:

   ```json
   {
     "mcpServers": {
       "openhab": {
         "command": "openhab-mcp-server",
         "env": {
           "OPENHAB_URL": "http://localhost:8080",
           "OPENHAB_TOKEN": "your-openhab-api-token-here",
           "LOG_LEVEL": "INFO"
         }
       }
     }
   }
   ```

3. **Replace Configuration Values**:
   - `OPENHAB_URL`: Your openHAB server URL (e.g., `http://192.168.1.100:8080`)
   - `OPENHAB_TOKEN`: Your openHAB API token from the setup step

4. **Restart Claude Desktop**: Close and reopen Claude Desktop to load the new configuration

#### Verification

1. **Check MCP Server Status**:
   Start a new conversation in Claude Desktop and ask:
   ```
   Can you check my openHAB system status?
   ```

2. **Test Basic Functionality**:
   ```
   List all my openHAB items
   ```
   ```
   What's the current state of my living room lights?
   ```

#### Advanced Configuration

For more advanced setups, you can customize the configuration:

```json
{
  "mcpServers": {
    "openhab": {
      "command": "openhab-mcp-server",
      "env": {
        "OPENHAB_URL": "http://your-openhab-server:8080",
        "OPENHAB_TOKEN": "your-api-token",
        "OPENHAB_TIMEOUT": "30",
        "LOG_LEVEL": "INFO",
        "SCRIPT_SECURITY_LEVEL": "STRICT"
      }
    }
  }
}
```

#### Remote openHAB Server

If your openHAB server is on a different machine:

```json
{
  "mcpServers": {
    "openhab": {
      "command": "openhab-mcp-server",
      "env": {
        "OPENHAB_URL": "http://192.168.1.100:8080",
        "OPENHAB_TOKEN": "your-api-token",
        "OPENHAB_TIMEOUT": "60"
      }
    }
  }
}
```

#### Multiple openHAB Instances

You can configure multiple openHAB servers:

```json
{
  "mcpServers": {
    "openhab-main": {
      "command": "openhab-mcp-server",
      "env": {
        "OPENHAB_URL": "http://main-house:8080",
        "OPENHAB_TOKEN": "main-house-token"
      }
    },
    "openhab-garage": {
      "command": "openhab-mcp-server",
      "env": {
        "OPENHAB_URL": "http://garage:8080",
        "OPENHAB_TOKEN": "garage-token"
      }
    }
  }
}
```

#### What You Can Do with Claude

Once configured, you can interact with your openHAB system through natural language:

**System Monitoring**:
- "What's the status of my smart home system?"
- "Show me all devices that are offline"
- "What's the temperature in the living room?"

**Device Control**:
- "Turn on the kitchen lights"
- "Set the thermostat to 72 degrees"
- "Close all the blinds"

**Automation Management**:
- "List all my automation rules"
- "Show me rules that aren't working"
- "Create a rule to turn off lights at midnight"

**Troubleshooting**:
- "Why isn't my motion sensor working?"
- "Check the connectivity of my Zigbee devices"
- "Show me recent error logs"

**Configuration**:
- "Add a new switch item called 'Garden Lights'"
- "Link my new dimmer to the dining room channel"
- "Install the Astro binding"

#### Troubleshooting Claude Desktop Integration

**MCP Server Not Loading**:
1. Check the configuration file path and syntax
2. Verify the `openhab-mcp-server` command is in your PATH:
   ```bash
   openhab-mcp-server --version
   ```
3. Check Claude Desktop logs (usually in the same directory as the config file)

**Connection Issues**:
1. Verify openHAB is accessible from your machine:
   ```bash
   curl http://localhost:8080/rest/items
   ```
2. Test the API token:
   ```bash
   curl -H "Authorization: Bearer your-token" http://localhost:8080/rest/items
   ```

**Permission Errors**:
1. Ensure the API token has sufficient permissions in openHAB
2. Check openHAB logs for authentication errors

**Performance Issues**:
1. Increase the timeout value in configuration
2. Check network connectivity to openHAB server
3. Monitor openHAB server performance

#### Security Considerations

- **API Token Security**: Store your API token securely and don't share it
- **Network Security**: Use HTTPS for remote openHAB connections when possible
- **Access Control**: Configure openHAB API security settings appropriately
- **Firewall**: Ensure proper firewall rules for openHAB access

#### Example Configuration File

Complete example `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openhab": {
      "command": "openhab-mcp-server",
      "env": {
        "OPENHAB_URL": "http://localhost:8080",
        "OPENHAB_TOKEN": "oh.myserver.1234567890abcdef",
        "OPENHAB_TIMEOUT": "30",
        "LOG_LEVEL": "INFO",
        "SCRIPT_SECURITY_LEVEL": "STRICT"
      }
    }
  },
  "globalShortcut": "Ctrl+Shift+Space"
}
```

This configuration enables Claude Desktop to communicate with your openHAB system, providing a powerful natural language interface for home automation control and monitoring.

### VSCode Integration

The openHAB MCP Server integrates seamlessly with Visual Studio Code for development and testing. This section covers setting up the MCP server within VSCode environments.

#### MCP Client Configuration

You can configure the openHAB MCP Server in any MCP-compatible client:

1. **Install the Package** (recommended for stable usage):
   ```bash
   pip install openhab-mcp-server
   ```

2. **Configure MCP Server** in your MCP client configuration file:
   ```json
   {
     "mcpServers": {
       "openhab": {
         "command": "openhab-mcp-server",
         "env": {
           "OPENHAB_URL": "http://localhost:8080",
           "OPENHAB_TOKEN": "your-api-token-here",
           "LOG_LEVEL": "INFO"
         },
         "disabled": false
       }
     }
   }
   ```

3. **For Development** (when working on the MCP server itself):
   ```json
   {
     "mcpServers": {
       "openhab-dev": {
         "command": "python",
         "args": ["-m", "openhab_mcp_server.cli"],
         "cwd": "${workspaceFolder}",
         "env": {
           "OPENHAB_URL": "http://localhost:8080",
           "OPENHAB_TOKEN": "your-api-token-here",
           "LOG_LEVEL": "DEBUG"
         },
         "disabled": false
       }
     }
   }
   ```

#### VSCode Development Setup

For VSCode development, the project includes pre-configured settings:

- **Essential Extensions**: Python, Black formatter, Ruff linter, MyPy type checker
- **Debugging Configuration**: Launch configurations for MCP server and tests
- **Code Quality Integration**: Automatic formatting, linting, and type checking
- **Testing Setup**: Pytest integration with Test Explorer
- **Task Automation**: Build, test, and quality check tasks

**Quick VSCode Setup**:
```bash
# Install recommended extensions
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension charliermarsh.ruff
code --install-extension ms-python.mypy-type-checker

# Open project in VSCode
code .
```

#### Testing MCP Server in VSCode

1. **Using Debug Configuration**:
   - Open the project in VSCode
   - Go to Run and Debug (Ctrl+Shift+D)
   - Select "Run MCP Server" configuration
   - Set breakpoints and start debugging (F5)

2. **Using Integrated Terminal**:
   ```bash
   # Activate virtual environment
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   
   # Run MCP server with debug logging
   OPENHAB_URL=http://localhost:8080 OPENHAB_TOKEN=your-token LOG_LEVEL=DEBUG python -m openhab_mcp_server.cli
   ```

3. **Testing with MCP Client**:
   ```bash
   # Test MCP server connectivity
   curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -d '{"method": "initialize", "params": {}}'
   ```

#### Environment Configuration

Create a `.env` file in your project root for development:

```env
# openHAB Configuration
OPENHAB_URL=http://localhost:8080
OPENHAB_TOKEN=your-development-token-here
OPENHAB_TIMEOUT=30

# MCP Server Configuration
MCP_HOST=localhost
MCP_PORT=8000
LOG_LEVEL=DEBUG

# Development Settings
SCRIPT_SECURITY_LEVEL=NORMAL
METRICS_ENABLED=true
```

#### Debugging MCP Communication

1. **Enable Debug Logging**:
   ```bash
   export LOG_LEVEL=DEBUG
   python -m openhab_mcp_server.cli
   ```

2. **Monitor MCP Messages**:
   - Use VSCode's integrated terminal to view real-time logs
   - Set breakpoints in MCP tool implementations
   - Use the Debug Console to inspect variables and state

3. **Test Individual Tools**:
   ```python
   # In VSCode Python REPL or debug console
   from openhab_mcp_server.tools.items import get_item_state
   
   # Test tool directly
   result = await get_item_state("MyItem")
   print(result)
   ```

#### Common VSCode Workflows

1. **Development Cycle**:
   - Edit code with IntelliSense and type checking
   - Run tests automatically on save
   - Debug MCP server with breakpoints
   - Format and lint code on save

2. **Testing Workflow**:
   - Use Test Explorer to run specific tests
   - Debug failing tests with integrated debugger
   - View test coverage in editor

3. **Quality Assurance**:
   - Automatic code formatting with Black
   - Real-time linting with Ruff
   - Type checking with MyPy
   - Pre-commit hooks for quality gates

#### Troubleshooting VSCode Integration

**MCP Server Not Starting**:
- Check Python interpreter is correctly selected
- Verify virtual environment is activated
- Ensure all dependencies are installed: `pip install -e ".[dev]"`

**Import Errors**:
- Confirm package is installed in development mode
- Check PYTHONPATH includes project root
- Restart VSCode after installing packages

**Debugging Issues**:
- Verify launch configuration in `.vscode/launch.json`
- Check environment variables are set correctly
- Ensure openHAB server is accessible

**Performance Issues**:
- Exclude build directories in VSCode settings
- Disable unused extensions
- Use workspace-specific settings for large projects

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