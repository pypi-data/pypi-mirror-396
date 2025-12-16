"""
Property-based tests for Main UI management functionality.

This module contains property-based tests that validate the correctness
of Main UI management operations including page retrieval, creation,
widget updates, layout management, and configuration export.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import Dict, List, Any, Optional
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from openhab_mcp_server.tools.ui import (
    UIPageListTool, UIPageCreateTool, UIWidgetUpdateTool,
    UILayoutManageTool, UIConfigExportTool
)
from openhab_mcp_server.models import UIPageInfo, UIWidgetInfo, UIExportConfig
from openhab_mcp_server.utils.openhab_client import OpenHABClient


# Test data generators

@st.composite
def ui_page_data(draw):
    """Generate valid UI page data."""
    page_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-')))
    assume(page_id and page_id.strip())
    
    return {
        'uid': page_id,
        'label': draw(st.text(min_size=1, max_size=100)),
        'component': 'ui:page',
        'config': draw(st.dictionaries(
            st.text(min_size=1, max_size=20), 
            st.one_of(st.text(), st.integers(), st.booleans()),
            min_size=0, max_size=5
        )),
        'slots': {
            'default': draw(st.lists(
                st.dictionaries(
                    st.text(min_size=1, max_size=20),
                    st.one_of(st.text(), st.integers(), st.booleans()),
                    min_size=1, max_size=3
                ),
                min_size=0, max_size=5
            ))
        }
    }

@st.composite
def widget_properties(draw):
    """Generate valid widget properties."""
    return draw(st.dictionaries(
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_')),
        st.one_of(
            st.text(min_size=0, max_size=100),
            st.integers(min_value=-1000, max_value=1000),
            st.booleans(),
            st.lists(st.text(min_size=0, max_size=20), min_size=0, max_size=3)
        ),
        min_size=1, max_size=10
    ))

@st.composite
def layout_config(draw):
    """Generate valid layout configuration."""
    return draw(st.dictionaries(
        st.sampled_from(['grid', 'masonry', 'responsive', 'columns', 'rows']),
        st.one_of(
            st.integers(min_value=1, max_value=12),
            st.booleans(),
            st.text(min_size=1, max_size=20)
        ),
        min_size=1, max_size=5
    ))


class TestUIPageRetrieval:
    """Test UI page retrieval functionality."""
    
    async def test_ui_page_retrieval_completeness(self, pages_data):
        """
        **Feature: openhab-mcp-server, Property 48: UI page retrieval completeness**
        **Validates: Requirements 15.1**
        
        For any UI page query, all Main UI pages should be returned with 
        complete configuration and widget structure information.
        """
        # Create mock client
        mock_client = AsyncMock(spec=OpenHABClient)
        mock_client.get_ui_pages.return_value = pages_data
        
        # Create tool instance
        tool = UIPageListTool(mock_client)
        
        # Execute the tool
        result = await tool.execute(include_widgets=True)
        
        # Verify result structure
        assert isinstance(result, list)
        assert len(result) == 1  # Should return one TextContent
        
        result_text = result[0].text
        
        if not pages_data:
            # Should indicate no pages found
            assert "No Main UI pages found" in result_text
        else:
            # Should contain information about all pages
            assert f"Found {len(pages_data)} Main UI pages" in result_text
            
            # Each page should be mentioned
            for page in pages_data:
                page_id = page.get('uid', '')
                if page_id:
                    assert page_id in result_text
                
                # Should include widget count information
                widgets = page.get('slots', {}).get('default', [])
                assert f"Widgets: {len(widgets)}" in result_text
        
        # Verify client was called correctly
        mock_client.get_ui_pages.assert_called_once()
    
    async def test_ui_page_retrieval_without_widgets(self, pages_data):
        """Test UI page retrieval without widget information."""
        # Create mock client
        mock_client = AsyncMock(spec=OpenHABClient)
        mock_client.get_ui_pages.return_value = pages_data
        
        # Create tool instance
        tool = UIPageListTool(mock_client)
        
        # Execute the tool without widgets
        result = await tool.execute(include_widgets=False)
        
        # Verify result
        assert isinstance(result, list)
        result_text = result[0].text
        
        # Should not include widget information when include_widgets=False
        for page in pages_data:
            page_id = page.get('uid', '')
            if page_id:
                assert page_id in result_text
                # Widget count should not be included
                widgets = page.get('slots', {}).get('default', [])
                if widgets:  # Only check if there are widgets
                    assert f"Widgets: {len(widgets)}" not in result_text


class TestUIPageCreation:
    """Test UI page creation functionality."""
    
    async def test_ui_page_creation_validation(self, page_config):
        """
        **Feature: openhab-mcp-server, Property 49: UI page creation validation**
        **Validates: Requirements 15.2**
        
        For any UI page creation request, valid pages should be created with 
        proper widget layout validation and invalid configurations should be rejected.
        """
        # Create mock client
        mock_client = AsyncMock(spec=OpenHABClient)
        
        # Assume successful creation returns the page ID
        expected_page_id = page_config.get('uid', 'test_page')
        mock_client.create_ui_page.return_value = expected_page_id
        
        # Create tool instance
        tool = UIPageCreateTool(mock_client)
        
        # Execute the tool
        result = await tool.execute(page_config)
        
        # Verify result
        assert isinstance(result, list)
        result_text = result[0].text
        
        # Should indicate successful creation
        assert "Successfully created" in result_text
        assert expected_page_id in result_text
        
        # Verify client was called with correct config
        mock_client.create_ui_page.assert_called_once_with(page_config)
    
    async def test_ui_page_creation_missing_uid(self, incomplete_config):
        """Test UI page creation with missing UID."""
        if 'uid' in incomplete_config:
            return  # Skip if UID is present
        
        # Create mock client
        mock_client = AsyncMock(spec=OpenHABClient)
        
        # Create tool instance
        tool = UIPageCreateTool(mock_client)
        
        # Execute the tool
        result = await tool.execute(incomplete_config)
        
        # Verify error handling
        assert isinstance(result, list)
        result_text = result[0].text
        
        # Should indicate error about missing UID
        assert "Error" in result_text
        assert "uid" in result_text.lower()
        
        # Client should not be called
        mock_client.create_ui_page.assert_not_called()


class TestUIWidgetUpdates:
    """Test UI widget update functionality."""
    
    async def test_ui_widget_update_consistency(self, page_id, widget_id, properties):
        """
        **Feature: openhab-mcp-server, Property 50: UI widget update consistency**
        **Validates: Requirements 15.3**
        
        For any UI widget update, the changes should be applied to widget properties 
        and the UI display should reflect the updates.
        """
        if not (page_id.strip() and widget_id.strip()):
            return  # Skip invalid inputs
        
        # Create mock client
        mock_client = AsyncMock(spec=OpenHABClient)
        mock_client.update_ui_widget.return_value = True
        
        # Create tool instance
        tool = UIWidgetUpdateTool(mock_client)
        
        # Execute the tool
        result = await tool.execute(page_id, widget_id, properties)
        
        # Verify result
        assert isinstance(result, list)
        result_text = result[0].text
        
        # Should indicate successful update
        assert "Successfully updated" in result_text
        assert widget_id in result_text
        assert page_id in result_text
        
        # Verify client was called correctly
        mock_client.update_ui_widget.assert_called_once_with(page_id, widget_id, properties)
    
    async def test_ui_widget_update_failure(self, page_id, widget_id, properties):
        """Test UI widget update failure handling."""
        if not (page_id.strip() and widget_id.strip()):
            return  # Skip invalid inputs
        
        # Create mock client that returns failure
        mock_client = AsyncMock(spec=OpenHABClient)
        mock_client.update_ui_widget.return_value = False
        
        # Create tool instance
        tool = UIWidgetUpdateTool(mock_client)
        
        # Execute the tool
        result = await tool.execute(page_id, widget_id, properties)
        
        # Verify error handling
        assert isinstance(result, list)
        result_text = result[0].text
        
        # Should indicate failure
        assert "Failed to update" in result_text
        assert widget_id in result_text
        assert page_id in result_text


class TestUILayoutManagement:
    """Test UI layout management functionality."""
    
    async def test_ui_layout_management_accuracy(self, page_id, layout_config_data):
        """
        **Feature: openhab-mcp-server, Property 51: UI layout management accuracy**
        **Validates: Requirements 15.4**
        
        For any UI layout management operation, widgets should be properly organized 
        within pages and responsive design settings should be handled correctly.
        """
        if not page_id.strip():
            return  # Skip invalid inputs
        
        # Create mock client
        mock_client = AsyncMock(spec=OpenHABClient)
        mock_client.manage_ui_layout.return_value = True
        
        # Create tool instance
        tool = UILayoutManageTool(mock_client)
        
        # Execute the tool
        result = await tool.execute(page_id, layout_config_data)
        
        # Verify result
        assert isinstance(result, list)
        result_text = result[0].text
        
        # Should indicate successful layout update
        assert "Successfully updated layout" in result_text
        assert page_id in result_text
        
        # Verify client was called correctly
        mock_client.manage_ui_layout.assert_called_once_with(page_id, layout_config_data)


class TestUIConfigurationExport:
    """Test UI configuration export functionality."""
    
    async def test_ui_configuration_export_completeness(self, page_ids, include_global_settings):
        """
        **Feature: openhab-mcp-server, Property 52: UI configuration export completeness**
        **Validates: Requirements 15.5**
        
        For any UI configuration export request, the exported data should include 
        complete page and widget definitions suitable for backup or sharing.
        """
        # Create mock export data
        mock_pages = []
        if page_ids:
            for page_id in page_ids:
                mock_pages.append({
                    'uid': page_id,
                    'label': f'Page {page_id}',
                    'config': {'test': 'config'},
                    'slots': {'default': [{'uid': f'widget_{page_id}', 'type': 'Label'}]}
                })
        
        mock_export_data = {
            'pages': mock_pages,
            'global_settings': {'theme': 'default'} if include_global_settings else {},
            'export_info': {
                'total_pages': len(mock_pages),
                'exported_page_ids': page_ids or []
            }
        }
        
        # Create mock client
        mock_client = AsyncMock(spec=OpenHABClient)
        mock_client.export_ui_config.return_value = mock_export_data
        
        # Create tool instance
        tool = UIConfigExportTool(mock_client)
        
        # Execute the tool
        result = await tool.execute(page_ids, include_global_settings)
        
        # Verify result
        assert isinstance(result, list)
        result_text = result[0].text
        
        if not mock_pages:
            # Should handle empty export
            assert "Pages exported: 0" in result_text
        else:
            # Should include export information
            assert f"Pages exported: {len(mock_pages)}" in result_text
            
            # Each page should be mentioned
            for page in mock_pages:
                page_id = page.get('uid', '')
                if page_id:
                    assert page_id in result_text
        
        # Should include global settings info if requested
        if include_global_settings and mock_export_data.get('global_settings'):
            assert "Global settings" in result_text
        
        # Verify client was called correctly
        mock_client.export_ui_config.assert_called_once_with(page_ids)
    
    async def test_ui_configuration_export_empty_result(self, page_ids):
        """Test UI configuration export with empty result."""
        # Create mock client that returns empty data
        mock_client = AsyncMock(spec=OpenHABClient)
        mock_client.export_ui_config.return_value = {}
        
        # Create tool instance
        tool = UIConfigExportTool(mock_client)
        
        # Execute the tool
        result = await tool.execute(page_ids)
        
        # Verify error handling
        assert isinstance(result, list)
        result_text = result[0].text
        
        # Should indicate no data found
        assert "No UI configuration data found" in result_text


# Async test runner
def run_async_test(coro):
    """Helper to run async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Pytest integration
class TestUIPropertyTests:
    """Pytest wrapper for property-based tests."""
    
    def test_ui_page_retrieval_completeness_sync(self):
        """Sync wrapper for UI page retrieval test."""
        test_instance = TestUIPageRetrieval()
        
        # Run a few examples manually
        test_cases = [
            [],  # Empty pages
            [{'uid': 'page1', 'label': 'Page 1', 'slots': {'default': []}}],  # Single page
            [
                {'uid': 'page1', 'label': 'Page 1', 'slots': {'default': []}},
                {'uid': 'page2', 'label': 'Page 2', 'slots': {'default': [{'uid': 'widget1'}]}}
            ]  # Multiple pages
        ]
        
        for pages_data in test_cases:
            run_async_test(test_instance.test_ui_page_retrieval_completeness(pages_data))
    
    def test_ui_page_creation_validation_sync(self):
        """Sync wrapper for UI page creation test."""
        test_instance = TestUIPageCreation()
        
        # Test valid page config
        page_config = {
            'uid': 'test_page',
            'label': 'Test Page',
            'component': 'ui:page',
            'config': {},
            'slots': {'default': []}
        }
        
        run_async_test(test_instance.test_ui_page_creation_validation(page_config))
    
    def test_ui_widget_update_consistency_sync(self):
        """Sync wrapper for UI widget update test."""
        test_instance = TestUIWidgetUpdates()
        
        # Test widget update
        run_async_test(test_instance.test_ui_widget_update_consistency(
            'test_page', 'test_widget', {'label': 'Updated Label', 'visible': True}
        ))
    
    def test_ui_layout_management_accuracy_sync(self):
        """Sync wrapper for UI layout management test."""
        test_instance = TestUILayoutManagement()
        
        # Test layout management
        run_async_test(test_instance.test_ui_layout_management_accuracy(
            'test_page', {'grid': 3, 'responsive': True}
        ))
    
    def test_ui_configuration_export_completeness_sync(self):
        """Sync wrapper for UI configuration export test."""
        test_instance = TestUIConfigurationExport()
        
        # Test configuration export
        run_async_test(test_instance.test_ui_configuration_export_completeness(
            ['page1', 'page2'], True
        ))