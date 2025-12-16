"""
Command-line interface for the openHAB MCP Server.

This module provides a command-line entry point for running the openHAB MCP server
with configurable options for host, port, and configuration file paths.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from openhab_mcp_server.server import OpenHABMCPServer
from openhab_mcp_server.utils.config import Config, get_config
from openhab_mcp_server.utils.logging import configure_logging


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="openhab-mcp-server",
        description="openHAB Model Context Protocol Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  OPENHAB_URL       openHAB server URL (default: http://localhost:8080)
  OPENHAB_TOKEN     openHAB API token for authentication
  OPENHAB_TIMEOUT   Request timeout in seconds (default: 30)
  LOG_LEVEL         Logging level (default: INFO)

Examples:
  openhab-mcp-server
  openhab-mcp-server --log-level DEBUG
  openhab-mcp-server --openhab-url http://192.168.1.100:8080
        """
    )
    
    # Server configuration options
    parser.add_argument(
        "--openhab-url",
        type=str,
        help="openHAB server URL (overrides OPENHAB_URL environment variable)"
    )
    
    parser.add_argument(
        "--openhab-token",
        type=str,
        help="openHAB API token (overrides OPENHAB_TOKEN environment variable)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        help="Request timeout in seconds (overrides OPENHAB_TIMEOUT environment variable)"
    )
    
    # Logging configuration
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (overrides LOG_LEVEL environment variable)"
    )
    
    parser.add_argument(
        "--log-format",
        choices=["text", "json"],
        default="text",
        help="Log output format (default: text)"
    )
    
    # Configuration file
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file (JSON format)"
    )
    
    # Development and debugging options
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration and exit"
    )
    
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test connection to openHAB and exit"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    return parser


def load_config_from_args(args: argparse.Namespace) -> Config:
    """Load configuration from command line arguments and environment.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Configuration object
        
    Raises:
        SystemExit: If configuration is invalid
    """
    try:
        # Start with environment-based config
        config = get_config()
        
        # Override with command line arguments if provided
        if args.openhab_url:
            config.openhab_url = args.openhab_url
        
        if args.openhab_token:
            config.openhab_token = args.openhab_token
        
        if args.timeout:
            config.timeout = args.timeout
        
        if args.log_level:
            config.log_level = args.log_level
        
        # Load from config file if provided
        if args.config:
            if not args.config.exists():
                print(f"Error: Configuration file not found: {args.config}", file=sys.stderr)
                sys.exit(1)
            
            try:
                import json
                with open(args.config, 'r') as f:
                    config_data = json.load(f)
                
                # Update config with file values (command line args take precedence)
                for key, value in config_data.items():
                    if hasattr(config, key) and not getattr(args, key.replace('_', '-'), None):
                        setattr(config, key, value)
                        
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading configuration file: {e}", file=sys.stderr)
                sys.exit(1)
        
        return config
        
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)


def validate_config(config: Config) -> bool:
    """Validate the configuration.
    
    Args:
        config: Configuration to validate
        
    Returns:
        True if configuration is valid, False otherwise
    """
    errors = []
    
    # Check required fields
    if not config.openhab_url:
        errors.append("openHAB URL is required (set OPENHAB_URL or use --openhab-url)")
    elif not config.openhab_url.startswith(('http://', 'https://')):
        errors.append("openHAB URL must start with http:// or https://")
    
    if not config.openhab_token:
        errors.append("openHAB API token is required (set OPENHAB_TOKEN or use --openhab-token)")
    
    if config.timeout <= 0:
        errors.append("Timeout must be greater than 0")
    
    # Print validation results
    if errors:
        print("Configuration validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return False
    else:
        print("Configuration validation passed")
        print(f"  openHAB URL: {config.openhab_url}")
        print(f"  Timeout: {config.timeout}s")
        print(f"  Log Level: {config.log_level}")
        print(f"  Has API Token: {'Yes' if config.openhab_token else 'No'}")
        return True


async def test_connection(config: Config) -> bool:
    """Test connection to openHAB server.
    
    Args:
        config: Configuration to use for connection test
        
    Returns:
        True if connection successful, False otherwise
    """
    try:
        print(f"Testing connection to {config.openhab_url}...")
        
        server = OpenHABMCPServer(config)
        await server.start()
        
        print("✓ Connection test successful")
        print("✓ openHAB server is reachable")
        print("✓ Authentication successful")
        
        await server.shutdown()
        return True
        
    except Exception as e:
        print(f"✗ Connection test failed: {e}", file=sys.stderr)
        return False


async def run_server(config: Config, log_format: str = "text") -> None:
    """Run the MCP server.
    
    Args:
        config: Server configuration
        log_format: Log output format ("text" or "json")
    """
    # Configure logging
    configure_logging(
        level=config.log_level,
        format_json=(log_format == "json"),
        include_structured_data=True
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting openHAB MCP Server...")
        logger.info(f"openHAB URL: {config.openhab_url}")
        logger.info(f"Timeout: {config.timeout}s")
        logger.info(f"Log Level: {config.log_level}")
        
        # Create and start server
        server = OpenHABMCPServer(config)
        await server.start()
        
        logger.info("openHAB MCP Server started successfully")
        logger.info("Server is ready to accept MCP connections")
        
        # Keep the server running
        try:
            # This will run indefinitely until interrupted
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        if 'server' in locals():
            logger.info("Shutting down server...")
            await server.shutdown()
            logger.info("Server shutdown complete")


def main() -> None:
    """Main entry point for the CLI.
    
    This function is used as the console script entry point when the package
    is installed via pip.
    """
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Load configuration
    config = load_config_from_args(args)
    
    # Handle special modes
    if args.validate_config:
        success = validate_config(config)
        sys.exit(0 if success else 1)
    
    if args.test_connection:
        success = asyncio.run(test_connection(config))
        sys.exit(0 if success else 1)
    
    # Validate configuration before starting server
    if not validate_config(config):
        sys.exit(1)
    
    # Run the server
    try:
        asyncio.run(run_server(config, args.log_format))
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()