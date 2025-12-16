"""Unit tests for security features."""

import pytest
from unittest.mock import patch, MagicMock

from openhab_mcp_server.utils.security import (
    InputSanitizer, AuthorizationChecker, CredentialManager, SecurityLogger
)
from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABAuthenticationError
from openhab_mcp_server.utils.config import Config


class TestInputSanitizer:
    """Unit tests for input sanitization."""
    
    def test_sanitize_string_basic(self):
        """Test basic string sanitization."""
        # Valid input should pass through
        result = InputSanitizer.sanitize_string("valid_input")
        assert result == "valid_input"
        
        # Malicious HTML should be rejected
        with pytest.raises(ValueError, match="malicious"):
            InputSanitizer.sanitize_string("<script>alert('xss')</script>")
    
    def test_sanitize_string_malicious_patterns(self):
        """Test that malicious patterns are detected."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "; rm -rf /",
            "../../../etc/passwd"
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(ValueError, match="malicious"):
                InputSanitizer.sanitize_string(malicious_input)
    
    def test_sanitize_string_length_limit(self):
        """Test length limit enforcement."""
        long_string = "a" * 1000
        
        with pytest.raises(ValueError, match="too long"):
            InputSanitizer.sanitize_string(long_string, max_length=100)
    
    def test_validate_item_name_valid(self):
        """Test valid item name validation."""
        valid_names = ["TestItem", "item_123", "sensor-1", "MyDevice"]
        
        for name in valid_names:
            result = InputSanitizer.validate_item_name(name)
            assert result.is_valid, f"'{name}' should be valid"
    
    def test_validate_item_name_invalid(self):
        """Test invalid item name validation."""
        invalid_names = [
            "",  # Empty
            " ",  # Whitespace only
            "item with spaces",  # Contains spaces
            "123item",  # Starts with number
            "item@home",  # Invalid character
            "<script>alert('xss')</script>",  # Malicious
        ]
        
        for name in invalid_names:
            result = InputSanitizer.validate_item_name(name)
            assert not result.is_valid, f"'{name}' should be invalid"
            assert len(result.errors) > 0
    
    def test_validate_thing_uid_valid(self):
        """Test valid thing UID validation."""
        valid_uids = [
            "binding:type:id",
            "zwave:device:controller_node002",
            "mqtt:topic:sensor_1"
        ]
        
        for uid in valid_uids:
            result = InputSanitizer.validate_thing_uid(uid)
            assert result.is_valid, f"'{uid}' should be valid"
    
    def test_validate_thing_uid_invalid(self):
        """Test invalid thing UID validation."""
        invalid_uids = [
            "",  # Empty
            "invalid",  # No colons
            "binding:",  # Empty part
            ":type:id",  # Empty binding
            "binding:type:",  # Empty id
            "binding@type:id",  # Invalid character
        ]
        
        for uid in invalid_uids:
            result = InputSanitizer.validate_thing_uid(uid)
            assert not result.is_valid, f"'{uid}' should be invalid"
    
    def test_validate_command_valid(self):
        """Test valid command validation."""
        valid_commands = [
            "ON", "OFF", "TOGGLE",
            "50", "75.5", "100%",
            "255,128,64",  # HSB color
            '"string value"',  # Quoted string
        ]
        
        for command in valid_commands:
            result = InputSanitizer.validate_command(command)
            assert result.is_valid, f"'{command}' should be valid"
    
    def test_validate_command_invalid(self):
        """Test invalid command validation."""
        invalid_commands = [
            "",  # Empty
            " ",  # Whitespace only
            "; rm -rf /",  # Command injection
            "<script>alert('xss')</script>",  # Script injection
        ]
        
        for command in invalid_commands:
            result = InputSanitizer.validate_command(command)
            assert not result.is_valid, f"'{command}' should be invalid"
    
    def test_sanitize_configuration_valid(self):
        """Test valid configuration sanitization."""
        config = {
            "host": "192.168.1.100",
            "port": 8080,
            "enabled": True,
            "timeout": 30.5,
            "tags": ["sensor", "temperature"],
            "metadata": {"type": "device"}
        }
        
        result = InputSanitizer.sanitize_configuration(config)
        assert isinstance(result, dict)
        assert result["host"] == "192.168.1.100"
        assert result["port"] == 8080
        assert result["enabled"] is True
    
    def test_sanitize_configuration_invalid(self):
        """Test invalid configuration handling."""
        # Non-dict input
        with pytest.raises(ValueError, match="dictionary"):
            InputSanitizer.sanitize_configuration("not a dict")
        
        # Invalid key type
        with pytest.raises(ValueError, match="key must be string"):
            InputSanitizer.sanitize_configuration({123: "value"})
        
        # Malicious key
        with pytest.raises(ValueError, match="contains invalid characters"):
            InputSanitizer.sanitize_configuration({"<script>": "value"})


class TestCredentialManager:
    """Unit tests for credential management."""
    
    def test_mask_token_none(self):
        """Test masking None token."""
        result = CredentialManager.mask_token(None)
        assert result == "None"
    
    def test_mask_token_short(self):
        """Test masking short token."""
        result = CredentialManager.mask_token("short")
        assert result == "***"
    
    def test_mask_token_long(self):
        """Test masking long token."""
        token = "abcdefghijklmnopqrstuvwxyz123456"
        result = CredentialManager.mask_token(token)
        assert result == "abcd...3456"
        assert token not in result
    
    def test_validate_token_format_valid(self):
        """Test valid token format validation."""
        valid_tokens = [
            "abcdefghij1234567890",
            "token.with.dots",
            "token-with-hyphens",
            "token_with_underscores"
        ]
        
        for token in valid_tokens:
            assert CredentialManager.validate_token_format(token)
    
    def test_validate_token_format_invalid(self):
        """Test invalid token format validation."""
        invalid_tokens = [
            None,
            "",
            "short",  # Too short
            "token with spaces",  # Contains spaces
            "token@with#special!chars",  # Invalid characters
        ]
        
        for token in invalid_tokens:
            assert not CredentialManager.validate_token_format(token)
    
    def test_sanitize_headers_for_logging(self):
        """Test header sanitization for logging."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer secret-token-123",
            "X-API-Key": "api-key-456",
            "User-Agent": "openHAB-MCP/1.0"
        }
        
        result = CredentialManager.sanitize_headers_for_logging(headers)
        
        assert result["Content-Type"] == "application/json"
        assert result["Authorization"] == "***"
        assert result["X-API-Key"] == "***"
        assert result["User-Agent"] == "openHAB-MCP/1.0"
        
        # Ensure original token is not in sanitized version
        assert "secret-token-123" not in str(result)
        assert "api-key-456" not in str(result)


class TestAuthorizationChecker:
    """Unit tests for authorization checking."""
    
    def test_check_request_authorization_no_token(self):
        """Test authorization check without token."""
        context = {
            'has_token': False,
            'endpoint': 'items',
            'recent_request_count': 5,
            'time_window_seconds': 60
        }
        
        result = AuthorizationChecker.check_request_authorization(context)
        assert result is False
    
    def test_check_request_authorization_with_token(self):
        """Test authorization check with valid token."""
        context = {
            'has_token': True,
            'endpoint': 'items',
            'recent_request_count': 5,
            'time_window_seconds': 60
        }
        
        result = AuthorizationChecker.check_request_authorization(context)
        assert result is True
    
    def test_check_request_authorization_rate_limited(self):
        """Test authorization check with rate limiting."""
        context = {
            'has_token': True,
            'endpoint': 'items',
            'recent_request_count': 150,  # Exceeds limit
            'time_window_seconds': 60
        }
        
        result = AuthorizationChecker.check_request_authorization(context)
        assert result is False
    
    def test_is_rate_limited(self):
        """Test rate limiting logic."""
        # Within limits
        context = {'recent_request_count': 30, 'time_window_seconds': 60}
        assert not AuthorizationChecker._is_rate_limited(context)
        
        # Exceeds limits
        context = {'recent_request_count': 100, 'time_window_seconds': 60}
        assert AuthorizationChecker._is_rate_limited(context)
    
    def test_validate_request_source_normal(self):
        """Test normal request source validation."""
        request_info = {'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        result = AuthorizationChecker.validate_request_source(request_info)
        assert result is True
    
    def test_validate_request_source_suspicious(self):
        """Test suspicious request source validation."""
        suspicious_agents = [
            'sqlmap/1.0',
            'nikto scanner',
            'nmap probe',
            'security scanner'
        ]
        
        for agent in suspicious_agents:
            request_info = {'user_agent': agent}
            result = AuthorizationChecker.validate_request_source(request_info)
            assert result is False


class TestSecurityLogger:
    """Unit tests for security logging."""
    
    @patch('openhab_mcp_server.utils.security.logger')
    def test_log_validation_failure(self, mock_logger):
        """Test validation failure logging."""
        SecurityLogger.log_validation_failure(
            "item_name", 
            "malicious_input_here", 
            ["Invalid characters", "Too long"]
        )
        
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        assert "Input validation failed" in call_args
        assert "item_name" in call_args
        assert "Invalid characters" in call_args
    
    @patch('openhab_mcp_server.utils.security.logger')
    def test_log_unauthorized_request(self, mock_logger):
        """Test unauthorized request logging."""
        SecurityLogger.log_unauthorized_request(
            "api_access",
            "No valid token",
            {"endpoint": "/items"}
        )
        
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        assert "Unauthorized request blocked" in call_args
        assert "api_access" in call_args
        assert "No valid token" in call_args
    
    @patch('openhab_mcp_server.utils.security.logger')
    def test_log_authentication_failure(self, mock_logger):
        """Test authentication failure logging."""
        SecurityLogger.log_authentication_failure(
            "invalid_token",
            {"token_length": 10}
        )
        
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        assert "Authentication failure" in call_args
        assert "invalid_token" in call_args
    
    @patch('openhab_mcp_server.utils.security.logger')
    def test_log_suspicious_activity(self, mock_logger):
        """Test suspicious activity logging."""
        SecurityLogger.log_suspicious_activity(
            "high_request_rate",
            "Unusual number of requests detected",
            {"count": 200, "timeframe": "1 minute"}
        )
        
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        assert "Suspicious activity detected" in call_args
        assert "high_request_rate" in call_args
        assert "Unusual number of requests" in call_args


class TestOpenHABClientSecurity:
    """Unit tests for openHAB client security features."""
    
    def test_config_token_masking(self):
        """Test that config masks tokens in string representation."""
        config = Config(
            openhab_url="http://localhost:8080",
            openhab_token="secret-token-12345",
            timeout=30,
            log_level="INFO"
        )
        
        config_str = str(config)
        config_repr = repr(config)
        
        # Token should not appear in full
        assert "secret-token-12345" not in config_str
        assert "secret-token-12345" not in config_repr
        
        # Should show masked version
        assert "***" in config_str
    
    def test_client_url_sanitization(self):
        """Test URL sanitization for logging."""
        config = Config(
            openhab_url="http://localhost:8080",
            openhab_token="secret-token-12345",
            timeout=30,
            log_level="INFO"
        )
        
        client = OpenHABClient(config)
        
        # Test URL with token parameter
        test_url = "http://localhost:8080/rest/items?token=secret-token-12345"
        sanitized = client._sanitize_url_for_logging(test_url)
        
        # Token should be masked (check for URL encoded version too)
        assert "secret-token-12345" not in sanitized
        assert ("***" in sanitized or "%2A%2A%2A" in sanitized)
    
    def test_client_error_message_sanitization(self):
        """Test error message sanitization."""
        config = Config(
            openhab_url="http://localhost:8080",
            openhab_token="secret-token-12345",
            timeout=30,
            log_level="INFO"
        )
        
        client = OpenHABClient(config)
        
        # Test error message with token
        error_msg = "Authentication failed with token secret-token-12345: Invalid credentials"
        sanitized = client._sanitize_error_message(error_msg)
        
        # Token should be masked
        assert "secret-token-12345" not in sanitized
        assert "***" in sanitized
        assert "Authentication failed" in sanitized
    
    def test_client_authorization_check(self):
        """Test client authorization checking."""
        config = Config(
            openhab_url="http://localhost:8080",
            openhab_token="secret-token-12345",
            timeout=30,
            log_level="INFO"
        )
        
        client = OpenHABClient(config)
        
        # Should authorize normal requests
        assert client._check_request_authorization("items")
        
        # Should authorize sensitive endpoints with token
        assert client._check_request_authorization("systeminfo")
    
    def test_client_authorization_check_no_token(self):
        """Test client authorization checking without token."""
        config = Config(
            openhab_url="http://localhost:8080",
            openhab_token=None,
            timeout=30,
            log_level="INFO"
        )
        
        client = OpenHABClient(config)
        
        # Should reject sensitive endpoints without token
        assert not client._check_request_authorization("systeminfo")
        assert not client._check_request_authorization("bindings")


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
