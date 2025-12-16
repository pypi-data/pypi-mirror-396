"""
Health monitoring utilities for the openHAB MCP Server.

This module provides health check functionality for container orchestration
and system monitoring.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

import aiohttp
from aiohttp import web

from .config import Config
from .openhab_client import OpenHABClient


logger = logging.getLogger(__name__)


class HealthStatus:
    """Health status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    WARNING = "warning"
    UNKNOWN = "unknown"


class HealthCheck:
    """Individual health check result."""
    
    def __init__(
        self,
        name: str,
        status: str = HealthStatus.UNKNOWN,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        response_time: Optional[float] = None
    ):
        """Initialize health check result.
        
        Args:
            name: Name of the health check
            status: Health status (healthy, unhealthy, warning, unknown)
            message: Human-readable status message
            details: Additional details about the check
            response_time: Response time in milliseconds
        """
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.response_time = response_time
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "timestamp": self.timestamp
        }
        
        if self.details:
            result["details"] = self.details
        
        if self.response_time is not None:
            result["response_time_ms"] = round(self.response_time, 2)
        
        return result


class HealthMonitor:
    """Health monitoring system for the MCP server."""
    
    def __init__(self, config: Config):
        """Initialize health monitor.
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.start_time = time.time()
        self.openhab_client: Optional[OpenHABClient] = None
        self._app: Optional[web.Application] = None
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None
        
    async def start_health_server(self, port: int = 8081) -> None:
        """Start the health check HTTP server.
        
        Args:
            port: Port to listen on for health checks
        """
        try:
            # Create aiohttp application
            self._app = web.Application()
            
            # Add health check routes
            self._app.router.add_get('/', self._health_handler)
            self._app.router.add_get('/health', self._health_handler)
            self._app.router.add_get('/health/live', self._liveness_handler)
            self._app.router.add_get('/health/ready', self._readiness_handler)
            self._app.router.add_get('/metrics', self._metrics_handler)
            
            # Start server
            self._runner = web.AppRunner(self._app)
            await self._runner.setup()
            
            self._site = web.TCPSite(self._runner, '0.0.0.0', port)
            await self._site.start()
            
            logger.info(f"Health check server started on port {port}")
            
        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")
            raise
    
    async def stop_health_server(self) -> None:
        """Stop the health check HTTP server."""
        try:
            if self._site:
                await self._site.stop()
                self._site = None
            
            if self._runner:
                await self._runner.cleanup()
                self._runner = None
            
            self._app = None
            logger.info("Health check server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping health check server: {e}")
    
    async def _health_handler(self, request: web.Request) -> web.Response:
        """Handle general health check requests."""
        try:
            health_result = await self.run_all_checks()
            
            # Determine HTTP status code based on health
            if health_result["status"] == HealthStatus.HEALTHY:
                status_code = 200
            elif health_result["status"] == HealthStatus.WARNING:
                status_code = 200  # Warnings don't fail health checks
            else:
                status_code = 503  # Service Unavailable
            
            return web.json_response(
                health_result,
                status=status_code
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            error_response = {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Health check error: {str(e)}",
                "timestamp": time.time()
            }
            return web.json_response(error_response, status=503)
    
    async def _liveness_handler(self, request: web.Request) -> web.Response:
        """Handle Kubernetes liveness probe requests."""
        try:
            # Simple liveness check - just verify the process is running
            uptime = time.time() - self.start_time
            
            result = {
                "status": HealthStatus.HEALTHY,
                "message": "Service is alive",
                "uptime": round(uptime, 2),
                "timestamp": time.time()
            }
            
            return web.json_response(result, status=200)
            
        except Exception as e:
            logger.error(f"Liveness check failed: {e}")
            return web.json_response(
                {"status": HealthStatus.UNHEALTHY, "message": str(e)},
                status=503
            )
    
    async def _readiness_handler(self, request: web.Request) -> web.Response:
        """Handle Kubernetes readiness probe requests."""
        try:
            # Check if service is ready to accept requests
            checks = [
                await self._check_configuration(),
                await self._check_openhab_connection()
            ]
            
            # Service is ready if all critical checks pass
            failed_checks = [c for c in checks if c.status == HealthStatus.UNHEALTHY]
            
            if failed_checks:
                result = {
                    "status": HealthStatus.UNHEALTHY,
                    "message": f"{len(failed_checks)} readiness check(s) failed",
                    "checks": [c.to_dict() for c in checks],
                    "timestamp": time.time()
                }
                return web.json_response(result, status=503)
            else:
                result = {
                    "status": HealthStatus.HEALTHY,
                    "message": "Service is ready",
                    "checks": [c.to_dict() for c in checks],
                    "timestamp": time.time()
                }
                return web.json_response(result, status=200)
                
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return web.json_response(
                {"status": HealthStatus.UNHEALTHY, "message": str(e)},
                status=503
            )
    
    async def _metrics_handler(self, request: web.Request) -> web.Response:
        """Handle metrics requests for monitoring systems."""
        try:
            uptime = time.time() - self.start_time
            
            # Basic metrics in Prometheus format
            metrics = [
                f"# HELP openhab_mcp_uptime_seconds Total uptime in seconds",
                f"# TYPE openhab_mcp_uptime_seconds counter",
                f"openhab_mcp_uptime_seconds {uptime}",
                "",
                f"# HELP openhab_mcp_start_time_seconds Start time as Unix timestamp",
                f"# TYPE openhab_mcp_start_time_seconds gauge",
                f"openhab_mcp_start_time_seconds {self.start_time}",
                ""
            ]
            
            # Add health check metrics
            health_result = await self.run_all_checks()
            health_value = 1 if health_result["status"] == HealthStatus.HEALTHY else 0
            
            metrics.extend([
                f"# HELP openhab_mcp_health Health status (1=healthy, 0=unhealthy)",
                f"# TYPE openhab_mcp_health gauge",
                f"openhab_mcp_health {health_value}",
                ""
            ])
            
            # Add individual check metrics
            for check in health_result.get("checks", []):
                check_name = check["name"].replace("-", "_")
                check_value = 1 if check["status"] == HealthStatus.HEALTHY else 0
                
                metrics.extend([
                    f"# HELP openhab_mcp_check_{check_name} Health check status",
                    f"# TYPE openhab_mcp_check_{check_name} gauge",
                    f"openhab_mcp_check_{check_name} {check_value}",
                    ""
                ])
                
                # Add response time if available
                if "response_time_ms" in check:
                    metrics.extend([
                        f"# HELP openhab_mcp_check_{check_name}_response_time_ms Response time in milliseconds",
                        f"# TYPE openhab_mcp_check_{check_name}_response_time_ms gauge",
                        f"openhab_mcp_check_{check_name}_response_time_ms {check['response_time_ms']}",
                        ""
                    ])
            
            return web.Response(
                text="\n".join(metrics),
                content_type="text/plain"
            )
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return web.Response(text=f"# Error: {e}", status=500)
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return consolidated results."""
        checks = []
        
        # Run all health checks
        checks.append(await self._check_configuration())
        checks.append(self._check_filesystem_access())
        checks.append(await self._check_openhab_connection())
        checks.append(self._check_process_health())
        
        # Determine overall health status
        unhealthy_checks = [c for c in checks if c.status == HealthStatus.UNHEALTHY]
        warning_checks = [c for c in checks if c.status == HealthStatus.WARNING]
        
        if unhealthy_checks:
            overall_status = HealthStatus.UNHEALTHY
            status_message = f"{len(unhealthy_checks)} check(s) failed"
        elif warning_checks:
            overall_status = HealthStatus.WARNING
            status_message = f"{len(warning_checks)} check(s) have warnings"
        else:
            overall_status = HealthStatus.HEALTHY
            status_message = "All checks passed"
        
        return {
            "status": overall_status,
            "message": status_message,
            "timestamp": time.time(),
            "uptime": round(time.time() - self.start_time, 2),
            "version": "1.0.0",
            "checks": [c.to_dict() for c in checks]
        }
    
    async def _check_configuration(self) -> HealthCheck:
        """Check configuration validity."""
        try:
            # Validate required configuration
            if not self.config.openhab_url:
                return HealthCheck(
                    "configuration",
                    HealthStatus.UNHEALTHY,
                    "openHAB URL not configured"
                )
            
            if not self.config.openhab_token:
                return HealthCheck(
                    "configuration",
                    HealthStatus.WARNING,
                    "openHAB token not configured - authentication may fail"
                )
            
            return HealthCheck(
                "configuration",
                HealthStatus.HEALTHY,
                "Configuration is valid",
                {
                    "openhab_url": self.config.openhab_url,
                    "timeout": self.config.timeout,
                    "log_level": self.config.log_level
                }
            )
            
        except Exception as e:
            return HealthCheck(
                "configuration",
                HealthStatus.UNHEALTHY,
                f"Configuration error: {str(e)}"
            )
    
    def _check_filesystem_access(self) -> HealthCheck:
        """Check filesystem access for required directories."""
        try:
            paths_to_check = {
                "config": "/app/config",
                "logs": "/app/logs",
                "data": "/app/data"
            }
            
            details = {}
            all_accessible = True
            
            for name, path in paths_to_check.items():
                path_obj = Path(path)
                try:
                    if path_obj.exists() and path_obj.is_dir():
                        # Try to create a test file to verify write access
                        test_file = path_obj / ".health_check"
                        test_file.touch()
                        test_file.unlink()  # Clean up
                        details[name] = "accessible"
                    else:
                        details[name] = "not accessible"
                        all_accessible = False
                        
                except PermissionError:
                    details[name] = "permission denied"
                    all_accessible = False
                except Exception as e:
                    details[name] = f"error: {str(e)}"
                    all_accessible = False
            
            if all_accessible:
                return HealthCheck(
                    "filesystem",
                    HealthStatus.HEALTHY,
                    "All filesystem paths accessible",
                    details
                )
            else:
                return HealthCheck(
                    "filesystem",
                    HealthStatus.WARNING,
                    "Some filesystem paths not accessible",
                    details
                )
                
        except Exception as e:
            return HealthCheck(
                "filesystem",
                HealthStatus.UNHEALTHY,
                f"Filesystem check error: {str(e)}"
            )
    
    async def _check_openhab_connection(self) -> HealthCheck:
        """Check connection to openHAB server."""
        if not self.config.openhab_token:
            return HealthCheck(
                "openhab-connection",
                HealthStatus.WARNING,
                "No openHAB token configured - connection test skipped"
            )
        
        start_time = time.time()
        
        try:
            # Create client if not exists
            if not self.openhab_client:
                self.openhab_client = OpenHABClient(
                    self.config.openhab_url,
                    self.config.openhab_token,
                    timeout=min(self.config.timeout, 10)  # Shorter timeout for health checks
                )
            
            # Test basic connectivity
            system_info = await self.openhab_client.get_system_info()
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if system_info:
                return HealthCheck(
                    "openhab-connection",
                    HealthStatus.HEALTHY,
                    "openHAB connection successful",
                    {
                        "openhab_version": system_info.get("version", "unknown"),
                        "openhab_url": self.config.openhab_url
                    },
                    response_time
                )
            else:
                return HealthCheck(
                    "openhab-connection",
                    HealthStatus.UNHEALTHY,
                    "openHAB returned empty response",
                    response_time=response_time
                )
                
        except asyncio.TimeoutError:
            return HealthCheck(
                "openhab-connection",
                HealthStatus.UNHEALTHY,
                f"Connection timeout after {self.config.timeout}s"
            )
        except Exception as e:
            return HealthCheck(
                "openhab-connection",
                HealthStatus.UNHEALTHY,
                f"Connection error: {str(e)}"
            )
    
    def _check_process_health(self) -> HealthCheck:
        """Check basic process health metrics."""
        try:
            import os
            import psutil
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            details = {
                "pid": os.getpid(),
                "memory_rss_mb": round(memory_info.rss / 1024 / 1024, 2),
                "memory_vms_mb": round(memory_info.vms / 1024 / 1024, 2),
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads()
            }
            
            return HealthCheck(
                "process-health",
                HealthStatus.HEALTHY,
                "Process running normally",
                details
            )
            
        except ImportError:
            # psutil not available, basic check
            import os
            return HealthCheck(
                "process-health",
                HealthStatus.HEALTHY,
                "Process running normally",
                {"pid": os.getpid()}
            )
        except Exception as e:
            return HealthCheck(
                "process-health",
                HealthStatus.WARNING,
                f"Process health check error: {str(e)}"
            )