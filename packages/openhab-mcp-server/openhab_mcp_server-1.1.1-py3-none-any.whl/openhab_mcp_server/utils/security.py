"""
Security utilities for input validation and sanitization.

This module provides comprehensive input validation and sanitization functions
to prevent injection attacks and ensure data integrity before making API calls.
"""

import re
import html
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote, unquote

from openhab_mcp_server.models import ValidationResult


logger = logging.getLogger(__name__)


class InputSanitizer:
    """Comprehensive input sanitization and validation."""
    
    # Patterns for detecting potentially malicious input
    INJECTION_PATTERNS = [
        # SQL injection patterns
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
        r'(--|#|/\*|\*/)',
        r'(\bOR\b.*=.*\bOR\b)',
        r'(\bAND\b.*=.*\bAND\b)',
        
        # Script injection patterns
        r'(<script[^>]*>.*?</script>)',
        r'(javascript:)',
        r'(on\w+\s*=)',
        r'(<iframe[^>]*>)',
        r'(<object[^>]*>)',
        r'(<embed[^>]*>)',
        
        # Command injection patterns
        r'([;&|`$(){}[\]\\])',
        r'(\.\./)',
        r'(/etc/passwd)',
        r'(/bin/)',
        r'(cmd\.exe)',
        r'(powershell)',
        
        # Path traversal patterns
        r'(\.\.[\\/])',
        r'([\\/]\.\.)',
        r'(%2e%2e)',
        r'(%252e%252e)',
    ]
    
    # Compiled regex patterns for performance
    _compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in INJECTION_PATTERNS]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: Optional[int] = None) -> str:
        """Sanitize a string input by removing potentially dangerous content.
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            ValueError: If input contains malicious patterns
        """
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        # Check for injection patterns
        for pattern in cls._compiled_patterns:
            if pattern.search(value):
                logger.warning(f"Potentially malicious input detected: {value[:50]}...")
                raise ValueError("Input contains potentially malicious content")
        
        # Basic sanitization
        sanitized = value.strip()
        
        # HTML encode to prevent XSS
        sanitized = html.escape(sanitized)
        
        # URL decode to normalize input
        try:
            sanitized = unquote(sanitized)
        except Exception:
            # If URL decoding fails, keep original
            pass
        
        # Enforce length limits
        if max_length and len(sanitized) > max_length:
            raise ValueError(f"Input too long (max {max_length} characters)")
        
        return sanitized
    
    @classmethod
    def validate_item_name(cls, item_name: str) -> ValidationResult:
        """Validate openHAB item name with security checks.
        
        Args:
            item_name: Item name to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        if not item_name or not item_name.strip():
            result.add_error("Item name cannot be empty")
            return result
        
        try:
            sanitized = cls.sanitize_string(item_name, max_length=100)
        except ValueError as e:
            result.add_error(str(e))
            return result
        
        # openHAB item name specific validation
        if ' ' in sanitized:
            result.add_error("Item name cannot contain spaces")
        
        # Only allow alphanumeric, underscore, and hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', sanitized):
            result.add_error("Item name can only contain letters, numbers, underscores, and hyphens")
        
        # Must start with letter
        if not sanitized[0].isalpha():
            result.add_error("Item name must start with a letter")
        
        return result
    
    @classmethod
    def validate_thing_uid(cls, thing_uid: str) -> ValidationResult:
        """Validate openHAB thing UID with security checks.
        
        Args:
            thing_uid: Thing UID to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        if not thing_uid or not thing_uid.strip():
            result.add_error("Thing UID cannot be empty")
            return result
        
        try:
            sanitized = cls.sanitize_string(thing_uid, max_length=200)
        except ValueError as e:
            result.add_error(str(e))
            return result
        
        # openHAB thing UID format: binding:type:id
        parts = sanitized.split(':')
        if len(parts) < 2:
            result.add_error("Thing UID must contain at least binding and type separated by ':'")
            return result
        
        # Validate each part
        for i, part in enumerate(parts):
            if not part.strip():
                result.add_error(f"Thing UID part {i+1} cannot be empty")
            elif not re.match(r'^[a-zA-Z0-9_-]+$', part):
                result.add_error(f"Thing UID part {i+1} can only contain letters, numbers, underscores, and hyphens")
        
        return result
    
    @classmethod
    def validate_rule_uid(cls, rule_uid: str) -> ValidationResult:
        """Validate openHAB rule UID with security checks.
        
        Args:
            rule_uid: Rule UID to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        if not rule_uid or not rule_uid.strip():
            result.add_error("Rule UID cannot be empty")
            return result
        
        try:
            sanitized = cls.sanitize_string(rule_uid, max_length=200)
        except ValueError as e:
            result.add_error(str(e))
            return result
        
        # Rule UID validation
        if ' ' in sanitized:
            result.add_error("Rule UID cannot contain spaces")
        
        # Allow alphanumeric, underscore, hyphen, and dot
        if not re.match(r'^[a-zA-Z0-9._-]+$', sanitized):
            result.add_error("Rule UID can only contain letters, numbers, underscores, hyphens, and dots")
        
        return result
    
    @classmethod
    def validate_command(cls, command: str) -> ValidationResult:
        """Validate openHAB item command with security checks.
        
        Args:
            command: Command to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        if not command or not command.strip():
            result.add_error("Command cannot be empty")
            return result
        
        try:
            sanitized = cls.sanitize_string(command, max_length=1000)
        except ValueError as e:
            result.add_error(str(e))
            return result
        
        # Basic command validation - allow common openHAB commands
        valid_simple_commands = {
            'ON', 'OFF', 'TOGGLE', 'UP', 'DOWN', 'STOP', 'MOVE', 'INCREASE', 'DECREASE',
            'PLAY', 'PAUSE', 'NEXT', 'PREVIOUS', 'REWIND', 'FASTFORWARD'
        }
        
        # Check if it's a simple command
        if sanitized.upper() in valid_simple_commands:
            return result
        
        # Check if it's a numeric value (for dimmer, number items)
        try:
            float(sanitized)
            return result
        except ValueError:
            pass
        
        # Check if it's a percentage
        if re.match(r'^\d+(\.\d+)?%$', sanitized):
            return result
        
        # Check if it's a color value (HSB format)
        if re.match(r'^\d+,\d+,\d+$', sanitized):
            return result
        
        # Check if it's a string value (quoted)
        if sanitized.startswith('"') and sanitized.endswith('"'):
            return result
        
        # If none of the above, it might be a complex command - be more restrictive
        if len(sanitized) > 100:
            result.add_error("Complex commands must be less than 100 characters")
        
        return result
    
    @classmethod
    def sanitize_configuration(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize configuration dictionary.
        
        Args:
            config: Configuration dictionary to sanitize
            
        Returns:
            Sanitized configuration dictionary
            
        Raises:
            ValueError: If configuration contains malicious content
        """
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        sanitized_config = {}
        
        for key, value in config.items():
            # Sanitize key
            if not isinstance(key, str):
                raise ValueError(f"Configuration key must be string: {key}")
            
            try:
                sanitized_key = cls.sanitize_string(key, max_length=100)
            except ValueError as e:
                raise ValueError(f"Invalid configuration key '{key}': {e}")
            
            # Validate key format
            if not re.match(r'^[a-zA-Z0-9._-]+$', sanitized_key):
                raise ValueError(f"Configuration key '{key}' contains invalid characters")
            
            # Sanitize value based on type
            if isinstance(value, str):
                try:
                    sanitized_value = cls.sanitize_string(value, max_length=1000)
                except ValueError as e:
                    raise ValueError(f"Invalid configuration value for '{key}': {e}")
            elif isinstance(value, (int, float, bool)):
                sanitized_value = value
            elif isinstance(value, list):
                # Sanitize list elements
                sanitized_value = []
                for item in value:
                    if isinstance(item, str):
                        try:
                            sanitized_item = cls.sanitize_string(item, max_length=500)
                            sanitized_value.append(sanitized_item)
                        except ValueError as e:
                            raise ValueError(f"Invalid list item in '{key}': {e}")
                    elif isinstance(item, (int, float, bool)):
                        sanitized_value.append(item)
                    else:
                        raise ValueError(f"Unsupported list item type in '{key}': {type(item)}")
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                try:
                    sanitized_value = cls.sanitize_configuration(value)
                except ValueError as e:
                    raise ValueError(f"Invalid nested configuration in '{key}': {e}")
            elif value is None:
                sanitized_value = None
            else:
                raise ValueError(f"Unsupported configuration value type for '{key}': {type(value)}")
            
            sanitized_config[sanitized_key] = sanitized_value
        
        return sanitized_config
    
    @classmethod
    def validate_binding_id(cls, binding_id: str) -> ValidationResult:
        """Validate binding ID with security checks.
        
        Args:
            binding_id: Binding ID to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        if not binding_id or not binding_id.strip():
            result.add_error("Binding ID cannot be empty")
            return result
        
        try:
            sanitized = cls.sanitize_string(binding_id, max_length=50)
        except ValueError as e:
            result.add_error(str(e))
            return result
        
        # Binding ID validation
        if not re.match(r'^[a-zA-Z0-9_-]+$', sanitized):
            result.add_error("Binding ID can only contain letters, numbers, underscores, and hyphens")
        
        # Must start with letter
        if not sanitized[0].isalpha():
            result.add_error("Binding ID must start with a letter")
        
        return result
    
    @classmethod
    def sanitize_script_code(cls, script_code: str) -> str:
        """Sanitize Python script code for safe execution.
        
        Args:
            script_code: Python script code to sanitize
            
        Returns:
            Sanitized script code
            
        Raises:
            ValueError: If script contains dangerous patterns
        """
        if not isinstance(script_code, str):
            raise ValueError("Script code must be a string")
        
        if not script_code.strip():
            raise ValueError("Script code cannot be empty")
        
        # Check for dangerous patterns specific to Python scripts
        dangerous_patterns = [
            # File system access
            r'\bopen\s*\(',
            r'\bfile\s*\(',
            r'__file__',
            r'__import__',
            
            # System access
            r'\bos\.',
            r'\bsys\.',
            r'\bsubprocess\.',
            r'\beval\s*\(',
            r'\bexec\s*\(',
            r'\bcompile\s*\(',
            
            # Network access
            r'\burllib',
            r'\brequests\.',
            r'\bsocket\.',
            r'\bhttp\.',
            
            # Dangerous builtins
            r'\bglobals\s*\(',
            r'\blocals\s*\(',
            r'\bvars\s*\(',
            r'\bdir\s*\(',
            r'\bgetattr\s*\(',
            r'\bsetattr\s*\(',
            r'\bdelattr\s*\(',
            r'\bhasattr\s*\(',
        ]
        
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if re.search(pattern, script_code, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected in script: {pattern}")
                raise ValueError(f"Script contains dangerous pattern: {pattern}")
        
        # Basic sanitization - remove null bytes and control characters
        sanitized = script_code.replace('\x00', '').replace('\r', '\n')
        
        # Limit script size
        max_script_size = 50000  # 50KB
        if len(sanitized) > max_script_size:
            raise ValueError(f"Script too large (max {max_script_size} characters)")
        
        return sanitized


class CredentialManager:
    """Secure credential management utilities."""
    
    @staticmethod
    def mask_token(token: Optional[str]) -> str:
        """Mask authentication token for logging/display.
        
        Args:
            token: Token to mask
            
        Returns:
            Masked token string
        """
        if not token:
            return "None"
        
        if len(token) <= 8:
            return "***"
        
        # Show first 4 and last 4 characters with masking in between
        return f"{token[:4]}...{token[-4:]}"
    
    @staticmethod
    def validate_token_format(token: str) -> bool:
        """Validate token format without logging the actual token.
        
        Args:
            token: Token to validate
            
        Returns:
            True if token format appears valid
        """
        if not token or not isinstance(token, str):
            return False
        
        token = token.strip()
        
        # Basic format checks
        if len(token) < 10:
            return False
        
        # Check for reasonable token characteristics
        # Most API tokens are alphanumeric with some special chars
        import re
        if not re.match(r'^[A-Za-z0-9._-]+$', token):
            return False
        
        return True
    
    @staticmethod
    def sanitize_headers_for_logging(headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize HTTP headers for safe logging.
        
        Args:
            headers: Headers dictionary to sanitize
            
        Returns:
            Sanitized headers dictionary
        """
        sanitized = {}
        
        for key, value in headers.items():
            if key.lower() in ['authorization', 'x-api-key', 'x-auth-token']:
                sanitized[key] = "***"
            else:
                sanitized[key] = value
        
        return sanitized


class AuthorizationChecker:
    """Authorization and access control utilities."""
    
    @staticmethod
    def check_request_authorization(request_context: Dict[str, Any]) -> bool:
        """Check if a request is authorized.
        
        Args:
            request_context: Context information about the request
            
        Returns:
            True if request is authorized, False otherwise
        """
        # Basic authorization checks
        
        # Check if authentication token is present
        if not request_context.get('has_token', False):
            SecurityLogger.log_unauthorized_request(
                "missing_token",
                "No authentication token provided",
                {"context": "api_request"}
            )
            return False
        
        # Check for suspicious patterns in request
        if AuthorizationChecker._has_suspicious_patterns(request_context):
            return False
        
        # Check rate limiting (basic implementation)
        if AuthorizationChecker._is_rate_limited(request_context):
            return False
        
        return True
    
    @staticmethod
    def _has_suspicious_patterns(request_context: Dict[str, Any]) -> bool:
        """Check for suspicious patterns in the request.
        
        Args:
            request_context: Request context to analyze
            
        Returns:
            True if suspicious patterns detected
        """
        # Check for rapid successive requests (basic rate limiting)
        request_count = request_context.get('recent_request_count', 0)
        if request_count > 100:  # More than 100 requests recently
            SecurityLogger.log_suspicious_activity(
                "high_request_rate",
                f"Unusually high request rate: {request_count} requests",
                {"context": request_context.get('endpoint', 'unknown')}
            )
            return True
        
        # Check for unusual request patterns
        endpoint = request_context.get('endpoint', '')
        if endpoint and any(pattern in endpoint.lower() for pattern in ['admin', 'config', 'system']):
            # Log access to sensitive endpoints
            SecurityLogger.log_security_event(
                "sensitive_endpoint_access",
                {"endpoint": endpoint, "authorized": True}
            )
        
        return False
    
    @staticmethod
    def _is_rate_limited(request_context: Dict[str, Any]) -> bool:
        """Check if request should be rate limited.
        
        Args:
            request_context: Request context to check
            
        Returns:
            True if request should be rate limited
        """
        # Simple rate limiting check
        request_count = request_context.get('recent_request_count', 0)
        time_window = request_context.get('time_window_seconds', 60)
        
        # Allow up to 60 requests per minute
        max_requests_per_minute = 60
        
        if request_count > max_requests_per_minute:
            SecurityLogger.log_unauthorized_request(
                "rate_limit_exceeded",
                f"Rate limit exceeded: {request_count} requests in {time_window} seconds",
                {"max_allowed": max_requests_per_minute}
            )
            return True
        
        return False
    
    @staticmethod
    def validate_request_source(request_info: Dict[str, Any]) -> bool:
        """Validate the source of a request.
        
        Args:
            request_info: Information about the request source
            
        Returns:
            True if request source is valid
        """
        # Basic request source validation
        user_agent = request_info.get('user_agent', '')
        
        # Check for suspicious user agents
        suspicious_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'zap', 'burp',
            'scanner', 'crawler', 'bot'
        ]
        
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            SecurityLogger.log_suspicious_activity(
                "suspicious_user_agent",
                f"Potentially malicious user agent detected",
                {"user_agent": user_agent[:100]}  # Truncate for logging
            )
            return False
        
        return True


class SecurityLogger:
    """Security event logging utilities."""
    
    @staticmethod
    def log_validation_failure(input_type: str, input_value: str, errors: List[str]) -> None:
        """Log input validation failures for security monitoring.
        
        Args:
            input_type: Type of input that failed validation
            input_value: The input value (truncated for security)
            errors: List of validation errors
        """
        # Truncate input value for logging (don't log full potentially malicious content)
        truncated_value = input_value[:50] + "..." if len(input_value) > 50 else input_value
        
        logger.warning(
            f"Input validation failed - Type: {input_type}, "
            f"Value: {truncated_value}, Errors: {', '.join(errors)}"
        )
    
    @staticmethod
    def log_sanitization_applied(input_type: str, original_length: int, sanitized_length: int) -> None:
        """Log when input sanitization is applied.
        
        Args:
            input_type: Type of input that was sanitized
            original_length: Length of original input
            sanitized_length: Length after sanitization
        """
        if original_length != sanitized_length:
            logger.info(
                f"Input sanitized - Type: {input_type}, "
                f"Original length: {original_length}, Sanitized length: {sanitized_length}"
            )
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
        """Log security events for monitoring and alerting.
        
        Args:
            event_type: Type of security event
            details: Additional event details
        """
        logger.warning(f"Security event - Type: {event_type}, Details: {details}")
    
    @staticmethod
    def log_unauthorized_request(request_type: str, reason: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log unauthorized request attempts for security monitoring.
        
        Args:
            request_type: Type of request that was unauthorized
            reason: Reason for rejection
            details: Additional details about the request
        """
        log_details = details or {}
        logger.warning(
            f"Unauthorized request blocked - Type: {request_type}, "
            f"Reason: {reason}, Details: {log_details}"
        )
    
    @staticmethod
    def log_authentication_failure(failure_type: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log authentication failures for security monitoring.
        
        Args:
            failure_type: Type of authentication failure
            details: Additional details about the failure
        """
        log_details = details or {}
        logger.warning(
            f"Authentication failure - Type: {failure_type}, Details: {log_details}"
        )
    
    @staticmethod
    def log_suspicious_activity(activity_type: str, description: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log suspicious activity for security monitoring.
        
        Args:
            activity_type: Type of suspicious activity
            description: Description of the activity
            details: Additional details
        """
        log_details = details or {}
        logger.warning(
            f"Suspicious activity detected - Type: {activity_type}, "
            f"Description: {description}, Details: {log_details}"
        )


# Decorator for automatic input validation
def validate_inputs(**validators):
    """Decorator to automatically validate function inputs.
    
    Args:
        **validators: Mapping of parameter names to validation functions
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get function signature to map args to parameter names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each parameter
            for param_name, validator_func in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if value is not None:  # Skip None values
                        try:
                            result = validator_func(value)
                            if hasattr(result, 'is_valid') and not result.is_valid:
                                SecurityLogger.log_validation_failure(
                                    param_name, str(value), result.errors
                                )
                                raise ValueError(f"Invalid {param_name}: {', '.join(result.errors)}")
                        except Exception as e:
                            SecurityLogger.log_validation_failure(
                                param_name, str(value), [str(e)]
                            )
                            raise
            
            return func(*args, **kwargs)
        return wrapper
    return decorator