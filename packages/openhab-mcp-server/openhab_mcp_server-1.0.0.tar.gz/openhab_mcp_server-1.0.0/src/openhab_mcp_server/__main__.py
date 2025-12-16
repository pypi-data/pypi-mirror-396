"""
Entry point for running the openHAB MCP server as a module.

This allows the server to be run with:
    python -m openhab_mcp_server
    python -m src.openhab_mcp_server
"""

from openhab_mcp_server.cli import main

if __name__ == "__main__":
    main()