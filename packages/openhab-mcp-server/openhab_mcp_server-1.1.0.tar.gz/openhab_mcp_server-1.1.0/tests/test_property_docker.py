"""
Property-based tests for Docker containerization functionality.

**Feature: openhab-mcp-server, Property 35: Container configuration flexibility**
**Feature: openhab-mcp-server, Property 36: Container startup reliability**
**Feature: openhab-mcp-server, Property 37: Container health monitoring**
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from hypothesis import given, strategies as st, assume, settings

from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.utils.health import HealthMonitor, HealthStatus


# Test data generators
@st.composite
def valid_config_dict(draw):
    """Generate valid configuration dictionaries."""
    return {
        "openhab_url": draw(st.sampled_from([
            "http://localhost:8080",
            "http://openhab:8080", 
            "https://openhab.example.com:8443",
            "http://192.168.1.100:8080"
        ])),
        "openhab_token": draw(st.text(min_size=10, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        "timeout": draw(st.integers(min_value=5, max_value=300)),
        "log_level": draw(st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR"])),
        "retry_attempts": draw(st.integers(min_value=0, max_value=10)),
        "retry_backoff_factor": draw(st.floats(min_value=1.0, max_value=5.0)),
        "retry_max_delay": draw(st.integers(min_value=10, max_value=300))
    }


@st.composite
def environment_variables(draw):
    """Generate environment variable dictionaries."""
    env_vars = {}
    
    # Core configuration
    if draw(st.booleans()):
        env_vars["OPENHAB_URL"] = draw(st.sampled_from([
            "http://localhost:8080",
            "http://host.docker.internal:8080",
            "http://openhab.openhab.svc.cluster.local:8080"
        ]))
    
    if draw(st.booleans()):
        env_vars["OPENHAB_TOKEN"] = draw(st.text(
            min_size=10, 
            max_size=100, 
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), blacklist_characters='\x00')
        ))
    
    if draw(st.booleans()):
        env_vars["OPENHAB_TIMEOUT"] = str(draw(st.integers(min_value=5, max_value=300)))
    
    if draw(st.booleans()):
        env_vars["LOG_LEVEL"] = draw(st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR"]))
    
    if draw(st.booleans()):
        env_vars["LOG_FORMAT"] = draw(st.sampled_from(["text", "json"]))
    
    # Health check configuration
    if draw(st.booleans()):
        env_vars["HEALTH_CHECK_PORT"] = str(draw(st.integers(min_value=8000, max_value=9000)))
    
    return env_vars


@st.composite
def volume_mount_paths(draw):
    """Generate volume mount path configurations."""
    return {
        "config_path": draw(st.sampled_from([
            "/app/config",
            "/opt/openhab-mcp/config", 
            "/etc/openhab-mcp"
        ])),
        "logs_path": draw(st.sampled_from([
            "/app/logs",
            "/var/log/openhab-mcp",
            "/opt/openhab-mcp/logs"
        ])),
        "data_path": draw(st.sampled_from([
            "/app/data",
            "/var/lib/openhab-mcp",
            "/opt/openhab-mcp/data"
        ]))
    }


class TestContainerConfiguration:
    """Test container configuration flexibility."""
    
    @given(config_data=valid_config_dict())
    @settings(max_examples=50)
    def test_config_from_file_flexibility(self, config_data):
        """
        **Property 35: Container configuration flexibility**
        For any valid configuration data, the system should accept configuration 
        through JSON files and create valid Config objects.
        **Validates: Requirements 12.2**
        """
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            # Property: Configuration should load successfully from file
            config = Config.from_file(config_path)
            
            # Property: All configuration values should be preserved
            assert config.openhab_url == config_data["openhab_url"]
            assert config.openhab_token == config_data["openhab_token"]
            assert config.timeout == config_data["timeout"]
            assert config.log_level == config_data["log_level"]
            assert config.retry_attempts == config_data["retry_attempts"]
            assert config.retry_backoff_factor == config_data["retry_backoff_factor"]
            assert config.retry_max_delay == config_data["retry_max_delay"]
            
            # Property: Configuration should be valid
            assert config.timeout > 0
            assert config.retry_attempts >= 0
            assert config.retry_backoff_factor > 0
            assert config.retry_max_delay > 0
            assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            
        finally:
            # Clean up
            config_path.unlink()
    
    @given(env_vars=environment_variables(), config_data=valid_config_dict())
    @settings(max_examples=30, deadline=None)
    def test_env_override_flexibility(self, env_vars, config_data):
        """
        **Property 35: Container configuration flexibility**
        For any environment variables and file configuration, environment variables 
        should take precedence over file values.
        **Validates: Requirements 12.2**
        """
        # Filter out problematic environment variables that might interfere
        filtered_env_vars = {k: v for k, v in env_vars.items() 
                           if k in ["OPENHAB_URL", "OPENHAB_TOKEN", "OPENHAB_TIMEOUT", "LOG_LEVEL"]}
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            # Clear any existing environment variables that might interfere
            env_to_clear = ["OPENHAB_URL", "OPENHAB_TOKEN", "OPENHAB_TIMEOUT", "LOG_LEVEL"]
            original_env = {}
            for key in env_to_clear:
                if key in os.environ:
                    original_env[key] = os.environ[key]
                    del os.environ[key]
            
            try:
                # Set test environment variables
                for key, value in filtered_env_vars.items():
                    os.environ[key] = value
                
                config = Config.from_env_and_file(config_path)
                
                # Property: Environment variables should override file values
                if "OPENHAB_URL" in filtered_env_vars:
                    assert config.openhab_url == filtered_env_vars["OPENHAB_URL"]
                else:
                    assert config.openhab_url == config_data["openhab_url"]
                
                if "OPENHAB_TOKEN" in filtered_env_vars:
                    assert config.openhab_token == filtered_env_vars["OPENHAB_TOKEN"]
                else:
                    assert config.openhab_token == config_data["openhab_token"]
                
                if "OPENHAB_TIMEOUT" in filtered_env_vars:
                    assert config.timeout == int(filtered_env_vars["OPENHAB_TIMEOUT"])
                else:
                    assert config.timeout == config_data["timeout"]
                
                if "LOG_LEVEL" in filtered_env_vars:
                    assert config.log_level == filtered_env_vars["LOG_LEVEL"]
                else:
                    assert config.log_level == config_data["log_level"]
                
                # Property: Configuration should remain valid after override
                assert config.timeout > 0
                assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            
            finally:
                # Restore original environment
                for key in env_to_clear:
                    if key in os.environ:
                        del os.environ[key]
                for key, value in original_env.items():
                    os.environ[key] = value
        
        finally:
            # Clean up
            config_path.unlink()
    
    @given(paths=volume_mount_paths())
    @settings(max_examples=30)
    def test_volume_mount_support(self, paths):
        """
        **Property 35: Container configuration flexibility**
        For any volume mount paths, the system should support persistent configuration
        through mounted volumes.
        **Validates: Requirements 12.2**
        """
        # Create temporary directories to simulate volume mounts
        temp_dirs = {}
        
        try:
            for name, path in paths.items():
                # Create temporary directory
                temp_dir = tempfile.mkdtemp()
                temp_dirs[name] = temp_dir
                
                # Create a config file in the config directory
                if name == "config_path":
                    config_file = Path(temp_dir) / "config.json"
                    config_data = {
                        "openhab_url": "http://localhost:8080",
                        "openhab_token": "test-token",
                        "timeout": 30,
                        "log_level": "INFO"
                    }
                    with open(config_file, 'w') as f:
                        json.dump(config_data, f)
                    
                    # Property: Configuration should load from volume mount
                    config = Config.from_file(config_file)
                    assert config.openhab_url == config_data["openhab_url"]
                    assert config.openhab_token == config_data["openhab_token"]
                
                # Property: Directories should be writable (for logs and data)
                if name in ["logs_path", "data_path"]:
                    test_file = Path(temp_dir) / "test_write.txt"
                    test_file.write_text("test")
                    assert test_file.exists()
                    assert test_file.read_text() == "test"
        
        finally:
            # Clean up temporary directories
            import shutil
            for temp_dir in temp_dirs.values():
                shutil.rmtree(temp_dir, ignore_errors=True)


class TestContainerStartup:
    """Test container startup reliability."""
    
    @given(config_data=valid_config_dict())
    @settings(max_examples=30)
    @pytest.mark.asyncio
    async def test_health_monitor_startup_reliability(self, config_data):
        """
        **Property 36: Container startup reliability**
        For any valid configuration, the health monitor should initialize properly
        and be ready to accept health check requests.
        **Validates: Requirements 12.3**
        """
        # Create config from test data
        config = Config(**config_data)
        
        # Property: Health monitor should initialize without errors
        health_monitor = HealthMonitor(config)
        assert health_monitor.config == config
        assert health_monitor.start_time > 0
        
        # Property: Health monitor should be able to run checks
        try:
            # Mock the OpenHAB client to avoid actual network calls
            with patch('openhab_mcp_server.utils.health.OpenHABClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value = mock_client
                mock_client.get_system_info.return_value = {
                    "version": "4.0.0",
                    "buildString": "Test Build"
                }
                
                # Property: Health checks should complete successfully
                health_result = await health_monitor.run_all_checks()
                
                assert "status" in health_result
                assert "timestamp" in health_result
                assert "uptime" in health_result
                assert "checks" in health_result
                assert isinstance(health_result["checks"], list)
                
                # Property: Health status should be valid
                assert health_result["status"] in [
                    HealthStatus.HEALTHY, 
                    HealthStatus.WARNING, 
                    HealthStatus.UNHEALTHY
                ]
                
                # Property: Uptime should be reasonable
                assert health_result["uptime"] >= 0
                assert health_result["uptime"] < 60  # Should be recent
        
        except Exception as e:
            pytest.fail(f"Health monitor startup failed: {e}")
    
    @given(port=st.integers(min_value=8000, max_value=9000))
    @settings(max_examples=20)
    @pytest.mark.asyncio
    async def test_health_server_startup_reliability(self, port):
        """
        **Property 36: Container startup reliability**
        For any valid port number, the health check server should start successfully
        and be ready to accept connections.
        **Validates: Requirements 12.3**
        """
        config = Config(
            openhab_url="http://localhost:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
        
        health_monitor = HealthMonitor(config)
        
        try:
            # Property: Health server should start without errors
            await health_monitor.start_health_server(port)
            
            # Property: Health server should be accessible
            # Note: We can't easily test actual HTTP connectivity in unit tests
            # but we can verify the server components are initialized
            assert health_monitor._app is not None
            assert health_monitor._runner is not None
            assert health_monitor._site is not None
            
        except Exception as e:
            # If port is already in use, that's expected in some test environments
            if "Address already in use" in str(e) or "Permission denied" in str(e):
                pytest.skip(f"Port {port} not available for testing")
            else:
                pytest.fail(f"Health server startup failed: {e}")
        
        finally:
            # Property: Health server should stop cleanly
            try:
                await health_monitor.stop_health_server()
            except Exception:
                pass  # Ignore cleanup errors


class TestContainerHealthMonitoring:
    """Test container health monitoring."""
    
    @given(config_data=valid_config_dict())
    @settings(max_examples=30)
    @pytest.mark.asyncio
    async def test_health_monitoring_completeness(self, config_data):
        """
        **Property 37: Container health monitoring**
        For any configuration, health checks should provide appropriate status
        information for container orchestration.
        **Validates: Requirements 12.4**
        """
        config = Config(**config_data)
        health_monitor = HealthMonitor(config)
        
        # Mock OpenHAB client to control test conditions
        with patch('openhab_mcp_server.utils.health.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.get_system_info.return_value = {
                "version": "4.0.0",
                "buildString": "Test Build"
            }
            
            # Property: Health checks should return comprehensive information
            health_result = await health_monitor.run_all_checks()
            
            # Property: Result should contain required fields for orchestration
            required_fields = ["status", "message", "timestamp", "uptime", "checks"]
            for field in required_fields:
                assert field in health_result, f"Missing required field: {field}"
            
            # Property: Individual checks should be present
            check_names = [check["name"] for check in health_result["checks"]]
            expected_checks = ["configuration", "filesystem", "openhab-connection", "process-health"]
            
            for expected_check in expected_checks:
                assert expected_check in check_names, f"Missing health check: {expected_check}"
            
            # Property: Each check should have proper structure
            for check in health_result["checks"]:
                assert "name" in check
                assert "status" in check
                assert "message" in check
                assert "timestamp" in check
                
                # Property: Status should be valid
                assert check["status"] in [
                    HealthStatus.HEALTHY,
                    HealthStatus.WARNING, 
                    HealthStatus.UNHEALTHY,
                    HealthStatus.UNKNOWN
                ]
            
            # Property: Overall status should be derived from individual checks
            unhealthy_checks = [c for c in health_result["checks"] if c["status"] == HealthStatus.UNHEALTHY]
            warning_checks = [c for c in health_result["checks"] if c["status"] == HealthStatus.WARNING]
            
            if unhealthy_checks:
                assert health_result["status"] == HealthStatus.UNHEALTHY
            elif warning_checks:
                assert health_result["status"] == HealthStatus.WARNING
            else:
                assert health_result["status"] == HealthStatus.HEALTHY
    
    @given(
        openhab_available=st.booleans(),
        filesystem_writable=st.booleans(),
        config_valid=st.booleans()
    )
    @settings(max_examples=40)
    @pytest.mark.asyncio
    async def test_health_status_accuracy(self, openhab_available, filesystem_writable, config_valid):
        """
        **Property 37: Container health monitoring**
        For any combination of system conditions, health status should accurately
        reflect the actual system state.
        **Validates: Requirements 12.4**
        """
        # Create config based on validity flag
        if config_valid:
            config = Config(
                openhab_url="http://localhost:8080",
                openhab_token="valid-token-12345",
                timeout=30,
                log_level="INFO"
            )
        else:
            config = Config(
                openhab_url="",  # Invalid URL
                openhab_token=None,
                timeout=30,
                log_level="INFO"
            )
        
        health_monitor = HealthMonitor(config)
        
        # Mock OpenHAB client based on availability
        with patch('openhab_mcp_server.utils.health.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            if openhab_available:
                mock_client.get_system_info.return_value = {
                    "version": "4.0.0",
                    "buildString": "Test Build"
                }
            else:
                mock_client.get_system_info.side_effect = Exception("Connection failed")
            
            # Mock filesystem access
            with patch('pathlib.Path.exists') as mock_exists, \
                 patch('pathlib.Path.is_dir') as mock_is_dir, \
                 patch('pathlib.Path.touch') as mock_touch, \
                 patch('pathlib.Path.unlink') as mock_unlink:
                
                mock_exists.return_value = filesystem_writable
                mock_is_dir.return_value = filesystem_writable
                
                if not filesystem_writable:
                    mock_touch.side_effect = PermissionError("Permission denied")
                
                # Property: Health status should reflect actual conditions
                health_result = await health_monitor.run_all_checks()
                
                # Property: Configuration check should reflect config validity
                config_check = next((c for c in health_result["checks"] if c["name"] == "configuration"), None)
                assert config_check is not None
                
                if not config_valid:
                    assert config_check["status"] in [HealthStatus.UNHEALTHY, HealthStatus.WARNING]
                
                # Property: OpenHAB connection check should reflect availability
                if config.openhab_token:  # Only if token is configured
                    openhab_check = next((c for c in health_result["checks"] if c["name"] == "openhab-connection"), None)
                    assert openhab_check is not None
                    
                    if openhab_available:
                        assert openhab_check["status"] == HealthStatus.HEALTHY
                    else:
                        assert openhab_check["status"] == HealthStatus.UNHEALTHY
                
                # Property: Filesystem check should reflect write access
                filesystem_check = next((c for c in health_result["checks"] if c["name"] == "filesystem"), None)
                assert filesystem_check is not None
                
                if filesystem_writable:
                    assert filesystem_check["status"] == HealthStatus.HEALTHY
                else:
                    assert filesystem_check["status"] in [HealthStatus.WARNING, HealthStatus.UNHEALTHY]