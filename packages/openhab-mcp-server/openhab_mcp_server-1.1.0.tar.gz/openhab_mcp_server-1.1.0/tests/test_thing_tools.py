"""Unit tests for openHAB thing management tools."""

import pytest
from unittest.mock import AsyncMock, patch
from aioresponses import aioresponses

from openhab_mcp_server.tools.things import ThingStatusTool, ThingConfigTool, ThingDiscoveryTool
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.utils.openhab_client import OpenHABError


class TestThingStatusTool:
    """Unit tests for ThingStatusTool."""
    
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
        """Create ThingStatusTool instance for testing."""
        return ThingStatusTool(self._get_test_config())
    
    async def test_execute_success_full_data(self, tool):
        """Test successful thing status retrieval with full data."""
        thing_data = {
            "UID": "zwave:device:controller:node5",
            "label": "Living Room Motion Sensor",
            "thingTypeUID": "zwave:device",
            "statusInfo": {
                "status": "ONLINE",
                "statusDetail": "NONE"
            },
            "configuration": {
                "node_id": 5,
                "wakeup_interval": 3600,
                "association_group_1": "1"
            },
            "channels": [
                {
                    "uid": "zwave:device:controller:node5:sensor_binary",
                    "channelTypeUID": "zwave:sensor_binary",
                    "label": "Binary Sensor"
                },
                {
                    "uid": "zwave:device:controller:node5:battery-level",
                    "channelTypeUID": "system:battery-level",
                    "label": "Battery Level"
                }
            ],
            "bridgeUID": "zwave:serial_zstick:controller"
        }
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/things/zwave:device:controller:node5",
                payload=thing_data,
                status=200
            )
            
            result = await tool.execute("zwave:device:controller:node5")
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Thing: zwave:device:controller:node5" in response_text
            assert "Status: ONLINE" in response_text
            assert "Status Detail: NONE" in response_text
            assert "Label: Living Room Motion Sensor" in response_text
            assert "Type: zwave:device" in response_text
            assert "Bridge: zwave:serial_zstick:controller" in response_text
            assert "Configuration:" in response_text
            assert "node_id: 5" in response_text
            assert "wakeup_interval: 3600" in response_text
            assert "Channels (2):" in response_text
            assert "sensor_binary" in response_text
            assert "battery-level" in response_text
    
    async def test_execute_success_minimal_data(self, tool):
        """Test successful thing status retrieval with minimal data."""
        thing_data = {
            "UID": "binding:type:id",
            "statusInfo": {
                "status": "OFFLINE",
                "statusDetail": "COMMUNICATION_ERROR"
            }
        }
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/things/binding:type:id",
                payload=thing_data,
                status=200
            )
            
            result = await tool.execute("binding:type:id")
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Thing: binding:type:id" in response_text
            assert "Status: OFFLINE" in response_text
            assert "Status Detail: COMMUNICATION_ERROR" in response_text
            # Should not contain optional fields
            assert "Label:" not in response_text
            assert "Type:" not in response_text
            assert "Bridge:" not in response_text
            assert "Configuration:" not in response_text
            assert "Channels:" not in response_text
    
    async def test_execute_thing_not_found(self, tool):
        """Test handling of non-existent thing."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/things/nonexistent:thing:id",
                status=404
            )
            
            result = await tool.execute("nonexistent:thing:id")
            
            assert len(result) == 1
            assert "Thing 'nonexistent:thing:id' not found" in result[0].text
    
    async def test_execute_invalid_thing_uid(self, tool):
        """Test validation of invalid thing UIDs."""
        # Test empty UID
        result = await tool.execute("")
        assert len(result) == 1
        assert "Invalid thing UID" in result[0].text
        assert "Thing UID cannot be empty" in result[0].text
        
        # Test UID without colons
        result = await tool.execute("invaliduid")
        assert len(result) == 1
        assert "Invalid thing UID" in result[0].text
        assert "must contain at least binding and type separated by ':'" in result[0].text
        
        # Test UID with empty parts
        result = await tool.execute("binding::id")
        assert len(result) == 1
        assert "Invalid thing UID" in result[0].text
        assert "Thing UID part 2 cannot be empty" in result[0].text
    
    async def test_execute_openhab_error(self, tool):
        """Test handling of openHAB API errors."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/things/test:thing:id",
                status=500,
                payload={"message": "Internal Server Error"}
            )
            
            result = await tool.execute("test:thing:id")
            
            assert len(result) == 1
            assert "Error retrieving thing status" in result[0].text
    
    async def test_execute_sensitive_config_masking(self, tool):
        """Test that sensitive configuration values are masked."""
        thing_data = {
            "UID": "binding:type:id",
            "statusInfo": {"status": "ONLINE", "statusDetail": "NONE"},
            "configuration": {
                "username": "user123",
                "password": "secret123",
                "api_token": "abc123def456",
                "secret_key": "mysecret",
                "normal_config": "visible_value"
            }
        }
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/things/binding:type:id",
                payload=thing_data,
                status=200
            )
            
            result = await tool.execute("binding:type:id")
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Configuration:" in response_text
            assert "normal_config: visible_value" in response_text
            # Sensitive values should be masked
            assert "password: ***" in response_text
            assert "api_token: ***" in response_text
            assert "secret_key: ***" in response_text
            # Should not contain actual sensitive values
            assert "secret123" not in response_text
            assert "abc123def456" not in response_text
            assert "mysecret" not in response_text
    
    async def test_execute_many_channels_truncation(self, tool):
        """Test that many channels are truncated in display."""
        channels = []
        for i in range(15):
            channels.append({
                "uid": f"binding:type:id:channel{i}",
                "channelTypeUID": f"system:channel{i}",
                "label": f"Channel {i}"
            })
        
        thing_data = {
            "UID": "binding:type:id",
            "statusInfo": {"status": "ONLINE", "statusDetail": "NONE"},
            "channels": channels
        }
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/things/binding:type:id",
                payload=thing_data,
                status=200
            )
            
            result = await tool.execute("binding:type:id")
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Channels (15):" in response_text
            assert "channel0" in response_text
            assert "channel9" in response_text
            assert "and 5 more channels" in response_text
            # Should not show all channels
            assert "channel14" not in response_text


class TestThingConfigTool:
    """Unit tests for ThingConfigTool."""
    
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
        """Create ThingConfigTool instance for testing."""
        return ThingConfigTool(self._get_test_config())
    
    async def test_execute_success(self, tool):
        """Test successful configuration update."""
        existing_thing = {
            "UID": "test:thing:id",
            "statusInfo": {"status": "ONLINE", "statusDetail": "NONE"},
            "configuration": {"param1": "old_value", "param2": 100}
        }
        
        updated_thing = {
            "UID": "test:thing:id",
            "statusInfo": {"status": "ONLINE", "statusDetail": "NONE"},
            "configuration": {"param1": "new_value", "param2": 200}
        }
        
        new_config = {"param1": "new_value", "param2": 200}
        
        with aioresponses() as mock:
            # Mock thing existence check
            mock.get(
                "http://test-openhab:8080/rest/things/test:thing:id",
                payload=existing_thing,
                status=200
            )
            
            # Mock configuration update
            mock.put(
                "http://test-openhab:8080/rest/things/test:thing:id/config",
                status=204
            )
            
            # Mock verification call
            mock.get(
                "http://test-openhab:8080/rest/things/test:thing:id",
                payload=updated_thing,
                status=200
            )
            
            result = await tool.execute("test:thing:id", new_config)
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Successfully updated configuration for thing 'test:thing:id'" in response_text
            assert "Applied changes:" in response_text
            assert "param1: new_value" in response_text
            assert "param2: 200" in response_text
    
    async def test_execute_thing_not_found(self, tool):
        """Test handling when thing doesn't exist."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/things/nonexistent:thing:id",
                status=404
            )
            
            result = await tool.execute("nonexistent:thing:id", {"param": "value"})
            
            assert len(result) == 1
            assert "Thing 'nonexistent:thing:id' not found" in result[0].text
    
    async def test_execute_invalid_inputs(self, tool):
        """Test validation of invalid inputs."""
        # Test invalid thing UID
        result = await tool.execute("", {"param": "value"})
        assert len(result) == 1
        assert "Validation errors" in result[0].text
        assert "Thing UID: Thing UID cannot be empty" in result[0].text
        
        # Test empty configuration
        result = await tool.execute("test:thing:id", {})
        assert len(result) == 1
        assert "Validation errors" in result[0].text
        assert "Configuration: Configuration cannot be empty" in result[0].text
        
        # Test non-dict configuration
        result = await tool.execute("test:thing:id", "not_a_dict")
        assert len(result) == 1
        assert "Validation errors" in result[0].text
        assert "Configuration: Configuration must be a dictionary" in result[0].text
    
    async def test_execute_config_update_failure(self, tool):
        """Test handling of configuration update failure."""
        existing_thing = {
            "UID": "test:thing:id",
            "statusInfo": {"status": "ONLINE", "statusDetail": "NONE"},
            "configuration": {}
        }
        
        with aioresponses() as mock:
            # Mock thing existence check
            mock.get(
                "http://test-openhab:8080/rest/things/test:thing:id",
                payload=existing_thing,
                status=200
            )
            
            # Mock configuration update failure
            mock.put(
                "http://test-openhab:8080/rest/things/test:thing:id/config",
                status=400,
                payload={"message": "Invalid configuration"}
            )
            
            result = await tool.execute("test:thing:id", {"param": "value"})
            
            assert len(result) == 1
            assert "Failed to update configuration for thing 'test:thing:id'" in result[0].text
    
    async def test_execute_different_config_types(self, tool):
        """Test configuration updates with different value types."""
        existing_thing = {
            "UID": "test:thing:id",
            "statusInfo": {"status": "ONLINE", "statusDetail": "NONE"},
            "configuration": {}
        }
        
        updated_thing = {
            "UID": "test:thing:id",
            "statusInfo": {"status": "ONLINE", "statusDetail": "NONE"},
            "configuration": {
                "string_param": "text_value",
                "int_param": 42,
                "bool_param": True,
                "float_param": 3.14
            }
        }
        
        config = {
            "string_param": "text_value",
            "int_param": 42,
            "bool_param": True,
            "float_param": 3.14
        }
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/things/test:thing:id",
                payload=existing_thing,
                status=200
            )
            mock.put(
                "http://test-openhab:8080/rest/things/test:thing:id/config",
                status=204
            )
            mock.get(
                "http://test-openhab:8080/rest/things/test:thing:id",
                payload=updated_thing,
                status=200
            )
            
            result = await tool.execute("test:thing:id", config)
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Successfully updated configuration" in response_text
            assert "string_param: text_value" in response_text
            assert "int_param: 42" in response_text
            assert "bool_param: True" in response_text
            assert "float_param: 3.14" in response_text


class TestThingDiscoveryTool:
    """Unit tests for ThingDiscoveryTool."""
    
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
        """Create ThingDiscoveryTool instance for testing."""
        return ThingDiscoveryTool(self._get_test_config())
    
    async def test_execute_success_with_discoveries(self, tool):
        """Test successful discovery with found devices."""
        discovered_things = [
            {
                "thingUID": "zwave:device:controller:node10",
                "thingTypeUID": "zwave:device",
                "label": "Unknown Device",
                "properties": {
                    "vendor": "AEON Labs",
                    "deviceType": "Motion Sensor",
                    "nodeId": "10"
                }
            },
            {
                "thingUID": "zwave:device:controller:node11",
                "thingTypeUID": "zwave:device",
                "label": "Door Sensor",
                "properties": {
                    "vendor": "FIBARO",
                    "deviceType": "Door/Window Sensor",
                    "nodeId": "11",
                    "version": "3.2",
                    "manufacturer": "0x010f"
                }
            }
        ]
        
        with aioresponses() as mock:
            # Mock discovery scan trigger
            mock.post(
                "http://test-openhab:8080/rest/discovery/bindings/zwave/scan",
                status=204
            )
            
            # Mock discovery results
            mock.get(
                "http://test-openhab:8080/rest/discovery",
                payload=discovered_things,
                status=200
            )
            
            result = await tool.execute("zwave")
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Discovery results for binding 'zwave' (2 devices found):" in response_text
            assert "zwave:device:controller:node10 - Unknown Device (zwave:device)" in response_text
            assert "zwave:device:controller:node11 - Door Sensor (zwave:device)" in response_text
            assert "Properties: vendor: AEON Labs, deviceType: Motion Sensor, nodeId: 10" in response_text
            assert "Properties: vendor: FIBARO, deviceType: Door/Window Sensor, nodeId: 11" in response_text
            assert "(and 2 more)" in response_text  # Should show truncation for second device
    
    async def test_execute_success_no_discoveries(self, tool):
        """Test successful discovery with no found devices."""
        with aioresponses() as mock:
            # Mock discovery scan trigger
            mock.post(
                "http://test-openhab:8080/rest/discovery/bindings/zigbee/scan",
                status=204
            )
            
            # Mock empty discovery results
            mock.get(
                "http://test-openhab:8080/rest/discovery",
                payload=[],
                status=200
            )
            
            result = await tool.execute("zigbee")
            
            assert len(result) == 1
            assert "No new devices discovered for binding 'zigbee'" in result[0].text
    
    async def test_execute_invalid_binding_id(self, tool):
        """Test validation of invalid binding IDs."""
        # Test empty binding ID
        result = await tool.execute("")
        assert len(result) == 1
        assert "Invalid binding ID" in result[0].text
        assert "Binding ID cannot be empty" in result[0].text
        
        # Test binding ID with invalid characters
        result = await tool.execute("invalid@binding")
        assert len(result) == 1
        assert "Invalid binding ID" in result[0].text
        assert "can only contain letters, numbers, underscores, and hyphens" in result[0].text
        
        # Test too long binding ID
        long_id = "a" * 51
        result = await tool.execute(long_id)
        assert len(result) == 1
        assert "Invalid binding ID" in result[0].text
        assert "Input too long (max 50 characters)" in result[0].text
    
    async def test_execute_discovery_error(self, tool):
        """Test handling of discovery errors."""
        with aioresponses() as mock:
            # Mock discovery scan failure
            mock.post(
                "http://test-openhab:8080/rest/discovery/bindings/nonexistent/scan",
                status=404,
                payload={"message": "Binding not found"}
            )
            
            result = await tool.execute("nonexistent")
            
            assert len(result) == 1
            # The client catches API errors and returns empty list, so tool reports no devices found
            assert "No new devices discovered for binding 'nonexistent'" in result[0].text
    
    async def test_execute_minimal_discovery_data(self, tool):
        """Test discovery with minimal device data."""
        discovered_things = [
            {
                "thingUID": "binding:type:id1",
                "thingTypeUID": "binding:type"
                # No label or properties
            }
        ]
        
        with aioresponses() as mock:
            mock.post(
                "http://test-openhab:8080/rest/discovery/bindings/test/scan",
                status=204
            )
            mock.get(
                "http://test-openhab:8080/rest/discovery",
                payload=discovered_things,
                status=200
            )
            
            result = await tool.execute("test")
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Discovery results for binding 'test' (1 devices found):" in response_text
            assert "binding:type:id1 (binding:type)" in response_text
            # Should not contain properties section
            assert "Properties:" not in response_text
    
    async def test_execute_valid_binding_ids(self, tool):
        """Test discovery with various valid binding ID formats."""
        valid_ids = ["zwave", "zigbee", "hue", "mqtt-broker", "serial_binding", "test123"]
        
        with aioresponses() as mock:
            for binding_id in valid_ids:
                mock.post(
                    f"http://test-openhab:8080/rest/discovery/bindings/{binding_id}/scan",
                    status=204
                )
                mock.get(
                    "http://test-openhab:8080/rest/discovery",
                    payload=[],
                    status=200
                )
            
            for binding_id in valid_ids:
                result = await tool.execute(binding_id)
                assert len(result) == 1
                assert f"No new devices discovered for binding '{binding_id}'" in result[0].text


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
