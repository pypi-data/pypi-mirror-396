# Configuration Guide

This document describes the various ways to configure the openHAB MCP Server.

## Environment Variables

The server uses the following environment variables for configuration:

### Required
- `OPENHAB_TOKEN`: API token for openHAB authentication (required)

### Optional
- `OPENHAB_URL`: openHAB server URL (default: `http://localhost:8080`)
- `OPENHAB_TIMEOUT`: Request timeout in seconds (default: `30`)
- `LOG_LEVEL`: Logging level - DEBUG, INFO, WARNING, ERROR (default: `INFO`)

### Script Execution Configuration
- `SCRIPT_TIMEOUT_SECONDS`: Maximum script execution time (default: `30`)
- `SCRIPT_MEMORY_LIMIT_MB`: Memory limit for scripts in MB (default: `128`)
- `SCRIPT_SECURITY_LEVEL`: Security level - STRICT, NORMAL, PERMISSIVE (default: `STRICT`)

### Docker Configuration
- `MCP_HOST`: MCP server host for Docker (default: `0.0.0.0`)
- `MCP_PORT`: MCP server port (default: `8000`)
- `HEALTH_CHECK_INTERVAL`: Health check interval in seconds (default: `30`)

## MCP Client Configuration

### Standard MCP Client Configuration

For MCP clients, use the standard MCP server configuration format:

```json
{
  "mcpServers": {
    "openhab": {
      "command": "openhab-mcp-server",
      "env": {
        "OPENHAB_URL": "http://localhost:8080",
        "OPENHAB_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

## Configuration Methods

### Method 1: Environment Variables (Recommended)

Set environment variables in your shell or system:

**Windows:**
```cmd
set OPENHAB_URL=http://localhost:8080
set OPENHAB_TOKEN=your-api-token-here
openhab-mcp-server
```

**Linux/Mac:**
```bash
export OPENHAB_URL=http://localhost:8080
export OPENHAB_TOKEN=your-api-token-here
openhab-mcp-server
```

### Method 2: MCP Configuration File

Set environment variables in the MCP configuration file (shown above).

### Method 3: Configuration File

Create a configuration file and specify it with the `--config` option:

**config.json:**
```json
{
  "openhab_url": "http://localhost:8080",
  "openhab_token": "your-api-token-here",
  "openhab_timeout": 30,
  "log_level": "INFO",
  "script_timeout_seconds": 30,
  "script_memory_limit_mb": 128,
  "script_security_level": "STRICT"
}
```

**Usage:**
```bash
openhab-mcp-server --config config.json
```

## Getting an openHAB API Token

1. Open the openHAB web interface (usually http://localhost:8080)
2. Go to **Settings** → **API Security**
3. Click **Create API Token**
4. Enter a name for the token (e.g., "MCP Server")
5. Copy the generated token
6. Set it as the `OPENHAB_TOKEN` environment variable

## Security Considerations

- **Never commit API tokens to version control**
- Use environment variables or secure configuration management
- Regularly rotate API tokens
- Use the minimum required permissions for the token
- Monitor API token usage in openHAB logs

## Troubleshooting Configuration

### Common Issues

1. **Connection Refused**
   - Check that openHAB is running
   - Verify the `OPENHAB_URL` is correct
   - Check firewall settings

2. **Authentication Failed**
   - Verify the `OPENHAB_TOKEN` is correct
   - Check that the token hasn't expired
   - Ensure the token has proper permissions

3. **Timeout Errors**
   - Increase `OPENHAB_TIMEOUT` value
   - Check network connectivity
   - Verify openHAB server performance

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
export LOG_LEVEL=DEBUG
openhab-mcp-server
```

Or in the MCP configuration:

```json
{
  "env": {
    "LOG_LEVEL": "DEBUG"
  }
}
```

### Validation

Test your configuration with the built-in diagnostics:

```bash
openhab-mcp-server --validate-config
```

This will test the connection to openHAB and verify the API token.

## Docker Configuration

The openHAB MCP Server provides comprehensive Docker support for containerized deployments, including standalone containers, Docker Compose, and Kubernetes orchestration.

### Container Architecture

The Docker image is built on Alpine Linux for minimal size and security:

- **Base Image**: `python:3.11-alpine`
- **Size**: Approximately 150MB compressed
- **Security**: Non-root user execution, minimal attack surface
- **Multi-Architecture**: Supports AMD64, ARM64, and ARM/v7

### Environment Variables for Docker

#### Core Configuration

```bash
# Required
OPENHAB_URL=http://openhab:8080          # openHAB server URL
OPENHAB_TOKEN=your-api-token             # API authentication token

# Optional
OPENHAB_TIMEOUT=30                       # Request timeout in seconds
LOG_LEVEL=INFO                           # Logging level (DEBUG, INFO, WARNING, ERROR)
```

#### Server Configuration

```bash
# MCP Server Settings
MCP_HOST=0.0.0.0                         # Server bind address (0.0.0.0 for containers)
MCP_PORT=8000                            # Server port
MCP_MAX_CONNECTIONS=100                  # Maximum concurrent connections
MCP_REQUEST_TIMEOUT=60                   # Request timeout in seconds
```

#### Script Execution Configuration

```bash
# Script Security and Limits
SCRIPT_TIMEOUT_SECONDS=30                # Maximum script execution time
SCRIPT_MEMORY_LIMIT_MB=128               # Memory limit for scripts
SCRIPT_SECURITY_LEVEL=STRICT             # Security level (STRICT, NORMAL, PERMISSIVE)
SCRIPT_MAX_CONCURRENT=5                  # Maximum concurrent script executions
```

#### Health and Monitoring

```bash
# Health Check Configuration
HEALTH_CHECK_INTERVAL=30                 # Health check interval in seconds
HEALTH_CHECK_TIMEOUT=10                  # Health check timeout in seconds
HEALTH_CHECK_RETRIES=3                   # Number of health check retries
METRICS_ENABLED=true                     # Enable metrics collection
```

### Basic Docker Usage

#### Quick Start

```bash
# Pull and run the latest image
docker run -d \
  --name openhab-mcp-server \
  -e OPENHAB_URL=http://your-openhab-host:8080 \
  -e OPENHAB_TOKEN=your-api-token \
  -p 8000:8000 \
  gbicskei/openhab-mcp-server:latest
```

#### With Full Configuration

```bash
docker run -d \
  --name openhab-mcp-server \
  --restart unless-stopped \
  -e OPENHAB_URL=http://openhab:8080 \
  -e OPENHAB_TOKEN=your-api-token \
  -e OPENHAB_TIMEOUT=30 \
  -e LOG_LEVEL=INFO \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8000 \
  -e SCRIPT_TIMEOUT_SECONDS=30 \
  -e SCRIPT_MEMORY_LIMIT_MB=128 \
  -e SCRIPT_SECURITY_LEVEL=STRICT \
  -e HEALTH_CHECK_INTERVAL=30 \
  -e METRICS_ENABLED=true \
  -p 8000:8000 \
  -v /path/to/config:/app/config:ro \
  -v /path/to/logs:/app/logs \
  gbicskei/openhab-mcp-server:latest
```

### Docker Compose Configuration

Docker Compose provides an easy way to deploy the MCP server alongside openHAB and other services.

#### Basic Compose File

**docker-compose.yml:**
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
      - SCRIPT_TIMEOUT_SECONDS=30
      - SCRIPT_MEMORY_LIMIT_MB=128
      - SCRIPT_SECURITY_LEVEL=STRICT
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
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
    networks:
      - openhab-network

  openhab:
    image: openhab/openhab:4.1.0
    container_name: openhab
    ports:
      - "8080:8080"
      - "8443:8443"
    volumes:
      - openhab_addons:/openhab/addons
      - openhab_conf:/openhab/conf
      - openhab_userdata:/openhab/userdata
      - /etc/localtime:/etc/localtime:ro
    environment:
      - EXTRA_JAVA_OPTS=-Duser.timezone=America/New_York -Xmx2g
      - OPENHAB_HTTP_PORT=8080
      - OPENHAB_HTTPS_PORT=8443
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/rest/"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    restart: unless-stopped
    networks:
      - openhab-network

volumes:
  openhab_addons:
  openhab_conf:
  openhab_userdata:

networks:
  openhab-network:
    driver: bridge
```

#### Production Compose File

**docker-compose.prod.yml:**
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
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
      - MCP_MAX_CONNECTIONS=100
      - SCRIPT_TIMEOUT_SECONDS=30
      - SCRIPT_MEMORY_LIMIT_MB=128
      - SCRIPT_SECURITY_LEVEL=STRICT
      - SCRIPT_MAX_CONCURRENT=5
      - HEALTH_CHECK_INTERVAL=30
      - METRICS_ENABLED=true
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
      - /etc/ssl/certs:/etc/ssl/certs:ro
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
    networks:
      - openhab-network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  openhab:
    image: openhab/openhab:4.1.0
    container_name: openhab
    ports:
      - "8080:8080"
      - "8443:8443"
    volumes:
      - openhab_addons:/openhab/addons
      - openhab_conf:/openhab/conf
      - openhab_userdata:/openhab/userdata
      - /etc/localtime:/etc/localtime:ro
      - ./ssl:/openhab/conf/ssl:ro
    environment:
      - EXTRA_JAVA_OPTS=-Duser.timezone=America/New_York -Xmx4g -XX:+UseG1GC
      - OPENHAB_HTTP_PORT=8080
      - OPENHAB_HTTPS_PORT=8443
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/rest/"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    restart: unless-stopped
    networks:
      - openhab-network
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "5"

secrets:
  openhab_token:
    file: ./secrets/openhab_token.txt

volumes:
  openhab_addons:
  openhab_conf:
  openhab_userdata:

networks:
  openhab-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

#### Environment File

Create a `.env` file for environment variables:

```bash
# .env file
OPENHAB_TOKEN=your-api-token-here
COMPOSE_PROJECT_NAME=openhab-stack
TZ=America/New_York

# Optional overrides
OPENHAB_VERSION=4.1.0
MCP_SERVER_VERSION=latest
LOG_LEVEL=INFO
SCRIPT_SECURITY_LEVEL=STRICT
```

### Volume Mounts

The container supports several volume mount points for configuration and data persistence:

#### Configuration Volumes
- `/app/config`: Configuration files (optional)
  - Custom configuration files
  - SSL certificates and keys
  - Script libraries and modules

#### Data Volumes  
- `/app/logs`: Log files (optional)
  - Application logs
  - Access logs
  - Error logs
  - Audit logs

#### Script Volumes
- `/app/scripts`: Custom script libraries (optional)
  - Shared Python modules
  - Custom transformation functions
  - Utility libraries

#### Example Volume Configuration

```bash
# Create local directories
mkdir -p ./config ./logs ./scripts

# Set permissions
chmod 755 ./config ./logs ./scripts

# Run with volumes
docker run -d \
  --name openhab-mcp-server \
  -v $(pwd)/config:/app/config:ro \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/scripts:/app/scripts:ro \
  gbicskei/openhab-mcp-server:latest
```

### Kubernetes Deployment

For production Kubernetes deployments, use the following configurations:

#### Namespace and ConfigMap

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openhab-system
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: openhab-mcp-config
  namespace: openhab-system
data:
  OPENHAB_URL: "http://openhab-service.openhab-system.svc.cluster.local:8080"
  OPENHAB_TIMEOUT: "30"
  LOG_LEVEL: "INFO"
  MCP_HOST: "0.0.0.0"
  MCP_PORT: "8000"
  SCRIPT_TIMEOUT_SECONDS: "30"
  SCRIPT_MEMORY_LIMIT_MB: "128"
  SCRIPT_SECURITY_LEVEL: "STRICT"
  HEALTH_CHECK_INTERVAL: "30"
  METRICS_ENABLED: "true"
```

#### Secret for API Token

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openhab-mcp-secrets
  namespace: openhab-system
type: Opaque
data:
  openhab-token: <base64-encoded-token>
```

#### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openhab-mcp-server
  namespace: openhab-system
  labels:
    app: openhab-mcp-server
spec:
  replicas: 2
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
          name: mcp-port
        envFrom:
        - configMapRef:
            name: openhab-mcp-config
        env:
        - name: OPENHAB_TOKEN
          valueFrom:
            secretKeyRef:
              name: openhab-mcp-secrets
              key: openhab-token
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
          readOnly: true
        - name: logs-volume
          mountPath: /app/logs
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1000
          runAsGroup: 1000
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
      volumes:
      - name: config-volume
        configMap:
          name: openhab-mcp-config
      - name: logs-volume
        emptyDir: {}
      securityContext:
        fsGroup: 1000
      restartPolicy: Always
---
apiVersion: v1
kind: Service
metadata:
  name: openhab-mcp-service
  namespace: openhab-system
  labels:
    app: openhab-mcp-server
spec:
  selector:
    app: openhab-mcp-server
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
    name: mcp-port
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: openhab-mcp-ingress
  namespace: openhab-system
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - openhab-mcp.example.com
    secretName: openhab-mcp-tls
  rules:
  - host: openhab-mcp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: openhab-mcp-service
            port:
              number: 8000
```

#### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: openhab-mcp-hpa
  namespace: openhab-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openhab-mcp-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Health Monitoring

The Docker container includes health check endpoints:

- **Health**: `http://localhost:8000/health`
- **Liveness**: `http://localhost:8000/health/live`
- **Readiness**: `http://localhost:8000/health/ready`
- **Metrics**: `http://localhost:8000/metrics`

## Script Execution Security

### Security Levels

- **STRICT**: Maximum security, minimal module access
- **NORMAL**: Balanced security and functionality
- **PERMISSIVE**: Reduced restrictions for advanced use cases

### Resource Limits

Configure resource limits for script execution:

```json
{
  "script_timeout_seconds": 30,
  "script_memory_limit_mb": 128,
  "script_security_level": "STRICT"
}
```

### Whitelisted Modules

Scripts have access to these Python modules:
- `math`, `datetime`, `json`, `re`
- `collections`, `itertools`, `functools`
- openHAB client context (provided automatically)

### Security Constraints

- No file system access outside sandbox
- No network access except openHAB API
- No subprocess execution
- Limited execution time and memory
- Syntax validation before execution
