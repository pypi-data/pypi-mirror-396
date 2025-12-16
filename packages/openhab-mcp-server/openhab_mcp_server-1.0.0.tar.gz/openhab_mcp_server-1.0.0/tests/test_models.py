"""Unit tests for data models."""

import pytest
from pydantic import ValidationError

from openhab_mcp_server.models import (
    ItemState,
    ThingStatus,
    RuleDefinition,
    SystemInfo,
    MCPError,
    ValidationResult,
    AddonInfo,
)


class TestItemState:
    """Unit tests for ItemState model."""
    
    def test_valid_item_state_creation(self):
        """Test creating a valid ItemState with all fields."""
        item = ItemState(
            name="TestItem",
            state="ON",
            type="Switch",
            label="Test Switch",
            category="Light",
            tags=["indoor", "living_room"]
        )
        
        assert item.name == "TestItem"
        assert item.state == "ON"
        assert item.type == "Switch"
        assert item.label == "Test Switch"
        assert item.category == "Light"
        assert item.tags == ["indoor", "living_room"]
    
    def test_minimal_item_state_creation(self):
        """Test creating ItemState with only required fields."""
        item = ItemState(
            name="MinimalItem",
            state="OFF",
            type="Switch"
        )
        
        assert item.name == "MinimalItem"
        assert item.state == "OFF"
        assert item.type == "Switch"
        assert item.label is None
        assert item.category is None
        assert item.tags == []
    
    def test_item_name_validation_empty(self):
        """Test that empty item names are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ItemState(name="", state="ON", type="Switch")
        
        assert "Item name cannot be empty" in str(exc_info.value)
    
    def test_item_name_validation_whitespace(self):
        """Test that whitespace-only item names are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ItemState(name="   ", state="ON", type="Switch")
        
        assert "Item name cannot be empty" in str(exc_info.value)
    
    def test_item_name_validation_spaces(self):
        """Test that item names with spaces are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ItemState(name="Test Item", state="ON", type="Switch")
        
        assert "Item name cannot contain spaces" in str(exc_info.value)
    
    def test_item_type_validation_invalid(self):
        """Test that invalid item types are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ItemState(name="TestItem", state="ON", type="InvalidType")
        
        assert "Invalid item type" in str(exc_info.value)
    
    def test_item_type_validation_valid_types(self):
        """Test that all valid item types are accepted."""
        valid_types = ['Switch', 'Dimmer', 'Number', 'String', 'DateTime', 
                      'Contact', 'Rollershutter', 'Color', 'Location', 'Player', 'Group']
        
        for item_type in valid_types:
            item = ItemState(name="TestItem", state="TEST", type=item_type)
            assert item.type == item_type
    
    def test_serialization_round_trip(self):
        """Test serialization and deserialization consistency."""
        original = ItemState(
            name="TestItem",
            state="ON",
            type="Switch",
            label="Test Switch",
            category="Light",
            tags=["indoor", "living_room"]
        )
        
        # Serialize to dict
        data = original.model_dump()
        
        # Deserialize back to object
        restored = ItemState(**data)
        
        # Verify all fields match
        assert restored.name == original.name
        assert restored.state == original.state
        assert restored.type == original.type
        assert restored.label == original.label
        assert restored.category == original.category
        assert restored.tags == original.tags
    
    def test_json_serialization_round_trip(self):
        """Test JSON serialization and deserialization consistency."""
        original = ItemState(
            name="TestItem",
            state="ON",
            type="Switch",
            label="Test Switch",
            category="Light",
            tags=["indoor", "living_room"]
        )
        
        # Serialize to JSON
        json_data = original.model_dump_json()
        
        # Deserialize back to object
        restored = ItemState.model_validate_json(json_data)
        
        # Verify all fields match
        assert restored.name == original.name
        assert restored.state == original.state
        assert restored.type == original.type
        assert restored.label == original.label
        assert restored.category == original.category
        assert restored.tags == original.tags


class TestThingStatus:
    """Unit tests for ThingStatus model."""
    
    def test_valid_thing_status_creation(self):
        """Test creating a valid ThingStatus with all fields."""
        thing = ThingStatus(
            uid="zwave:device:controller:node2",
            status="ONLINE",
            status_detail="NONE",
            label="Living Room Light",
            bridge_uid="zwave:serial_zstick:controller",
            configuration={"parameter1": "value1", "parameter2": 42}
        )
        
        assert thing.uid == "zwave:device:controller:node2"
        assert thing.status == "ONLINE"
        assert thing.status_detail == "NONE"
        assert thing.label == "Living Room Light"
        assert thing.bridge_uid == "zwave:serial_zstick:controller"
        assert thing.configuration == {"parameter1": "value1", "parameter2": 42}
    
    def test_minimal_thing_status_creation(self):
        """Test creating ThingStatus with only required fields."""
        thing = ThingStatus(
            uid="binding:type:id",
            status="ONLINE",
            status_detail="NONE",
            label="Test Thing"
        )
        
        assert thing.uid == "binding:type:id"
        assert thing.status == "ONLINE"
        assert thing.status_detail == "NONE"
        assert thing.label == "Test Thing"
        assert thing.bridge_uid is None
        assert thing.configuration == {}
    
    def test_thing_uid_validation_empty(self):
        """Test that empty thing UIDs are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ThingStatus(uid="", status="ONLINE", status_detail="NONE", label="Test")
        
        assert "Thing UID cannot be empty" in str(exc_info.value)
    
    def test_thing_uid_validation_invalid_format(self):
        """Test that invalid UID formats are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ThingStatus(uid="invalid", status="ONLINE", status_detail="NONE", label="Test")
        
        assert "Thing UID must contain at least binding and type" in str(exc_info.value)
    
    def test_thing_uid_validation_empty_parts(self):
        """Test that UIDs with empty parts are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ThingStatus(uid="binding::id", status="ONLINE", status_detail="NONE", label="Test")
        
        assert "Thing UID parts cannot be empty" in str(exc_info.value)
    
    def test_thing_status_validation_invalid(self):
        """Test that invalid thing statuses are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ThingStatus(uid="binding:type:id", status="INVALID", status_detail="NONE", label="Test")
        
        assert "Invalid thing status" in str(exc_info.value)
    
    def test_thing_status_validation_valid_statuses(self):
        """Test that all valid thing statuses are accepted."""
        valid_statuses = ['ONLINE', 'OFFLINE', 'UNKNOWN', 'INITIALIZING', 'REMOVING', 'REMOVED']
        
        for status in valid_statuses:
            thing = ThingStatus(
                uid="binding:type:id",
                status=status,
                status_detail="NONE",
                label="Test Thing"
            )
            assert thing.status == status
    
    def test_serialization_round_trip(self):
        """Test serialization and deserialization consistency."""
        original = ThingStatus(
            uid="zwave:device:controller:node2",
            status="ONLINE",
            status_detail="NONE",
            label="Living Room Light",
            bridge_uid="zwave:serial_zstick:controller",
            configuration={"parameter1": "value1", "parameter2": 42}
        )
        
        # Serialize to dict
        data = original.model_dump()
        
        # Deserialize back to object
        restored = ThingStatus(**data)
        
        # Verify all fields match
        assert restored.uid == original.uid
        assert restored.status == original.status
        assert restored.status_detail == original.status_detail
        assert restored.label == original.label
        assert restored.bridge_uid == original.bridge_uid
        assert restored.configuration == original.configuration


class TestRuleDefinition:
    """Unit tests for RuleDefinition model."""
    
    def test_valid_rule_definition_creation(self):
        """Test creating a valid RuleDefinition with all fields."""
        rule = RuleDefinition(
            name="Test Rule",
            description="A test automation rule",
            triggers=[{"type": "ItemStateChangeTrigger", "itemName": "TestItem"}],
            conditions=[{"type": "ItemStateCondition", "itemName": "TestItem", "state": "ON"}],
            actions=[{"type": "ItemCommandAction", "itemName": "TargetItem", "command": "ON"}],
            enabled=True
        )
        
        assert rule.name == "Test Rule"
        assert rule.description == "A test automation rule"
        assert len(rule.triggers) == 1
        assert len(rule.conditions) == 1
        assert len(rule.actions) == 1
        assert rule.enabled is True
    
    def test_minimal_rule_definition_creation(self):
        """Test creating RuleDefinition with only required fields."""
        rule = RuleDefinition(
            name="Minimal Rule",
            triggers=[{"type": "ItemStateChangeTrigger", "itemName": "TestItem"}],
            actions=[{"type": "ItemCommandAction", "itemName": "TargetItem", "command": "ON"}]
        )
        
        assert rule.name == "Minimal Rule"
        assert rule.description is None
        assert len(rule.triggers) == 1
        assert rule.conditions == []
        assert len(rule.actions) == 1
        assert rule.enabled is True
    
    def test_rule_name_validation_empty(self):
        """Test that empty rule names are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleDefinition(
                name="",
                triggers=[{"type": "ItemStateChangeTrigger"}],
                actions=[{"type": "ItemCommandAction"}]
            )
        
        assert "Rule name cannot be empty" in str(exc_info.value)
    
    def test_rule_triggers_validation_empty(self):
        """Test that rules without triggers are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleDefinition(
                name="Test Rule",
                triggers=[],
                actions=[{"type": "ItemCommandAction"}]
            )
        
        assert "Rule must have at least one trigger" in str(exc_info.value)
    
    def test_rule_actions_validation_empty(self):
        """Test that rules without actions are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleDefinition(
                name="Test Rule",
                triggers=[{"type": "ItemStateChangeTrigger"}],
                actions=[]
            )
        
        assert "Rule must have at least one action" in str(exc_info.value)
    
    def test_serialization_round_trip(self):
        """Test serialization and deserialization consistency."""
        original = RuleDefinition(
            name="Test Rule",
            description="A test automation rule",
            triggers=[{"type": "ItemStateChangeTrigger", "itemName": "TestItem"}],
            conditions=[{"type": "ItemStateCondition", "itemName": "TestItem", "state": "ON"}],
            actions=[{"type": "ItemCommandAction", "itemName": "TargetItem", "command": "ON"}],
            enabled=False
        )
        
        # Serialize to dict
        data = original.model_dump()
        
        # Deserialize back to object
        restored = RuleDefinition(**data)
        
        # Verify all fields match
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.triggers == original.triggers
        assert restored.conditions == original.conditions
        assert restored.actions == original.actions
        assert restored.enabled == original.enabled


class TestSystemInfo:
    """Unit tests for SystemInfo model."""
    
    def test_valid_system_info_creation(self):
        """Test creating a valid SystemInfo with all fields."""
        system = SystemInfo(
            version="3.4.0",
            build_string="Release Build",
            locale="en_US",
            measurement_system="metric",
            start_level=100
        )
        
        assert system.version == "3.4.0"
        assert system.build_string == "Release Build"
        assert system.locale == "en_US"
        assert system.measurement_system == "metric"
        assert system.start_level == 100
    
    def test_version_validation_empty(self):
        """Test that empty versions are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SystemInfo(
                version="",
                build_string="Release Build",
                locale="en_US",
                measurement_system="metric",
                start_level=100
            )
        
        assert "Version cannot be empty" in str(exc_info.value)
    
    def test_measurement_system_validation_invalid(self):
        """Test that invalid measurement systems are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SystemInfo(
                version="3.4.0",
                build_string="Release Build",
                locale="en_US",
                measurement_system="invalid",
                start_level=100
            )
        
        assert "Invalid measurement system" in str(exc_info.value)
    
    def test_measurement_system_validation_case_insensitive(self):
        """Test that measurement system validation is case insensitive."""
        system1 = SystemInfo(
            version="3.4.0",
            build_string="Release Build",
            locale="en_US",
            measurement_system="METRIC",
            start_level=100
        )
        
        system2 = SystemInfo(
            version="3.4.0",
            build_string="Release Build",
            locale="en_US",
            measurement_system="Imperial",
            start_level=100
        )
        
        assert system1.measurement_system == "metric"
        assert system2.measurement_system == "imperial"
    
    def test_start_level_validation_negative(self):
        """Test that negative start levels are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SystemInfo(
                version="3.4.0",
                build_string="Release Build",
                locale="en_US",
                measurement_system="metric",
                start_level=-1
            )
        
        assert "Start level must be non-negative" in str(exc_info.value)
    
    def test_start_level_validation_zero(self):
        """Test that zero start level is accepted."""
        system = SystemInfo(
            version="3.4.0",
            build_string="Release Build",
            locale="en_US",
            measurement_system="metric",
            start_level=0
        )
        
        assert system.start_level == 0
    
    def test_serialization_round_trip(self):
        """Test serialization and deserialization consistency."""
        original = SystemInfo(
            version="3.4.0",
            build_string="Release Build",
            locale="en_US",
            measurement_system="metric",
            start_level=100
        )
        
        # Serialize to dict
        data = original.model_dump()
        
        # Deserialize back to object
        restored = SystemInfo(**data)
        
        # Verify all fields match
        assert restored.version == original.version
        assert restored.build_string == original.build_string
        assert restored.locale == original.locale
        assert restored.measurement_system == original.measurement_system
        assert restored.start_level == original.start_level


class TestMCPError:
    """Unit tests for MCPError model."""
    
    def test_valid_mcp_error_creation(self):
        """Test creating a valid MCPError with all fields."""
        error = MCPError(
            error_type="ValidationError",
            message="Invalid input provided",
            details={"field": "name", "value": ""},
            suggestions=["Provide a non-empty name", "Check input format"]
        )
        
        assert error.error_type == "ValidationError"
        assert error.message == "Invalid input provided"
        assert error.details == {"field": "name", "value": ""}
        assert error.suggestions == ["Provide a non-empty name", "Check input format"]
    
    def test_minimal_mcp_error_creation(self):
        """Test creating MCPError with only required fields."""
        error = MCPError(
            error_type="NetworkError",
            message="Connection failed"
        )
        
        assert error.error_type == "NetworkError"
        assert error.message == "Connection failed"
        assert error.details is None
        assert error.suggestions == []
    
    def test_error_type_validation_empty(self):
        """Test that empty error types are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MCPError(error_type="", message="Test message")
        
        assert "Error type cannot be empty" in str(exc_info.value)
    
    def test_message_validation_empty(self):
        """Test that empty messages are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MCPError(error_type="TestError", message="")
        
        assert "Error message cannot be empty" in str(exc_info.value)


class TestValidationResult:
    """Unit tests for ValidationResult model."""
    
    def test_valid_validation_result_creation(self):
        """Test creating a valid ValidationResult."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Minor issue detected"]
        )
        
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == ["Minor issue detected"]
    
    def test_add_error_method(self):
        """Test that add_error method works correctly."""
        result = ValidationResult(is_valid=True)
        
        result.add_error("Test error")
        
        assert result.is_valid is False
        assert "Test error" in result.errors
    
    def test_add_warning_method(self):
        """Test that add_warning method works correctly."""
        result = ValidationResult(is_valid=True)
        
        result.add_warning("Test warning")
        
        assert result.is_valid is True  # Warnings don't affect validity
        assert "Test warning" in result.warnings
    
    def test_multiple_errors_and_warnings(self):
        """Test adding multiple errors and warnings."""
        result = ValidationResult(is_valid=True)
        
        result.add_error("Error 1")
        result.add_error("Error 2")
        result.add_warning("Warning 1")
        result.add_warning("Warning 2")
        
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 2
        assert "Error 1" in result.errors
        assert "Error 2" in result.errors
        assert "Warning 1" in result.warnings
        assert "Warning 2" in result.warnings


class TestAddonInfo:
    """Unit tests for AddonInfo model."""
    
    def test_valid_addon_info_creation(self):
        """Test creating a valid AddonInfo with all fields."""
        addon = AddonInfo(
            id="zwave",
            name="Z-Wave Binding",
            version="3.4.0",
            description="Z-Wave protocol support for openHAB",
            installed=True,
            type="binding",
            author="openHAB Community",
            configuration={"port": "/dev/ttyUSB0", "networkKey": "secret"}
        )
        
        assert addon.id == "zwave"
        assert addon.name == "Z-Wave Binding"
        assert addon.version == "3.4.0"
        assert addon.description == "Z-Wave protocol support for openHAB"
        assert addon.installed is True
        assert addon.type == "binding"
        assert addon.author == "openHAB Community"
        assert addon.configuration == {"port": "/dev/ttyUSB0", "networkKey": "secret"}
    
    def test_minimal_addon_info_creation(self):
        """Test creating AddonInfo with only required fields."""
        addon = AddonInfo(
            id="mqtt",
            name="MQTT Binding",
            installed=False,
            type="binding"
        )
        
        assert addon.id == "mqtt"
        assert addon.name == "MQTT Binding"
        assert addon.version is None
        assert addon.description is None
        assert addon.installed is False
        assert addon.type == "binding"
        assert addon.author is None
        assert addon.configuration == {}
    
    def test_addon_id_validation_empty(self):
        """Test that empty addon IDs are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AddonInfo(id="", name="Test Addon", installed=True, type="binding")
        
        assert "Addon ID cannot be empty" in str(exc_info.value)
    
    def test_addon_id_validation_whitespace(self):
        """Test that whitespace-only addon IDs are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AddonInfo(id="   ", name="Test Addon", installed=True, type="binding")
        
        assert "Addon ID cannot be empty" in str(exc_info.value)
    
    def test_addon_name_validation_empty(self):
        """Test that empty addon names are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AddonInfo(id="test", name="", installed=True, type="binding")
        
        assert "Addon name cannot be empty" in str(exc_info.value)
    
    def test_addon_name_validation_whitespace(self):
        """Test that whitespace-only addon names are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AddonInfo(id="test", name="   ", installed=True, type="binding")
        
        assert "Addon name cannot be empty" in str(exc_info.value)
    
    def test_addon_type_validation_invalid(self):
        """Test that invalid addon types are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AddonInfo(id="test", name="Test Addon", installed=True, type="invalid")
        
        assert "Invalid addon type" in str(exc_info.value)
    
    def test_addon_type_validation_valid_types(self):
        """Test that all valid addon types are accepted."""
        valid_types = ['binding', 'transformation', 'persistence', 'automation', 
                      'voice', 'ui', 'misc', 'io']
        
        for addon_type in valid_types:
            addon = AddonInfo(
                id="test",
                name="Test Addon",
                installed=True,
                type=addon_type
            )
            assert addon.type == addon_type.lower()
    
    def test_addon_type_validation_case_insensitive(self):
        """Test that addon type validation is case insensitive."""
        addon1 = AddonInfo(
            id="test1",
            name="Test Addon 1",
            installed=True,
            type="BINDING"
        )
        
        addon2 = AddonInfo(
            id="test2",
            name="Test Addon 2",
            installed=True,
            type="Transformation"
        )
        
        assert addon1.type == "binding"
        assert addon2.type == "transformation"
    
    def test_addon_configuration_validation(self):
        """Test that addon configuration accepts various parameter types."""
        config = {
            "string_param": "value",
            "int_param": 42,
            "bool_param": True,
            "float_param": 3.14,
            "list_param": ["item1", "item2"],
            "dict_param": {"nested": "value"}
        }
        
        addon = AddonInfo(
            id="test",
            name="Test Addon",
            installed=True,
            type="binding",
            configuration=config
        )
        
        assert addon.configuration == config
    
    def test_serialization_round_trip(self):
        """Test serialization and deserialization consistency."""
        original = AddonInfo(
            id="zwave",
            name="Z-Wave Binding",
            version="3.4.0",
            description="Z-Wave protocol support for openHAB",
            installed=True,
            type="binding",
            author="openHAB Community",
            configuration={"port": "/dev/ttyUSB0", "networkKey": "secret"}
        )
        
        # Serialize to dict
        data = original.model_dump()
        
        # Deserialize back to object
        restored = AddonInfo(**data)
        
        # Verify all fields match
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.version == original.version
        assert restored.description == original.description
        assert restored.installed == original.installed
        assert restored.type == original.type
        assert restored.author == original.author
        assert restored.configuration == original.configuration
    
    def test_json_serialization_round_trip(self):
        """Test JSON serialization and deserialization consistency."""
        original = AddonInfo(
            id="mqtt",
            name="MQTT Binding",
            version="3.4.0",
            description="MQTT protocol support",
            installed=False,
            type="binding",
            author="openHAB Team",
            configuration={"broker": "localhost", "port": 1883}
        )
        
        # Serialize to JSON
        json_data = original.model_dump_json()
        
        # Deserialize back to object
        restored = AddonInfo.model_validate_json(json_data)
        
        # Verify all fields match
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.version == original.version
        assert restored.description == original.description
        assert restored.installed == original.installed
        assert restored.type == original.type
        assert restored.author == original.author
        assert restored.configuration == original.configuration
