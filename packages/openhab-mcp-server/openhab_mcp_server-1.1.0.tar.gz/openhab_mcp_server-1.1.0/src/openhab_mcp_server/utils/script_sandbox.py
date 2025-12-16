"""
Secure script sandbox environment for Python script execution.

This module provides a secure sandbox environment for executing Python scripts
with restricted builtins, module whitelist, and resource limits to prevent
system compromise while allowing safe script execution.
"""

import ast
import builtins
import io
import logging
import sys
import time
from contextlib import redirect_stdout, redirect_stderr
from typing import Any, Dict, List, Optional, Set

# Import resource module if available (Unix/Linux only)
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False

# Import signal module and check for SIGALRM (Unix/Linux only)
try:
    import signal
    HAS_SIGALRM = hasattr(signal, 'SIGALRM')
except ImportError:
    HAS_SIGALRM = False

from openhab_mcp_server.models import ScriptValidationResult, ScriptExecutionResult


logger = logging.getLogger(__name__)


class ScriptTimeoutError(Exception):
    """Raised when script execution exceeds time limit."""
    pass


class ScriptSecurityError(Exception):
    """Raised when script violates security constraints."""
    pass


class ScriptSandbox:
    """Secure sandbox environment for Python script execution."""
    
    # Allowed built-in functions (whitelist approach)
    ALLOWED_BUILTINS = {
        'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter', 'float',
        'int', 'len', 'list', 'map', 'max', 'min', 'print', 'range', 'round',
        'set', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip'
    }
    
    # Allowed modules (whitelist approach)
    ALLOWED_MODULES = {
        'json', 'math', 'datetime', 're', 'collections', 'itertools',
        'functools', 'operator', 'statistics'
    }
    
    # Forbidden AST node types for security
    FORBIDDEN_NODES = {
        ast.Import,      # Prevent arbitrary imports
        ast.ImportFrom,  # Prevent arbitrary imports
        ast.Call,        # Will be checked separately for dangerous calls
    }
    
    # Dangerous function calls to block
    DANGEROUS_CALLS = {
        'exec', 'eval', 'compile', '__import__', 'open', 'file', 'input',
        'raw_input', 'reload', 'vars', 'locals', 'globals', 'dir',
        'getattr', 'setattr', 'delattr', 'hasattr'
    }
    
    def __init__(self, 
                 max_execution_time: float = 30.0,
                 max_memory_mb: int = 100,
                 max_output_size: int = 10000):
        """Initialize the script sandbox.
        
        Args:
            max_execution_time: Maximum execution time in seconds
            max_memory_mb: Maximum memory usage in MB
            max_output_size: Maximum output size in characters
        """
        self.max_execution_time = max_execution_time
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.max_output_size = max_output_size
        
    def validate_script(self, script_code: str) -> ScriptValidationResult:
        """Validate script syntax and security constraints.
        
        Args:
            script_code: Python script code to validate
            
        Returns:
            ScriptValidationResult with validation details
        """
        result = ScriptValidationResult(valid=True)
        
        # Check for empty script
        if not script_code.strip():
            result.add_syntax_error("Script cannot be empty")
            return result
        
        # Parse AST for syntax validation
        try:
            tree = ast.parse(script_code)
        except SyntaxError as e:
            result.add_syntax_error(f"Syntax error: {e}")
            return result
        
        # Security validation
        self._validate_security_constraints(tree, result)
        
        return result
    
    def _validate_security_constraints(self, tree: ast.AST, result: ScriptValidationResult) -> None:
        """Validate security constraints in the AST.
        
        Args:
            tree: Parsed AST tree
            result: Validation result to update
        """
        for node in ast.walk(tree):
            # Check for forbidden node types
            if type(node) in self.FORBIDDEN_NODES:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    # Check if import is allowed
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name not in self.ALLOWED_MODULES:
                                result.add_security_violation(
                                    f"Import of module '{alias.name}' is not allowed"
                                )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module not in self.ALLOWED_MODULES:
                            result.add_security_violation(
                                f"Import from module '{node.module}' is not allowed"
                            )
                elif isinstance(node, ast.Call):
                    # Check for dangerous function calls
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.DANGEROUS_CALLS:
                            result.add_security_violation(
                                f"Call to dangerous function '{node.func.id}' is not allowed"
                            )
                    elif isinstance(node.func, ast.Attribute):
                        # Check for dangerous attribute access
                        if node.func.attr.startswith('_'):
                            result.add_security_violation(
                                f"Access to private attribute '{node.func.attr}' is not allowed"
                            )
            
            # Check for attribute access to dangerous attributes
            if isinstance(node, ast.Attribute):
                if node.attr.startswith('__') and node.attr.endswith('__'):
                    result.add_security_violation(
                        f"Access to dunder attribute '{node.attr}' is not allowed"
                    )
    
    def execute_script(self, script_code: str, context: Optional[Dict[str, Any]] = None) -> ScriptExecutionResult:
        """Execute Python script in secure sandbox.
        
        Args:
            script_code: Python script code to execute
            context: Optional context variables to make available to script
            
        Returns:
            ScriptExecutionResult with execution details
        """
        start_time = time.time()
        
        # Validate script first
        validation = self.validate_script(script_code)
        if not validation.valid:
            return ScriptExecutionResult(
                success=False,
                output="",
                errors=f"Script validation failed: {validation.syntax_errors + validation.security_violations}",
                execution_time=time.time() - start_time,
                return_value=None
            )
        
        # Set up restricted environment
        restricted_globals = self._create_restricted_globals(context or {})
        
        # Capture output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # Set resource limits
            self._set_resource_limits()
            
            # Set up timeout handler (Unix/Linux only)
            old_handler = None
            if HAS_SIGALRM:
                old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(int(self.max_execution_time))
            
            try:
                # Execute script with output capture
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    # Compile and execute
                    compiled_code = compile(script_code, '<sandbox>', 'exec')
                    exec(compiled_code, restricted_globals)
                
                # Get captured output
                output = stdout_capture.getvalue()
                errors = stderr_capture.getvalue()
                
                # Check output size limits
                if len(output) > self.max_output_size:
                    output = output[:self.max_output_size] + "\n... (output truncated)"
                
                execution_time = time.time() - start_time
                
                return ScriptExecutionResult(
                    success=True,
                    output=output,
                    errors=errors if errors else None,
                    execution_time=execution_time,
                    return_value=restricted_globals.get('__return_value__')
                )
                
            finally:
                # Restore signal handler and cancel alarm (Unix/Linux only)
                if HAS_SIGALRM and old_handler is not None:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
                
        except ScriptTimeoutError:
            return ScriptExecutionResult(
                success=False,
                output=stdout_capture.getvalue(),
                errors="Script execution timed out",
                execution_time=self.max_execution_time,
                return_value=None
            )
        except Exception as e:
            return ScriptExecutionResult(
                success=False,
                output=stdout_capture.getvalue(),
                errors=f"Script execution failed: {str(e)}",
                execution_time=time.time() - start_time,
                return_value=None
            )
    
    def _create_restricted_globals(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create restricted global namespace for script execution.
        
        Args:
            context: User-provided context variables
            
        Returns:
            Dictionary with restricted global namespace
        """
        # Start with minimal builtins
        restricted_builtins = {}
        for name in self.ALLOWED_BUILTINS:
            if hasattr(builtins, name):
                restricted_builtins[name] = getattr(builtins, name)
        
        # Create restricted globals
        restricted_globals = {
            '__builtins__': restricted_builtins,
            '__name__': '__sandbox__',
            '__doc__': None,
        }
        
        # Add allowed modules
        for module_name in self.ALLOWED_MODULES:
            try:
                module = __import__(module_name)
                restricted_globals[module_name] = module
            except ImportError:
                logger.warning(f"Could not import allowed module: {module_name}")
        
        # Add user context (with validation)
        for key, value in context.items():
            if not key.startswith('_'):  # Don't allow private variables
                restricted_globals[key] = value
        
        return restricted_globals
    
    def _set_resource_limits(self) -> None:
        """Set resource limits for script execution."""
        if not HAS_RESOURCE:
            logger.warning("Resource module not available (Windows), skipping resource limits")
            return
            
        try:
            # Set memory limit
            resource.setrlimit(resource.RLIMIT_AS, (self.max_memory_bytes, self.max_memory_bytes))
            
            # Set CPU time limit (slightly higher than wall clock time)
            cpu_limit = int(self.max_execution_time * 1.5)
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
            
        except (OSError, ValueError) as e:
            logger.warning(f"Could not set resource limits: {e}")
    
    def _timeout_handler(self, signum: int, frame: Any) -> None:
        """Handle script execution timeout.
        
        Args:
            signum: Signal number
            frame: Current stack frame
            
        Raises:
            ScriptTimeoutError: Always raised to interrupt execution
        """
        raise ScriptTimeoutError("Script execution timed out")