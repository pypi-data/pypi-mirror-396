"""
MCP tool implementations for secure Python script execution.

This module provides MCP tools for executing Python scripts in a secure
sandbox environment with authenticated openHAB API access, syntax validation,
and security constraint checking.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from mcp.types import TextContent

from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.utils.security import InputSanitizer, SecurityLogger
from openhab_mcp_server.utils.script_sandbox import ScriptSandbox
from openhab_mcp_server.utils.script_context import ScriptContext
from openhab_mcp_server.models import ScriptExecutionResult, ScriptValidationResult


logger = logging.getLogger(__name__)


class ScriptExecuteTool:
    """Execute Python scripts in a secure sandbox environment."""
    
    def __init__(self, config: Config, openhab_client: OpenHABClient):
        """Initialize the tool with configuration and openHAB client.
        
        Args:
            config: Configuration object
            openhab_client: Authenticated openHAB client
        """
        self.config = config
        self.openhab_client = openhab_client
        self.sandbox = ScriptSandbox(
            max_execution_time=30.0,  # 30 second timeout
            max_memory_mb=100,        # 100MB memory limit
            max_output_size=10000     # 10KB output limit
        )
        self.input_sanitizer = InputSanitizer()
        self.security_logger = SecurityLogger()
    
    async def execute(self, script_code: str, context: Optional[Dict[str, Any]] = None) -> List[TextContent]:
        """Execute Python script in secure sandbox.
        
        Args:
            script_code: Python script code to execute
            context: Optional context variables to make available to script
            
        Returns:
            List containing script execution results as TextContent
        """
        # Validate and sanitize input
        if not script_code or not script_code.strip():
            return [TextContent(
                type="text",
                text="Error: Script code cannot be empty"
            )]
        
        # Sanitize script code
        try:
            sanitized_code = InputSanitizer.sanitize_script_code(script_code)
        except Exception as e:
            self.security_logger.log_security_event(
                "script_sanitization_failed",
                {"error": str(e), "script_length": len(script_code)}
            )
            return [TextContent(
                type="text",
                text=f"Error: Script sanitization failed: {e}"
            )]
        
        # Create script context with openHAB API access
        script_context = ScriptContext(self.openhab_client, self.config)
        
        # Merge user context with openHAB context
        execution_context = script_context.create_context_dict()
        if context:
            # Only allow safe context variables
            for key, value in context.items():
                if not key.startswith('_') and key not in execution_context:
                    execution_context[key] = value
        
        # Log script execution attempt
        logger.info(f"Executing script with {len(sanitized_code)} characters")
        self.security_logger.log_security_event(
            "script_execution_started",
            {
                "script_length": len(sanitized_code),
                "context_keys": list(execution_context.keys())
            }
        )
        
        try:
            # Execute script in sandbox
            result = self.sandbox.execute_script(sanitized_code, execution_context)
            
            # Log execution result
            self.security_logger.log_security_event(
                "script_execution_completed",
                {
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "output_length": len(result.output) if result.output else 0
                }
            )
            
            # Format result for MCP response
            response_parts = []
            
            # Add execution status
            status = "SUCCESS" if result.success else "FAILED"
            response_parts.append(f"Script execution {status}")
            response_parts.append(f"Execution time: {result.execution_time:.3f} seconds")
            
            # Add output if present
            if result.output:
                response_parts.append("\n--- Script Output ---")
                response_parts.append(result.output)
            
            # Add errors if present
            if result.errors:
                response_parts.append("\n--- Errors ---")
                response_parts.append(result.errors)
            
            # Add return value if present
            if result.return_value is not None:
                response_parts.append("\n--- Return Value ---")
                response_parts.append(str(result.return_value))
            
            # Add script logs if present
            script_logs = script_context.get_logs()
            if script_logs:
                response_parts.append("\n--- Script Logs ---")
                response_parts.extend(script_logs)
            
            return [TextContent(
                type="text",
                text="\n".join(response_parts)
            )]
            
        except Exception as e:
            # Log unexpected error
            logger.error(f"Unexpected error during script execution: {e}")
            self.security_logger.log_security_event(
                "script_execution_error",
                {"error": str(e), "error_type": type(e).__name__}
            )
            
            return [TextContent(
                type="text",
                text=f"Error: Unexpected error during script execution: {e}"
            )]


class ScriptValidateTool:
    """Validate Python script syntax and security constraints."""
    
    def __init__(self, config: Config):
        """Initialize the tool with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.sandbox = ScriptSandbox()
        self.input_sanitizer = InputSanitizer()
        self.security_logger = SecurityLogger()
    
    async def execute(self, script_code: str) -> List[TextContent]:
        """Validate Python script syntax and security constraints.
        
        Args:
            script_code: Python script code to validate
            
        Returns:
            List containing validation results as TextContent
        """
        # Validate input
        if not script_code or not script_code.strip():
            return [TextContent(
                type="text",
                text="Error: Script code cannot be empty"
            )]
        
        # Log validation attempt
        logger.info(f"Validating script with {len(script_code)} characters")
        self.security_logger.log_security_event(
            "script_validation_started",
            {"script_length": len(script_code)}
        )
        
        try:
            # Validate script
            result = self.sandbox.validate_script(script_code)
            
            # Log validation result
            self.security_logger.log_security_event(
                "script_validation_completed",
                {
                    "valid": result.valid,
                    "syntax_errors": len(result.syntax_errors),
                    "security_violations": len(result.security_violations),
                    "warnings": len(result.warnings)
                }
            )
            
            # Format result for MCP response
            response_parts = []
            
            # Add validation status
            status = "VALID" if result.valid else "INVALID"
            response_parts.append(f"Script validation: {status}")
            
            # Add syntax errors if present
            if result.syntax_errors:
                response_parts.append("\n--- Syntax Errors ---")
                for i, error in enumerate(result.syntax_errors, 1):
                    response_parts.append(f"{i}. {error}")
            
            # Add security violations if present
            if result.security_violations:
                response_parts.append("\n--- Security Violations ---")
                for i, violation in enumerate(result.security_violations, 1):
                    response_parts.append(f"{i}. {violation}")
            
            # Add warnings if present
            if result.warnings:
                response_parts.append("\n--- Warnings ---")
                for i, warning in enumerate(result.warnings, 1):
                    response_parts.append(f"{i}. {warning}")
            
            # Add summary
            if result.valid:
                response_parts.append("\nScript is valid and safe to execute.")
            else:
                response_parts.append(f"\nScript has {len(result.syntax_errors)} syntax errors and {len(result.security_violations)} security violations.")
            
            return [TextContent(
                type="text",
                text="\n".join(response_parts)
            )]
            
        except Exception as e:
            # Log unexpected error
            logger.error(f"Unexpected error during script validation: {e}")
            self.security_logger.log_security_event(
                "script_validation_error",
                {"error": str(e), "error_type": type(e).__name__}
            )
            
            return [TextContent(
                type="text",
                text=f"Error: Unexpected error during script validation: {e}"
            )]