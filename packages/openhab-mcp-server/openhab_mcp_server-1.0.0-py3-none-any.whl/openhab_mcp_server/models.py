"""
Pydantic models for openHAB entities.

This module defines data models for openHAB entities including items, things,
rules, and system information. All models include comprehensive validation
and serialization/deserialization capabilities.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class ItemState(BaseModel):
    """openHAB item state representation."""
    
    name: str = Field(..., description="Unique name of the openHAB item")
    state: str = Field(..., description="Current state value of the item")
    type: str = Field(..., description="Item type (e.g., Switch, Dimmer, Number)")
    label: Optional[str] = Field(None, description="Human-readable label for the item")
    category: Optional[str] = Field(None, description="Category for UI grouping")
    tags: List[str] = Field(default_factory=list, description="List of tags associated with the item")
    # Extensions for new functionality
    linked_channels: List[str] = Field(default_factory=list, description="List of channels linked to this item")
    transformations: List[str] = Field(default_factory=list, description="List of transformations applied to this item")
    script_accessible: bool = Field(True, description="Whether this item can be accessed from scripts")
    ui_widgets: List[str] = Field(default_factory=list, description="List of UI widgets that use this item")
    # Additional extensions for enhanced functionality
    link_profiles: List[str] = Field(default_factory=list, description="List of link profiles applied to this item")
    container_accessible: bool = Field(True, description="Whether this item is accessible from containerized environments")
    transformation_chain: List[Dict[str, Any]] = Field(default_factory=list, description="Ordered list of transformations applied to this item")
    ui_page_references: List[str] = Field(default_factory=list, description="List of UI pages that reference this item")
    script_usage_count: int = Field(0, description="Number of times this item has been accessed by scripts")
    last_script_access: Optional[str] = Field(None, description="Timestamp of last script access to this item")
    # Security and validation extensions
    script_security_level: str = Field("safe", description="Security level for script access (safe, restricted, blocked)")
    container_health_impact: bool = Field(False, description="Whether this item affects container health monitoring")
    link_validation_status: str = Field("valid", description="Validation status of item links (valid, warning, error)")
    transformation_validation_errors: List[str] = Field(default_factory=list, description="List of transformation validation errors")
    ui_layout_constraints: Dict[str, Any] = Field(default_factory=dict, description="UI layout constraints for this item")
    # Additional metadata for enhanced functionality
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the item")
    last_update: Optional[str] = Field(None, description="Timestamp of last state update")
    persistence_services: List[str] = Field(default_factory=list, description="List of persistence services storing this item")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate item name format."""
        if not v or not v.strip():
            raise ValueError("Item name cannot be empty")
        if ' ' in v:
            raise ValueError("Item name cannot contain spaces")
        return v.strip()
    
    @validator('type')
    def validate_type(cls, v):
        """Validate item type."""
        valid_types = {
            'Switch', 'Dimmer', 'Number', 'String', 'DateTime', 'Contact',
            'Rollershutter', 'Color', 'Location', 'Player', 'Group'
        }
        if v not in valid_types:
            raise ValueError(f"Invalid item type: {v}. Must be one of {valid_types}")
        return v
    
    @validator('linked_channels')
    def validate_linked_channels(cls, v):
        """Validate linked channels format."""
        for channel in v:
            if not isinstance(channel, str) or ':' not in channel:
                raise ValueError(f"Invalid channel UID format: {channel}. Must contain ':' separator")
        return v
    
    @validator('transformations')
    def validate_transformations(cls, v):
        """Validate transformation references."""
        for transformation in v:
            if not isinstance(transformation, str) or not transformation.strip():
                raise ValueError("Transformation reference cannot be empty")
        return v
    
    @validator('script_security_level')
    def validate_script_security_level(cls, v):
        """Validate script security level."""
        valid_levels = {'safe', 'restricted', 'blocked'}
        if v.lower() not in valid_levels:
            raise ValueError(f"Invalid script security level: {v}. Must be one of {valid_levels}")
        return v.lower()
    
    @validator('link_validation_status')
    def validate_link_validation_status(cls, v):
        """Validate link validation status."""
        valid_statuses = {'valid', 'warning', 'error'}
        if v.lower() not in valid_statuses:
            raise ValueError(f"Invalid link validation status: {v}. Must be one of {valid_statuses}")
        return v.lower()
    
    @validator('script_usage_count')
    def validate_script_usage_count(cls, v):
        """Validate script usage count is non-negative."""
        if v < 0:
            raise ValueError("Script usage count must be non-negative")
        return v
    
    @validator('transformation_chain')
    def validate_transformation_chain(cls, v):
        """Validate transformation chain format."""
        for transformation in v:
            if not isinstance(transformation, dict):
                raise ValueError("Each transformation in chain must be a dictionary")
            if 'type' not in transformation:
                raise ValueError("Each transformation must have a 'type' field")
        return v
    
    @validator('last_script_access')
    def validate_last_script_access(cls, v):
        """Validate last script access timestamp format."""
        if v is not None and not v.strip():
            raise ValueError("Last script access timestamp cannot be empty string")
        return v
    
    @validator('last_update')
    def validate_last_update(cls, v):
        """Validate last update timestamp format."""
        if v is not None and not v.strip():
            raise ValueError("Last update timestamp cannot be empty string")
        return v
    
    def increment_script_usage(self) -> None:
        """Increment script usage count and update timestamp."""
        self.script_usage_count += 1
        self.last_script_access = datetime.now().isoformat()
    
    def add_transformation_error(self, error: str) -> None:
        """Add a transformation validation error."""
        if error not in self.transformation_validation_errors:
            self.transformation_validation_errors.append(error)
            self.link_validation_status = "error"
    
    def clear_transformation_errors(self) -> None:
        """Clear all transformation validation errors."""
        self.transformation_validation_errors.clear()
        if self.link_validation_status == "error":
            self.link_validation_status = "valid"
    
    def is_script_accessible(self) -> bool:
        """Check if item is accessible from scripts based on security level."""
        return self.script_accessible and self.script_security_level != "blocked"
    
    def is_container_compatible(self) -> bool:
        """Check if item is compatible with containerized environments."""
        return self.container_accessible
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ThingStatus(BaseModel):
    """openHAB thing status representation."""
    
    uid: str = Field(..., description="Unique identifier of the thing")
    status: str = Field(..., description="Current status of the thing")
    status_detail: str = Field(..., description="Detailed status information")
    label: str = Field(..., description="Human-readable label for the thing")
    bridge_uid: Optional[str] = Field(None, description="UID of the bridge thing if applicable")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Thing configuration parameters")
    # Extensions for new functionality
    channels: List[Dict[str, Any]] = Field(default_factory=list, description="List of channels provided by this thing")
    linked_items: List[str] = Field(default_factory=list, description="List of items linked to this thing's channels")
    container_managed: bool = Field(False, description="Whether this thing is managed by a containerized binding")
    transformation_usage: List[str] = Field(default_factory=list, description="List of transformations used by this thing")
    
    @validator('uid')
    def validate_uid(cls, v):
        """Validate thing UID format."""
        if not v or not v.strip():
            raise ValueError("Thing UID cannot be empty")
        # openHAB thing UIDs typically follow binding:type:id format
        parts = v.split(':')
        if len(parts) < 2:
            raise ValueError("Thing UID must contain at least binding and type separated by ':'")
        # Check that all parts are non-empty
        if any(not part.strip() for part in parts):
            raise ValueError("Thing UID parts cannot be empty")
        return v.strip()
    
    @validator('status')
    def validate_status(cls, v):
        """Validate thing status."""
        valid_statuses = {
            'ONLINE', 'OFFLINE', 'UNKNOWN', 'INITIALIZING', 'REMOVING', 'REMOVED'
        }
        if v not in valid_statuses:
            raise ValueError(f"Invalid thing status: {v}. Must be one of {valid_statuses}")
        return v
    
    @validator('channels')
    def validate_channels(cls, v):
        """Validate channels list."""
        for channel in v:
            if not isinstance(channel, dict):
                raise ValueError("Channel must be a dictionary")
            if 'uid' not in channel:
                raise ValueError("Channel must have a 'uid' field")
        return v
    
    @validator('linked_items')
    def validate_linked_items(cls, v):
        """Validate linked items format."""
        for item in v:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("Item name cannot be empty")
            if ' ' in item:
                raise ValueError("Item name cannot contain spaces")
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


class RuleDefinition(BaseModel):
    """Rule definition for creation/modification."""
    
    name: str = Field(..., description="Name of the rule")
    description: Optional[str] = Field(None, description="Optional description of the rule")
    triggers: List[Dict[str, Any]] = Field(..., description="List of rule triggers")
    conditions: List[Dict[str, Any]] = Field(default_factory=list, description="List of rule conditions")
    actions: List[Dict[str, Any]] = Field(..., description="List of rule actions")
    enabled: bool = Field(True, description="Whether the rule is enabled")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate rule name."""
        if not v or not v.strip():
            raise ValueError("Rule name cannot be empty")
        return v.strip()
    
    @validator('triggers')
    def validate_triggers(cls, v):
        """Validate that triggers list is not empty."""
        if not v:
            raise ValueError("Rule must have at least one trigger")
        return v
    
    @validator('actions')
    def validate_actions(cls, v):
        """Validate that actions list is not empty."""
        if not v:
            raise ValueError("Rule must have at least one action")
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


class SystemInfo(BaseModel):
    """System information model."""
    
    version: str = Field(..., description="openHAB version")
    build_string: str = Field(..., description="Build information string")
    locale: str = Field(..., description="System locale")
    measurement_system: str = Field(..., description="Measurement system (metric/imperial)")
    start_level: int = Field(..., description="OSGi start level")
    # Extensions for new functionality
    container_runtime: Optional[str] = Field(None, description="Container runtime information if running in container")
    script_engine_status: Optional[str] = Field(None, description="Status of the script execution engine")
    ui_framework_version: Optional[str] = Field(None, description="Version of the Main UI framework")
    transformation_services: List[str] = Field(default_factory=list, description="List of available transformation services")
    link_registry_size: Optional[int] = Field(None, description="Number of registered item links")
    
    @validator('version')
    def validate_version(cls, v):
        """Validate version format."""
        if not v or not v.strip():
            raise ValueError("Version cannot be empty")
        return v.strip()
    
    @validator('measurement_system')
    def validate_measurement_system(cls, v):
        """Validate measurement system."""
        valid_systems = {'metric', 'imperial'}
        if v.lower() not in valid_systems:
            raise ValueError(f"Invalid measurement system: {v}. Must be one of {valid_systems}")
        return v.lower()
    
    @validator('start_level')
    def validate_start_level(cls, v):
        """Validate start level is positive."""
        if v < 0:
            raise ValueError("Start level must be non-negative")
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


# Additional utility models for error handling and responses

class MCPError(BaseModel):
    """Standardized error response format."""
    
    error_type: str = Field(..., description="Type of error")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    suggestions: List[str] = Field(default_factory=list, description="Suggested solutions")
    
    @validator('error_type')
    def validate_error_type(cls, v):
        """Validate error type."""
        if not v or not v.strip():
            raise ValueError("Error type cannot be empty")
        return v.strip()
    
    @validator('message')
    def validate_message(cls, v):
        """Validate error message."""
        if not v or not v.strip():
            raise ValueError("Error message cannot be empty")
        return v.strip()


class AddonInfo(BaseModel):
    """Addon information model."""
    
    id: str = Field(..., description="Unique identifier of the addon")
    name: str = Field(..., description="Human-readable name of the addon")
    version: Optional[str] = Field(None, description="Version of the addon")
    description: Optional[str] = Field(None, description="Description of the addon")
    installed: bool = Field(..., description="Whether the addon is currently installed")
    type: str = Field(..., description="Type of addon (binding, transformation, etc.)")
    author: Optional[str] = Field(None, description="Author of the addon")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Addon configuration parameters")
    # Extensions for new functionality
    container_compatible: bool = Field(True, description="Whether the addon works in containerized environments")
    script_integration: bool = Field(False, description="Whether the addon provides script integration capabilities")
    ui_components: List[str] = Field(default_factory=list, description="List of UI components provided by this addon")
    transformation_types: List[str] = Field(default_factory=list, description="List of transformation types provided (for transformation addons)")
    link_profiles: List[str] = Field(default_factory=list, description="List of link profiles provided by this addon")
    dependencies: List[str] = Field(default_factory=list, description="List of addon dependencies")
    
    @validator('id')
    def validate_id(cls, v):
        """Validate addon ID format."""
        if not v or not v.strip():
            raise ValueError("Addon ID cannot be empty")
        return v.strip()
    
    @validator('name')
    def validate_name(cls, v):
        """Validate addon name."""
        if not v or not v.strip():
            raise ValueError("Addon name cannot be empty")
        return v.strip()
    
    @validator('type')
    def validate_type(cls, v):
        """Validate addon type."""
        valid_types = {
            'binding', 'transformation', 'persistence', 'automation', 
            'voice', 'ui', 'misc', 'io'
        }
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid addon type: {v}. Must be one of {valid_types}")
        return v.lower()
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


class ValidationResult(BaseModel):
    """Result of input validation operations."""
    
    is_valid: bool = Field(..., description="Whether the input is valid")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings")
    validated_fields: Dict[str, Any] = Field(default_factory=dict, description="Successfully validated fields")
    # Extensions for new functionality
    security_violations: List[str] = Field(default_factory=list, description="List of security constraint violations")
    syntax_errors: List[str] = Field(default_factory=list, description="List of syntax errors found")
    container_compatibility: Optional[bool] = Field(None, description="Whether the validated configuration is container-compatible")
    transformation_syntax_valid: Optional[bool] = Field(None, description="Whether transformation syntax is valid")
    ui_layout_valid: Optional[bool] = Field(None, description="Whether UI layout configuration is valid")
    link_validation_status: Optional[str] = Field(None, description="Status of link validation (valid, invalid, warning)")
    script_security_level: Optional[str] = Field(None, description="Security level assessment for script validation")
    
    def add_error(self, error: str) -> None:
        """Add a validation error."""
        self.is_valid = False
        self.errors.append(error)
    
    def add_warning(self, warning: str) -> None:
        """Add a validation warning."""
        self.warnings.append(warning)
    
    def add_validated_field(self, field_name: str, value: Any) -> None:
        """Add a successfully validated field."""
        self.validated_fields[field_name] = value
    
    def add_security_violation(self, violation: str) -> None:
        """Add a security violation."""
        self.is_valid = False
        self.security_violations.append(violation)
    
    def add_syntax_error(self, error: str) -> None:
        """Add a syntax error."""
        self.is_valid = False
        self.syntax_errors.append(error)
    
    def set_script_security_level(self, level: str) -> None:
        """Set the script security level assessment."""
        valid_levels = {'safe', 'warning', 'dangerous', 'blocked'}
        if level.lower() not in valid_levels:
            raise ValueError(f"Invalid security level: {level}. Must be one of {valid_levels}")
        self.script_security_level = level.lower()
    
    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self.errors) > 0 or len(self.security_violations) > 0 or len(self.syntax_errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any validation warnings."""
        return len(self.warnings) > 0
    
    def has_security_violations(self) -> bool:
        """Check if there are any security violations."""
        return len(self.security_violations) > 0
    
    def is_script_safe(self) -> bool:
        """Check if script validation indicates safe execution."""
        return self.script_security_level in ['safe', 'warning'] if self.script_security_level else True


class ScriptExecutionResult(BaseModel):
    """Script execution result model."""
    
    success: bool = Field(..., description="Whether the script executed successfully")
    output: str = Field(default="", description="Standard output from script execution")
    errors: Optional[str] = Field(None, description="Error messages if execution failed")
    execution_time: float = Field(..., description="Time taken to execute the script in seconds")
    return_value: Optional[Any] = Field(None, description="Return value from the script if any")
    timestamp: Optional[str] = Field(None, description="Timestamp when script was executed")
    
    @validator('execution_time')
    def validate_execution_time(cls, v):
        """Validate execution time is non-negative."""
        if v < 0:
            raise ValueError("Execution time must be non-negative")
        return v
    
    @validator('timestamp', pre=True, always=True)
    def set_timestamp(cls, v):
        """Set timestamp if not provided."""
        if v is None:
            return datetime.now().isoformat()
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScriptValidationResult(BaseModel):
    """Script validation result model."""
    
    valid: bool = Field(..., description="Whether the script is valid")
    syntax_errors: List[str] = Field(default_factory=list, description="List of syntax errors found")
    security_violations: List[str] = Field(default_factory=list, description="List of security violations found")
    warnings: List[str] = Field(default_factory=list, description="List of warnings about the script")
    allowed_modules: List[str] = Field(default_factory=list, description="List of modules the script is allowed to use")
    restricted_functions: List[str] = Field(default_factory=list, description="List of restricted functions found in script")
    
    def add_syntax_error(self, error: str) -> None:
        """Add a syntax error."""
        self.valid = False
        self.syntax_errors.append(error)
    
    def add_security_violation(self, violation: str) -> None:
        """Add a security violation."""
        self.valid = False
        self.security_violations.append(violation)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning."""
        self.warnings.append(warning)
    
    def add_restricted_function(self, function: str) -> None:
        """Add a restricted function found in script."""
        self.restricted_functions.append(function)
        self.add_security_violation(f"Use of restricted function: {function}")


class LinkInfo(BaseModel):
    """Item link information model."""
    
    item_name: str = Field(..., description="Name of the linked item")
    channel_uid: str = Field(..., description="UID of the linked channel")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Link configuration parameters")
    auto_update: Optional[bool] = Field(None, description="Whether the link should auto-update the item")
    profile: Optional[str] = Field(None, description="Profile to use for the link")
    
    @validator('item_name')
    def validate_item_name(cls, v):
        """Validate item name format."""
        if not v or not v.strip():
            raise ValueError("Item name cannot be empty")
        if ' ' in v:
            raise ValueError("Item name cannot contain spaces")
        return v.strip()
    
    @validator('channel_uid')
    def validate_channel_uid(cls, v):
        """Validate channel UID format."""
        if not v or not v.strip():
            raise ValueError("Channel UID cannot be empty")
        # openHAB channel UIDs typically follow thing_uid:channel_id format
        if ':' not in v:
            raise ValueError("Channel UID must contain ':' separator")
        return v.strip()
    
    @validator('profile')
    def validate_profile(cls, v):
        """Validate profile format."""
        if v is not None and not v.strip():
            raise ValueError("Profile cannot be empty string")
        return v.strip() if v else None
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


class TransformationInfo(BaseModel):
    """Transformation information model."""
    
    id: str = Field(..., description="Unique identifier for the transformation")
    type: str = Field(..., description="Type of transformation (MAP, REGEX, JSONPATH, etc.)")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Transformation configuration parameters")
    description: Optional[str] = Field(None, description="Description of the transformation")
    file_path: Optional[str] = Field(None, description="File path for file-based transformations")
    pattern: Optional[str] = Field(None, description="Pattern for regex or other pattern-based transformations")
    
    @validator('id')
    def validate_id(cls, v):
        """Validate transformation ID format."""
        if not v or not v.strip():
            raise ValueError("Transformation ID cannot be empty")
        return v.strip()
    
    @validator('type')
    def validate_type(cls, v):
        """Validate transformation type."""
        valid_types = {
            'MAP', 'REGEX', 'JSONPATH', 'XPATH', 'JAVASCRIPT', 'SCALE', 
            'EXEC', 'JINJA', 'XSLT', 'ROLLERSHUTTER', 'BASICPROFILES'
        }
        if v.upper() not in valid_types:
            raise ValueError(f"Invalid transformation type: {v}. Must be one of {valid_types}")
        return v.upper()
    
    @validator('file_path')
    def validate_file_path(cls, v):
        """Validate file path format."""
        if v is not None and not v.strip():
            raise ValueError("File path cannot be empty string")
        return v.strip() if v else None
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


class TransformationTestResult(BaseModel):
    """Transformation test result model."""
    
    success: bool = Field(..., description="Whether the transformation test was successful")
    input_value: str = Field(..., description="Input value used for testing")
    output_value: Optional[str] = Field(None, description="Output value from transformation")
    error_message: Optional[str] = Field(None, description="Error message if transformation failed")
    execution_time: float = Field(..., description="Time taken to execute transformation in seconds")
    
    @validator('execution_time')
    def validate_execution_time(cls, v):
        """Validate execution time is non-negative."""
        if v < 0:
            raise ValueError("Execution time must be non-negative")
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


class UIPageInfo(BaseModel):
    """Main UI page information model."""
    
    id: str = Field(..., description="Unique identifier for the UI page")
    name: str = Field(..., description="Human-readable name of the page")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Page configuration parameters")
    widgets: List[Dict[str, Any]] = Field(default_factory=list, description="List of widgets on the page")
    layout: Dict[str, Any] = Field(default_factory=dict, description="Layout configuration for the page")
    icon: Optional[str] = Field(None, description="Icon for the page")
    order: Optional[int] = Field(None, description="Display order of the page")
    visible: bool = Field(True, description="Whether the page is visible in navigation")
    
    @validator('id')
    def validate_id(cls, v):
        """Validate page ID format."""
        if not v or not v.strip():
            raise ValueError("Page ID cannot be empty")
        return v.strip()
    
    @validator('name')
    def validate_name(cls, v):
        """Validate page name."""
        if not v or not v.strip():
            raise ValueError("Page name cannot be empty")
        return v.strip()
    
    @validator('order')
    def validate_order(cls, v):
        """Validate page order."""
        if v is not None and v < 0:
            raise ValueError("Page order must be non-negative")
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


class UIWidgetInfo(BaseModel):
    """UI widget information model."""
    
    id: str = Field(..., description="Unique identifier for the widget")
    type: str = Field(..., description="Type of widget (e.g., Label, Switch, Chart)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Widget properties and configuration")
    position: Dict[str, Any] = Field(default_factory=dict, description="Widget position and layout information")
    item: Optional[str] = Field(None, description="openHAB item associated with the widget")
    label: Optional[str] = Field(None, description="Display label for the widget")
    icon: Optional[str] = Field(None, description="Icon for the widget")
    visibility: Optional[Dict[str, Any]] = Field(None, description="Visibility conditions for the widget")
    
    @validator('id')
    def validate_id(cls, v):
        """Validate widget ID format."""
        if not v or not v.strip():
            raise ValueError("Widget ID cannot be empty")
        return v.strip()
    
    @validator('type')
    def validate_type(cls, v):
        """Validate widget type."""
        if not v or not v.strip():
            raise ValueError("Widget type cannot be empty")
        # Common openHAB Main UI widget types
        valid_types = {
            'Label', 'Switch', 'Slider', 'Selection', 'Setpoint', 'Rollershutter',
            'Colorpicker', 'Chart', 'Image', 'Video', 'Webview', 'Mapview',
            'Button', 'Input', 'Text', 'Frame', 'Group', 'Default'
        }
        if v not in valid_types:
            # Allow custom widget types but issue a warning in logs
            pass
        return v
    
    @validator('item')
    def validate_item(cls, v):
        """Validate item name format."""
        if v is not None:
            if not v.strip():
                raise ValueError("Item name cannot be empty string")
            if ' ' in v:
                raise ValueError("Item name cannot contain spaces")
        return v.strip() if v else None
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


class UIExportConfig(BaseModel):
    """UI configuration export model."""
    
    pages: List[UIPageInfo] = Field(..., description="List of UI pages to export")
    global_settings: Dict[str, Any] = Field(default_factory=dict, description="Global UI settings")
    export_timestamp: str = Field(..., description="Timestamp when the export was created")
    
    @validator('pages')
    def validate_pages(cls, v):
        """Validate that pages list is not empty."""
        if not v:
            raise ValueError("Export must contain at least one page")
        return v
    
    @validator('export_timestamp')
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if not v or not v.strip():
            raise ValueError("Export timestamp cannot be empty")
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


class ContainerHealthStatus(BaseModel):
    """Container health status model."""
    
    status: str = Field(..., description="Container health status (healthy, unhealthy, starting)")
    checks: Dict[str, bool] = Field(default_factory=dict, description="Individual health check results")
    uptime: float = Field(..., description="Container uptime in seconds")
    last_check: str = Field(..., description="Timestamp of last health check")
    memory_usage: Optional[float] = Field(None, description="Memory usage percentage")
    cpu_usage: Optional[float] = Field(None, description="CPU usage percentage")
    network_status: Optional[str] = Field(None, description="Network connectivity status")
    
    @validator('status')
    def validate_status(cls, v):
        """Validate container status."""
        valid_statuses = {'healthy', 'unhealthy', 'starting'}
        if v.lower() not in valid_statuses:
            raise ValueError(f"Invalid container status: {v}. Must be one of {valid_statuses}")
        return v.lower()
    
    @validator('uptime')
    def validate_uptime(cls, v):
        """Validate uptime is non-negative."""
        if v < 0:
            raise ValueError("Uptime must be non-negative")
        return v
    
    @validator('last_check')
    def validate_last_check(cls, v):
        """Validate last check timestamp."""
        if not v or not v.strip():
            raise ValueError("Last check timestamp cannot be empty")
        return v.strip()
    
    @validator('memory_usage')
    def validate_memory_usage(cls, v):
        """Validate memory usage percentage."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Memory usage must be between 0 and 100 percent")
        return v
    
    @validator('cpu_usage')
    def validate_cpu_usage(cls, v):
        """Validate CPU usage percentage."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("CPU usage must be between 0 and 100 percent")
        return v
    
    def add_health_check(self, check_name: str, result: bool) -> None:
        """Add a health check result."""
        self.checks[check_name] = result
    
    def is_healthy(self) -> bool:
        """Check if container is healthy based on all checks."""
        return self.status == 'healthy' and all(self.checks.values())
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


class ScriptContext(BaseModel):
    """Script execution context model."""
    
    allowed_modules: List[str] = Field(default_factory=list, description="List of modules allowed for import")
    restricted_functions: List[str] = Field(default_factory=list, description="List of restricted function names")
    timeout_seconds: int = Field(30, description="Maximum execution time in seconds")
    memory_limit_mb: Optional[int] = Field(None, description="Memory limit in megabytes")
    openhab_access: bool = Field(True, description="Whether script has access to openHAB APIs")
    log_level: str = Field("INFO", description="Logging level for script execution")
    
    @validator('timeout_seconds')
    def validate_timeout(cls, v):
        """Validate timeout is positive."""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        if v > 300:  # 5 minutes max
            raise ValueError("Timeout cannot exceed 300 seconds")
        return v
    
    @validator('memory_limit_mb')
    def validate_memory_limit(cls, v):
        """Validate memory limit."""
        if v is not None and v <= 0:
            raise ValueError("Memory limit must be positive")
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()
    
    def add_allowed_module(self, module_name: str) -> None:
        """Add an allowed module."""
        if module_name not in self.allowed_modules:
            self.allowed_modules.append(module_name)
    
    def add_restricted_function(self, function_name: str) -> None:
        """Add a restricted function."""
        if function_name not in self.restricted_functions:
            self.restricted_functions.append(function_name)
    
    def is_module_allowed(self, module_name: str) -> bool:
        """Check if a module is allowed for import."""
        return module_name in self.allowed_modules
    
    def is_function_restricted(self, function_name: str) -> bool:
        """Check if a function is restricted."""
        return function_name in self.restricted_functions


class LinkProfile(BaseModel):
    """Link profile information model."""
    
    id: str = Field(..., description="Unique identifier for the profile")
    name: str = Field(..., description="Human-readable name of the profile")
    description: Optional[str] = Field(None, description="Description of the profile")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Profile configuration parameters")
    supported_item_types: List[str] = Field(default_factory=list, description="List of supported item types")
    supported_channel_types: List[str] = Field(default_factory=list, description="List of supported channel types")
    
    @validator('id')
    def validate_id(cls, v):
        """Validate profile ID format."""
        if not v or not v.strip():
            raise ValueError("Profile ID cannot be empty")
        return v.strip()
    
    @validator('name')
    def validate_name(cls, v):
        """Validate profile name."""
        if not v or not v.strip():
            raise ValueError("Profile name cannot be empty")
        return v.strip()
    
    def supports_item_type(self, item_type: str) -> bool:
        """Check if profile supports a specific item type."""
        return item_type in self.supported_item_types or not self.supported_item_types
    
    def supports_channel_type(self, channel_type: str) -> bool:
        """Check if profile supports a specific channel type."""
        return channel_type in self.supported_channel_types or not self.supported_channel_types


class UILayoutConfig(BaseModel):
    """UI layout configuration model."""
    
    layout_type: str = Field(..., description="Type of layout (grid, masonry, list)")
    columns: Optional[int] = Field(None, description="Number of columns for grid layouts")
    responsive: bool = Field(True, description="Whether layout is responsive")
    breakpoints: Dict[str, int] = Field(default_factory=dict, description="Responsive breakpoints")
    spacing: Optional[int] = Field(None, description="Spacing between widgets")
    padding: Optional[int] = Field(None, description="Padding around widgets")
    
    @validator('layout_type')
    def validate_layout_type(cls, v):
        """Validate layout type."""
        valid_types = {'grid', 'masonry', 'list', 'flex'}
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid layout type: {v}. Must be one of {valid_types}")
        return v.lower()
    
    @validator('columns')
    def validate_columns(cls, v):
        """Validate column count."""
        if v is not None and (v < 1 or v > 12):
            raise ValueError("Columns must be between 1 and 12")
        return v
    
    @validator('spacing')
    def validate_spacing(cls, v):
        """Validate spacing value."""
        if v is not None and v < 0:
            raise ValueError("Spacing must be non-negative")
        return v
    
    @validator('padding')
    def validate_padding(cls, v):
        """Validate padding value."""
        if v is not None and v < 0:
            raise ValueError("Padding must be non-negative")
        return v
    
    def get_columns_for_breakpoint(self, breakpoint: str) -> Optional[int]:
        """Get column count for a specific breakpoint."""
        return self.breakpoints.get(breakpoint, self.columns)


class TransformationUsage(BaseModel):
    """Transformation usage tracking model."""
    
    transformation_id: str = Field(..., description="ID of the transformation")
    usage_locations: List[Dict[str, Any]] = Field(default_factory=list, description="List of locations where transformation is used")
    usage_count: int = Field(0, description="Total number of times transformation is used")
    last_used: Optional[str] = Field(None, description="Timestamp of last usage")
    
    @validator('transformation_id')
    def validate_transformation_id(cls, v):
        """Validate transformation ID."""
        if not v or not v.strip():
            raise ValueError("Transformation ID cannot be empty")
        return v.strip()
    
    @validator('usage_count')
    def validate_usage_count(cls, v):
        """Validate usage count is non-negative."""
        if v < 0:
            raise ValueError("Usage count must be non-negative")
        return v
    
    def add_usage_location(self, location_type: str, location_id: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Add a usage location."""
        location = {
            'type': location_type,
            'id': location_id,
            'details': details or {}
        }
        if location not in self.usage_locations:
            self.usage_locations.append(location)
            self.usage_count = len(self.usage_locations)
    
    def remove_usage_location(self, location_type: str, location_id: str) -> None:
        """Remove a usage location."""
        self.usage_locations = [
            loc for loc in self.usage_locations 
            if not (loc['type'] == location_type and loc['id'] == location_id)
        ]
        self.usage_count = len(self.usage_locations)
    
    def is_used(self) -> bool:
        """Check if transformation is currently used anywhere."""
        return self.usage_count > 0