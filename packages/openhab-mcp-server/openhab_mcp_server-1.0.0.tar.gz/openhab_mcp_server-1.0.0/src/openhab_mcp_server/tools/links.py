"""
Link management tools for openHAB MCP server.

This module provides MCP tools for managing item links in openHAB,
including listing, creating, updating, and deleting links between
items and channels.
"""

import logging
from typing import Any, Dict, List, Optional

from mcp.types import TextContent

from openhab_mcp_server.models import LinkInfo, ValidationResult
from openhab_mcp_server.utils.openhab_client import OpenHABClient
from openhab_mcp_server.utils.config import get_config
from openhab_mcp_server.utils.logging import get_logger, LogCategory


logger = logging.getLogger(__name__)
structured_logger = get_logger("link_tools")


class LinkListTool:
    """List item links with filtering options."""
    
    @staticmethod
    async def execute(
        item_name: Optional[str] = None,
        channel_uid: Optional[str] = None
    ) -> List[TextContent]:
        """Get links associated with specific items or channels.
        
        Args:
            item_name: Optional item name to filter by
            channel_uid: Optional channel UID to filter by
            
        Returns:
            List of TextContent with link information
        """
        try:
            structured_logger.info(
                f"Listing links with filters - item: {item_name}, channel: {channel_uid}",
                category=LogCategory.TOOL_EXECUTION
            )
            
            async with OpenHABClient(get_config()) as client:
                links = await client.get_links(item_name=item_name, channel_uid=channel_uid)
                
                if not links:
                    filter_desc = []
                    if item_name:
                        filter_desc.append(f"item '{item_name}'")
                    if channel_uid:
                        filter_desc.append(f"channel '{channel_uid}'")
                    
                    filter_text = " and ".join(filter_desc) if filter_desc else "any criteria"
                    
                    structured_logger.info(
                        f"No links found matching {filter_text}",
                        category=LogCategory.TOOL_EXECUTION
                    )
                    
                    return [TextContent(
                        type="text",
                        text=f"No links found matching {filter_text}."
                    )]
                
                # Format links for display
                link_list = []
                for link in links:
                    link_info = f"• Item: {link.get('itemName', 'Unknown')}"
                    link_info += f"\n  Channel: {link.get('channelUID', 'Unknown')}"
                    
                    config = link.get('configuration', {})
                    if config:
                        link_info += f"\n  Configuration: {config}"
                    
                    link_list.append(link_info)
                
                result_text = f"Found {len(links)} link(s):\n\n" + "\n\n".join(link_list)
                
                structured_logger.info(
                    f"Successfully listed {len(links)} links",
                    category=LogCategory.TOOL_EXECUTION
                )
                
                return [TextContent(type="text", text=result_text)]
                
        except Exception as e:
            error_msg = f"Failed to list links: {str(e)}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]


class LinkCreateTool:
    """Create new item links."""
    
    @staticmethod
    def _validate_link_input(item_name: str, channel_uid: str) -> ValidationResult:
        """Validate link creation input parameters.
        
        Args:
            item_name: Name of the item
            channel_uid: UID of the channel
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        # Validate item name
        if not item_name or not item_name.strip():
            result.add_error("Item name cannot be empty")
        elif ' ' in item_name:
            result.add_error("Item name cannot contain spaces")
        
        # Validate channel UID
        if not channel_uid or not channel_uid.strip():
            result.add_error("Channel UID cannot be empty")
        elif ':' not in channel_uid:
            result.add_error("Channel UID must contain ':' separator (format: thing_uid:channel_id)")
        else:
            # Check that channel UID has at least 2 parts
            parts = channel_uid.split(':')
            if len(parts) < 2:
                result.add_error("Channel UID must have at least thing UID and channel ID")
            elif any(not part.strip() for part in parts):
                result.add_error("Channel UID parts cannot be empty")
        
        return result
    
    @staticmethod
    async def execute(
        item_name: str,
        channel_uid: str,
        configuration: Optional[Dict[str, Any]] = None
    ) -> List[TextContent]:
        """Create link between channel and item with validation.
        
        Args:
            item_name: Name of the item to link
            channel_uid: UID of the channel to link
            configuration: Optional configuration parameters
            
        Returns:
            List of TextContent with creation result
        """
        try:
            structured_logger.info(
                f"Creating link between item '{item_name}' and channel '{channel_uid}'",
                category=LogCategory.TOOL_EXECUTION
            )
            
            # Validate input parameters
            validation = LinkCreateTool._validate_link_input(item_name, channel_uid)
            if not validation.is_valid:
                error_msg = "Link creation validation failed:\n" + "\n".join(validation.errors)
                structured_logger.error(
                    error_msg,
                    category=LogCategory.TOOL_EXECUTION
                )
                return [TextContent(type="text", text=error_msg)]
            
            async with OpenHABClient(get_config()) as client:
                success = await client.create_link(item_name, channel_uid, configuration)
                
                if success:
                    result_text = f"Successfully created link between item '{item_name}' and channel '{channel_uid}'"
                    if configuration:
                        result_text += f" with configuration: {configuration}"
                    
                    structured_logger.info(
                        "Link created successfully",
                        category=LogCategory.TOOL_EXECUTION
                    )
                else:
                    result_text = f"Failed to create link between item '{item_name}' and channel '{channel_uid}'"
                    structured_logger.error(
                        "Link creation failed",
                        category=LogCategory.TOOL_EXECUTION
                    )
                
                return [TextContent(type="text", text=result_text)]
                
        except Exception as e:
            error_msg = f"Failed to create link: {str(e)}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]


class LinkUpdateTool:
    """Update existing link configuration."""
    
    @staticmethod
    async def execute(
        item_name: str,
        channel_uid: str,
        configuration: Dict[str, Any]
    ) -> List[TextContent]:
        """Update link configuration and transformation settings.
        
        Args:
            item_name: Name of the linked item
            channel_uid: UID of the linked channel
            configuration: New configuration parameters
            
        Returns:
            List of TextContent with update result
        """
        try:
            structured_logger.info(
                f"Updating link configuration between item '{item_name}' and channel '{channel_uid}'",
                category=LogCategory.TOOL_EXECUTION
            )
            
            # Validate input parameters
            validation = LinkCreateTool._validate_link_input(item_name, channel_uid)
            if not validation.is_valid:
                error_msg = "Link update validation failed:\n" + "\n".join(validation.errors)
                structured_logger.error(
                    error_msg,
                    category=LogCategory.TOOL_EXECUTION
                )
                return [TextContent(type="text", text=error_msg)]
            
            if not configuration:
                error_msg = "Configuration cannot be empty for link update"
                structured_logger.error(
                    error_msg,
                    category=LogCategory.TOOL_EXECUTION
                )
                return [TextContent(type="text", text=error_msg)]
            
            async with OpenHABClient(get_config()) as client:
                success = await client.update_link(item_name, channel_uid, configuration)
                
                if success:
                    result_text = f"Successfully updated link configuration between item '{item_name}' and channel '{channel_uid}'"
                    result_text += f"\nNew configuration: {configuration}"
                    
                    structured_logger.info(
                        "Link configuration updated successfully",
                        category=LogCategory.TOOL_EXECUTION
                    )
                else:
                    result_text = f"Failed to update link configuration between item '{item_name}' and channel '{channel_uid}'"
                    structured_logger.error(
                        "Link configuration update failed",
                        category=LogCategory.TOOL_EXECUTION
                    )
                
                return [TextContent(type="text", text=result_text)]
                
        except Exception as e:
            error_msg = f"Failed to update link configuration: {str(e)}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]


class LinkDeleteTool:
    """Remove item links."""
    
    @staticmethod
    async def execute(
        item_name: str,
        channel_uid: str
    ) -> List[TextContent]:
        """Delete link and validate removal.
        
        Args:
            item_name: Name of the linked item
            channel_uid: UID of the linked channel
            
        Returns:
            List of TextContent with deletion result
        """
        try:
            structured_logger.info(
                f"Deleting link between item '{item_name}' and channel '{channel_uid}'",
                category=LogCategory.TOOL_EXECUTION
            )
            
            # Validate input parameters
            validation = LinkCreateTool._validate_link_input(item_name, channel_uid)
            if not validation.is_valid:
                error_msg = "Link deletion validation failed:\n" + "\n".join(validation.errors)
                structured_logger.error(
                    error_msg,
                    category=LogCategory.TOOL_EXECUTION
                )
                return [TextContent(type="text", text=error_msg)]
            
            async with OpenHABClient(get_config()) as client:
                success = await client.delete_link(item_name, channel_uid)
                
                if success:
                    result_text = f"Successfully deleted link between item '{item_name}' and channel '{channel_uid}'"
                    
                    structured_logger.info(
                        "Link deleted successfully",
                        category=LogCategory.TOOL_EXECUTION
                    )
                else:
                    result_text = f"Failed to delete link between item '{item_name}' and channel '{channel_uid}'"
                    structured_logger.error(
                        "Link deletion failed",
                        category=LogCategory.TOOL_EXECUTION
                    )
                
                return [TextContent(type="text", text=result_text)]
                
        except Exception as e:
            error_msg = f"Failed to delete link: {str(e)}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]