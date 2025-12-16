"""Property-based tests for operation examples completeness."""

import pytest
from hypothesis import given, strategies as st, settings

from openhab_mcp_server.tools.examples import OperationExamplesTool, APIDocumentationTool
from openhab_mcp_server.utils.config import Config


# Test data generators
@st.composite
def operation_type_strategy(draw):
    """Generate valid operation types."""
    valid_types = [
        "item_control",
        "item_monitoring", 
        "thing_management",
        "rule_automation",
        "system_monitoring"
    ]
    return draw(st.sampled_from(valid_types))


@st.composite
def documentation_section_strategy(draw):
    """Generate valid documentation sections."""
    valid_sections = [
        "tools",
        "resources",
        "common_workflows"
    ]
    return draw(st.sampled_from(valid_sections))


@st.composite
def invalid_operation_type_strategy(draw):
    """Generate invalid operation types."""
    return draw(st.one_of(
        st.just(""),  # Empty string
        st.just("   "),  # Whitespace only
        st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() not in [
                "item_control", "item_monitoring", "thing_management",
                "rule_automation", "system_monitoring"
            ]
        )
    ))


@st.composite
def invalid_documentation_section_strategy(draw):
    """Generate invalid documentation sections."""
    return draw(st.one_of(
        st.just(""),  # Empty string
        st.just("   "),  # Whitespace only
        st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() not in ["tools", "resources", "common_workflows"]
        )
    ))


class TestOperationExamplesProperties:
    """Property-based tests for OperationExamplesTool."""
    
    def _get_test_tool(self):
        """Get test operation examples tool."""
        config = Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
        return OperationExamplesTool(config)
    
    @given(operation_type=operation_type_strategy())
    @settings(max_examples=100, deadline=5000)
    async def test_property_operation_examples_completeness(self, operation_type):
        """**Feature: openhab-mcp-server, Property 14: Operation examples completeness**
        
        For any common operation, the system should provide sample requests and responses 
        when examples are requested.
        
        **Validates: Requirements 5.4**
        """
        tool = self._get_test_tool()
        
        # Execute the tool with a valid operation type
        result = await tool.execute(operation_type)
        
        # Property: Should always return a non-empty list
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) > 0, "Expected non-empty result list"
        
        # Property: Each result should be TextContent
        for item in result:
            assert hasattr(item, 'type'), "Result item should have 'type' attribute"
            assert hasattr(item, 'text'), "Result item should have 'text' attribute"
            assert item.type == "text", f"Expected type 'text', got {item.type}"
        
        # Property: Content should include operation examples
        content = result[0].text
        assert operation_type.replace('_', ' ').title() in content, \
            f"Content should mention the operation type '{operation_type}'"
        
        # Property: Content should include sample requests and responses
        assert "Tool:" in content or "Parameters:" in content or "Expected Response:" in content, \
            "Content should include sample requests and responses"
        
        # Property: Content should be non-empty and meaningful
        assert len(content.strip()) > 0, "Content should not be empty"
        assert not content.isspace(), "Content should not be only whitespace"
    
    @given(operation_type=invalid_operation_type_strategy())
    @settings(max_examples=50, deadline=5000)
    async def test_property_invalid_operation_type_handling(self, operation_type):
        """Test that invalid operation types are handled correctly."""
        tool = self._get_test_tool()
        
        # Execute the tool with an invalid operation type
        result = await tool.execute(operation_type)
        
        # Property: Should return error message for invalid types
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) > 0, "Expected non-empty result list"
        
        content = result[0].text
        assert "Invalid operation type" in content or "No examples found" in content, \
            "Should return appropriate error message for invalid operation type"
    
    async def test_property_all_examples_completeness(self):
        """Test that requesting all examples returns complete information."""
        tool = self._get_test_tool()
        
        # Execute the tool without operation type filter
        result = await tool.execute(None)
        
        # Property: Should return overview of all operation types
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) > 0, "Expected non-empty result list"
        
        content = result[0].text
        
        # Property: Should mention all available operation types
        expected_types = [
            "Item Control", "Item Monitoring", "Thing Management", 
            "Rule Automation", "System Monitoring"
        ]
        
        for expected_type in expected_types:
            assert expected_type in content, \
                f"Overview should mention operation type '{expected_type}'"
        
        # Property: Should provide usage instructions
        assert "get_operation_examples" in content, \
            "Should provide usage instructions"


class TestAPIDocumentationProperties:
    """Property-based tests for APIDocumentationTool."""
    
    def _get_test_tool(self):
        """Get test API documentation tool."""
        config = Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
        return APIDocumentationTool(config)
    
    @given(section=documentation_section_strategy())
    @settings(max_examples=100, deadline=5000)
    async def test_property_api_documentation_completeness(self, section):
        """Test that API documentation provides complete information for each section."""
        tool = self._get_test_tool()
        
        # Execute the tool with a valid section
        result = await tool.execute(section)
        
        # Property: Should always return a non-empty list
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) > 0, "Expected non-empty result list"
        
        # Property: Each result should be TextContent
        for item in result:
            assert hasattr(item, 'type'), "Result item should have 'type' attribute"
            assert hasattr(item, 'text'), "Result item should have 'text' attribute"
            assert item.type == "text", f"Expected type 'text', got {item.type}"
        
        # Property: Content should include section information
        content = result[0].text
        assert section.title() in content, \
            f"Content should mention the section '{section}'"
        
        # Property: Content should include usage patterns
        assert ("Usage Pattern" in content or "Description" in content or 
                "usage patterns" in content or "workflows" in content), \
            "Content should include usage patterns or descriptions"
        
        # Property: Content should be structured and informative
        assert len(content.strip()) > 0, "Content should not be empty"
        assert not content.isspace(), "Content should not be only whitespace"
        
        # Property: Section-specific requirements
        if section == "tools":
            assert "Available Tools:" in content, "Tools section should list available tools"
            assert "Parameters:" in content or "parameters" in content.lower(), \
                "Tools section should include parameter information"
        elif section == "resources":
            assert "Available Resources:" in content, "Resources section should list available resources"
            assert "openhab://" in content, "Resources section should include resource URIs"
        elif section == "common_workflows":
            assert "Common Workflows:" in content, "Workflows section should list workflows"
            assert ("steps" in content.lower() or "Steps" in content or 
                    "1." in content or "2." in content), \
                "Workflows section should include step information"
    
    @given(section=invalid_documentation_section_strategy())
    @settings(max_examples=50, deadline=5000)
    async def test_property_invalid_section_handling(self, section):
        """Test that invalid documentation sections are handled correctly."""
        tool = self._get_test_tool()
        
        # Execute the tool with an invalid section
        result = await tool.execute(section)
        
        # Property: Should return error message for invalid sections
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) > 0, "Expected non-empty result list"
        
        content = result[0].text
        assert "Invalid documentation section" in content or "No documentation found" in content, \
            "Should return appropriate error message for invalid section"
    
    async def test_property_overview_documentation_completeness(self):
        """Test that requesting overview documentation returns complete information."""
        tool = self._get_test_tool()
        
        # Execute the tool without section filter
        result = await tool.execute(None)
        
        # Property: Should return overview of all sections
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) > 0, "Expected non-empty result list"
        
        content = result[0].text
        
        # Property: Should mention all available sections
        expected_sections = ["Tools", "Resources", "Common"]
        
        for expected_section in expected_sections:
            assert expected_section in content, \
                f"Overview should mention section '{expected_section}'"
        
        # Property: Should provide usage instructions
        assert "get_api_documentation" in content, \
            "Should provide usage instructions"
        
        # Property: Should list available sections
        assert "Available sections:" in content, \
            "Should list available sections"


class TestExamplesIntegrationProperties:
    """Integration property tests for examples and documentation tools."""
    
    async def test_property_examples_and_documentation_consistency(self):
        """Test that examples and documentation are consistent with each other."""
        config = Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
        
        examples_tool = OperationExamplesTool(config)
        docs_tool = APIDocumentationTool(config)
        
        # Get all examples
        examples_result = await examples_tool.execute(None)
        examples_content = examples_result[0].text
        
        # Get tools documentation
        docs_result = await docs_tool.execute("tools")
        docs_content = docs_result[0].text
        
        # Property: Tools mentioned in examples should be documented
        # Extract tool names from examples (simplified check)
        if "get_item_state" in examples_content:
            assert "get_item_state" in docs_content, \
                "Tools used in examples should be documented"
        
        if "send_item_command" in examples_content:
            assert "send_item_command" in docs_content, \
                "Tools used in examples should be documented"
        
        # Property: Both should be non-empty and structured
        assert len(examples_content.strip()) > 0, "Examples should not be empty"
        assert len(docs_content.strip()) > 0, "Documentation should not be empty"
        
        # Property: Both should contain usage information
        assert ("Tool:" in examples_content or "Parameters:" in examples_content or 
                "examples available" in examples_content), \
            "Examples should contain tool usage information"
        assert "Description:" in docs_content or "Parameters:" in docs_content, \
            "Documentation should contain tool descriptions"
