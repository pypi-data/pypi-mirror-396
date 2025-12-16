"""openHAB MCP Server package.

A Model Context Protocol server that bridges AI assistants with openHAB home automation systems.
Provides structured access to openHAB's documentation, APIs, and operational capabilities.
"""

from openhab_mcp_server.models import (
    ItemState,
    ThingStatus,
    RuleDefinition,
    SystemInfo,
    MCPError,
    ValidationResult,
)

__version__ = "1.0.0"
__author__ = "openHAB MCP Server Contributors"
__email__ = "info@example.com"
__description__ = "Model Context Protocol server for openHAB home automation"
__license__ = "MIT"
__url__ = "https://github.com/openhab/openhab-mcp-server"

__all__ = [
    "ItemState",
    "ThingStatus", 
    "RuleDefinition",
    "SystemInfo",
    "MCPError",
    "ValidationResult",
]