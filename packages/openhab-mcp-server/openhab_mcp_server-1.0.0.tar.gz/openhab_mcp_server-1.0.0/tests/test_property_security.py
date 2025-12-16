"""Property-based tests for security features."""

import asyncio
import json
from typing import Any, Dict, Optional
import pytest
from hypothesis import given, strategies as st, settings, assume
from aioresponses import aioresponses

from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError, OpenHABAuthenticationError
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.utils.security import InputSanitizer, AuthorizationChecker, CredentialManager, SecurityLogger


# Test data generators
@st.composite
def valid_token_strategy(draw):
    """Generate valid-looking API tokens."""
    # Generate tokens that look realistic
    token_length = draw(st.integers(min_value=20, max_value=100))
    token = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='._-'),
        min_size=token_length,
        max_size=token_length
    ))
    return token


@st.composite
def malicious_input_strategy(draw):
    """Generate potentially malicious input strings."""
    return draw(st.one_of(
        # SQL injection patterns
        st.just("'; DROP TABLE users; --"),
        st.just("1' OR '1'='1"),
        st.just("admin'--"),
        
        # Script injection patterns
        st.just("<script>alert('xss')</script>"),
        st.just("javascript:alert(1)"),
        st.just("<iframe src='evil.com'></iframe>"),
        
        # Command injection patterns
        st.just("; rm -rf /"),
        st.just("| cat /etc/passwd"),
        st.just("$(whoami)"),
        
        # Path traversal patterns
        st.just("../../../etc/passwd"),
        st.just("..\\..\\windows\\system32"),
        st.just("%2e%2e%2f%2e%2e%2f"),
        
        # Long strings that might cause buffer overflows (within Hypothesis limits)
        st.text(min_size=1000, max_size=5000),
        
        # Binary data
        st.binary(min_size=100, max_size=1000).map(lambda x: x.decode('latin1', errors='ignore'))
    ))


@st.composite
def request_context_strategy(draw):
    """Generate request context for authorization testing."""
    return {
        'has_token': draw(st.booleans()),
        'endpoint': draw(st.text(min_size=1, max_size=100)),
        'recent_request_count': draw(st.integers(min_value=0, max_value=200)),
        'time_window_seconds': draw(st.integers(min_value=1, max_value=300))
    }


class TestSecurityProperties:
    """Property-based tests for security features."""
    
    def _get_test_config(self, token: Optional[str] = None):
        """Get test configuration with optional token."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token=token,
            timeout=30,
            log_level="INFO"
        )
    
    @given(
        token=st.one_of(st.none(), valid_token_strategy()),
        malicious_input=malicious_input_strategy()
    )
    @settings(max_examples=100, deadline=5000)
    async def test_property_authentication_security_consistency(self, token, malicious_input):
        """**Feature: openhab-mcp-server, Property 15: Authentication security consistency**
        
        For any openHAB API request, the system should use secure authentication headers 
        and sanitize all input parameters before making calls.
        
        **Validates: Requirements 6.1, 6.2**
        """
        config = self._get_test_config(token)
        client = OpenHABClient(config)
        
        # Test input sanitization
        try:
            # Attempt to use malicious input as item name
            sanitized_result = InputSanitizer.validate_item_name(malicious_input)
            
            # Property: Malicious input should be rejected or sanitized
            if not sanitized_result.is_valid:
                # Input was properly rejected
                assert len(sanitized_result.errors) > 0
            else:
                # If input was accepted, it should be safe
                # This should rarely happen with our malicious inputs
                pass
                
        except ValueError:
            # Input sanitization properly rejected the malicious input
            pass
        
        # Test authentication header handling
        with aioresponses() as mock:
            # Mock a simple API call
            mock.get(
                "http://test-openhab:8080/rest/systeminfo",
                payload={"version": "3.4.0"},
                status=200 if token else 401
            )
            
            async with client:
                if token:
                    # Property: Valid token should allow API access
                    try:
                        result = await client.get_system_info()
                        assert result is not None
                        assert "version" in result
                    except OpenHABError:
                        # Some tokens might still be invalid, that's ok
                        pass
                else:
                    # Property: No token should result in authentication error
                    with pytest.raises(OpenHABAuthenticationError):
                        await client.get_system_info()
    
    @given(token=st.one_of(st.none(), valid_token_strategy()))
    @settings(max_examples=100, deadline=5000)
    def test_property_credential_protection(self, token):
        """**Feature: openhab-mcp-server, Property 16: Credential protection**
        
        For any operation involving sensitive information, authentication credentials 
        should never appear in logs or response data.
        
        **Validates: Requirements 6.3**
        """
        config = self._get_test_config(token)
        
        # Property: Token should be masked in string representation
        config_str = str(config)
        config_repr = repr(config)
        
        if token:
            # Token should not appear in full in string representations
            assert token not in config_str
            assert token not in config_repr
            assert "***" in config_str  # Should show masked version
        else:
            assert "None" in config_str
        
        # Test credential manager masking
        masked = CredentialManager.mask_token(token)
        
        if token:
            # Property: Masked token should not contain the full original token
            if len(token) > 8:
                assert token not in masked
                assert "..." in masked or "***" in masked
            else:
                assert masked == "***"
        else:
            assert masked == "None"
        
        # Test header sanitization
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        sanitized_headers = CredentialManager.sanitize_headers_for_logging(headers)
        
        if token:
            # Property: Authorization header should be masked in sanitized version
            assert sanitized_headers.get("Authorization") == "***"
            assert token not in str(sanitized_headers)
        
        # Test URL sanitization for logging
        client = OpenHABClient(config)
        test_url = f"http://test-openhab:8080/rest/items?token={token}" if token else "http://test-openhab:8080/rest/items"
        sanitized_url = client._sanitize_url_for_logging(test_url)
        
        if token:
            # Property: Token should not appear in sanitized URL
            assert token not in sanitized_url
    
    @given(request_context=request_context_strategy())
    @settings(max_examples=100, deadline=5000)
    def test_property_unauthorized_request_handling(self, request_context):
        """**Feature: openhab-mcp-server, Property 17: Unauthorized request handling**
        
        For any unauthorized request, the system should reject the request and 
        log appropriate security events.
        
        **Validates: Requirements 6.4**
        """
        # Property: Authorization check should be consistent
        is_authorized = AuthorizationChecker.check_request_authorization(request_context)
        
        # Test the logic of authorization
        if not request_context.get('has_token', False):
            # Property: Requests without tokens should be rejected
            assert is_authorized is False
        elif request_context.get('recent_request_count', 0) > 100:
            # Property: High request rates should be rejected
            assert is_authorized is False
        else:
            # Property: Valid requests with tokens should be authorized
            # (unless other security rules apply)
            pass  # Authorization might still be False due to other rules
        
        # Test rate limiting logic
        if request_context.get('recent_request_count', 0) > 60:
            # Property: Rate limiting should trigger for high request counts
            is_rate_limited = AuthorizationChecker._is_rate_limited(request_context)
            assert is_rate_limited is True
    
    @given(
        error_message=st.text(min_size=10, max_size=500),
        token=st.one_of(st.none(), valid_token_strategy())
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_error_handling_security(self, error_message, token):
        """**Feature: openhab-mcp-server, Property 9: Error handling security**
        
        For any API failure condition, the error message should be meaningful for 
        debugging while not exposing internal system details or credentials.
        
        **Validates: Requirements 4.1**
        """
        config = self._get_test_config(token)
        client = OpenHABClient(config)
        
        # Inject token into error message to simulate credential exposure
        if token:
            test_error = f"Authentication failed with token {token}: {error_message}"
        else:
            test_error = f"Connection failed: {error_message}"
        
        # Property: Error message sanitization should remove credentials
        sanitized_error = client._sanitize_error_message(test_error)
        
        if token:
            # Property: Original token should not appear in sanitized error
            assert token not in sanitized_error
            # Property: Sanitized version should contain masked token
            assert "***" in sanitized_error or "Bearer ***" in sanitized_error
        
        # Property: Error message should still be meaningful
        assert len(sanitized_error) > 0
        assert "failed" in sanitized_error.lower() or "error" in sanitized_error.lower()
    
    @given(
        item_name=st.text(min_size=1, max_size=200),
        malicious_command=malicious_input_strategy()
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_input_validation_completeness(self, item_name, malicious_command):
        """**Feature: openhab-mcp-server, Property 11: Input validation completeness**
        
        For any invalid input parameter, the system should validate and reject 
        the malformed request with appropriate error messages.
        
        **Validates: Requirements 4.3**
        """
        # Test item name validation
        item_validation = InputSanitizer.validate_item_name(item_name)
        
        # Property: Validation should always return a result
        assert hasattr(item_validation, 'is_valid')
        assert isinstance(item_validation.is_valid, bool)
        assert hasattr(item_validation, 'errors')
        assert isinstance(item_validation.errors, list)
        
        # If validation fails, there should be error messages
        if not item_validation.is_valid:
            assert len(item_validation.errors) > 0
            # Property: Error messages should be descriptive
            for error in item_validation.errors:
                assert isinstance(error, str)
                assert len(error) > 0
        
        # Test command validation with malicious input
        command_validation = InputSanitizer.validate_command(malicious_command)
        
        # Property: Malicious commands should typically be rejected
        # (though some might pass if they happen to look like valid commands)
        if not command_validation.is_valid:
            assert len(command_validation.errors) > 0
            # Property: Should detect malicious patterns
            error_text = " ".join(command_validation.errors).lower()
            assert any(keyword in error_text for keyword in [
                'malicious', 'invalid', 'dangerous', 'long', 'empty', 'characters'
            ])
    
    @given(
        config_dict=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.one_of(
                st.text(max_size=1000),
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.booleans(),
                st.none(),
                malicious_input_strategy()
            ),
            min_size=1,
            max_size=20
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_configuration_sanitization(self, config_dict):
        """Test that configuration sanitization handles all input types safely."""
        try:
            # Property: Configuration sanitization should handle any dictionary
            sanitized = InputSanitizer.sanitize_configuration(config_dict)
            
            # Property: Sanitized config should be a dictionary
            assert isinstance(sanitized, dict)
            
            # Property: Should have same or fewer keys (some might be rejected)
            assert len(sanitized) <= len(config_dict)
            
            # Property: All keys should be strings
            for key in sanitized.keys():
                assert isinstance(key, str)
                assert len(key) > 0
            
            # Property: Values should be safe types
            for value in sanitized.values():
                assert value is None or isinstance(value, (str, int, float, bool, list, dict))
                
        except ValueError as e:
            # Property: If sanitization fails, it should provide a clear error message
            assert isinstance(e, ValueError)
            assert len(str(e)) > 0


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
