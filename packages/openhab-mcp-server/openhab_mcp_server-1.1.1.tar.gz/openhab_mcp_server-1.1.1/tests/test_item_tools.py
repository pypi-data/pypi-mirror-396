"""Unit tests for openHAB item control tools."""

import pytest
from unittest.mock import AsyncMock, patch
from aioresponses import aioresponses

from openhab_mcp_server.tools.items import ItemStateTool, ItemCommandTool, ItemListTool
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.utils.openhab_client import OpenHABError


class TestItemStateTool:
    """Unit tests for ItemStateTool."""
    
    def _get_test_config(self):
        """Get test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.fixture
    def tool(self):
        """Create ItemStateTool instance for testing."""
        return ItemStateTool(self._get_test_config())
    
    async def test_execute_success(self, tool):
        """Test successful item state retrieval."""
        item_data = {
            "name": "TestItem",
            "state": "ON",
            "type": "Switch",
            "label": "Test Switch",
            "category": "Light",
            "tags": ["Lighting"],
            "groupNames": ["TestGroup"]
        }
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items/TestItem",
                payload=item_data,
                status=200
            )
            
            result = await tool.execute("TestItem")
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Item: TestItem" in response_text
            assert "State: ON" in response_text
            assert "Type: Switch" in response_text
            assert "Label: Test Switch" in response_text
            assert "Category: Light" in response_text
            assert "Tags: Lighting" in response_text
            assert "Groups: TestGroup" in response_text
    
    async def test_execute_item_not_found(self, tool):
        """Test handling of non-existent item."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items/NonExistentItem",
                status=404
            )
            
            result = await tool.execute("NonExistentItem")
            
            assert len(result) == 1
            assert "Item 'NonExistentItem' not found" in result[0].text
    
    async def test_execute_invalid_item_name(self, tool):
        """Test validation of invalid item names."""
        # Test empty name
        result = await tool.execute("")
        assert len(result) == 1
        assert "Invalid item name" in result[0].text
        assert "Item name cannot be empty" in result[0].text
        
        # Test name with spaces
        result = await tool.execute("Invalid Name")
        assert len(result) == 1
        assert "Invalid item name" in result[0].text
        assert "Item name cannot contain spaces" in result[0].text
        
        # Test name with invalid characters
        result = await tool.execute("Invalid@Name")
        assert len(result) == 1
        assert "Invalid item name" in result[0].text
        assert "can only contain letters, numbers, underscores, and hyphens" in result[0].text
    
    async def test_execute_openhab_error(self, tool):
        """Test handling of openHAB API errors."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items/TestItem",
                status=500,
                payload={"message": "Internal Server Error"}
            )
            
            result = await tool.execute("TestItem")
            
            assert len(result) == 1
            assert "Error retrieving item state" in result[0].text
    
    async def test_format_minimal_item_data(self, tool):
        """Test formatting with minimal item data."""
        item_data = {
            "name": "MinimalItem",
            "state": "OFF",
            "type": "Switch"
        }
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items/MinimalItem",
                payload=item_data,
                status=200
            )
            
            result = await tool.execute("MinimalItem")
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Item: MinimalItem" in response_text
            assert "State: OFF" in response_text
            assert "Type: Switch" in response_text
            # Should not contain optional fields
            assert "Label:" not in response_text
            assert "Category:" not in response_text
            assert "Tags:" not in response_text


class TestItemCommandTool:
    """Unit tests for ItemCommandTool."""
    
    def _get_test_config(self):
        """Get test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.fixture
    def tool(self):
        """Create ItemCommandTool instance for testing."""
        return ItemCommandTool(self._get_test_config())
    
    async def test_execute_success(self, tool):
        """Test successful command sending."""
        with aioresponses() as mock:
            mock.post(
                "http://test-openhab:8080/rest/items/TestItem",
                status=204
            )
            
            result = await tool.execute("TestItem", "ON")
            
            assert len(result) == 1
            assert "Successfully sent command 'ON' to item 'TestItem'" in result[0].text
    
    async def test_execute_command_failure(self, tool):
        """Test handling of command failure."""
        with aioresponses() as mock:
            mock.post(
                "http://test-openhab:8080/rest/items/TestItem",
                status=400,
                payload={"message": "Bad Request"}
            )
            
            result = await tool.execute("TestItem", "INVALID")
            
            assert len(result) == 1
            assert "Failed to send command 'INVALID' to item 'TestItem'" in result[0].text
    
    async def test_execute_invalid_inputs(self, tool):
        """Test validation of invalid inputs."""
        # Test empty item name
        result = await tool.execute("", "ON")
        assert len(result) == 1
        assert "Validation errors" in result[0].text
        assert "Item name: Item name cannot be empty" in result[0].text
        
        # Test empty command
        result = await tool.execute("TestItem", "")
        assert len(result) == 1
        assert "Validation errors" in result[0].text
        assert "Command: Command cannot be empty" in result[0].text
        
        # Test both invalid
        result = await tool.execute("", "")
        assert len(result) == 1
        assert "Validation errors" in result[0].text
        assert "Item name: Item name cannot be empty" in result[0].text
        assert "Command: Command cannot be empty" in result[0].text
    
    async def test_execute_different_command_formats(self, tool):
        """Test sending different command formats."""
        commands = ["ON", "OFF", "50", "INCREASE", "DECREASE", "STOP"]
        
        with aioresponses() as mock:
            for command in commands:
                mock.post(
                    "http://test-openhab:8080/rest/items/TestItem",
                    status=204
                )
            
            for command in commands:
                result = await tool.execute("TestItem", command)
                assert len(result) == 1
                assert f"Successfully sent command '{command}' to item 'TestItem'" in result[0].text


class TestItemListTool:
    """Unit tests for ItemListTool."""
    
    def _get_test_config(self):
        """Get test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.fixture
    def tool(self):
        """Create ItemListTool instance for testing."""
        return ItemListTool(self._get_test_config())
    
    async def test_execute_success_all_items(self, tool):
        """Test successful listing of all items."""
        items_data = [
            {
                "name": "Switch1",
                "state": "ON",
                "type": "Switch",
                "label": "Living Room Light"
            },
            {
                "name": "Dimmer1",
                "state": "75",
                "type": "Dimmer",
                "label": "Bedroom Light"
            },
            {
                "name": "Sensor1",
                "state": "23.5",
                "type": "Number"
            }
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items",
                payload=items_data,
                status=200
            )
            
            result = await tool.execute()
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Found 3 items:" in response_text
            assert "Switch1 (Switch) - State: ON - Living Room Light" in response_text
            assert "Dimmer1 (Dimmer) - State: 75 - Bedroom Light" in response_text
            assert "Sensor1 (Number) - State: 23.5" in response_text
    
    async def test_execute_success_filtered_items(self, tool):
        """Test successful listing with item type filter."""
        switch_items = [
            {
                "name": "Switch1",
                "state": "ON",
                "type": "Switch",
                "label": "Living Room Light"
            },
            {
                "name": "Switch2",
                "state": "OFF",
                "type": "Switch",
                "label": "Kitchen Light"
            }
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items?type=Switch",
                payload=switch_items,
                status=200
            )
            
            result = await tool.execute("Switch")
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Found 2 items of type 'Switch':" in response_text
            assert "Switch1 (Switch) - State: ON - Living Room Light" in response_text
            assert "Switch2 (Switch) - State: OFF - Kitchen Light" in response_text
    
    async def test_execute_no_items_found(self, tool):
        """Test handling when no items are found."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items",
                payload=[],
                status=200
            )
            
            result = await tool.execute()
            
            assert len(result) == 1
            assert "No items found" in result[0].text
    
    async def test_execute_no_items_found_with_filter(self, tool):
        """Test handling when no items are found with filter."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items?type=Dimmer",
                payload=[],
                status=200
            )
            
            result = await tool.execute("Dimmer")
            
            assert len(result) == 1
            assert "No items found of type 'Dimmer'" in result[0].text
    
    async def test_execute_invalid_item_type(self, tool):
        """Test validation of invalid item type."""
        result = await tool.execute("InvalidType")
        
        assert len(result) == 1
        assert "Invalid item type" in result[0].text
        assert "Valid types:" in result[0].text
    
    async def test_execute_empty_item_type(self, tool):
        """Test validation of empty item type."""
        result = await tool.execute("")
        
        assert len(result) == 1
        assert "Invalid item type" in result[0].text
        assert "Item type cannot be empty" in result[0].text
    
    async def test_execute_openhab_error(self, tool):
        """Test handling of openHAB API errors."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items",
                status=500,
                payload={"message": "Internal Server Error"}
            )
            
            result = await tool.execute()
            
            assert len(result) == 1
            assert "Error listing items" in result[0].text
    
    async def test_execute_items_without_labels(self, tool):
        """Test formatting items that don't have labels."""
        items_data = [
            {
                "name": "UnlabeledItem",
                "state": "UNDEF",
                "type": "String"
            }
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items",
                payload=items_data,
                status=200
            )
            
            result = await tool.execute()
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Found 1 items:" in response_text
            assert "UnlabeledItem (String) - State: UNDEF" in response_text
            # Should not have a label part
            assert " - " not in response_text.split("State: UNDEF")[1]


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
