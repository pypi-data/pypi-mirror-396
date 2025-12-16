"""Unit tests for addon management tools."""

import pytest
from aioresponses import aioresponses

from openhab_mcp_server.tools.addons import (
    AddonListTool, AddonInstallTool, AddonUninstallTool, AddonConfigTool,
    AddonListParams, AddonInstallParams, AddonUninstallParams, AddonConfigParams
)
from openhab_mcp_server.utils.config import Config


class TestAddonTools:
    """Unit tests for addon management tools."""
    
    def _get_test_config(self):
        """Get test configuration."""
        return Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
    
    @pytest.mark.asyncio
    async def test_addon_list_tool_all_addons(self):
        """Test listing all addons."""
        config = self._get_test_config()
        tool = AddonListTool(config)
        
        installed_addons = [
            {
                "id": "binding-zwave",
                "name": "Z-Wave Binding",
                "type": "binding",
                "version": "3.4.0",
                "installed": True
            }
        ]
        
        available_addons = [
            {
                "id": "binding-mqtt",
                "name": "MQTT Binding", 
                "type": "binding",
                "version": "3.4.0",
                "installed": False
            }
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=installed_addons,
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=available_addons,
                status=200
            )
            
            params = AddonListParams()
            result = await tool.execute(params)
            
            assert len(result) == 1
            assert "2 addon(s)" in result[0].text
            assert "Z-Wave Binding" in result[0].text
            assert "MQTT Binding" in result[0].text
    
    @pytest.mark.asyncio
    async def test_addon_list_tool_filter_by_type(self):
        """Test listing addons filtered by type."""
        config = self._get_test_config()
        tool = AddonListTool(config)
        
        installed_addons = [
            {
                "id": "binding-zwave",
                "name": "Z-Wave Binding",
                "type": "binding",
                "version": "3.4.0",
                "installed": True
            }
        ]
        
        available_addons = [
            {
                "id": "transformation-map",
                "name": "Map Transformation",
                "type": "transformation", 
                "version": "3.4.0",
                "installed": False
            }
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=installed_addons,
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=available_addons,
                status=200
            )
            
            params = AddonListParams(filter_type="binding")
            result = await tool.execute(params)
            
            assert len(result) == 1
            assert "1 addon(s)" in result[0].text
            assert "Z-Wave Binding" in result[0].text
            assert "Map Transformation" not in result[0].text
    
    @pytest.mark.asyncio
    async def test_addon_list_tool_installed_only(self):
        """Test listing only installed addons."""
        config = self._get_test_config()
        tool = AddonListTool(config)
        
        installed_addons = [
            {
                "id": "binding-zwave",
                "name": "Z-Wave Binding",
                "type": "binding",
                "version": "3.4.0",
                "installed": True
            }
        ]
        
        available_addons = [
            {
                "id": "binding-mqtt",
                "name": "MQTT Binding",
                "type": "binding",
                "version": "3.4.0",
                "installed": False
            }
        ]
        
        with aioresponses() as mock:
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=installed_addons,
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=available_addons,
                status=200
            )
            
            params = AddonListParams(installed_only=True)
            result = await tool.execute(params)
            
            assert len(result) == 1
            assert "1 addon(s)" in result[0].text
            assert "Z-Wave Binding" in result[0].text
            assert "MQTT Binding" not in result[0].text
    
    @pytest.mark.asyncio
    async def test_addon_install_tool_success(self):
        """Test successful addon installation."""
        config = self._get_test_config()
        tool = AddonInstallTool(config)
        
        available_addon = {
            "id": "binding-mqtt",
            "name": "MQTT Binding",
            "type": "binding",
            "installed": False
        }
        
        with aioresponses() as mock:
            # Mock addon list to check if addon exists
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=[],
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=[available_addon],
                status=200
            )
            
            # Mock successful installation
            mock.post(
                "http://test-openhab:8080/rest/extensions/binding-mqtt/install",
                status=200
            )
            
            params = AddonInstallParams(addon_id="binding-mqtt")
            result = await tool.execute(params)
            
            assert len(result) == 1
            assert "Successfully installed addon 'binding-mqtt'" in result[0].text
    
    @pytest.mark.asyncio
    async def test_addon_install_tool_already_installed(self):
        """Test installing an already installed addon."""
        config = self._get_test_config()
        tool = AddonInstallTool(config)
        
        installed_addon = {
            "id": "binding-mqtt",
            "name": "MQTT Binding",
            "type": "binding",
            "installed": True
        }
        
        with aioresponses() as mock:
            # Mock addon list showing addon as installed
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=[installed_addon],
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=[],
                status=200
            )
            
            params = AddonInstallParams(addon_id="binding-mqtt")
            result = await tool.execute(params)
            
            assert len(result) == 1
            assert "already installed" in result[0].text
    
    @pytest.mark.asyncio
    async def test_addon_install_tool_not_found(self):
        """Test installing a non-existent addon."""
        config = self._get_test_config()
        tool = AddonInstallTool(config)
        
        with aioresponses() as mock:
            # Mock empty addon lists
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=[],
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=[],
                status=200
            )
            
            params = AddonInstallParams(addon_id="binding-nonexistent")
            result = await tool.execute(params)
            
            assert len(result) == 1
            assert "not found in registry" in result[0].text
    
    @pytest.mark.asyncio
    async def test_addon_uninstall_tool_success(self):
        """Test successful addon uninstallation."""
        config = self._get_test_config()
        tool = AddonUninstallTool(config)
        
        installed_addon = {
            "id": "binding-mqtt",
            "name": "MQTT Binding",
            "type": "binding",
            "installed": True
        }
        
        with aioresponses() as mock:
            # Mock addon list showing addon as installed
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=[installed_addon],
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=[],
                status=200
            )
            
            # Mock successful uninstallation
            mock.post(
                "http://test-openhab:8080/rest/extensions/binding-mqtt/uninstall",
                status=200
            )
            
            params = AddonUninstallParams(addon_id="binding-mqtt")
            result = await tool.execute(params)
            
            assert len(result) == 1
            assert "Successfully uninstalled addon 'binding-mqtt'" in result[0].text
    
    @pytest.mark.asyncio
    async def test_addon_uninstall_tool_not_installed(self):
        """Test uninstalling a non-installed addon."""
        config = self._get_test_config()
        tool = AddonUninstallTool(config)
        
        available_addon = {
            "id": "binding-mqtt",
            "name": "MQTT Binding",
            "type": "binding",
            "installed": False
        }
        
        with aioresponses() as mock:
            # Mock addon list showing addon as not installed
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=[],
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=[available_addon],
                status=200
            )
            
            params = AddonUninstallParams(addon_id="binding-mqtt")
            result = await tool.execute(params)
            
            assert len(result) == 1
            assert "is not installed" in result[0].text
    
    @pytest.mark.asyncio
    async def test_addon_config_tool_success(self):
        """Test successful addon configuration update."""
        config = self._get_test_config()
        tool = AddonConfigTool(config)
        
        installed_addon = {
            "id": "binding-mqtt",
            "name": "MQTT Binding",
            "type": "binding",
            "installed": True
        }
        
        config_params = {
            "broker_url": "tcp://localhost:1883",
            "username": "test_user"
        }
        
        with aioresponses() as mock:
            # Mock addon list showing addon as installed
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=[installed_addon],
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=[],
                status=200
            )
            
            # Mock successful configuration update
            mock.put(
                "http://test-openhab:8080/rest/extensions/binding-mqtt/config",
                status=200
            )
            
            params = AddonConfigParams(addon_id="binding-mqtt", config=config_params)
            result = await tool.execute(params)
            
            assert len(result) == 1
            assert "Successfully updated configuration" in result[0].text
            assert "broker_url, username" in result[0].text
    
    @pytest.mark.asyncio
    async def test_addon_config_tool_not_installed(self):
        """Test configuring a non-installed addon."""
        config = self._get_test_config()
        tool = AddonConfigTool(config)
        
        available_addon = {
            "id": "binding-mqtt",
            "name": "MQTT Binding",
            "type": "binding",
            "installed": False
        }
        
        config_params = {
            "broker_url": "tcp://localhost:1883"
        }
        
        with aioresponses() as mock:
            # Mock addon list showing addon as not installed
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=[],
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=[available_addon],
                status=200
            )
            
            params = AddonConfigParams(addon_id="binding-mqtt", config=config_params)
            result = await tool.execute(params)
            
            assert len(result) == 1
            assert "is not installed" in result[0].text
            assert "Configuration can only be updated for installed addons" in result[0].text
    
    @pytest.mark.asyncio
    async def test_addon_config_tool_not_found(self):
        """Test configuring a non-existent addon."""
        config = self._get_test_config()
        tool = AddonConfigTool(config)
        
        config_params = {
            "param1": "value1"
        }
        
        with aioresponses() as mock:
            # Mock empty addon lists
            mock.get(
                "http://test-openhab:8080/rest/extensions",
                payload=[],
                status=200
            )
            mock.get(
                "http://test-openhab:8080/rest/extensions/types",
                payload=[],
                status=200
            )
            
            params = AddonConfigParams(addon_id="binding-nonexistent", config=config_params)
            result = await tool.execute(params)
            
            assert len(result) == 1
            assert "not found" in result[0].text