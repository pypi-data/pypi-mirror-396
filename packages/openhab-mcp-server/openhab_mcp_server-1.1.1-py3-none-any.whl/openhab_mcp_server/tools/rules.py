"""
MCP tool implementations for openHAB rule operations.

This module provides MCP tools for interacting with openHAB automation rules including
listing rules, executing rules manually, and creating new rules.
"""

import logging
from typing import Any, Dict, List, Optional

from mcp.types import TextContent

from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.utils.security import InputSanitizer, SecurityLogger
from openhab_mcp_server.models import RuleDefinition, ValidationResult


logger = logging.getLogger(__name__)


class RuleListTool:
    """List all automation rules with their status and metadata."""
    
    def __init__(self, config: Config):
        """Initialize the tool with configuration.
        
        Args:
            config: Configuration object for openHAB connection
        """
        self.config = config
    
    async def execute(self, status_filter: Optional[str] = None) -> List[TextContent]:
        """Get all rules with their status and execution history.
        
        Args:
            status_filter: Optional filter by rule status (e.g., 'ENABLED', 'DISABLED')
            
        Returns:
            List containing formatted rule list as TextContent
        """
        # Validate status filter if provided
        if status_filter is not None:
            validation = self._validate_status_filter(status_filter)
            if not validation.is_valid:
                return [TextContent(
                    type="text",
                    text=f"Invalid status filter: {', '.join(validation.errors)}"
                )]
        
        # Get rules from openHAB
        async with OpenHABClient(self.config) as client:
            try:
                rules = await client.get_rules()
                
                if not rules:
                    return [TextContent(
                        type="text",
                        text="No automation rules found"
                    )]
                
                # Filter by status if requested
                if status_filter:
                    rules = [rule for rule in rules if rule.get('status') == status_filter.upper()]
                    
                    if not rules:
                        return [TextContent(
                            type="text",
                            text=f"No rules found with status '{status_filter}'"
                        )]
                
                # Format response
                return [TextContent(
                    type="text",
                    text=self._format_rule_list(rules, status_filter)
                )]
                
            except OpenHABError as e:
                logger.error(f"Error listing rules: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error listing rules: {e}"
                )]
    
    def _validate_status_filter(self, status_filter: str) -> ValidationResult:
        """Validate status filter.
        
        Args:
            status_filter: Status filter to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        if not status_filter or not status_filter.strip():
            result.add_error("Status filter cannot be empty")
            return result
        
        valid_statuses = {'ENABLED', 'DISABLED', 'IDLE', 'RUNNING'}
        
        if status_filter.upper() not in valid_statuses:
            result.add_error(f"Invalid status '{status_filter}'. Valid statuses: {', '.join(sorted(valid_statuses))}")
        
        return result
    
    def _format_rule_list(self, rules: List[Dict[str, Any]], status_filter: Optional[str]) -> str:
        """Format rule list for display.
        
        Args:
            rules: List of rule data from openHAB API
            status_filter: Filter used (for header)
            
        Returns:
            Formatted string representation of rule list
        """
        header = f"Found {len(rules)} automation rules"
        if status_filter:
            header += f" with status '{status_filter}'"
        header += ":"
        
        rule_lines = []
        for rule in rules:
            rule_uid = rule.get('uid', 'Unknown')
            rule_name = rule.get('name', 'Unnamed Rule')
            rule_status = rule.get('status', 'UNKNOWN')
            rule_enabled = rule.get('enabled', False)
            
            # Basic rule info
            rule_info = f"• {rule_name} ({rule_uid})"
            rule_info += f"\n  Status: {rule_status}"
            rule_info += f" | Enabled: {'Yes' if rule_enabled else 'No'}"
            
            # Add description if available
            if rule.get('description'):
                description = rule['description']
                if len(description) > 100:
                    description = description[:97] + "..."
                rule_info += f"\n  Description: {description}"
            
            # Add trigger count
            triggers = rule.get('triggers', [])
            conditions = rule.get('conditions', [])
            actions = rule.get('actions', [])
            
            rule_info += f"\n  Components: {len(triggers)} triggers, {len(conditions)} conditions, {len(actions)} actions"
            
            # Add visibility info
            visibility = rule.get('visibility', 'VISIBLE')
            if visibility != 'VISIBLE':
                rule_info += f"\n  Visibility: {visibility}"
            
            rule_lines.append(rule_info)
        
        return header + "\n\n" + "\n\n".join(rule_lines)


class RuleExecuteTool:
    """Manually execute automation rules."""
    
    def __init__(self, config: Config):
        """Initialize the tool with configuration.
        
        Args:
            config: Configuration object for openHAB connection
        """
        self.config = config
    
    async def execute(self, rule_uid: str) -> List[TextContent]:
        """Trigger rule execution manually and track execution status.
        
        Args:
            rule_uid: UID of the rule to execute
            
        Returns:
            List containing execution result as TextContent
        """
        # Validate input
        validation = self._validate_rule_uid(rule_uid)
        if not validation.is_valid:
            return [TextContent(
                type="text",
                text=f"Invalid rule UID: {', '.join(validation.errors)}"
            )]
        
        # Execute rule in openHAB
        async with OpenHABClient(self.config) as client:
            try:
                # First check if rule exists and get its current status
                rule_data = await client.get_rule(rule_uid)
                if rule_data is None:
                    return [TextContent(
                        type="text",
                        text=f"Rule '{rule_uid}' not found"
                    )]
                
                rule_name = rule_data.get('name', 'Unnamed Rule')
                rule_enabled = rule_data.get('enabled', False)
                
                if not rule_enabled:
                    return [TextContent(
                        type="text",
                        text=f"Cannot execute rule '{rule_name}' ({rule_uid}) - rule is disabled"
                    )]
                
                # Execute the rule
                success = await client.execute_rule(rule_uid)
                
                if success:
                    return [TextContent(
                        type="text",
                        text=f"Successfully executed rule '{rule_name}' ({rule_uid})"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Failed to execute rule '{rule_name}' ({rule_uid})"
                    )]
                    
            except OpenHABError as e:
                logger.error(f"Error executing rule '{rule_uid}': {e}")
                return [TextContent(
                    type="text",
                    text=f"Error executing rule: {e}"
                )]
    
    def _validate_rule_uid(self, rule_uid: str) -> ValidationResult:
        """Validate rule UID format with security checks.
        
        Args:
            rule_uid: Rule UID to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = InputSanitizer.validate_rule_uid(rule_uid)
        
        if not result.is_valid:
            SecurityLogger.log_validation_failure("rule_uid", rule_uid, result.errors)
        
        return result


class RuleCreateTool:
    """Create new automation rules."""
    
    def __init__(self, config: Config):
        """Initialize the tool with configuration.
        
        Args:
            config: Configuration object for openHAB connection
        """
        self.config = config
    
    async def execute(self, rule_definition: Dict[str, Any]) -> List[TextContent]:
        """Create new automation rule with validation and UID generation.
        
        Args:
            rule_definition: Rule definition data including name, triggers, conditions, actions
            
        Returns:
            List containing rule creation result as TextContent
        """
        # Validate rule definition
        validation = self._validate_rule_definition(rule_definition)
        if not validation.is_valid:
            return [TextContent(
                type="text",
                text=f"Invalid rule definition:\n" + "\n".join(validation.errors)
            )]
        
        # Create rule in openHAB
        async with OpenHABClient(self.config) as client:
            try:
                # Generate UID if not provided
                if 'uid' not in rule_definition or not rule_definition['uid']:
                    rule_definition['uid'] = self._generate_rule_uid(rule_definition['name'])
                
                # Create the rule
                created_uid = await client.create_rule(rule_definition)
                
                if created_uid:
                    rule_name = rule_definition.get('name', 'Unnamed Rule')
                    return [TextContent(
                        type="text",
                        text=f"Successfully created rule '{rule_name}' with UID: {created_uid}"
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text="Failed to create rule - check rule definition and openHAB logs"
                    )]
                    
            except OpenHABError as e:
                logger.error(f"Error creating rule: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error creating rule: {e}"
                )]
    
    def _validate_rule_definition(self, rule_definition: Dict[str, Any]) -> ValidationResult:
        """Validate rule definition structure and content with security checks.
        
        Args:
            rule_definition: Rule definition to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        if not isinstance(rule_definition, dict):
            result.add_error("Rule definition must be a dictionary")
            return result
        
        # Check required fields
        required_fields = ['name', 'triggers', 'actions']
        for field in required_fields:
            if field not in rule_definition:
                result.add_error(f"Missing required field: {field}")
            elif not rule_definition[field]:
                result.add_error(f"Field '{field}' cannot be empty")
        
        # Validate name with security checks
        if 'name' in rule_definition:
            name = rule_definition['name']
            if not isinstance(name, str) or not name.strip():
                result.add_error("Rule name must be a non-empty string")
            else:
                try:
                    sanitized_name = InputSanitizer.sanitize_string(name, max_length=100)
                except ValueError as e:
                    result.add_error(f"Invalid rule name: {e}")
        
        # Validate description with security checks
        if 'description' in rule_definition and rule_definition['description']:
            description = rule_definition['description']
            if isinstance(description, str):
                try:
                    InputSanitizer.sanitize_string(description, max_length=500)
                except ValueError as e:
                    result.add_error(f"Invalid rule description: {e}")
        
        # Validate triggers
        if 'triggers' in rule_definition:
            triggers = rule_definition['triggers']
            if not isinstance(triggers, list):
                result.add_error("Triggers must be a list")
            elif len(triggers) == 0:
                result.add_error("Rule must have at least one trigger")
            elif len(triggers) > 50:  # Reasonable limit
                result.add_error("Too many triggers (max 50)")
            else:
                for i, trigger in enumerate(triggers):
                    if not isinstance(trigger, dict):
                        result.add_error(f"Trigger {i+1} must be a dictionary")
                    elif 'id' not in trigger:
                        result.add_error(f"Trigger {i+1} must have an 'id' field")
                    else:
                        # Validate trigger ID
                        trigger_id = trigger['id']
                        if not isinstance(trigger_id, str) or not trigger_id.strip():
                            result.add_error(f"Trigger {i+1} ID must be a non-empty string")
        
        # Validate conditions (optional)
        if 'conditions' in rule_definition:
            conditions = rule_definition['conditions']
            if not isinstance(conditions, list):
                result.add_error("Conditions must be a list")
            elif len(conditions) > 50:  # Reasonable limit
                result.add_error("Too many conditions (max 50)")
            else:
                for i, condition in enumerate(conditions):
                    if not isinstance(condition, dict):
                        result.add_error(f"Condition {i+1} must be a dictionary")
                    elif 'id' not in condition:
                        result.add_error(f"Condition {i+1} must have an 'id' field")
                    else:
                        # Validate condition ID
                        condition_id = condition['id']
                        if not isinstance(condition_id, str) or not condition_id.strip():
                            result.add_error(f"Condition {i+1} ID must be a non-empty string")
        
        # Validate actions
        if 'actions' in rule_definition:
            actions = rule_definition['actions']
            if not isinstance(actions, list):
                result.add_error("Actions must be a list")
            elif len(actions) == 0:
                result.add_error("Rule must have at least one action")
            elif len(actions) > 50:  # Reasonable limit
                result.add_error("Too many actions (max 50)")
            else:
                for i, action in enumerate(actions):
                    if not isinstance(action, dict):
                        result.add_error(f"Action {i+1} must be a dictionary")
                    elif 'id' not in action:
                        result.add_error(f"Action {i+1} must have an 'id' field")
                    else:
                        # Validate action ID
                        action_id = action['id']
                        if not isinstance(action_id, str) or not action_id.strip():
                            result.add_error(f"Action {i+1} ID must be a non-empty string")
        
        # Validate enabled flag (optional, defaults to True)
        if 'enabled' in rule_definition:
            enabled = rule_definition['enabled']
            if not isinstance(enabled, bool):
                result.add_error("Enabled field must be a boolean")
        
        # Log validation failures
        if not result.is_valid:
            SecurityLogger.log_validation_failure("rule_definition", str(rule_definition), result.errors)
        
        return result
    
    def _generate_rule_uid(self, rule_name: str) -> str:
        """Generate a unique rule UID based on the rule name.
        
        Args:
            rule_name: Name of the rule
            
        Returns:
            Generated UID for the rule
        """
        import re
        import uuid
        
        # Clean the name for use in UID
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', rule_name.strip())
        clean_name = re.sub(r'_+', '_', clean_name)  # Replace multiple underscores with single
        clean_name = clean_name.strip('_')  # Remove leading/trailing underscores
        
        if not clean_name:
            clean_name = "rule"
        
        # Add a short UUID to ensure uniqueness
        short_uuid = str(uuid.uuid4())[:8]
        
        return f"{clean_name}_{short_uuid}"