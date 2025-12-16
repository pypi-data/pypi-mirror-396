"""Property-based tests for openHAB thing management tools."""

import asyncio
import json
from typing import Any, Dict, List
import pytest
from hypothesis import given, strategies as st, settings
from aioresponses import aioresponses

from openhab_mcp_server.tools.things import ThingStatusTool, ThingConfigTool, ThingDiscoveryTool
from openhab_mcp_server.utils.config import Config


# Test data generators
@st.composite
def thing_uid_strategy(draw):
    """Generate valid openHAB thing UIDs."""
    # Thing UIDs follow binding:type:id format
    # Only ASCII letters, numbers, underscores, and hyphens are allowed
    # Avoid patterns that trigger security validation (like consecutive hyphens)
    binding = draw(st.text(
        alphabet=st.characters(min_codepoint=ord('a'), max_codepoint=ord('z')) | 
                 st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')) |
                 st.characters(min_codepoint=ord('0'), max_codepoint=ord('9')),
        min_size=2,
        max_size=20
    ))
    thing_type = draw(st.text(
        alphabet=st.characters(min_codepoint=ord('a'), max_codepoint=ord('z')) | 
                 st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')) |
                 st.characters(min_codepoint=ord('0'), max_codepoint=ord('9')),
        min_size=2,
        max_size=20
    ))
    # Generate thing_id without consecutive special characters to avoid security validation
    thing_id_chars = draw(st.lists(
        st.one_of(
            st.characters(min_codepoint=ord('a'), max_codepoint=ord('z')),
            st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')),
            st.characters(min_codepoint=ord('0'), max_codepoint=ord('9')),
            st.just('_'),
            st.just('-')
        ),
        min_size=1,
        max_size=30
    ))
    # Ensure no consecutive hyphens or other patterns that trigger security validation
    thing_id = ''.join(thing_id_chars).replace('--', '-').replace('__', '_')
    if not thing_id:
        thing_id = 'a'
    return f"{binding}:{thing_type}:{thing_id}"


@st.composite
def thing_status_strategy(draw):
    """Generate valid openHAB thing status values."""
    return draw(st.sampled_from(['ONLINE', 'OFFLINE', 'UNKNOWN', 'INITIALIZING', 'REMOVING', 'REMOVED']))


@st.composite
def thing_response_strategy(draw):
    """Generate valid openHAB thing response data."""
    uid = draw(thing_uid_strategy())
    status = draw(thing_status_strategy())
    
    # Generate configuration
    config_keys = draw(st.lists(
        st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=3, max_size=15),
        min_size=0,
        max_size=10,
        unique=True
    ))
    configuration = {}
    for key in config_keys:
        configuration[key] = draw(st.one_of(
            st.text(min_size=1, max_size=50),
            st.integers(min_value=0, max_value=1000),
            st.booleans()
        ))
    
    # Generate channels
    num_channels = draw(st.integers(min_value=0, max_value=15))
    channels = []
    for i in range(num_channels):
        channel_id = f"channel{i}"
        channels.append({
            "uid": f"{uid}:{channel_id}",
            "channelTypeUID": f"system:{draw(st.sampled_from(['switch', 'dimmer', 'number', 'string']))}",
            "label": f"Channel {i}",
            "description": f"Test channel {i}"
        })
    
    return {
        "UID": uid,
        "label": draw(st.text(min_size=1, max_size=100)),
        "thingTypeUID": f"{uid.split(':')[0]}:{uid.split(':')[1]}",
        "statusInfo": {
            "status": status,
            "statusDetail": draw(st.sampled_from(['NONE', 'CONFIGURATION_PENDING', 'COMMUNICATION_ERROR', 'BRIDGE_OFFLINE']))
        },
        "configuration": configuration,
        "channels": channels,
        "bridgeUID": draw(st.one_of(st.none(), thing_uid_strategy()))
    }


@st.composite
def binding_id_strategy(draw):
    """Generate valid binding IDs."""
    # Must start with a letter, then can contain letters, numbers, underscores, hyphens
    # Avoid patterns that trigger security validation
    first_char = draw(st.characters(min_codepoint=ord('a'), max_codepoint=ord('z')) | 
                     st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')))
    rest_chars = draw(st.lists(
        st.one_of(
            st.characters(min_codepoint=ord('a'), max_codepoint=ord('z')),
            st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')),
            st.characters(min_codepoint=ord('0'), max_codepoint=ord('9')),
            st.just('_'),
            st.just('-')
        ),
        min_size=1,
        max_size=29
    ))
    # Ensure no consecutive hyphens or other patterns that trigger security validation
    rest = ''.join(rest_chars).replace('--', '-').replace('__', '_')
    if not rest:
        rest = 'a'
    return first_char + rest


@st.composite
def discovery_result_strategy(draw):
    """Generate discovery result data."""
    thing_uid = draw(thing_uid_strategy())
    return {
        "thingUID": thing_uid,
        "thingTypeUID": f"{thing_uid.split(':')[0]}:{thing_uid.split(':')[1]}",
        "label": draw(st.text(min_size=1, max_size=100)),
        "properties": draw(st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.text(min_size=1, max_size=50),
            min_size=0,
            max_size=5
        ))
    }


class TestThingToolsProperties:
    """Property-based tests for thing management tools."""
    
    def _get_test_config(self):
        """Get test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @given(thing_uid=thing_uid_strategy(), thing_data=thing_response_strategy())
    @settings(max_examples=100, deadline=5000)
    async def test_property_thing_status_completeness(self, thing_uid, thing_data):
        """**Feature: openhab-mcp-server, Property 4: Thing status completeness**
        
        For any valid thing UID, the status query should return both device 
        connectivity and configuration information.
        
        **Validates: Requirements 2.2**
        """
        tool = ThingStatusTool(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock successful thing status response
            mock.get(
                f"http://test-openhab:8080/rest/things/{thing_uid}",
                payload=thing_data,
                status=200
            )
            
            result = await tool.execute(thing_uid)
            
            # Property: Should return exactly one TextContent response
            assert len(result) == 1
            response_text = result[0].text
            
            # Property: Response should contain connectivity information (status)
            status_info = thing_data.get("statusInfo", {})
            expected_status = status_info.get("status", "UNKNOWN")
            assert f"Status: {expected_status}" in response_text
            
            # Property: Response should contain configuration information
            configuration = thing_data.get("configuration", {})
            if configuration:
                assert "Configuration:" in response_text
                # At least some config keys should be present (excluding sensitive ones)
                non_sensitive_keys = [k for k in configuration.keys() 
                                    if not any(sensitive in k.lower() 
                                             for sensitive in ['password', 'token', 'secret', 'key'])]
                if non_sensitive_keys:
                    # At least one non-sensitive config key should appear
                    assert any(key in response_text for key in non_sensitive_keys)
            
            # Property: Response should contain the thing UID
            assert thing_data["UID"] in response_text
            
            # Property: Response should contain the thing label if present
            if thing_data.get("label"):
                assert thing_data["label"] in response_text
    
    @given(
        thing_uid=thing_uid_strategy(),
        configuration=st.dictionaries(
            st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=3, max_size=15),
            st.one_of(
                st.text(min_size=1, max_size=50),
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            ),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=100, deadline=5000)
    async def test_property_configuration_update_validation(self, thing_uid, configuration):
        """**Feature: openhab-mcp-server, Property 7: Configuration update validation**
        
        For any valid thing configuration update, the system should modify device 
        settings and validate the changes are applied correctly.
        
        **Validates: Requirements 3.2**
        """
        tool = ThingConfigTool(self._get_test_config())
        
        # Create mock thing data with the updated configuration
        mock_thing_data = {
            "UID": thing_uid,
            "label": "Test Thing",
            "thingTypeUID": f"{thing_uid.split(':')[0]}:{thing_uid.split(':')[1]}",
            "statusInfo": {"status": "ONLINE", "statusDetail": "NONE"},
            "configuration": configuration,
            "channels": []
        }
        
        with aioresponses() as mock:
            # Mock thing existence check
            mock.get(
                f"http://test-openhab:8080/rest/things/{thing_uid}",
                payload=mock_thing_data,
                status=200
            )
            
            # Mock successful configuration update
            mock.put(
                f"http://test-openhab:8080/rest/things/{thing_uid}/config",
                status=204  # No Content for successful update
            )
            
            # Mock verification call (get thing again to verify update)
            mock.get(
                f"http://test-openhab:8080/rest/things/{thing_uid}",
                payload=mock_thing_data,
                status=200
            )
            
            result = await tool.execute(thing_uid, configuration)
            
            # Property: Should return exactly one TextContent response
            assert len(result) == 1
            response_text = result[0].text
            
            # Property: Response should indicate successful update
            assert "Successfully updated configuration" in response_text
            assert thing_uid in response_text
            
            # Property: Response should show applied changes
            assert "Applied changes:" in response_text
            
            # Property: All configuration keys should be mentioned in the response
            for key, value in configuration.items():
                assert f"{key}: {value}" in response_text
    
    @given(binding_id=binding_id_strategy(), discovered_things=st.lists(discovery_result_strategy(), min_size=0, max_size=10))
    @settings(max_examples=50, deadline=5000)
    async def test_property_discovery_results_format(self, binding_id, discovered_things):
        """Test that discovery results are properly formatted."""
        tool = ThingDiscoveryTool(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock discovery scan trigger
            mock.post(
                f"http://test-openhab:8080/rest/discovery/bindings/{binding_id}/scan",
                status=204
            )
            
            # Mock discovery results
            mock.get(
                "http://test-openhab:8080/rest/discovery",
                payload=discovered_things,
                status=200
            )
            
            result = await tool.execute(binding_id)
            
            # Property: Should return exactly one TextContent response
            assert len(result) == 1
            response_text = result[0].text
            
            # Property: Response should mention the binding ID
            assert binding_id in response_text
            
            if discovered_things:
                # Property: Response should indicate the number of discovered devices
                assert f"{len(discovered_things)} devices found" in response_text
                
                # Property: Each discovered thing should be mentioned
                for thing in discovered_things:
                    thing_uid = thing.get("thingUID", "")
                    if thing_uid:
                        assert thing_uid in response_text
            else:
                # Property: Should indicate no devices found
                assert "No new devices discovered" in response_text
    
    @given(thing_uid=thing_uid_strategy())
    @settings(max_examples=50, deadline=5000)
    async def test_property_nonexistent_thing_handling(self, thing_uid):
        """Test that non-existent things are handled correctly."""
        tool = ThingStatusTool(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock 404 response for non-existent thing
            mock.get(
                f"http://test-openhab:8080/rest/things/{thing_uid}",
                status=404
            )
            
            result = await tool.execute(thing_uid)
            
            # Property: Should return exactly one TextContent response
            assert len(result) == 1
            response_text = result[0].text
            
            # Property: Should indicate thing not found
            assert "not found" in response_text.lower()
            assert thing_uid in response_text


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
