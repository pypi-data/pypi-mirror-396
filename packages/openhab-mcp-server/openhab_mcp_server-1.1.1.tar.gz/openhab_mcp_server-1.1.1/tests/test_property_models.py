"""Property-based tests for input validation completeness."""

import pytest
from hypothesis import given, strategies as st, settings
from pydantic import ValidationError

from openhab_mcp_server.models import ItemState, ThingStatus, RuleDefinition, SystemInfo, MCPError, ValidationResult, AddonInfo


# Test data generators
@st.composite
def valid_item_name_strategy(draw):
    """Generate valid openHAB item names."""
    # Valid item names: letters, numbers, underscores, no spaces, not empty
    name = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_'),
        min_size=1,
        max_size=50
    ))
    # Ensure it doesn't start with a number if it's all digits
    if name and name[0].isdigit():
        name = 'Item' + name
    return name


@st.composite
def invalid_item_name_strategy(draw):
    """Generate invalid openHAB item names."""
    return draw(st.one_of(
        st.just(""),  # Empty string
        st.just("   "),  # Whitespace only
        st.text(min_size=1, max_size=20).filter(lambda x: ' ' in x),  # Contains spaces
    ))


@st.composite
def valid_thing_uid_strategy(draw):
    """Generate valid openHAB thing UIDs."""
    binding = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=20))
    thing_type = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=20))
    thing_id = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'), min_size=1, max_size=20))
    return f"{binding}:{thing_type}:{thing_id}"


@st.composite
def invalid_thing_uid_strategy(draw):
    """Generate invalid openHAB thing UIDs."""
    return draw(st.one_of(
        st.just(""),  # Empty string
        st.just("   "),  # Whitespace only
        st.text(min_size=1, max_size=10).filter(lambda x: ':' not in x),  # No colons
        st.just("binding:"),  # Missing parts
    ))


@st.composite
def valid_rule_data_strategy(draw):
    """Generate valid rule definition data."""
    return {
        "name": draw(st.text(min_size=1, max_size=100)),
        "description": draw(st.one_of(st.none(), st.text(min_size=1, max_size=500))),
        "triggers": draw(st.lists(
            st.fixed_dictionaries({"type": st.text(min_size=1, max_size=50)}),
            min_size=1,
            max_size=5
        )),
        "conditions": draw(st.lists(
            st.fixed_dictionaries({"type": st.text(min_size=1, max_size=50)}),
            max_size=3
        )),
        "actions": draw(st.lists(
            st.fixed_dictionaries({"type": st.text(min_size=1, max_size=50)}),
            min_size=1,
            max_size=5
        )),
        "enabled": draw(st.booleans())
    }


@st.composite
def valid_addon_id_strategy(draw):
    """Generate valid addon IDs."""
    # Valid addon IDs: letters, numbers, underscores, hyphens, no spaces, not empty
    addon_id = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'),
        min_size=1,
        max_size=50
    ))
    return addon_id


@st.composite
def invalid_addon_id_strategy(draw):
    """Generate invalid addon IDs."""
    return draw(st.one_of(
        st.just(""),  # Empty string
        st.just("   "),  # Whitespace only
    ))


@st.composite
def invalid_addon_name_strategy(draw):
    """Generate invalid addon names."""
    return draw(st.one_of(
        st.just(""),  # Empty string
        st.just("   "),  # Whitespace only
    ))


class TestInputValidationProperties:
    """Property-based tests for input validation completeness."""
    
    @given(
        name=invalid_item_name_strategy(),
        state=st.text(min_size=1, max_size=100),
        item_type=st.sampled_from(['Switch', 'Dimmer', 'Number', 'String'])
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_input_validation_completeness_item_names(self, name, state, item_type):
        """**Feature: openhab-mcp-server, Property 11: Input validation completeness**
        
        For any invalid input parameter, the system should validate and reject 
        the malformed request with appropriate error messages.
        
        **Validates: Requirements 4.3**
        """
        # Property: Invalid item names should be rejected with ValidationError
        with pytest.raises(ValidationError) as exc_info:
            ItemState(name=name, state=state, type=item_type)
        
        # Property: Error should contain meaningful message about the validation failure
        error_messages = str(exc_info.value)
        assert any(keyword in error_messages.lower() for keyword in ['name', 'empty', 'space'])
    
    @given(
        name=valid_item_name_strategy(),
        state=st.text(min_size=1, max_size=100),
        item_type=st.text(min_size=1, max_size=50).filter(
            lambda x: x not in {'Switch', 'Dimmer', 'Number', 'String', 'DateTime', 'Contact', 'Rollershutter', 'Color', 'Location', 'Player', 'Group'}
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_input_validation_completeness_item_types(self, name, state, item_type):
        """Test that invalid item types are rejected."""
        # Property: Invalid item types should be rejected with ValidationError
        with pytest.raises(ValidationError) as exc_info:
            ItemState(name=name, state=state, type=item_type)
        
        # Property: Error should mention invalid type
        error_messages = str(exc_info.value)
        assert 'type' in error_messages.lower()
    
    @given(uid=invalid_thing_uid_strategy())
    @settings(max_examples=100, deadline=5000)
    def test_property_input_validation_completeness_thing_uids(self, uid):
        """Test that invalid thing UIDs are rejected."""
        # Property: Invalid thing UIDs should be rejected with ValidationError
        with pytest.raises(ValidationError) as exc_info:
            ThingStatus(
                uid=uid,
                status="ONLINE",
                status_detail="OK",
                label="Test Thing"
            )
        
        # Property: Error should contain meaningful message about UID format
        error_messages = str(exc_info.value)
        assert any(keyword in error_messages.lower() for keyword in ['uid', 'empty', 'binding'])
    
    @given(status=st.text(min_size=1, max_size=50).filter(
        lambda x: x not in {'ONLINE', 'OFFLINE', 'UNKNOWN', 'INITIALIZING', 'REMOVING', 'REMOVED'}
    ))
    @settings(max_examples=100, deadline=5000)
    def test_property_input_validation_completeness_thing_status(self, status):
        """Test that invalid thing statuses are rejected."""
        # Property: Invalid thing statuses should be rejected with ValidationError
        with pytest.raises(ValidationError) as exc_info:
            ThingStatus(
                uid="binding:type:id",
                status=status,
                status_detail="OK",
                label="Test Thing"
            )
        
        # Property: Error should mention invalid status
        error_messages = str(exc_info.value)
        assert 'status' in error_messages.lower()
    
    @given(name=st.one_of(st.just(""), st.just("   ")))
    @settings(max_examples=50, deadline=5000)
    def test_property_input_validation_completeness_rule_names(self, name):
        """Test that empty rule names are rejected."""
        # Property: Empty rule names should be rejected with ValidationError
        with pytest.raises(ValidationError) as exc_info:
            RuleDefinition(
                name=name,
                triggers=[{"type": "test"}],
                actions=[{"type": "test"}]
            )
        
        # Property: Error should mention name validation
        error_messages = str(exc_info.value)
        assert 'name' in error_messages.lower()
    
    @given(rule_data=valid_rule_data_strategy())
    @settings(max_examples=100, deadline=5000)
    def test_property_input_validation_completeness_empty_triggers_actions(self, rule_data):
        """Test that rules with empty triggers or actions are rejected."""
        # Test empty triggers
        rule_data_no_triggers = rule_data.copy()
        rule_data_no_triggers["triggers"] = []
        
        # Property: Rules with no triggers should be rejected
        with pytest.raises(ValidationError) as exc_info:
            RuleDefinition(**rule_data_no_triggers)
        
        error_messages = str(exc_info.value)
        assert 'trigger' in error_messages.lower()
        
        # Test empty actions
        rule_data_no_actions = rule_data.copy()
        rule_data_no_actions["actions"] = []
        
        # Property: Rules with no actions should be rejected
        with pytest.raises(ValidationError) as exc_info:
            RuleDefinition(**rule_data_no_actions)
        
        error_messages = str(exc_info.value)
        assert 'action' in error_messages.lower()
    
    @given(
        version=st.one_of(st.just(""), st.just("   ")),
        build_string=st.text(min_size=1, max_size=100),
        locale=st.text(min_size=1, max_size=20),
        measurement_system=st.sampled_from(['metric', 'imperial']),
        start_level=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_input_validation_completeness_system_info_version(self, version, build_string, locale, measurement_system, start_level):
        """Test that empty system versions are rejected."""
        # Property: Empty versions should be rejected with ValidationError
        with pytest.raises(ValidationError) as exc_info:
            SystemInfo(
                version=version,
                build_string=build_string,
                locale=locale,
                measurement_system=measurement_system,
                start_level=start_level
            )
        
        # Property: Error should mention version validation
        error_messages = str(exc_info.value)
        assert 'version' in error_messages.lower()
    
    @given(
        measurement_system=st.text(min_size=1, max_size=50).filter(
            lambda x: x.lower() not in {'metric', 'imperial'}
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_input_validation_completeness_measurement_system(self, measurement_system):
        """Test that invalid measurement systems are rejected."""
        # Property: Invalid measurement systems should be rejected with ValidationError
        with pytest.raises(ValidationError) as exc_info:
            SystemInfo(
                version="3.4.0",
                build_string="Build 1234",
                locale="en_US",
                measurement_system=measurement_system,
                start_level=80
            )
        
        # Property: Error should mention measurement system validation
        error_messages = str(exc_info.value)
        assert 'measurement' in error_messages.lower()
    
    @given(start_level=st.integers(max_value=-1))
    @settings(max_examples=50, deadline=5000)
    def test_property_input_validation_completeness_negative_start_level(self, start_level):
        """Test that negative start levels are rejected."""
        # Property: Negative start levels should be rejected with ValidationError
        with pytest.raises(ValidationError) as exc_info:
            SystemInfo(
                version="3.4.0",
                build_string="Build 1234",
                locale="en_US",
                measurement_system="metric",
                start_level=start_level
            )
        
        # Property: Error should mention start level validation
        error_messages = str(exc_info.value)
        assert any(keyword in error_messages.lower() for keyword in ['start', 'level', 'negative'])
    
    @given(
        error_type=st.one_of(st.just(""), st.just("   ")),
        message=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_input_validation_completeness_mcp_error_type(self, error_type, message):
        """Test that empty error types are rejected."""
        # Property: Empty error types should be rejected with ValidationError
        with pytest.raises(ValidationError) as exc_info:
            MCPError(error_type=error_type, message=message)
        
        # Property: Error should mention error type validation
        error_messages = str(exc_info.value)
        assert any(keyword in error_messages.lower() for keyword in ['error', 'type', 'empty'])
    
    @given(
        error_type=st.text(min_size=1, max_size=50),
        message=st.one_of(st.just(""), st.just("   "))
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_input_validation_completeness_mcp_error_message(self, error_type, message):
        """Test that empty error messages are rejected."""
        # Property: Empty error messages should be rejected with ValidationError
        with pytest.raises(ValidationError) as exc_info:
            MCPError(error_type=error_type, message=message)
        
        # Property: Error should mention message validation
        error_messages = str(exc_info.value)
        assert any(keyword in error_messages.lower() for keyword in ['message', 'empty'])


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
