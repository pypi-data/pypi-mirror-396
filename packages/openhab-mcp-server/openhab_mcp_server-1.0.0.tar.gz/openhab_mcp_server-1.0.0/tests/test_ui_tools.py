"""
Unit tests for Main UI management tools.

This module contains unit tests for the Main UI management functionality
including page creation, widget updates, layout management, and configuration export.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import asyncio
from typing import Dict, List, Any

from openhab_mcp_server.tools.ui import (
    UIPageListTool, UIPageCreateTool, UIWidgetUpdateTool,
    UILayoutManageTool, UIConfigExportTool
)
from openhab_mcp_server.utils.openhab_client import OpenHABClient


class TestUIPageListTool:
    """Test UI page listing functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock openHAB client."""
        return AsyncMock(spec=OpenHABClient)
    
    @pytest.fixture
    def ui_page_list_tool(self, mock_client):
        """Create UIPageListTool instance with mock client."""
        return UIPageListTool(mock_client)
    
    @pytest.mark.asyncio
    async def test_list_pages_success(self, ui_page_list_tool, mock_client):
        """Test successful page listing."""
        # Setup mock data
        mock_pages = [
            {
                'uid': 'page1',
                'label': 'Page 1',
                'config': {'theme': 'default'},
                'slots': {'default': [{'uid': 'widget1', 'type': 'Label'}]},
                'layout': {'type': 'grid'}
            },
            {
                'uid': 'page2',
                'label': 'Page 2',
                'config': {},
                'slots': {'default': []},
                'layout': {}
            }
        ]
        mock_client.get_ui_pages.return_value = mock_pages
        
        # Execute
        result = await ui_page_list_tool.execute(include_widgets=True)
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Found 2 Main UI pages" in result_text
        assert "Page 1" in result_text
        assert "Page 2" in result_text
        assert "Widgets: 1" in result_text
        assert "Widgets: 0" in result_text
        mock_client.get_ui_pages.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_pages_without_widgets(self, ui_page_list_tool, mock_client):
        """Test page listing without widget information."""
        mock_pages = [
            {
                'uid': 'page1',
                'label': 'Page 1',
                'config': {},
                'slots': {'default': [{'uid': 'widget1'}]},
                'layout': {}
            }
        ]
        mock_client.get_ui_pages.return_value = mock_pages
        
        # Execute
        result = await ui_page_list_tool.execute(include_widgets=False)
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Found 1 Main UI pages" in result_text
        assert "Page 1" in result_text
        # Should not include widget count when include_widgets=False
        assert "Widgets:" not in result_text
    
    @pytest.mark.asyncio
    async def test_list_pages_empty(self, ui_page_list_tool, mock_client):
        """Test listing when no pages exist."""
        mock_client.get_ui_pages.return_value = []
        
        # Execute
        result = await ui_page_list_tool.execute()
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "No Main UI pages found" in result_text
    
    @pytest.mark.asyncio
    async def test_list_pages_error(self, ui_page_list_tool, mock_client):
        """Test error handling during page listing."""
        mock_client.get_ui_pages.side_effect = Exception("Connection failed")
        
        # Execute
        result = await ui_page_list_tool.execute()
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Error:" in result_text
        assert "Failed to retrieve UI pages" in result_text


class TestUIPageCreateTool:
    """Test UI page creation functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock openHAB client."""
        return AsyncMock(spec=OpenHABClient)
    
    @pytest.fixture
    def ui_page_create_tool(self, mock_client):
        """Create UIPageCreateTool instance with mock client."""
        return UIPageCreateTool(mock_client)
    
    @pytest.mark.asyncio
    async def test_create_page_success(self, ui_page_create_tool, mock_client):
        """Test successful page creation."""
        page_config = {
            'uid': 'test_page',
            'label': 'Test Page',
            'component': 'ui:page',
            'config': {},
            'slots': {'default': []}
        }
        mock_client.create_ui_page.return_value = 'test_page'
        
        # Execute
        result = await ui_page_create_tool.execute(page_config)
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Successfully created" in result_text
        assert "Test Page" in result_text
        assert "test_page" in result_text
        mock_client.create_ui_page.assert_called_once_with(page_config)
    
    @pytest.mark.asyncio
    async def test_create_page_missing_uid(self, ui_page_create_tool, mock_client):
        """Test page creation with missing UID."""
        page_config = {
            'label': 'Test Page',
            'config': {}
        }
        
        # Execute
        result = await ui_page_create_tool.execute(page_config)
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Error:" in result_text
        assert "uid" in result_text.lower()
        mock_client.create_ui_page.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_page_auto_label(self, ui_page_create_tool, mock_client):
        """Test page creation with automatic label from UID."""
        page_config = {
            'uid': 'test_page'
        }
        mock_client.create_ui_page.return_value = 'test_page'
        
        # Execute
        result = await ui_page_create_tool.execute(page_config)
        
        # Verify that label was set to UID
        expected_config = page_config.copy()
        expected_config['label'] = 'test_page'
        mock_client.create_ui_page.assert_called_once_with(expected_config)
    
    @pytest.mark.asyncio
    async def test_create_page_error(self, ui_page_create_tool, mock_client):
        """Test error handling during page creation."""
        page_config = {'uid': 'test_page'}
        mock_client.create_ui_page.side_effect = Exception("Creation failed")
        
        # Execute
        result = await ui_page_create_tool.execute(page_config)
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Error:" in result_text
        assert "Failed to create UI page" in result_text


class TestUIWidgetUpdateTool:
    """Test UI widget update functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock openHAB client."""
        return AsyncMock(spec=OpenHABClient)
    
    @pytest.fixture
    def ui_widget_update_tool(self, mock_client):
        """Create UIWidgetUpdateTool instance with mock client."""
        return UIWidgetUpdateTool(mock_client)
    
    @pytest.mark.asyncio
    async def test_update_widget_success(self, ui_widget_update_tool, mock_client):
        """Test successful widget update."""
        mock_client.update_ui_widget.return_value = True
        
        # Execute
        result = await ui_widget_update_tool.execute(
            'test_page', 'test_widget', {'label': 'Updated Label'}
        )
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Successfully updated" in result_text
        assert "test_widget" in result_text
        assert "test_page" in result_text
        mock_client.update_ui_widget.assert_called_once_with(
            'test_page', 'test_widget', {'label': 'Updated Label'}
        )
    
    @pytest.mark.asyncio
    async def test_update_widget_failure(self, ui_widget_update_tool, mock_client):
        """Test widget update failure."""
        mock_client.update_ui_widget.return_value = False
        
        # Execute
        result = await ui_widget_update_tool.execute(
            'test_page', 'test_widget', {'label': 'Updated Label'}
        )
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Failed to update" in result_text
        assert "test_widget" in result_text
        assert "test_page" in result_text
    
    @pytest.mark.asyncio
    async def test_update_widget_error(self, ui_widget_update_tool, mock_client):
        """Test error handling during widget update."""
        mock_client.update_ui_widget.side_effect = Exception("Update failed")
        
        # Execute
        result = await ui_widget_update_tool.execute(
            'test_page', 'test_widget', {'label': 'Updated Label'}
        )
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Error:" in result_text
        assert "Failed to update widget" in result_text


class TestUILayoutManageTool:
    """Test UI layout management functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock openHAB client."""
        return AsyncMock(spec=OpenHABClient)
    
    @pytest.fixture
    def ui_layout_manage_tool(self, mock_client):
        """Create UILayoutManageTool instance with mock client."""
        return UILayoutManageTool(mock_client)
    
    @pytest.mark.asyncio
    async def test_manage_layout_success(self, ui_layout_manage_tool, mock_client):
        """Test successful layout management."""
        mock_client.manage_ui_layout.return_value = True
        layout_config = {'grid': 3, 'responsive': True}
        
        # Execute
        result = await ui_layout_manage_tool.execute('test_page', layout_config)
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Successfully updated layout" in result_text
        assert "test_page" in result_text
        mock_client.manage_ui_layout.assert_called_once_with('test_page', layout_config)
    
    @pytest.mark.asyncio
    async def test_manage_layout_failure(self, ui_layout_manage_tool, mock_client):
        """Test layout management failure."""
        mock_client.manage_ui_layout.return_value = False
        layout_config = {'grid': 3}
        
        # Execute
        result = await ui_layout_manage_tool.execute('test_page', layout_config)
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Failed to update layout" in result_text
        assert "test_page" in result_text
    
    @pytest.mark.asyncio
    async def test_manage_layout_error(self, ui_layout_manage_tool, mock_client):
        """Test error handling during layout management."""
        mock_client.manage_ui_layout.side_effect = Exception("Layout failed")
        
        # Execute
        result = await ui_layout_manage_tool.execute('test_page', {'grid': 3})
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Error:" in result_text
        assert "Failed to manage layout" in result_text


class TestUIConfigExportTool:
    """Test UI configuration export functionality."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock openHAB client."""
        return AsyncMock(spec=OpenHABClient)
    
    @pytest.fixture
    def ui_config_export_tool(self, mock_client):
        """Create UIConfigExportTool instance with mock client."""
        return UIConfigExportTool(mock_client)
    
    @pytest.mark.asyncio
    async def test_export_config_success(self, ui_config_export_tool, mock_client):
        """Test successful configuration export."""
        mock_export_data = {
            'pages': [
                {
                    'uid': 'page1',
                    'label': 'Page 1',
                    'config': {'theme': 'default'},
                    'slots': {'default': [{'uid': 'widget1'}]},
                    'layout': {'type': 'grid'}
                }
            ],
            'global_settings': {'theme': 'default'}
        }
        mock_client.export_ui_config.return_value = mock_export_data
        
        # Execute
        result = await ui_config_export_tool.execute(['page1'], True)
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "UI Configuration Export" in result_text
        assert "Pages exported: 1" in result_text
        assert "Page 1" in result_text
        assert "Global settings" in result_text
        mock_client.export_ui_config.assert_called_once_with(['page1'])
    
    @pytest.mark.asyncio
    async def test_export_config_no_global_settings(self, ui_config_export_tool, mock_client):
        """Test configuration export without global settings."""
        mock_export_data = {
            'pages': [
                {
                    'uid': 'page1',
                    'label': 'Page 1',
                    'config': {},
                    'slots': {'default': []},
                    'layout': {}
                }
            ],
            'global_settings': {}
        }
        mock_client.export_ui_config.return_value = mock_export_data
        
        # Execute
        result = await ui_config_export_tool.execute(['page1'], False)
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "UI Configuration Export" in result_text
        assert "Pages exported: 1" in result_text
        # Should not include global settings when include_global_settings=False
        assert "Global settings" not in result_text
    
    @pytest.mark.asyncio
    async def test_export_config_empty(self, ui_config_export_tool, mock_client):
        """Test configuration export with no data."""
        mock_client.export_ui_config.return_value = {}
        
        # Execute
        result = await ui_config_export_tool.execute()
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "No UI configuration data found" in result_text
    
    @pytest.mark.asyncio
    async def test_export_config_all_pages(self, ui_config_export_tool, mock_client):
        """Test configuration export for all pages."""
        mock_export_data = {
            'pages': [
                {'uid': 'page1', 'label': 'Page 1', 'config': {}, 'slots': {'default': []}, 'layout': {}},
                {'uid': 'page2', 'label': 'Page 2', 'config': {}, 'slots': {'default': []}, 'layout': {}}
            ],
            'global_settings': {}
        }
        mock_client.export_ui_config.return_value = mock_export_data
        
        # Execute (None means all pages)
        result = await ui_config_export_tool.execute(None, True)
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Pages exported: 2" in result_text
        assert "Page 1" in result_text
        assert "Page 2" in result_text
        mock_client.export_ui_config.assert_called_once_with(None)
    
    @pytest.mark.asyncio
    async def test_export_config_error(self, ui_config_export_tool, mock_client):
        """Test error handling during configuration export."""
        mock_client.export_ui_config.side_effect = Exception("Export failed")
        
        # Execute
        result = await ui_config_export_tool.execute()
        
        # Verify
        assert len(result) == 1
        result_text = result[0].text
        assert "Error:" in result_text
        assert "Failed to export UI configuration" in result_text


# Integration tests
class TestUIToolsIntegration:
    """Integration tests for UI management tools."""
    
    @pytest.mark.asyncio
    async def test_page_creation_and_listing_workflow(self):
        """Test complete workflow of creating a page and then listing it."""
        mock_client = AsyncMock(spec=OpenHABClient)
        
        # Setup page creation
        page_config = {
            'uid': 'test_page',
            'label': 'Test Page',
            'config': {},
            'slots': {'default': []}
        }
        mock_client.create_ui_page.return_value = 'test_page'
        
        # Setup page listing after creation
        mock_pages = [
            {
                'uid': 'test_page',
                'label': 'Test Page',
                'config': {},
                'slots': {'default': []},
                'layout': {}
            }
        ]
        mock_client.get_ui_pages.return_value = mock_pages
        
        # Create page
        create_tool = UIPageCreateTool(mock_client)
        create_result = await create_tool.execute(page_config)
        
        # List pages
        list_tool = UIPageListTool(mock_client)
        list_result = await list_tool.execute()
        
        # Verify creation
        assert "Successfully created" in create_result[0].text
        
        # Verify listing
        assert "Found 1 Main UI pages" in list_result[0].text
        assert "Test Page" in list_result[0].text
    
    @pytest.mark.asyncio
    async def test_widget_update_and_export_workflow(self):
        """Test workflow of updating a widget and then exporting configuration."""
        mock_client = AsyncMock(spec=OpenHABClient)
        
        # Setup widget update
        mock_client.update_ui_widget.return_value = True
        
        # Setup export after update
        mock_export_data = {
            'pages': [
                {
                    'uid': 'test_page',
                    'label': 'Test Page',
                    'config': {},
                    'slots': {'default': [{'uid': 'test_widget', 'config': {'label': 'Updated Label'}}]},
                    'layout': {}
                }
            ],
            'global_settings': {}
        }
        mock_client.export_ui_config.return_value = mock_export_data
        
        # Update widget
        update_tool = UIWidgetUpdateTool(mock_client)
        update_result = await update_tool.execute(
            'test_page', 'test_widget', {'label': 'Updated Label'}
        )
        
        # Export configuration
        export_tool = UIConfigExportTool(mock_client)
        export_result = await export_tool.execute(['test_page'])
        
        # Verify update
        assert "Successfully updated" in update_result[0].text
        
        # Verify export
        assert "UI Configuration Export" in export_result[0].text
        assert "Test Page" in export_result[0].text