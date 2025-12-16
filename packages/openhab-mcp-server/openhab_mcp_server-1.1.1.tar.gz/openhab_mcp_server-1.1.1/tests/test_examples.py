"""Unit tests for operation examples and API documentation tools."""

import pytest
from unittest.mock import Mock, patch

from openhab_mcp_server.tools.examples import OperationExamplesTool, APIDocumentationTool
from openhab_mcp_server.utils.config import Config


class TestOperationExamplesTool:
    """Unit tests for OperationExamplesTool."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="oh.test.token123456789012345678901234567890",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.fixture
    def examples_tool(self, config):
        """Create OperationExamplesTool instance."""
        return OperationExamplesTool(config)
    
    @pytest.mark.asyncio
    async def test_execute_with_valid_operation_type(self, examples_tool):
        """Test executing with a valid operation type."""
        result = await examples_tool.execute("item_control")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        
        content = result[0].text
        assert "Item Control Examples" in content
        assert "Control openHAB items by sending commands" in content
        assert "Turn on a switch" in content
        assert "send_item_command" in content
        assert "LivingRoom_Light" in content
    
    @pytest.mark.asyncio
    async def test_execute_with_invalid_operation_type(self, examples_tool):
        """Test executing with an invalid operation type."""
        result = await examples_tool.execute("invalid_type")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        
        content = result[0].text
        assert "Invalid operation type" in content
    
    @pytest.mark.asyncio
    async def test_execute_with_empty_operation_type(self, examples_tool):
        """Test executing with an empty operation type."""
        result = await examples_tool.execute("")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        
        content = result[0].text
        assert "Invalid operation type" in content
        assert "Operation type cannot be empty" in content
    
    @pytest.mark.asyncio
    async def test_execute_without_operation_type(self, examples_tool):
        """Test executing without specifying operation type (overview)."""
        result = await examples_tool.execute(None)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        
        content = result[0].text
        assert "openHAB MCP Server - Operation Examples" in content
        assert "Available operation types:" in content
        assert "Item Control" in content
        assert "Item Monitoring" in content
        assert "Thing Management" in content
        assert "Rule Automation" in content
        assert "System Monitoring" in content
    
    @pytest.mark.asyncio
    async def test_execute_all_operation_types(self, examples_tool):
        """Test executing with all valid operation types."""
        operation_types = [
            "item_control",
            "item_monitoring", 
            "thing_management",
            "rule_automation",
            "system_monitoring"
        ]
        
        for operation_type in operation_types:
            result = await examples_tool.execute(operation_type)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            
            content = result[0].text
            assert operation_type.replace('_', ' ').title() in content
            assert "Tool:" in content
            assert "Parameters:" in content
            assert "Expected Response:" in content
    
    def test_validate_operation_type_valid(self, examples_tool):
        """Test validation of valid operation types."""
        valid_types = [
            "item_control",
            "item_monitoring",
            "thing_management", 
            "rule_automation",
            "system_monitoring"
        ]
        
        for operation_type in valid_types:
            result = examples_tool._validate_operation_type(operation_type)
            assert result.is_valid
            assert len(result.errors) == 0
    
    def test_validate_operation_type_invalid(self, examples_tool):
        """Test validation of invalid operation types."""
        invalid_types = [
            "",
            "   ",
            "invalid_type",
            "nonexistent"
        ]
        
        for operation_type in invalid_types:
            result = examples_tool._validate_operation_type(operation_type)
            assert not result.is_valid
            assert len(result.errors) > 0
    
    def test_format_operation_examples(self, examples_tool):
        """Test formatting of operation examples."""
        examples_data = {
            "description": "Test operation examples",
            "examples": [
                {
                    "operation": "Test operation",
                    "tool": "test_tool",
                    "parameters": {"param1": "value1"},
                    "expected_response": "Test response"
                }
            ]
        }
        
        result = examples_tool._format_operation_examples("test_type", examples_data)
        
        assert "Test Type Examples" in result
        assert "Test operation examples" in result
        assert "Test operation" in result
        assert "test_tool" in result
        assert "param1" in result
        assert "Test response" in result
    
    def test_format_all_examples(self, examples_tool):
        """Test formatting of all examples overview."""
        result = examples_tool._format_all_examples()
        
        assert "openHAB MCP Server - Operation Examples" in result
        assert "Available operation types:" in result
        assert "Item Control" in result
        assert "get_operation_examples" in result


class TestAPIDocumentationTool:
    """Unit tests for APIDocumentationTool."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="oh.test.token123456789012345678901234567890",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.fixture
    def api_docs_tool(self, config):
        """Create APIDocumentationTool instance."""
        return APIDocumentationTool(config)
    
    @pytest.mark.asyncio
    async def test_execute_with_tools_section(self, api_docs_tool):
        """Test executing with tools section."""
        result = await api_docs_tool.execute("tools")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        
        content = result[0].text
        assert "Tools Documentation" in content
        assert "Available MCP tools for openHAB operations" in content
        assert "Available Tools:" in content
        assert "get_item_state" in content
        assert "send_item_command" in content
        assert "Parameters:" in content
    
    @pytest.mark.asyncio
    async def test_execute_with_resources_section(self, api_docs_tool):
        """Test executing with resources section."""
        result = await api_docs_tool.execute("resources")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        
        content = result[0].text
        assert "Resources Documentation" in content
        assert "Available MCP resources for read-only data access" in content
        assert "Available Resources:" in content
        assert "openhab://docs/setup" in content
        assert "openhab://system/status" in content
    
    @pytest.mark.asyncio
    async def test_execute_with_workflows_section(self, api_docs_tool):
        """Test executing with common_workflows section."""
        result = await api_docs_tool.execute("common_workflows")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        
        content = result[0].text
        assert "Common_Workflows Documentation" in content
        assert "Common usage patterns and workflows" in content
        assert "Common Workflows:" in content
        assert "Device Control" in content
        assert "System Monitoring" in content
        assert "Troubleshooting" in content
    
    @pytest.mark.asyncio
    async def test_execute_with_invalid_section(self, api_docs_tool):
        """Test executing with an invalid section."""
        result = await api_docs_tool.execute("invalid_section")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        
        content = result[0].text
        assert "Invalid documentation section" in content
    
    @pytest.mark.asyncio
    async def test_execute_with_empty_section(self, api_docs_tool):
        """Test executing with an empty section."""
        result = await api_docs_tool.execute("")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        
        content = result[0].text
        assert "Invalid documentation section" in content
        assert "Documentation section cannot be empty" in content
    
    @pytest.mark.asyncio
    async def test_execute_without_section(self, api_docs_tool):
        """Test executing without specifying section (overview)."""
        result = await api_docs_tool.execute(None)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        
        content = result[0].text
        assert "openHAB MCP Server - API Documentation" in content
        assert "Tools" in content
        assert "Resources" in content
        assert "Common_Workflows" in content
        assert "get_api_documentation" in content
    
    @pytest.mark.asyncio
    async def test_execute_all_sections(self, api_docs_tool):
        """Test executing with all valid sections."""
        sections = ["tools", "resources", "common_workflows"]
        
        for section in sections:
            result = await api_docs_tool.execute(section)
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            
            content = result[0].text
            assert section.title() in content or section.replace('_', ' ').title() in content
    
    def test_validate_section_valid(self, api_docs_tool):
        """Test validation of valid sections."""
        valid_sections = ["tools", "resources", "common_workflows"]
        
        for section in valid_sections:
            result = api_docs_tool._validate_section(section)
            assert result.is_valid
            assert len(result.errors) == 0
    
    def test_validate_section_invalid(self, api_docs_tool):
        """Test validation of invalid sections."""
        invalid_sections = [
            "",
            "   ",
            "invalid_section",
            "nonexistent"
        ]
        
        for section in invalid_sections:
            result = api_docs_tool._validate_section(section)
            assert not result.is_valid
            assert len(result.errors) > 0
    
    def test_format_section_documentation_tools(self, api_docs_tool):
        """Test formatting of tools section documentation."""
        doc_data = {
            "description": "Test tools documentation",
            "endpoints": {
                "test_tool": {
                    "description": "Test tool description",
                    "usage_pattern": "Test usage pattern",
                    "parameters": {
                        "param1": {
                            "type": "string",
                            "required": True,
                            "description": "Test parameter",
                            "example": "test_value"
                        }
                    },
                    "related_tools": ["other_tool"]
                }
            }
        }
        
        result = api_docs_tool._format_section_documentation("tools", doc_data)
        
        assert "Tools Documentation" in result
        assert "Test tools documentation" in result
        assert "Available Tools:" in result
        assert "test_tool" in result
        assert "Test tool description" in result
        assert "Test usage pattern" in result
        assert "Parameters:" in result
        assert "param1" in result
        assert "Related Tools:" in result
    
    def test_format_overview_documentation(self, api_docs_tool):
        """Test formatting of overview documentation."""
        result = api_docs_tool._format_overview_documentation()
        
        assert "openHAB MCP Server - API Documentation" in result
        assert "Tools" in result
        assert "Resources" in result
        assert "Common_Workflows" in result
        assert "get_api_documentation" in result
        assert "Available sections:" in result


class TestExamplesIntegration:
    """Integration tests for examples and documentation tools."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="oh.test.token123456789012345678901234567890",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.mark.asyncio
    async def test_examples_and_documentation_consistency(self, config):
        """Test that examples and documentation are consistent."""
        examples_tool = OperationExamplesTool(config)
        docs_tool = APIDocumentationTool(config)
        
        # Get item control examples
        examples_result = await examples_tool.execute("item_control")
        examples_content = examples_result[0].text
        
        # Get tools documentation
        docs_result = await docs_tool.execute("tools")
        docs_content = docs_result[0].text
        
        # Check that tools mentioned in examples are documented
        if "send_item_command" in examples_content:
            assert "send_item_command" in docs_content
        
        if "get_item_state" in examples_content:
            assert "get_item_state" in docs_content
    
    @pytest.mark.asyncio
    async def test_all_operation_types_have_examples(self, config):
        """Test that all operation types have examples."""
        examples_tool = OperationExamplesTool(config)
        
        # Get overview
        overview_result = await examples_tool.execute(None)
        overview_content = overview_result[0].text
        
        # Extract operation types from overview
        operation_types = [
            "item_control",
            "item_monitoring",
            "thing_management", 
            "rule_automation",
            "system_monitoring"
        ]
        
        # Test each operation type has examples
        for operation_type in operation_types:
            result = await examples_tool.execute(operation_type)
            content = result[0].text
            
            # Should contain examples
            assert "Tool:" in content
            assert "Parameters:" in content
            assert "Expected Response:" in content
    
    @pytest.mark.asyncio
    async def test_all_documentation_sections_complete(self, config):
        """Test that all documentation sections are complete."""
        docs_tool = APIDocumentationTool(config)
        
        sections = ["tools", "resources", "common_workflows"]
        
        for section in sections:
            result = await docs_tool.execute(section)
            content = result[0].text
            
            # Should be non-empty and structured
            assert len(content.strip()) > 0
            assert section.title() in content or section.replace('_', ' ').title() in content
    
    @pytest.mark.asyncio
    async def test_error_handling(self, config):
        """Test error handling in both tools."""
        examples_tool = OperationExamplesTool(config)
        docs_tool = APIDocumentationTool(config)
        
        # Test invalid inputs
        invalid_examples = await examples_tool.execute("invalid")
        assert "Invalid operation type" in invalid_examples[0].text
        
        invalid_docs = await docs_tool.execute("invalid")
        assert "Invalid documentation section" in invalid_docs[0].text
        
        # Test empty inputs
        empty_examples = await examples_tool.execute("")
        assert "Invalid operation type" in empty_examples[0].text
        
        empty_docs = await docs_tool.execute("")
        assert "Invalid documentation section" in empty_docs[0].text
