# New Features Guide

This document describes the latest features added to the openHAB MCP Server, including script execution, transformation management, Main UI management, link management, and Docker containerization.

## Script Execution Framework

### Overview

The script execution framework provides secure Python script execution with authenticated access to openHAB APIs. This enables advanced automation scenarios and custom logic that goes beyond standard openHAB rules.

### Key Features

- **Secure Sandbox Environment**: Scripts run in an isolated environment with restricted capabilities
- **openHAB API Integration**: Authenticated access to all openHAB REST APIs
- **Resource Management**: Configurable limits for execution time and memory usage
- **Security Validation**: Comprehensive security scanning and validation before execution
- **Audit Logging**: Complete execution history and security event tracking

### Use Cases

#### Home Automation Scripts
```python
# Example: Intelligent lighting control
items = openhab.get_items(item_type='Switch')
lights = [item for item in items if 'Light' in item['name']]

# Turn off lights in unoccupied rooms
for light in lights:
    room = light['name'].split('_')[0]
    motion_sensor = f"{room}_Motion"
    
    motion_state = openhab.get_item_state(motion_sensor)
    if motion_state == 'OFF' and light['state'] == 'ON':
        openhab.send_item_command(light['name'], 'OFF')
        print(f"Turned off {light['name']} - no motion detected")
```

#### System Monitoring Scripts
```python
# Example: System health monitoring
import datetime

# Check system status
system_info = openhab.get_system_info()
things = openhab.get_things()

# Identify offline devices
offline_things = [thing for thing in things if thing['statusInfo']['status'] != 'ONLINE']

# Generate report
report = {
    'timestamp': datetime.datetime.now().isoformat(),
    'system_version': system_info['version'],
    'total_things': len(things),
    'offline_count': len(offline_things),
    'offline_devices': [thing['UID'] for thing in offline_things]
}

# Log critical issues
if len(offline_things) > 5:
    print(f"WARNING: {len(offline_things)} devices offline!")

return report
```

### Security Architecture

#### Multi-Layer Security Model

1. **Execution Sandbox**
   - Restricted Python environment with limited built-ins
   - Module import whitelist enforcement
   - Function blacklist for dangerous operations
   - AST-based code analysis for security violations

2. **Resource Controls**
   - Execution time limits (configurable, default 30 seconds)
   - Memory usage monitoring and limits
   - CPU usage throttling
   - Concurrent execution limits

3. **System Isolation**
   - No file system access outside sandbox
   - No network access except openHAB API
   - No subprocess or system command execution
   - No dynamic code generation or evaluation

4. **API Security**
   - Authenticated openHAB API access
   - Input validation and sanitization
   - Rate limiting and abuse prevention
   - Audit logging of all API operations

#### Security Configuration

```bash
# Environment variables for security tuning
SCRIPT_TIMEOUT_SECONDS=30          # Maximum execution time
SCRIPT_MEMORY_LIMIT_MB=128         # Memory limit
SCRIPT_SECURITY_LEVEL=STRICT       # Security level
SCRIPT_MAX_CONCURRENT=5            # Concurrent execution limit
```

## Link Management

### Overview

Link management provides comprehensive control over the connections between openHAB items and thing channels. This enables dynamic reconfiguration of device mappings and data flow.

### Key Features

- **Dynamic Link Creation**: Create item-channel connections programmatically
- **Configuration Management**: Update link parameters and transformations
- **Bulk Operations**: Manage multiple links efficiently
- **Validation**: Ensure link integrity and compatibility
- **Profile Support**: Advanced link profiles for data transformation

### Advanced Link Profiles

#### Transformation Profiles
```python
# Create link with MAP transformation
create_link(
    item_name="Temperature_Display",
    channel_uid="sensor:temperature:1:value",
    configuration={
        "profile": "transform:MAP",
        "function": "temperature.map",
        "sourceFormat": "%.1f°C"
    }
)
```

#### Follow Profiles
```python
# Create follow profile for synchronized items
create_link(
    item_name="Mirror_Switch",
    channel_uid="switch:main:1:state",
    configuration={
        "profile": "follow",
        "offset": 0
    }
)
```

#### Custom Profiles
```python
# Create custom profile with JavaScript transformation
create_link(
    item_name="Calculated_Value",
    channel_uid="sensor:multi:1:value",
    configuration={
        "profile": "transform:JS",
        "function": "custom_calculation.js",
        "parameters": {
            "multiplier": 1.5,
            "offset": 10
        }
    }
)
```

### Bulk Link Management

```python
# Example: Reconfigure all temperature sensors
temperature_links = list_links()
temp_links = [link for link in temperature_links if 'Temperature' in link['item_name']]

for link in temp_links:
    # Update all temperature links to use Celsius display
    update_link(
        item_name=link['item_name'],
        channel_uid=link['channel_uid'],
        configuration={
            "profile": "transform:MAP",
            "function": "celsius.map"
        }
    )
```

## Transformation Management

### Overview

Transformation management provides comprehensive control over data processing and format conversion in openHAB. This enables sophisticated data manipulation and protocol translation.

### Transformation Types

#### MAP Transformations
```python
# Create discrete value mapping
transform_id = create_transformation(
    transformation_type="MAP",
    configuration={
        "file": "device_states.map",
        "default": "UNKNOWN"
    }
)

# device_states.map content:
# 0=OFF
# 1=ON
# 2=STANDBY
# 255=ERROR
```

#### REGEX Transformations
```python
# Extract numeric values from text
transform_id = create_transformation(
    transformation_type="REGEX",
    configuration={
        "pattern": r"Temperature: (\d+\.?\d*)",
        "substitute": "$1"
    }
)
```

#### JSONPATH Transformations
```python
# Extract data from JSON responses
transform_id = create_transformation(
    transformation_type="JSONPATH",
    configuration={
        "path": "$.sensors[0].temperature.value"
    }
)
```

#### XPATH Transformations
```python
# Extract data from XML responses
transform_id = create_transformation(
    transformation_type="XPATH",
    configuration={
        "expression": "//temperature/@value"
    }
)
```

### Advanced Transformation Features

#### Chained Transformations
```python
# Create transformation chain for complex processing
transform_id = create_transformation(
    transformation_type="CHAIN",
    configuration={
        "transformations": [
            "JSONPATH:$.data.value",
            "REGEX:s/([0-9]+).*/$1/",
            "MAP:temperature_ranges.map"
        ]
    }
)
```

#### Conditional Transformations
```python
# Apply different transformations based on conditions
transform_id = create_transformation(
    transformation_type="SCRIPT",
    configuration={
        "script": """
        if (input > 100) {
            return MAP("high_temp.map")(input);
        } else {
            return MAP("normal_temp.map")(input);
        }
        """
    }
)
```

### Testing and Validation

```python
# Test transformation with sample data
test_cases = [
    "Temperature: 23.5°C",
    "Temperature: 75.2°F", 
    "Temp: 18.0",
    "Invalid data"
]

for test_input in test_cases:
    result = test_transformation(transform_id, test_input)
    print(f"Input: {test_input} -> Output: {result['output_value']}")
```

## Main UI Management

### Overview

Main UI management provides programmatic control over openHAB's modern web interface. This enables dynamic dashboard creation, widget management, and responsive design configuration.

### UI Architecture

#### Page Structure
- **Pages**: Top-level containers for organizing content
- **Blocks**: Sections within pages for grouping related widgets
- **Widgets**: Individual UI components for display and control
- **Layouts**: Responsive grid systems for organizing content

#### Widget Categories

**Control Widgets**
```python
# Switch widget for device control
switch_widget = {
    "type": "oh-switch-card",
    "config": {
        "item": "LivingRoom_Light",
        "title": "Living Room Light",
        "icon": "lightbulb",
        "color": "yellow"
    }
}
```

**Display Widgets**
```python
# Chart widget for data visualization
chart_widget = {
    "type": "oh-chart-card",
    "config": {
        "title": "Temperature History",
        "chartType": "line",
        "period": "24h",
        "items": ["Temperature_Sensor"]
    }
}
```

**Layout Widgets**
```python
# Grid layout for responsive design
grid_layout = {
    "type": "oh-grid-row",
    "config": {
        "columns": 3,
        "spacing": 10
    },
    "slots": {
        "default": [switch_widget, chart_widget]
    }
}
```

### Dynamic Page Creation

```python
# Create comprehensive room control page
room_config = {
    "name": "Living Room",
    "description": "Living room controls and monitoring",
    "layout": {
        "type": "masonry",
        "columns": 2,
        "spacing": 15,
        "responsive": {
            "mobile": {"columns": 1},
            "tablet": {"columns": 2},
            "desktop": {"columns": 3}
        }
    },
    "widgets": [
        {
            "type": "oh-switch-card",
            "config": {
                "item": "LivingRoom_Light",
                "title": "Main Light",
                "icon": "lightbulb"
            }
        },
        {
            "type": "oh-slider-card", 
            "config": {
                "item": "LivingRoom_Dimmer",
                "title": "Brightness",
                "min": 0,
                "max": 100,
                "step": 5
            }
        },
        {
            "type": "oh-chart-card",
            "config": {
                "title": "Temperature",
                "chartType": "line",
                "period": "12h",
                "items": ["LivingRoom_Temperature"]
            }
        }
    ]
}

page_id = create_ui_page(room_config)
```

### Responsive Design

```python
# Configure responsive breakpoints
responsive_config = {
    "breakpoints": {
        "mobile": {"max": 768, "columns": 1},
        "tablet": {"min": 769, "max": 1024, "columns": 2},
        "desktop": {"min": 1025, "columns": 3}
    },
    "spacing": {
        "mobile": 10,
        "tablet": 15,
        "desktop": 20
    }
}

manage_ui_layout(page_id, responsive_config)
```

### Theme and Styling

```python
# Apply custom theme to page
theme_config = {
    "theme": "dark",
    "colors": {
        "primary": "#2196F3",
        "accent": "#FF9800",
        "background": "#121212"
    },
    "typography": {
        "fontFamily": "Roboto",
        "fontSize": "14px"
    }
}

update_ui_page_theme(page_id, theme_config)
```

## Docker Containerization

### Overview

Docker containerization provides a complete deployment solution with security, monitoring, and orchestration capabilities. The container is optimized for production use with comprehensive health monitoring.

### Container Features

#### Security Hardening
- **Alpine Linux Base**: Minimal attack surface with security updates
- **Non-root Execution**: Runs as unprivileged user (UID 1000)
- **Read-only Filesystem**: Root filesystem mounted read-only where possible
- **Capability Dropping**: Unnecessary Linux capabilities removed
- **Security Scanning**: Regular vulnerability assessment and patching

#### Health Monitoring
```yaml
# Comprehensive health checks
healthcheck:
  test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

#### Resource Management
```yaml
# Resource limits and reservations
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 128M
```

### Orchestration Support

#### Docker Swarm
```yaml
version: '3.8'
services:
  openhab-mcp-server:
    image: gbicskei/openhab-mcp-server:latest
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.role == worker
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
```

#### Kubernetes Integration
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openhab-mcp-server
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      containers:
      - name: openhab-mcp-server
        image: gbicskei/openhab-mcp-server:latest
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
```

### Monitoring and Observability

#### Prometheus Metrics
```yaml
# Metrics endpoint configuration
- name: METRICS_ENABLED
  value: "true"
- name: METRICS_PORT
  value: "9090"
- name: METRICS_PATH
  value: "/metrics"
```

#### Logging Configuration
```yaml
# Structured logging setup
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    labels: "service,version,environment"
```

#### Distributed Tracing
```yaml
# Jaeger tracing integration
- name: TRACING_ENABLED
  value: "true"
- name: JAEGER_ENDPOINT
  value: "http://jaeger-collector:14268/api/traces"
```

## Migration Guide

### Upgrading from Previous Versions

#### Configuration Migration
```bash
# Backup existing configuration
cp mcp-config.json mcp-config.json.backup

# Update configuration for new features
# Add script execution settings
# Add Docker environment variables
# Update security settings
```

#### Feature Adoption
1. **Script Execution**: Start with STRICT security level
2. **Link Management**: Test with non-critical devices first
3. **Transformation Management**: Validate existing transformations
4. **Main UI Management**: Create test pages before modifying production
5. **Docker Deployment**: Use staging environment for testing

### Best Practices

#### Security
- Always use STRICT security level for script execution in production
- Regularly rotate openHAB API tokens
- Monitor security events and audit logs
- Keep Docker images updated with security patches

#### Performance
- Monitor script execution times and resource usage
- Use caching for frequently accessed transformations
- Optimize UI pages for mobile devices
- Configure appropriate resource limits for containers

#### Reliability
- Implement comprehensive health checks
- Use rolling updates for zero-downtime deployments
- Monitor system metrics and set up alerting
- Maintain backup and recovery procedures

## Troubleshooting

### Common Issues

#### Script Execution Problems
```bash
# Check script validation
validate_script(script_code)

# Review security logs
docker logs openhab-mcp-server | grep "SECURITY"

# Adjust security level if needed
export SCRIPT_SECURITY_LEVEL=NORMAL
```

#### Link Management Issues
```bash
# Verify item and channel existence
list_items()
get_thing_status(thing_uid)

# Check link configuration
list_links(item_name="problematic_item")
```

#### Container Issues
```bash
# Check container health
docker inspect openhab-mcp-server --format='{{.State.Health.Status}}'

# Review container logs
docker logs openhab-mcp-server --tail=100

# Monitor resource usage
docker stats openhab-mcp-server
```

### Support Resources

- **Documentation**: Complete feature documentation in `/docs`
- **Examples**: Sample configurations and scripts
- **Community**: [GitHub discussions](https://github.com/gbicskei/openhab-mcp-server/discussions) and [issue tracking](https://github.com/gbicskei/openhab-mcp-server/issues)
- **Maintainer**: Gabor Bicskei (gbicskei@gmail.com)
