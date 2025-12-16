"""
MCP tools for openHAB addon management.

This module provides tools for managing openHAB addons including listing,
installing, uninstalling, and configuring addons.
"""

import logging
from typing import Any, Dict, List, Optional

from mcp.types import TextContent
from pydantic import BaseModel, Field

from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError
from openhab_mcp_server.models import AddonInfo, MCPError
from openhab_mcp_server.utils.config import get_config, Config
from openhab_mcp_server.utils.logging import get_logger, LogCategory

logger = logging.getLogger(__name__)
structured_logger = get_logger("addon_tools")


class AddonListParams(BaseModel):
    """Parameters for addon listing."""
    
    filter_type: Optional[str] = Field(
        None, 
        description="Filter addons by type (binding, transformation, persistence, automation, voice, ui, misc, io)"
    )
    installed_only: Optional[bool] = Field(
        False,
        description="If true, only return installed addons"
    )
    available_only: Optional[bool] = Field(
        False,
        description="If true, only return available (not installed) addons"
    )


class AddonInstallParams(BaseModel):
    """Parameters for addon installation."""
    
    addon_id: str = Field(..., description="ID of the addon to install")


class AddonUninstallParams(BaseModel):
    """Parameters for addon uninstallation."""
    
    addon_id: str = Field(..., description="ID of the addon to uninstall")


class AddonConfigParams(BaseModel):
    """Parameters for addon configuration."""
    
    addon_id: str = Field(..., description="ID of the addon to configure")
    config: Dict[str, Any] = Field(..., description="Configuration parameters to update")


class AddonListTool:
    """Tool for listing available and installed openHAB addons."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the addon list tool."""
        self.config = config or get_config()
    
    async def execute(self, params: AddonListParams) -> List[TextContent]:
        """Execute the addon list tool.
        
        Args:
            params: Tool parameters
            
        Returns:
            List of text content with addon information
        """
        try:
            structured_logger.info(
                "Listing addons",
                category=LogCategory.TOOL_EXECUTION
            )
            
            async with OpenHABClient(self.config) as client:
                # Get all addons
                addons = await client.get_addons(params.filter_type)
                
                # Apply additional filters
                if params.installed_only:
                    addons = [addon for addon in addons if addon.get('installed', False)]
                elif params.available_only:
                    addons = [addon for addon in addons if not addon.get('installed', False)]
                
                # Validate and format addon data
                formatted_addons = []
                for addon_data in addons:
                    try:
                        # Create AddonInfo model for validation
                        addon = AddonInfo(
                            id=addon_data.get('id', ''),
                            name=addon_data.get('name', addon_data.get('label', '')),
                            version=addon_data.get('version'),
                            description=addon_data.get('description'),
                            installed=addon_data.get('installed', False),
                            type=addon_data.get('type', 'misc'),
                            author=addon_data.get('author'),
                            configuration=addon_data.get('configuration', {})
                        )
                        formatted_addons.append(addon.dict())
                    except Exception as e:
                        structured_logger.warning(
                            f"Skipping invalid addon data: {e}",
                            category=LogCategory.TOOL_EXECUTION,
                            addon_id=addon_data.get('id', 'unknown')
                        )
                        continue
                
                # Create response
                if not formatted_addons:
                    message = "No addons found"
                    if params.filter_type:
                        message += f" for type '{params.filter_type}'"
                    if params.installed_only:
                        message += " (installed only)"
                    elif params.available_only:
                        message += " (available only)"
                else:
                    status_filter = ""
                    if params.installed_only:
                        status_filter = " (installed)"
                    elif params.available_only:
                        status_filter = " (available)"
                    
                    type_filter = f" of type '{params.filter_type}'" if params.filter_type else ""
                    message = f"Found {len(formatted_addons)} addon(s){type_filter}{status_filter}:\n\n"
                    
                    for addon in formatted_addons:
                        status = "✓ Installed" if addon['installed'] else "○ Available"
                        version_info = f" v{addon['version']}" if addon['version'] else ""
                        author_info = f" by {addon['author']}" if addon['author'] else ""
                        
                        message += f"• {addon['name']} ({addon['id']}){version_info}\n"
                        message += f"  Type: {addon['type'].title()}\n"
                        message += f"  Status: {status}\n"
                        if addon['description']:
                            message += f"  Description: {addon['description']}\n"
                        if author_info:
                            message += f"  Author: {addon['author']}\n"
                        message += "\n"
                
                structured_logger.info(
                    f"Successfully listed {len(formatted_addons)} addons",
                    category=LogCategory.TOOL_EXECUTION
                )
                
                return [TextContent(type="text", text=message)]
                
        except OpenHABError as e:
            error_msg = f"Failed to list addons: {e}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"Unexpected error listing addons: {e}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]


class AddonInstallTool:
    """Tool for installing openHAB addons."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the addon install tool."""
        self.config = config or get_config()
    
    async def execute(self, params: AddonInstallParams) -> List[TextContent]:
        """Execute the addon install tool.
        
        Args:
            params: Tool parameters
            
        Returns:
            List of text content with installation result
        """
        try:
            structured_logger.info(
                f"Installing addon '{params.addon_id}'",
                category=LogCategory.TOOL_EXECUTION
            )
            
            async with OpenHABClient(self.config) as client:
                # Check if addon exists and is not already installed
                addons = await client.get_addons()
                target_addon = None
                
                for addon in addons:
                    if addon.get('id') == params.addon_id:
                        target_addon = addon
                        break
                
                if not target_addon:
                    error_msg = f"Addon '{params.addon_id}' not found in registry"
                    structured_logger.warning(
                        error_msg,
                        category=LogCategory.TOOL_EXECUTION
                    )
                    return [TextContent(type="text", text=error_msg)]
                
                if target_addon.get('installed', False):
                    message = f"Addon '{params.addon_id}' is already installed"
                    structured_logger.info(
                        message,
                        category=LogCategory.TOOL_EXECUTION
                    )
                    return [TextContent(type="text", text=message)]
                
                # Install the addon
                success = await client.install_addon(params.addon_id)
                
                if success:
                    message = f"Successfully installed addon '{params.addon_id}'"
                    addon_name = target_addon.get('name', params.addon_id)
                    if addon_name != params.addon_id:
                        message += f" ({addon_name})"
                    
                    structured_logger.info(
                        message,
                        category=LogCategory.TOOL_EXECUTION
                    )
                else:
                    message = f"Failed to install addon '{params.addon_id}'"
                    structured_logger.error(
                        message,
                        category=LogCategory.TOOL_EXECUTION
                    )
                
                return [TextContent(type="text", text=message)]
                
        except OpenHABError as e:
            error_msg = f"Failed to install addon '{params.addon_id}': {e}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"Unexpected error installing addon '{params.addon_id}': {e}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]


class AddonUninstallTool:
    """Tool for uninstalling openHAB addons."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the addon uninstall tool."""
        self.config = config or get_config()
    
    async def execute(self, params: AddonUninstallParams) -> List[TextContent]:
        """Execute the addon uninstall tool.
        
        Args:
            params: Tool parameters
            
        Returns:
            List of text content with uninstallation result
        """
        try:
            structured_logger.info(
                f"Uninstalling addon '{params.addon_id}'",
                category=LogCategory.TOOL_EXECUTION
            )
            
            async with OpenHABClient(self.config) as client:
                # Check if addon exists and is installed
                addons = await client.get_addons()
                target_addon = None
                
                for addon in addons:
                    if addon.get('id') == params.addon_id:
                        target_addon = addon
                        break
                
                if not target_addon:
                    error_msg = f"Addon '{params.addon_id}' not found"
                    structured_logger.warning(
                        error_msg,
                        category=LogCategory.TOOL_EXECUTION
                    )
                    return [TextContent(type="text", text=error_msg)]
                
                if not target_addon.get('installed', False):
                    message = f"Addon '{params.addon_id}' is not installed"
                    structured_logger.info(
                        message,
                        category=LogCategory.TOOL_EXECUTION
                    )
                    return [TextContent(type="text", text=message)]
                
                # Uninstall the addon
                success = await client.uninstall_addon(params.addon_id)
                
                if success:
                    message = f"Successfully uninstalled addon '{params.addon_id}'"
                    addon_name = target_addon.get('name', params.addon_id)
                    if addon_name != params.addon_id:
                        message += f" ({addon_name})"
                    
                    structured_logger.info(
                        message,
                        category=LogCategory.TOOL_EXECUTION
                    )
                else:
                    message = f"Failed to uninstall addon '{params.addon_id}'"
                    structured_logger.error(
                        message,
                        category=LogCategory.TOOL_EXECUTION
                    )
                
                return [TextContent(type="text", text=message)]
                
        except OpenHABError as e:
            error_msg = f"Failed to uninstall addon '{params.addon_id}': {e}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"Unexpected error uninstalling addon '{params.addon_id}': {e}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]


class AddonConfigTool:
    """Tool for configuring openHAB addons."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the addon config tool."""
        self.config = config or get_config()
    
    async def execute(self, params: AddonConfigParams) -> List[TextContent]:
        """Execute the addon config tool.
        
        Args:
            params: Tool parameters
            
        Returns:
            List of text content with configuration result
        """
        try:
            structured_logger.info(
                f"Updating configuration for addon '{params.addon_id}'",
                category=LogCategory.TOOL_EXECUTION
            )
            
            async with OpenHABClient(self.config) as client:
                # Check if addon exists and is installed
                addons = await client.get_addons()
                target_addon = None
                
                for addon in addons:
                    if addon.get('id') == params.addon_id:
                        target_addon = addon
                        break
                
                if not target_addon:
                    error_msg = f"Addon '{params.addon_id}' not found"
                    structured_logger.warning(
                        error_msg,
                        category=LogCategory.TOOL_EXECUTION
                    )
                    return [TextContent(type="text", text=error_msg)]
                
                if not target_addon.get('installed', False):
                    error_msg = f"Addon '{params.addon_id}' is not installed. Configuration can only be updated for installed addons."
                    structured_logger.warning(
                        error_msg,
                        category=LogCategory.TOOL_EXECUTION
                    )
                    return [TextContent(type="text", text=error_msg)]
                
                # Update addon configuration
                success = await client.update_addon_config(params.addon_id, params.config)
                
                if success:
                    message = f"Successfully updated configuration for addon '{params.addon_id}'"
                    addon_name = target_addon.get('name', params.addon_id)
                    if addon_name != params.addon_id:
                        message += f" ({addon_name})"
                    
                    # Add details about what was configured
                    if params.config:
                        message += f"\nUpdated parameters: {', '.join(params.config.keys())}"
                    
                    structured_logger.info(
                        message,
                        category=LogCategory.TOOL_EXECUTION
                    )
                else:
                    message = f"Failed to update configuration for addon '{params.addon_id}'"
                    structured_logger.error(
                        message,
                        category=LogCategory.TOOL_EXECUTION
                    )
                
                return [TextContent(type="text", text=message)]
                
        except OpenHABError as e:
            error_msg = f"Failed to update configuration for addon '{params.addon_id}': {e}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"Unexpected error updating configuration for addon '{params.addon_id}': {e}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]