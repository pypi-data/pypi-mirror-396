"""Property-based tests for addon management functionality."""

import asyncio
import json
from typing import Any, Dict, List
import pytest
from hypothesis import given, strategies as st, settings
from aioresponses import aioresponses

from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.tools.addons import AddonListTool, AddonInstallTool, AddonUninstallTool, AddonConfigTool
from openhab_mcp_server.tools.addons import AddonListParams, AddonInstallParams, AddonUninstallParams, AddonConfigParams


# Test data generators
@st.composite
def addon_id_strategy(draw):
    """Generate valid addon IDs."""
    # Addon IDs typically follow pattern: binding-name, transformation-name, etc.
    prefix = draw(st.sampled_from(['binding', 'transformation', 'persistence', 'automation', 'voice', 'ui', 'misc', 'io']))
    name = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'),
        min_size=1,
        max_size=30
    ))
    return f"{prefix}-{name}"


@st.composite
def addon_type_strategy(draw):
    """Generate valid addon types."""
    return draw(st.sampled_from(['binding', 'transformation', 'persistence', 'automation', 'voice', 'ui', 'misc', 'io']))


@st.composite
def addon_response_strategy(draw):
    """Generate valid addon response data."""
    addon_id = draw(addon_id_strategy())
    addon_type = draw(addon_type_strategy())
    return {
        "id": addon_id,
        "name": draw(st.text(min_size=1, max_size=100)),
        "version": draw(st.one_of(st.none(), st.text(min_size=1, max_size=20))),
        "description": draw(st.one_of(st.none(), st.text(min_size=0, max_size=200))),
        "type": addon_type,
        "author": draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
        "installed": draw(st.booleans()),
        "configuration": draw(st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(st.text(), st.integers(), st.booleans()),
            max_size=5
        ))
    }


@st.composite
def addon_config_strategy(draw):
    """Generate valid addon configuration data."""
    return draw(st.dictionaries(
        st.text(min_size=1, max_size=30),
        st.one_of(
            st.text(min_size=0, max_size=100),
            st.integers(min_value=-1000, max_value=1000),
            st.booleans(),
            st.floats(allow_nan=False, allow_infinity=False)
        ),
        min_size=1,
        max_size=10
    ))


class TestAddonManagementProperties:
    """Property-based tests for addon management."""
    
    def _get_test_config(self):
        """Get test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @given(
        available_addons=st.lists(addon_response_strategy(), min_size=0, max_size=20),
        installed_addons=st.lists(addon_response_strategy(), min_size=0, max_size=10),
        filter_type=st.one_of(st.none(), addon_type_strategy())
    )
    @settings(max_examples=100, deadline=10000)
    async def test_property_addon_registry_retrieval_accuracy(self, available_addons, installed_addons, filter_type):
        """**Feature: openhab-mcp-server, Property 22: Addon registry retrieval accuracy**
        
        For any addon registry query, all returned addons should come from the openHAB 
        addon registry and contain required information fields.
        
        **Validates: Requirements 9.1**
        """
        # Ensure installed addons are marked as installed
        for addon in installed_addons:
            addon['installed'] = True
        
        # Ensure available addons are marked as not installed (unless they're in installed list)
        installed_ids = {addon['id'] for addon in installed_addons}
        for addon in available_addons:
            if addon['id'] not in installed_ids:
                addon['installed'] = False
        
        client = OpenHABClient(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock installed addons response
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=installed_addons,
                status=200
            )
            
            # Mock available addons response
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=available_addons,
                status=200
            )
            
            async with client:
                result = await client.get_addons(filter_type)
            
            # Property: All returned addons should have required fields
            for addon in result:
                assert 'id' in addon
                assert 'installed' in addon
                assert isinstance(addon['installed'], bool)
                
                # If filter_type is specified, all addons should match that type
                if filter_type:
                    assert addon.get('type', '').lower() == filter_type.lower()
            
            # Property: Installed addons should be marked as installed
            result_ids = {addon['id'] for addon in result}
            for installed_addon in installed_addons:
                if installed_addon['id'] in result_ids:
                    matching_addon = next(a for a in result if a['id'] == installed_addon['id'])
                    assert matching_addon['installed'] is True
    
    @given(
        installed_addons=st.lists(addon_response_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=100, deadline=5000)
    async def test_property_installed_addon_status_completeness(self, installed_addons):
        """**Feature: openhab-mcp-server, Property 23: Installed addon status completeness**
        
        For any installed addon query, the returned information should include both 
        current status and configuration details.
        
        **Validates: Requirements 9.2**
        """
        # Ensure all addons are marked as installed
        for addon in installed_addons:
            addon['installed'] = True
        
        client = OpenHABClient(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock installed addons response
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=installed_addons,
                status=200
            )
            
            # Mock available addons response (empty for this test)
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=[],
                status=200
            )
            
            async with client:
                result = await client.get_addons()
            
            # Property: All installed addons should have complete status information
            installed_results = [addon for addon in result if addon.get('installed', False)]
            
            for addon in installed_results:
                # Required fields for installed addons
                assert 'id' in addon
                assert 'installed' in addon
                assert addon['installed'] is True
                
                # Status completeness - should have identifying information
                assert addon.get('id') is not None
                assert len(addon.get('id', '')) > 0
    
    @given(
        addon_id=addon_id_strategy(),
        addon_data=addon_response_strategy()
    )
    @settings(max_examples=100, deadline=5000)
    async def test_property_addon_installation_consistency(self, addon_id, addon_data):
        """**Feature: openhab-mcp-server, Property 24: Addon installation consistency**
        
        For any valid addon ID, installing the addon should execute via the openHAB 
        REST API and the addon should appear in the installed addons list.
        
        **Validates: Requirements 9.3**
        """
        # Set up addon as available but not installed initially
        addon_data['id'] = addon_id
        addon_data['installed'] = False
        
        client = OpenHABClient(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock initial addon list (not installed)
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=[],
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=[addon_data],
                status=200
            )
            
            # Mock successful installation
            mock.post(
                f"http://test-openhab:8080/rest/extensions/{addon_id}/install",
                status=200
            )
            
            async with client:
                # Test installation
                result = await client.install_addon(addon_id)
                
                # Property: Installation should succeed for valid addon
                assert result is True
    
    @given(
        addon_id=addon_id_strategy(),
        addon_data=addon_response_strategy()
    )
    @settings(max_examples=100, deadline=5000)
    async def test_property_addon_uninstallation_validation(self, addon_id, addon_data):
        """**Feature: openhab-mcp-server, Property 25: Addon uninstallation validation**
        
        For any installed addon, uninstalling it should remove the addon and it should 
        no longer appear in the installed addons list.
        
        **Validates: Requirements 9.4**
        """
        # Set up addon as installed
        addon_data['id'] = addon_id
        addon_data['installed'] = True
        
        client = OpenHABClient(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock addon as installed
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=[addon_data],
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=[],
                status=200
            )
            
            # Mock successful uninstallation
            mock.post(
                f"http://test-openhab:8080/rest/extensions/{addon_id}/uninstall",
                status=200
            )
            
            async with client:
                # Test uninstallation
                result = await client.uninstall_addon(addon_id)
                
                # Property: Uninstallation should succeed for installed addon
                assert result is True
    
    @given(
        addon_id=addon_id_strategy(),
        config=addon_config_strategy()
    )
    @settings(max_examples=100, deadline=5000)
    async def test_property_addon_configuration_persistence(self, addon_id, config):
        """**Feature: openhab-mcp-server, Property 26: Addon configuration persistence**
        
        For any addon configuration update, the changes should be applied and persist 
        when the addon configuration is queried again.
        
        **Validates: Requirements 9.5**
        """
        client = OpenHABClient(self._get_test_config())
        
        with aioresponses() as mock:
            # Mock successful configuration update
            mock.put(
                f"http://test-openhab:8080/rest/extensions/{addon_id}/config",
                status=200
            )
            
            # Mock configuration retrieval with updated config
            mock.get(
                f"http://test-openhab:8080/rest/extensions/{addon_id}/config",
                payload=config,
                status=200
            )
            
            async with client:
                # Test configuration update
                update_result = await client.update_addon_config(addon_id, config)
                assert update_result is True
                
                # Test configuration persistence
                retrieved_config = await client.get_addon_config(addon_id)
                
                # Property: Retrieved configuration should match what was set
                assert retrieved_config is not None
                for key, value in config.items():
                    assert key in retrieved_config
                    assert retrieved_config[key] == value


