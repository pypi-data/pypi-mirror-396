# Advanced Features Guide

This document describes the advanced features of the openHAB MCP Server, including script execution, transformation management, Main UI management, and link management.

## Script Execution

The openHAB MCP Server provides secure Python script execution capabilities, allowing users to run custom automation logic with access to the openHAB API.

### Security Model

Script execution runs in a sandboxed environment with comprehensive security measures to protect the host system while providing safe access to openHAB functionality.

#### Core Security Principles

- **Principle of Least Privilege**: Scripts have minimal access required for openHAB operations
- **Defense in Depth**: Multiple layers of security controls prevent system compromise
- **Fail-Safe Defaults**: Security restrictions are enabled by default
- **Audit and Monitoring**: All script activities are logged and monitored

#### Security Layers

**1. Execution Sandbox**
- **Restricted Environment**: Scripts run in an isolated Python environment
- **Module Whitelist**: Only pre-approved Python modules are available for import
- **Function Blacklist**: Dangerous built-in functions are disabled or restricted
- **Import Control**: Dynamic imports and module loading are prevented

**2. Resource Constraints**
- **Execution Time Limits**: Scripts are terminated after configured timeout (default: 30 seconds)
- **Memory Limits**: Memory usage is monitored and capped (default: 128MB where supported)
- **CPU Throttling**: Excessive CPU usage triggers warnings and termination
- **Recursion Limits**: Deep recursion is prevented to avoid stack overflow

**3. System Isolation**
- **No File System Access**: Scripts cannot read, write, or execute files on the host
- **No Network Access**: Direct network operations are blocked
- **No Subprocess Execution**: Scripts cannot spawn processes or execute system commands
- **No System Calls**: Direct system call access is prohibited

**4. API Security**
- **Authenticated Context**: openHAB API access uses secure, authenticated connections
- **Permission Validation**: API operations respect openHAB's security model
- **Input Sanitization**: All API inputs are validated and sanitized
- **Rate Limiting**: API calls are subject to rate limiting to prevent abuse

**5. Code Validation**
- **Syntax Checking**: Scripts are parsed and validated before execution
- **Security Scanning**: Dangerous patterns and constructs are detected and blocked
- **AST Analysis**: Abstract syntax tree analysis identifies potential security risks
- **Signature Verification**: Script integrity can be verified through checksums

### Available Tools

#### execute_script

Execute Python scripts with openHAB API access:

```python
# Example script
script_code = """
# Get all lights and turn them off
items = openhab.get_items(item_type='Switch')
lights = [item for item in items if 'Light' in item['name']]

for light in lights:
    if light['state'] == 'ON':
        openhab.send_item_command(light['name'], 'OFF')
        print(f"Turned off {light['name']}")

return f"Processed {len(lights)} lights"
"""

result = execute_script(script_code)
```

#### validate_script

Validate script syntax and security before execution:

```python
validation = validate_script(script_code)
if validation['valid']:
    result = execute_script(script_code)
else:
    print("Script validation failed:", validation['errors'])
```

### Script Context

Scripts have access to an `openhab` context object with these methods:

- `get_items(item_type=None)`: Get all items or filter by type
- `get_item_state(item_name)`: Get current state of an item
- `send_item_command(item_name, command)`: Send command to an item
- `get_things()`: Get all things
- `get_thing_status(thing_uid)`: Get thing status
- `get_rules()`: Get all rules
- `execute_rule(rule_uid)`: Execute a rule

### Configuration

Configure script execution limits:

```bash
# Environment variables
export SCRIPT_TIMEOUT_SECONDS=30
export SCRIPT_MEMORY_LIMIT_MB=128
export SCRIPT_SECURITY_LEVEL=STRICT
```

### Security Levels

- **STRICT**: Maximum security, minimal module access
- **NORMAL**: Balanced security and functionality  
- **PERMISSIVE**: Reduced restrictions for advanced use cases

### Whitelisted Modules

Scripts have access to these Python modules:

- **Standard Library**: `math`, `datetime`, `json`, `re`, `collections`, `itertools`, `functools`
- **Data Processing**: Basic data manipulation functions
- **openHAB Context**: Authenticated API access (provided automatically)

### Example Scripts

#### Turn Off All Lights

```python
# Get all switch items
items = openhab.get_items(item_type='Switch')

# Filter for lights
lights = [item for item in items if any(tag in item.get('tags', []) for tag in ['Lighting', 'Light'])]

count = 0
for light in lights:
    if light['state'] == 'ON':
        openhab.send_item_command(light['name'], 'OFF')
        count += 1

return f"Turned off {count} lights"
```

#### Check System Status

```python
import datetime

# Get system info
system_info = openhab.get_system_info()

# Get thing status
things = openhab.get_things()
offline_things = [thing for thing in things if thing['statusInfo']['status'] != 'ONLINE']

# Create status report
report = {
    'timestamp': datetime.datetime.now().isoformat(),
    'system_version': system_info['version'],
    'total_things': len(things),
    'offline_things': len(offline_things),
    'offline_list': [thing['UID'] for thing in offline_things]
}

return report
```

## Link Management

Manage connections between openHAB items and thing channels.

### Available Tools

#### list_links

List all item-channel links or filter by item/channel:

```python
# List all links
all_links = list_links()

# Filter by item
item_links = list_links(item_name="LivingRoom_Light")

# Filter by channel
channel_links = list_links(channel_uid="zwave:device:controller:node5:switch_binary")
```

#### create_link

Create new item-channel links:

```python
# Basic link creation
success = create_link(
    item_name="LivingRoom_Light",
    channel_uid="zwave:device:controller:node5:switch_binary"
)

# Link with configuration
success = create_link(
    item_name="Temperature_Sensor",
    channel_uid="zwave:device:controller:node3:sensor_temperature",
    configuration={
        "profile": "transform:MAP",
        "function": "temperature.map"
    }
)
```

#### update_link

Update existing link configuration:

```python
success = update_link(
    item_name="LivingRoom_Light",
    channel_uid="zwave:device:controller:node5:switch_binary",
    configuration={
        "profile": "follow",
        "offset": 0
    }
)
```

#### delete_link

Remove item-channel links:

```python
success = delete_link(
    item_name="LivingRoom_Light",
    channel_uid="zwave:device:controller:node5:switch_binary"
)
```

### Link Profiles

Common link profiles and their configurations:

#### Transform Profile

```python
configuration = {
    "profile": "transform:MAP",
    "function": "states.map",
    "sourceFormat": "%s"
}
```

#### Follow Profile

```python
configuration = {
    "profile": "follow",
    "offset": 0
}
```

#### Offset Profile

```python
configuration = {
    "profile": "offset",
    "offset": 10.0
}
```

## Transformation Management

Manage data transformations for converting values between different formats. Transformations are essential for integrating different systems and protocols in openHAB, allowing you to convert data formats, apply calculations, and normalize values from various sources.

### Overview

Transformations in openHAB serve several key purposes:

- **Data Format Conversion**: Convert between different data formats (JSON, XML, CSV, etc.)
- **Value Mapping**: Map discrete values to different representations
- **Mathematical Operations**: Apply calculations and formulas to numeric values
- **String Processing**: Parse and manipulate text data using regular expressions
- **Protocol Translation**: Convert between different communication protocols

### Transformation Architecture

Transformations work at multiple levels in openHAB:

1. **Item Level**: Applied when item states are updated
2. **Channel Level**: Applied when channel values are processed
3. **Rule Level**: Applied within automation rules
4. **Binding Level**: Applied by bindings during data processing

### Performance Considerations

- **Caching**: Transformation results are cached when possible
- **Lazy Loading**: Transformation files are loaded on-demand
- **Resource Management**: Memory usage is monitored for large transformation files
- **Error Handling**: Failed transformations don't block system operation

### Available Tools

#### list_transformations

List available transformation addons:

```python
transformations = list_transformations()
# Returns list of installed transformation addons with capabilities
```

#### create_transformation

Create new transformations:

```python
# MAP transformation
transform_id = create_transformation(
    transformation_type="MAP",
    configuration={
        "file": "states.map",
        "default": "UNKNOWN"
    }
)

# REGEX transformation
transform_id = create_transformation(
    transformation_type="REGEX",
    configuration={
        "pattern": r"(\d+\.?\d*)",
        "substitute": "$1"
    }
)
```

#### test_transformation

Test transformations with sample data:

```python
result = test_transformation(
    transformation_id="map_states_1",
    sample_data="ON"
)
# Returns: {"success": True, "input_value": "ON", "output_value": "1", "execution_time": 0.001}
```

#### update_transformation

Update transformation configuration:

```python
success = update_transformation(
    transformation_id="map_states_1",
    configuration={
        "file": "updated_states.map",
        "default": "0"
    }
)
```

#### get_transformation_usage

Find where transformations are used:

```python
usage = get_transformation_usage("map_states_1")
# Returns list of items, links, and rules using the transformation
```

### Transformation Types

#### MAP Transformation

Convert discrete values using a mapping file:

```python
# Create MAP transformation
transform_id = create_transformation(
    transformation_type="MAP",
    configuration={
        "file": "switch_states.map",
        "default": "UNKNOWN"
    }
)

# switch_states.map content:
# ON=1
# OFF=0
# UNDEF=UNKNOWN
```

#### REGEX Transformation

Extract or modify values using regular expressions:

```python
# Extract numeric value
transform_id = create_transformation(
    transformation_type="REGEX",
    configuration={
        "pattern": r"Temperature: (\d+\.?\d*)",
        "substitute": "$1"
    }
)
```

#### JSONPATH Transformation

Extract values from JSON data:

```python
transform_id = create_transformation(
    transformation_type="JSONPATH",
    configuration={
        "path": "$.temperature.value"
    }
)
```

## Main UI Management

Manage openHAB Main UI pages and widgets programmatically. The Main UI is openHAB's modern, responsive web interface that provides a flexible framework for creating custom dashboards and control interfaces.

### Main UI Architecture

The Main UI is built on a component-based architecture:

- **Pages**: Top-level containers that organize content
- **Widgets**: Individual UI components that display information or provide controls
- **Layouts**: Responsive grid systems that organize widgets
- **Themes**: Visual styling and appearance customization
- **Semantic Model**: Integration with openHAB's semantic model for automatic UI generation

### Design Principles

**1. Responsive Design**
- Mobile-first approach with responsive breakpoints
- Adaptive layouts that work on all screen sizes
- Touch-friendly controls and gestures

**2. Semantic Integration**
- Automatic widget suggestions based on item semantics
- Intelligent grouping and organization
- Context-aware control recommendations

**3. Customization**
- Flexible widget configuration options
- Custom CSS and styling capabilities
- Extensible component system

**4. Performance**
- Lazy loading of widgets and content
- Efficient state synchronization
- Optimized rendering for large dashboards

### Widget Categories

**Control Widgets**
- Switches, sliders, buttons for device control
- Input widgets for data entry
- Selection widgets for choosing options

**Display Widgets**
- Charts and graphs for data visualization
- Status indicators and badges
- Image and media display widgets

**Layout Widgets**
- Containers and panels for organization
- Tabs and accordions for space management
- Grid and flexbox layouts for responsive design

**Advanced Widgets**
- Maps for location-based controls
- Calendars and schedulers
- Custom HTML and iframe widgets

### Available Tools

#### list_ui_pages

List all Main UI pages:

```python
pages = list_ui_pages()
# Returns list of pages with configuration and widget structure
```

#### create_ui_page

Create new UI pages:

```python
page_config = {
    "name": "Living Room",
    "description": "Living room controls",
    "layout": {
        "type": "grid",
        "columns": 2
    },
    "widgets": [
        {
            "type": "switch",
            "properties": {
                "item": "LivingRoom_Light",
                "title": "Main Light"
            }
        }
    ]
}

page_id = create_ui_page(page_config)
```

#### update_ui_widget

Update widget properties:

```python
success = update_ui_widget(
    page_id="living_room",
    widget_id="light_switch_1",
    properties={
        "title": "Updated Light Switch",
        "icon": "lightbulb",
        "color": "blue"
    }
)
```

#### manage_ui_layout

Manage page layouts and responsive design:

```python
layout_config = {
    "type": "masonry",
    "columns": 3,
    "spacing": 10,
    "responsive": {
        "mobile": {"columns": 1},
        "tablet": {"columns": 2}
    }
}

success = manage_ui_layout("living_room", layout_config)
```

#### export_ui_config

Export UI configuration for backup or sharing:

```python
# Export all pages
config = export_ui_config()

# Export specific pages
config = export_ui_config(page_ids=["living_room", "kitchen"])
```

### Widget Types

#### Switch Widget

```python
widget = {
    "type": "switch",
    "properties": {
        "item": "LivingRoom_Light",
        "title": "Living Room Light",
        "icon": "lightbulb",
        "color": "yellow"
    }
}
```

#### Slider Widget

```python
widget = {
    "type": "slider",
    "properties": {
        "item": "LivingRoom_Dimmer",
        "title": "Brightness",
        "min": 0,
        "max": 100,
        "step": 5
    }
}
```

#### Chart Widget

```python
widget = {
    "type": "chart",
    "properties": {
        "item": "Temperature_Sensor",
        "title": "Temperature History",
        "period": "24h",
        "chart_type": "line"
    }
}
```

### Layout Types

#### Grid Layout

```python
layout = {
    "type": "grid",
    "columns": 3,
    "spacing": 10,
    "padding": 15
}
```

#### Masonry Layout

```python
layout = {
    "type": "masonry",
    "columns": 2,
    "spacing": 15,
    "responsive": {
        "mobile": {"columns": 1},
        "tablet": {"columns": 2},
        "desktop": {"columns": 3}
    }
}
```

## Best Practices

### Script Execution

1. **Keep Scripts Simple**: Focus on specific tasks
2. **Handle Errors**: Use try-catch blocks for robust scripts
3. **Test First**: Use `validate_script` before execution
4. **Resource Awareness**: Be mindful of execution time and memory
5. **Security**: Never include sensitive data in scripts

### Link Management

1. **Validate Channels**: Ensure channels exist before creating links
2. **Use Profiles**: Leverage transformation profiles for data conversion
3. **Document Links**: Keep track of link purposes and configurations
4. **Test Changes**: Verify link behavior after creation/updates

### Transformation Management

1. **Test Thoroughly**: Use `test_transformation` with various inputs
2. **Version Control**: Keep transformation files in version control
3. **Performance**: Monitor transformation execution time
4. **Fallbacks**: Always provide default values for MAP transformations

### Main UI Management

1. **Responsive Design**: Consider different screen sizes
2. **User Experience**: Group related controls logically
3. **Performance**: Avoid too many widgets on a single page
4. **Backup**: Regularly export UI configurations
5. **Testing**: Test UI changes on different devices

## Troubleshooting

### Script Execution Issues

- **Timeout Errors**: Increase `SCRIPT_TIMEOUT_SECONDS`
- **Memory Errors**: Increase `SCRIPT_MEMORY_LIMIT_MB`
- **Import Errors**: Check module whitelist
- **API Errors**: Verify openHAB connection and permissions

### Link Management Issues

- **Creation Failures**: Verify item and channel exist
- **Profile Errors**: Check profile syntax and parameters
- **Update Failures**: Ensure link exists before updating

### Transformation Issues

- **Test Failures**: Check transformation syntax and configuration
- **Performance Issues**: Optimize transformation logic
- **Usage Tracking**: Use `get_transformation_usage` to find dependencies

### UI Management Issues

- **Widget Errors**: Verify widget type and properties
- **Layout Issues**: Check responsive design configuration
- **Export Failures**: Ensure sufficient permissions