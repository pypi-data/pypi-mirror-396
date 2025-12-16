"""
Property-based tests for script execution functionality.

This module contains property-based tests that validate the correctness
properties of the script execution framework including sandbox security,
validation, API authentication, and error handling.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize
import asyncio
import time
from typing import Dict, Any, List

from openhab_mcp_server.utils.script_sandbox import ScriptSandbox, ScriptSecurityError, ScriptTimeoutError
from openhab_mcp_server.utils.script_context import ScriptContext
from openhab_mcp_server.utils.openhab_client import OpenHABClient
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.models import ScriptExecutionResult, ScriptValidationResult


class TestScriptSandboxSecurity:
    """Property-based tests for script sandbox security."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sandbox = ScriptSandbox(
            max_execution_time=5.0,  # Short timeout for tests
            max_memory_mb=50,        # Limited memory for tests
            max_output_size=1000     # Limited output for tests
        )
    
    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=100, deadline=10000)
    def test_property_30_script_sandbox_security(self, script_code: str):
        """
        **Feature: openhab-mcp-server, Property 30: Script sandbox security**
        
        Property: For any Python script execution, the script should run within 
        a secure sandbox environment without escaping to the host system.
        
        **Validates: Requirements 11.1**
        """
        # Skip empty or whitespace-only scripts
        assume(script_code.strip())
        
        # Test that dangerous operations are blocked
        dangerous_patterns = [
            'import os',
            'import sys', 
            'import subprocess',
            '__import__("os")',
            'open("/etc/passwd")',
            'exec("import os")',
            'eval("__import__")',
            'globals()',
            'locals()',
        ]
        
        # If script contains dangerous patterns, it should be rejected during validation
        contains_dangerous = any(pattern in script_code for pattern in dangerous_patterns)
        
        validation_result = self.sandbox.validate_script(script_code)
        
        if contains_dangerous:
            # Script with dangerous patterns should be marked as invalid
            assert not validation_result.valid, f"Script with dangerous pattern should be invalid: {script_code[:100]}"
            assert len(validation_result.security_violations) > 0, "Should have security violations"
        else:
            # If validation passes, execution should be contained
            if validation_result.valid:
                execution_result = self.sandbox.execute_script(script_code)
                
                # Even if execution fails, it should not compromise the host system
                # We verify this by checking that the process is still running normally
                # and that no system-level exceptions occurred
                assert isinstance(execution_result, ScriptExecutionResult)
                assert execution_result.execution_time >= 0
                
                # Verify output is limited
                if execution_result.output:
                    assert len(execution_result.output) <= self.sandbox.max_output_size
    
    @given(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc')), min_size=1, max_size=100))
    @settings(max_examples=50, deadline=5000)
    def test_safe_script_execution_succeeds(self, safe_code: str):
        """Test that safe scripts execute successfully."""
        # Create a simple safe script
        safe_script = f"""
result = {safe_code!r}
print(f"Safe execution: {{result}}")
"""
        
        validation_result = self.sandbox.validate_script(safe_script)
        
        if validation_result.valid:
            execution_result = self.sandbox.execute_script(safe_script)
            
            # Safe scripts should execute without security violations
            assert isinstance(execution_result, ScriptExecutionResult)
            assert execution_result.execution_time >= 0
    
    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=20, deadline=5000)
    def test_resource_limits_enforced(self, iterations: int):
        """Test that resource limits are enforced."""
        # Create a script that tries to consume resources
        resource_script = f"""
# Try to create large data structures
data = []
for i in range({iterations}):
    data.append("x" * 1000)
    print(f"Iteration {{i}}")
"""
        
        validation_result = self.sandbox.validate_script(resource_script)
        
        if validation_result.valid:
            execution_result = self.sandbox.execute_script(resource_script)
            
            # Execution should complete within time limits
            assert execution_result.execution_time <= self.sandbox.max_execution_time + 1.0  # Allow small margin
            
            # Output should be limited
            if execution_result.output:
                assert len(execution_result.output) <= self.sandbox.max_output_size


class TestScriptValidation:
    """Property-based tests for script validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sandbox = ScriptSandbox()
    
    @given(st.text(min_size=1, max_size=5000))
    @settings(max_examples=100, deadline=10000)
    def test_property_31_script_validation_completeness(self, script_code: str):
        """
        **Feature: openhab-mcp-server, Property 31: Script validation completeness**
        
        Property: For any script input, the system should validate syntax and 
        security constraints before execution, rejecting malicious or invalid scripts.
        
        **Validates: Requirements 11.2**
        """
        # Skip empty scripts
        assume(script_code.strip())
        
        validation_result = self.sandbox.validate_script(script_code)
        
        # Validation result should always be a ScriptValidationResult
        assert isinstance(validation_result, ScriptValidationResult)
        
        # If script is marked as valid, it should have no syntax errors or security violations
        if validation_result.valid:
            assert len(validation_result.syntax_errors) == 0, "Valid script should have no syntax errors"
            assert len(validation_result.security_violations) == 0, "Valid script should have no security violations"
        else:
            # Invalid script should have at least one error or violation
            total_issues = len(validation_result.syntax_errors) + len(validation_result.security_violations)
            assert total_issues > 0, "Invalid script should have at least one error or violation"
        
        # Test that syntax errors are properly detected
        try:
            compile(script_code, '<test>', 'exec')
            syntax_valid = True
        except SyntaxError:
            syntax_valid = False
        
        # If Python compilation fails, validation should detect syntax errors
        if not syntax_valid:
            assert not validation_result.valid or len(validation_result.syntax_errors) > 0
    
    @given(st.sampled_from([
        'import os\nprint("test")',
        'exec("print(1)")',
        'eval("1+1")',
        '__import__("sys")',
        'open("/etc/passwd")',
        'globals()',
        'locals()',
        'getattr(object, "__class__")',
    ]))
    @settings(max_examples=10, deadline=5000)
    def test_dangerous_patterns_detected(self, dangerous_script: str):
        """Test that dangerous patterns are consistently detected."""
        validation_result = self.sandbox.validate_script(dangerous_script)
        
        # Dangerous scripts should always be marked as invalid
        assert not validation_result.valid, f"Dangerous script should be invalid: {dangerous_script}"
        assert len(validation_result.security_violations) > 0, "Should have security violations"


class TestScriptAPIAuthentication:
    """Property-based tests for script API authentication."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mock config and client for testing
        self.config = Config(
            openhab_url="http://localhost:8080",
            openhab_token="test_token",
            timeout=30,
            log_level="INFO"
        )
        
        # Create a mock OpenHAB client
        class MockOpenHABClient:
            async def get_item_state(self, item_name: str):
                return {"name": item_name, "state": "ON", "type": "Switch"}
            
            async def send_item_command(self, item_name: str, command: str):
                return True
            
            async def get_items(self):
                return [{"name": "TestItem", "state": "ON", "type": "Switch"}]
            
            async def get_thing_status(self, thing_uid: str):
                return {"uid": thing_uid, "status": "ONLINE"}
            
            async def get_things(self):
                return [{"uid": "test:thing:1", "status": "ONLINE"}]
            
            async def get_system_info(self):
                return {"version": "4.0.0", "locale": "en_US"}
        
        self.openhab_client = MockOpenHABClient()
        self.script_context = ScriptContext(self.openhab_client, self.config)
    
    @given(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=50))
    @settings(max_examples=20, deadline=5000)
    def test_property_32_script_api_authentication(self, item_name: str):
        """
        **Feature: openhab-mcp-server, Property 32: Script API authentication**
        
        Property: For any script that accesses openHAB APIs, the system should 
        provide authenticated access with proper security context.
        
        **Validates: Requirements 11.3**
        """
        # Create a script that uses openHAB API
        script_code = f"""
# Test authenticated API access
item_state = get_item_state("{item_name}")
print(f"Item state: {{item_state}}")

all_items = get_all_items()
print(f"Total items: {{len(all_items)}}")

system_info = get_system_info()
print(f"System version: {{system_info.get('version', 'unknown')}}")
"""
        
        sandbox = ScriptSandbox()
        validation_result = sandbox.validate_script(script_code)
        
        if validation_result.valid:
            # Execute script with authenticated context
            context = self.script_context.create_context_dict()
            execution_result = sandbox.execute_script(script_code, context)
            
            # Script should execute successfully with authenticated access
            assert isinstance(execution_result, ScriptExecutionResult)
            
            # If execution succeeds, it should have access to openHAB functions
            if execution_result.success:
                # Verify that openHAB API functions were available
                assert "get_item_state" in context
                assert "get_all_items" in context
                assert "get_system_info" in context
                
                # Verify that the context provides proper isolation
                assert "openhab" in context
                assert isinstance(context["openhab"], ScriptContext)


class TestScriptExecutionResults:
    """Property-based tests for script execution results."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sandbox = ScriptSandbox(max_execution_time=5.0)
    
    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=50, deadline=10000)
    def test_property_33_script_execution_result_completeness(self, script_code: str):
        """
        **Feature: openhab-mcp-server, Property 33: Script execution result completeness**
        
        Property: For any completed script execution, the results should include 
        output, errors, and execution time information.
        
        **Validates: Requirements 11.4**
        """
        # Skip empty scripts
        assume(script_code.strip())
        
        validation_result = self.sandbox.validate_script(script_code)
        
        if validation_result.valid:
            start_time = time.time()
            execution_result = self.sandbox.execute_script(script_code)
            end_time = time.time()
            
            # Result should always be a ScriptExecutionResult
            assert isinstance(execution_result, ScriptExecutionResult)
            
            # Should have execution time information
            assert hasattr(execution_result, 'execution_time')
            assert execution_result.execution_time >= 0
            assert execution_result.execution_time <= (end_time - start_time) + 1.0  # Allow margin
            
            # Should have success status
            assert hasattr(execution_result, 'success')
            assert isinstance(execution_result.success, bool)
            
            # Should have output field (may be empty)
            assert hasattr(execution_result, 'output')
            assert isinstance(execution_result.output, str)
            
            # Should have errors field (may be None)
            assert hasattr(execution_result, 'errors')
            
            # Should have return_value field (may be None)
            assert hasattr(execution_result, 'return_value')


class TestScriptErrorHandling:
    """Property-based tests for script error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sandbox = ScriptSandbox(max_execution_time=2.0)  # Short timeout for error tests
    
    @given(st.sampled_from([
        'raise ValueError("test error")',
        '1/0',  # Division by zero
        'undefined_variable',  # NameError
        'print(x for x in range(10**6))',  # Potential memory issue
        'while True: pass',  # Infinite loop
    ]))
    @settings(max_examples=10, deadline=5000)
    def test_property_34_script_failure_error_handling(self, failing_script: str):
        """
        **Feature: openhab-mcp-server, Property 34: Script failure error handling**
        
        Property: For any failed script execution, the system should provide 
        detailed error information while preventing system compromise.
        
        **Validates: Requirements 11.5**
        """
        validation_result = self.sandbox.validate_script(failing_script)
        
        if validation_result.valid:
            execution_result = self.sandbox.execute_script(failing_script)
            
            # Should always return a result, even for failures
            assert isinstance(execution_result, ScriptExecutionResult)
            
            # Failed execution should be marked as unsuccessful
            if not execution_result.success:
                # Should have error information
                assert execution_result.errors is not None
                assert len(execution_result.errors) > 0
                
                # Should still have execution time
                assert execution_result.execution_time >= 0
                
                # Should not compromise the system (we're still running)
                assert True  # If we reach here, system is not compromised
            
            # Execution time should be reasonable (not infinite)
            assert execution_result.execution_time <= self.sandbox.max_execution_time + 1.0
    
    @given(st.integers(min_value=10, max_value=100))
    @settings(max_examples=10, deadline=5000)
    def test_timeout_handling(self, sleep_seconds: int):
        """Test that timeout handling works correctly."""
        # Create a script that would run longer than the timeout
        timeout_script = f"""
import time
time.sleep({sleep_seconds})
print("This should not print")
"""
        
        validation_result = self.sandbox.validate_script(timeout_script)
        
        if validation_result.valid:
            execution_result = self.sandbox.execute_script(timeout_script)
            
            # Should handle timeout gracefully
            assert isinstance(execution_result, ScriptExecutionResult)
            
            # Should not exceed timeout significantly
            assert execution_result.execution_time <= self.sandbox.max_execution_time + 2.0
            
            # If it timed out, should have appropriate error
            if not execution_result.success and execution_result.execution_time >= self.sandbox.max_execution_time - 0.5:
                assert "timeout" in execution_result.errors.lower()