"""Unit tests for MCP server initialization and functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from openhab_mcp_server.server import OpenHABMCPServer
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.utils.openhab_client import OpenHABError, OpenHABConnectionError


class TestOpenHABMCPServer:
    """Unit tests for openHAB MCP server."""
    
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
    def server(self, config):
        """Test server instance."""
        return OpenHABMCPServer(config)
    
    # Test server startup and shutdown procedures
    
    async def test_server_initialization_success(self, server):
        """Test successful server initialization."""
        with patch('openhab_mcp_server.server.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock successful system info response
            mock_client.get_system_info.return_value = {
                "version": "4.0.0",
                "buildString": "Release Build"
            }
            
            # Mock context manager methods
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            # Test server start
            await server.start()
            
            # Verify server state after initialization
            assert server.openhab_client is not None
            assert server.server is not None
            
            # Verify connection test was called
            mock_client.get_system_info.assert_called_once()
            
            # Test server shutdown
            await server.shutdown()
            
            # Verify cleanup
            assert server.openhab_client is None
    
    async def test_server_initialization_connection_failure(self, server):
        """Test server initialization with connection failure."""
        with patch('openhab_mcp_server.server.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock connection failure
            mock_client.get_system_info.side_effect = OpenHABConnectionError("Connection failed")
            
            # Mock context manager methods
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            # Test that start raises exception on connection failure
            with pytest.raises(OpenHABConnectionError):
                await server.start()
    
    async def test_server_initialization_with_custom_config(self):
        """Test server initialization with custom configuration."""
        custom_config = Config(
            openhab_url="http://custom-openhab:9090",
            openhab_token="custom-token",
            timeout=60,
            log_level="DEBUG"
        )
        
        server = OpenHABMCPServer(custom_config)
        
        with patch('openhab_mcp_server.server.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock successful system info response
            mock_client.get_system_info.return_value = {
                "version": "4.0.0",
                "buildString": "Release Build"
            }
            
            # Mock context manager methods
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            await server.start()
            
            # Verify custom config was used
            assert server.config.openhab_url == "http://custom-openhab:9090"
            assert server.config.openhab_token == "custom-token"
            assert server.config.timeout == 60
            assert server.config.log_level == "DEBUG"
            
            await server.shutdown()
    
    async def test_server_shutdown_without_start(self, server):
        """Test server shutdown without prior start."""
        # Should not raise exception
        await server.shutdown()
        assert server.openhab_client is None
    
    async def test_server_shutdown_error_handling(self, server):
        """Test server shutdown with client close error."""
        with patch('openhab_mcp_server.server.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock successful system info response
            mock_client.get_system_info.return_value = {
                "version": "4.0.0",
                "buildString": "Release Build"
            }
            
            # Mock context manager methods
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            # Mock close method to raise exception
            mock_client.close.side_effect = Exception("Close error")
            
            await server.start()
            
            # Shutdown should handle the exception
            with pytest.raises(Exception, match="Close error"):
                await server.shutdown()
    
    # Test tool and resource registration
    
    async def test_tool_registration_success(self, server):
        """Test successful tool registration."""
        with patch('openhab_mcp_server.server.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock successful system info response
            mock_client.get_system_info.return_value = {
                "version": "4.0.0",
                "buildString": "Release Build"
            }
            
            # Mock context manager methods
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            await server.start()
            
            # Verify that tools were registered (no exceptions during start)
            # The actual tool registration happens during start()
            assert server.server is not None
            
            await server.shutdown()
    
    async def test_resource_registration_success(self, server):
        """Test successful resource registration."""
        with patch('openhab_mcp_server.server.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock successful system info response
            mock_client.get_system_info.return_value = {
                "version": "4.0.0",
                "buildString": "Release Build"
            }
            
            # Mock context manager methods
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            await server.start()
            
            # Verify that resources were registered (no exceptions during start)
            # The actual resource registration happens during start()
            assert server.server is not None
            
            await server.shutdown()
    
    async def test_connection_test_success(self, server):
        """Test successful connection test during initialization."""
        with patch('openhab_mcp_server.server.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock successful system info response with specific version
            expected_system_info = {
                "version": "4.1.0",
                "buildString": "Snapshot Build #2024",
                "locale": "en_US"
            }
            mock_client.get_system_info.return_value = expected_system_info
            
            # Mock context manager methods
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            await server.start()
            
            # Verify connection test was performed
            mock_client.get_system_info.assert_called_once()
            
            await server.shutdown()
    
    async def test_connection_test_failure(self, server):
        """Test connection test failure during initialization."""
        with patch('openhab_mcp_server.server.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock connection test failure
            mock_client.get_system_info.side_effect = OpenHABError("API Error")
            
            # Mock context manager methods
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            # Should raise the OpenHABError
            with pytest.raises(OpenHABError, match="API Error"):
                await server.start()
    
    # Test server configuration and state
    
    def test_server_config_initialization(self):
        """Test server configuration initialization."""
        config = Config(
            openhab_url="http://test:8080",
            openhab_token="test_token_123456",
            timeout=45,
            log_level="WARNING"
        )
        
        server = OpenHABMCPServer(config)
        
        assert server.config == config
        assert server.config.openhab_url == "http://test:8080"
        assert server.config.openhab_token == "test_token_123456"
        assert server.config.timeout == 45
        assert server.config.log_level == "WARNING"
    
    def test_server_default_config_initialization(self):
        """Test server initialization with default config."""
        with patch('openhab_mcp_server.server.get_config') as mock_get_config:
            mock_config = Config(
                openhab_url="http://localhost:8080",
                openhab_token=None,
                timeout=30,
                log_level="INFO"
            )
            mock_get_config.return_value = mock_config
            
            server = OpenHABMCPServer()
            
            assert server.config == mock_config
            mock_get_config.assert_called_once()
    
    def test_server_initial_state(self, server):
        """Test server initial state before start."""
        assert server.openhab_client is None
        assert server.server is not None  # MCP server is created in __init__
        assert server.config is not None
    
    # Test error scenarios
    
    async def test_start_with_invalid_config(self):
        """Test server start with invalid configuration."""
        # Create config with invalid timeout (this should be caught by validation)
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            invalid_config = Config(
                openhab_url="http://localhost:8080",
                openhab_token="token",
                timeout=-1,  # Invalid negative timeout
                log_level="INFO"
            )
    
    async def test_multiple_start_calls(self, server):
        """Test multiple start calls on the same server."""
        with patch('openhab_mcp_server.server.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock successful system info response
            mock_client.get_system_info.return_value = {
                "version": "4.0.0",
                "buildString": "Release Build"
            }
            
            # Mock context manager methods
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            # First start should succeed
            await server.start()
            assert server.openhab_client is not None
            
            # Second start should also work (or handle gracefully)
            await server.start()
            assert server.openhab_client is not None
            
            await server.shutdown()
    
    async def test_multiple_shutdown_calls(self, server):
        """Test multiple shutdown calls on the same server."""
        with patch('openhab_mcp_server.server.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock successful system info response
            mock_client.get_system_info.return_value = {
                "version": "4.0.0",
                "buildString": "Release Build"
            }
            
            # Mock context manager methods
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            
            await server.start()
            
            # First shutdown
            await server.shutdown()
            assert server.openhab_client is None
            
            # Second shutdown should not raise exception
            await server.shutdown()
            assert server.openhab_client is None


# Async test runner for manual testing
async def run_async_tests():
    """Run async tests manually."""
    test_instance = TestOpenHABMCPServer()
    
    # Create test fixtures
    config = Config(
        openhab_url="http://test-openhab:8080",
        openhab_token="test-token",
        timeout=30,
        log_level="INFO"
    )
    server = OpenHABMCPServer(config)
    
    # Run tests
    await test_instance.test_server_initialization_success(server)
    print("✓ Server initialization test passed")
    
    await test_instance.test_server_shutdown_without_start(server)
    print("✓ Server shutdown test passed")


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
