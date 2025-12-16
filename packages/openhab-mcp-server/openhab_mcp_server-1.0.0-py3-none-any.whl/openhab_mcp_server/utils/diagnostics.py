"""
System diagnostics and health monitoring for openHAB MCP server.

This module provides health metrics, connection status monitoring,
and diagnostic endpoints for system status reporting.
"""

import asyncio
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from openhab_mcp_server.utils.config import Config, get_config
from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError
from openhab_mcp_server.utils.logging import get_logger, LogCategory


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthMetric:
    """Individual health metric."""
    name: str
    status: HealthStatus
    value: Union[str, int, float, bool]
    message: str
    timestamp: str
    threshold: Optional[Union[int, float]] = None
    unit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {k: v.value if isinstance(v, Enum) else v for k, v in asdict(self).items() if v is not None}


@dataclass
class ComponentHealth:
    """Health status for a system component."""
    component: str
    status: HealthStatus
    metrics: List[HealthMetric]
    last_check: str
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'component': self.component,
            'status': self.status.value,
            'metrics': [m.to_dict() for m in self.metrics],
            'last_check': self.last_check,
            'error_message': self.error_message
        }


@dataclass
class SystemHealth:
    """Overall system health status."""
    overall_status: HealthStatus
    components: List[ComponentHealth]
    timestamp: str
    uptime_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'overall_status': self.overall_status.value,
            'components': [c.to_dict() for c in self.components],
            'timestamp': self.timestamp,
            'uptime_seconds': self.uptime_seconds
        }


class HealthChecker:
    """Health monitoring and diagnostics system."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize health checker.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        self.logger = get_logger("health_checker")
        self.start_time = time.time()
        self._last_health_check: Optional[SystemHealth] = None
        self._health_history: List[SystemHealth] = []
        self._max_history_size = 100
        
        # Health thresholds
        self.thresholds = {
            'response_time_ms': 5000,  # 5 seconds
            'success_rate_percent': 95.0,
            'error_rate_percent': 5.0,
            'connection_timeout_seconds': 30
        }
    
    async def check_system_health(self) -> SystemHealth:
        """Perform comprehensive system health check.
        
        Returns:
            SystemHealth object with current status
        """
        self.logger.info("Starting system health check", category=LogCategory.HEALTH)
        
        components = []
        overall_status = HealthStatus.HEALTHY
        
        # Check openHAB connectivity
        openhab_health = await self._check_openhab_health()
        components.append(openhab_health)
        if openhab_health.status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
            overall_status = openhab_health.status
        
        # Check MCP server health
        server_health = await self._check_server_health()
        components.append(server_health)
        if server_health.status == HealthStatus.CRITICAL:
            overall_status = HealthStatus.CRITICAL
        elif server_health.status == HealthStatus.WARNING and overall_status == HealthStatus.HEALTHY:
            overall_status = HealthStatus.WARNING
        
        # Check system resources
        resource_health = await self._check_resource_health()
        components.append(resource_health)
        if resource_health.status == HealthStatus.CRITICAL:
            overall_status = HealthStatus.CRITICAL
        elif resource_health.status == HealthStatus.WARNING and overall_status == HealthStatus.HEALTHY:
            overall_status = HealthStatus.WARNING
        
        # Create system health report
        system_health = SystemHealth(
            overall_status=overall_status,
            components=components,
            timestamp=datetime.utcnow().isoformat() + "Z",
            uptime_seconds=time.time() - self.start_time
        )
        
        # Store in history
        self._last_health_check = system_health
        self._health_history.append(system_health)
        if len(self._health_history) > self._max_history_size:
            self._health_history.pop(0)
        
        self.logger.info(
            f"System health check completed: {overall_status.value}",
            category=LogCategory.HEALTH,
            metadata={
                'overall_status': overall_status.value,
                'component_count': len(components),
                'uptime_seconds': system_health.uptime_seconds
            }
        )
        
        return system_health
    
    async def _check_openhab_health(self) -> ComponentHealth:
        """Check openHAB server health."""
        metrics = []
        status = HealthStatus.HEALTHY
        error_message = None
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        try:
            client = OpenHABClient(self.config)
            
            # Test basic connectivity
            start_time = time.time()
            async with client:
                # Get system info
                system_info = await client.get_system_info()
                response_time_ms = (time.time() - start_time) * 1000
                
                # Response time metric
                response_status = HealthStatus.HEALTHY
                if response_time_ms > self.thresholds['response_time_ms']:
                    response_status = HealthStatus.WARNING
                    status = HealthStatus.WARNING
                
                metrics.append(HealthMetric(
                    name="response_time",
                    status=response_status,
                    value=round(response_time_ms, 2),
                    message=f"API response time: {response_time_ms:.2f}ms",
                    timestamp=timestamp,
                    threshold=self.thresholds['response_time_ms'],
                    unit="ms"
                ))
                
                # Version metric
                version = system_info.get('version', 'unknown')
                metrics.append(HealthMetric(
                    name="version",
                    status=HealthStatus.HEALTHY,
                    value=version,
                    message=f"openHAB version: {version}",
                    timestamp=timestamp
                ))
                
                # Start level metric
                start_level = system_info.get('startLevel', 0)
                start_level_status = HealthStatus.HEALTHY if start_level >= 80 else HealthStatus.WARNING
                if start_level_status == HealthStatus.WARNING:
                    status = HealthStatus.WARNING
                
                metrics.append(HealthMetric(
                    name="start_level",
                    status=start_level_status,
                    value=start_level,
                    message=f"System start level: {start_level}",
                    timestamp=timestamp,
                    threshold=80
                ))
                
                # Test additional endpoints
                try:
                    items = await client.get_items()
                    metrics.append(HealthMetric(
                        name="items_accessible",
                        status=HealthStatus.HEALTHY,
                        value=len(items),
                        message=f"Items endpoint accessible, {len(items)} items found",
                        timestamp=timestamp
                    ))
                except Exception as e:
                    metrics.append(HealthMetric(
                        name="items_accessible",
                        status=HealthStatus.WARNING,
                        value=False,
                        message=f"Items endpoint error: {str(e)}",
                        timestamp=timestamp
                    ))
                    status = HealthStatus.WARNING
                
                try:
                    things = await client.get_things()
                    metrics.append(HealthMetric(
                        name="things_accessible",
                        status=HealthStatus.HEALTHY,
                        value=len(things),
                        message=f"Things endpoint accessible, {len(things)} things found",
                        timestamp=timestamp
                    ))
                except Exception as e:
                    metrics.append(HealthMetric(
                        name="things_accessible",
                        status=HealthStatus.WARNING,
                        value=False,
                        message=f"Things endpoint error: {str(e)}",
                        timestamp=timestamp
                    ))
                    status = HealthStatus.WARNING
                
        except OpenHABError as e:
            status = HealthStatus.CRITICAL
            error_message = str(e)
            metrics.append(HealthMetric(
                name="connectivity",
                status=HealthStatus.CRITICAL,
                value=False,
                message=f"openHAB connection failed: {str(e)}",
                timestamp=timestamp
            ))
        except Exception as e:
            status = HealthStatus.CRITICAL
            error_message = str(e)
            metrics.append(HealthMetric(
                name="connectivity",
                status=HealthStatus.CRITICAL,
                value=False,
                message=f"Unexpected error: {str(e)}",
                timestamp=timestamp
            ))
        
        return ComponentHealth(
            component="openhab_server",
            status=status,
            metrics=metrics,
            last_check=timestamp,
            error_message=error_message
        )
    
    async def _check_server_health(self) -> ComponentHealth:
        """Check MCP server health."""
        metrics = []
        status = HealthStatus.HEALTHY
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Uptime metric
        uptime_seconds = time.time() - self.start_time
        metrics.append(HealthMetric(
            name="uptime",
            status=HealthStatus.HEALTHY,
            value=round(uptime_seconds, 2),
            message=f"Server uptime: {uptime_seconds:.2f} seconds",
            timestamp=timestamp,
            unit="seconds"
        ))
        
        # Memory usage (basic check)
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            memory_status = HealthStatus.HEALTHY
            if memory_mb > 500:  # 500MB threshold
                memory_status = HealthStatus.WARNING
                status = HealthStatus.WARNING
            
            metrics.append(HealthMetric(
                name="memory_usage",
                status=memory_status,
                value=round(memory_mb, 2),
                message=f"Memory usage: {memory_mb:.2f} MB",
                timestamp=timestamp,
                threshold=500,
                unit="MB"
            ))
        except ImportError:
            # psutil not available, skip memory check
            metrics.append(HealthMetric(
                name="memory_usage",
                status=HealthStatus.UNKNOWN,
                value="unavailable",
                message="Memory monitoring unavailable (psutil not installed)",
                timestamp=timestamp
            ))
        except Exception as e:
            metrics.append(HealthMetric(
                name="memory_usage",
                status=HealthStatus.WARNING,
                value="error",
                message=f"Memory check failed: {str(e)}",
                timestamp=timestamp
            ))
            status = HealthStatus.WARNING
        
        # Check if we have request metrics
        from openhab_mcp_server.utils.logging import get_logger
        server_logger = get_logger("mcp_server")
        if hasattr(server_logger, 'metrics'):
            metrics_summary = server_logger.metrics.get_stats_summary()
            
            # Success rate metric
            success_rate = metrics_summary.get('success_rate_percent', 100.0)
            success_status = HealthStatus.HEALTHY
            if success_rate < self.thresholds['success_rate_percent']:
                success_status = HealthStatus.WARNING
                status = HealthStatus.WARNING
            
            metrics.append(HealthMetric(
                name="success_rate",
                status=success_status,
                value=success_rate,
                message=f"Request success rate: {success_rate:.2f}%",
                timestamp=timestamp,
                threshold=self.thresholds['success_rate_percent'],
                unit="%"
            ))
            
            # Average response time
            avg_response_time = metrics_summary.get('average_response_time_ms', 0.0)
            response_status = HealthStatus.HEALTHY
            if avg_response_time > self.thresholds['response_time_ms']:
                response_status = HealthStatus.WARNING
                status = HealthStatus.WARNING
            
            metrics.append(HealthMetric(
                name="avg_response_time",
                status=response_status,
                value=avg_response_time,
                message=f"Average response time: {avg_response_time:.2f}ms",
                timestamp=timestamp,
                threshold=self.thresholds['response_time_ms'],
                unit="ms"
            ))
            
            # Total requests
            total_requests = metrics_summary.get('total_requests', 0)
            metrics.append(HealthMetric(
                name="total_requests",
                status=HealthStatus.HEALTHY,
                value=total_requests,
                message=f"Total requests processed: {total_requests}",
                timestamp=timestamp
            ))
        
        return ComponentHealth(
            component="mcp_server",
            status=status,
            metrics=metrics,
            last_check=timestamp
        )
    
    async def _check_resource_health(self) -> ComponentHealth:
        """Check system resource health."""
        metrics = []
        status = HealthStatus.HEALTHY
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Check async event loop health
        try:
            loop = asyncio.get_running_loop()
            
            # Check if loop is running
            metrics.append(HealthMetric(
                name="event_loop",
                status=HealthStatus.HEALTHY,
                value=True,
                message="Event loop is running",
                timestamp=timestamp
            ))
            
            # Check for pending tasks (basic health indicator)
            try:
                all_tasks = asyncio.all_tasks(loop)
                pending_tasks = len([t for t in all_tasks if not t.done()])
                
                task_status = HealthStatus.HEALTHY
                if pending_tasks > 50:  # Arbitrary threshold
                    task_status = HealthStatus.WARNING
                    status = HealthStatus.WARNING
                
                metrics.append(HealthMetric(
                    name="pending_tasks",
                    status=task_status,
                    value=pending_tasks,
                    message=f"Pending async tasks: {pending_tasks}",
                    timestamp=timestamp,
                    threshold=50
                ))
            except Exception as e:
                metrics.append(HealthMetric(
                    name="pending_tasks",
                    status=HealthStatus.WARNING,
                    value="error",
                    message=f"Task count check failed: {str(e)}",
                    timestamp=timestamp
                ))
                status = HealthStatus.WARNING
                
        except Exception as e:
            metrics.append(HealthMetric(
                name="event_loop",
                status=HealthStatus.CRITICAL,
                value=False,
                message=f"Event loop check failed: {str(e)}",
                timestamp=timestamp
            ))
            status = HealthStatus.CRITICAL
        
        # Check configuration health
        try:
            config_status = HealthStatus.HEALTHY
            config_issues = []
            
            if not self.config.openhab_token:
                config_issues.append("No API token configured")
                config_status = HealthStatus.WARNING
                status = HealthStatus.WARNING
            
            if not self.config.openhab_url or self.config.openhab_url == "http://localhost:8080":
                config_issues.append("Using default openHAB URL")
            
            message = "Configuration is valid"
            if config_issues:
                message = f"Configuration issues: {', '.join(config_issues)}"
            
            metrics.append(HealthMetric(
                name="configuration",
                status=config_status,
                value=len(config_issues) == 0,
                message=message,
                timestamp=timestamp
            ))
            
        except Exception as e:
            metrics.append(HealthMetric(
                name="configuration",
                status=HealthStatus.WARNING,
                value=False,
                message=f"Configuration check failed: {str(e)}",
                timestamp=timestamp
            ))
            status = HealthStatus.WARNING
        
        return ComponentHealth(
            component="system_resources",
            status=status,
            metrics=metrics,
            last_check=timestamp
        )
    
    def get_last_health_check(self) -> Optional[SystemHealth]:
        """Get the last health check result."""
        return self._last_health_check
    
    def get_health_history(self, limit: Optional[int] = None) -> List[SystemHealth]:
        """Get health check history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of SystemHealth objects
        """
        history = self._health_history.copy()
        if limit:
            history = history[-limit:]
        return history
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of system health status."""
        if not self._last_health_check:
            return {
                'status': 'unknown',
                'message': 'No health checks performed yet',
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
        
        last_check = self._last_health_check
        component_statuses = {c.component: c.status.value for c in last_check.components}
        
        # Calculate health trends if we have history
        trend = "stable"
        if len(self._health_history) >= 2:
            recent_statuses = [h.overall_status for h in self._health_history[-5:]]
            if all(s == HealthStatus.HEALTHY for s in recent_statuses[-3:]):
                trend = "improving"
            elif any(s == HealthStatus.CRITICAL for s in recent_statuses[-2:]):
                trend = "degrading"
        
        return {
            'overall_status': last_check.overall_status.value,
            'uptime_seconds': last_check.uptime_seconds,
            'component_statuses': component_statuses,
            'trend': trend,
            'last_check': last_check.timestamp,
            'checks_performed': len(self._health_history)
        }
    
    async def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get comprehensive diagnostic information."""
        # Perform fresh health check
        health = await self.check_system_health()
        
        # Get configuration info (sanitized)
        config_info = {
            'openhab_url': self.config.openhab_url,
            'timeout': self.config.timeout,
            'log_level': self.config.log_level,
            'has_token': bool(self.config.openhab_token)
        }
        
        # Get request metrics if available
        request_metrics = {}
        try:
            from openhab_mcp_server.utils.logging import get_logger
            server_logger = get_logger("mcp_server")
            if hasattr(server_logger, 'metrics'):
                request_metrics = server_logger.metrics.get_stats_summary()
        except Exception:
            pass
        
        return {
            'health': health.to_dict(),
            'configuration': config_info,
            'request_metrics': request_metrics,
            'system_info': {
                'start_time': self.start_time,
                'uptime_seconds': time.time() - self.start_time,
                'health_checks_performed': len(self._health_history)
            }
        }


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker(config: Optional[Config] = None) -> HealthChecker:
    """Get or create global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker(config)
    return _health_checker