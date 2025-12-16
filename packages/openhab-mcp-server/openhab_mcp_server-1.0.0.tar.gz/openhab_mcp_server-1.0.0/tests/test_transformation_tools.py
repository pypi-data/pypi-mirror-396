"""Unit tests for transformation management tools."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

from openhab_mcp_server.tools.transformations import (
    TransformationListTool, TransformationCreateTool, TransformationTestTool,
    TransformationUpdateTool, TransformationUsageTool
)


class TestTransformationListTool:
    """Unit tests for TransformationListTool."""
    
    @pytest.mark.asyncio
    async def test_execute_success_with_transformations(self):
        """Test successful transformation listing with transformations available."""
        transformations = [
            {
                'id': 'map_test1',
                'type': 'MAP',
                'description': 'Test MAP transformation',
                'configuration': {'filename': 'test.map'}
            },
            {
                'id': 'regex_test2',
                'type': 'REGEX',
                'description': 'Test REGEX transformation',
                'configuration': {'pattern': '.*'}
            }
        ]
        
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_transformations.return_value = transformations
            
            result = await TransformationListTool.execute()
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Found 2 transformation(s)" in result[0].text
            assert "MAP" in result[0].text
            assert "REGEX" in result[0].text
            assert "map_test1" in result[0].text
            assert "regex_test2" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_success_no_transformations(self):
        """Test successful transformation listing with no transformations."""
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_transformations.return_value = []
            
            result = await TransformationListTool.execute()
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "No transformation addons" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_client_error(self):
        """Test transformation listing with client error."""
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_transformations.side_effect = Exception("Connection failed")
            
            result = await TransformationListTool.execute()
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Failed to list transformations" in result[0].text
            assert "Connection failed" in result[0].text


class TestTransformationCreateTool:
    """Unit tests for TransformationCreateTool."""
    
    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful transformation creation."""
        transformation_type = "MAP"
        configuration = {"filename": "test.map"}
        expected_id = "map_test123"
        
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.create_transformation.return_value = expected_id
            
            result = await TransformationCreateTool.execute(transformation_type, configuration)
            
            mock_client.create_transformation.assert_called_once_with(transformation_type, configuration)
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Successfully created transformation" in result[0].text
            assert transformation_type in result[0].text
            assert expected_id in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_invalid_type(self):
        """Test transformation creation with invalid type."""
        transformation_type = "INVALID"
        configuration = {"test": "value"}
        
        result = await TransformationCreateTool.execute(transformation_type, configuration)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Transformation creation validation failed" in result[0].text
        assert "Invalid transformation type" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_empty_configuration(self):
        """Test transformation creation with empty configuration."""
        transformation_type = "MAP"
        configuration = {}
        
        result = await TransformationCreateTool.execute(transformation_type, configuration)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Transformation creation validation failed" in result[0].text
        assert "Configuration cannot be empty" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_client_error(self):
        """Test transformation creation with client error."""
        transformation_type = "MAP"
        configuration = {"filename": "test.map"}
        
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.create_transformation.side_effect = Exception("Creation failed")
            
            result = await TransformationCreateTool.execute(transformation_type, configuration)
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Failed to create transformation" in result[0].text
            assert "Creation failed" in result[0].text


class TestTransformationTestTool:
    """Unit tests for TransformationTestTool."""
    
    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful transformation testing."""
        transformation_id = "map_test1"
        sample_data = "ON"
        test_result = {
            'success': True,
            'input_value': sample_data,
            'output_value': 'Open',
            'execution_time': 0.001,
            'error_message': None
        }
        
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.test_transformation.return_value = test_result
            
            result = await TransformationTestTool.execute(transformation_id, sample_data)
            
            mock_client.test_transformation.assert_called_once_with(transformation_id, sample_data)
            assert len(result) == 1
            assert result[0].type == "text"
            assert transformation_id in result[0].text
            assert sample_data in result[0].text
            assert "Open" in result[0].text
            assert "Execution time:" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_transformation_failure(self):
        """Test transformation testing with transformation failure."""
        transformation_id = "map_test1"
        sample_data = "INVALID"
        test_result = {
            'success': False,
            'input_value': sample_data,
            'output_value': None,
            'execution_time': 0.001,
            'error_message': 'No mapping found'
        }
        
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.test_transformation.return_value = test_result
            
            result = await TransformationTestTool.execute(transformation_id, sample_data)
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert transformation_id in result[0].text
            assert sample_data in result[0].text
            assert "No mapping found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_empty_transformation_id(self):
        """Test transformation testing with empty transformation ID."""
        transformation_id = ""
        sample_data = "ON"
        
        result = await TransformationTestTool.execute(transformation_id, sample_data)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Transformation ID cannot be empty" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_none_sample_data(self):
        """Test transformation testing with None sample data."""
        transformation_id = "map_test1"
        sample_data = None
        
        result = await TransformationTestTool.execute(transformation_id, sample_data)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Sample data cannot be None" in result[0].text


class TestTransformationUpdateTool:
    """Unit tests for TransformationUpdateTool."""
    
    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful transformation configuration update."""
        transformation_id = "map_test1"
        configuration = {"filename": "updated.map"}
        
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.update_transformation.return_value = True
            
            result = await TransformationUpdateTool.execute(transformation_id, configuration)
            
            mock_client.update_transformation.assert_called_once_with(transformation_id, configuration)
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Successfully updated transformation configuration" in result[0].text
            assert transformation_id in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_update_failure(self):
        """Test transformation update with update failure."""
        transformation_id = "map_test1"
        configuration = {"filename": "updated.map"}
        
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.update_transformation.return_value = False
            
            result = await TransformationUpdateTool.execute(transformation_id, configuration)
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Failed to update transformation configuration" in result[0].text
            assert transformation_id in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_empty_transformation_id(self):
        """Test transformation update with empty transformation ID."""
        transformation_id = ""
        configuration = {"filename": "test.map"}
        
        result = await TransformationUpdateTool.execute(transformation_id, configuration)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Transformation ID cannot be empty" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_empty_configuration(self):
        """Test transformation update with empty configuration."""
        transformation_id = "map_test1"
        configuration = {}
        
        result = await TransformationUpdateTool.execute(transformation_id, configuration)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Configuration cannot be empty" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_invalid_configuration_type(self):
        """Test transformation update with invalid configuration type."""
        transformation_id = "map_test1"
        configuration = "invalid"
        
        result = await TransformationUpdateTool.execute(transformation_id, configuration)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Configuration must be a dictionary" in result[0].text


class TestTransformationUsageTool:
    """Unit tests for TransformationUsageTool."""
    
    @pytest.mark.asyncio
    async def test_execute_success_with_usage(self):
        """Test successful transformation usage query with usage found."""
        transformation_id = "map_test1"
        usage_locations = [
            {
                'type': 'item',
                'name': 'TestItem',
                'context': 'State description pattern'
            },
            {
                'type': 'link',
                'name': 'TestItem -> channel:test',
                'context': 'Link profile: transform:MAP'
            }
        ]
        
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_transformation_usage.return_value = usage_locations
            
            result = await TransformationUsageTool.execute(transformation_id)
            
            mock_client.get_transformation_usage.assert_called_once_with(transformation_id)
            assert len(result) == 1
            assert result[0].type == "text"
            assert transformation_id in result[0].text
            assert "is used in 2 location(s)" in result[0].text
            assert "TestItem" in result[0].text
            assert "item" in result[0].text.lower()
            assert "link" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_execute_success_no_usage(self):
        """Test successful transformation usage query with no usage found."""
        transformation_id = "map_test1"
        
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_transformation_usage.return_value = []
            
            result = await TransformationUsageTool.execute(transformation_id)
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert transformation_id in result[0].text
            assert "is not currently used" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_empty_transformation_id(self):
        """Test transformation usage query with empty transformation ID."""
        transformation_id = ""
        
        result = await TransformationUsageTool.execute(transformation_id)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Transformation ID cannot be empty" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_client_error(self):
        """Test transformation usage query with client error."""
        transformation_id = "map_test1"
        
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_transformation_usage.side_effect = Exception("Query failed")
            
            result = await TransformationUsageTool.execute(transformation_id)
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Failed to query transformation usage" in result[0].text
            assert "Query failed" in result[0].text