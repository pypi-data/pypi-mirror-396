"""
MCP resource implementations for openHAB data access.

This module provides MCP resources for read-only access to openHAB
documentation, system state, and other information.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp

from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError
from openhab_mcp_server.utils.config import get_config


logger = logging.getLogger(__name__)


class DocumentationResource:
    """Provides access to openHAB documentation."""
    
    def __init__(self, client: Optional[OpenHABClient] = None):
        """Initialize documentation resource.
        
        Args:
            client: OpenHAB client instance. If None, creates new one.
        """
        self.client = client or OpenHABClient()
        self.config = get_config()
        
        # openHAB documentation base URLs
        self.docs_base_url = "https://www.openhab.org/docs/"
        self.community_base_url = "https://community.openhab.org/"
        
        # Common documentation sections
        self.doc_sections = {
            "installation": "installation/",
            "tutorial": "tutorial/",
            "configuration": "configuration/",
            "concepts": "concepts/",
            "addons": "addons/",
            "administration": "administration/",
            "developer": "developer/",
            "ui": "ui/",
            "apps": "apps/"
        }
    
    async def get_content(self, uri: str) -> str:
        """Retrieve documentation content by URI.
        
        Args:
            uri: Documentation URI to retrieve
            
        Returns:
            Documentation content as string
            
        Raises:
            ValueError: If URI is invalid
            OpenHABError: If content retrieval fails
        """
        try:
            # Parse and validate URI
            parsed_uri = urlparse(uri)
            if not parsed_uri.scheme and not parsed_uri.netloc:
                # Relative URI - construct full URL
                if uri.startswith('/'):
                    uri = uri[1:]  # Remove leading slash
                full_url = urljoin(self.docs_base_url, uri)
            else:
                # Absolute URI - validate it's from openHAB docs
                if not (uri.startswith(self.docs_base_url) or 
                       uri.startswith(self.community_base_url)):
                    raise ValueError(
                        f"URI must be from openHAB documentation domains: "
                        f"{self.docs_base_url} or {self.community_base_url}"
                    )
                full_url = uri
            
            # Fetch content
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(full_url) as response:
                    if response.status == 404:
                        raise OpenHABError(f"Documentation not found: {uri}")
                    elif response.status >= 400:
                        raise OpenHABError(
                            f"Failed to retrieve documentation: HTTP {response.status}"
                        )
                    
                    content = await response.text()
                    logger.info(f"Retrieved documentation from {full_url}")
                    return content
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error retrieving documentation: {e}")
            raise OpenHABError(f"Network error: {e}")
        except asyncio.TimeoutError:
            logger.error("Timeout retrieving documentation")
            raise OpenHABError("Request timeout")
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search documentation for relevant content.
        
        Args:
            query: Search query string
            
        Returns:
            List of search results with title, URL, and excerpt
        """
        if not query or not query.strip():
            return []
        
        query = query.strip().lower()
        results = []
        
        # Search through common documentation sections
        for section_name, section_path in self.doc_sections.items():
            if query in section_name.lower():
                results.append({
                    "title": f"openHAB {section_name.title()} Documentation",
                    "url": urljoin(self.docs_base_url, section_path),
                    "excerpt": f"Complete guide for openHAB {section_name}",
                    "relevance": "high" if query == section_name.lower() else "medium"
                })
        
        # Add specific topic matches
        topic_matches = {
            "items": {
                "title": "Items Configuration",
                "url": urljoin(self.docs_base_url, "configuration/items.html"),
                "excerpt": "Learn how to define and configure openHAB items"
            },
            "things": {
                "title": "Things Configuration", 
                "url": urljoin(self.docs_base_url, "configuration/things.html"),
                "excerpt": "Configure things and bindings in openHAB"
            },
            "rules": {
                "title": "Rules and Automation",
                "url": urljoin(self.docs_base_url, "configuration/rules-dsl.html"),
                "excerpt": "Create automation rules using openHAB's rule engine"
            },
            "bindings": {
                "title": "Bindings Documentation",
                "url": urljoin(self.docs_base_url, "addons/bindings.html"),
                "excerpt": "Available bindings for connecting external systems"
            },
            "sitemap": {
                "title": "Sitemap Configuration",
                "url": urljoin(self.docs_base_url, "ui/sitemaps.html"),
                "excerpt": "Create user interfaces with sitemaps"
            },
            "persistence": {
                "title": "Persistence Services",
                "url": urljoin(self.docs_base_url, "configuration/persistence.html"),
                "excerpt": "Store and retrieve historical data"
            },
            "transformations": {
                "title": "Transformations",
                "url": urljoin(self.docs_base_url, "configuration/transformations.html"),
                "excerpt": "Transform data between different formats"
            },
            "rest": {
                "title": "REST API Documentation",
                "url": urljoin(self.docs_base_url, "configuration/restdocs.html"),
                "excerpt": "openHAB REST API reference and examples"
            }
        }
        
        for topic, info in topic_matches.items():
            if topic in query or any(word in query for word in topic.split()):
                result = dict(info)
                result["relevance"] = "high" if topic in query else "medium"
                results.append(result)
        
        # Add troubleshooting guides for error-related queries
        if any(word in query for word in ["error", "problem", "issue", "troubleshoot", "debug"]):
            results.append({
                "title": "Troubleshooting Guide",
                "url": urljoin(self.docs_base_url, "administration/logging.html"),
                "excerpt": "Debug and troubleshoot openHAB issues using logs",
                "relevance": "high"
            })
        
        # Sort by relevance (high first, then medium)
        results.sort(key=lambda x: (x["relevance"] != "high", x["title"]))
        
        logger.info(f"Found {len(results)} documentation results for query: {query}")
        return results
    
    def get_setup_guides(self) -> List[Dict[str, Any]]:
        """Get list of setup and configuration guides.
        
        Returns:
            List of setup guide information
        """
        guides = [
            {
                "title": "Installation Guide",
                "url": urljoin(self.docs_base_url, "installation/"),
                "description": "Complete installation instructions for all platforms",
                "category": "setup"
            },
            {
                "title": "First Steps Tutorial", 
                "url": urljoin(self.docs_base_url, "tutorial/"),
                "description": "Step-by-step tutorial for new users",
                "category": "tutorial"
            },
            {
                "title": "Configuration Overview",
                "url": urljoin(self.docs_base_url, "configuration/"),
                "description": "Overview of openHAB configuration concepts",
                "category": "configuration"
            },
            {
                "title": "Basic UI Setup",
                "url": urljoin(self.docs_base_url, "ui/basic/"),
                "description": "Set up the Basic UI for device control",
                "category": "ui"
            },
            {
                "title": "Paper UI Migration",
                "url": urljoin(self.docs_base_url, "administration/paperui.html"),
                "description": "Migrate from Paper UI to Main UI",
                "category": "migration"
            }
        ]
        
        return guides
    
    def get_troubleshooting_steps(self) -> List[Dict[str, Any]]:
        """Get common troubleshooting steps and solutions.
        
        Returns:
            List of troubleshooting information
        """
        steps = [
            {
                "issue": "Items not updating",
                "solution": "Check thing status and binding configuration",
                "url": urljoin(self.docs_base_url, "administration/logging.html"),
                "category": "items"
            },
            {
                "issue": "Rules not executing",
                "solution": "Verify rule syntax and check logs for errors",
                "url": urljoin(self.docs_base_url, "configuration/rules-dsl.html"),
                "category": "rules"
            },
            {
                "issue": "Binding connection issues",
                "solution": "Check network connectivity and binding configuration",
                "url": urljoin(self.docs_base_url, "addons/bindings.html"),
                "category": "bindings"
            },
            {
                "issue": "High memory usage",
                "solution": "Review persistence configuration and log levels",
                "url": urljoin(self.docs_base_url, "administration/logging.html"),
                "category": "performance"
            },
            {
                "issue": "UI not accessible",
                "solution": "Check firewall settings and port configuration",
                "url": urljoin(self.docs_base_url, "administration/security.html"),
                "category": "ui"
            }
        ]
        
        return steps


class SystemStateResource:
    """Provides read-only access to system state."""
    
    def __init__(self, client: Optional[OpenHABClient] = None):
        """Initialize system state resource.
        
        Args:
            client: OpenHAB client instance. If None, creates new one.
        """
        self.client = client or OpenHABClient()
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get overall system information.
        
        Returns:
            System information including version, status, and health
        """
        try:
            async with self.client:
                # Get basic system info
                system_info = await self.client.get_system_info()
                
                # Get additional status information
                bindings = await self.client.get_bindings()
                items = await self.client.get_items()
                things = await self.client.get_things()
                rules = await self.client.get_rules()
                
                # Calculate health metrics
                online_things = sum(1 for thing in things if thing.get('statusInfo', {}).get('status') == 'ONLINE')
                total_things = len(things)
                enabled_rules = sum(1 for rule in rules if self._get_rule_status(rule) == 'IDLE')
                
                return {
                    "system": system_info,
                    "health": {
                        "things_online": online_things,
                        "things_total": total_things,
                        "things_online_percentage": (online_things / total_things * 100) if total_things > 0 else 0,
                        "items_count": len(items),
                        "rules_enabled": enabled_rules,
                        "rules_total": len(rules),
                        "bindings_installed": len(bindings)
                    },
                    "status": "healthy" if online_things / max(total_things, 1) > 0.8 else "degraded"
                }
                
        except OpenHABError as e:
            logger.error(f"Failed to get system info: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    async def get_binding_status(self) -> List[Dict[str, Any]]:
        """Get status of all bindings.
        
        Returns:
            List of binding status information
        """
        try:
            async with self.client:
                bindings = await self.client.get_bindings()
                
                # Enhance binding info with status
                binding_status = []
                for binding in bindings:
                    binding_id = binding.get('id', 'unknown')
                    
                    # Get things using this binding
                    things = await self.client.get_things()
                    binding_things = [
                        thing for thing in things 
                        if thing.get('UID', '').startswith(f"{binding_id}:")
                    ]
                    
                    online_count = sum(
                        1 for thing in binding_things 
                        if thing.get('statusInfo', {}).get('status') == 'ONLINE'
                    )
                    
                    binding_status.append({
                        "id": binding_id,
                        "name": binding.get('name', binding_id),
                        "version": binding.get('version', 'unknown'),
                        "things_total": len(binding_things),
                        "things_online": online_count,
                        "status": "active" if online_count > 0 else "inactive",
                        "description": binding.get('description', '')
                    })
                
                return binding_status
                
        except OpenHABError as e:
            logger.error(f"Failed to get binding status: {e}")
            return []
    
    async def get_connectivity_status(self) -> Dict[str, Any]:
        """Get connectivity status for external services.
        
        Returns:
            Connectivity status information
        """
        try:
            async with self.client:
                # Test basic API connectivity
                system_info = await self.client.get_system_info()
                api_status = "connected"
                
                # Get things and check their connectivity
                things = await self.client.get_things()
                connectivity_summary = {
                    "api": {
                        "status": api_status,
                        "version": system_info.get('version', 'unknown')
                    },
                    "things": {
                        "total": len(things),
                        "online": sum(1 for t in things if t.get('statusInfo', {}).get('status') == 'ONLINE'),
                        "offline": sum(1 for t in things if t.get('statusInfo', {}).get('status') == 'OFFLINE'),
                        "unknown": sum(1 for t in things if t.get('statusInfo', {}).get('status') not in ['ONLINE', 'OFFLINE'])
                    }
                }
                
                return connectivity_summary
                
        except OpenHABError as e:
            logger.error(f"Failed to get connectivity status: {e}")
            return {
                "api": {"status": "error", "error": str(e)},
                "things": {"total": 0, "online": 0, "offline": 0, "unknown": 0}
            }
    
    def _get_rule_status(self, rule: Dict[str, Any]) -> str:
        """Get rule status handling both string and dict formats.
        
        Args:
            rule: Rule dictionary
            
        Returns:
            Rule status string
        """
        status = rule.get('status')
        if isinstance(status, dict):
            return status.get('status', 'UNKNOWN')
        elif isinstance(status, str):
            return status
        else:
            return 'UNKNOWN'