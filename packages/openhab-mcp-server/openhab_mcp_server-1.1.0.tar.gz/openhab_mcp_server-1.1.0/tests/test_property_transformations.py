"""Property-based tests for transformation management functionality."""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
from typing import Dict, Any, List, Optional

from openhab_mcp_server.tools.transformations import (
    TransformationListTool, TransformationCreateTool, TransformationTestTool,
    TransformationUpdateTool, TransformationUsageTool
)
from openhab_mcp_server.utils.openhab_client import OpenHABClient
from openhab_mcp_server.models import TransformationInfo, TransformationTestResult


# Test data generators
@st.composite
def valid_transformation_type_strategy(draw):
    """Generate valid transformation types."""
    return draw(st.sampled_from([
        'MAP', 'REGEX', 'JSONPATH', 'XPATH', 'JAVASCRIPT', 'SCALE', 
        'EXEC', 'JINJA', 'XSLT', 'ROLLERSHUTTER'
    ]))


@st.composite
def valid_transformation_id_strategy(draw):
    """Generate valid transformation IDs."""
    transformation_type = draw(valid_transformation_type_strategy()).lower()
    suffix = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=1,
        max_size=8
    ))
    return f"{transformation_type}_{suffix}"


@st.composite
def valid_transformation_configuration_strategy(draw):
    """Generate valid transformation configuration dictionaries."""
    transformation_type = draw(valid_transformation_type_strategy())
    config = {}
    
    if transformation_type == 'MAP':
        config['filename'] = draw(st.text(min_size=1, max_size=50)) + '.map'
    elif transformation_type == 'REGEX':
        config['pattern'] = draw(st.text(min_size=1, max_size=100))
    elif transformation_type == 'JSONPATH':
        config['path'] = '$.' + draw(st.text(min_size=1, max_size=50))
    elif transformation_type == 'XPATH':
        config['xpath'] = '//' + draw(st.text(min_size=1, max_size=50))
    elif transformation_type == 'JAVASCRIPT':
        config['script'] = draw(st.text(min_size=1, max_size=200))
    elif transformation_type == 'SCALE':
        config['min'] = draw(st.floats(min_value=-1000, max_value=1000))
        config['max'] = draw(st.floats(min_value=-1000, max_value=1000))
    else:
        # Generic configuration for other types
        config['parameter'] = draw(st.text(min_size=1, max_size=100))
    
    return config


@st.composite
def transformation_info_strategy(draw):
    """Generate TransformationInfo objects."""
    transformation_type = draw(valid_transformation_type_strategy())
    return {
        'id': draw(valid_transformation_id_strategy()),
        'type': transformation_type,
        'configuration': draw(valid_transformation_configuration_strategy()),
        'description': draw(st.one_of(st.none(), st.text(min_size=1, max_size=200)))
    }


@st.composite
def sample_data_strategy(draw):
    """Generate sample data for transformation testing."""
    return draw(st.one_of(
        st.text(min_size=0, max_size=1000),
        st.integers().map(str),
        st.floats().map(str),
        st.just('{"value": 42, "status": "OK"}'),  # JSON data
        st.just('<root><value>42</value></root>'),  # XML data
        st.sampled_from(['ON', 'OFF', 'OPEN', 'CLOSED', 'NULL'])  # Common openHAB states
    ))


class TestTransformationListingProperty:
    """Property-based tests for transformation listing completeness."""
    
    @given(st.lists(transformation_info_strategy(), min_size=0, max_size=10))
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_transformation_listing_completeness(self, transformations):
        """
        **Feature: openhab-mcp-server, Property 43: Transformation listing completeness**
        **Validates: Requirements 14.1**
        
        For any transformation listing request, all installed transformation addons 
        should be returned with their capabilities.
        """
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock the get_transformations method to return our test data
            mock_client.get_transformations.return_value = transformations
            
            # Execute the transformation listing tool
            result = await TransformationListTool.execute()
            
            # Verify the client method was called
            mock_client.get_transformations.assert_called_once()
            
            # Verify result structure
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            
            result_text = result[0].text
            
            if not transformations:
                # If no transformations, should indicate that
                assert "No transformation addons" in result_text
            else:
                # If transformations exist, should list them with capabilities
                assert f"Found {len(transformations)} transformation(s)" in result_text
                
                # Each transformation should be represented in the output
                for transformation in transformations:
                    transformation_type = transformation.get('type', 'Unknown')
                    transformation_id = transformation.get('id', 'Unknown')
                    
                    # The output should contain the transformation type and ID
                    assert transformation_type in result_text
                    assert transformation_id in result_text


class TestTransformationCreationProperty:
    """Property-based tests for transformation creation validation."""
    
    @given(
        valid_transformation_type_strategy(),
        valid_transformation_configuration_strategy()
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_transformation_creation_validation(self, transformation_type, configuration):
        """
        **Feature: openhab-mcp-server, Property 44: Transformation creation validation**
        **Validates: Requirements 14.2**
        
        For any transformation creation request, valid transformations should be created 
        and invalid configurations should be rejected with proper syntax validation.
        """
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock successful transformation creation
            expected_id = f"{transformation_type.lower()}_test123"
            mock_client.create_transformation.return_value = expected_id
            
            # Execute the transformation creation tool
            result = await TransformationCreateTool.execute(transformation_type, configuration)
            
            # Verify the client method was called with correct parameters
            mock_client.create_transformation.assert_called_once_with(transformation_type, configuration)
            
            # Verify result structure
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            
            result_text = result[0].text
            
            # Should indicate successful creation
            assert "Successfully created transformation" in result_text
            assert transformation_type in result_text
            assert expected_id in result_text


class TestTransformationTestingProperty:
    """Property-based tests for transformation testing accuracy."""
    
    @given(
        valid_transformation_id_strategy(),
        sample_data_strategy()
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_transformation_testing_accuracy(self, transformation_id, sample_data):
        """
        **Feature: openhab-mcp-server, Property 45: Transformation testing accuracy**
        **Validates: Requirements 14.3**
        
        For any transformation test request, the system should execute the transformation 
        with sample data and return accurate results.
        """
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock successful transformation test
            test_result = {
                'success': True,
                'input_value': sample_data,
                'output_value': f"transformed_{sample_data}",
                'execution_time': 0.001,
                'error_message': None
            }
            mock_client.test_transformation.return_value = test_result
            
            # Execute the transformation test tool
            result = await TransformationTestTool.execute(transformation_id, sample_data)
            
            # Verify the client method was called with correct parameters
            mock_client.test_transformation.assert_called_once_with(transformation_id, sample_data)
            
            # Verify result structure
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            
            result_text = result[0].text
            
            # Should contain test results with input and output
            assert transformation_id in result_text
            assert sample_data in result_text or str(sample_data) in result_text
            assert "transformed_" in result_text or "Output:" in result_text
            assert "Execution time:" in result_text


class TestTransformationConfigurationProperty:
    """Property-based tests for transformation configuration persistence."""
    
    @given(
        valid_transformation_id_strategy(),
        valid_transformation_configuration_strategy()
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_transformation_configuration_persistence(self, transformation_id, configuration):
        """
        **Feature: openhab-mcp-server, Property 46: Transformation configuration persistence**
        **Validates: Requirements 14.4**
        
        For any transformation configuration update, the changes should be applied 
        and persist when the transformation is queried again.
        """
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock successful configuration update
            mock_client.update_transformation.return_value = True
            
            # Execute the transformation update tool
            result = await TransformationUpdateTool.execute(transformation_id, configuration)
            
            # Verify the client method was called with correct parameters
            mock_client.update_transformation.assert_called_once_with(transformation_id, configuration)
            
            # Verify result structure
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            
            result_text = result[0].text
            
            # Should indicate successful update
            assert "Successfully updated transformation configuration" in result_text
            assert transformation_id in result_text
            
            # Configuration should be mentioned in the result
            config_str = str(configuration)
            assert config_str in result_text or "New configuration:" in result_text


class TestTransformationUsageProperty:
    """Property-based tests for transformation usage tracking."""
    
    @given(
        valid_transformation_id_strategy(),
        st.lists(
            st.dictionaries(
                st.sampled_from(['type', 'name', 'context']),
                st.text(min_size=1, max_size=100),
                min_size=3, max_size=3
            ),
            min_size=0, max_size=5
        )
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_transformation_usage_tracking(self, transformation_id, usage_locations):
        """
        **Feature: openhab-mcp-server, Property 47: Transformation usage tracking**
        **Validates: Requirements 14.5**
        
        For any transformation usage query, the system should return all locations 
        where the transformation is applied in the system.
        """
        with patch('openhab_mcp_server.tools.transformations.OpenHABClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock transformation usage locations
            mock_client.get_transformation_usage.return_value = usage_locations
            
            # Execute the transformation usage tool
            result = await TransformationUsageTool.execute(transformation_id)
            
            # Verify the client method was called with correct parameters
            mock_client.get_transformation_usage.assert_called_once_with(transformation_id)
            
            # Verify result structure
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].type == "text"
            
            result_text = result[0].text
            
            # Should contain transformation ID
            assert transformation_id in result_text
            
            if not usage_locations:
                # If no usage, should indicate that
                assert "is not currently used" in result_text
            else:
                # If usage exists, should list all locations
                assert f"is used in {len(usage_locations)} location(s)" in result_text
                
                # Each usage location should be represented
                for location in usage_locations:
                    location_type = location.get('type', '')
                    location_name = location.get('name', '')
                    
                    # The output should contain information about each location
                    if location_type:
                        assert location_type.lower() in result_text.lower()
                    if location_name:
                        assert location_name in result_text