"""Unit tests for openHAB link management tools."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from openhab_mcp_server.tools.links import LinkListTool, LinkCreateTool, LinkUpdateTool, LinkDeleteTool
from openhab_mcp_server.utils.config import Config


class TestLinkListTool:
    """Unit tests for LinkListTool."""
    
    @pytest.fixture
    def tool(self):
        """Create LinkListTool instance for testing."""
        return LinkListTool()
    
    @pytest.mark.asyncio
    async def test_execute_success_with_links(self, tool):
        """Test successful link listing with results."""
        test_links = [
            {
                "itemName": "TestItem1",
                "channelUID": "binding:thing:device:channel1",
                "configuration": {"profile": "default"}
            },
            {
                "itemName": "TestItem2", 
                "channelUID": "binding:thing:device:channel2",
                "configuration": {}
            }
        ]
        
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.get_links.return_value = test_links
            
            # Execute the tool
            result = await tool.execute()
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Found 2 link(s)" in result[0].text
            assert "TestItem1" in result[0].text
            assert "TestItem2" in result[0].text
            assert "binding:thing:device:channel1" in result[0].text
            assert "binding:thing:device:channel2" in result[0].text
            
            # Verify client was called correctly
            mock_client.get_links.assert_called_once_with(item_name=None, channel_uid=None)
    
    @pytest.mark.asyncio
    async def test_execute_success_no_links(self, tool):
        """Test successful link listing with no results."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.get_links.return_value = []
            
            # Execute the tool
            result = await tool.execute()
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "No links found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_with_filters(self, tool):
        """Test link listing with item and channel filters."""
        test_links = [
            {
                "itemName": "FilteredItem",
                "channelUID": "binding:thing:device:filtered_channel",
                "configuration": {}
            }
        ]
        
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.get_links.return_value = test_links
            
            # Execute the tool with filters
            result = await tool.execute(item_name="FilteredItem", channel_uid="binding:thing:device:filtered_channel")
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Found 1 link(s)" in result[0].text
            
            # Verify client was called with filters
            mock_client.get_links.assert_called_once_with(item_name="FilteredItem", channel_uid="binding:thing:device:filtered_channel")
    
    @pytest.mark.asyncio
    async def test_execute_with_item_filter_only(self, tool):
        """Test link listing with item filter only."""
        test_links = [
            {
                "itemName": "FilteredItem",
                "channelUID": "binding:thing:device:channel1",
                "configuration": {"profile": "default"}
            }
        ]
        
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.get_links.return_value = test_links
            
            # Execute the tool with item filter only
            result = await tool.execute(item_name="FilteredItem")
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Found 1 link(s)" in result[0].text
            assert "FilteredItem" in result[0].text
            
            # Verify client was called with correct filter
            mock_client.get_links.assert_called_once_with(item_name="FilteredItem", channel_uid=None)
    
    @pytest.mark.asyncio
    async def test_execute_with_channel_filter_only(self, tool):
        """Test link listing with channel filter only."""
        test_links = [
            {
                "itemName": "TestItem",
                "channelUID": "binding:thing:device:filtered_channel",
                "configuration": {}
            }
        ]
        
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.get_links.return_value = test_links
            
            # Execute the tool with channel filter only
            result = await tool.execute(channel_uid="binding:thing:device:filtered_channel")
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Found 1 link(s)" in result[0].text
            assert "filtered_channel" in result[0].text
            
            # Verify client was called with correct filter
            mock_client.get_links.assert_called_once_with(item_name=None, channel_uid="binding:thing:device:filtered_channel")
    
    @pytest.mark.asyncio
    async def test_execute_no_links_with_item_filter(self, tool):
        """Test link listing with no results for item filter."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.get_links.return_value = []
            
            # Execute the tool with item filter
            result = await tool.execute(item_name="NonExistentItem")
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "No links found matching item 'NonExistentItem'" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_no_links_with_both_filters(self, tool):
        """Test link listing with no results for both filters."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.get_links.return_value = []
            
            # Execute the tool with both filters
            result = await tool.execute(item_name="NonExistentItem", channel_uid="binding:thing:device:nonexistent")
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "No links found matching item 'NonExistentItem' and channel 'binding:thing:device:nonexistent'" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_links_with_complex_configuration(self, tool):
        """Test link listing with complex configuration display."""
        test_links = [
            {
                "itemName": "ComplexItem",
                "channelUID": "binding:thing:device:channel",
                "configuration": {
                    "profile": "transform:MAP",
                    "function": "test.map",
                    "sourceFormat": "%s",
                    "targetFormat": "%.1f"
                }
            }
        ]
        
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.get_links.return_value = test_links
            
            # Execute the tool
            result = await tool.execute()
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Found 1 link(s)" in result[0].text
            assert "ComplexItem" in result[0].text
            assert "transform:MAP" in result[0].text
            assert "test.map" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_error_handling(self, tool):
        """Test error handling in link listing."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client to raise exception
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.get_links.side_effect = Exception("Connection error")
            
            # Execute the tool
            result = await tool.execute()
            
            # Verify error handling
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Failed to list links" in result[0].text
            assert "Connection error" in result[0].text


class TestLinkCreateTool:
    """Unit tests for LinkCreateTool."""
    
    @pytest.fixture
    def tool(self):
        """Create LinkCreateTool instance for testing."""
        return LinkCreateTool()
    
    @pytest.mark.asyncio
    async def test_execute_success(self, tool):
        """Test successful link creation."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.create_link.return_value = True
            
            # Execute the tool
            result = await tool.execute("TestItem", "binding:thing:device:channel", {"profile": "default"})
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Successfully created link" in result[0].text
            assert "TestItem" in result[0].text
            assert "binding:thing:device:channel" in result[0].text
            
            # Verify client was called correctly
            mock_client.create_link.assert_called_once_with("TestItem", "binding:thing:device:channel", {"profile": "default"})
    
    @pytest.mark.asyncio
    async def test_execute_success_no_config(self, tool):
        """Test successful link creation without configuration."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.create_link.return_value = True
            
            # Execute the tool
            result = await tool.execute("TestItem", "binding:thing:device:channel")
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Successfully created link" in result[0].text
            
            # Verify client was called correctly
            mock_client.create_link.assert_called_once_with("TestItem", "binding:thing:device:channel", None)
    
    @pytest.mark.asyncio
    async def test_execute_validation_error_empty_item(self, tool):
        """Test validation error for empty item name."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            
            # Execute the tool with invalid input
            result = await tool.execute("", "binding:thing:device:channel")
            
            # Verify validation error
            assert len(result) == 1
            assert result[0].type == "text"
            assert "validation failed" in result[0].text.lower()
            
            # Verify client was not called
            mock_client.create_link.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_validation_error_invalid_channel(self, tool):
        """Test validation error for invalid channel UID."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            
            # Execute the tool with invalid channel UID (no colon)
            result = await tool.execute("TestItem", "invalid_channel_uid")
            
            # Verify validation error
            assert len(result) == 1
            assert result[0].type == "text"
            assert "validation failed" in result[0].text.lower()
            
            # Verify client was not called
            mock_client.create_link.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_validation_error_item_with_spaces(self, tool):
        """Test validation error for item name with spaces."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            
            # Execute the tool with item name containing spaces
            result = await tool.execute("Test Item", "binding:thing:device:channel")
            
            # Verify validation error
            assert len(result) == 1
            assert result[0].type == "text"
            assert "validation failed" in result[0].text.lower()
            assert "cannot contain spaces" in result[0].text
            
            # Verify client was not called
            mock_client.create_link.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_validation_error_channel_empty_parts(self, tool):
        """Test validation error for channel UID with empty parts."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            
            # Execute the tool with channel UID having empty parts
            result = await tool.execute("TestItem", "binding::device:channel")
            
            # Verify validation error
            assert len(result) == 1
            assert result[0].type == "text"
            assert "validation failed" in result[0].text.lower()
            assert "cannot be empty" in result[0].text
            
            # Verify client was not called
            mock_client.create_link.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_validation_error_channel_insufficient_parts(self, tool):
        """Test validation error for channel UID with insufficient parts."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            
            # Execute the tool with channel UID having only one part
            result = await tool.execute("TestItem", "binding:")
            
            # Verify validation error
            assert len(result) == 1
            assert result[0].type == "text"
            assert "validation failed" in result[0].text.lower()
            
            # Verify client was not called
            mock_client.create_link.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_error_handling(self, tool):
        """Test error handling in link creation."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client to raise exception
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.create_link.side_effect = Exception("Connection error")
            
            # Execute the tool
            result = await tool.execute("TestItem", "binding:thing:device:channel")
            
            # Verify error handling
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Failed to create link" in result[0].text
            assert "Connection error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_creation_failure(self, tool):
        """Test handling of link creation failure."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.create_link.return_value = False
            
            # Execute the tool
            result = await tool.execute("TestItem", "binding:thing:device:channel")
            
            # Verify failure handling
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Failed to create link" in result[0].text


class TestLinkUpdateTool:
    """Unit tests for LinkUpdateTool."""
    
    @pytest.fixture
    def tool(self):
        """Create LinkUpdateTool instance for testing."""
        return LinkUpdateTool()
    
    @pytest.mark.asyncio
    async def test_execute_success(self, tool):
        """Test successful link configuration update."""
        config = {"profile": "follow", "transform": "MAP(test.map)"}
        
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.update_link.return_value = True
            
            # Execute the tool
            result = await tool.execute("TestItem", "binding:thing:device:channel", config)
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Successfully updated link configuration" in result[0].text
            assert "TestItem" in result[0].text
            assert "binding:thing:device:channel" in result[0].text
            assert str(config) in result[0].text
            
            # Verify client was called correctly
            mock_client.update_link.assert_called_once_with("TestItem", "binding:thing:device:channel", config)
    
    @pytest.mark.asyncio
    async def test_execute_success_with_transformation_settings(self, tool):
        """Test successful link update with transformation settings."""
        config = {
            "profile": "transform:MAP",
            "function": "test.map",
            "sourceFormat": "%s",
            "targetFormat": "%.1f"
        }
        
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.update_link.return_value = True
            
            # Execute the tool
            result = await tool.execute("TestItem", "binding:thing:device:channel", config)
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Successfully updated link configuration" in result[0].text
            assert str(config) in result[0].text
            
            # Verify client was called correctly
            mock_client.update_link.assert_called_once_with("TestItem", "binding:thing:device:channel", config)
    
    @pytest.mark.asyncio
    async def test_execute_validation_error_empty_configuration(self, tool):
        """Test validation error for empty configuration."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            
            # Execute the tool with empty configuration
            result = await tool.execute("TestItem", "binding:thing:device:channel", {})
            
            # Verify validation error
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Configuration cannot be empty" in result[0].text
            
            # Verify client was not called
            mock_client.update_link.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_validation_error_none_configuration(self, tool):
        """Test validation error for None configuration."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            
            # Execute the tool with None configuration
            result = await tool.execute("TestItem", "binding:thing:device:channel", None)
            
            # Verify validation error
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Configuration cannot be empty" in result[0].text
            
            # Verify client was not called
            mock_client.update_link.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_update_failure(self, tool):
        """Test handling of link update failure."""
        config = {"profile": "default"}
        
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.update_link.return_value = False
            
            # Execute the tool
            result = await tool.execute("TestItem", "binding:thing:device:channel", config)
            
            # Verify failure handling
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Failed to update link configuration" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_error_handling(self, tool):
        """Test error handling in link update."""
        config = {"profile": "default"}
        
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client to raise exception
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.update_link.side_effect = Exception("Connection error")
            
            # Execute the tool
            result = await tool.execute("TestItem", "binding:thing:device:channel", config)
            
            # Verify error handling
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Failed to update link configuration" in result[0].text
            assert "Connection error" in result[0].text


class TestLinkDeleteTool:
    """Unit tests for LinkDeleteTool."""
    
    @pytest.fixture
    def tool(self):
        """Create LinkDeleteTool instance for testing."""
        return LinkDeleteTool()
    
    @pytest.mark.asyncio
    async def test_execute_success(self, tool):
        """Test successful link deletion."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.delete_link.return_value = True
            
            # Execute the tool
            result = await tool.execute("TestItem", "binding:thing:device:channel")
            
            # Verify results
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Successfully deleted link" in result[0].text
            assert "TestItem" in result[0].text
            assert "binding:thing:device:channel" in result[0].text
            
            # Verify client was called correctly
            mock_client.delete_link.assert_called_once_with("TestItem", "binding:thing:device:channel")
    
    @pytest.mark.asyncio
    async def test_execute_deletion_failure(self, tool):
        """Test handling of link deletion failure."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.delete_link.return_value = False
            
            # Execute the tool
            result = await tool.execute("TestItem", "binding:thing:device:channel")
            
            # Verify failure handling
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Failed to delete link" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_validation_error(self, tool):
        """Test validation error handling."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            
            # Execute the tool with invalid input
            result = await tool.execute("", "invalid_channel")
            
            # Verify validation error
            assert len(result) == 1
            assert result[0].type == "text"
            assert "validation failed" in result[0].text.lower()
            
            # Verify client was not called
            mock_client.delete_link.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_execute_error_handling(self, tool):
        """Test error handling in link deletion."""
        with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
             patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
            
            # Setup mock client to raise exception
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_get_config.return_value = MagicMock()
            mock_client.delete_link.side_effect = Exception("Connection error")
            
            # Execute the tool
            result = await tool.execute("TestItem", "binding:thing:device:channel")
            
            # Verify error handling
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Failed to delete link" in result[0].text
            assert "Connection error" in result[0].text