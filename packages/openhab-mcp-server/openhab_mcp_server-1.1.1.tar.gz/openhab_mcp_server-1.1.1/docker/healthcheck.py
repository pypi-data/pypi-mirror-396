#!/usr/bin/env python3
"""
Health check script for the openHAB MCP Server Docker container.

This script performs basic health checks to ensure the container is running
properly and can be used by container orchestration systems.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

import aiohttp


class HealthChecker:
    """Health check implementation for the MCP server container."""
    
    def __init__(self):
        """Initialize the health checker with configuration from environment."""
        self.openhab_url = os.getenv("OPENHAB_URL", "http://localhost:8080")
        self.openhab_token = os.getenv("OPENHAB_TOKEN")
        self.timeout = int(os.getenv("OPENHAB_TIMEOUT", "10"))
        self.health_port = int(os.getenv("HEALTH_CHECK_PORT", "8081"))
        self.start_time = time.time()
        
    async def check_openhab_connection(self) -> Dict[str, Any]:
        """Check connection to openHAB server.
        
        Returns:
            Dictionary with check results
        """
        check_result = {
            "name": "openhab_connection",
            "status": "unknown",
            "message": "",
            "response_time": None
        }
        
        if not self.openhab_token:
            check_result.update({
                "status": "warning",
                "message": "No openHAB token configured - connection test skipped"
            })
            return check_result
        
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.openhab_token}"}
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Test basic connectivity with system info endpoint
                url = f"{self.openhab_url}/rest/systeminfo"
                async with session.get(url, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        check_result.update({
                            "status": "healthy",
                            "message": "openHAB connection successful",
                            "response_time": round(response_time * 1000, 2)  # ms
                        })
                    else:
                        check_result.update({
                            "status": "unhealthy",
                            "message": f"openHAB returned status {response.status}",
                            "response_time": round(response_time * 1000, 2)
                        })
                        
        except asyncio.TimeoutError:
            check_result.update({
                "status": "unhealthy",
                "message": f"Connection timeout after {self.timeout}s"
            })
        except aiohttp.ClientError as e:
            check_result.update({
                "status": "unhealthy",
                "message": f"Connection error: {str(e)}"
            })
        except Exception as e:
            check_result.update({
                "status": "unhealthy",
                "message": f"Unexpected error: {str(e)}"
            })
            
        return check_result
    
    def check_filesystem_access(self) -> Dict[str, Any]:
        """Check filesystem access for configuration and logs.
        
        Returns:
            Dictionary with check results
        """
        check_result = {
            "name": "filesystem_access",
            "status": "unknown",
            "message": "",
            "details": {}
        }
        
        paths_to_check = {
            "config": "/app/config",
            "logs": "/app/logs", 
            "data": "/app/data"
        }
        
        all_accessible = True
        details = {}
        
        for name, path in paths_to_check.items():
            path_obj = Path(path)
            try:
                # Check if directory exists and is accessible
                if path_obj.exists():
                    if path_obj.is_dir():
                        # Try to create a test file to verify write access
                        test_file = path_obj / ".health_check"
                        test_file.touch()
                        test_file.unlink()  # Clean up
                        details[name] = "accessible"
                    else:
                        details[name] = "exists but not a directory"
                        all_accessible = False
                else:
                    details[name] = "does not exist"
                    all_accessible = False
                    
            except PermissionError:
                details[name] = "permission denied"
                all_accessible = False
            except Exception as e:
                details[name] = f"error: {str(e)}"
                all_accessible = False
        
        check_result["details"] = details
        
        if all_accessible:
            check_result.update({
                "status": "healthy",
                "message": "All filesystem paths accessible"
            })
        else:
            check_result.update({
                "status": "unhealthy", 
                "message": "Some filesystem paths not accessible"
            })
            
        return check_result
    
    def check_process_health(self) -> Dict[str, Any]:
        """Check basic process health metrics.
        
        Returns:
            Dictionary with check results
        """
        check_result = {
            "name": "process_health",
            "status": "healthy",
            "message": "Process running normally",
            "uptime": round(time.time() - self.start_time, 2),
            "pid": os.getpid()
        }
        
        return check_result
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return consolidated results.
        
        Returns:
            Dictionary with overall health status and individual check results
        """
        checks = []
        
        # Run all health checks
        checks.append(await self.check_openhab_connection())
        checks.append(self.check_filesystem_access())
        checks.append(self.check_process_health())
        
        # Determine overall health status
        unhealthy_checks = [c for c in checks if c["status"] == "unhealthy"]
        warning_checks = [c for c in checks if c["status"] == "warning"]
        
        if unhealthy_checks:
            overall_status = "unhealthy"
            status_message = f"{len(unhealthy_checks)} check(s) failed"
        elif warning_checks:
            overall_status = "warning"
            status_message = f"{len(warning_checks)} check(s) have warnings"
        else:
            overall_status = "healthy"
            status_message = "All checks passed"
        
        return {
            "status": overall_status,
            "message": status_message,
            "timestamp": time.time(),
            "uptime": round(time.time() - self.start_time, 2),
            "checks": checks
        }


async def main() -> None:
    """Main health check entry point."""
    checker = HealthChecker()
    
    try:
        # Run health checks
        results = await checker.run_all_checks()
        
        # Output results as JSON for container orchestration
        print(json.dumps(results, indent=2))
        
        # Exit with appropriate code
        if results["status"] == "unhealthy":
            sys.exit(1)
        elif results["status"] == "warning":
            # Warnings don't fail health check but are logged
            sys.exit(0)
        else:
            sys.exit(0)
            
    except Exception as e:
        # Handle unexpected errors
        error_result = {
            "status": "unhealthy",
            "message": f"Health check failed with error: {str(e)}",
            "timestamp": time.time(),
            "error": True
        }
        
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())