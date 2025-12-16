"""
Main UI management tools for openHAB MCP server.

This module provides MCP tools for managing openHAB's Main UI including
page creation, widget updates, layout management, and configuration export.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.types import TextContent

from ..utils.openhab_client import OpenHABClient
from ..models import UIPageInfo, UIWidgetInfo, UIExportConfig, MCPError

logger = logging.getLogger(__name__)


class UIPageListTool:
    """List Main UI pages with configuration."""
    
    def __init__(self, client: OpenHABClient):
        """Initialize the UI page list tool."""
        self.client = client
    
    async def execute(self, include_widgets: bool = True) -> List[TextContent]:
        """Execute the UI page list tool."""
        try:
            logger.info("Listing Main UI pages")
            
            # Get UI pages from openHAB
            pages_data = await self.client.get_ui_pages()
            
            # Convert to UIPageInfo models
            pages = []
            for page_data in pages_data:
                try:
                    page_info = UIPageInfo(
                        id=page_data.get('uid', ''),
                        name=page_data.get('label', page_data.get('uid', '')),
                        configuration=page_data.get('config', {}),
                        widgets=page_data.get('slots', {}).get('default', []) if include_widgets else [],
                        layout=page_data.get('layout', {})
                    )
                    pages.append(page_info)
                except Exception as e:
                    logger.warning(f"Failed to parse page data for {page_data.get('uid', 'unknown')}: {e}")
                    continue
            
            # Format response
            if not pages:
                return [TextContent(
                    type="text",
                    text="No Main UI pages found in the openHAB system."
                )]
            
            response_text = f"Found {len(pages)} Main UI pages:\n\n"
            for page in pages:
                response_text += f"**{page.name}** (ID: {page.id})\n"
                if page.configuration:
                    response_text += f"  Configuration: {len(page.configuration)} parameters\n"
                if include_widgets:
                    response_text += f"  Widgets: {len(page.widgets)}\n"
                if page.layout:
                    response_text += f"  Layout: {page.layout.get('type', 'default')}\n"
                response_text += "\n"
            
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            logger.error(f"Failed to list UI pages: {e}")
            error = MCPError(
                error_type="ui_list_error",
                message=f"Failed to retrieve UI pages: {str(e)}",
                suggestions=["Check openHAB connection", "Verify Main UI is installed and configured"]
            )
            return [TextContent(type="text", text=f"Error: {error.message}")]


class UIPageCreateTool:
    """Create new Main UI pages."""
    
    def __init__(self, client: OpenHABClient):
        """Initialize the UI page create tool."""
        self.client = client
    
    async def execute(self, page_config: Dict[str, Any]) -> List[TextContent]:
        """Execute the UI page create tool."""
        try:
            logger.info(f"Creating Main UI page with config: {page_config}")
            
            # Validate required fields
            if 'uid' not in page_config:
                return [TextContent(
                    type="text",
                    text="Error: Page configuration must include 'uid' field"
                )]
            
            if 'label' not in page_config:
                page_config['label'] = page_config['uid']
            
            # Create the page
            page_id = await self.client.create_ui_page(page_config)
            
            if page_id:
                return [TextContent(
                    type="text",
                    text=f"Successfully created Main UI page '{page_config['label']}' with ID: {page_id}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text="Failed to create Main UI page - no page ID returned"
                )]
            
        except Exception as e:
            logger.error(f"Failed to create UI page: {e}")
            error = MCPError(
                error_type="ui_create_error",
                message=f"Failed to create UI page: {str(e)}",
                suggestions=[
                    "Check page configuration format",
                    "Ensure page UID is unique",
                    "Verify widget configurations are valid"
                ]
            )
            return [TextContent(type="text", text=f"Error: {error.message}")]


class UIWidgetUpdateTool:
    """Update UI widget properties."""
    
    def __init__(self, client: OpenHABClient):
        """Initialize the UI widget update tool."""
        self.client = client
    
    async def execute(self, page_id: str, widget_id: str, properties: Dict[str, Any]) -> List[TextContent]:
        """Execute the UI widget update tool."""
        try:
            logger.info(f"Updating widget {widget_id} on page {page_id}")
            
            # Update the widget
            success = await self.client.update_ui_widget(page_id, widget_id, properties)
            
            if success:
                return [TextContent(
                    type="text",
                    text=f"Successfully updated widget '{widget_id}' on page '{page_id}'"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Failed to update widget '{widget_id}' on page '{page_id}'"
                )]
            
        except Exception as e:
            logger.error(f"Failed to update UI widget: {e}")
            error = MCPError(
                error_type="ui_widget_error",
                message=f"Failed to update widget: {str(e)}",
                suggestions=[
                    "Check that page ID exists",
                    "Verify widget ID is correct",
                    "Ensure widget properties are valid for the widget type"
                ]
            )
            return [TextContent(type="text", text=f"Error: {error.message}")]


class UILayoutManageTool:
    """Manage UI layouts and responsive design."""
    
    def __init__(self, client: OpenHABClient):
        """Initialize the UI layout manage tool."""
        self.client = client
    
    async def execute(self, page_id: str, layout_config: Dict[str, Any]) -> List[TextContent]:
        """Execute the UI layout manage tool."""
        try:
            logger.info(f"Managing layout for page {page_id}")
            
            # Update the layout
            success = await self.client.manage_ui_layout(page_id, layout_config)
            
            if success:
                return [TextContent(
                    type="text",
                    text=f"Successfully updated layout for page '{page_id}'"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Failed to update layout for page '{page_id}'"
                )]
            
        except Exception as e:
            logger.error(f"Failed to manage UI layout: {e}")
            error = MCPError(
                error_type="ui_layout_error",
                message=f"Failed to manage layout: {str(e)}",
                suggestions=[
                    "Check that page ID exists",
                    "Verify layout configuration format",
                    "Ensure responsive design settings are valid"
                ]
            )
            return [TextContent(type="text", text=f"Error: {error.message}")]


class UIConfigExportTool:
    """Export UI configuration for backup or sharing."""
    
    def __init__(self, client: OpenHABClient):
        """Initialize the UI config export tool."""
        self.client = client
    
    async def execute(self, page_ids: Optional[List[str]] = None, include_global_settings: bool = True) -> List[TextContent]:
        """Execute the UI config export tool."""
        try:
            logger.info(f"Exporting UI configuration for pages: {page_ids}")
            
            # Export the configuration
            export_data = await self.client.export_ui_config(page_ids)
            
            if not export_data:
                return [TextContent(
                    type="text",
                    text="No UI configuration data found to export"
                )]
            
            # Create export config model
            try:
                # Convert pages data to UIPageInfo models
                pages = []
                for page_data in export_data.get('pages', []):
                    page_info = UIPageInfo(
                        id=page_data.get('uid', ''),
                        name=page_data.get('label', page_data.get('uid', '')),
                        configuration=page_data.get('config', {}),
                        widgets=page_data.get('slots', {}).get('default', []),
                        layout=page_data.get('layout', {})
                    )
                    pages.append(page_info)
                
                export_config = UIExportConfig(
                    pages=pages,
                    global_settings=export_data.get('global_settings', {}) if include_global_settings else {},
                    export_timestamp=datetime.now().isoformat()
                )
                
                # Format response
                response_text = f"UI Configuration Export\n"
                response_text += f"Timestamp: {export_config.export_timestamp}\n"
                response_text += f"Pages exported: {len(export_config.pages)}\n\n"
                
                for page in export_config.pages:
                    response_text += f"**{page.name}** (ID: {page.id})\n"
                    response_text += f"  Widgets: {len(page.widgets)}\n"
                    response_text += f"  Configuration keys: {list(page.configuration.keys())}\n\n"
                
                if export_config.global_settings:
                    response_text += f"Global settings: {len(export_config.global_settings)} parameters\n"
                
                return [TextContent(type="text", text=response_text)]
                
            except Exception as e:
                logger.error(f"Failed to create export config model: {e}")
                return [TextContent(
                    type="text",
                    text=f"Export completed but failed to format results: {str(e)}"
                )]
            
        except Exception as e:
            logger.error(f"Failed to export UI configuration: {e}")
            error = MCPError(
                error_type="ui_export_error",
                message=f"Failed to export UI configuration: {str(e)}",
                suggestions=[
                    "Check that specified page IDs exist",
                    "Verify openHAB connection",
                    "Ensure Main UI is properly configured"
                ]
            )
            return [TextContent(type="text", text=f"Error: {error.message}")]