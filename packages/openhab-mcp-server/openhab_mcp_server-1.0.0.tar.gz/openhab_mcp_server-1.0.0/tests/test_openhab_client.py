"""Unit tests for openHAB client."""

import pytest
from aioresponses import aioresponses
import aiohttp

from openhab_mcp_server.utils.openhab_client import (
    OpenHABClient,
    OpenHABError,
    OpenHABConnectionError,
    OpenHABAuthenticationError,
    OpenHABAPIError,
)
from openhab_mcp_server.utils.config import Config


class TestOpenHABClient:
    """Unit tests for openHAB client."""
    
    @pytest.fixture
    def config(self):
        """Test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.fixture
    def client(self, config):
        """Test client instance."""
        return OpenHABClient(config)
    
    # Test successful API calls with mocked responses
    
    async def test_get_item_state_success(self, client):
        """Test successful item state retrieval."""
        item_data = {
            "name": "TestItem",
            "state": "ON",
            "type": "Switch",
            "label": "Test Switch",
            "category": "switch",
            "tags": ["test"]
        }
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items/TestItem",
                payload=item_data,
                status=200
            )
            
            async with client:
                result = await client.get_item_state("TestItem")
            
            assert result == item_data
    
    async def test_send_item_command_success(self, client):
        """Test successful item command sending."""
        with aioresponses() as mock:
            mock.post(
                "http://test-openhab:8080/rest/items/TestItem",
                status=204
            )
            
            async with client:
                result = await client.send_item_command("TestItem", "ON")
            
            assert result is True
    
    async def test_update_item_state_success(self, client):
        """Test successful item state update."""
        with aioresponses() as mock:
            mock.put(
                "http://test-openhab:8080/rest/items/TestItem/state",
                status=204
            )
            
            async with client:
                result = await client.update_item_state("TestItem", "ON")
            
            assert result is True
    
    async def test_get_items_success(self, client):
        """Test successful items list retrieval."""
        items_data = [
            {"name": "Item1", "state": "ON", "type": "Switch"},
            {"name": "Item2", "state": "50", "type": "Dimmer"}
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items",
                payload=items_data,
                status=200
            )
            
            async with client:
                result = await client.get_items()
            
            assert result == items_data
    
    async def test_get_things_success(self, client):
        """Test successful things list retrieval."""
        things_data = [
            {"UID": "thing1", "status": "ONLINE", "label": "Thing 1"},
            {"UID": "thing2", "status": "OFFLINE", "label": "Thing 2"}
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/things",
                payload=things_data,
                status=200
            )
            
            async with client:
                result = await client.get_things()
            
            assert result == things_data
    
    async def test_get_system_info_success(self, client):
        """Test successful system info retrieval."""
        system_data = {
            "version": "4.0.0",
            "buildString": "Release Build",
            "locale": "en_US",
            "measurementSystem": "SI"
        }
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/systeminfo",
                payload=system_data,
                status=200
            )
            
            async with client:
                result = await client.get_system_info()
            
            assert result == system_data
    
    # Test error handling for network failures and API errors
    
    async def test_item_not_found(self, client):
        """Test handling of non-existent item."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items/NonExistentItem",
                status=404
            )
            
            async with client:
                result = await client.get_item_state("NonExistentItem")
            
            assert result is None
    
    async def test_api_error_handling(self, client):
        """Test handling of API errors."""
        with aioresponses() as mock:
            # Mock multiple responses for retry attempts
            for _ in range(4):  # Initial + 3 retries
                mock.get(
                    "http://test-openhab:8080/rest/items/TestItem",
                    status=500,
                    payload={"message": "Internal Server Error"}
                )
            
            async with client:
                with pytest.raises(OpenHABAPIError) as exc_info:
                    await client.get_item_state("TestItem")
                
                assert exc_info.value.status_code == 500
    
    async def test_command_failure_handling(self, client):
        """Test handling of command failures."""
        with aioresponses() as mock:
            mock.post(
                "http://test-openhab:8080/rest/items/TestItem",
                status=400,
                payload={"message": "Bad Request"}
            )
            
            async with client:
                result = await client.send_item_command("TestItem", "INVALID")
            
            assert result is False
    
    async def test_network_error_handling(self, client):
        """Test handling of network connection errors."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items/TestItem",
                exception=aiohttp.ClientError("Connection refused")
            )
            
            async with client:
                with pytest.raises(OpenHABConnectionError):
                    await client.get_item_state("TestItem")
    
    # Test authentication header inclusion
    
    async def test_authentication_header_included(self, client):
        """Test that authentication header is included in requests."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items/TestItem",
                payload={"name": "TestItem", "state": "ON"},
                status=200
            )
            
            async with client:
                result = await client.get_item_state("TestItem")
            
            # Verify the result to ensure the request was successful
            assert result["name"] == "TestItem"
            assert result["state"] == "ON"
            
            # The authentication token is stored securely and added to headers during requests
            auth_headers = client._get_auth_headers()
            assert auth_headers.get('Authorization') == 'Bearer test-token'
    
    async def test_authentication_error_handling(self, client):
        """Test handling of authentication errors."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items/TestItem",
                status=401
            )
            
            async with client:
                with pytest.raises(OpenHABAuthenticationError) as exc_info:
                    await client.get_item_state("TestItem")
                
                assert "Authentication failed" in str(exc_info.value)
    
    async def test_client_without_token(self):
        """Test client behavior without authentication token."""
        config = Config(
            openhab_url="http://test-openhab:8080",
            openhab_token=None,  # No token
            timeout=30,
            log_level="INFO"
        )
        client = OpenHABClient(config)
        
        async with client:
            # Without a token, requests should be rejected by security checks
            with pytest.raises(OpenHABAuthenticationError) as exc_info:
                await client.get_item_state("TestItem")
            
            assert "Request not authorized" in str(exc_info.value)
            
            # Check that no Authorization header is set in the auth headers
            auth_headers = client._get_auth_headers()
            assert 'Authorization' not in auth_headers
    
    # Test context manager behavior
    
    async def test_context_manager_usage(self, client):
        """Test proper context manager usage."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/systeminfo",
                payload={"version": "4.0.0"},
                status=200
            )
            
            async with client as ctx_client:
                result = await ctx_client.get_system_info()
                assert result["version"] == "4.0.0"
        
        # Session should be closed after context exit
        assert client._session is None or client._session.closed
    
    async def test_manual_session_management(self, client):
        """Test manual session management."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/systeminfo",
                payload={"version": "4.0.0"},
                status=200
            )
            
            await client._ensure_session()
            result = await client.get_system_info()
            await client.close()
            
            assert result["version"] == "4.0.0"
            assert client._session is None or client._session.closed
    
    # Test specific openHAB operations
    
    async def test_thing_operations(self, client):
        """Test thing-related operations."""
        thing_data = {
            "UID": "test:thing:1",
            "status": "ONLINE",
            "statusDetail": "NONE",
            "label": "Test Thing",
            "configuration": {"param1": "value1"}
        }
        
        with aioresponses() as mock:
            # Test get thing status
            mock.get(
                "http://test-openhab:8080/rest/things/test:thing:1",
                payload=thing_data,
                status=200
            )
            
            # Test update thing config
            mock.put(
                "http://test-openhab:8080/rest/things/test:thing:1/config",
                status=204
            )
            
            async with client:
                # Test get thing status
                result = await client.get_thing_status("test:thing:1")
                assert result == thing_data
                
                # Test update thing config
                success = await client.update_thing_config(
                    "test:thing:1", 
                    {"param1": "new_value"}
                )
                assert success is True
    
    async def test_rule_operations(self, client):
        """Test rule-related operations."""
        rules_data = [
            {"uid": "rule1", "name": "Test Rule 1", "status": "IDLE"},
            {"uid": "rule2", "name": "Test Rule 2", "status": "RUNNING"}
        ]
        
        rule_data = {
            "uid": "rule1",
            "name": "Test Rule 1",
            "description": "A test rule",
            "status": "IDLE"
        }
        
        with aioresponses() as mock:
            # Test get rules
            mock.get(
                "http://test-openhab:8080/rest/rules",
                payload=rules_data,
                status=200
            )
            
            # Test get specific rule
            mock.get(
                "http://test-openhab:8080/rest/rules/rule1",
                payload=rule_data,
                status=200
            )
            
            # Test execute rule
            mock.post(
                "http://test-openhab:8080/rest/rules/rule1/runnow",
                status=204
            )
            
            # Test create rule
            mock.post(
                "http://test-openhab:8080/rest/rules",
                payload={"uid": "new_rule"},
                status=201
            )
            
            async with client:
                # Test get rules
                rules = await client.get_rules()
                assert rules == rules_data
                
                # Test get specific rule
                rule = await client.get_rule("rule1")
                assert rule == rule_data
                
                # Test execute rule
                success = await client.execute_rule("rule1")
                assert success is True
                
                # Test create rule
                rule_def = {
                    "name": "New Rule",
                    "triggers": [],
                    "actions": []
                }
                uid = await client.create_rule(rule_def)
                assert uid == "new_rule"
    
    # Test concurrent request handling and resource management
    
    async def test_multiple_simultaneous_requests(self, client):
        """Test multiple simultaneous requests."""
        import asyncio
        
        # Mock responses for multiple items
        items_data = [
            {"name": f"Item{i}", "state": "ON", "type": "Switch"} 
            for i in range(5)
        ]
        
        with aioresponses() as mock:
            for i, item_data in enumerate(items_data):
                mock.get(
                    f"http://test-openhab:8080/rest/items/Item{i}",
                    payload=item_data,
                    status=200
                )
            
            async with client:
                # Create multiple concurrent requests
                tasks = [
                    client.get_item_state(f"Item{i}")
                    for i in range(5)
                ]
                
                # Execute all requests concurrently
                results = await asyncio.gather(*tasks)
                
                # Verify all requests completed successfully
                assert len(results) == 5
                for i, result in enumerate(results):
                    assert result["name"] == f"Item{i}"
                    assert result["state"] == "ON"
                    assert result["type"] == "Switch"
    
    async def test_batch_item_state_retrieval(self, client):
        """Test batch retrieval of multiple item states."""
        item_names = ["Item1", "Item2", "Item3"]
        items_data = [
            {"name": "Item1", "state": "ON", "type": "Switch"},
            {"name": "Item2", "state": "50", "type": "Dimmer"},
            {"name": "Item3", "state": "CLOSED", "type": "Contact"}
        ]
        
        with aioresponses() as mock:
            for item_data in items_data:
                mock.get(
                    f"http://test-openhab:8080/rest/items/{item_data['name']}",
                    payload=item_data,
                    status=200
                )
            
            async with client:
                results = await client.get_multiple_item_states(item_names)
                
                # Verify all items were retrieved
                assert len(results) == 3
                for item_name in item_names:
                    assert item_name in results
                    assert results[item_name] is not None
                    assert results[item_name]["name"] == item_name
    
    async def test_batch_command_sending(self, client):
        """Test batch sending of commands to multiple items."""
        commands = [
            ("Item1", "ON"),
            ("Item2", "75"),
            ("Item3", "OFF")
        ]
        
        with aioresponses() as mock:
            for item_name, command in commands:
                mock.post(
                    f"http://test-openhab:8080/rest/items/{item_name}",
                    status=204
                )
            
            async with client:
                results = await client.send_multiple_commands(commands)
                
                # Verify all commands were sent successfully
                assert len(results) == 3
                for item_name, _ in commands:
                    assert item_name in results
                    assert results[item_name] is True
    
    async def test_batch_thing_status_retrieval(self, client):
        """Test batch retrieval of multiple thing statuses."""
        thing_uids = ["thing1", "thing2", "thing3"]
        things_data = [
            {"UID": "thing1", "status": "ONLINE", "label": "Thing 1"},
            {"UID": "thing2", "status": "OFFLINE", "label": "Thing 2"},
            {"UID": "thing3", "status": "ONLINE", "label": "Thing 3"}
        ]
        
        with aioresponses() as mock:
            for thing_data in things_data:
                mock.get(
                    f"http://test-openhab:8080/rest/things/{thing_data['UID']}",
                    payload=thing_data,
                    status=200
                )
            
            async with client:
                results = await client.get_multiple_thing_statuses(thing_uids)
                
                # Verify all things were retrieved
                assert len(results) == 3
                for thing_uid in thing_uids:
                    assert thing_uid in results
                    assert results[thing_uid] is not None
                    assert results[thing_uid]["UID"] == thing_uid
    
    async def test_concurrent_requests_with_controlled_limit(self, client):
        """Test concurrent request execution with controlled concurrency limit."""
        # Create a large number of requests to test concurrency control
        num_requests = 15
        requests = []
        
        for i in range(num_requests):
            requests.append({
                'method': 'GET',
                'endpoint': f'items/Item{i}',
                'data': None,
                'params': None
            })
        
        with aioresponses() as mock:
            for i in range(num_requests):
                mock.get(
                    f"http://test-openhab:8080/rest/items/Item{i}",
                    payload={"name": f"Item{i}", "state": "ON", "type": "Switch"},
                    status=200
                )
            
            async with client:
                # Execute with controlled concurrency (max 5 concurrent)
                results = await client.execute_concurrent_requests(requests, max_concurrent=5)
                
                # Verify all requests completed
                assert len(results) == num_requests
                
                # Verify no exceptions occurred
                for result in results:
                    assert not isinstance(result, Exception)
                    assert result["state"] == "ON"
    
    async def test_connection_pool_management(self, client):
        """Test connection pool and resource management."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/systeminfo",
                payload={"version": "4.0.0"},
                status=200
            )
            
            async with client:
                # Verify connection pool is initialized
                assert client._connection_pool is not None
                
                # Make a request to ensure session is created
                result = await client.get_system_info()
                assert result["version"] == "4.0.0"
                
                # Check that active request count is tracked
                active_count = await client.get_concurrent_request_count()
                assert active_count >= 0
        
        # After context exit, resources should be cleaned up
        assert client._session is None or client._session.closed
    
    async def test_request_queue_processing(self, client):
        """Test request queue and batch processing."""
        import asyncio
        
        with aioresponses() as mock:
            # Mock multiple item requests
            for i in range(3):
                mock.get(
                    f"http://test-openhab:8080/rest/items/Item{i}",
                    payload={"name": f"Item{i}", "state": "ON", "type": "Switch"},
                    status=200
                )
            
            async with client:
                # Queue multiple requests (non-priority)
                tasks = []
                for i in range(3):
                    task = asyncio.create_task(
                        client.queue_request('GET', f'items/Item{i}')
                    )
                    tasks.append(task)
                
                # Wait for all queued requests to complete
                results = await asyncio.gather(*tasks)
                
                # Verify all requests completed successfully
                assert len(results) == 3
                for i, result in enumerate(results):
                    assert result["name"] == f"Item{i}"
                    assert result["state"] == "ON"
    
    async def test_priority_request_handling(self, client):
        """Test priority request handling bypasses queue."""
        with aioresponses() as mock:
            mock.post(
                "http://test-openhab:8080/rest/items/TestItem",
                status=204
            )
            
            async with client:
                # Priority request (POST) should bypass queue
                result = await client.queue_request(
                    'POST', 
                    'items/TestItem', 
                    data="ON",
                    priority=True
                )
                
                # For POST requests that return 204, we expect an empty dict
                assert result == {}
    
    async def test_resource_cleanup_on_error(self, client):
        """Test proper resource cleanup when errors occur."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/items/TestItem",
                exception=aiohttp.ClientError("Connection error")
            )
            
            async with client:
                # Verify that connection errors are handled properly
                with pytest.raises(OpenHABConnectionError):
                    await client.get_item_state("TestItem")
                
                # Connection pool should still be functional
                active_count = await client.get_concurrent_request_count()
                assert active_count >= 0
    
    # Test timeout scenarios with retry logic
    
    async def test_timeout_retry_exhaustion(self, client):
        """Test timeout scenarios where all retries are exhausted."""
        # Configure client for faster testing
        client.update_retry_config(max_attempts=1, backoff_factor=1.1, max_delay=1)
        
        with aioresponses() as mock:
            # Single request that times out (no retries with max_attempts=1)
            mock.get(
                "http://test-openhab:8080/rest/items/TestItem",
                exception=aiohttp.ServerTimeoutError("Timeout")
            )
            
            async with client:
                # Should raise connection error after exhausting retries
                with pytest.raises(OpenHABConnectionError) as exc_info:
                    await client.get_item_state("TestItem")
                
                assert "timeout" in str(exc_info.value).lower()
    
    async def test_connection_error_exhaustion(self, client):
        """Test connection error scenarios where retries are exhausted."""
        # Configure client for faster testing
        client.update_retry_config(max_attempts=1, backoff_factor=1.1, max_delay=1)
        
        with aioresponses() as mock:
            # Single request that fails with connection error
            mock.get(
                "http://test-openhab:8080/rest/items/TestItem",
                exception=aiohttp.ClientConnectionError("Connection failed")
            )
            
            async with client:
                # Should raise connection error after exhausting retries
                with pytest.raises(OpenHABConnectionError) as exc_info:
                    await client.get_item_state("TestItem")
                
                assert "connection failed" in str(exc_info.value).lower()
    
    async def test_server_error_exhaustion(self, client):
        """Test server error (5xx) scenarios where retries are exhausted."""
        # Configure client for faster testing
        client.update_retry_config(max_attempts=1, backoff_factor=1.1, max_delay=1)
        
        with aioresponses() as mock:
            # Single request that returns 503
            mock.get(
                "http://test-openhab:8080/rest/items/TestItem",
                status=503,
                payload={"message": "Service Unavailable"}
            )
            
            async with client:
                # Should raise API error after exhausting retries
                with pytest.raises(OpenHABAPIError) as exc_info:
                    await client.get_item_state("TestItem")
                
                assert exc_info.value.status_code == 503
                assert "service unavailable" in str(exc_info.value).lower()
    
    async def test_non_retryable_errors_no_retry(self, client):
        """Test that non-retryable errors are not retried."""
        # Configure client for faster testing
        client.update_retry_config(max_attempts=3, backoff_factor=1.1, max_delay=1)
        
        with aioresponses() as mock:
            # 400 Bad Request should not be retried
            mock.get(
                "http://test-openhab:8080/rest/items/TestItem",
                status=400,
                payload={"message": "Bad Request"}
            )
            
            async with client:
                # Should fail immediately without retries
                with pytest.raises(OpenHABAPIError) as exc_info:
                    await client.get_item_state("TestItem")
                
                assert exc_info.value.status_code == 400
                assert "Bad Request" in str(exc_info.value)
    
    async def test_exponential_backoff_implementation(self, client):
        """Test exponential backoff implementation."""
        retry_config = client.get_retry_config()
        
        # Test delay calculation for different attempts
        delay_0 = retry_config.calculate_delay(0)
        delay_1 = retry_config.calculate_delay(1)
        delay_2 = retry_config.calculate_delay(2)
        delay_3 = retry_config.calculate_delay(3)
        
        # First attempt should have no delay
        assert delay_0 == 0
        
        # Subsequent delays should increase (allowing for jitter)
        assert delay_1 > 0
        assert delay_2 > delay_1 * 0.8  # Allow for jitter
        assert delay_3 > delay_2 * 0.8  # Allow for jitter
        
        # All delays should be within max_delay
        assert delay_1 <= retry_config.max_delay
        assert delay_2 <= retry_config.max_delay
        assert delay_3 <= retry_config.max_delay
    
    async def test_retry_config_update(self, client):
        """Test retry configuration updates."""
        # Get initial config
        initial_config = client.get_retry_config()
        initial_attempts = initial_config.max_attempts
        initial_backoff = initial_config.backoff_factor
        initial_max_delay = initial_config.max_delay
        
        # Update configuration
        new_attempts = initial_attempts + 2
        new_backoff = initial_backoff + 0.5
        new_max_delay = initial_max_delay + 10
        
        client.update_retry_config(
            max_attempts=new_attempts,
            backoff_factor=new_backoff,
            max_delay=new_max_delay
        )
        
        # Verify updates
        updated_config = client.get_retry_config()
        assert updated_config.max_attempts == new_attempts
        assert updated_config.backoff_factor == new_backoff
        assert updated_config.max_delay == new_max_delay
        
        # Test partial updates
        client.update_retry_config(max_attempts=1)
        partial_config = client.get_retry_config()
        assert partial_config.max_attempts == 1
        assert partial_config.backoff_factor == new_backoff  # Should remain unchanged
        assert partial_config.max_delay == new_max_delay  # Should remain unchanged
    
    async def test_timeout_error_classification(self):
        """Test timeout error classification for retry logic."""
        from openhab_mcp_server.utils.openhab_client import is_retryable_error
        import aiohttp
        import asyncio
        
        # Test retryable timeout errors
        assert is_retryable_error(aiohttp.ServerTimeoutError("Timeout")) == True
        assert is_retryable_error(asyncio.TimeoutError()) == True
        assert is_retryable_error(aiohttp.ClientConnectionError("Connection failed")) == True
        assert is_retryable_error(aiohttp.ClientConnectorError(None, OSError("Connection refused"))) == True
        
        # Test retryable server errors
        from openhab_mcp_server.utils.openhab_client import OpenHABAPIError
        assert is_retryable_error(OpenHABAPIError("Server Error", 500)) == True
        assert is_retryable_error(OpenHABAPIError("Bad Gateway", 502)) == True
        assert is_retryable_error(OpenHABAPIError("Service Unavailable", 503)) == True
        assert is_retryable_error(OpenHABAPIError("Gateway Timeout", 504)) == True
        assert is_retryable_error(OpenHABAPIError("Too Many Requests", 429)) == True
        
        # Test non-retryable errors
        from openhab_mcp_server.utils.openhab_client import OpenHABAuthenticationError
        assert is_retryable_error(OpenHABAuthenticationError("Auth failed")) == False
        assert is_retryable_error(OpenHABAPIError("Bad Request", 400)) == False
        assert is_retryable_error(OpenHABAPIError("Unauthorized", 401)) == False
        assert is_retryable_error(OpenHABAPIError("Forbidden", 403)) == False
        assert is_retryable_error(OpenHABAPIError("Not Found", 404)) == False
        
        # Test unknown errors (should not be retryable by default)
        assert is_retryable_error(ValueError("Some error")) == False
        assert is_retryable_error(RuntimeError("Runtime error")) == False
    
    async def test_concurrent_mixed_operations(self, client):
        """Test concurrent execution of mixed read/write operations."""
        import asyncio
        
        with aioresponses() as mock:
            # Mock GET requests
            for i in range(3):
                mock.get(
                    f"http://test-openhab:8080/rest/items/Item{i}",
                    payload={"name": f"Item{i}", "state": "ON", "type": "Switch"},
                    status=200
                )
            
            # Mock POST requests
            for i in range(3):
                mock.post(
                    f"http://test-openhab:8080/rest/items/Item{i}",
                    status=204
                )
            
            async with client:
                # Create mixed concurrent operations
                tasks = []
                
                # Add GET requests
                for i in range(3):
                    tasks.append(client.get_item_state(f"Item{i}"))
                
                # Add POST requests
                for i in range(3):
                    tasks.append(client.send_item_command(f"Item{i}", "OFF"))
                
                # Execute all operations concurrently
                results = await asyncio.gather(*tasks)
                
                # Verify results
                assert len(results) == 6
                
                # First 3 should be GET results (dict objects)
                for i in range(3):
                    assert isinstance(results[i], dict)
                    assert results[i]["name"] == f"Item{i}"
                
                # Last 3 should be POST results (boolean True)
                for i in range(3, 6):
                    assert results[i] is True


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
