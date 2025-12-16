"""
MCP tool implementations for operation examples and API documentation.

This module provides MCP tools for generating examples of common operations
and exposing API documentation with usage patterns.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from mcp.types import TextContent

from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.utils.security import InputSanitizer, SecurityLogger
from openhab_mcp_server.models import ValidationResult


logger = logging.getLogger(__name__)


class OperationExamplesTool:
    """Generate examples for common openHAB operations."""
    
    def __init__(self, config: Config):
        """Initialize the tool with configuration.
        
        Args:
            config: Configuration object for openHAB connection
        """
        self.config = config
        
        # Define common operation examples
        self.operation_examples = {
            "item_control": {
                "description": "Control openHAB items by sending commands",
                "examples": [
                    {
                        "operation": "Turn on a switch",
                        "tool": "send_item_command",
                        "parameters": {
                            "name": "LivingRoom_Light",
                            "command": "ON"
                        },
                        "expected_response": "Successfully sent command 'ON' to item 'LivingRoom_Light'"
                    },
                    {
                        "operation": "Set dimmer brightness",
                        "tool": "send_item_command", 
                        "parameters": {
                            "name": "Bedroom_Dimmer",
                            "command": "75"
                        },
                        "expected_response": "Successfully sent command '75' to item 'Bedroom_Dimmer'"
                    },
                    {
                        "operation": "Set thermostat temperature",
                        "tool": "send_item_command",
                        "parameters": {
                            "name": "Thermostat_SetPoint",
                            "command": "21.5"
                        },
                        "expected_response": "Successfully sent command '21.5' to item 'Thermostat_SetPoint'"
                    }
                ]
            },
            "item_monitoring": {
                "description": "Monitor openHAB item states and values",
                "examples": [
                    {
                        "operation": "Get switch state",
                        "tool": "get_item_state",
                        "parameters": {
                            "name": "LivingRoom_Light"
                        },
                        "expected_response": "Item: LivingRoom_Light\nState: ON\nType: Switch\nLabel: Living Room Light"
                    },
                    {
                        "operation": "Get temperature sensor reading",
                        "tool": "get_item_state",
                        "parameters": {
                            "name": "Temperature_Sensor"
                        },
                        "expected_response": "Item: Temperature_Sensor\nState: 22.3\nType: Number\nLabel: Temperature Sensor"
                    },
                    {
                        "operation": "List all switch items",
                        "tool": "list_items",
                        "parameters": {
                            "item_type": "Switch"
                        },
                        "expected_response": "Found 5 items of type 'Switch':\n• LivingRoom_Light (Switch) - State: ON - Living Room Light"
                    }
                ]
            },
            "thing_management": {
                "description": "Manage openHAB things and their configurations",
                "examples": [
                    {
                        "operation": "Check thing status",
                        "tool": "get_thing_status",
                        "parameters": {
                            "uid": "zwave:device:controller:node5"
                        },
                        "expected_response": "Thing: zwave:device:controller:node5\nStatus: ONLINE\nLabel: Z-Wave Motion Sensor\nThing Type: zwave:device"
                    },
                    {
                        "operation": "List all things",
                        "tool": "list_things",
                        "parameters": {},
                        "expected_response": "Found 12 things:\n• zwave:device:controller:node5 - Status: ONLINE - Z-Wave Motion Sensor"
                    }
                ]
            },
            "rule_automation": {
                "description": "Manage openHAB automation rules",
                "examples": [
                    {
                        "operation": "List automation rules",
                        "tool": "list_rules",
                        "parameters": {},
                        "expected_response": "Found 3 rules:\n• Motion Light Rule (motion_light_rule) - Enabled"
                    },
                    {
                        "operation": "Execute a rule manually",
                        "tool": "execute_rule",
                        "parameters": {
                            "uid": "motion_light_rule"
                        },
                        "expected_response": "Successfully executed rule 'motion_light_rule'"
                    }
                ]
            },
            "system_monitoring": {
                "description": "Monitor openHAB system status and health",
                "examples": [
                    {
                        "operation": "Get system information",
                        "tool": "get_system_info",
                        "parameters": {},
                        "expected_response": "openHAB System Information:\nVersion: 4.1.0\nBuild: Release Build\nLocale: en_US"
                    },
                    {
                        "operation": "Check system health",
                        "tool": "get_health_status",
                        "parameters": {},
                        "expected_response": "System Health Status: HEALTHY\nUptime: 86400.00 seconds"
                    },
                    {
                        "operation": "List installed bindings",
                        "tool": "list_bindings",
                        "parameters": {},
                        "expected_response": "Found 8 bindings:\n• zwave - Z-Wave Binding - Z-Wave protocol support"
                    }
                ]
            }
        }
    
    async def execute(self, operation_type: Optional[str] = None) -> List[TextContent]:
        """Generate examples for common operations.
        
        Args:
            operation_type: Optional filter for specific operation type
            
        Returns:
            List containing operation examples as TextContent
        """
        # Validate operation type if provided
        if operation_type is not None:
            validation = self._validate_operation_type(operation_type)
            if not validation.is_valid:
                return [TextContent(
                    type="text",
                    text=f"Invalid operation type: {', '.join(validation.errors)}"
                )]
        
        try:
            if operation_type:
                # Return examples for specific operation type
                if operation_type in self.operation_examples:
                    examples = self.operation_examples[operation_type]
                    return [TextContent(
                        type="text",
                        text=self._format_operation_examples(operation_type, examples)
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"No examples found for operation type '{operation_type}'"
                    )]
            else:
                # Return all available examples
                return [TextContent(
                    type="text",
                    text=self._format_all_examples()
                )]
                
        except Exception as e:
            logger.error(f"Error generating operation examples: {e}")
            return [TextContent(
                type="text",
                text=f"Error generating examples: {e}"
            )]
    
    def _validate_operation_type(self, operation_type: str) -> ValidationResult:
        """Validate operation type.
        
        Args:
            operation_type: Operation type to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        if not operation_type or not operation_type.strip():
            result.add_error("Operation type cannot be empty")
            return result
        
        valid_types = set(self.operation_examples.keys())
        
        if operation_type not in valid_types:
            result.add_error(
                f"Invalid operation type '{operation_type}'. "
                f"Valid types: {', '.join(sorted(valid_types))}"
            )
        
        return result
    
    def _format_operation_examples(self, operation_type: str, examples_data: Dict[str, Any]) -> str:
        """Format examples for a specific operation type.
        
        Args:
            operation_type: Type of operation
            examples_data: Examples data for the operation type
            
        Returns:
            Formatted string representation of examples
        """
        lines = [
            f"=== {operation_type.replace('_', ' ').title()} Examples ===",
            "",
            examples_data["description"],
            ""
        ]
        
        for i, example in enumerate(examples_data["examples"], 1):
            lines.extend([
                f"{i}. {example['operation']}",
                f"   Tool: {example['tool']}",
                f"   Parameters: {json.dumps(example['parameters'], indent=6)}",
                f"   Expected Response: {example['expected_response']}",
                ""
            ])
        
        return "\n".join(lines)
    
    def _format_all_examples(self) -> str:
        """Format all available examples.
        
        Returns:
            Formatted string representation of all examples
        """
        lines = [
            "=== openHAB MCP Server - Operation Examples ===",
            "",
            "Available operation types:",
            ""
        ]
        
        for operation_type, examples_data in self.operation_examples.items():
            lines.extend([
                f"• {operation_type.replace('_', ' ').title()}",
                f"  {examples_data['description']}",
                f"  {len(examples_data['examples'])} examples available",
                ""
            ])
        
        lines.extend([
            "To get examples for a specific operation type, use:",
            "get_operation_examples(operation_type=\"item_control\")",
            "",
            "Available operation types: " + ", ".join(sorted(self.operation_examples.keys()))
        ])
        
        return "\n".join(lines)


class APIDocumentationTool:
    """Expose API documentation with usage patterns."""
    
    def __init__(self, config: Config):
        """Initialize the tool with configuration.
        
        Args:
            config: Configuration object for openHAB connection
        """
        self.config = config
        
        # Define API documentation structure
        self.api_documentation = {
            "tools": {
                "description": "Available MCP tools for openHAB operations",
                "endpoints": {
                    "get_item_state": {
                        "description": "Retrieve the current state of an openHAB item",
                        "parameters": {
                            "name": {
                                "type": "string",
                                "required": True,
                                "description": "Name of the openHAB item",
                                "example": "LivingRoom_Light"
                            }
                        },
                        "returns": "Current state information for the item",
                        "usage_pattern": "Monitor device states and sensor readings",
                        "related_tools": ["send_item_command", "list_items"]
                    },
                    "send_item_command": {
                        "description": "Send a command to an openHAB item",
                        "parameters": {
                            "name": {
                                "type": "string", 
                                "required": True,
                                "description": "Name of the openHAB item",
                                "example": "LivingRoom_Light"
                            },
                            "command": {
                                "type": "string",
                                "required": True,
                                "description": "Command to send to the item",
                                "example": "ON"
                            }
                        },
                        "returns": "Result of the command execution",
                        "usage_pattern": "Control devices and change item states",
                        "related_tools": ["get_item_state", "list_items"]
                    },
                    "list_items": {
                        "description": "List all openHAB items or items of a specific type",
                        "parameters": {
                            "item_type": {
                                "type": "string",
                                "required": False,
                                "description": "Optional filter by item type",
                                "example": "Switch"
                            }
                        },
                        "returns": "List of items with their basic information",
                        "usage_pattern": "Discover available items and their types",
                        "related_tools": ["get_item_state", "send_item_command"]
                    },
                    "get_thing_status": {
                        "description": "Get status and configuration of an openHAB thing",
                        "parameters": {
                            "uid": {
                                "type": "string",
                                "required": True,
                                "description": "UID of the openHAB thing",
                                "example": "zwave:device:controller:node5"
                            }
                        },
                        "returns": "Thing status and configuration information",
                        "usage_pattern": "Monitor device connectivity and configuration",
                        "related_tools": ["list_things"]
                    },
                    "list_things": {
                        "description": "List all openHAB things",
                        "parameters": {},
                        "returns": "List of things with their basic information",
                        "usage_pattern": "Discover configured devices and services",
                        "related_tools": ["get_thing_status"]
                    },
                    "list_rules": {
                        "description": "List all openHAB automation rules",
                        "parameters": {},
                        "returns": "List of rules with their basic information",
                        "usage_pattern": "Review automation configuration",
                        "related_tools": ["execute_rule"]
                    },
                    "execute_rule": {
                        "description": "Manually execute an openHAB rule",
                        "parameters": {
                            "uid": {
                                "type": "string",
                                "required": True,
                                "description": "UID of the rule to execute",
                                "example": "motion_light_rule"
                            }
                        },
                        "returns": "Result of the rule execution",
                        "usage_pattern": "Test automation rules manually",
                        "related_tools": ["list_rules"]
                    },
                    "get_system_info": {
                        "description": "Get openHAB system information",
                        "parameters": {},
                        "returns": "System information including version and configuration",
                        "usage_pattern": "Check system status and version",
                        "related_tools": ["get_health_status", "list_bindings"]
                    },
                    "list_bindings": {
                        "description": "List all installed openHAB bindings",
                        "parameters": {},
                        "returns": "List of installed bindings",
                        "usage_pattern": "Review available integrations",
                        "related_tools": ["get_system_info"]
                    },
                    "get_health_status": {
                        "description": "Get current system health status",
                        "parameters": {},
                        "returns": "Comprehensive health status report",
                        "usage_pattern": "Monitor system health and performance",
                        "related_tools": ["get_diagnostics", "get_metrics_summary"]
                    },
                    "get_diagnostics": {
                        "description": "Get comprehensive diagnostic information",
                        "parameters": {},
                        "returns": "Detailed diagnostic report including metrics and configuration",
                        "usage_pattern": "Troubleshoot system issues",
                        "related_tools": ["get_health_status", "get_metrics_summary"]
                    },
                    "get_metrics_summary": {
                        "description": "Get request metrics summary",
                        "parameters": {},
                        "returns": "Summary of request metrics and performance data",
                        "usage_pattern": "Monitor API performance",
                        "related_tools": ["get_health_status", "get_diagnostics"]
                    }
                }
            },
            "resources": {
                "description": "Available MCP resources for read-only data access",
                "endpoints": {
                    "openhab://docs/setup": {
                        "description": "Complete setup and installation guide for openHAB",
                        "mime_type": "text/plain",
                        "usage_pattern": "Get installation and setup instructions"
                    },
                    "openhab://docs/configuration": {
                        "description": "Guide for configuring items, things, and rules",
                        "mime_type": "text/plain",
                        "usage_pattern": "Learn configuration concepts and procedures"
                    },
                    "openhab://docs/troubleshooting": {
                        "description": "Common issues and troubleshooting steps",
                        "mime_type": "text/plain",
                        "usage_pattern": "Resolve common problems and issues"
                    },
                    "openhab://system/status": {
                        "description": "Current system status and health information",
                        "mime_type": "application/json",
                        "usage_pattern": "Monitor overall system health"
                    },
                    "openhab://diagnostics/health": {
                        "description": "Current system health status and metrics",
                        "mime_type": "application/json",
                        "usage_pattern": "Get detailed health metrics"
                    },
                    "openhab://diagnostics/metrics": {
                        "description": "Request performance metrics and statistics",
                        "mime_type": "application/json",
                        "usage_pattern": "Monitor API performance and usage"
                    }
                }
            },
            "common_workflows": {
                "description": "Common usage patterns and workflows",
                "workflows": {
                    "device_control": {
                        "description": "Control devices through items",
                        "steps": [
                            "1. Use list_items to discover available items",
                            "2. Use get_item_state to check current state",
                            "3. Use send_item_command to control the device",
                            "4. Use get_item_state again to verify the change"
                        ]
                    },
                    "system_monitoring": {
                        "description": "Monitor system health and status",
                        "steps": [
                            "1. Use get_system_info to check basic system information",
                            "2. Use get_health_status for overall health",
                            "3. Use list_things to check device connectivity",
                            "4. Use get_diagnostics for detailed troubleshooting"
                        ]
                    },
                    "troubleshooting": {
                        "description": "Diagnose and resolve issues",
                        "steps": [
                            "1. Use get_diagnostics to identify issues",
                            "2. Use list_things to check device status",
                            "3. Use get_metrics_summary to check performance",
                            "4. Access openhab://docs/troubleshooting for guidance"
                        ]
                    }
                }
            }
        }
    
    async def execute(self, section: Optional[str] = None) -> List[TextContent]:
        """Expose API documentation with usage patterns.
        
        Args:
            section: Optional filter for specific documentation section
            
        Returns:
            List containing API documentation as TextContent
        """
        # Validate section if provided
        if section is not None:
            validation = self._validate_section(section)
            if not validation.is_valid:
                return [TextContent(
                    type="text",
                    text=f"Invalid documentation section: {', '.join(validation.errors)}"
                )]
        
        try:
            if section:
                # Return documentation for specific section
                if section in self.api_documentation:
                    doc_data = self.api_documentation[section]
                    return [TextContent(
                        type="text",
                        text=self._format_section_documentation(section, doc_data)
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"No documentation found for section '{section}'"
                    )]
            else:
                # Return overview of all documentation
                return [TextContent(
                    type="text",
                    text=self._format_overview_documentation()
                )]
                
        except Exception as e:
            logger.error(f"Error generating API documentation: {e}")
            return [TextContent(
                type="text",
                text=f"Error generating documentation: {e}"
            )]
    
    def _validate_section(self, section: str) -> ValidationResult:
        """Validate documentation section.
        
        Args:
            section: Documentation section to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        if not section or not section.strip():
            result.add_error("Documentation section cannot be empty")
            return result
        
        valid_sections = set(self.api_documentation.keys())
        
        if section not in valid_sections:
            result.add_error(
                f"Invalid documentation section '{section}'. "
                f"Valid sections: {', '.join(sorted(valid_sections))}"
            )
        
        return result
    
    def _format_section_documentation(self, section: str, doc_data: Dict[str, Any]) -> str:
        """Format documentation for a specific section.
        
        Args:
            section: Documentation section name
            doc_data: Documentation data for the section
            
        Returns:
            Formatted string representation of section documentation
        """
        lines = [
            f"=== {section.title()} Documentation ===",
            "",
            doc_data["description"],
            ""
        ]
        
        if section == "tools":
            lines.append("Available Tools:")
            lines.append("")
            
            for tool_name, tool_info in doc_data["endpoints"].items():
                lines.extend([
                    f"• {tool_name}",
                    f"  Description: {tool_info['description']}",
                    f"  Usage Pattern: {tool_info['usage_pattern']}",
                    ""
                ])
                
                if tool_info.get("parameters"):
                    lines.append("  Parameters:")
                    for param_name, param_info in tool_info["parameters"].items():
                        required = " (required)" if param_info.get("required") else " (optional)"
                        lines.append(f"    - {param_name}{required}: {param_info['description']}")
                        if param_info.get("example"):
                            lines.append(f"      Example: {param_info['example']}")
                    lines.append("")
                
                if tool_info.get("related_tools"):
                    lines.append(f"  Related Tools: {', '.join(tool_info['related_tools'])}")
                    lines.append("")
        
        elif section == "resources":
            lines.append("Available Resources:")
            lines.append("")
            
            for resource_uri, resource_info in doc_data["endpoints"].items():
                lines.extend([
                    f"• {resource_uri}",
                    f"  Description: {resource_info['description']}",
                    f"  MIME Type: {resource_info['mime_type']}",
                    f"  Usage Pattern: {resource_info['usage_pattern']}",
                    ""
                ])
        
        elif section == "common_workflows":
            lines.append("Common Workflows:")
            lines.append("")
            
            for workflow_name, workflow_info in doc_data["workflows"].items():
                lines.extend([
                    f"• {workflow_name.replace('_', ' ').title()}",
                    f"  {workflow_info['description']}",
                    ""
                ])
                
                for step in workflow_info["steps"]:
                    lines.append(f"  {step}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _format_overview_documentation(self) -> str:
        """Format overview documentation for all sections.
        
        Returns:
            Formatted string representation of overview documentation
        """
        lines = [
            "=== openHAB MCP Server - API Documentation ===",
            "",
            "This MCP server provides tools and resources for interacting with openHAB",
            "home automation systems. The API is organized into the following sections:",
            ""
        ]
        
        for section_name, section_data in self.api_documentation.items():
            endpoint_count = len(section_data.get("endpoints", section_data.get("workflows", {})))
            lines.extend([
                f"• {section_name.title()}",
                f"  {section_data['description']}",
                f"  {endpoint_count} items available",
                ""
            ])
        
        lines.extend([
            "To get detailed documentation for a specific section, use:",
            "get_api_documentation(section=\"tools\")",
            "",
            "Available sections: " + ", ".join(sorted(self.api_documentation.keys())),
            "",
            "For operation examples, use the get_operation_examples tool."
        ])
        
        return "\n".join(lines)