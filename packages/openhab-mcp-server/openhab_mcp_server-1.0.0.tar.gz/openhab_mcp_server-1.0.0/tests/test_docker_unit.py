"""
Unit tests for Docker containerization functionality.

Tests container build, deployment, configuration through environment variables,
and health check endpoints and monitoring.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

import pytest
import aiohttp
from aiohttp import web

from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.utils.health import HealthMonitor, HealthStatus, HealthCheck


class TestDockerConfiguration:
    """Test Docker configuration functionality."""
    
    def test_config_from_environment_variables(self):
        """Test configuration loading from environment variables."""
        env_vars = {
            "OPENHAB_URL": "http://openhab:8080",
            "OPENHAB_TOKEN": "test-token-123",
            "OPENHAB_TIMEOUT": "45",
            "LOG_LEVEL": "DEBUG"
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            config = Config.from_env()
            
            assert config.openhab_url == "http://openhab:8080"
            assert config.openhab_token == "test-token-123"
            assert config.timeout == 45
            assert config.log_level == "DEBUG"
    
    def test_config_from_json_file(self):
        """Test configuration loading from JSON file."""
        config_data = {
            "openhab_url": "http://localhost:8080",
            "openhab_token": "file-token-456",
            "timeout": 60,
            "log_level": "INFO",
            "retry_attempts": 5
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            config = Config.from_file(config_path)
            
            assert config.openhab_url == "http://localhost:8080"
            assert config.openhab_token == "file-token-456"
            assert config.timeout == 60
            assert config.log_level == "INFO"
            assert config.retry_attempts == 5
        finally:
            config_path.unlink()
    
    def test_config_environment_override_file(self):
        """Test that environment variables override file configuration."""
        # Create config file
        config_data = {
            "openhab_url": "http://file-host:8080",
            "openhab_token": "file-token",
            "timeout": 30,
            "log_level": "INFO"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        # Set environment variables that should override
        env_vars = {
            "OPENHAB_URL": "http://env-host:8080",
            "OPENHAB_TOKEN": "env-token-1234567890",  # Make token long enough
            "LOG_LEVEL": "DEBUG"
        }
        
        try:
            with patch.dict(os.environ, env_vars, clear=False):
                config = Config.from_env_and_file(config_path)
                
                # Environment variables should override
                assert config.openhab_url == "http://env-host:8080"
                assert config.openhab_token == "env-token-1234567890"
                assert config.log_level == "DEBUG"
                
                # File values should be used where no env override
                assert config.timeout == 30
        finally:
            config_path.unlink()
    
    def test_config_validation_errors(self):
        """Test configuration validation with invalid values."""
        # Test invalid timeout
        with pytest.raises(ValueError, match="Timeout must be positive"):
            Config(
                openhab_url="http://localhost:8080",
                timeout=-1
            )
        
        # Test invalid retry attempts
        with pytest.raises(ValueError, match="Retry attempts must be non-negative"):
            Config(
                openhab_url="http://localhost:8080",
                retry_attempts=-1
            )
        
        # Test invalid log level
        with pytest.raises(ValueError, match="Log level must be one of"):
            Config(
                openhab_url="http://localhost:8080",
                log_level="INVALID"
            )


class TestHealthMonitoring:
    """Test health monitoring functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config(
            openhab_url="http://localhost:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.fixture
    def health_monitor(self, config):
        """Create health monitor instance."""
        return HealthMonitor(config)
    
    def test_health_check_creation(self):
        """Test HealthCheck object creation and serialization."""
        check = HealthCheck(
            name="test-check",
            status=HealthStatus.HEALTHY,
            message="Test passed",
            details={"key": "value"},
            response_time=123.45
        )
        
        result = check.to_dict()
        
        assert result["name"] == "test-check"
        assert result["status"] == HealthStatus.HEALTHY
        assert result["message"] == "Test passed"
        assert result["details"] == {"key": "value"}
        assert result["response_time_ms"] == 123.45
        assert "timestamp" in result
    
    def test_health_monitor_initialization(self, health_monitor, config):
        """Test health monitor initialization."""
        assert health_monitor.config == config
        assert health_monitor.start_time > 0
        assert health_monitor.openhab_client is None
        assert health_monitor._app is None
    
    @pytest.mark.asyncio
    async def test_configuration_check_valid(self, health_monitor):
        """Test configuration health check with valid config."""
        check = await health_monitor._check_configuration()
        
        assert check.name == "configuration"
        assert check.status == HealthStatus.HEALTHY  # Token is configured in fixture
        assert "valid" in check.message.lower()
    
    @pytest.mark.asyncio
    async def test_configuration_check_invalid_url(self):
        """Test configuration health check with invalid URL."""
        config = Config(
            openhab_url="",  # Invalid empty URL
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
        health_monitor = HealthMonitor(config)
        
        check = await health_monitor._check_configuration()
        
        assert check.name == "configuration"
        assert check.status == HealthStatus.UNHEALTHY
        assert "url not configured" in check.message.lower()
    
    def test_filesystem_check_accessible(self, health_monitor):
        """Test filesystem health check with accessible paths."""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.is_dir') as mock_is_dir, \
             patch('pathlib.Path.touch') as mock_touch, \
             patch('pathlib.Path.unlink') as mock_unlink:
            
            mock_exists.return_value = True
            mock_is_dir.return_value = True
            
            check = health_monitor._check_filesystem_access()
            
            assert check.name == "filesystem"
            assert check.status == HealthStatus.HEALTHY
            assert "accessible" in check.message.lower()
    
    def test_filesystem_check_permission_denied(self, health_monitor):
        """Test filesystem health check with permission errors."""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.is_dir') as mock_is_dir, \
             patch('pathlib.Path.touch') as mock_touch:
            
            mock_exists.return_value = True
            mock_is_dir.return_value = True
            mock_touch.side_effect = PermissionError("Permission denied")
            
            check = health_monitor._check_filesystem_access()
            
            assert check.name == "filesystem"
            assert check.status in [HealthStatus.WARNING, HealthStatus.UNHEALTHY]
            assert "not accessible" in check.message.lower()
    
    @pytest.mark.asyncio
    async def test_openhab_connection_check_success(self, health_monitor):
        """Test openHAB connection health check with successful connection."""
        # Set up config with token
        health_monitor.config.openhab_token = "test-token"
        
        with patch('openhab_mcp_server.utils.health.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.get_system_info.return_value = {
                "version": "4.0.0",
                "buildString": "Test Build"
            }
            
            check = await health_monitor._check_openhab_connection()
            
            assert check.name == "openhab-connection"
            assert check.status == HealthStatus.HEALTHY
            assert "successful" in check.message.lower()
            assert check.response_time is not None
            assert check.response_time > 0
    
    @pytest.mark.asyncio
    async def test_openhab_connection_check_failure(self, health_monitor):
        """Test openHAB connection health check with connection failure."""
        # Set up config with token
        health_monitor.config.openhab_token = "test-token"
        
        with patch('openhab_mcp_server.utils.health.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.get_system_info.side_effect = Exception("Connection failed")
            
            check = await health_monitor._check_openhab_connection()
            
            assert check.name == "openhab-connection"
            assert check.status == HealthStatus.UNHEALTHY
            assert "connection error" in check.message.lower()
    
    @pytest.mark.asyncio
    async def test_openhab_connection_check_no_token(self, health_monitor):
        """Test openHAB connection health check without token."""
        # Ensure no token is set
        health_monitor.config.openhab_token = None
        
        check = await health_monitor._check_openhab_connection()
        
        assert check.name == "openhab-connection"
        assert check.status == HealthStatus.WARNING
        assert "no openhab token" in check.message.lower()
    
    def test_process_health_check(self, health_monitor):
        """Test process health check."""
        check = health_monitor._check_process_health()
        
        assert check.name == "process-health"
        assert check.status == HealthStatus.HEALTHY
        assert "running normally" in check.message.lower()
        assert "pid" in check.details
    
    @pytest.mark.asyncio
    async def test_run_all_checks_healthy(self, health_monitor):
        """Test running all health checks with healthy results."""
        with patch.object(health_monitor, '_check_configuration') as mock_config, \
             patch.object(health_monitor, '_check_filesystem_access') as mock_fs, \
             patch.object(health_monitor, '_check_openhab_connection') as mock_openhab, \
             patch.object(health_monitor, '_check_process_health') as mock_process:
            
            # Mock all checks as healthy
            mock_config.return_value = HealthCheck("configuration", HealthStatus.HEALTHY, "OK")
            mock_fs.return_value = HealthCheck("filesystem", HealthStatus.HEALTHY, "OK")
            mock_openhab.return_value = HealthCheck("openhab-connection", HealthStatus.HEALTHY, "OK")
            mock_process.return_value = HealthCheck("process-health", HealthStatus.HEALTHY, "OK")
            
            result = await health_monitor.run_all_checks()
            
            assert result["status"] == HealthStatus.HEALTHY
            assert "all checks passed" in result["message"].lower()
            assert len(result["checks"]) == 4
            assert "uptime" in result
            assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_run_all_checks_unhealthy(self, health_monitor):
        """Test running all health checks with some unhealthy results."""
        with patch.object(health_monitor, '_check_configuration') as mock_config, \
             patch.object(health_monitor, '_check_filesystem_access') as mock_fs, \
             patch.object(health_monitor, '_check_openhab_connection') as mock_openhab, \
             patch.object(health_monitor, '_check_process_health') as mock_process:
            
            # Mock some checks as unhealthy
            mock_config.return_value = HealthCheck("configuration", HealthStatus.UNHEALTHY, "Failed")
            mock_fs.return_value = HealthCheck("filesystem", HealthStatus.HEALTHY, "OK")
            mock_openhab.return_value = HealthCheck("openhab-connection", HealthStatus.UNHEALTHY, "Failed")
            mock_process.return_value = HealthCheck("process-health", HealthStatus.HEALTHY, "OK")
            
            result = await health_monitor.run_all_checks()
            
            assert result["status"] == HealthStatus.UNHEALTHY
            assert "2 check(s) failed" in result["message"]
            assert len(result["checks"]) == 4


class TestHealthServer:
    """Test health check HTTP server functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config(
            openhab_url="http://localhost:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.fixture
    def health_monitor(self, config):
        """Create health monitor instance."""
        return HealthMonitor(config)
    
    @pytest.mark.asyncio
    async def test_health_server_startup_shutdown(self, health_monitor):
        """Test health server startup and shutdown."""
        try:
            # Start server on a random available port
            await health_monitor.start_health_server(8999)
            
            # Verify server components are initialized
            assert health_monitor._app is not None
            assert health_monitor._runner is not None
            assert health_monitor._site is not None
            
        except OSError as e:
            if "Address already in use" in str(e):
                pytest.skip("Port 8999 not available for testing")
            else:
                raise
        finally:
            # Clean shutdown
            await health_monitor.stop_health_server()
            
            # Verify cleanup
            assert health_monitor._app is None
            assert health_monitor._runner is None
            assert health_monitor._site is None
    
    @pytest.mark.asyncio
    async def test_health_handler_healthy(self, health_monitor):
        """Test health endpoint handler with healthy status."""
        # Mock the health check method
        with patch.object(health_monitor, 'run_all_checks') as mock_checks:
            mock_checks.return_value = {
                "status": HealthStatus.HEALTHY,
                "message": "All checks passed",
                "timestamp": 1234567890,
                "uptime": 100,
                "checks": []
            }
            
            # Create mock request
            request = MagicMock()
            
            # Call handler
            response = await health_monitor._health_handler(request)
            
            assert response.status == 200
    
    @pytest.mark.asyncio
    async def test_health_handler_unhealthy(self, health_monitor):
        """Test health endpoint handler with unhealthy status."""
        # Mock the health check method
        with patch.object(health_monitor, 'run_all_checks') as mock_checks:
            mock_checks.return_value = {
                "status": HealthStatus.UNHEALTHY,
                "message": "Some checks failed",
                "timestamp": 1234567890,
                "uptime": 100,
                "checks": []
            }
            
            # Create mock request
            request = MagicMock()
            
            # Call handler
            response = await health_monitor._health_handler(request)
            
            assert response.status == 503  # Service Unavailable
    
    @pytest.mark.asyncio
    async def test_liveness_handler(self, health_monitor):
        """Test liveness probe handler."""
        request = MagicMock()
        
        response = await health_monitor._liveness_handler(request)
        
        assert response.status == 200
        # Verify response contains expected fields
        # Note: We can't easily test the JSON content without parsing it
    
    @pytest.mark.asyncio
    async def test_readiness_handler_ready(self, health_monitor):
        """Test readiness probe handler when service is ready."""
        with patch.object(health_monitor, '_check_configuration') as mock_config, \
             patch.object(health_monitor, '_check_openhab_connection') as mock_openhab:
            
            # Mock checks as healthy
            mock_config.return_value = HealthCheck("configuration", HealthStatus.HEALTHY, "OK")
            mock_openhab.return_value = HealthCheck("openhab-connection", HealthStatus.HEALTHY, "OK")
            
            request = MagicMock()
            
            response = await health_monitor._readiness_handler(request)
            
            assert response.status == 200
    
    @pytest.mark.asyncio
    async def test_readiness_handler_not_ready(self, health_monitor):
        """Test readiness probe handler when service is not ready."""
        with patch.object(health_monitor, '_check_configuration') as mock_config, \
             patch.object(health_monitor, '_check_openhab_connection') as mock_openhab:
            
            # Mock checks as unhealthy
            mock_config.return_value = HealthCheck("configuration", HealthStatus.UNHEALTHY, "Failed")
            mock_openhab.return_value = HealthCheck("openhab-connection", HealthStatus.UNHEALTHY, "Failed")
            
            request = MagicMock()
            
            response = await health_monitor._readiness_handler(request)
            
            assert response.status == 503
    
    @pytest.mark.asyncio
    async def test_metrics_handler(self, health_monitor):
        """Test metrics endpoint handler."""
        with patch.object(health_monitor, 'run_all_checks') as mock_checks:
            mock_checks.return_value = {
                "status": HealthStatus.HEALTHY,
                "message": "All checks passed",
                "timestamp": 1234567890,
                "uptime": 100,
                "checks": [
                    {
                        "name": "configuration",
                        "status": HealthStatus.HEALTHY,
                        "response_time_ms": 5.0
                    }
                ]
            }
            
            request = MagicMock()
            
            response = await health_monitor._metrics_handler(request)
            
            assert response.status == 200


class TestDockerIntegration:
    """Test Docker integration scenarios."""
    
    def test_docker_environment_simulation(self):
        """Test configuration in Docker-like environment."""
        # Simulate Docker environment variables
        docker_env = {
            "OPENHAB_URL": "http://openhab.openhab.svc.cluster.local:8080",
            "OPENHAB_TOKEN": "k8s-secret-token",
            "OPENHAB_TIMEOUT": "60",
            "LOG_LEVEL": "INFO",
            "LOG_FORMAT": "json",
            "HEALTH_CHECK_PORT": "8081"
        }
        
        with patch.dict(os.environ, docker_env, clear=False):
            config = Config.from_env()
            
            # Verify Docker-specific configuration
            assert "svc.cluster.local" in config.openhab_url
            assert config.openhab_token == "k8s-secret-token"
            assert config.timeout == 60
            assert config.log_level == "INFO"
    
    def test_volume_mount_configuration(self):
        """Test configuration loading from volume-mounted files."""
        # Simulate volume-mounted configuration
        config_data = {
            "openhab_url": "http://openhab:8080",
            "openhab_token": "volume-mounted-token",
            "timeout": 45,
            "log_level": "DEBUG",
            "health_check": {
                "enabled": True,
                "port": 8081,
                "interval": 30
            }
        }
        
        # Create temporary file to simulate volume mount
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            # Test loading from volume-mounted path
            config = Config.from_file(config_path)
            
            assert config.openhab_url == "http://openhab:8080"
            assert config.openhab_token == "volume-mounted-token"
            assert config.timeout == 45
            assert config.log_level == "DEBUG"
        finally:
            config_path.unlink()
    
    @pytest.mark.asyncio
    async def test_container_health_check_integration(self):
        """Test complete health check integration for containers."""
        config = Config(
            openhab_url="http://openhab:8080",
            openhab_token="container-token",
            timeout=30,
            log_level="INFO"
        )
        
        health_monitor = HealthMonitor(config)
        
        # Mock openHAB client for container environment
        with patch('openhab_mcp_server.utils.health.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.get_system_info.return_value = {
                "version": "4.0.0",
                "buildString": "Container Build"
            }
            
            # Run health checks
            result = await health_monitor.run_all_checks()
            
            # Verify container-appropriate health status
            assert "status" in result
            assert "timestamp" in result
            assert "uptime" in result
            assert "checks" in result
            assert len(result["checks"]) >= 3  # At least config, filesystem, process
            
            # Verify all required health check types are present
            check_names = [check["name"] for check in result["checks"]]
            expected_checks = ["configuration", "filesystem", "process-health"]
            for expected in expected_checks:
                assert expected in check_names