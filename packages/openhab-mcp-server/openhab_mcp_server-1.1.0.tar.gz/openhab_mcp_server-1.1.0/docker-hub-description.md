# Docker Hub Repository Documentation

## Short Description
Model Context Protocol (MCP) server for openHAB home automation - bridges AI assistants with openHAB systems

## Full Description

# openHAB MCP Server

A comprehensive Model Context Protocol (MCP) server that bridges AI assistants with openHAB home automation systems, providing structured access to openHAB's documentation, APIs, and operational capabilities.

## Quick Start

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

## Key Features

- **Complete openHAB Integration**: Full access to items, things, rules, and system configuration
- **AI Assistant Ready**: Native MCP protocol support for seamless AI integration
- **Documentation Access**: Searchable openHAB documentation and tutorials
- **Real-time Monitoring**: Live system status, item states, and health metrics
- **Configuration Management**: Comprehensive item, thing, and rule management
- **Troubleshooting Support**: Advanced diagnostics and log analysis
- **Enterprise Security**: Multi-layer security with sandboxed script execution
- **Production Ready**: Optimized Docker deployment with health checks

## Architecture

- **Multi-stage Alpine build** for minimal size (~80MB)
- **Non-root execution** (UID 1000) for enhanced security
- **Built-in health checks** and Prometheus metrics
- **Tini init system** for proper signal handling
- **Comprehensive logging** with configurable levels

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENHAB_URL` | openHAB server URL | `http://localhost:8080` |
| `OPENHAB_TOKEN` | API authentication token | *Required* |
| `OPENHAB_TIMEOUT` | Request timeout (seconds) | `30` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MCP_HOST` | Server bind address | `0.0.0.0` |
| `MCP_PORT` | Server port | `8000` |

### Volume Mounts

- `/app/config` - Configuration files (optional)
- `/app/logs` - Log output directory (optional)
- `/app/data` - Persistent data storage (optional)

## Deployment Examples

### Docker Compose

```yaml
version: '3.8'
services:
  openhab-mcp-server:
    image: gbicskei/openhab-mcp-server:latest
    container_name: openhab-mcp-server
    environment:
      - OPENHAB_URL=http://openhab:8080
      - OPENHAB_TOKEN=${OPENHAB_TOKEN}
      - LOG_LEVEL=INFO
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    depends_on:
      - openhab

  openhab:
    image: openhab/openhab:latest
    ports:
      - "8080:8080"
    volumes:
      - openhab_conf:/openhab/conf
      - openhab_userdata:/openhab/userdata
    restart: unless-stopped

volumes:
  openhab_conf:
  openhab_userdata:
```

### Kubernetes

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
            path: /health
            port: 8000
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Available Tools & Resources

### Core Tools
- **Item Control**: Get/set item states, send commands
- **Thing Management**: Configure things, discover devices
- **Rule Operations**: Create, execute, and manage automation rules
- **System Monitoring**: Health checks, diagnostics, metrics

### Advanced Features
- **Addon Management**: Install/configure openHAB addons
- **Script Execution**: Secure Python scripting with openHAB API access
- **Link Management**: Item-channel link configuration
- **UI Management**: Main UI page and widget management
- **Transformation Tools**: Data transformation configuration and testing

### Resources
- **Documentation**: Searchable openHAB docs and tutorials
- **System State**: Real-time item states and thing status
- **Diagnostics**: Comprehensive system health and performance metrics

## Security Features

- **Multi-layer Security**: Input validation, authentication, and audit logging
- **Sandboxed Execution**: Secure Python script execution environment
- **Resource Monitoring**: CPU, memory, and execution time limits
- **Credential Protection**: Secure token handling and log sanitization
- **Security Levels**: Configurable security policies (STRICT/NORMAL/PERMISSIVE)

## Monitoring & Health

### Health Check Endpoints
- `/health` - Overall health status
- `/health/live` - Liveness probe
- `/health/ready` - Readiness probe
- `/metrics` - Prometheus metrics
- `/status` - Detailed system status

### Built-in Monitoring
- Real-time performance metrics
- Resource usage tracking
- Security event logging
- Comprehensive audit trails

## Integration

### MCP Client Configuration

Add to your MCP client (e.g., Claude Desktop, Cline):

```json
{
  "mcpServers": {
    "openhab": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "OPENHAB_URL=http://your-openhab:8080",
        "-e", "OPENHAB_TOKEN=your-token",
        "gbicskei/openhab-mcp-server:latest"
      ]
    }
  }
}
```

### API Token Setup

1. Open openHAB web interface (http://localhost:8080)
2. Go to Settings → API Security
3. Create new API token
4. Use token in `OPENHAB_TOKEN` environment variable

## Documentation

- **GitHub Repository**: [gbicskei/openhab-mcp-server](https://github.com/gbicskei/openhab-mcp-server)
- **Installation Guide**: See README.md for detailed setup instructions
- **API Documentation**: Comprehensive tool and resource documentation
- **Examples**: Usage examples and integration patterns

## Tags

Available image tags:
- `latest` - Latest stable release
- `1.0.0` - Specific version release
- `main` - Development branch (use with caution)

## Support

- **Issues**: [GitHub Issues](https://github.com/gbicskei/openhab-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/gbicskei/openhab-mcp-server/discussions)
- **Email**: gbicskei@gmail.com

## License

MIT License - Open source and free to use

---

**Perfect for**: Home automation enthusiasts, AI assistant developers, openHAB users seeking enhanced AI integration, and smart home system administrators.