"""
Main MCP server implementation for openHAB integration.

This module implements the OpenHABMCPServer class that serves as the main
entry point for the MCP server, handling tool and resource registration,
server initialization, and shutdown procedures.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    ServerCapabilities,
)

from openhab_mcp_server.utils.config import Config, get_config
from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError
from openhab_mcp_server.utils.logging import get_logger, configure_logging, LogCategory
from openhab_mcp_server.utils.diagnostics import get_health_checker, HealthChecker


# Configure structured logging
logger = logging.getLogger(__name__)
structured_logger = get_logger("mcp_server")


class OpenHABMCPServer:
    """Main MCP server implementation for openHAB integration."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the MCP server.
        
        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or get_config()
        self.server = Server("openhab-mcp-server")
        self.openhab_client: Optional[OpenHABClient] = None
        self.health_checker: Optional[HealthChecker] = None
        
        # Configure structured logging
        configure_logging(
            level=self.config.log_level,
            format_json=False,
            include_structured_data=True
        )
        
        structured_logger.info(
            "Initializing openHAB MCP Server",
            category=LogCategory.SYSTEM,
            metadata={
                "openhab_url": self.config.openhab_url,
                "timeout_seconds": self.config.timeout,
                "log_level": self.config.log_level
            }
        )
    
    async def start(self) -> None:
        """Initialize and start the MCP server."""
        structured_logger.info("Starting openHAB MCP Server...", category=LogCategory.SYSTEM)
        
        try:
            # Initialize openHAB client
            self.openhab_client = OpenHABClient(self.config)
            
            # Initialize health checker
            self.health_checker = get_health_checker(self.config)
            
            # Test connection to openHAB
            await self._test_connection()
            
            # Register tools and resources
            await self.register_tools()
            await self.register_resources()
            
            structured_logger.info(
                "openHAB MCP Server started successfully",
                category=LogCategory.SYSTEM,
                success=True
            )
            
        except Exception as e:
            structured_logger.error(
                f"Failed to start server: {e}",
                category=LogCategory.SYSTEM,
                success=False,
                error_type=type(e).__name__
            )
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the MCP server and cleanup resources."""
        structured_logger.info("Shutting down openHAB MCP Server...", category=LogCategory.SYSTEM)
        
        try:
            if self.openhab_client:
                await self.openhab_client.close()
                self.openhab_client = None
            
            structured_logger.info(
                "openHAB MCP Server shutdown complete",
                category=LogCategory.SYSTEM,
                success=True
            )
            
        except Exception as e:
            structured_logger.error(
                f"Error during shutdown: {e}",
                category=LogCategory.SYSTEM,
                success=False,
                error_type=type(e).__name__
            )
            raise
    
    async def _test_connection(self) -> None:
        """Test connection to openHAB server."""
        if not self.openhab_client:
            raise RuntimeError("openHAB client not initialized")
        
        try:
            structured_logger.info("Testing connection to openHAB...", category=LogCategory.SYSTEM)
            async with self.openhab_client:
                system_info = await self.openhab_client.get_system_info()
                version = system_info.get('version', 'unknown')
                structured_logger.info(
                    f"Connected to openHAB {version}",
                    category=LogCategory.SYSTEM,
                    success=True,
                    metadata={"openhab_version": version, "system_info": system_info}
                )
                
        except OpenHABError as e:
            structured_logger.error(
                f"Failed to connect to openHAB: {e}",
                category=LogCategory.SYSTEM,
                success=False,
                error_type=type(e).__name__
            )
            raise
    
    async def register_tools(self) -> None:
        """Register all available MCP tools."""
        logger.info("Registering MCP tools...")
        
        # Item control tools
        await self._register_item_tools()
        
        # Thing management tools  
        await self._register_thing_tools()
        
        # Rule operations tools
        await self._register_rule_tools()
        
        # Addon management tools
        await self._register_addon_tools()
        
        # System tools
        await self._register_system_tools()
        
        # Diagnostic tools
        await self._register_diagnostic_tools()
        
        # Example and documentation tools
        await self._register_example_tools()
        
        # Script execution tools
        await self._register_script_tools()
        
        # Link management tools
        await self._register_link_tools()
        
        # UI management tools
        await self._register_ui_tools()
        
        # Transformation management tools
        await self._register_transformation_tools()
        
        logger.info("MCP tools registered successfully")
    
    async def register_resources(self) -> None:
        """Register all available MCP resources."""
        logger.info("Registering MCP resources...")
        
        # Documentation resources
        await self._register_documentation_resources()
        
        # System state resources
        await self._register_system_state_resources()
        
        # Diagnostic resources
        await self._register_diagnostic_resources()
        
        logger.info("MCP resources registered successfully")
    
    async def _register_item_tools(self) -> None:
        """Register item control tools."""
        from openhab_mcp_server.tools.items import ItemStateTool, ItemCommandTool, ItemListTool
        
        # Initialize tool instances
        item_state_tool = ItemStateTool(self.config)
        item_command_tool = ItemCommandTool(self.config)
        item_list_tool = ItemListTool(self.config)
        
        @self.server.call_tool()
        async def get_item_state(name: str) -> List[TextContent]:
            """Get current state of an openHAB item.
            
            Args:
                name: Name of the openHAB item
                
            Returns:
                Current state information for the item
            """
            return await item_state_tool.execute(name)
        
        @self.server.call_tool()
        async def send_item_command(name: str, command: str) -> List[TextContent]:
            """Send a command to an openHAB item.
            
            Args:
                name: Name of the openHAB item
                command: Command to send to the item
                
            Returns:
                Result of the command execution
            """
            return await item_command_tool.execute(name, command)
        
        @self.server.call_tool()
        async def list_items(item_type: Optional[str] = None) -> List[TextContent]:
            """List all openHAB items or items of a specific type.
            
            Args:
                item_type: Optional filter by item type (e.g., 'Switch', 'Dimmer')
                
            Returns:
                List of items with their basic information
            """
            return await item_list_tool.execute(item_type)
    
    async def _register_thing_tools(self) -> None:
        """Register thing management tools."""
        from openhab_mcp_server.tools.things import ThingStatusTool, ThingConfigTool, ThingDiscoveryTool
        
        # Initialize tool instances
        thing_status_tool = ThingStatusTool(self.config)
        thing_config_tool = ThingConfigTool(self.config)
        thing_discovery_tool = ThingDiscoveryTool(self.config)
        
        @self.server.call_tool()
        async def get_thing_status(uid: str) -> List[TextContent]:
            """Get status and configuration of an openHAB thing.
            
            Args:
                uid: UID of the openHAB thing
                
            Returns:
                Thing status and configuration information
            """
            return await thing_status_tool.execute(uid)
        
        @self.server.call_tool()
        async def update_thing_config(uid: str, configuration: Dict[str, Any]) -> List[TextContent]:
            """Update thing configuration parameters.
            
            Args:
                uid: UID of the openHAB thing
                configuration: Configuration parameters to update
                
            Returns:
                Result of the configuration update
            """
            return await thing_config_tool.execute(uid, configuration)
        
        @self.server.call_tool()
        async def discover_things(binding_id: str) -> List[TextContent]:
            """Trigger discovery for new things.
            
            Args:
                binding_id: ID of the binding to discover for
                
            Returns:
                Discovery results with found devices
            """
            return await thing_discovery_tool.execute(binding_id)
        
        @self.server.call_tool()
        async def list_things() -> List[TextContent]:
            """List all openHAB things.
            
            Returns:
                List of things with their basic information
            """
            if not self.openhab_client:
                raise RuntimeError("openHAB client not initialized")
            
            try:
                async with self.openhab_client:
                    things = await self.openhab_client.get_things()
                    
                    if not things:
                        return [TextContent(
                            type="text",
                            text="No things found"
                        )]
                    
                    thing_list = []
                    for thing in things:
                        status = thing.get('statusInfo', {}).get('status', 'UNKNOWN')
                        thing_info = (
                            f"• {thing.get('UID', 'Unknown')} - "
                            f"Status: {status} - "
                            f"{thing.get('label', 'No label')}"
                        )
                        thing_list.append(thing_info)
                    
                    return [TextContent(
                        type="text",
                        text=f"Found {len(things)} things:\n" + "\n".join(thing_list)
                    )]
                    
            except OpenHABError as e:
                logger.error(f"Error listing things: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error listing things: {e}"
                )]
    
    async def _register_rule_tools(self) -> None:
        """Register rule operations tools."""
        from openhab_mcp_server.tools.rules import RuleListTool, RuleExecuteTool, RuleCreateTool
        
        # Initialize tool instances
        rule_list_tool = RuleListTool(self.config)
        rule_execute_tool = RuleExecuteTool(self.config)
        rule_create_tool = RuleCreateTool(self.config)
        
        @self.server.call_tool()
        async def list_rules(status_filter: Optional[str] = None) -> List[TextContent]:
            """List all openHAB automation rules.
            
            Args:
                status_filter: Optional filter by rule status (e.g., 'ENABLED', 'DISABLED')
                
            Returns:
                List of rules with their basic information
            """
            return await rule_list_tool.execute(status_filter)
        
        @self.server.call_tool()
        async def execute_rule(uid: str) -> List[TextContent]:
            """Manually execute an openHAB rule.
            
            Args:
                uid: UID of the rule to execute
                
            Returns:
                Result of the rule execution
            """
            return await rule_execute_tool.execute(uid)
        
        @self.server.call_tool()
        async def create_rule(rule_definition: Dict[str, Any]) -> List[TextContent]:
            """Create a new automation rule.
            
            Args:
                rule_definition: Rule definition including name, triggers, conditions, actions
                
            Returns:
                Result of the rule creation
            """
            return await rule_create_tool.execute(rule_definition)
    
    async def _register_addon_tools(self) -> None:
        """Register addon management tools."""
        from openhab_mcp_server.tools.addons import AddonListTool, AddonInstallTool, AddonUninstallTool, AddonConfigTool
        
        # Initialize tool instances
        addon_list_tool = AddonListTool(self.config)
        addon_install_tool = AddonInstallTool(self.config)
        addon_uninstall_tool = AddonUninstallTool(self.config)
        addon_config_tool = AddonConfigTool(self.config)
        
        @self.server.call_tool()
        async def list_addons(
            filter_type: Optional[str] = None,
            installed_only: Optional[bool] = False,
            available_only: Optional[bool] = False
        ) -> List[TextContent]:
            """List available and installed openHAB addons.
            
            Args:
                filter_type: Filter addons by type (binding, transformation, persistence, automation, voice, ui, misc, io)
                installed_only: If true, only return installed addons
                available_only: If true, only return available (not installed) addons
                
            Returns:
                List of addons with their information
            """
            from openhab_mcp_server.tools.addons import AddonListParams
            params = AddonListParams(
                filter_type=filter_type,
                installed_only=installed_only,
                available_only=available_only
            )
            return await addon_list_tool.execute(params)
        
        @self.server.call_tool()
        async def install_addon(addon_id: str) -> List[TextContent]:
            """Install an openHAB addon from the addon registry.
            
            Args:
                addon_id: ID of the addon to install
                
            Returns:
                Result of the addon installation
            """
            from openhab_mcp_server.tools.addons import AddonInstallParams
            params = AddonInstallParams(addon_id=addon_id)
            return await addon_install_tool.execute(params)
        
        @self.server.call_tool()
        async def uninstall_addon(addon_id: str) -> List[TextContent]:
            """Uninstall an installed openHAB addon.
            
            Args:
                addon_id: ID of the addon to uninstall
                
            Returns:
                Result of the addon uninstallation
            """
            from openhab_mcp_server.tools.addons import AddonUninstallParams
            params = AddonUninstallParams(addon_id=addon_id)
            return await addon_uninstall_tool.execute(params)
        
        @self.server.call_tool()
        async def configure_addon(addon_id: str, config: Dict[str, Any]) -> List[TextContent]:
            """Update configuration parameters for an openHAB addon.
            
            Args:
                addon_id: ID of the addon to configure
                config: Configuration parameters to update
                
            Returns:
                Result of the addon configuration update
            """
            from openhab_mcp_server.tools.addons import AddonConfigParams
            params = AddonConfigParams(addon_id=addon_id, config=config)
            return await addon_config_tool.execute(params)
    
    async def _register_system_tools(self) -> None:
        """Register system information tools."""
        
        @self.server.call_tool()
        async def get_system_info() -> List[TextContent]:
            """Get openHAB system information.
            
            Returns:
                System information including version and configuration
            """
            if not self.openhab_client:
                raise RuntimeError("openHAB client not initialized")
            
            try:
                async with self.openhab_client:
                    system_info = await self.openhab_client.get_system_info()
                    
                    return [TextContent(
                        type="text",
                        text=f"openHAB System Information:\n"
                             f"Version: {system_info.get('version', 'Unknown')}\n"
                             f"Build: {system_info.get('buildString', 'Unknown')}\n"
                             f"Locale: {system_info.get('locale', 'Unknown')}\n"
                             f"Start Level: {system_info.get('startLevel', 'Unknown')}"
                    )]
                    
            except OpenHABError as e:
                logger.error(f"Error getting system info: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error retrieving system information: {e}"
                )]
        
        @self.server.call_tool()
        async def list_bindings() -> List[TextContent]:
            """List all installed openHAB bindings.
            
            Returns:
                List of installed bindings
            """
            if not self.openhab_client:
                raise RuntimeError("openHAB client not initialized")
            
            try:
                async with self.openhab_client:
                    bindings = await self.openhab_client.get_bindings()
                    
                    if not bindings:
                        return [TextContent(
                            type="text",
                            text="No bindings found"
                        )]
                    
                    binding_list = []
                    for binding in bindings:
                        binding_info = (
                            f"• {binding.get('id', 'Unknown')} - "
                            f"{binding.get('name', 'No name')}"
                        )
                        if binding.get('description'):
                            binding_info += f" - {binding['description']}"
                        binding_list.append(binding_info)
                    
                    return [TextContent(
                        type="text",
                        text=f"Found {len(bindings)} bindings:\n" + "\n".join(binding_list)
                    )]
                    
            except OpenHABError as e:
                logger.error(f"Error listing bindings: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error listing bindings: {e}"
                )]
    
    async def _register_diagnostic_tools(self) -> None:
        """Register diagnostic and health monitoring tools."""
        
        @self.server.call_tool()
        async def get_health_status() -> List[TextContent]:
            """Get current system health status.
            
            Returns:
                Comprehensive health status report
            """
            if not self.health_checker:
                return [TextContent(
                    type="text",
                    text="Health checker not initialized"
                )]
            
            try:
                health = await self.health_checker.check_system_health()
                
                # Format health report
                report_lines = [
                    f"System Health Status: {health.overall_status.value.upper()}",
                    f"Uptime: {health.uptime_seconds:.2f} seconds",
                    f"Last Check: {health.timestamp}",
                    "",
                    "Component Status:"
                ]
                
                for component in health.components:
                    report_lines.append(f"  {component.component}: {component.status.value.upper()}")
                    if component.error_message:
                        report_lines.append(f"    Error: {component.error_message}")
                    
                    for metric in component.metrics:
                        status_indicator = "✓" if metric.status.value == "healthy" else "⚠" if metric.status.value == "warning" else "✗"
                        report_lines.append(f"    {status_indicator} {metric.name}: {metric.message}")
                
                return [TextContent(
                    type="text",
                    text="\n".join(report_lines)
                )]
                
            except Exception as e:
                structured_logger.error(
                    f"Health check failed: {e}",
                    category=LogCategory.HEALTH,
                    error_type=type(e).__name__
                )
                return [TextContent(
                    type="text",
                    text=f"Health check failed: {e}"
                )]
        
        @self.server.call_tool()
        async def get_diagnostics() -> List[TextContent]:
            """Get comprehensive diagnostic information.
            
            Returns:
                Detailed diagnostic report including metrics and configuration
            """
            if not self.health_checker:
                return [TextContent(
                    type="text",
                    text="Health checker not initialized"
                )]
            
            try:
                diagnostics = await self.health_checker.get_diagnostic_info()
                
                # Format diagnostic report
                report_lines = [
                    "=== openHAB MCP Server Diagnostics ===",
                    "",
                    f"Overall Status: {diagnostics['health']['overall_status'].upper()}",
                    f"Uptime: {diagnostics['system_info']['uptime_seconds']:.2f} seconds",
                    "",
                    "Configuration:",
                    f"  openHAB URL: {diagnostics['configuration']['openhab_url']}",
                    f"  Timeout: {diagnostics['configuration']['timeout']}s",
                    f"  Log Level: {diagnostics['configuration']['log_level']}",
                    f"  Has API Token: {diagnostics['configuration']['has_token']}",
                    ""
                ]
                
                # Request metrics
                if diagnostics['request_metrics']:
                    metrics = diagnostics['request_metrics']
                    report_lines.extend([
                        "Request Metrics:",
                        f"  Total Requests: {metrics.get('total_requests', 0)}",
                        f"  Success Rate: {metrics.get('success_rate_percent', 0):.2f}%",
                        f"  Average Response Time: {metrics.get('average_response_time_ms', 0):.2f}ms",
                        f"  Failed Requests: {metrics.get('failed_requests', 0)}",
                        ""
                    ])
                    
                    if metrics.get('error_counts'):
                        report_lines.append("Error Breakdown:")
                        for error_type, count in metrics['error_counts'].items():
                            report_lines.append(f"  {error_type}: {count}")
                        report_lines.append("")
                    
                    if metrics.get('endpoint_stats'):
                        report_lines.append("Endpoint Statistics:")
                        for endpoint, stats in metrics['endpoint_stats'].items():
                            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                            report_lines.append(
                                f"  {endpoint}: {stats['total']} requests, "
                                f"{success_rate:.1f}% success, "
                                f"{stats['avg_duration_ms']:.2f}ms avg"
                            )
                        report_lines.append("")
                
                # Component details
                report_lines.append("Component Details:")
                for component in diagnostics['health']['components']:
                    report_lines.append(f"  {component['component']}: {component['status'].upper()}")
                    for metric in component['metrics']:
                        report_lines.append(f"    • {metric['name']}: {metric['message']}")
                
                return [TextContent(
                    type="text",
                    text="\n".join(report_lines)
                )]
                
            except Exception as e:
                structured_logger.error(
                    f"Diagnostics failed: {e}",
                    category=LogCategory.HEALTH,
                    error_type=type(e).__name__
                )
                return [TextContent(
                    type="text",
                    text=f"Diagnostics failed: {e}"
                )]
        
        @self.server.call_tool()
        async def get_metrics_summary() -> List[TextContent]:
            """Get request metrics summary.
            
            Returns:
                Summary of request metrics and performance data
            """
            try:
                # Get metrics from structured logger
                server_logger = get_logger("mcp_server")
                if hasattr(server_logger, 'metrics'):
                    metrics = server_logger.metrics.get_stats_summary()
                    
                    report_lines = [
                        "=== Request Metrics Summary ===",
                        "",
                        f"Total Requests: {metrics.get('total_requests', 0)}",
                        f"Successful Requests: {metrics.get('successful_requests', 0)}",
                        f"Failed Requests: {metrics.get('failed_requests', 0)}",
                        f"Success Rate: {metrics.get('success_rate_percent', 0):.2f}%",
                        f"Average Response Time: {metrics.get('average_response_time_ms', 0):.2f}ms",
                        ""
                    ]
                    
                    if metrics.get('error_counts'):
                        report_lines.append("Error Types:")
                        for error_type, count in metrics['error_counts'].items():
                            report_lines.append(f"  {error_type}: {count}")
                        report_lines.append("")
                    
                    if metrics.get('endpoint_stats'):
                        report_lines.append("Per-Endpoint Statistics:")
                        for endpoint, stats in metrics['endpoint_stats'].items():
                            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
                            report_lines.extend([
                                f"  {endpoint}:",
                                f"    Total: {stats['total']}",
                                f"    Success: {stats['success']} ({success_rate:.1f}%)",
                                f"    Failed: {stats['failed']}",
                                f"    Avg Duration: {stats['avg_duration_ms']:.2f}ms"
                            ])
                    
                    return [TextContent(
                        type="text",
                        text="\n".join(report_lines)
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text="No metrics available - structured logging not initialized"
                    )]
                    
            except Exception as e:
                structured_logger.error(
                    f"Metrics summary failed: {e}",
                    category=LogCategory.PERFORMANCE,
                    error_type=type(e).__name__
                )
                return [TextContent(
                    type="text",
                    text=f"Metrics summary failed: {e}"
                )]
    
    async def _register_example_tools(self) -> None:
        """Register example and documentation tools."""
        from openhab_mcp_server.tools.examples import OperationExamplesTool, APIDocumentationTool
        
        # Initialize tool instances
        examples_tool = OperationExamplesTool(self.config)
        api_docs_tool = APIDocumentationTool(self.config)
        
        @self.server.call_tool()
        async def get_operation_examples(operation_type: Optional[str] = None) -> List[TextContent]:
            """Get examples for common openHAB operations.
            
            Args:
                operation_type: Optional filter for specific operation type
                    (item_control, item_monitoring, thing_management, rule_automation, system_monitoring)
                
            Returns:
                Examples for the specified operation type or all operations
            """
            return await examples_tool.execute(operation_type)
        
        @self.server.call_tool()
        async def get_api_documentation(section: Optional[str] = None) -> List[TextContent]:
            """Get API documentation with usage patterns.
            
            Args:
                section: Optional filter for specific documentation section
                    (tools, resources, common_workflows)
                
            Returns:
                API documentation for the specified section or overview of all sections
            """
            return await api_docs_tool.execute(section)
    
    async def _register_script_tools(self) -> None:
        """Register script execution tools."""
        from openhab_mcp_server.tools.scripts import ScriptExecuteTool, ScriptValidateTool
        
        # Initialize tool instances
        script_execute_tool = ScriptExecuteTool(self.config, self.openhab_client)
        script_validate_tool = ScriptValidateTool(self.config)
        
        @self.server.call_tool()
        async def execute_script(script_code: str, context: Optional[Dict[str, Any]] = None) -> List[TextContent]:
            """Execute Python script in secure sandbox environment.
            
            Args:
                script_code: Python script code to execute
                context: Optional context variables to make available to script
                
            Returns:
                Script execution results including output, errors, and execution time
            """
            return await script_execute_tool.execute(script_code, context)
        
        @self.server.call_tool()
        async def validate_script(script_code: str) -> List[TextContent]:
            """Validate Python script syntax and security constraints.
            
            Args:
                script_code: Python script code to validate
                
            Returns:
                Script validation results including syntax errors and security violations
            """
            return await script_validate_tool.execute(script_code)
    
    async def _register_link_tools(self) -> None:
        """Register link management tools."""
        from openhab_mcp_server.tools.links import LinkListTool, LinkCreateTool, LinkUpdateTool, LinkDeleteTool
        
        # Initialize tool instances
        link_list_tool = LinkListTool()
        link_create_tool = LinkCreateTool()
        link_update_tool = LinkUpdateTool()
        link_delete_tool = LinkDeleteTool()
        
        @self.server.call_tool()
        async def list_links(item_name: Optional[str] = None, channel_uid: Optional[str] = None) -> List[TextContent]:
            """List item links with optional filtering by item name or channel UID.
            
            Args:
                item_name: Optional item name to filter links
                channel_uid: Optional channel UID to filter links
                
            Returns:
                List of links matching the filter criteria
            """
            return await link_list_tool.execute(item_name, channel_uid)
        
        @self.server.call_tool()
        async def create_link(item_name: str, channel_uid: str, configuration: Optional[Dict[str, Any]] = None) -> List[TextContent]:
            """Create a new link between an item and a channel.
            
            Args:
                item_name: Name of the item to link
                channel_uid: UID of the channel to link (format: thing_uid:channel_id)
                configuration: Optional configuration parameters for the link
                
            Returns:
                Result of the link creation operation
            """
            return await link_create_tool.execute(item_name, channel_uid, configuration)
        
        @self.server.call_tool()
        async def update_link(item_name: str, channel_uid: str, configuration: Dict[str, Any]) -> List[TextContent]:
            """Update configuration of an existing link between an item and channel.
            
            Args:
                item_name: Name of the linked item
                channel_uid: UID of the linked channel
                configuration: New configuration parameters for the link
                
            Returns:
                Result of the link configuration update
            """
            return await link_update_tool.execute(item_name, channel_uid, configuration)
        
        @self.server.call_tool()
        async def delete_link(item_name: str, channel_uid: str) -> List[TextContent]:
            """Delete a link between an item and channel.
            
            Args:
                item_name: Name of the linked item
                channel_uid: UID of the linked channel
                
            Returns:
                Result of the link deletion operation
            """
            return await link_delete_tool.execute(item_name, channel_uid)
    
    async def _register_ui_tools(self) -> None:
        """Register Main UI management tools."""
        from openhab_mcp_server.tools.ui import (
            UIPageListTool, UIPageCreateTool, UIWidgetUpdateTool,
            UILayoutManageTool, UIConfigExportTool
        )
        
        # Initialize tool instances
        ui_page_list_tool = UIPageListTool(self.openhab_client)
        ui_page_create_tool = UIPageCreateTool(self.openhab_client)
        ui_widget_update_tool = UIWidgetUpdateTool(self.openhab_client)
        ui_layout_manage_tool = UILayoutManageTool(self.openhab_client)
        ui_config_export_tool = UIConfigExportTool(self.openhab_client)
        
        @self.server.call_tool()
        async def list_ui_pages(include_widgets: bool = True) -> List[TextContent]:
            """List all Main UI pages with their configuration and widget structure.
            
            Args:
                include_widgets: Whether to include widget information in the response
                
            Returns:
                List of UI pages with configuration details
            """
            return await ui_page_list_tool.execute(include_widgets)
        
        @self.server.call_tool()
        async def create_ui_page(page_config: Dict[str, Any]) -> List[TextContent]:
            """Create a new Main UI page with widget layout validation.
            
            Args:
                page_config: Complete page configuration including name, layout, and widgets
                
            Returns:
                Result of the page creation operation
            """
            return await ui_page_create_tool.execute(page_config)
        
        @self.server.call_tool()
        async def update_ui_widget(page_id: str, widget_id: str, properties: Dict[str, Any]) -> List[TextContent]:
            """Update UI widget properties and refresh UI display.
            
            Args:
                page_id: ID of the page containing the widget
                widget_id: ID of the widget to update
                properties: New widget properties to apply
                
            Returns:
                Result of the widget update operation
            """
            return await ui_widget_update_tool.execute(page_id, widget_id, properties)
        
        @self.server.call_tool()
        async def manage_ui_layout(page_id: str, layout_config: Dict[str, Any]) -> List[TextContent]:
            """Manage UI layouts and responsive design settings.
            
            Args:
                page_id: ID of the page to manage layout for
                layout_config: Layout configuration including responsive settings
                
            Returns:
                Result of the layout management operation
            """
            return await ui_layout_manage_tool.execute(page_id, layout_config)
        
        @self.server.call_tool()
        async def export_ui_config(page_ids: Optional[List[str]] = None, include_global_settings: bool = True) -> List[TextContent]:
            """Export UI configuration for backup or sharing.
            
            Args:
                page_ids: List of page IDs to export (if None, exports all pages)
                include_global_settings: Whether to include global UI settings in the export
                
            Returns:
                Exported UI configuration data
            """
            return await ui_config_export_tool.execute(page_ids, include_global_settings)
    
    async def _register_transformation_tools(self) -> None:
        """Register transformation management tools."""
        from openhab_mcp_server.tools.transformations import (
            TransformationListTool, TransformationCreateTool, TransformationTestTool,
            TransformationUpdateTool, TransformationUsageTool
        )
        
        # Initialize tool instances
        transformation_list_tool = TransformationListTool()
        transformation_create_tool = TransformationCreateTool()
        transformation_test_tool = TransformationTestTool()
        transformation_update_tool = TransformationUpdateTool()
        transformation_usage_tool = TransformationUsageTool()
        
        @self.server.call_tool()
        async def list_transformations() -> List[TextContent]:
            """List all installed transformation addons with their capabilities.
            
            Returns:
                List of available transformation addons and their configuration
            """
            return await transformation_list_tool.execute()
        
        @self.server.call_tool()
        async def create_transformation(transformation_type: str, configuration: Dict[str, Any]) -> List[TextContent]:
            """Create and configure a new transformation.
            
            Args:
                transformation_type: Type of transformation (MAP, REGEX, JSONPATH, etc.)
                configuration: Configuration parameters for the transformation
                
            Returns:
                Result of the transformation creation operation
            """
            return await transformation_create_tool.execute(transformation_type, configuration)
        
        @self.server.call_tool()
        async def test_transformation(transformation_id: str, sample_data: str) -> List[TextContent]:
            """Test a transformation with sample data.
            
            Args:
                transformation_id: ID of the transformation to test
                sample_data: Sample input data for testing the transformation
                
            Returns:
                Test results including input, output, and execution time
            """
            return await transformation_test_tool.execute(transformation_id, sample_data)
        
        @self.server.call_tool()
        async def update_transformation(transformation_id: str, configuration: Dict[str, Any]) -> List[TextContent]:
            """Update transformation configuration parameters.
            
            Args:
                transformation_id: ID of the transformation to update
                configuration: New configuration parameters for the transformation
                
            Returns:
                Result of the transformation configuration update
            """
            return await transformation_update_tool.execute(transformation_id, configuration)
        
        @self.server.call_tool()
        async def get_transformation_usage(transformation_id: str) -> List[TextContent]:
            """Query where a transformation is used in the system.
            
            Args:
                transformation_id: ID of the transformation to query usage for
                
            Returns:
                List of locations where the transformation is applied
            """
            return await transformation_usage_tool.execute(transformation_id)
    
    async def _register_documentation_resources(self) -> None:
        """Register documentation resources."""
        from openhab_mcp_server.resources.openhab import DocumentationResource
        
        # Initialize resource instance
        doc_resource = DocumentationResource()
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available documentation resources."""
            return [
                Resource(
                    uri="openhab://docs/setup",
                    name="openHAB Setup Guide",
                    description="Complete setup and installation guide for openHAB",
                    mimeType="text/plain"
                ),
                Resource(
                    uri="openhab://docs/configuration", 
                    name="Configuration Guide",
                    description="Guide for configuring items, things, and rules",
                    mimeType="text/plain"
                ),
                Resource(
                    uri="openhab://docs/troubleshooting",
                    name="Troubleshooting Guide", 
                    description="Common issues and troubleshooting steps",
                    mimeType="text/plain"
                ),
                Resource(
                    uri="openhab://docs/search",
                    name="Documentation Search",
                    description="Search openHAB documentation for specific topics",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read documentation resource content."""
            
            if uri == "openhab://docs/setup":
                return """openHAB Setup Guide
                
1. Installation
   - Download openHAB from https://www.openhab.org/download/
   - Extract to desired directory
   - Run start.sh (Linux/Mac) or start.bat (Windows)

2. Initial Configuration
   - Access web interface at http://localhost:8080
   - Complete initial setup wizard
   - Configure authentication if needed

3. Basic Configuration
   - Add bindings for your devices
   - Discover and add things
   - Create items for device channels
   - Set up basic rules for automation

For detailed instructions, visit: https://www.openhab.org/docs/installation/
"""
            elif uri == "openhab://docs/configuration":
                return """Configuration Guide

1. Things
   - Represent physical devices or services
   - Configured through UI or text files
   - Provide channels for item linking

2. Items
   - Virtual representations of device features
   - Link to thing channels
   - Have types like Switch, Dimmer, Number

3. Rules
   - Automation logic
   - Triggered by events, time, or conditions
   - Can control items and execute actions

For detailed configuration guides, visit: https://www.openhab.org/docs/configuration/
"""
            elif uri == "openhab://docs/troubleshooting":
                return """Troubleshooting Guide

Common Issues:

1. Things Offline
   - Check network connectivity
   - Verify device configuration
   - Review binding documentation

2. Items Not Updating
   - Ensure item is linked to channel
   - Check thing status
   - Review logs for errors

3. Rules Not Executing
   - Verify rule is enabled
   - Check trigger conditions
   - Review rule syntax

For comprehensive troubleshooting, visit: https://www.openhab.org/docs/administration/
"""
            elif uri == "openhab://docs/search":
                # Return search functionality as JSON
                guides = doc_resource.get_setup_guides()
                troubleshooting = doc_resource.get_troubleshooting_steps()
                
                search_data = {
                    "setup_guides": guides,
                    "troubleshooting_steps": troubleshooting,
                    "search_help": "Use the documentation search functionality to find specific topics"
                }
                
                return json.dumps(search_data, indent=2)
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
    
    async def _register_system_state_resources(self) -> None:
        """Register system state resources."""
        from openhab_mcp_server.resources.openhab import SystemStateResource
        
        # Initialize resource instance
        system_resource = SystemStateResource()
        
        @self.server.list_resources()
        async def list_system_resources() -> List[Resource]:
            """List available system state resources."""
            return [
                Resource(
                    uri="openhab://system/status",
                    name="System Status",
                    description="Current system status and health information",
                    mimeType="application/json"
                ),
                Resource(
                    uri="openhab://system/items",
                    name="All Items",
                    description="Complete list of all configured items",
                    mimeType="application/json"
                ),
                Resource(
                    uri="openhab://system/things",
                    name="All Things", 
                    description="Complete list of all configured things",
                    mimeType="application/json"
                ),
                Resource(
                    uri="openhab://system/bindings",
                    name="Binding Status",
                    description="Status of all installed bindings",
                    mimeType="application/json"
                ),
                Resource(
                    uri="openhab://system/connectivity",
                    name="Connectivity Status",
                    description="Connectivity status for external services",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_system_resource(uri: str) -> str:
            """Read system state resource content."""
            
            try:
                if uri == "openhab://system/status":
                    system_info = await system_resource.get_system_info()
                    return json.dumps(system_info, indent=2)
                
                elif uri == "openhab://system/items":
                    if not self.openhab_client:
                        return '{"error": "openHAB client not initialized"}'
                    
                    async with self.openhab_client:
                        items = await self.openhab_client.get_items()
                        return json.dumps({"items": items}, indent=2)
                
                elif uri == "openhab://system/things":
                    if not self.openhab_client:
                        return '{"error": "openHAB client not initialized"}'
                    
                    async with self.openhab_client:
                        things = await self.openhab_client.get_things()
                        return json.dumps({"things": things}, indent=2)
                
                elif uri == "openhab://system/bindings":
                    binding_status = await system_resource.get_binding_status()
                    return json.dumps({"bindings": binding_status}, indent=2)
                
                elif uri == "openhab://system/connectivity":
                    connectivity = await system_resource.get_connectivity_status()
                    return json.dumps(connectivity, indent=2)
                
                else:
                    return '{"error": "Unknown system resource URI"}'
                    
            except Exception as e:
                structured_logger.error(
                    f"System resource read failed: {e}",
                    category=LogCategory.RESOURCE_ACCESS,
                    error_type=type(e).__name__,
                    metadata={"uri": uri}
                )
                return f'{{"error": "Failed to read system resource: {str(e)}"}}'
    
    async def _register_diagnostic_resources(self) -> None:
        """Register diagnostic and health monitoring resources."""
        
        @self.server.list_resources()
        async def list_diagnostic_resources() -> List[Resource]:
            """List available diagnostic resources."""
            return [
                Resource(
                    uri="openhab://diagnostics/health",
                    name="System Health",
                    description="Current system health status and metrics",
                    mimeType="application/json"
                ),
                Resource(
                    uri="openhab://diagnostics/metrics",
                    name="Request Metrics",
                    description="Request performance metrics and statistics",
                    mimeType="application/json"
                ),
                Resource(
                    uri="openhab://diagnostics/config",
                    name="Configuration Status",
                    description="Current configuration and validation status",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_diagnostic_resource(uri: str) -> str:
            """Read diagnostic resource content."""
            
            if not self.health_checker:
                return '{"error": "Health checker not initialized"}'
            
            try:
                if uri == "openhab://diagnostics/health":
                    health = await self.health_checker.check_system_health()
                    return json.dumps(health.to_dict(), indent=2)
                
                elif uri == "openhab://diagnostics/metrics":
                    # Get metrics from structured logger
                    server_logger = get_logger("mcp_server")
                    if hasattr(server_logger, 'metrics'):
                        metrics = server_logger.metrics.get_stats_summary()
                        return json.dumps(metrics, indent=2)
                    else:
                        return '{"error": "No metrics available"}'
                
                elif uri == "openhab://diagnostics/config":
                    config_status = {
                        "openhab_url": self.config.openhab_url,
                        "timeout": self.config.timeout,
                        "log_level": self.config.log_level,
                        "has_token": bool(self.config.openhab_token),
                        "validation": {
                            "url_valid": bool(self.config.openhab_url and self.config.openhab_url.startswith('http')),
                            "timeout_valid": self.config.timeout > 0,
                            "token_configured": bool(self.config.openhab_token)
                        }
                    }
                    return json.dumps(config_status, indent=2)
                
                else:
                    return '{"error": "Unknown diagnostic resource URI"}'
                    
            except Exception as e:
                structured_logger.error(
                    f"Diagnostic resource read failed: {e}",
                    category=LogCategory.RESOURCE_ACCESS,
                    error_type=type(e).__name__,
                    metadata={"uri": uri}
                )
                return f'{{"error": "Failed to read diagnostic resource: {str(e)}"}}'


async def main():
    """Main entry point for the MCP server."""
    server_instance = None
    
    try:
        # Create and start server
        server_instance = OpenHABMCPServer()
        await server_instance.start()
        
        # Run the MCP server
        async with stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="openhab-mcp-server",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        tools={},
                        resources={},
                    ),
                ),
            )
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        if server_instance:
            await server_instance.shutdown()


if __name__ == "__main__":
    asyncio.run(main())