"""Property-based tests for openHAB rule management tools."""

import asyncio
import json
from typing import Any, Dict, List
import pytest
from hypothesis import given, strategies as st, settings
from aioresponses import aioresponses

from openhab_mcp_server.tools.rules import RuleListTool, RuleExecuteTool, RuleCreateTool
from openhab_mcp_server.utils.config import Config


# Test data generators
@st.composite
def rule_uid_strategy(draw):
    """Generate valid openHAB rule UIDs."""
    # Rule UIDs can contain letters, numbers, underscores, hyphens, and dots
    uid = draw(st.text(
        alphabet=st.characters(min_codepoint=ord('a'), max_codepoint=ord('z')) | 
                 st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')) |
                 st.characters(min_codepoint=ord('0'), max_codepoint=ord('9')) |
                 st.just('_') | st.just('-') | st.just('.'),
        min_size=1,
        max_size=50
    ))
    # Ensure it doesn't start with a number or special character
    if uid and (uid[0].isdigit() or uid[0] in '_-.'):
        uid = 'rule_' + uid
    return uid


@st.composite
def rule_name_strategy(draw):
    """Generate valid rule names."""
    # Generate safe rule names that won't trigger security validation
    return draw(st.text(
        alphabet=st.characters(min_codepoint=ord('a'), max_codepoint=ord('z')) | 
                 st.characters(min_codepoint=ord('A'), max_codepoint=ord('Z')) |
                 st.characters(min_codepoint=ord('0'), max_codepoint=ord('9')) |
                 st.just(' ') | st.just('_') | st.just('-'),
        min_size=1,
        max_size=100
    ))


@st.composite
def rule_trigger_strategy(draw):
    """Generate valid rule trigger definitions."""
    trigger_types = ['core.ItemStateChangeTrigger', 'core.ItemCommandTrigger', 'timer.TimeOfDayTrigger']
    trigger_type = draw(st.sampled_from(trigger_types))
    
    base_trigger = {
        "id": draw(st.text(min_size=1, max_size=20)),
        "typeUID": trigger_type,
        "configuration": {}
    }
    
    if trigger_type == 'core.ItemStateChangeTrigger':
        base_trigger["configuration"]["itemName"] = draw(st.text(min_size=1, max_size=50))
    elif trigger_type == 'core.ItemCommandTrigger':
        base_trigger["configuration"]["itemName"] = draw(st.text(min_size=1, max_size=50))
        base_trigger["configuration"]["command"] = draw(st.sampled_from(['ON', 'OFF', 'OPEN', 'CLOSED']))
    elif trigger_type == 'timer.TimeOfDayTrigger':
        # Generate valid time format HH:MM
        hour = draw(st.integers(min_value=0, max_value=23))
        minute = draw(st.integers(min_value=0, max_value=59))
        base_trigger["configuration"]["time"] = f"{hour:02d}:{minute:02d}"
    
    return base_trigger


@st.composite
def rule_action_strategy(draw):
    """Generate valid rule action definitions."""
    action_types = ['core.ItemCommandAction', 'core.RunRuleAction', 'media.SayAction']
    action_type = draw(st.sampled_from(action_types))
    
    base_action = {
        "id": draw(st.text(min_size=1, max_size=20)),
        "typeUID": action_type,
        "configuration": {}
    }
    
    if action_type == 'core.ItemCommandAction':
        base_action["configuration"]["itemName"] = draw(st.text(min_size=1, max_size=50))
        base_action["configuration"]["command"] = draw(st.sampled_from(['ON', 'OFF', 'OPEN', 'CLOSED']))
    elif action_type == 'core.RunRuleAction':
        base_action["configuration"]["ruleUIDs"] = [draw(rule_uid_strategy())]
    elif action_type == 'media.SayAction':
        base_action["configuration"]["text"] = draw(st.text(min_size=1, max_size=100))
    
    return base_action


@st.composite
def rule_condition_strategy(draw):
    """Generate valid rule condition definitions."""
    return {
        "id": draw(st.text(min_size=1, max_size=20)),
        "typeUID": draw(st.sampled_from(['core.GenericEventCondition', 'script.ScriptCondition'])),
        "configuration": draw(st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(st.text(), st.integers(), st.booleans())
        ))
    }


@st.composite
def rule_response_strategy(draw):
    """Generate valid openHAB rule response data."""
    uid = draw(rule_uid_strategy())
    name = draw(rule_name_strategy())
    
    return {
        "uid": uid,
        "name": name,
        "description": draw(st.one_of(st.none(), st.text(min_size=0, max_size=200))),
        "status": draw(st.sampled_from(['ENABLED', 'DISABLED', 'IDLE', 'RUNNING'])),
        "enabled": draw(st.booleans()),
        "visibility": draw(st.sampled_from(['VISIBLE', 'HIDDEN'])),
        "triggers": draw(st.lists(rule_trigger_strategy(), min_size=1, max_size=3)),
        "conditions": draw(st.lists(rule_condition_strategy(), max_size=2)),
        "actions": draw(st.lists(rule_action_strategy(), min_size=1, max_size=3))
    }


@st.composite
def rule_definition_strategy(draw):
    """Generate valid rule definition for creation."""
    return {
        "name": draw(rule_name_strategy()),
        "description": draw(st.one_of(st.none(), st.text(min_size=0, max_size=200))),
        "triggers": draw(st.lists(rule_trigger_strategy(), min_size=1, max_size=3)),
        "conditions": draw(st.lists(rule_condition_strategy(), max_size=2)),
        "actions": draw(st.lists(rule_action_strategy(), min_size=1, max_size=3)),
        "enabled": draw(st.booleans())
    }


class TestRuleManagementProperties:
    """Property-based tests for rule management tools."""
    
    def _get_test_config(self):
        """Get test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @given(rule_definition=rule_definition_strategy())
    @settings(max_examples=100, deadline=10000)
    async def test_property_rule_management_consistency(self, rule_definition):
        """**Feature: openhab-mcp-server, Property 8: Rule management consistency**
        
        For any valid rule definition, creating or modifying the rule should implement 
        the automation logic according to the specifications.
        
        **Validates: Requirements 3.3**
        """
        config = self._get_test_config()
        create_tool = RuleCreateTool(config)
        list_tool = RuleListTool(config)
        execute_tool = RuleExecuteTool(config)
        
        # Generate a unique UID for this test
        test_uid = f"test_rule_{hash(str(rule_definition)) % 10000}"
        
        with aioresponses() as mock:
            # Mock rule creation
            mock.post(
                "http://test-openhab:8080/rest/rules",
                payload={"uid": test_uid},
                status=201
            )
            
            # Mock rule listing to verify creation
            created_rule = {
                "uid": test_uid,
                "name": rule_definition["name"],
                "description": rule_definition.get("description"),
                "status": "ENABLED" if rule_definition.get("enabled", True) else "DISABLED",
                "enabled": rule_definition.get("enabled", True),
                "visibility": "VISIBLE",
                "triggers": rule_definition["triggers"],
                "conditions": rule_definition.get("conditions", []),
                "actions": rule_definition["actions"]
            }
            
            mock.get(
                "http://test-openhab:8080/rest/rules",
                payload=[created_rule],
                status=200
            )
            
            # Mock rule retrieval for execution check
            mock.get(
                f"http://test-openhab:8080/rest/rules/{test_uid}",
                payload=created_rule,
                status=200
            )
            
            # Mock rule execution
            mock.post(
                f"http://test-openhab:8080/rest/rules/{test_uid}/runnow",
                status=200
            )
            
            # Property 1: Rule creation should succeed with valid definition
            create_result = await create_tool.execute(rule_definition)
            assert len(create_result) == 1
            assert "Successfully created rule" in create_result[0].text
            assert test_uid in create_result[0].text
            
            # Property 2: Created rule should appear in rule list with correct properties
            list_result = await list_tool.execute()
            assert len(list_result) == 1
            list_text = list_result[0].text
            
            # Rule should be listed with its name and UID
            assert rule_definition["name"] in list_text
            assert test_uid in list_text
            
            # Rule status should match enabled flag
            expected_status = "ENABLED" if rule_definition.get("enabled", True) else "DISABLED"
            assert expected_status in list_text
            
            # Component counts should be correct
            trigger_count = len(rule_definition["triggers"])
            condition_count = len(rule_definition.get("conditions", []))
            action_count = len(rule_definition["actions"])
            assert f"{trigger_count} triggers, {condition_count} conditions, {action_count} actions" in list_text
            
            # Property 3: Enabled rules should be executable
            if rule_definition.get("enabled", True):
                execute_result = await execute_tool.execute(test_uid)
                assert len(execute_result) == 1
                assert "Successfully executed rule" in execute_result[0].text
                assert test_uid in execute_result[0].text
    
    @given(rules_data=st.lists(rule_response_strategy(), min_size=0, max_size=10))
    @settings(max_examples=50, deadline=5000)
    async def test_property_rule_listing_completeness(self, rules_data):
        """Test that rule listing returns complete information for all rules."""
        config = self._get_test_config()
        tool = RuleListTool(config)
        
        with aioresponses() as mock:
            # Mock rules list response
            mock.get(
                "http://test-openhab:8080/rest/rules",
                payload=rules_data,
                status=200
            )
            
            result = await tool.execute()
            
            # Property: Should return single response with all rules
            assert len(result) == 1
            response_text = result[0].text
            
            if not rules_data:
                # Property: Empty list should be handled correctly
                assert "No automation rules found" in response_text
            else:
                # Property: All rules should be present in the response
                assert f"Found {len(rules_data)} automation rules:" in response_text
                
                for rule in rules_data:
                    # Each rule should appear with its name and UID
                    assert rule["name"] in response_text
                    assert rule["uid"] in response_text
                    assert rule["status"] in response_text
                    
                    # Enabled status should be shown
                    enabled_text = "Yes" if rule["enabled"] else "No"
                    assert enabled_text in response_text
    
    @given(
        rule_uid=rule_uid_strategy(),
        rule_enabled=st.booleans()
    )
    @settings(max_examples=50, deadline=5000)
    async def test_property_rule_execution_validation(self, rule_uid, rule_enabled):
        """Test that rule execution properly validates rule state."""
        config = self._get_test_config()
        tool = RuleExecuteTool(config)
        
        rule_data = {
            "uid": rule_uid,
            "name": f"Test Rule {rule_uid}",
            "enabled": rule_enabled,
            "status": "ENABLED" if rule_enabled else "DISABLED"
        }
        
        with aioresponses() as mock:
            # Mock rule retrieval
            mock.get(
                f"http://test-openhab:8080/rest/rules/{rule_uid}",
                payload=rule_data,
                status=200
            )
            
            if rule_enabled:
                # Mock successful execution for enabled rules
                mock.post(
                    f"http://test-openhab:8080/rest/rules/{rule_uid}/runnow",
                    status=200
                )
            
            result = await tool.execute(rule_uid)
            
            # Property: Response should reflect rule's enabled state
            assert len(result) == 1
            response_text = result[0].text
            
            if rule_enabled:
                # Property: Enabled rules should execute successfully
                assert "Successfully executed rule" in response_text
            else:
                # Property: Disabled rules should be rejected with clear message
                assert "Cannot execute rule" in response_text
                assert "rule is disabled" in response_text
    
    @given(invalid_rule_def=st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(st.text(), st.integers(), st.booleans(), st.none()),
        min_size=0,
        max_size=5
    ))
    @settings(max_examples=50, deadline=5000)
    async def test_property_rule_validation_completeness(self, invalid_rule_def):
        """Test that rule validation catches invalid definitions."""
        config = self._get_test_config()
        tool = RuleCreateTool(config)
        
        # Property: Invalid rule definitions should be rejected
        result = await tool.execute(invalid_rule_def)
        
        assert len(result) == 1
        response_text = result[0].text
        
        # Property: Validation errors should be clearly reported
        if not invalid_rule_def.get("name"):
            assert "Missing required field: name" in response_text or "Rule name" in response_text
        
        if not invalid_rule_def.get("triggers"):
            assert "Missing required field: triggers" in response_text or "Triggers" in response_text
        
        if not invalid_rule_def.get("actions"):
            assert "Missing required field: actions" in response_text or "Actions" in response_text


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
