"""
Secure API context for script execution.

This module provides a secure context class that gives scripts authenticated
access to openHAB APIs while maintaining security constraints and proper
isolation from the host system.
"""

import logging
from typing import Any, Dict, List, Optional

from openhab_mcp_server.utils.openhab_client import OpenHABClient, OpenHABError
from openhab_mcp_server.utils.config import Config
from openhab_mcp_server.models import ItemState, ThingStatus


logger = logging.getLogger(__name__)


class ScriptContext:
    """Secure context for script execution with openHAB API access."""
    
    def __init__(self, openhab_client: OpenHABClient, config: Config):
        """Initialize script context.
        
        Args:
            openhab_client: Authenticated openHAB client
            config: Configuration object
        """
        self.openhab_client = openhab_client
        self.config = config
        self._log_entries: List[str] = []
    
    def get_item_state(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Get state of an openHAB item.
        
        Args:
            item_name: Name of the item
            
        Returns:
            Item state information or None if not found
        """
        try:
            # Use synchronous wrapper for async client
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.openhab_client.get_item_state(item_name)
                )
                return result
            finally:
                loop.close()
        except Exception as e:
            self.log(f"Error getting item state for {item_name}: {e}")
            return None
    
    def send_item_command(self, item_name: str, command: str) -> bool:
        """Send command to an openHAB item.
        
        Args:
            item_name: Name of the item
            command: Command to send
            
        Returns:
            True if command was sent successfully, False otherwise
        """
        try:
            # Use synchronous wrapper for async client
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.openhab_client.send_item_command(item_name, command)
                )
                return result
            finally:
                loop.close()
        except Exception as e:
            self.log(f"Error sending command to {item_name}: {e}")
            return False
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all openHAB items.
        
        Returns:
            List of all items
        """
        try:
            # Use synchronous wrapper for async client
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.openhab_client.get_items()
                )
                return result
            finally:
                loop.close()
        except Exception as e:
            self.log(f"Error getting all items: {e}")
            return []
    
    def get_thing_status(self, thing_uid: str) -> Optional[Dict[str, Any]]:
        """Get status of an openHAB thing.
        
        Args:
            thing_uid: UID of the thing
            
        Returns:
            Thing status information or None if not found
        """
        try:
            # Use synchronous wrapper for async client
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.openhab_client.get_thing_status(thing_uid)
                )
                return result
            finally:
                loop.close()
        except Exception as e:
            self.log(f"Error getting thing status for {thing_uid}: {e}")
            return None
    
    def get_all_things(self) -> List[Dict[str, Any]]:
        """Get all openHAB things.
        
        Returns:
            List of all things
        """
        try:
            # Use synchronous wrapper for async client
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.openhab_client.get_things()
                )
                return result
            finally:
                loop.close()
        except Exception as e:
            self.log(f"Error getting all things: {e}")
            return []
    
    def log(self, message: str) -> None:
        """Log a message from the script.
        
        Args:
            message: Message to log
        """
        log_entry = f"[SCRIPT] {message}"
        self._log_entries.append(log_entry)
        logger.info(log_entry)
    
    def get_logs(self) -> List[str]:
        """Get all log entries from script execution.
        
        Returns:
            List of log entries
        """
        return self._log_entries.copy()
    
    def clear_logs(self) -> None:
        """Clear all log entries."""
        self._log_entries.clear()
    
    def get_system_info(self) -> Optional[Dict[str, Any]]:
        """Get openHAB system information.
        
        Returns:
            System information or None if not available
        """
        try:
            # Use synchronous wrapper for async client
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.openhab_client.get_system_info()
                )
                return result
            finally:
                loop.close()
        except Exception as e:
            self.log(f"Error getting system info: {e}")
            return None
    
    def create_context_dict(self) -> Dict[str, Any]:
        """Create context dictionary for script execution.
        
        Returns:
            Dictionary with context variables for scripts
        """
        return {
            'openhab': self,
            'get_item_state': self.get_item_state,
            'send_item_command': self.send_item_command,
            'get_all_items': self.get_all_items,
            'get_thing_status': self.get_thing_status,
            'get_all_things': self.get_all_things,
            'get_system_info': self.get_system_info,
            'log': self.log,
        }