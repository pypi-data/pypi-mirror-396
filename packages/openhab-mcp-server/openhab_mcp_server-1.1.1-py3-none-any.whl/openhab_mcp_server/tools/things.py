"""
MCP tool implementations for openHAB thing operations.

This module provides MCP tools for interacting with openHAB things including
retrieving status, updating configurations, and discovering new devices.
"""

import logging
from typing import Any, Dict, List, Optional

from mcp.types import TextContent

from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.utils.security import InputSanitizer, SecurityLogger
from openhab_mcp_server.models import ThingStatus, ValidationResult


logger = logging.getLogger(__name__)


class ThingStatusTool:
    """Get status and configuration of openHAB things."""
    
    def __init__(self, config: Config):
        """Initialize the tool with configuration.
        
        Args:
            config: Configuration object for openHAB connection
        """
        self.config = config
    
    async def execute(self, thing_uid: str) -> List[TextContent]:
        """Retrieve thing status and configuration from openHAB.
        
        Args:
            thing_uid: UID of the openHAB thing
            
        Returns:
            List containing thing status information as TextContent
            
        Raises:
            ValueError: If thing_uid is invalid
        """
        # Validate input
        validation = self._validate_thing_uid(thing_uid)
        if not validation.is_valid:
            return [TextContent(
                type="text",
                text=f"Invalid thing UID: {', '.join(validation.errors)}"
            )]
        
        # Get thing status from openHAB
        async with OpenHABClient(self.config) as client:
            try:
                thing_data = await client.get_thing_status(thing_uid)
                
                if thing_data is None:
                    return [TextContent(
                        type="text",
                        text=f"Thing '{thing_uid}' not found"
                    )]
                
                # Format response
                return [TextContent(
                    type="text",
                    text=self._format_thing_status(thing_data)
                )]
                
            except OpenHABError as e:
                logger.error(f"Error getting thing status for '{thing_uid}': {e}")
                return [TextContent(
                    type="text",
                    text=f"Error retrieving thing status: {e}"
                )]
    
    def _validate_thing_uid(self, thing_uid: str) -> ValidationResult:
        """Validate thing UID format with security checks.
        
        Args:
            thing_uid: Thing UID to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = InputSanitizer.validate_thing_uid(thing_uid)
        
        if not result.is_valid:
            SecurityLogger.log_validation_failure("thing_uid", thing_uid, result.errors)
        
        return result
    
    def _format_thing_status(self, thing_data: Dict[str, Any]) -> str:
        """Format thing status data for display.
        
        Args:
            thing_data: Raw thing data from openHAB API
            
        Returns:
            Formatted string representation of thing status
        """
        lines = [
            f"Thing: {thing_data.get('UID', 'Unknown')}",
            f"Status: {thing_data.get('statusInfo', {}).get('status', 'UNKNOWN')}",
            f"Status Detail: {thing_data.get('statusInfo', {}).get('statusDetail', 'NONE')}"
        ]
        
        if thing_data.get('label'):
            lines.append(f"Label: {thing_data['label']}")
        
        if thing_data.get('thingTypeUID'):
            lines.append(f"Type: {thing_data['thingTypeUID']}")
        
        if thing_data.get('bridgeUID'):
            lines.append(f"Bridge: {thing_data['bridgeUID']}")
        
        # Configuration information
        config = thing_data.get('configuration', {})
        if config:
            lines.append("\nConfiguration:")
            for key, value in config.items():
                # Don't expose sensitive information like passwords
                if any(sensitive in key.lower() for sensitive in ['password', 'token', 'secret', 'key']):
                    value = "***"
                lines.append(f"  {key}: {value}")
        
        # Channel information
        channels = thing_data.get('channels', [])
        if channels:
            lines.append(f"\nChannels ({len(channels)}):")
            for channel in channels[:10]:  # Limit to first 10 channels
                channel_uid = channel.get('uid', 'Unknown')
                channel_type = channel.get('channelTypeUID', 'Unknown')
                lines.append(f"  • {channel_uid} ({channel_type})")
            
            if len(channels) > 10:
                lines.append(f"  ... and {len(channels) - 10} more channels")
        
        return "\n".join(lines)


class ThingConfigTool:
    """Update thing configuration parameters."""
    
    def __init__(self, config: Config):
        """Initialize the tool with configuration.
        
        Args:
            config: Configuration object for openHAB connection
        """
        self.config = config
    
    async def execute(self, thing_uid: str, configuration: Dict[str, Any]) -> List[TextContent]:
        """Update thing configuration and validate changes.
        
        Args:
            thing_uid: UID of the openHAB thing
            configuration: Configuration parameters to update
            
        Returns:
            List containing configuration update result as TextContent
        """
        # Validate inputs
        uid_validation = self._validate_thing_uid(thing_uid)
        config_validation = self._validate_configuration(configuration)
        
        errors = []
        if not uid_validation.is_valid:
            errors.extend([f"Thing UID: {error}" for error in uid_validation.errors])
        if not config_validation.is_valid:
            errors.extend([f"Configuration: {error}" for error in config_validation.errors])
        
        if errors:
            return [TextContent(
                type="text",
                text=f"Validation errors:\n" + "\n".join(errors)
            )]
        
        # Update thing configuration in openHAB
        async with OpenHABClient(self.config) as client:
            try:
                # First check if thing exists
                existing_thing = await client.get_thing_status(thing_uid)
                if existing_thing is None:
                    return [TextContent(
                        type="text",
                        text=f"Thing '{thing_uid}' not found"
                    )]
                
                # Update configuration
                success = await client.update_thing_config(thing_uid, configuration)
                
                if success:
                    # Verify the update by retrieving the thing again
                    updated_thing = await client.get_thing_status(thing_uid)
                    updated_config = updated_thing.get('configuration', {}) if updated_thing else {}
                    
                    # Check if our changes were applied
                    applied_changes = []
                    for key, value in configuration.items():
                        if key in updated_config and updated_config[key] == value:
                            applied_changes.append(f"  {key}: {value}")
                    
                    result_text = f"Successfully updated configuration for thing '{thing_uid}'"
                    if applied_changes:
                        result_text += f"\n\nApplied changes:\n" + "\n".join(applied_changes)
                    
                    return [TextContent(
                        type="text",
                        text=result_text
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Failed to update configuration for thing '{thing_uid}'"
                    )]
                    
            except OpenHABError as e:
                logger.error(f"Error updating configuration for '{thing_uid}': {e}")
                return [TextContent(
                    type="text",
                    text=f"Error updating configuration: {e}"
                )]
    
    def _validate_thing_uid(self, thing_uid: str) -> ValidationResult:
        """Validate thing UID format with security checks.
        
        Args:
            thing_uid: Thing UID to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = InputSanitizer.validate_thing_uid(thing_uid)
        
        if not result.is_valid:
            SecurityLogger.log_validation_failure("thing_uid", thing_uid, result.errors)
        
        return result
    
    def _validate_configuration(self, configuration: Dict[str, Any]) -> ValidationResult:
        """Validate configuration parameters with security checks.
        
        Args:
            configuration: Configuration to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # Use security sanitizer to validate configuration
            InputSanitizer.sanitize_configuration(configuration)
        except ValueError as e:
            result.add_error(str(e))
            SecurityLogger.log_validation_failure("configuration", str(configuration), [str(e)])
        
        return result


class ThingDiscoveryTool:
    """Trigger discovery for new things."""
    
    def __init__(self, config: Config):
        """Initialize the tool with configuration.
        
        Args:
            config: Configuration object for openHAB connection
        """
        self.config = config
    
    async def execute(self, binding_id: str) -> List[TextContent]:
        """Trigger discovery and return discovered devices with their capabilities.
        
        Args:
            binding_id: ID of the binding to discover for
            
        Returns:
            List containing discovery results as TextContent
        """
        # Validate input
        validation = self._validate_binding_id(binding_id)
        if not validation.is_valid:
            return [TextContent(
                type="text",
                text=f"Invalid binding ID: {', '.join(validation.errors)}"
            )]
        
        # Trigger discovery in openHAB
        async with OpenHABClient(self.config) as client:
            try:
                discovered_things = await client.discover_things(binding_id)
                
                if not discovered_things:
                    return [TextContent(
                        type="text",
                        text=f"No new devices discovered for binding '{binding_id}'"
                    )]
                
                # Format response
                return [TextContent(
                    type="text",
                    text=self._format_discovery_results(discovered_things, binding_id)
                )]
                
            except OpenHABError as e:
                logger.error(f"Error discovering things for binding '{binding_id}': {e}")
                return [TextContent(
                    type="text",
                    text=f"Error during discovery: {e}"
                )]
    
    def _validate_binding_id(self, binding_id: str) -> ValidationResult:
        """Validate binding ID format with security checks.
        
        Args:
            binding_id: Binding ID to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = InputSanitizer.validate_binding_id(binding_id)
        
        if not result.is_valid:
            SecurityLogger.log_validation_failure("binding_id", binding_id, result.errors)
        
        return result
    
    def _format_discovery_results(self, discovered_things: List[Dict[str, Any]], binding_id: str) -> str:
        """Format discovery results for display.
        
        Args:
            discovered_things: List of discovered thing data from openHAB API
            binding_id: Binding ID used for discovery
            
        Returns:
            Formatted string representation of discovery results
        """
        header = f"Discovery results for binding '{binding_id}' ({len(discovered_things)} devices found):"
        
        if not discovered_things:
            return f"No new devices discovered for binding '{binding_id}'"
        
        thing_lines = []
        for thing in discovered_things:
            thing_uid = thing.get('thingUID', 'Unknown')
            label = thing.get('label', 'No label')
            thing_type = thing.get('thingTypeUID', 'Unknown type')
            
            thing_info = f"• {thing_uid}"
            if label != 'No label':
                thing_info += f" - {label}"
            thing_info += f" ({thing_type})"
            
            # Add properties if available
            properties = thing.get('properties', {})
            if properties:
                prop_items = []
                for key, value in list(properties.items())[:3]:  # Show first 3 properties
                    prop_items.append(f"{key}: {value}")
                if prop_items:
                    thing_info += f"\n    Properties: {', '.join(prop_items)}"
                if len(properties) > 3:
                    thing_info += f" (and {len(properties) - 3} more)"
            
            thing_lines.append(thing_info)
        
        return header + "\n\n" + "\n\n".join(thing_lines)