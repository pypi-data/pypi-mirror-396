"""Property-based tests for MCP resources."""

import asyncio
from typing import Any, Dict, List
import pytest
from hypothesis import given, strategies as st, settings
from aioresponses import aioresponses

from openhab_mcp_server.resources.openhab import DocumentationResource, SystemStateResource
from openhab_mcp_server.utils.openhab_client import OpenHABClient
from openhab_mcp_server.utils.config import Config


# Test data generators
@st.composite
def documentation_query_strategy(draw):
    """Generate valid documentation queries."""
    return draw(st.one_of(
        st.sampled_from([
            "items", "things", "rules", "bindings", "installation", 
            "configuration", "tutorial", "sitemap", "persistence",
            "transformations", "rest", "api", "troubleshoot", "error"
        ]),
        st.text(min_size=1, max_size=50).filter(lambda x: x.strip())
    ))


@st.composite
def documentation_uri_strategy(draw):
    """Generate valid documentation URIs."""
    sections = [
        "installation/", "tutorial/", "configuration/", "concepts/",
        "addons/", "administration/", "developer/", "ui/", "apps/"
    ]
    
    return draw(st.one_of(
        st.sampled_from(sections),  # Section URIs
        st.sampled_from([
            "configuration/items.html",
            "configuration/things.html", 
            "configuration/rules-dsl.html",
            "addons/bindings.html",
            "ui/sitemaps.html",
            "administration/logging.html"
        ]),  # Specific page URIs
        st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='/-_.'),
            min_size=1,
            max_size=100
        ).map(lambda x: x + ".html")  # Generated URIs
    ))


@st.composite
def system_info_strategy(draw):
    """Generate valid system info responses."""
    return {
        "version": draw(st.text(min_size=1, max_size=20)),
        "buildString": draw(st.text(min_size=1, max_size=100)),
        "locale": draw(st.sampled_from(["en_US", "de_DE", "fr_FR", "es_ES"])),
        "measurementSystem": draw(st.sampled_from(["metric", "imperial"])),
        "startLevel": draw(st.integers(min_value=50, max_value=100))
    }


@st.composite
def binding_data_strategy(draw):
    """Generate valid binding data."""
    binding_id = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=1,
        max_size=20
    ))
    
    return {
        "id": binding_id,
        "name": draw(st.text(min_size=1, max_size=50)),
        "version": draw(st.text(min_size=1, max_size=20)),
        "description": draw(st.text(min_size=0, max_size=200))
    }


@st.composite
def thing_data_strategy(draw):
    """Generate valid thing data."""
    binding_id = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=1,
        max_size=20
    ))
    thing_type = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=1,
        max_size=20
    ))
    thing_id = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'),
        min_size=1,
        max_size=20
    ))
    
    return {
        "UID": f"{binding_id}:{thing_type}:{thing_id}",
        "label": draw(st.text(min_size=1, max_size=100)),
        "statusInfo": {
            "status": draw(st.sampled_from(["ONLINE", "OFFLINE", "UNKNOWN"])),
            "statusDetail": draw(st.text(min_size=1, max_size=50))
        },
        "configuration": draw(st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(st.text(min_size=1, max_size=50), st.integers(), st.booleans()),
            max_size=5
        ))
    }


class TestDocumentationResourceProperties:
    """Property-based tests for DocumentationResource."""
    
    def _get_test_resource(self):
        """Get test documentation resource."""
        config = Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
        client = OpenHABClient(config)
        return DocumentationResource(client)
    
    @given(query=documentation_query_strategy())
    @settings(max_examples=100, deadline=5000)
    async def test_property_documentation_retrieval_completeness(self, query):
        """**Feature: openhab-mcp-server, Property 1: Documentation retrieval completeness**
        
        For any valid documentation query, the returned content should include 
        setup guides, configuration examples, and troubleshooting steps when available.
        
        **Validates: Requirements 1.1, 1.2**
        """
        resource = self._get_test_resource()
        
        # Execute search
        results = await resource.search(query)
        
        # Property: Search should return a list of results
        assert isinstance(results, list)
        
        if results:  # If results are found
            for result in results:
                # Property: Each result should have required fields
                assert "title" in result
                assert "url" in result
                assert "excerpt" in result
                assert "relevance" in result
                
                # Property: Title and excerpt should be non-empty strings
                assert isinstance(result["title"], str)
                assert len(result["title"]) > 0
                assert isinstance(result["excerpt"], str)
                assert len(result["excerpt"]) > 0
                
                # Property: URL should be a valid openHAB documentation URL
                assert result["url"].startswith("https://www.openhab.org/docs/")
                
                # Property: Relevance should be either "high" or "medium"
                assert result["relevance"] in ["high", "medium"]
        
        # Property: For specific queries, should include relevant content types
        if query.lower() in ["installation", "setup"]:
            # Should include setup guides
            setup_results = [r for r in results if "setup" in r["title"].lower() or "installation" in r["title"].lower()]
            assert len(setup_results) > 0
        
        if query.lower() in ["configuration", "config"]:
            # Should include configuration examples
            config_results = [r for r in results if "configuration" in r["title"].lower() or "config" in r["excerpt"].lower()]
            assert len(config_results) > 0
        
        if query.lower() in ["troubleshoot", "error", "problem", "debug"]:
            # Should include troubleshooting steps
            troubleshoot_results = [r for r in results if any(
                keyword in r["title"].lower() or keyword in r["excerpt"].lower()
                for keyword in ["troubleshoot", "debug", "log", "error"]
            )]
            assert len(troubleshoot_results) > 0
    
    @given(query=documentation_query_strategy())
    @settings(max_examples=100, deadline=5000)
    async def test_property_search_relevance_consistency(self, query):
        """**Feature: openhab-mcp-server, Property 2: Search relevance consistency**
        
        For any search query, all returned documentation sections should be 
        contextually relevant to the search terms.
        
        **Validates: Requirements 1.3**
        """
        resource = self._get_test_resource()
        
        # Execute search
        results = await resource.search(query)
        
        # Property: All results should be relevant to the query
        query_lower = query.lower()
        
        for result in results:
            title_lower = result["title"].lower()
            excerpt_lower = result["excerpt"].lower()
            
            # Property: Result should contain query terms or related concepts
            is_relevant = (
                query_lower in title_lower or
                query_lower in excerpt_lower or
                any(word in title_lower or word in excerpt_lower 
                    for word in query_lower.split()) or
                self._is_conceptually_related(query_lower, title_lower, excerpt_lower) or
                self._contains_relevant_substrings(query_lower, title_lower, excerpt_lower)
            )
            
            assert is_relevant, f"Result '{result['title']}' not relevant to query '{query}'"
        
        # Property: Results should be sorted by relevance (high before medium)
        high_relevance_indices = [i for i, r in enumerate(results) if r["relevance"] == "high"]
        medium_relevance_indices = [i for i, r in enumerate(results) if r["relevance"] == "medium"]
        
        if high_relevance_indices and medium_relevance_indices:
            # All high relevance results should come before medium relevance
            assert max(high_relevance_indices) < min(medium_relevance_indices)
    
    def _is_conceptually_related(self, query: str, title: str, excerpt: str) -> bool:
        """Check if content is conceptually related to query."""
        # Define concept relationships
        concept_map = {
            "items": ["configuration", "state", "command", "switch", "dimmer"],
            "things": ["binding", "device", "discovery", "channel"],
            "rules": ["automation", "trigger", "action", "script"],
            "bindings": ["addon", "integration", "protocol", "device"],
            "installation": ["setup", "install", "deploy", "start"],
            "configuration": ["config", "setup", "parameter", "setting"],
            "troubleshoot": ["error", "problem", "debug", "log", "issue"],
            "error": ["troubleshoot", "problem", "debug", "log", "issue"]
        }
        
        related_terms = concept_map.get(query, [])
        content = title + " " + excerpt
        
        return any(term in content for term in related_terms)
    
    def _contains_relevant_substrings(self, query: str, title: str, excerpt: str) -> bool:
        """Check if query contains relevant substrings that match content."""
        content = (title + " " + excerpt).lower()
        
        # Define key terms that should match if found as substrings in the query
        key_terms = ["error", "troubleshoot", "debug", "problem", "issue", "config", "setup", "install"]
        
        # Check if any key term is a substring of the query and also appears in content
        for term in key_terms:
            if term in query and term in content:
                return True
        
        return False
    
    @given(uri=documentation_uri_strategy())
    @settings(max_examples=50, deadline=10000)
    async def test_property_resource_uri_accessibility(self, uri):
        """**Feature: openhab-mcp-server, Property 13: Resource URI accessibility**
        
        For any valid resource URI, the system should support efficient data 
        retrieval through URI-based querying.
        
        **Validates: Requirements 5.2**
        """
        resource = self._get_test_resource()
        
        # Mock successful documentation retrieval
        mock_content = f"""
        <!DOCTYPE html>
        <html>
        <head><title>openHAB Documentation</title></head>
        <body>
            <h1>openHAB Documentation</h1>
            <p>This is documentation content for {uri}</p>
            <h2>Setup Guide</h2>
            <p>Follow these steps to configure...</p>
            <h2>Configuration Examples</h2>
            <pre>Item MyItem "My Item" &lt;switch&gt;</pre>
            <h2>Troubleshooting</h2>
            <p>If you encounter issues, check the logs...</p>
        </body>
        </html>
        """
        
        with aioresponses() as mock:
            # Mock the documentation URL
            expected_url = f"https://www.openhab.org/docs/{uri}"
            mock.get(expected_url, body=mock_content, status=200)
            
            # Property: URI should be accessible and return content
            content = await resource.get_content(uri)
            
            # Property: Content should be returned as string
            assert isinstance(content, str)
            assert len(content) > 0
            
            # Property: Content should contain expected documentation elements
            assert "openHAB" in content
            
            # Property: For documentation URIs, should contain structured content
            if any(section in uri for section in ["configuration", "tutorial", "installation"]):
                # Should contain typical documentation structure
                assert any(keyword in content.lower() for keyword in ["setup", "config", "example", "step"])


class TestSystemStateResourceProperties:
    """Property-based tests for SystemStateResource."""
    
    def _get_test_resource(self):
        """Get test system state resource."""
        config = Config(
            openhab_url="http://test-openhab:8080",
            openhab_token="test-token",
            timeout=30,
            log_level="INFO"
        )
        client = OpenHABClient(config)
        return SystemStateResource(client)
    
    @given(
        system_info=system_info_strategy(),
        bindings=st.lists(binding_data_strategy(), min_size=0, max_size=10),
        things=st.lists(thing_data_strategy(), min_size=0, max_size=20),
        items=st.lists(st.dictionaries(
            st.sampled_from(["name", "state", "type"]),
            st.text(min_size=1, max_size=50),
            min_size=3, max_size=3
        ), min_size=0, max_size=15),
        rules=st.lists(st.dictionaries(
            st.sampled_from(["uid", "name", "status"]),
            st.one_of(st.text(min_size=1, max_size=50), st.dictionaries(
                st.text(min_size=1, max_size=20),
                st.text(min_size=1, max_size=20),
                max_size=2
            )),
            min_size=3, max_size=3
        ), min_size=0, max_size=10)
    )
    @settings(max_examples=50, deadline=10000)
    async def test_property_system_state_completeness(self, system_info, bindings, things, items, rules):
        """Test that system state includes all required information."""
        resource = self._get_test_resource()
        
        with aioresponses() as mock:
            # Mock all required API endpoints
            mock.get("http://test-openhab:8080/rest/systeminfo", payload=system_info)
            mock.get("http://test-openhab:8080/rest/bindings", payload=bindings)
            mock.get("http://test-openhab:8080/rest/things", payload=things)
            mock.get("http://test-openhab:8080/rest/items", payload=items)
            mock.get("http://test-openhab:8080/rest/rules", payload=rules)
            
            # Get system info
            result = await resource.get_system_info()
            
            # Property: Result should contain system and health information
            assert "system" in result
            assert "health" in result
            assert "status" in result
            
            # Property: System info should match API response
            assert result["system"] == system_info
            
            # Property: Health metrics should be calculated correctly
            health = result["health"]
            assert "things_online" in health
            assert "things_total" in health
            assert "things_online_percentage" in health
            assert "items_count" in health
            assert "rules_enabled" in health
            assert "rules_total" in health
            assert "bindings_installed" in health
            
            # Property: Counts should match input data
            assert health["things_total"] == len(things)
            assert health["items_count"] == len(items)
            assert health["rules_total"] == len(rules)
            assert health["bindings_installed"] == len(bindings)
            
            # Property: Online percentage should be calculated correctly
            online_things = sum(1 for thing in things if thing.get('statusInfo', {}).get('status') == 'ONLINE')
            expected_percentage = (online_things / len(things) * 100) if len(things) > 0 else 0
            assert abs(health["things_online_percentage"] - expected_percentage) < 0.01
            
            # Property: Status should reflect system health
            if len(things) == 0:
                assert result["status"] in ["healthy", "degraded"]
            else:
                online_ratio = online_things / len(things)
                expected_status = "healthy" if online_ratio > 0.8 else "degraded"
                assert result["status"] == expected_status


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
