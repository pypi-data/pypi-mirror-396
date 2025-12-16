"""Unit tests for openHAB rule operation tools."""

import pytest
from unittest.mock import AsyncMock, patch
from aioresponses import aioresponses

from openhab_mcp_server.tools.rules import RuleListTool, RuleExecuteTool, RuleCreateTool
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.utils.openhab_client import OpenHABError


class TestRuleListTool:
    """Unit tests for RuleListTool."""
    
    def _get_test_config(self):
        """Get test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.fixture
    def tool(self):
        """Create RuleListTool instance for testing."""
        return RuleListTool(self._get_test_config())
    
    async def test_execute_success_all_rules(self, tool):
        """Test successful listing of all rules."""
        rules_data = [
            {
                "uid": "rule1",
                "name": "Morning Lights",
                "description": "Turn on lights in the morning",
                "status": "ENABLED",
                "enabled": True,
                "visibility": "VISIBLE",
                "triggers": [
                    {"id": "trigger1", "typeUID": "timer.TimeOfDayTrigger"}
                ],
                "conditions": [],
                "actions": [
                    {"id": "action1", "typeUID": "core.ItemCommandAction"}
                ]
            },
            {
                "uid": "rule2",
                "name": "Security Alert",
                "description": "Alert when door opens at night",
                "status": "DISABLED",
                "enabled": False,
                "visibility": "VISIBLE",
                "triggers": [
                    {"id": "trigger1", "typeUID": "core.ItemStateChangeTrigger"}
                ],
                "conditions": [
                    {"id": "condition1", "typeUID": "core.TimeOfDayCondition"}
                ],
                "actions": [
                    {"id": "action1", "typeUID": "media.SayAction"},
                    {"id": "action2", "typeUID": "core.ItemCommandAction"}
                ]
            }
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/rules",
                payload=rules_data,
                status=200
            )
            
            result = await tool.execute()
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Found 2 automation rules:" in response_text
            assert "Morning Lights (rule1)" in response_text
            assert "Status: ENABLED" in response_text
            assert "Enabled: Yes" in response_text
            assert "Turn on lights in the morning" in response_text
            assert "1 triggers, 0 conditions, 1 actions" in response_text
            
            assert "Security Alert (rule2)" in response_text
            assert "Status: DISABLED" in response_text
            assert "Enabled: No" in response_text
            assert "Alert when door opens at night" in response_text
            assert "1 triggers, 1 conditions, 2 actions" in response_text
    
    async def test_execute_success_filtered_rules(self, tool):
        """Test successful listing with status filter."""
        enabled_rules = [
            {
                "uid": "rule1",
                "name": "Active Rule",
                "status": "ENABLED",
                "enabled": True,
                "triggers": [{"id": "t1"}],
                "conditions": [],
                "actions": [{"id": "a1"}]
            }
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/rules",
                payload=enabled_rules,
                status=200
            )
            
            result = await tool.execute("ENABLED")
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Found 1 automation rules with status 'ENABLED':" in response_text
            assert "Active Rule (rule1)" in response_text
            assert "Status: ENABLED" in response_text
    
    async def test_execute_no_rules_found(self, tool):
        """Test handling when no rules are found."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/rules",
                payload=[],
                status=200
            )
            
            result = await tool.execute()
            
            assert len(result) == 1
            assert "No automation rules found" in result[0].text
    
    async def test_execute_no_rules_found_with_filter(self, tool):
        """Test handling when no rules match filter."""
        all_rules = [
            {
                "uid": "rule1",
                "name": "Test Rule",
                "status": "ENABLED",
                "enabled": True,
                "triggers": [{"id": "t1"}],
                "conditions": [],
                "actions": [{"id": "a1"}]
            }
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/rules",
                payload=all_rules,
                status=200
            )
            
            result = await tool.execute("DISABLED")
            
            assert len(result) == 1
            assert "No rules found with status 'DISABLED'" in result[0].text
    
    async def test_execute_invalid_status_filter(self, tool):
        """Test validation of invalid status filter."""
        result = await tool.execute("INVALID_STATUS")
        
        assert len(result) == 1
        assert "Invalid status filter" in result[0].text
        assert "Valid statuses:" in result[0].text
    
    async def test_execute_empty_status_filter(self, tool):
        """Test validation of empty status filter."""
        result = await tool.execute("")
        
        assert len(result) == 1
        assert "Invalid status filter" in result[0].text
        assert "Status filter cannot be empty" in result[0].text
    
    async def test_execute_openhab_error(self, tool):
        """Test handling of openHAB API errors."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/rules",
                status=500,
                payload={"message": "Internal Server Error"}
            )
            
            result = await tool.execute()
            
            assert len(result) == 1
            assert "Error listing rules" in result[0].text
    
    async def test_execute_rule_without_description(self, tool):
        """Test formatting rules without descriptions."""
        rules_data = [
            {
                "uid": "rule1",
                "name": "Simple Rule",
                "status": "ENABLED",
                "enabled": True,
                "triggers": [{"id": "t1"}],
                "conditions": [],
                "actions": [{"id": "a1"}]
            }
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/rules",
                payload=rules_data,
                status=200
            )
            
            result = await tool.execute()
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Simple Rule (rule1)" in response_text
            assert "Description:" not in response_text
    
    async def test_execute_rule_with_hidden_visibility(self, tool):
        """Test formatting rules with non-visible visibility."""
        rules_data = [
            {
                "uid": "rule1",
                "name": "Hidden Rule",
                "status": "ENABLED",
                "enabled": True,
                "visibility": "HIDDEN",
                "triggers": [{"id": "t1"}],
                "conditions": [],
                "actions": [{"id": "a1"}]
            }
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/rules",
                payload=rules_data,
                status=200
            )
            
            result = await tool.execute()
            
            assert len(result) == 1
            response_text = result[0].text
            assert "Hidden Rule (rule1)" in response_text
            assert "Visibility: HIDDEN" in response_text


class TestRuleExecuteTool:
    """Unit tests for RuleExecuteTool."""
    
    def _get_test_config(self):
        """Get test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.fixture
    def tool(self):
        """Create RuleExecuteTool instance for testing."""
        return RuleExecuteTool(self._get_test_config())
    
    async def test_execute_success_enabled_rule(self, tool):
        """Test successful execution of enabled rule."""
        rule_data = {
            "uid": "test_rule",
            "name": "Test Rule",
            "enabled": True,
            "status": "ENABLED"
        }
        
        with aioresponses() as mock:
            # Mock rule retrieval
            mock.get(
                "http://test-openhab:8080/rest/rules/test_rule",
                payload=rule_data,
                status=200
            )
            
            # Mock rule execution
            mock.post(
                "http://test-openhab:8080/rest/rules/test_rule/runnow",
                status=200
            )
            
            result = await tool.execute("test_rule")
            
            assert len(result) == 1
            assert "Successfully executed rule 'Test Rule' (test_rule)" in result[0].text
    
    async def test_execute_disabled_rule(self, tool):
        """Test execution attempt on disabled rule."""
        rule_data = {
            "uid": "disabled_rule",
            "name": "Disabled Rule",
            "enabled": False,
            "status": "DISABLED"
        }
        
        with aioresponses() as mock:
            # Mock rule retrieval
            mock.get(
                "http://test-openhab:8080/rest/rules/disabled_rule",
                payload=rule_data,
                status=200
            )
            
            result = await tool.execute("disabled_rule")
            
            assert len(result) == 1
            assert "Cannot execute rule 'Disabled Rule' (disabled_rule) - rule is disabled" in result[0].text
    
    async def test_execute_rule_not_found(self, tool):
        """Test execution of non-existent rule."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/rules/nonexistent_rule",
                status=404
            )
            
            result = await tool.execute("nonexistent_rule")
            
            assert len(result) == 1
            assert "Rule 'nonexistent_rule' not found" in result[0].text
    
    async def test_execute_execution_failure(self, tool):
        """Test handling of rule execution failure."""
        rule_data = {
            "uid": "failing_rule",
            "name": "Failing Rule",
            "enabled": True,
            "status": "ENABLED"
        }
        
        with aioresponses() as mock:
            # Mock rule retrieval
            mock.get(
                "http://test-openhab:8080/rest/rules/failing_rule",
                payload=rule_data,
                status=200
            )
            
            # Mock execution failure - multiple responses for retry attempts
            for _ in range(4):  # Initial + 3 retries
                mock.post(
                    "http://test-openhab:8080/rest/rules/failing_rule/runnow",
                    status=500,
                    payload={"message": "Execution failed"}
                )
            
            result = await tool.execute("failing_rule")
            
            assert len(result) == 1
            assert "Failed to execute rule 'Failing Rule' (failing_rule)" in result[0].text
    
    async def test_execute_invalid_rule_uid(self, tool):
        """Test validation of invalid rule UID."""
        # Test empty UID
        result = await tool.execute("")
        assert len(result) == 1
        assert "Invalid rule UID" in result[0].text
        assert "Rule UID cannot be empty" in result[0].text
        
        # Test UID with spaces
        result = await tool.execute("invalid rule")
        assert len(result) == 1
        assert "Invalid rule UID" in result[0].text
        assert "Rule UID cannot contain spaces" in result[0].text
        
        # Test very long UID
        long_uid = "a" * 201
        result = await tool.execute(long_uid)
        assert len(result) == 1
        assert "Invalid rule UID" in result[0].text
        assert "Input too long (max 200 characters)" in result[0].text
    
    async def test_execute_openhab_error(self, tool):
        """Test handling of openHAB API errors."""
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/rules/test_rule",
                status=500,
                payload={"message": "Internal Server Error"}
            )
            
            result = await tool.execute("test_rule")
            
            assert len(result) == 1
            assert "Error executing rule" in result[0].text


class TestRuleCreateTool:
    """Unit tests for RuleCreateTool."""
    
    def _get_test_config(self):
        """Get test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.fixture
    def tool(self):
        """Create RuleCreateTool instance for testing."""
        return RuleCreateTool(self._get_test_config())
    
    async def test_execute_success_with_uid(self, tool):
        """Test successful rule creation with provided UID."""
        rule_definition = {
            "uid": "custom_rule_uid",
            "name": "Test Rule",
            "description": "A test rule",
            "triggers": [
                {
                    "id": "trigger1",
                    "typeUID": "core.ItemStateChangeTrigger",
                    "configuration": {"itemName": "TestItem"}
                }
            ],
            "conditions": [],
            "actions": [
                {
                    "id": "action1",
                    "typeUID": "core.ItemCommandAction",
                    "configuration": {"itemName": "TestItem", "command": "ON"}
                }
            ],
            "enabled": True
        }
        
        with aioresponses() as mock:
            mock.post(
                "http://test-openhab:8080/rest/rules",
                payload={"uid": "custom_rule_uid"},
                status=201
            )
            
            result = await tool.execute(rule_definition)
            
            assert len(result) == 1
            assert "Successfully created rule 'Test Rule' with UID: custom_rule_uid" in result[0].text
    
    async def test_execute_success_without_uid(self, tool):
        """Test successful rule creation with generated UID."""
        rule_definition = {
            "name": "Auto UID Rule",
            "triggers": [
                {
                    "id": "trigger1",
                    "typeUID": "timer.TimeOfDayTrigger",
                    "configuration": {"time": "08:00"}
                }
            ],
            "actions": [
                {
                    "id": "action1",
                    "typeUID": "core.ItemCommandAction",
                    "configuration": {"itemName": "TestItem", "command": "ON"}
                }
            ]
        }
        
        with aioresponses() as mock:
            mock.post(
                "http://test-openhab:8080/rest/rules",
                payload={"uid": "Auto_UID_Rule_12345678"},
                status=201
            )
            
            result = await tool.execute(rule_definition)
            
            assert len(result) == 1
            assert "Successfully created rule 'Auto UID Rule' with UID: Auto_UID_Rule_12345678" in result[0].text
    
    async def test_execute_creation_failure(self, tool):
        """Test handling of rule creation failure."""
        rule_definition = {
            "name": "Failing Rule",
            "triggers": [
                {
                    "id": "trigger1",
                    "typeUID": "core.ItemStateChangeTrigger",
                    "configuration": {"itemName": "TestItem"}
                }
            ],
            "actions": [
                {
                    "id": "action1",
                    "typeUID": "core.ItemCommandAction",
                    "configuration": {"itemName": "TestItem", "command": "ON"}
                }
            ]
        }
        
        with aioresponses() as mock:
            mock.post(
                "http://test-openhab:8080/rest/rules",
                status=400,
                payload={"message": "Invalid rule definition"}
            )
            
            result = await tool.execute(rule_definition)
            
            assert len(result) == 1
            assert "Failed to create rule - check rule definition and openHAB logs" in result[0].text
    
    async def test_execute_invalid_rule_definition(self, tool):
        """Test validation of invalid rule definitions."""
        # Test missing required fields
        invalid_rule = {}
        result = await tool.execute(invalid_rule)
        assert len(result) == 1
        assert "Invalid rule definition" in result[0].text
        assert "Missing required field: name" in result[0].text
        assert "Missing required field: triggers" in result[0].text
        assert "Missing required field: actions" in result[0].text
        
        # Test empty name
        invalid_rule = {
            "name": "",
            "triggers": [{"id": "t1"}],
            "actions": [{"id": "a1"}]
        }
        result = await tool.execute(invalid_rule)
        assert len(result) == 1
        assert "Invalid rule definition" in result[0].text
        assert "Field 'name' cannot be empty" in result[0].text
        
        # Test empty triggers
        invalid_rule = {
            "name": "Test Rule",
            "triggers": [],
            "actions": [{"id": "a1"}]
        }
        result = await tool.execute(invalid_rule)
        assert len(result) == 1
        assert "Invalid rule definition" in result[0].text
        assert "Rule must have at least one trigger" in result[0].text
        
        # Test empty actions
        invalid_rule = {
            "name": "Test Rule",
            "triggers": [{"id": "t1"}],
            "actions": []
        }
        result = await tool.execute(invalid_rule)
        assert len(result) == 1
        assert "Invalid rule definition" in result[0].text
        assert "Rule must have at least one action" in result[0].text
    
    async def test_execute_invalid_trigger_format(self, tool):
        """Test validation of invalid trigger format."""
        invalid_rule = {
            "name": "Test Rule",
            "triggers": [
                {"typeUID": "core.ItemStateChangeTrigger"}  # Missing 'id' field
            ],
            "actions": [
                {"id": "action1", "typeUID": "core.ItemCommandAction"}
            ]
        }
        
        result = await tool.execute(invalid_rule)
        assert len(result) == 1
        assert "Invalid rule definition" in result[0].text
        assert "Trigger 1 must have an 'id' field" in result[0].text
    
    async def test_execute_invalid_action_format(self, tool):
        """Test validation of invalid action format."""
        invalid_rule = {
            "name": "Test Rule",
            "triggers": [
                {"id": "trigger1", "typeUID": "core.ItemStateChangeTrigger"}
            ],
            "actions": [
                {"typeUID": "core.ItemCommandAction"}  # Missing 'id' field
            ]
        }
        
        result = await tool.execute(invalid_rule)
        assert len(result) == 1
        assert "Invalid rule definition" in result[0].text
        assert "Action 1 must have an 'id' field" in result[0].text
    
    async def test_execute_invalid_condition_format(self, tool):
        """Test validation of invalid condition format."""
        invalid_rule = {
            "name": "Test Rule",
            "triggers": [
                {"id": "trigger1", "typeUID": "core.ItemStateChangeTrigger"}
            ],
            "conditions": [
                {"typeUID": "core.TimeOfDayCondition"}  # Missing 'id' field
            ],
            "actions": [
                {"id": "action1", "typeUID": "core.ItemCommandAction"}
            ]
        }
        
        result = await tool.execute(invalid_rule)
        assert len(result) == 1
        assert "Invalid rule definition" in result[0].text
        assert "Condition 1 must have an 'id' field" in result[0].text
    
    async def test_execute_non_dict_rule_definition(self, tool):
        """Test validation of non-dictionary rule definition."""
        result = await tool.execute("not a dict")
        assert len(result) == 1
        assert "Invalid rule definition" in result[0].text
        assert "Rule definition must be a dictionary" in result[0].text
    
    async def test_execute_invalid_enabled_field(self, tool):
        """Test validation of invalid enabled field."""
        invalid_rule = {
            "name": "Test Rule",
            "triggers": [
                {"id": "trigger1", "typeUID": "core.ItemStateChangeTrigger"}
            ],
            "actions": [
                {"id": "action1", "typeUID": "core.ItemCommandAction"}
            ],
            "enabled": "yes"  # Should be boolean
        }
        
        result = await tool.execute(invalid_rule)
        assert len(result) == 1
        assert "Invalid rule definition" in result[0].text
        assert "Enabled field must be a boolean" in result[0].text
    
    async def test_execute_openhab_error(self, tool):
        """Test handling of openHAB API errors."""
        rule_definition = {
            "name": "Test Rule",
            "triggers": [
                {"id": "trigger1", "typeUID": "core.ItemStateChangeTrigger"}
            ],
            "actions": [
                {"id": "action1", "typeUID": "core.ItemCommandAction"}
            ]
        }
        
        with aioresponses() as mock:
            # Mock multiple responses for retry attempts
            for _ in range(4):  # Initial + 3 retries
                mock.post(
                    "http://test-openhab:8080/rest/rules",
                    status=500,
                    payload={"message": "Internal Server Error"}
                )
            
            result = await tool.execute(rule_definition)
            
            assert len(result) == 1
            assert "Failed to create rule" in result[0].text
    
    def test_generate_rule_uid(self, tool):
        """Test UID generation from rule names."""
        # Test normal name
        uid = tool._generate_rule_uid("My Test Rule")
        assert uid.startswith("My_Test_Rule_")
        assert len(uid.split("_")[-1]) == 8  # UUID part
        
        # Test name with special characters
        uid = tool._generate_rule_uid("Rule@#$%Name!")
        assert uid.startswith("Rule_Name_")
        
        # Test empty name
        uid = tool._generate_rule_uid("")
        assert uid.startswith("rule_")
        
        # Test name with only special characters
        uid = tool._generate_rule_uid("@#$%")
        assert uid.startswith("rule_")


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
