"""
MCP tool implementations for openHAB item operations.

This module provides MCP tools for interacting with openHAB items including
retrieving states, sending commands, and listing items with filtering capabilities.
"""

import logging
from typing import Any, Dict, List, Optional

from mcp.types import TextContent

from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.utils.security import InputSanitizer, SecurityLogger
from openhab_mcp_server.models import ItemState, ValidationResult


logger = logging.getLogger(__name__)


class ItemStateTool:
    """Get current state of openHAB items."""
    
    def __init__(self, config: Config):
        """Initialize the tool with configuration.
        
        Args:
            config: Configuration object for openHAB connection
        """
        self.config = config
    
    async def execute(self, item_name: str) -> List[TextContent]:
        """Retrieve item state from openHAB.
        
        Args:
            item_name: Name of the openHAB item
            
        Returns:
            List containing item state information as TextContent
            
        Raises:
            ValueError: If item_name is invalid
        """
        # Validate input
        validation = self._validate_item_name(item_name)
        if not validation.is_valid:
            return [TextContent(
                type="text",
                text=f"Invalid item name: {', '.join(validation.errors)}"
            )]
        
        # Get item state from openHAB
        async with OpenHABClient(self.config) as client:
            try:
                item_data = await client.get_item_state(item_name)
                
                if item_data is None:
                    return [TextContent(
                        type="text",
                        text=f"Item '{item_name}' not found"
                    )]
                
                # Format response
                return [TextContent(
                    type="text",
                    text=self._format_item_state(item_data)
                )]
                
            except OpenHABError as e:
                logger.error(f"Error getting item state for '{item_name}': {e}")
                return [TextContent(
                    type="text",
                    text=f"Error retrieving item state: {e}"
                )]
    
    def _validate_item_name(self, item_name: str) -> ValidationResult:
        """Validate item name format with security checks.
        
        Args:
            item_name: Item name to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = InputSanitizer.validate_item_name(item_name)
        
        if not result.is_valid:
            SecurityLogger.log_validation_failure("item_name", item_name, result.errors)
        
        return result
    
    def _format_item_state(self, item_data: Dict[str, Any]) -> str:
        """Format item state data for display.
        
        Args:
            item_data: Raw item data from openHAB API
            
        Returns:
            Formatted string representation of item state
        """
        lines = [
            f"Item: {item_data.get('name', 'Unknown')}",
            f"State: {item_data.get('state', 'UNDEF')}",
            f"Type: {item_data.get('type', 'Unknown')}"
        ]
        
        if item_data.get('label'):
            lines.append(f"Label: {item_data['label']}")
        
        if item_data.get('category'):
            lines.append(f"Category: {item_data['category']}")
        
        if item_data.get('tags'):
            lines.append(f"Tags: {', '.join(item_data['tags'])}")
        
        if item_data.get('groupNames'):
            lines.append(f"Groups: {', '.join(item_data['groupNames'])}")
        
        return "\n".join(lines)


class ItemCommandTool:
    """Send commands to openHAB items."""
    
    def __init__(self, config: Config):
        """Initialize the tool with configuration.
        
        Args:
            config: Configuration object for openHAB connection
        """
        self.config = config
    
    async def execute(self, item_name: str, command: str) -> List[TextContent]:
        """Send command to item and return success status.
        
        Args:
            item_name: Name of the openHAB item
            command: Command to send to the item
            
        Returns:
            List containing command execution result as TextContent
        """
        # Validate inputs
        name_validation = self._validate_item_name(item_name)
        command_validation = self._validate_command(command)
        
        errors = []
        if not name_validation.is_valid:
            errors.extend([f"Item name: {error}" for error in name_validation.errors])
        if not command_validation.is_valid:
            errors.extend([f"Command: {error}" for error in command_validation.errors])
        
        if errors:
            return [TextContent(
                type="text",
                text=f"Validation errors:\n" + "\n".join(errors)
            )]
        
        # Send command to openHAB
        async with OpenHABClient(self.config) as client:
            try:
                success = await client.send_item_command(item_name, command)
                
                if success:
                    return [TextContent(
                        type="text",
                        text=f"Successfully sent command '{command}' to item '{item_name}'"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Failed to send command '{command}' to item '{item_name}'"
                    )]
                    
            except OpenHABError as e:
                logger.error(f"Error sending command to '{item_name}': {e}")
                return [TextContent(
                    type="text",
                    text=f"Error sending command: {e}"
                )]
    
    def _validate_item_name(self, item_name: str) -> ValidationResult:
        """Validate item name format with security checks.
        
        Args:
            item_name: Item name to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = InputSanitizer.validate_item_name(item_name)
        
        if not result.is_valid:
            SecurityLogger.log_validation_failure("item_name", item_name, result.errors)
        
        return result
    
    def _validate_command(self, command: str) -> ValidationResult:
        """Validate command format with security checks.
        
        Args:
            command: Command to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = InputSanitizer.validate_command(command)
        
        if not result.is_valid:
            SecurityLogger.log_validation_failure("command", command, result.errors)
        
        return result


class ItemListTool:
    """List all openHAB items with filtering capabilities."""
    
    def __init__(self, config: Config):
        """Initialize the tool with configuration.
        
        Args:
            config: Configuration object for openHAB connection
        """
        self.config = config
    
    async def execute(self, item_type: Optional[str] = None) -> List[TextContent]:
        """Get filtered list of items.
        
        Args:
            item_type: Optional filter by item type (e.g., 'Switch', 'Dimmer')
            
        Returns:
            List containing formatted item list as TextContent
        """
        # Validate item type if provided
        if item_type is not None:
            validation = self._validate_item_type(item_type)
            if not validation.is_valid:
                return [TextContent(
                    type="text",
                    text=f"Invalid item type: {', '.join(validation.errors)}"
                )]
        
        # Get items from openHAB
        async with OpenHABClient(self.config) as client:
            try:
                items = await client.get_items(item_type)
                
                if not items:
                    filter_text = f" of type '{item_type}'" if item_type else ""
                    return [TextContent(
                        type="text",
                        text=f"No items found{filter_text}"
                    )]
                
                # Format response
                return [TextContent(
                    type="text",
                    text=self._format_item_list(items, item_type)
                )]
                
            except OpenHABError as e:
                logger.error(f"Error listing items: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error listing items: {e}"
                )]
    
    def _validate_item_type(self, item_type: str) -> ValidationResult:
        """Validate item type.
        
        Args:
            item_type: Item type to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        if not item_type or not item_type.strip():
            result.add_error("Item type cannot be empty")
            return result
        
        valid_types = {
            'Switch', 'Dimmer', 'Number', 'String', 'DateTime', 'Contact',
            'Rollershutter', 'Color', 'Location', 'Player', 'Group'
        }
        
        if item_type not in valid_types:
            result.add_error(f"Invalid item type '{item_type}'. Valid types: {', '.join(sorted(valid_types))}")
        
        return result
    
    def _format_item_list(self, items: List[Dict[str, Any]], item_type: Optional[str]) -> str:
        """Format item list for display.
        
        Args:
            items: List of item data from openHAB API
            item_type: Filter type used (for header)
            
        Returns:
            Formatted string representation of item list
        """
        header = f"Found {len(items)} items"
        if item_type:
            header += f" of type '{item_type}'"
        header += ":"
        
        item_lines = []
        for item in items:
            item_info = (
                f"• {item.get('name', 'Unknown')} "
                f"({item.get('type', 'Unknown')}) - "
                f"State: {item.get('state', 'UNDEF')}"
            )
            
            if item.get('label'):
                item_info += f" - {item['label']}"
            
            item_lines.append(item_info)
        
        return header + "\n" + "\n".join(item_lines)