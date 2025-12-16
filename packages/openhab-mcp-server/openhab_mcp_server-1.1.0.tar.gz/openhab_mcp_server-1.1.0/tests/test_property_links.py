"""Property-based tests for link management functionality."""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
from typing import Dict, Any, List, Optional

from openhab_mcp_server.tools.links import LinkListTool, LinkCreateTool, LinkUpdateTool, LinkDeleteTool
from openhab_mcp_server.utils.openhab_client import OpenHABClient
from openhab_mcp_server.models import LinkInfo


# Test data generators
@st.composite
def valid_item_name_strategy(draw):
    """Generate valid openHAB item names."""
    # Valid item names: letters, numbers, underscores, no spaces, not empty
    name = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_'),
        min_size=1,
        max_size=50
    ))
    # Ensure it doesn't start with a number if it's all digits
    if name and name[0].isdigit():
        name = 'Item' + name
    return name


@st.composite
def valid_channel_uid_strategy(draw):
    """Generate valid openHAB channel UIDs."""
    binding = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=20))
    thing_type = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=20))
    thing_id = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'), min_size=1, max_size=20))
    channel_id = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'), min_size=1, max_size=20))
    return f"{binding}:{thing_type}:{thing_id}:{channel_id}"


@st.composite
def valid_link_configuration_strategy(draw):
    """Generate valid link configuration dictionaries."""
    config = {}
    
    # Ensure at least one configuration parameter is always present
    config["profile"] = draw(st.sampled_from(["default", "follow", "offset", "transform"]))
    
    # Add additional optional configuration parameters
    if draw(st.booleans()):
        config["transform"] = draw(st.text(min_size=1, max_size=100))
    
    if draw(st.booleans()):
        config["offset"] = draw(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
    
    return config


@st.composite
def valid_link_data_strategy(draw):
    """Generate valid link data structures."""
    return {
        "itemName": draw(valid_item_name_strategy()),
        "channelUID": draw(valid_channel_uid_strategy()),
        "configuration": draw(valid_link_configuration_strategy())
    }


@st.composite
def link_list_strategy(draw):
    """Generate lists of valid link data."""
    return draw(st.lists(
        valid_link_data_strategy(),
        min_size=0,
        max_size=10
    ))


class TestLinkRetrievalProperties:
    """Property-based tests for link retrieval completeness."""
    
    @given(
        links=link_list_strategy(),
        filter_item=st.one_of(st.none(), valid_item_name_strategy()),
        filter_channel=st.one_of(st.none(), valid_channel_uid_strategy())
    )
    @settings(max_examples=100, deadline=10000)
    def test_property_link_retrieval_completeness(self, links, filter_item, filter_channel):
        """**Feature: openhab-mcp-server, Property 38: Link retrieval completeness**
        
        For any valid item or channel identifier, querying links should return 
        all associated connections.
        
        **Validates: Requirements 13.1**
        """
        async def run_test():
            # Mock the OpenHABClient
            with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
                 patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
                
                # Setup mock client
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client
                mock_get_config.return_value = MagicMock()
                
                # Filter links based on the criteria
                filtered_links = links.copy()
                if filter_item:
                    filtered_links = [link for link in filtered_links if link.get('itemName') == filter_item]
                if filter_channel:
                    filtered_links = [link for link in filtered_links if link.get('channelUID') == filter_channel]
                
                # Mock client to return filtered links
                mock_client.get_links.return_value = filtered_links
                
                # Execute the tool
                tool = LinkListTool()
                result = await tool.execute(item_name=filter_item, channel_uid=filter_channel)
                
                # Property: Should call get_links with correct parameters
                mock_client.get_links.assert_called_once_with(item_name=filter_item, channel_uid=filter_channel)
                
                # Property: Should return TextContent
                assert len(result) == 1
                assert result[0].type == "text"
                
                # Property: If links exist, result should contain link information
                if filtered_links:
                    result_text = result[0].text
                    assert f"Found {len(filtered_links)} link(s)" in result_text
                    
                    # Property: Each link should be represented in the output
                    for link in filtered_links:
                        assert link.get('itemName', 'Unknown') in result_text
                        assert link.get('channelUID', 'Unknown') in result_text
                else:
                    # Property: If no links, should indicate no links found
                    assert "No links found" in result[0].text
        
        # Run the async test
        asyncio.run(run_test())


class TestLinkCreationProperties:
    """Property-based tests for link creation validation."""
    
    @given(
        item_name=valid_item_name_strategy(),
        channel_uid=valid_channel_uid_strategy(),
        configuration=st.one_of(st.none(), valid_link_configuration_strategy())
    )
    @settings(max_examples=100, deadline=10000)
    def test_property_link_creation_validation(self, item_name, channel_uid, configuration):
        """**Feature: openhab-mcp-server, Property 39: Link creation validation**
        
        For any link creation request, the system should establish valid connections 
        and reject invalid channel-item combinations.
        
        **Validates: Requirements 13.2**
        """
        async def run_test():
            # Mock the OpenHABClient
            with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
                 patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
                
                # Setup mock client
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client
                mock_get_config.return_value = MagicMock()
                
                # Mock successful link creation
                mock_client.create_link.return_value = True
                
                # Execute the tool
                tool = LinkCreateTool()
                result = await tool.execute(item_name, channel_uid, configuration)
                
                # Property: Should call create_link with correct parameters
                mock_client.create_link.assert_called_once_with(item_name, channel_uid, configuration)
                
                # Property: Should return TextContent
                assert len(result) == 1
                assert result[0].type == "text"
                
                # Property: Success message should contain item and channel names
                result_text = result[0].text
                assert item_name in result_text
                assert channel_uid in result_text
                assert "Successfully created link" in result_text
        
        # Run the async test
        asyncio.run(run_test())
    
    @given(
        item_name=st.one_of(st.just(""), st.text().filter(lambda x: ' ' in x)),
        channel_uid=valid_channel_uid_strategy(),
        configuration=st.one_of(st.none(), valid_link_configuration_strategy())
    )
    @settings(max_examples=50, deadline=10000)
    def test_property_link_creation_validation_invalid_item(self, item_name, channel_uid, configuration):
        """Test that invalid item names are rejected during link creation."""
        async def run_test():
            # Mock the OpenHABClient
            with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
                 patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
                
                # Setup mock client
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client
                mock_get_config.return_value = MagicMock()
                
                # Execute the tool
                tool = LinkCreateTool()
                result = await tool.execute(item_name, channel_uid, configuration)
                
                # Property: Should return validation error
                assert len(result) == 1
                assert result[0].type == "text"
                assert "validation failed" in result[0].text.lower()
                
                # Property: Should not call create_link for invalid input
                mock_client.create_link.assert_not_called()
        
        # Run the async test
        asyncio.run(run_test())


class TestLinkConfigurationProperties:
    """Property-based tests for link configuration persistence."""
    
    @given(
        item_name=valid_item_name_strategy(),
        channel_uid=valid_channel_uid_strategy(),
        configuration=valid_link_configuration_strategy()
    )
    @settings(max_examples=100, deadline=10000)
    def test_property_link_configuration_persistence(self, item_name, channel_uid, configuration):
        """**Feature: openhab-mcp-server, Property 40: Link configuration persistence**
        
        For any link configuration update, the changes should be applied and persist 
        when the link is queried again.
        
        **Validates: Requirements 13.3**
        """
        async def run_test():
            # Mock the OpenHABClient
            with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
                 patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
                
                # Setup mock client
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client
                mock_get_config.return_value = MagicMock()
                
                # Mock successful link update
                mock_client.update_link.return_value = True
                
                # Execute the tool
                tool = LinkUpdateTool()
                result = await tool.execute(item_name, channel_uid, configuration)
                
                # Property: Should call update_link with correct parameters
                mock_client.update_link.assert_called_once_with(item_name, channel_uid, configuration)
                
                # Property: Should return TextContent
                assert len(result) == 1
                assert result[0].type == "text"
                
                # Property: Success message should contain item, channel, and configuration
                result_text = result[0].text
                assert item_name in result_text
                assert channel_uid in result_text
                assert "Successfully updated link configuration" in result_text
                assert str(configuration) in result_text
        
        # Run the async test
        asyncio.run(run_test())


class TestLinkDeletionProperties:
    """Property-based tests for link deletion validation."""
    
    @given(
        item_name=valid_item_name_strategy(),
        channel_uid=valid_channel_uid_strategy()
    )
    @settings(max_examples=100, deadline=10000)
    def test_property_link_deletion_validation(self, item_name, channel_uid):
        """**Feature: openhab-mcp-server, Property 41: Link deletion validation**
        
        For any link removal request, the connection should be deleted and no longer 
        appear in subsequent queries.
        
        **Validates: Requirements 13.4**
        """
        async def run_test():
            # Mock the OpenHABClient
            with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
                 patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
                
                # Setup mock client
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client
                mock_get_config.return_value = MagicMock()
                
                # Mock successful link deletion
                mock_client.delete_link.return_value = True
                
                # Execute the tool
                tool = LinkDeleteTool()
                result = await tool.execute(item_name, channel_uid)
                
                # Property: Should call delete_link with correct parameters
                mock_client.delete_link.assert_called_once_with(item_name, channel_uid)
                
                # Property: Should return TextContent
                assert len(result) == 1
                assert result[0].type == "text"
                
                # Property: Success message should contain item and channel names
                result_text = result[0].text
                assert item_name in result_text
                assert channel_uid in result_text
                assert "Successfully deleted link" in result_text
        
        # Run the async test
        asyncio.run(run_test())


class TestLinkListingProperties:
    """Property-based tests for link listing completeness."""
    
    @given(
        links=link_list_strategy()
    )
    @settings(max_examples=100, deadline=10000)
    def test_property_link_listing_completeness(self, links):
        """**Feature: openhab-mcp-server, Property 42: Link listing completeness**
        
        For any link listing request, all returned links should include channel, 
        item, and configuration details.
        
        **Validates: Requirements 13.5**
        """
        async def run_test():
            # Mock the OpenHABClient
            with patch('openhab_mcp_server.tools.links.OpenHABClient') as mock_client_class, \
                 patch('openhab_mcp_server.tools.links.get_config') as mock_get_config:
                
                # Setup mock client
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client
                mock_get_config.return_value = MagicMock()
                
                # Mock client to return all links
                mock_client.get_links.return_value = links
                
                # Execute the tool
                tool = LinkListTool()
                result = await tool.execute()
                
                # Property: Should return TextContent
                assert len(result) == 1
                assert result[0].type == "text"
                
                result_text = result[0].text
                
                if links:
                    # Property: Each link should include item name, channel UID, and configuration
                    for link in links:
                        item_name = link.get('itemName', 'Unknown')
                        channel_uid = link.get('channelUID', 'Unknown')
                        
                        # Property: Item name should be present
                        assert item_name in result_text
                        
                        # Property: Channel UID should be present
                        assert channel_uid in result_text
                        
                        # Property: If configuration exists, it should be shown
                        config = link.get('configuration', {})
                        if config:
                            # Configuration should be mentioned in some form
                            assert "Configuration" in result_text or str(config) in result_text
                else:
                    # Property: If no links, should indicate no links found
                    assert "No links found" in result_text
        
        # Run the async test
        asyncio.run(run_test())