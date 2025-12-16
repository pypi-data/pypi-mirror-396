"""Unit tests for MCP resources."""

import pytest
import aiohttp
from unittest.mock import AsyncMock, patch
from aioresponses import aioresponses

from openhab_mcp_server.resources.openhab import DocumentationResource, SystemStateResource
from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError
from openhab_mcp_server.utils.config import Config


@pytest.fixture
def mock_config():
    """Create mock configuration for testing."""
    return Config(
        openhab_url="http://localhost:8080",
        openhab_token="test-token",
        timeout=30,
        log_level="INFO"
    )


@pytest.fixture
def mock_client():
    """Create mock OpenHAB client for testing."""
    client = AsyncMock(spec=OpenHABClient)
    return client


class TestDocumentationResource:
    """Test cases for DocumentationResource."""
    
    @pytest.fixture
    def doc_resource(self, mock_client):
        """Create DocumentationResource instance with mock client."""
        return DocumentationResource(client=mock_client)
    
    def test_init_with_client(self, mock_client):
        """Test initialization with provided client."""
        resource = DocumentationResource(client=mock_client)
        assert resource.client == mock_client
        assert resource.docs_base_url == "https://www.openhab.org/docs/"
        assert resource.community_base_url == "https://community.openhab.org/"
        assert "installation" in resource.doc_sections
        assert "configuration" in resource.doc_sections
    
    def test_init_without_client(self):
        """Test initialization without provided client creates new one."""
        with patch('openhab_mcp_server.resources.openhab.OpenHABClient') as mock_client_class:
            resource = DocumentationResource()
            mock_client_class.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_content_relative_uri(self, doc_resource):
        """Test retrieving content with relative URI."""
        with aioresponses() as m:
            expected_content = "<html><body>Installation Guide</body></html>"
            m.get(
                "https://www.openhab.org/docs/installation/",
                body=expected_content,
                content_type="text/html"
            )
            
            content = await doc_resource.get_content("installation/")
            assert content == expected_content
    
    @pytest.mark.asyncio
    async def test_get_content_absolute_uri_valid_domain(self, doc_resource):
        """Test retrieving content with absolute URI from valid domain."""
        with aioresponses() as m:
            expected_content = "<html><body>Tutorial</body></html>"
            url = "https://www.openhab.org/docs/tutorial/first_steps.html"
            m.get(url, body=expected_content, content_type="text/html")
            
            content = await doc_resource.get_content(url)
            assert content == expected_content
    
    @pytest.mark.asyncio
    async def test_get_content_absolute_uri_invalid_domain(self, doc_resource):
        """Test retrieving content with absolute URI from invalid domain raises error."""
        with pytest.raises(ValueError, match="URI must be from openHAB documentation domains"):
            await doc_resource.get_content("https://example.com/docs/")
    
    @pytest.mark.asyncio
    async def test_get_content_404_error(self, doc_resource):
        """Test handling of 404 errors."""
        with aioresponses() as m:
            m.get(
                "https://www.openhab.org/docs/nonexistent/",
                status=404
            )
            
            with pytest.raises(OpenHABError, match="Documentation not found"):
                await doc_resource.get_content("nonexistent/")
    
    @pytest.mark.asyncio
    async def test_get_content_server_error(self, doc_resource):
        """Test handling of server errors."""
        with aioresponses() as m:
            m.get(
                "https://www.openhab.org/docs/installation/",
                status=500
            )
            
            with pytest.raises(OpenHABError, match="Failed to retrieve documentation: HTTP 500"):
                await doc_resource.get_content("installation/")
    
    @pytest.mark.asyncio
    async def test_get_content_network_error(self, doc_resource):
        """Test handling of network errors."""
        with aioresponses() as m:
            m.get(
                "https://www.openhab.org/docs/installation/",
                exception=aiohttp.ClientError("Connection failed")
            )
            
            with pytest.raises(OpenHABError, match="Network error"):
                await doc_resource.get_content("installation/")
    
    @pytest.mark.asyncio
    async def test_search_empty_query(self, doc_resource):
        """Test search with empty query returns empty results."""
        results = await doc_resource.search("")
        assert results == []
        
        results = await doc_resource.search("   ")
        assert results == []
    
    @pytest.mark.asyncio
    async def test_search_section_match(self, doc_resource):
        """Test search matching documentation sections."""
        results = await doc_resource.search("installation")
        
        assert len(results) > 0
        installation_result = next(
            (r for r in results if "Installation" in r["title"]), None
        )
        assert installation_result is not None
        assert installation_result["relevance"] == "high"
        assert "installation/" in installation_result["url"]
    
    @pytest.mark.asyncio
    async def test_search_topic_match(self, doc_resource):
        """Test search matching specific topics."""
        results = await doc_resource.search("items")
        
        assert len(results) > 0
        items_result = next(
            (r for r in results if "Items Configuration" in r["title"]), None
        )
        assert items_result is not None
        assert "items.html" in items_result["url"]
    
    def test_get_setup_guides(self, doc_resource):
        """Test getting setup guides."""
        guides = doc_resource.get_setup_guides()
        
        assert len(guides) > 0
        assert all("title" in guide for guide in guides)
        assert all("url" in guide for guide in guides)
        assert all("description" in guide for guide in guides)
        assert all("category" in guide for guide in guides)
        
        # Check for expected guides
        titles = [guide["title"] for guide in guides]
        assert "Installation Guide" in titles
        assert "First Steps Tutorial" in titles
    
    def test_get_troubleshooting_steps(self, doc_resource):
        """Test getting troubleshooting steps."""
        steps = doc_resource.get_troubleshooting_steps()
        
        assert len(steps) > 0
        assert all("issue" in step for step in steps)
        assert all("solution" in step for step in steps)
        assert all("url" in step for step in steps)
        assert all("category" in step for step in steps)
        
        # Check for expected troubleshooting categories
        categories = [step["category"] for step in steps]
        assert "items" in categories
        assert "rules" in categories
        assert "bindings" in categories


class TestSystemStateResource:
    """Test cases for SystemStateResource."""
    
    @pytest.fixture
    def system_resource(self, mock_client):
        """Create SystemStateResource instance with mock client."""
        return SystemStateResource(client=mock_client)
    
    def test_init_with_client(self, mock_client):
        """Test initialization with provided client."""
        resource = SystemStateResource(client=mock_client)
        assert resource.client == mock_client
    
    def test_init_without_client(self):
        """Test initialization without provided client creates new one."""
        with patch('openhab_mcp_server.resources.openhab.OpenHABClient') as mock_client_class:
            resource = SystemStateResource()
            mock_client_class.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_system_info_success(self, system_resource, mock_client):
        """Test successful system info retrieval."""
        # Mock client responses
        mock_client.get_system_info.return_value = {
            "version": "3.4.0",
            "buildString": "Release Build"
        }
        mock_client.get_bindings.return_value = [
            {"id": "zwave", "name": "Z-Wave Binding"},
            {"id": "mqtt", "name": "MQTT Binding"}
        ]
        mock_client.get_items.return_value = [
            {"name": "TestItem1", "type": "Switch"},
            {"name": "TestItem2", "type": "Dimmer"}
        ]
        mock_client.get_things.return_value = [
            {"UID": "zwave:device:1", "statusInfo": {"status": "ONLINE"}},
            {"UID": "zwave:device:2", "statusInfo": {"status": "OFFLINE"}},
            {"UID": "mqtt:topic:3", "statusInfo": {"status": "ONLINE"}}
        ]
        mock_client.get_rules.return_value = [
            {"uid": "rule1", "status": {"status": "IDLE"}},
            {"uid": "rule2", "status": {"status": "DISABLED"}}
        ]
        
        # Configure async context manager
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        result = await system_resource.get_system_info()
        
        assert "system" in result
        assert "health" in result
        assert "status" in result
        
        assert result["system"]["version"] == "3.4.0"
        assert result["health"]["things_total"] == 3
        assert result["health"]["things_online"] == 2
        assert result["health"]["things_online_percentage"] == pytest.approx(66.67, rel=1e-2)
        assert result["health"]["items_count"] == 2
        assert result["health"]["rules_enabled"] == 1
        assert result["health"]["bindings_installed"] == 2
        assert result["status"] == "degraded"  # 66% < 80% threshold
    
    @pytest.mark.asyncio
    async def test_get_system_info_error(self, system_resource, mock_client):
        """Test system info retrieval with error."""
        mock_client.get_system_info.side_effect = OpenHABError("Connection failed")
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        result = await system_resource.get_system_info()
        
        assert "error" in result
        assert result["status"] == "error"
        assert "Connection failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_binding_status_success(self, system_resource, mock_client):
        """Test successful binding status retrieval."""
        mock_client.get_bindings.return_value = [
            {
                "id": "zwave",
                "name": "Z-Wave Binding",
                "version": "3.4.0",
                "description": "Z-Wave protocol support"
            }
        ]
        
        # Mock things for the binding
        mock_client.get_things.return_value = [
            {"UID": "zwave:device:1", "statusInfo": {"status": "ONLINE"}},
            {"UID": "zwave:device:2", "statusInfo": {"status": "OFFLINE"}}
        ]
        
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        result = await system_resource.get_binding_status()
        
        assert len(result) == 1
        
        zwave_status = result[0]
        assert zwave_status["id"] == "zwave"
        assert zwave_status["name"] == "Z-Wave Binding"
        assert zwave_status["things_total"] == 2
        assert zwave_status["things_online"] == 1
        assert zwave_status["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_get_connectivity_status_success(self, system_resource, mock_client):
        """Test successful connectivity status retrieval."""
        mock_client.get_system_info.return_value = {
            "version": "3.4.0",
            "buildString": "Release Build"
        }
        mock_client.get_things.return_value = [
            {"UID": "thing1", "statusInfo": {"status": "ONLINE"}},
            {"UID": "thing2", "statusInfo": {"status": "OFFLINE"}},
            {"UID": "thing3", "statusInfo": {"status": "UNKNOWN"}},
            {"UID": "thing4", "statusInfo": {"status": "ONLINE"}}
        ]
        
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        result = await system_resource.get_connectivity_status()
        
        assert "api" in result
        assert "things" in result
        
        assert result["api"]["status"] == "connected"
        assert result["api"]["version"] == "3.4.0"
        
        assert result["things"]["total"] == 4
        assert result["things"]["online"] == 2
        assert result["things"]["offline"] == 1
        assert result["things"]["unknown"] == 1
