"""
Unit tests for logging and diagnostics functionality.

Tests log message formatting, severity levels, metrics collection,
reporting, and diagnostic endpoint responses.
"""

import asyncio
import json
import logging
import time
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

import pytest

from openhab_mcp_server.utils.logging import (
    StructuredLogger, LogLevel, LogCategory, LogEntry, RequestMetrics,
    get_logger, configure_logging, StructuredFormatter, JsonFormatter
)
from openhab_mcp_server.utils.diagnostics import (
    HealthChecker, HealthStatus, HealthMetric, ComponentHealth, SystemHealth,
    get_health_checker
)
from openhab_mcp_server.utils.config import Config


class TestStructuredLogger:
    """Unit tests for StructuredLogger class."""
    
    def setup_method(self):
        """Setup for each test."""
        self.logger = StructuredLogger("test_component")
        self.log_capture = []
        
        # Mock the logger to capture log entries
        def capture_log(level, message, **kwargs):
            self.log_capture.append({
                'level': level,
                'message': message,
                'kwargs': kwargs
            })
        
        self.logger.logger.log = capture_log
    
    def test_basic_logging_methods(self):
        """Test that all logging methods create appropriate log entries."""
        test_message = "Test message"
        
        # Test each logging level
        self.logger.debug(test_message)
        self.logger.info(test_message)
        self.logger.warning(test_message)
        self.logger.error(test_message)
        self.logger.critical(test_message)
        
        # Verify all entries were created
        assert len(self.log_capture) == 5
        
        # Verify log levels
        expected_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        for i, expected_level in enumerate(expected_levels):
            assert self.log_capture[i]['level'] == expected_level
            assert test_message in self.log_capture[i]['message']
    
    def test_structured_data_inclusion(self):
        """Test that structured data is properly included in log entries."""
        test_message = "Test with metadata"
        test_metadata = {"key": "value", "number": 42}
        
        self.logger.info(
            test_message,
            category=LogCategory.API_REQUEST,
            request_id="test-123",
            metadata=test_metadata
        )
        
        assert len(self.log_capture) == 1
        entry = self.log_capture[0]
        
        # Check that structured data is passed through
        structured_data = entry['kwargs']['extra']['structured_data']
        assert structured_data['category'] == LogCategory.API_REQUEST.value
        assert structured_data['request_id'] == "test-123"
        assert structured_data['metadata'] == test_metadata
        assert structured_data['component'] == "test_component"
        assert 'timestamp' in structured_data
    
    def test_request_context_logging(self):
        """Test request context manager logging behavior."""
        endpoint = "test_endpoint"
        method = "GET"
        
        with self.logger.request_context(endpoint, method) as ctx:
            ctx.log_success(200, "Success message")
        
        # Should have start, success, and completion logs
        assert len(self.log_capture) >= 3
        
        # Check start log
        start_log = self.log_capture[0]
        assert "Starting GET request" in start_log['message']
        
        # Check success log
        success_logs = [log for log in self.log_capture if "Success message" in log['message']]
        assert len(success_logs) == 1
        
        # Check completion log
        completion_logs = [log for log in self.log_capture if "Request completed" in log['message']]
        assert len(completion_logs) == 1
    
    def test_request_context_error_logging(self):
        """Test request context error logging."""
        endpoint = "test_endpoint"
        method = "POST"
        
        with self.logger.request_context(endpoint, method) as ctx:
            ctx.log_error(500, "Error message", "server_error")
        
        # Should have start, error, and completion logs
        assert len(self.log_capture) >= 3
        
        # Check error log
        error_logs = [log for log in self.log_capture if "Request failed: Error message" in log['message']]
        assert len(error_logs) == 1
    
    def test_tool_execution_logging(self):
        """Test tool execution logging."""
        tool_name = "test_tool"
        parameters = {"param1": "value1"}
        duration_ms = 150.5
        result = "Tool result"
        
        self.logger.log_tool_execution(
            tool_name=tool_name,
            parameters=parameters,
            success=True,
            duration_ms=duration_ms,
            result=result
        )
        
        assert len(self.log_capture) == 1
        entry = self.log_capture[0]
        
        assert f"Tool '{tool_name}' executed" in entry['message']
        structured_data = entry['kwargs']['extra']['structured_data']
        assert structured_data['category'] == LogCategory.TOOL_EXECUTION.value
        assert structured_data['duration_ms'] == duration_ms
        assert structured_data['success'] is True
        assert structured_data['metadata']['tool_name'] == tool_name
        assert structured_data['metadata']['parameters'] == parameters
    
    def test_authentication_event_logging(self):
        """Test authentication event logging."""
        event_type = "login_attempt"
        details = {"user": "test_user", "ip": "192.168.1.1"}
        
        # Test successful authentication
        self.logger.log_authentication_event(event_type, True, details)
        
        assert len(self.log_capture) == 1
        entry = self.log_capture[0]
        
        assert entry['level'] == logging.INFO
        assert "Authentication login_attempt: success" in entry['message']
        structured_data = entry['kwargs']['extra']['structured_data']
        assert structured_data['category'] == LogCategory.AUTHENTICATION.value
        assert structured_data['success'] is True
        assert structured_data['metadata'] == details
    
    def test_security_event_logging(self):
        """Test security event logging."""
        event_type = "unauthorized_access"
        details = {"endpoint": "/admin", "ip": "192.168.1.100"}
        
        self.logger.log_security_event(event_type, details, LogLevel.WARNING)
        
        assert len(self.log_capture) == 1
        entry = self.log_capture[0]
        
        assert entry['level'] == logging.WARNING
        assert f"Security event: {event_type}" in entry['message']
        structured_data = entry['kwargs']['extra']['structured_data']
        assert structured_data['category'] == LogCategory.SECURITY.value
        assert structured_data['metadata'] == details


class TestRequestMetrics:
    """Unit tests for RequestMetrics class."""
    
    def setup_method(self):
        """Setup for each test."""
        self.metrics = RequestMetrics()
    
    def test_initial_state(self):
        """Test initial metrics state."""
        assert self.metrics.total_requests == 0
        assert self.metrics.successful_requests == 0
        assert self.metrics.failed_requests == 0
        assert self.metrics.get_success_rate() == 0.0
        assert self.metrics.get_average_response_time() == 0.0
    
    def test_record_successful_request(self):
        """Test recording successful requests."""
        endpoint = "test_endpoint"
        duration = 100.5
        
        self.metrics.record_request(endpoint, duration, True)
        
        assert self.metrics.total_requests == 1
        assert self.metrics.successful_requests == 1
        assert self.metrics.failed_requests == 0
        assert self.metrics.get_success_rate() == 100.0
        assert self.metrics.get_average_response_time() == duration
    
    def test_record_failed_request(self):
        """Test recording failed requests."""
        endpoint = "test_endpoint"
        duration = 200.0
        error_type = "timeout_error"
        
        self.metrics.record_request(endpoint, duration, False, error_type)
        
        assert self.metrics.total_requests == 1
        assert self.metrics.successful_requests == 0
        assert self.metrics.failed_requests == 1
        assert self.metrics.get_success_rate() == 0.0
        assert self.metrics.get_average_response_time() == duration
        assert self.metrics.error_counts[error_type] == 1
    
    def test_mixed_requests(self):
        """Test recording mix of successful and failed requests."""
        # Record 3 successful and 2 failed requests
        for i in range(3):
            self.metrics.record_request(f"endpoint_{i}", 100.0, True)
        
        for i in range(2):
            self.metrics.record_request(f"endpoint_{i}", 200.0, False, "error")
        
        assert self.metrics.total_requests == 5
        assert self.metrics.successful_requests == 3
        assert self.metrics.failed_requests == 2
        assert self.metrics.get_success_rate() == 60.0  # 3/5 * 100
        assert self.metrics.get_average_response_time() == 140.0  # (3*100 + 2*200) / 5
    
    def test_endpoint_statistics(self):
        """Test per-endpoint statistics tracking."""
        endpoint1 = "endpoint1"
        endpoint2 = "endpoint2"
        
        # Record requests for endpoint1
        self.metrics.record_request(endpoint1, 100.0, True)
        self.metrics.record_request(endpoint1, 200.0, False, "error")
        
        # Record requests for endpoint2
        self.metrics.record_request(endpoint2, 150.0, True)
        
        stats = self.metrics.get_stats_summary()
        endpoint_stats = stats['endpoint_stats']
        
        # Check endpoint1 stats
        assert endpoint_stats[endpoint1]['total'] == 2
        assert endpoint_stats[endpoint1]['success'] == 1
        assert endpoint_stats[endpoint1]['failed'] == 1
        assert endpoint_stats[endpoint1]['avg_duration_ms'] == 150.0  # (100 + 200) / 2
        
        # Check endpoint2 stats
        assert endpoint_stats[endpoint2]['total'] == 1
        assert endpoint_stats[endpoint2]['success'] == 1
        assert endpoint_stats[endpoint2]['failed'] == 0
        assert endpoint_stats[endpoint2]['avg_duration_ms'] == 150.0
    
    def test_rolling_average_limit(self):
        """Test that request times are limited to last 100 entries."""
        # Record 150 requests to test rolling limit
        for i in range(150):
            self.metrics.record_request("endpoint", float(i), True)
        
        # Should only keep last 100 request times
        assert len(self.metrics.request_times) == 100
        assert self.metrics.request_times[0] == 50.0  # First kept time should be request 50
        assert self.metrics.request_times[-1] == 149.0  # Last time should be request 149


class TestLogFormatters:
    """Unit tests for log formatters."""
    
    def test_structured_formatter_basic(self):
        """Test basic structured formatter functionality."""
        formatter = StructuredFormatter(include_structured_data=True)
        
        # Create a mock log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        assert "INFO [test_logger] Test message" in formatted
    
    def test_structured_formatter_with_data(self):
        """Test structured formatter with structured data."""
        formatter = StructuredFormatter(include_structured_data=True)
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add structured data
        record.structured_data = {
            'request_id': 'test-123',
            'duration_ms': 150.5
        }
        
        formatted = formatter.format(record)
        assert "[test-123]" in formatted
        assert "(took 150.50ms)" in formatted
    
    def test_json_formatter(self):
        """Test JSON formatter functionality."""
        formatter = JsonFormatter(include_structured_data=True)
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        record.structured_data = {'key': 'value'}
        
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        assert parsed['level'] == 'INFO'
        assert parsed['logger'] == 'test_logger'
        assert parsed['message'] == 'Test message'
        assert parsed['key'] == 'value'
        assert 'timestamp' in parsed


class TestHealthChecker:
    """Unit tests for HealthChecker class."""
    
    def setup_method(self):
        """Setup for each test."""
        self.config = Config(
            openhab_url="http://test:8080",
            openhab_token="test_token",
            timeout=30,
            log_level="INFO"
        )
        self.health_checker = HealthChecker(self.config)
    
    def test_initial_state(self):
        """Test initial health checker state."""
        assert self.health_checker.config == self.config
        assert self.health_checker._last_health_check is None
        assert len(self.health_checker._health_history) == 0
    
    @pytest.mark.asyncio
    async def test_openhab_health_check_success(self):
        """Test successful openHAB health check."""
        # Mock successful openHAB client
        mock_system_info = {
            'version': '4.0.0',
            'startLevel': 100
        }
        
        with patch('openhab_mcp_server.utils.diagnostics.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.__aenter__.return_value = mock_client
            mock_client.get_system_info.return_value = mock_system_info
            mock_client.get_items.return_value = [{'name': 'test_item'}]
            mock_client.get_things.return_value = [{'UID': 'test_thing'}]
            
            component_health = await self.health_checker._check_openhab_health()
            
            assert component_health.component == "openhab_server"
            assert component_health.status == HealthStatus.HEALTHY
            assert len(component_health.metrics) > 0
            
            # Check for expected metrics
            metric_names = [m.name for m in component_health.metrics]
            assert "response_time" in metric_names
            assert "version" in metric_names
            assert "start_level" in metric_names
    
    @pytest.mark.asyncio
    async def test_openhab_health_check_failure(self):
        """Test failed openHAB health check."""
        with patch('openhab_mcp_server.utils.diagnostics.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.__aenter__.side_effect = Exception("Connection failed")
            
            component_health = await self.health_checker._check_openhab_health()
            
            assert component_health.component == "openhab_server"
            assert component_health.status == HealthStatus.CRITICAL
            assert component_health.error_message == "Connection failed"
    
    @pytest.mark.asyncio
    async def test_server_health_check(self):
        """Test MCP server health check."""
        component_health = await self.health_checker._check_server_health()
        
        assert component_health.component == "mcp_server"
        assert component_health.status in [HealthStatus.HEALTHY, HealthStatus.WARNING]
        
        # Check for expected metrics
        metric_names = [m.name for m in component_health.metrics]
        assert "uptime" in metric_names
    
    @pytest.mark.asyncio
    async def test_resource_health_check(self):
        """Test system resource health check."""
        component_health = await self.health_checker._check_resource_health()
        
        assert component_health.component == "system_resources"
        assert component_health.status in [HealthStatus.HEALTHY, HealthStatus.WARNING]
        
        # Check for expected metrics
        metric_names = [m.name for m in component_health.metrics]
        assert "event_loop" in metric_names
        assert "configuration" in metric_names
    
    @pytest.mark.asyncio
    async def test_system_health_check_integration(self):
        """Test complete system health check."""
        with patch.object(self.health_checker, '_check_openhab_health') as mock_openhab, \
             patch.object(self.health_checker, '_check_server_health') as mock_server, \
             patch.object(self.health_checker, '_check_resource_health') as mock_resource:
            
            # Mock component health responses
            mock_openhab.return_value = ComponentHealth(
                component="openhab_server",
                status=HealthStatus.HEALTHY,
                metrics=[],
                last_check="2023-01-01T00:00:00Z"
            )
            
            mock_server.return_value = ComponentHealth(
                component="mcp_server",
                status=HealthStatus.HEALTHY,
                metrics=[],
                last_check="2023-01-01T00:00:00Z"
            )
            
            mock_resource.return_value = ComponentHealth(
                component="system_resources",
                status=HealthStatus.HEALTHY,
                metrics=[],
                last_check="2023-01-01T00:00:00Z"
            )
            
            system_health = await self.health_checker.check_system_health()
            
            assert system_health.overall_status == HealthStatus.HEALTHY
            assert len(system_health.components) == 3
            assert system_health.uptime_seconds > 0
    
    def test_health_summary(self):
        """Test health summary generation."""
        # Create a mock health check result
        mock_health = SystemHealth(
            overall_status=HealthStatus.HEALTHY,
            components=[],
            timestamp="2023-01-01T00:00:00Z",
            uptime_seconds=3600.0
        )
        
        self.health_checker._last_health_check = mock_health
        self.health_checker._health_history = [mock_health]
        
        summary = self.health_checker.get_health_summary()
        
        assert summary['overall_status'] == 'healthy'
        assert summary['uptime_seconds'] == 3600.0
        assert summary['checks_performed'] == 1
        assert 'trend' in summary
    
    @pytest.mark.asyncio
    async def test_diagnostic_info(self):
        """Test diagnostic information generation."""
        with patch.object(self.health_checker, 'check_system_health') as mock_health_check:
            mock_health = SystemHealth(
                overall_status=HealthStatus.HEALTHY,
                components=[],
                timestamp="2023-01-01T00:00:00Z",
                uptime_seconds=3600.0
            )
            mock_health_check.return_value = mock_health
            
            diagnostics = await self.health_checker.get_diagnostic_info()
            
            assert 'health' in diagnostics
            assert 'configuration' in diagnostics
            assert 'system_info' in diagnostics
            assert diagnostics['configuration']['openhab_url'] == "http://test:8080"
            assert diagnostics['configuration']['has_token'] is True


class TestHealthMetric:
    """Unit tests for HealthMetric class."""
    
    def test_health_metric_creation(self):
        """Test health metric creation and serialization."""
        metric = HealthMetric(
            name="test_metric",
            status=HealthStatus.HEALTHY,
            value=42,
            message="Test metric message",
            timestamp="2023-01-01T00:00:00Z",
            threshold=50,
            unit="ms"
        )
        
        assert metric.name == "test_metric"
        assert metric.status == HealthStatus.HEALTHY
        assert metric.value == 42
        assert metric.threshold == 50
        assert metric.unit == "ms"
        
        # Test serialization
        metric_dict = metric.to_dict()
        assert metric_dict['name'] == "test_metric"
        assert metric_dict['status'] == "healthy"
        assert metric_dict['value'] == 42
    
    def test_health_metric_without_optional_fields(self):
        """Test health metric with only required fields."""
        metric = HealthMetric(
            name="simple_metric",
            status=HealthStatus.WARNING,
            value="test_value",
            message="Simple message",
            timestamp="2023-01-01T00:00:00Z"
        )
        
        metric_dict = metric.to_dict()
        assert 'threshold' not in metric_dict
        assert 'unit' not in metric_dict
        assert metric_dict['status'] == "warning"


class TestGlobalFunctions:
    """Unit tests for global logging functions."""
    
    def test_get_logger_singleton(self):
        """Test that get_logger returns singleton instances."""
        logger1 = get_logger("test_component")
        logger2 = get_logger("test_component")
        logger3 = get_logger("different_component")
        
        assert logger1 is logger2  # Same component should return same instance
        assert logger1 is not logger3  # Different component should return different instance
        assert logger1.component == "test_component"
        assert logger3.component == "different_component"
    
    def test_configure_logging(self):
        """Test logging configuration."""
        # Test basic configuration
        configure_logging(level="DEBUG", format_json=False, include_structured_data=True)
        
        # Verify root logger level was set
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
        
        # Verify handler was added
        assert len(root_logger.handlers) > 0
    
    def test_get_health_checker_singleton(self):
        """Test that get_health_checker returns singleton instance."""
        checker1 = get_health_checker()
        checker2 = get_health_checker()
        
        assert checker1 is checker2  # Should return same instance


if __name__ == "__main__":
    pytest.main([__file__])
