"""
Structured logging system for openHAB MCP server.

This module provides comprehensive logging with appropriate severity levels,
request/response timing, success rate tracking, and structured log formatting.
"""

import json
import logging
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(Enum):
    """Log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """Log categories for structured logging."""
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    AUTHENTICATION = "authentication"
    SECURITY = "security"
    SYSTEM = "system"
    TOOL_EXECUTION = "tool_execution"
    RESOURCE_ACCESS = "resource_access"
    ERROR = "error"
    PERFORMANCE = "performance"
    HEALTH = "health"


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: str
    level: str
    category: str
    message: str
    component: str
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    duration_ms: Optional[float] = None
    status_code: Optional[int] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    success: Optional[bool] = None
    error_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class RequestMetrics:
    """Tracks request metrics for success rate monitoring."""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_duration_ms = 0.0
        self.request_times = []
        self.error_counts = {}
        self.endpoint_stats = {}
    
    def record_request(
        self,
        endpoint: str,
        duration_ms: float,
        success: bool,
        error_type: Optional[str] = None
    ) -> None:
        """Record a request for metrics tracking."""
        self.total_requests += 1
        self.total_duration_ms += duration_ms
        self.request_times.append(duration_ms)
        
        # Keep only last 100 request times for rolling average
        if len(self.request_times) > 100:
            self.request_times.pop(0)
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error_type:
                self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Track per-endpoint stats
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = {
                'total': 0, 'success': 0, 'failed': 0, 'avg_duration_ms': 0.0
            }
        
        stats = self.endpoint_stats[endpoint]
        stats['total'] += 1
        if success:
            stats['success'] += 1
        else:
            stats['failed'] += 1
        
        # Update rolling average duration
        stats['avg_duration_ms'] = (
            (stats['avg_duration_ms'] * (stats['total'] - 1) + duration_ms) / stats['total']
        )
    
    def get_success_rate(self) -> float:
        """Get overall success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_average_response_time(self) -> float:
        """Get average response time in milliseconds."""
        if not self.request_times:
            return 0.0
        return sum(self.request_times) / len(self.request_times)
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate_percent': round(self.get_success_rate(), 2),
            'average_response_time_ms': round(self.get_average_response_time(), 2),
            'error_counts': self.error_counts.copy(),
            'endpoint_stats': self.endpoint_stats.copy()
        }


class StructuredLogger:
    """Structured logger with metrics tracking."""
    
    def __init__(self, component: str, logger_name: Optional[str] = None):
        """Initialize structured logger.
        
        Args:
            component: Component name for log entries
            logger_name: Logger name (defaults to component)
        """
        self.component = component
        self.logger = logging.getLogger(logger_name or component)
        self.metrics = RequestMetrics()
        self._request_counter = 0
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        self._request_counter += 1
        return f"{self.component}-{int(time.time())}-{self._request_counter}"
    
    def _create_log_entry(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        **kwargs
    ) -> LogEntry:
        """Create structured log entry."""
        return LogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=level.value,
            category=category.value,
            message=message,
            component=self.component,
            **kwargs
        )
    
    def _log_entry(self, entry: LogEntry) -> None:
        """Log structured entry."""
        log_data = entry.to_dict()
        
        # Format message with structured data
        if entry.metadata or entry.duration_ms or entry.status_code:
            extra_info = []
            if entry.duration_ms:
                extra_info.append(f"duration={entry.duration_ms:.2f}ms")
            if entry.status_code:
                extra_info.append(f"status={entry.status_code}")
            if entry.endpoint:
                extra_info.append(f"endpoint={entry.endpoint}")
            
            formatted_message = entry.message
            if extra_info:
                formatted_message += f" [{', '.join(extra_info)}]"
        else:
            formatted_message = entry.message
        
        # Log with appropriate level
        log_level = getattr(logging, entry.level)
        self.logger.log(log_level, formatted_message, extra={'structured_data': log_data})
    
    def debug(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs) -> None:
        """Log debug message."""
        entry = self._create_log_entry(LogLevel.DEBUG, category, message, **kwargs)
        self._log_entry(entry)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs) -> None:
        """Log info message."""
        entry = self._create_log_entry(LogLevel.INFO, category, message, **kwargs)
        self._log_entry(entry)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs) -> None:
        """Log warning message."""
        entry = self._create_log_entry(LogLevel.WARNING, category, message, **kwargs)
        self._log_entry(entry)
    
    def error(self, message: str, category: LogCategory = LogCategory.ERROR, **kwargs) -> None:
        """Log error message."""
        entry = self._create_log_entry(LogLevel.ERROR, category, message, **kwargs)
        self._log_entry(entry)
    
    def critical(self, message: str, category: LogCategory = LogCategory.ERROR, **kwargs) -> None:
        """Log critical message."""
        entry = self._create_log_entry(LogLevel.CRITICAL, category, message, **kwargs)
        self._log_entry(entry)
    
    @contextmanager
    def request_context(
        self,
        endpoint: str,
        method: str = "GET",
        request_id: Optional[str] = None
    ):
        """Context manager for request logging with timing.
        
        Args:
            endpoint: API endpoint being accessed
            method: HTTP method
            request_id: Optional request ID (generated if not provided)
            
        Yields:
            Request context with logging methods
        """
        req_id = request_id or self._generate_request_id()
        start_time = time.time()
        success = False
        status_code = None
        error_type = None
        
        # Log request start
        self.info(
            f"Starting {method} request",
            category=LogCategory.API_REQUEST,
            request_id=req_id,
            endpoint=endpoint,
            method=method
        )
        
        class RequestContext:
            def __init__(self, logger_instance):
                self.logger = logger_instance
                self.request_id = req_id
                self.endpoint = endpoint
                self.method = method
            
            def log_success(self, status: int, message: str = "Request completed successfully"):
                nonlocal success, status_code
                success = True
                status_code = status
                self.logger.info(
                    message,
                    category=LogCategory.API_RESPONSE,
                    request_id=req_id,
                    endpoint=endpoint,
                    method=method,
                    status_code=status,
                    success=True
                )
            
            def log_error(self, status: int, error_msg: str, err_type: str = "api_error"):
                nonlocal success, status_code, error_type
                success = False
                status_code = status
                error_type = err_type
                self.logger.error(
                    f"Request failed: {error_msg}",
                    category=LogCategory.API_RESPONSE,
                    request_id=req_id,
                    endpoint=endpoint,
                    method=method,
                    status_code=status,
                    success=False,
                    error_type=err_type
                )
        
        try:
            yield RequestContext(self)
        except Exception as e:
            success = False
            error_type = type(e).__name__
            self.error(
                f"Request failed with exception: {str(e)}",
                category=LogCategory.API_RESPONSE,
                request_id=req_id,
                endpoint=endpoint,
                method=method,
                success=False,
                error_type=error_type
            )
            raise
        finally:
            # Calculate duration and log completion
            duration_ms = (time.time() - start_time) * 1000
            
            self.info(
                f"Request completed",
                category=LogCategory.PERFORMANCE,
                request_id=req_id,
                endpoint=endpoint,
                method=method,
                duration_ms=duration_ms,
                success=success,
                status_code=status_code
            )
            
            # Record metrics
            self.metrics.record_request(endpoint, duration_ms, success, error_type)
    
    def log_tool_execution(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        success: bool,
        duration_ms: float,
        result: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """Log tool execution with timing and results."""
        message = f"Tool '{tool_name}' executed"
        if not success and error:
            message += f" with error: {error}"
        
        self.info(
            message,
            category=LogCategory.TOOL_EXECUTION,
            duration_ms=duration_ms,
            success=success,
            metadata={
                'tool_name': tool_name,
                'parameters': parameters,
                'result_length': len(result) if result else 0,
                'error': error
            }
        )
    
    def log_resource_access(
        self,
        resource_uri: str,
        success: bool,
        duration_ms: float,
        content_length: Optional[int] = None,
        error: Optional[str] = None
    ) -> None:
        """Log resource access with timing and results."""
        message = f"Resource '{resource_uri}' accessed"
        if not success and error:
            message += f" with error: {error}"
        
        self.info(
            message,
            category=LogCategory.RESOURCE_ACCESS,
            duration_ms=duration_ms,
            success=success,
            metadata={
                'resource_uri': resource_uri,
                'content_length': content_length,
                'error': error
            }
        )
    
    def log_authentication_event(
        self,
        event_type: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log authentication events."""
        message = f"Authentication {event_type}: {'success' if success else 'failed'}"
        
        level = LogLevel.INFO if success else LogLevel.WARNING
        entry = self._create_log_entry(
            level,
            LogCategory.AUTHENTICATION,
            message,
            success=success,
            metadata=details or {}
        )
        self._log_entry(entry)
    
    def log_security_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: LogLevel = LogLevel.WARNING
    ) -> None:
        """Log security events."""
        message = f"Security event: {event_type}"
        
        entry = self._create_log_entry(
            severity,
            LogCategory.SECURITY,
            message,
            metadata=details
        )
        self._log_entry(entry)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        return self.metrics.get_stats_summary()


# Global logger instances
_loggers: Dict[str, StructuredLogger] = {}


def get_logger(component: str) -> StructuredLogger:
    """Get or create structured logger for component."""
    if component not in _loggers:
        _loggers[component] = StructuredLogger(component)
    return _loggers[component]


def configure_logging(
    level: str = "INFO",
    format_json: bool = False,
    include_structured_data: bool = True
) -> None:
    """Configure global logging settings.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_json: Whether to format logs as JSON
        include_structured_data: Whether to include structured data in logs
    """
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    if format_json:
        formatter = JsonFormatter(include_structured_data)
    else:
        formatter = StructuredFormatter(include_structured_data)
    
    # Configure root logger
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler with formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def __init__(self, include_structured_data: bool = True):
        super().__init__()
        self.include_structured_data = include_structured_data
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured data."""
        # Basic format
        formatted = f"{record.levelname} [{record.name}] {record.getMessage()}"
        
        # Add structured data if available
        if self.include_structured_data and hasattr(record, 'structured_data'):
            structured_data = record.structured_data
            if structured_data.get('request_id'):
                formatted = f"[{structured_data['request_id']}] {formatted}"
            
            # Add timing info if available
            if structured_data.get('duration_ms'):
                formatted += f" (took {structured_data['duration_ms']:.2f}ms)"
        
        return formatted


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def __init__(self, include_structured_data: bool = True):
        super().__init__()
        self.include_structured_data = include_structured_data
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage()
        }
        
        # Add structured data if available
        if self.include_structured_data and hasattr(record, 'structured_data'):
            log_data.update(record.structured_data)
        
        return json.dumps(log_data, default=str)