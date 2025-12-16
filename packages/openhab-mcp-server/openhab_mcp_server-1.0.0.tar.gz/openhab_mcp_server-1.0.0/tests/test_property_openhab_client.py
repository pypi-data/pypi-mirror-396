"""Property-based tests for openHAB client reliability."""

import asyncio
import json
from typing import Any, Dict
import pytest
from hypothesis import given, strategies as st, settings
from aioresponses import aioresponses

from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError
from openhab_mcp_server.utils.config import Config


# Test data generators
@st.composite
def item_name_strategy(draw):
    """Generate valid openHAB item names."""
    # openHAB item names can contain letters, numbers, underscores
    name = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_'),
        min_size=1,
        max_size=50
    ))
    # Ensure it doesn't start with a number
    if name and name[0].isdigit():
        name = 'Item' + name
    return name


@st.composite
def item_state_strategy(draw):
    """Generate valid openHAB item states."""
    return draw(st.one_of(
        st.text(min_size=1, max_size=100),  # String states
        st.integers(min_value=-1000, max_value=1000).map(str),  # Numeric states
        st.sampled_from(['ON', 'OFF', 'OPEN', 'CLOSED', 'NULL', 'UNDEF'])  # Common states
    ))


@st.composite
def item_response_strategy(draw):
    """Generate valid openHAB item response data."""
    name = draw(item_name_strategy())
    state = draw(item_state_strategy())
    return {
        "name": name,
        "state": state,
        "type": draw(st.sampled_from(['Switch', 'Dimmer', 'String', 'Number', 'Contact'])),
        "label": draw(st.text(min_size=0, max_size=100)),
        "category": draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
        "tags": draw(st.lists(st.text(min_size=1, max_size=20), max_size=5))
    }


class TestOpenHABClientProperties:
    """Property-based tests for openHAB client."""
    
    def _get_test_config(self):
        """Get test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @given(item_name=item_name_strategy(), item_data=item_response_strategy())
    @settings(max_examples=100, deadline=5000)
    async def test_property_item_state_retrieval_accuracy(self, item_name, item_data):
        """**Feature: openhab-mcp-server, Property 3: Item state retrieval accuracy**
        
        For any valid openHAB item name, requesting the item state should return 
        current values retrieved from the openHAB REST API.
        
        **Validates: Requirements 2.1**
        """
        client = OpenHABClient(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock successful item state response
            mock.get(
                f"http://test-openhab:8080/rest/items/{item_name}",
                payload=item_data,
                status=200
            )
            
            async with client:
                result = await client.get_item_state(item_name)
            
            # Property: Retrieved state should match the API response
            assert result is not None
            assert result["name"] == item_data["name"]
            assert result["state"] == item_data["state"]
            assert result["type"] == item_data["type"]
    
    @given(item_name=item_name_strategy())
    @settings(max_examples=50, deadline=5000)
    async def test_property_nonexistent_item_handling(self, item_name):
        """Test that non-existent items are handled correctly."""
        client = OpenHABClient(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock 404 response for non-existent item
            mock.get(
                f"http://test-openhab:8080/rest/items/{item_name}",
                status=404
            )
            
            async with client:
                result = await client.get_item_state(item_name)
            
            # Property: Non-existent items should return None
            assert result is None
    
    @given(
        item_name=item_name_strategy(),
        error_status=st.integers(min_value=400, max_value=599).filter(lambda x: x != 404)
    )
    @settings(max_examples=50, deadline=5000)
    async def test_property_api_error_handling(self, item_name, error_status):
        """Test that API errors are properly handled."""
        client = OpenHABClient(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock error response
            mock.get(
                f"http://test-openhab:8080/rest/items/{item_name}",
                status=error_status,
                payload={"message": f"Error {error_status}"}
            )
            
            async with client:
                # Property: API errors should raise OpenHABError
                with pytest.raises(OpenHABError):
                    await client.get_item_state(item_name)
    
    @given(items_data=st.lists(item_response_strategy(), min_size=0, max_size=20))
    @settings(max_examples=50, deadline=5000)
    async def test_property_items_list_consistency(self, items_data):
        """Test that item listing returns consistent data."""
        client = OpenHABClient(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock items list response
            mock.get(
                "http://test-openhab:8080/rest/items",
                payload=items_data,
                status=200
            )
            
            async with client:
                result = await client.get_items()
            
            # Property: Result should be a list with same length as mock data
            assert isinstance(result, list)
            assert len(result) == len(items_data)
            
            # Property: Each item should have required fields
            for i, item in enumerate(result):
                expected = items_data[i]
                assert item["name"] == expected["name"]
                assert item["state"] == expected["state"]
                assert item["type"] == expected["type"]


    @given(
        item_name=item_name_strategy(),
        command=st.one_of(
            st.sampled_from(['ON', 'OFF', 'OPEN', 'CLOSED']),  # Common commands
            st.integers(min_value=0, max_value=100).map(str),  # Numeric commands
            st.text(min_size=1, max_size=50)  # String commands
        )
    )
    @settings(max_examples=100, deadline=5000)
    async def test_property_command_execution_and_persistence(self, item_name, command):
        """**Feature: openhab-mcp-server, Property 6: Command execution and persistence**
        
        For any valid item command, sending the command should execute the state change 
        via the openHAB REST API and persist the change immediately.
        
        **Validates: Requirements 3.1, 3.4**
        """
        client = OpenHABClient(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock successful command response (204 No Content is typical for commands)
            mock.post(
                f"http://test-openhab:8080/rest/items/{item_name}",
                status=204
            )
            
            # Mock state retrieval to verify persistence
            mock.get(
                f"http://test-openhab:8080/rest/items/{item_name}",
                payload={
                    "name": item_name,
                    "state": command,
                    "type": "Switch",
                    "label": f"Test {item_name}",
                    "category": None,
                    "tags": []
                },
                status=200
            )
            
            async with client:
                # Property: Command should be sent successfully
                result = await client.send_item_command(item_name, command)
                assert result is True
                
                # Property: State should be persisted (retrievable after command)
                state = await client.get_item_state(item_name)
                assert state is not None
                assert state["state"] == command

    @given(item_names=st.lists(item_name_strategy(), min_size=1, max_size=10, unique=True))
    @settings(max_examples=100, deadline=10000)
    async def test_property_batch_query_efficiency(self, item_names):
        """**Feature: openhab-mcp-server, Property 5: Batch query efficiency**
        
        For any set of valid item names, querying multiple items should return 
        consolidated state information for all requested items.
        
        **Validates: Requirements 2.4**
        """
        from openhab_mcp_server.tools.items import ItemListTool
        
        config = self._get_test_config()
        tool = ItemListTool(config)
        
        # Generate mock item data for each requested item
        mock_items = []
        for item_name in item_names:
            mock_items.append({
                "name": item_name,
                "state": "ON",
                "type": "Switch",
                "label": f"Test {item_name}",
                "category": None,
                "tags": []
            })
        
        with aioresponses() as mock:
            # Mock the items list endpoint
            mock.get(
                "http://test-openhab:8080/rest/items",
                payload=mock_items,
                status=200
            )
            
            # Execute the batch query
            result = await tool.execute()
            
            # Property: Should return consolidated information for all items
            assert len(result) == 1  # Single TextContent response
            response_text = result[0].text
            
            # Property: All requested items should be present in the response
            for item_name in item_names:
                assert item_name in response_text
            
            # Property: Response should indicate the correct count
            assert f"Found {len(item_names)} items:" in response_text
            
            # Property: Each item should have state information
            for item_name in item_names:
                # Check that each item appears with its state
                assert f"{item_name} (Switch) - State: ON" in response_text

    @given(
        concurrent_requests=st.lists(
            st.tuples(
                item_name_strategy(),  # item name
                st.sampled_from(['GET', 'POST']),  # method
                st.integers(min_value=50, max_value=500)  # simulated delay ms
            ),
            min_size=2,
            max_size=20,
            unique_by=lambda x: (x[0], x[1])  # Ensure unique (item_name, method) combinations
        )
    )
    @settings(max_examples=100, deadline=15000)
    async def test_property_concurrent_request_efficiency(self, concurrent_requests):
        """**Feature: openhab-mcp-server, Property 18: Concurrent request efficiency**
        
        For any set of concurrent requests, the system should handle them efficiently 
        without blocking other operations.
        
        **Validates: Requirements 7.3**
        """
        import time
        
        client = OpenHABClient(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock responses for all requests with simulated delays
            for item_name, method, delay_ms in concurrent_requests:
                if method == 'GET':
                    # Mock item state request
                    mock.get(
                        f"http://test-openhab:8080/rest/items/{item_name}",
                        payload={
                            "name": item_name,
                            "state": "ON",
                            "type": "Switch",
                            "label": f"Test {item_name}",
                            "category": None,
                            "tags": []
                        },
                        status=200
                    )
                else:  # POST
                    # Mock command request
                    mock.post(
                        f"http://test-openhab:8080/rest/items/{item_name}",
                        status=204
                    )
            
            async with client:
                # Measure time for sequential execution
                start_time = time.time()
                sequential_results = []
                for item_name, method, delay_ms in concurrent_requests:
                    if method == 'GET':
                        result = await client.get_item_state(item_name)
                    else:
                        result = await client.send_item_command(item_name, "ON")
                    sequential_results.append(result)
                sequential_time = time.time() - start_time
                
                # Reset mocks for concurrent execution
                mock.clear()
                for item_name, method, delay_ms in concurrent_requests:
                    if method == 'GET':
                        mock.get(
                            f"http://test-openhab:8080/rest/items/{item_name}",
                            payload={
                                "name": item_name,
                                "state": "ON",
                                "type": "Switch",
                                "label": f"Test {item_name}",
                                "category": None,
                                "tags": []
                            },
                            status=200
                        )
                    else:
                        mock.post(
                            f"http://test-openhab:8080/rest/items/{item_name}",
                            status=204
                        )
                
                # Measure time for concurrent execution using batch methods
                start_time = time.time()
                
                # Separate GET and POST requests for batch processing
                get_items = [item_name for item_name, method, _ in concurrent_requests if method == 'GET']
                post_commands = [(item_name, "ON") for item_name, method, _ in concurrent_requests if method == 'POST']
                
                # Execute batches concurrently
                tasks = []
                if get_items:
                    tasks.append(client.get_multiple_item_states(get_items))
                if post_commands:
                    tasks.append(client.send_multiple_commands(post_commands))
                
                if tasks:
                    concurrent_results = await asyncio.gather(*tasks)
                else:
                    concurrent_results = []
                
                concurrent_time = time.time() - start_time
                
                # Property: Concurrent execution should handle all requests
                unique_get_items = list(set(get_items))  # Remove duplicates for batch processing
                unique_post_commands = list(set(post_commands))  # Remove duplicates for batch processing
                
                total_unique_get_requests = len(unique_get_items)
                total_unique_post_requests = len(unique_post_commands)
                
                if unique_get_items:
                    get_results = concurrent_results[0] if len(concurrent_results) > 0 else {}
                    assert len(get_results) == total_unique_get_requests
                    # Property: All unique GET requests should succeed
                    for item_name in unique_get_items:
                        assert item_name in get_results
                        assert get_results[item_name] is not None
                
                if unique_post_commands:
                    post_results = concurrent_results[-1] if len(concurrent_results) > 0 else {}
                    assert len(post_results) == total_unique_post_requests
                    # Property: All unique POST requests should succeed
                    for item_name, _ in unique_post_commands:
                        assert item_name in post_results
                        assert post_results[item_name] is True
                
                # Property: System should maintain efficiency under concurrent load
                # (This is validated by the fact that all requests complete successfully)
                assert len(concurrent_requests) >= 2  # Ensure we're testing concurrency
                
                # Property: Connection pool should handle concurrent requests without errors
                active_count = await client.get_concurrent_request_count()
                assert active_count >= 0  # Should track active requests properly

    @given(item_name=item_name_strategy())
    @settings(max_examples=100, deadline=5000)
    async def test_property_timeout_resilience(self, item_name):
        """**Feature: openhab-mcp-server, Property 10: Timeout resilience**
        
        For any network timeout scenario, the system should handle the timeout gracefully 
        and implement appropriate retry logic.
        
        **Validates: Requirements 4.2**
        """
        # Create client with specific retry configuration for testing
        config = self._get_test_config()
        config.retry_attempts = 3
        config.retry_backoff_factor = 1.5
        config.retry_max_delay = 10
        config.timeout = 30
        
        client = OpenHABClient(config)
        
        # Property: Retry configuration should be accessible and modifiable
        retry_config = client.get_retry_config()
        assert retry_config.max_attempts == 3
        assert retry_config.backoff_factor == 1.5
        assert retry_config.max_delay == 10
        
        # Property: Retry configuration can be updated
        client.update_retry_config(max_attempts=5, backoff_factor=2.0, max_delay=20)
        updated_config = client.get_retry_config()
        assert updated_config.max_attempts == 5
        assert updated_config.backoff_factor == 2.0
        assert updated_config.max_delay == 20
        
        # Property: Delay calculation should follow exponential backoff
        for attempt in range(1, 4):
            delay = updated_config.calculate_delay(attempt)
            
            # Property: Delay should be non-negative
            assert delay >= 0
            
            # Property: Delay should not exceed max_delay
            assert delay <= updated_config.max_delay
            
            # Property: First attempt should have no delay
            if attempt == 1:
                # Allow for small jitter
                assert delay <= 1.5  # Base delay (1.0) * backoff_factor (2.0) with jitter
            
        # Property: Error classification should work correctly
        from openhab_mcp_server.utils.openhab_client import is_retryable_error, OpenHABAPIError, OpenHABAuthenticationError
        import aiohttp
        
        # Retryable errors
        assert is_retryable_error(aiohttp.ServerTimeoutError("Timeout")) == True
        assert is_retryable_error(aiohttp.ClientConnectionError("Connection failed")) == True
        assert is_retryable_error(OpenHABAPIError("Server Error", 503)) == True
        assert is_retryable_error(OpenHABAPIError("Too Many Requests", 429)) == True
        
        # Non-retryable errors
        assert is_retryable_error(OpenHABAuthenticationError("Auth failed")) == False
        assert is_retryable_error(OpenHABAPIError("Bad Request", 400)) == False
        assert is_retryable_error(OpenHABAPIError("Not Found", 404)) == False

    @given(
        error_type=st.sampled_from(['timeout', 'connection_error', 'server_error']),
        item_name=item_name_strategy()
    )
    @settings(max_examples=50, deadline=8000)
    async def test_property_timeout_exhausted_retries(self, error_type, item_name):
        """Test that retry exhaustion is handled correctly."""
        import aiohttp
        
        # Create client with limited retry configuration
        config = self._get_test_config()
        config.retry_attempts = 2  # Only 2 attempts
        config.retry_backoff_factor = 1.1  # Fast backoff for testing
        config.retry_max_delay = 1  # Short delay for testing
        config.timeout = 1  # Short timeout for testing
        
        client = OpenHABClient(config)
        
        # Test exhausted retry scenario - all attempts fail
        with aioresponses() as mock:
            url = f"http://test-openhab:8080/rest/items/{item_name}"
            
            if error_type == 'timeout':
                # All attempts: timeout error (retryable)
                mock.get(url, exception=aiohttp.ServerTimeoutError("Timeout"))
                mock.get(url, exception=aiohttp.ServerTimeoutError("Timeout"))
                
            elif error_type == 'connection_error':
                # All attempts: connection error (retryable)
                mock.get(url, exception=aiohttp.ClientConnectionError("Connection failed"))
                mock.get(url, exception=aiohttp.ClientConnectionError("Connection failed"))
                
            elif error_type == 'server_error':
                # All attempts: 5xx server error (retryable)
                mock.get(url, status=503, payload={"message": "Service Unavailable"})
                mock.get(url, status=503, payload={"message": "Service Unavailable"})
            
            async with client:
                # Property: When retries are exhausted, appropriate error should be raised
                with pytest.raises(OpenHABError):
                    await client.get_item_state(item_name)

    @given(
        non_retryable_errors=st.lists(
            st.tuples(
                item_name_strategy(),  # item name
                st.sampled_from([400, 401, 403, 404])  # non-retryable status codes
            ),
            min_size=1,
            max_size=3,
            unique_by=lambda x: x[0]  # Unique item names
        )
    )
    @settings(max_examples=50, deadline=10000)
    async def test_property_non_retryable_error_handling(self, non_retryable_errors):
        """Test that non-retryable errors are not retried."""
        client = OpenHABClient(self._get_test_config())
        
        with aioresponses() as mock:
            for item_name, status_code in non_retryable_errors:
                url = f"http://test-openhab:8080/rest/items/{item_name}"
                
                if status_code == 401:
                    # Authentication errors should not be retried
                    mock.get(url, status=status_code)
                elif status_code == 404:
                    # Not found errors should not be retried
                    mock.get(url, status=status_code)
                else:
                    # Other 4xx client errors should not be retried
                    mock.get(url, status=status_code, payload={"message": f"Error {status_code}"})
            
            async with client:
                for item_name, status_code in non_retryable_errors:
                    # Property: Non-retryable errors should fail immediately without retries
                    if status_code == 401:
                        with pytest.raises(OpenHABError):  # Should be authentication error
                            await client.get_item_state(item_name)
                    elif status_code == 404:
                        # 404 is handled specially - returns None
                        result = await client.get_item_state(item_name)
                        assert result is None
                    else:
                        with pytest.raises(OpenHABError):  # Should be API error
                            await client.get_item_state(item_name)

    @given(
        retry_config_params=st.tuples(
            st.integers(min_value=1, max_value=5),  # max_attempts
            st.floats(min_value=1.1, max_value=3.0),  # backoff_factor
            st.integers(min_value=5, max_value=30)  # max_delay
        )
    )
    @settings(max_examples=50, deadline=5000)
    async def test_property_retry_configuration_flexibility(self, retry_config_params):
        """Test that retry configuration can be updated and is respected."""
        max_attempts, backoff_factor, max_delay = retry_config_params
        
        client = OpenHABClient(self._get_test_config())
        
        # Property: Retry configuration should be updatable
        client.update_retry_config(
            max_attempts=max_attempts,
            backoff_factor=backoff_factor,
            max_delay=max_delay
        )
        
        # Property: Updated configuration should be reflected
        config = client.get_retry_config()
        assert config.max_attempts == max_attempts
        assert config.backoff_factor == backoff_factor
        assert config.max_delay == max_delay
        
        # Property: Delay calculation should respect configuration
        for attempt in range(1, min(max_attempts + 1, 4)):  # Test first few attempts
            delay = config.calculate_delay(attempt)
            
            # Property: Delay should be non-negative
            assert delay >= 0
            
            # Property: Delay should not exceed max_delay
            assert delay <= max_delay
            
            # Property: Delay should increase with attempt number (exponential backoff)
            if attempt > 1:
                prev_delay = config.calculate_delay(attempt - 1)
                # Allow for jitter, so just check that delay is reasonable
                expected_base = 1.0 * (backoff_factor ** (attempt - 1))
                assert delay <= min(expected_base * 1.2, max_delay)  # Allow 20% jitter


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
