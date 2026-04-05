"""
GIMP Bridge Wrapper for real-time interaction with a running GIMP instance.
"""

import asyncio
import json
import logging
from typing import Dict, Optional

from .config import GimpConfig

logger = logging.getLogger(__name__)

class GimpBridgeError(Exception):
    """Base exception for GIMP Bridge operations."""
    pass

class GimpBridgeWrapper:
    """
    Client for the GIMP MCP Bridge plugin.
    
    Enables real-time command execution within a running GIMP 3.0 instance.
    """
    
    def __init__(self, config: GimpConfig):
        """
        Initialize GIMP Bridge wrapper.
        
        Args:
            config: GIMP configuration object
        """
        self.config = config
        self.host = config.bridge_host
        self.port = config.bridge_port
        
    async def is_alive(self) -> bool:
        """
        Check if the GIMP Bridge is reachable.
        
        Returns:
            bool: True if bridge is alive
        """
        if not self.config.enable_live_mode:
            return False
            
        try:
            # Short timeout for health check
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=1.0
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False
            
    async def execute_live_python(self, code: str, timeout: Optional[int] = None) -> Dict:
        """
        Execute Python code in a running GIMP instance via the bridge.
        
        Args:
            code: Python code snippet
            timeout: Operation timeout
            
        Returns:
            Dict: Result containing 'result' or 'error'
        """
        timeout = timeout or self.config.process_timeout
        
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=2.0 # Connection timeout
            )
            
            payload = json.dumps({"code": code}).encode('utf-8')
            writer.write(payload)
            await writer.drain()
            
            # Wait for response
            data = await asyncio.wait_for(reader.read(16384), timeout=timeout)
            writer.close()
            await writer.wait_closed()
            
            if not data:
                return {"error": "No response from GIMP bridge"}
                
            return json.loads(data.decode('utf-8'))
            
        except asyncio.TimeoutError:
            logger.error(f"GIMP Bridge operation timed out after {timeout}s")
            return {"error": f"Live operation timed out after {timeout} seconds"}
        except Exception as e:
            logger.error(f"GIMP Bridge communication failure: {e}")
            return {"error": str(e)}
