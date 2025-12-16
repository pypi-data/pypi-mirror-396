"""
Transformation management tools for openHAB MCP server.

This module provides MCP tools for managing transformations in openHAB,
including listing available transformations, creating new ones, testing
transformations with sample data, updating configurations, and tracking usage.
"""

import logging
from typing import Any, Dict, List, Optional

from mcp.types import TextContent

from openhab_mcp_server.models import TransformationInfo, TransformationTestResult, ValidationResult
from openhab_mcp_server.utils.openhab_client import OpenHABClient
from openhab_mcp_server.utils.config import get_config
from openhab_mcp_server.utils.logging import get_logger, LogCategory


logger = logging.getLogger(__name__)
structured_logger = get_logger("transformation_tools")


class TransformationListTool:
    """List available transformation addons and their capabilities."""
    
    @staticmethod
    async def execute() -> List[TextContent]:
        """Get all installed transformation addons with capabilities.
        
        Returns:
            List of TextContent with transformation information
        """
        try:
            structured_logger.info(
                "Listing available transformations",
                category=LogCategory.TOOL_EXECUTION
            )
            
            async with OpenHABClient(get_config()) as client:
                transformations = await client.get_transformations()
                
                if not transformations:
                    structured_logger.info(
                        "No transformations found",
                        category=LogCategory.TOOL_EXECUTION
                    )
                    
                    return [TextContent(
                        type="text",
                        text="No transformation addons are currently installed."
                    )]
                
                # Format transformations for display
                transformation_list = []
                for transformation in transformations:
                    trans_info = f"• Type: {transformation.get('type', 'Unknown')}"
                    trans_info += f"\n  ID: {transformation.get('id', 'Unknown')}"
                    
                    description = transformation.get('description')
                    if description:
                        trans_info += f"\n  Description: {description}"
                    
                    config = transformation.get('configuration', {})
                    if config:
                        trans_info += f"\n  Configuration: {config}"
                    
                    transformation_list.append(trans_info)
                
                result_text = f"Found {len(transformations)} transformation(s):\n\n" + "\n\n".join(transformation_list)
                
                structured_logger.info(
                    f"Successfully listed {len(transformations)} transformations",
                    category=LogCategory.TOOL_EXECUTION
                )
                
                return [TextContent(type="text", text=result_text)]
                
        except Exception as e:
            error_msg = f"Failed to list transformations: {str(e)}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]


class TransformationCreateTool:
    """Create and configure transformations."""
    
    @staticmethod
    def _validate_transformation_input(transformation_type: str, configuration: Dict[str, Any]) -> ValidationResult:
        """Validate transformation creation input parameters.
        
        Args:
            transformation_type: Type of transformation to create
            configuration: Configuration parameters for the transformation
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        # Validate transformation type
        valid_types = {
            'MAP', 'REGEX', 'JSONPATH', 'XPATH', 'JAVASCRIPT', 'SCALE', 
            'EXEC', 'JINJA', 'XSLT', 'ROLLERSHUTTER'
        }
        
        if not transformation_type or not transformation_type.strip():
            result.add_error("Transformation type cannot be empty")
        elif transformation_type.upper() not in valid_types:
            result.add_error(f"Invalid transformation type: {transformation_type}. Must be one of {valid_types}")
        
        # Validate configuration
        if not configuration:
            result.add_error("Configuration cannot be empty")
        elif not isinstance(configuration, dict):
            result.add_error("Configuration must be a dictionary")
        
        return result
    
    @staticmethod
    async def execute(
        transformation_type: str,
        configuration: Dict[str, Any]
    ) -> List[TextContent]:
        """Create transformation with syntax validation and return ID.
        
        Args:
            transformation_type: Type of transformation to create
            configuration: Configuration parameters for the transformation
            
        Returns:
            List of TextContent with creation result
        """
        try:
            structured_logger.info(
                f"Creating transformation of type '{transformation_type}'",
                category=LogCategory.TOOL_EXECUTION
            )
            
            # Validate input parameters
            validation = TransformationCreateTool._validate_transformation_input(transformation_type, configuration)
            if not validation.is_valid:
                error_msg = "Transformation creation validation failed:\n" + "\n".join(validation.errors)
                structured_logger.error(
                    error_msg,
                    category=LogCategory.TOOL_EXECUTION
                )
                return [TextContent(type="text", text=error_msg)]
            
            async with OpenHABClient(get_config()) as client:
                transformation_id = await client.create_transformation(transformation_type, configuration)
                
                if transformation_id:
                    result_text = f"Successfully created transformation of type '{transformation_type}'"
                    result_text += f"\nTransformation ID: {transformation_id}"
                    result_text += f"\nConfiguration: {configuration}"
                    
                    structured_logger.info(
                        f"Transformation created successfully with ID: {transformation_id}",
                        category=LogCategory.TOOL_EXECUTION
                    )
                else:
                    result_text = f"Failed to create transformation of type '{transformation_type}'"
                    structured_logger.error(
                        "Transformation creation failed",
                        category=LogCategory.TOOL_EXECUTION
                    )
                
                return [TextContent(type="text", text=result_text)]
                
        except Exception as e:
            error_msg = f"Failed to create transformation: {str(e)}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]


class TransformationTestTool:
    """Test transformations with sample data."""
    
    @staticmethod
    async def execute(
        transformation_id: str,
        sample_data: str
    ) -> List[TextContent]:
        """Execute transformation with sample data and return results.
        
        Args:
            transformation_id: ID of the transformation to test
            sample_data: Sample input data for testing
            
        Returns:
            List of TextContent with test results
        """
        try:
            structured_logger.info(
                f"Testing transformation '{transformation_id}' with sample data",
                category=LogCategory.TOOL_EXECUTION
            )
            
            # Validate input parameters
            if not transformation_id or not transformation_id.strip():
                error_msg = "Transformation ID cannot be empty"
                structured_logger.error(
                    error_msg,
                    category=LogCategory.TOOL_EXECUTION
                )
                return [TextContent(type="text", text=error_msg)]
            
            if sample_data is None:
                error_msg = "Sample data cannot be None"
                structured_logger.error(
                    error_msg,
                    category=LogCategory.TOOL_EXECUTION
                )
                return [TextContent(type="text", text=error_msg)]
            
            async with OpenHABClient(get_config()) as client:
                test_result = await client.test_transformation(transformation_id, sample_data)
                
                if test_result:
                    result_text = f"Transformation test results for '{transformation_id}':\n"
                    result_text += f"Input: {test_result.get('input_value', sample_data)}\n"
                    
                    if test_result.get('success', False):
                        result_text += f"Output: {test_result.get('output_value', 'No output')}\n"
                        result_text += f"Execution time: {test_result.get('execution_time', 0):.3f}s"
                        
                        structured_logger.info(
                            "Transformation test completed successfully",
                            category=LogCategory.TOOL_EXECUTION
                        )
                    else:
                        result_text += f"Error: {test_result.get('error_message', 'Unknown error')}\n"
                        result_text += f"Execution time: {test_result.get('execution_time', 0):.3f}s"
                        
                        structured_logger.error(
                            "Transformation test failed",
                            category=LogCategory.TOOL_EXECUTION
                        )
                else:
                    result_text = f"Failed to test transformation '{transformation_id}'"
                    structured_logger.error(
                        "Transformation test failed",
                        category=LogCategory.TOOL_EXECUTION
                    )
                
                return [TextContent(type="text", text=result_text)]
                
        except Exception as e:
            error_msg = f"Failed to test transformation: {str(e)}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]


class TransformationUpdateTool:
    """Update transformation configuration."""
    
    @staticmethod
    async def execute(
        transformation_id: str,
        configuration: Dict[str, Any]
    ) -> List[TextContent]:
        """Update transformation parameters with validation.
        
        Args:
            transformation_id: ID of the transformation to update
            configuration: New configuration parameters
            
        Returns:
            List of TextContent with update result
        """
        try:
            structured_logger.info(
                f"Updating transformation configuration for '{transformation_id}'",
                category=LogCategory.TOOL_EXECUTION
            )
            
            # Validate input parameters
            if not transformation_id or not transformation_id.strip():
                error_msg = "Transformation ID cannot be empty"
                structured_logger.error(
                    error_msg,
                    category=LogCategory.TOOL_EXECUTION
                )
                return [TextContent(type="text", text=error_msg)]
            
            if not configuration:
                error_msg = "Configuration cannot be empty for transformation update"
                structured_logger.error(
                    error_msg,
                    category=LogCategory.TOOL_EXECUTION
                )
                return [TextContent(type="text", text=error_msg)]
            
            if not isinstance(configuration, dict):
                error_msg = "Configuration must be a dictionary"
                structured_logger.error(
                    error_msg,
                    category=LogCategory.TOOL_EXECUTION
                )
                return [TextContent(type="text", text=error_msg)]
            
            async with OpenHABClient(get_config()) as client:
                success = await client.update_transformation(transformation_id, configuration)
                
                if success:
                    result_text = f"Successfully updated transformation configuration for '{transformation_id}'"
                    result_text += f"\nNew configuration: {configuration}"
                    
                    structured_logger.info(
                        "Transformation configuration updated successfully",
                        category=LogCategory.TOOL_EXECUTION
                    )
                else:
                    result_text = f"Failed to update transformation configuration for '{transformation_id}'"
                    structured_logger.error(
                        "Transformation configuration update failed",
                        category=LogCategory.TOOL_EXECUTION
                    )
                
                return [TextContent(type="text", text=result_text)]
                
        except Exception as e:
            error_msg = f"Failed to update transformation configuration: {str(e)}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]


class TransformationUsageTool:
    """Query where transformations are used in the system."""
    
    @staticmethod
    async def execute(
        transformation_id: str
    ) -> List[TextContent]:
        """Return all locations where transformation is applied in the system.
        
        Args:
            transformation_id: ID of the transformation to query usage for
            
        Returns:
            List of TextContent with usage information
        """
        try:
            structured_logger.info(
                f"Querying usage for transformation '{transformation_id}'",
                category=LogCategory.TOOL_EXECUTION
            )
            
            # Validate input parameters
            if not transformation_id or not transformation_id.strip():
                error_msg = "Transformation ID cannot be empty"
                structured_logger.error(
                    error_msg,
                    category=LogCategory.TOOL_EXECUTION
                )
                return [TextContent(type="text", text=error_msg)]
            
            async with OpenHABClient(get_config()) as client:
                usage_locations = await client.get_transformation_usage(transformation_id)
                
                if not usage_locations:
                    result_text = f"Transformation '{transformation_id}' is not currently used in any items, links, or rules."
                    
                    structured_logger.info(
                        f"No usage found for transformation '{transformation_id}'",
                        category=LogCategory.TOOL_EXECUTION
                    )
                else:
                    # Format usage locations for display
                    usage_list = []
                    for location in usage_locations:
                        usage_info = f"• Type: {location.get('type', 'Unknown')}"
                        usage_info += f"\n  Name: {location.get('name', 'Unknown')}"
                        
                        context = location.get('context')
                        if context:
                            usage_info += f"\n  Context: {context}"
                        
                        usage_list.append(usage_info)
                    
                    result_text = f"Transformation '{transformation_id}' is used in {len(usage_locations)} location(s):\n\n"
                    result_text += "\n\n".join(usage_list)
                    
                    structured_logger.info(
                        f"Found {len(usage_locations)} usage locations for transformation '{transformation_id}'",
                        category=LogCategory.TOOL_EXECUTION
                    )
                
                return [TextContent(type="text", text=result_text)]
                
        except Exception as e:
            error_msg = f"Failed to query transformation usage: {str(e)}"
            structured_logger.error(
                error_msg,
                category=LogCategory.TOOL_EXECUTION
            )
            return [TextContent(type="text", text=error_msg)]