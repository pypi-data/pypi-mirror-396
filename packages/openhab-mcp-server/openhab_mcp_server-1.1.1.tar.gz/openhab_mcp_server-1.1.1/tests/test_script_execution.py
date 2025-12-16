"""
Unit tests for script execution functionality.

This module contains unit tests for the script execution framework including
sandbox isolation, security validation, API context, and error handling.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from openhab_mcp_server.utils.script_sandbox import ScriptSandbox, ScriptSecurityError, ScriptTimeoutError
from openhab_mcp_server.utils.script_context import ScriptContext
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.models import ScriptExecutionResult, ScriptValidationResult
from openhab_mcp_server.tools.scripts import ScriptExecuteTool, ScriptValidateTool


class TestScriptSandbox:
    """Unit tests for ScriptSandbox class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sandbox = ScriptSandbox(
            max_execution_time=5.0,
            max_memory_mb=50,
            max_output_size=1000
        )
    
    def test_validate_script_valid_code(self):
        """Test validation of valid script code."""
        script = """
x = 1 + 2
print(f"Result: {x}")
"""
        result = self.sandbox.validate_script(script)
        
        assert isinstance(result, ScriptValidationResult)
        assert result.valid
        assert len(result.syntax_errors) == 0
        assert len(result.security_violations) == 0
    
    def test_validate_script_syntax_error(self):
        """Test validation of script with syntax errors."""
        script = """
x = 1 +
print("Invalid syntax")
"""
        result = self.sandbox.validate_script(script)
        
        assert isinstance(result, ScriptValidationResult)
        assert not result.valid
        assert len(result.syntax_errors) > 0
    
    def test_validate_script_security_violation(self):
        """Test validation of script with security violations."""
        script = """
import os
os.system("rm -rf /")
"""
        result = self.sandbox.validate_script(script)
        
        assert isinstance(result, ScriptValidationResult)
        assert not result.valid
        assert len(result.security_violations) > 0
    
    def test_validate_script_dangerous_calls(self):
        """Test validation detects dangerous function calls."""
        dangerous_scripts = [
            'exec("print(1)")',
            'eval("1+1")',
            '__import__("os")',
            'globals()',
            'locals()',
        ]
        
        for script in dangerous_scripts:
            result = self.sandbox.validate_script(script)
            assert not result.valid, f"Script should be invalid: {script}"
            assert len(result.security_violations) > 0
    
    def test_execute_script_simple_success(self):
        """Test successful execution of simple script."""
        script = """
result = 2 + 3
print(f"Sum: {result}")
"""
        result = self.sandbox.execute_script(script)
        
        assert isinstance(result, ScriptExecutionResult)
        assert result.success
        assert "Sum: 5" in result.output
        assert result.execution_time > 0
    
    def test_execute_script_with_context(self):
        """Test script execution with context variables."""
        script = """
total = x + y
print(f"Total: {total}")
"""
        context = {"x": 10, "y": 20}
        result = self.sandbox.execute_script(script, context)
        
        assert isinstance(result, ScriptExecutionResult)
        assert result.success
        assert "Total: 30" in result.output
    
    def test_execute_script_runtime_error(self):
        """Test script execution with runtime error."""
        script = """
x = 1 / 0
"""
        result = self.sandbox.execute_script(script)
        
        assert isinstance(result, ScriptExecutionResult)
        assert not result.success
        assert result.errors is not None
        assert "division by zero" in result.errors.lower()
    
    def test_execute_script_output_limit(self):
        """Test that output is limited to max_output_size."""
        script = """
for i in range(1000):
    print(f"Line {i}: " + "x" * 100)
"""
        result = self.sandbox.execute_script(script)
        
        assert isinstance(result, ScriptExecutionResult)
        assert len(result.output) <= self.sandbox.max_output_size
    
    def test_execute_script_invalid_validation(self):
        """Test that invalid scripts are not executed."""
        script = """
import os
print("This should not execute")
"""
        result = self.sandbox.execute_script(script)
        
        assert isinstance(result, ScriptExecutionResult)
        assert not result.success
        assert "validation failed" in result.errors.lower()
    
    def test_create_restricted_globals(self):
        """Test creation of restricted global namespace."""
        context = {"safe_var": 42, "_private": "should_not_be_added"}
        restricted = self.sandbox._create_restricted_globals(context)
        
        # Should have safe variable
        assert "safe_var" in restricted
        assert restricted["safe_var"] == 42
        
        # Should not have private variable
        assert "_private" not in restricted
        
        # Should have restricted builtins
        assert "__builtins__" in restricted
        assert "print" in restricted["__builtins__"]
        assert "exec" not in restricted["__builtins__"]
        
        # Should have allowed modules
        assert "json" in restricted
        assert "math" in restricted


class TestScriptContext:
    """Unit tests for ScriptContext class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config(
            openhab_url="http://localhost:8080",
            openhab_token="test_token",
            timeout=30,
            log_level="INFO"
        )
        
        # Create mock OpenHAB client
        self.mock_client = Mock()
        self.mock_client.get_item_state = AsyncMock(return_value={"name": "TestItem", "state": "ON"})
        self.mock_client.send_item_command = AsyncMock(return_value=True)
        self.mock_client.get_items = AsyncMock(return_value=[{"name": "TestItem", "state": "ON"}])
        self.mock_client.get_thing_status = AsyncMock(return_value={"uid": "test:thing:1", "status": "ONLINE"})
        self.mock_client.get_things = AsyncMock(return_value=[{"uid": "test:thing:1", "status": "ONLINE"}])
        self.mock_client.get_system_info = AsyncMock(return_value={"version": "4.0.0"})
        
        self.script_context = ScriptContext(self.mock_client, self.config)
    
    def test_get_item_state(self):
        """Test getting item state through script context."""
        result = self.script_context.get_item_state("TestItem")
        
        assert result is not None
        assert result["name"] == "TestItem"
        assert result["state"] == "ON"
    
    def test_send_item_command(self):
        """Test sending item command through script context."""
        result = self.script_context.send_item_command("TestItem", "OFF")
        
        assert result is True
    
    def test_get_all_items(self):
        """Test getting all items through script context."""
        result = self.script_context.get_all_items()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "TestItem"
    
    def test_get_thing_status(self):
        """Test getting thing status through script context."""
        result = self.script_context.get_thing_status("test:thing:1")
        
        assert result is not None
        assert result["uid"] == "test:thing:1"
        assert result["status"] == "ONLINE"
    
    def test_get_all_things(self):
        """Test getting all things through script context."""
        result = self.script_context.get_all_things()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["uid"] == "test:thing:1"
    
    def test_get_system_info(self):
        """Test getting system info through script context."""
        result = self.script_context.get_system_info()
        
        assert result is not None
        assert result["version"] == "4.0.0"
    
    def test_logging(self):
        """Test script logging functionality."""
        self.script_context.log("Test message")
        
        logs = self.script_context.get_logs()
        assert len(logs) == 1
        assert "Test message" in logs[0]
        
        self.script_context.clear_logs()
        assert len(self.script_context.get_logs()) == 0
    
    def test_create_context_dict(self):
        """Test creation of context dictionary."""
        context = self.script_context.create_context_dict()
        
        # Should have openHAB API functions
        assert "get_item_state" in context
        assert "send_item_command" in context
        assert "get_all_items" in context
        assert "get_thing_status" in context
        assert "get_all_things" in context
        assert "get_system_info" in context
        assert "log" in context
        
        # Should have openhab context object
        assert "openhab" in context
        assert isinstance(context["openhab"], ScriptContext)
    
    def test_api_error_handling(self):
        """Test error handling in API calls."""
        # Mock client to raise exception
        self.mock_client.get_item_state.side_effect = Exception("API Error")
        
        result = self.script_context.get_item_state("TestItem")
        
        # Should return None on error
        assert result is None
        
        # Should log the error
        logs = self.script_context.get_logs()
        assert len(logs) > 0
        assert "API Error" in logs[0]


class TestScriptExecuteTool:
    """Unit tests for ScriptExecuteTool class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config(
            openhab_url="http://localhost:8080",
            openhab_token="test_token",
            timeout=30,
            log_level="INFO"
        )
        
        # Create mock OpenHAB client
        self.mock_client = Mock()
        self.mock_client.get_item_state = AsyncMock(return_value={"name": "TestItem", "state": "ON"})
        
        self.tool = ScriptExecuteTool(self.config, self.mock_client)
    
    @pytest.mark.asyncio
    async def test_execute_valid_script(self):
        """Test execution of valid script."""
        script = """
result = 1 + 2
print(f"Result: {result}")
"""
        
        result = await self.tool.execute(script)
        
        assert len(result) == 1
        assert "SUCCESS" in result[0].text
        assert "Result: 3" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_empty_script(self):
        """Test execution with empty script."""
        result = await self.tool.execute("")
        
        assert len(result) == 1
        assert "Error: Script code cannot be empty" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_script_with_context(self):
        """Test execution with custom context."""
        script = """
print(f"Custom value: {custom_var}")
"""
        context = {"custom_var": "test_value"}
        
        result = await self.tool.execute(script, context)
        
        assert len(result) == 1
        assert "SUCCESS" in result[0].text
        assert "Custom value: test_value" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_script_with_openhab_api(self):
        """Test execution with openHAB API access."""
        script = """
item_state = get_item_state("TestItem")
print(f"Item state: {item_state}")
"""
        
        result = await self.tool.execute(script)
        
        assert len(result) == 1
        assert "SUCCESS" in result[0].text
        assert "TestItem" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_dangerous_script(self):
        """Test execution of dangerous script."""
        script = """
import os
os.system("echo 'dangerous'")
"""
        
        result = await self.tool.execute(script)
        
        assert len(result) == 1
        assert "FAILED" in result[0].text or "sanitization failed" in result[0].text


class TestScriptValidateTool:
    """Unit tests for ScriptValidateTool class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config(
            openhab_url="http://localhost:8080",
            openhab_token="test_token",
            timeout=30,
            log_level="INFO"
        )
        
        self.tool = ScriptValidateTool(self.config)
    
    @pytest.mark.asyncio
    async def test_validate_valid_script(self):
        """Test validation of valid script."""
        script = """
x = 1 + 2
print(f"Result: {x}")
"""
        
        result = await self.tool.execute(script)
        
        assert len(result) == 1
        assert "VALID" in result[0].text
        assert "Script is valid and safe to execute" in result[0].text
    
    @pytest.mark.asyncio
    async def test_validate_empty_script(self):
        """Test validation with empty script."""
        result = await self.tool.execute("")
        
        assert len(result) == 1
        assert "Error: Script code cannot be empty" in result[0].text
    
    @pytest.mark.asyncio
    async def test_validate_syntax_error(self):
        """Test validation of script with syntax error."""
        script = """
x = 1 +
print("Invalid")
"""
        
        result = await self.tool.execute(script)
        
        assert len(result) == 1
        assert "INVALID" in result[0].text
        assert "Syntax Errors" in result[0].text
    
    @pytest.mark.asyncio
    async def test_validate_security_violation(self):
        """Test validation of script with security violations."""
        script = """
import os
exec("print('dangerous')")
"""
        
        result = await self.tool.execute(script)
        
        assert len(result) == 1
        assert "INVALID" in result[0].text
        assert "Security Violations" in result[0].text
    
    @pytest.mark.asyncio
    async def test_validate_with_warnings(self):
        """Test validation that produces warnings."""
        # This would need to be implemented in the sandbox to produce warnings
        script = """
# This is a simple valid script
x = 42
print(x)
"""
        
        result = await self.tool.execute(script)
        
        assert len(result) == 1
        assert "VALID" in result[0].text


class TestScriptIntegration:
    """Integration tests for script execution components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config(
            openhab_url="http://localhost:8080",
            openhab_token="test_token",
            timeout=30,
            log_level="INFO"
        )
        
        # Create mock OpenHAB client
        self.mock_client = Mock()
        self.mock_client.get_item_state = AsyncMock(return_value={"name": "TestItem", "state": "ON"})
        self.mock_client.send_item_command = AsyncMock(return_value=True)
        
        self.sandbox = ScriptSandbox()
        self.script_context = ScriptContext(self.mock_client, self.config)
    
    def test_end_to_end_script_execution(self):
        """Test complete script execution workflow."""
        script = """
# Get item state
item_state = get_item_state("TestItem")
log(f"Retrieved item state: {item_state}")

# Send command
success = send_item_command("TestItem", "OFF")
log(f"Command sent successfully: {success}")

# Calculate result
result = 10 * 5
print(f"Calculation result: {result}")
"""
        
        # Validate script
        validation = self.sandbox.validate_script(script)
        assert validation.valid
        
        # Execute script with context
        context = self.script_context.create_context_dict()
        execution = self.sandbox.execute_script(script, context)
        
        assert execution.success
        assert "Calculation result: 50" in execution.output
        
        # Check logs
        logs = self.script_context.get_logs()
        assert len(logs) >= 2
        assert any("Retrieved item state" in log for log in logs)
        assert any("Command sent successfully" in log for log in logs)
    
    def test_script_isolation(self):
        """Test that scripts are properly isolated."""
        script1 = """
x = 100
print(f"Script 1: {x}")
"""
        
        script2 = """
try:
    print(f"Script 2: {x}")
except NameError:
    print("Script 2: x is not defined (good!)")
"""
        
        # Execute first script
        result1 = self.sandbox.execute_script(script1)
        assert result1.success
        assert "Script 1: 100" in result1.output
        
        # Execute second script - should not have access to x from first script
        result2 = self.sandbox.execute_script(script2)
        assert result2.success
        assert "x is not defined (good!)" in result2.output
    
    def test_security_enforcement(self):
        """Test that security constraints are enforced."""
        dangerous_scripts = [
            "import subprocess; subprocess.run(['ls'])",
            "open('/etc/passwd', 'r')",
            "__import__('os').system('echo test')",
            "exec('print(\"dangerous\")')",
            "eval('1+1')",
        ]
        
        for script in dangerous_scripts:
            # Should fail validation
            validation = self.sandbox.validate_script(script)
            assert not validation.valid, f"Script should be invalid: {script}"
            
            # Should fail execution
            execution = self.sandbox.execute_script(script)
            assert not execution.success, f"Script should fail execution: {script}"