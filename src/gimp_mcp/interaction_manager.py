"""
GIMP Interaction Manager - Orchestrates between Live and Headless modes.
"""

import logging
from typing import Any, Dict, Optional

from .config import GimpConfig
from .cli_wrapper import GimpCliWrapper
from .bridge_wrapper import GimpBridgeWrapper

logger = logging.getLogger(__name__)

class GimpInteractionManager:
    """
    Unified manager for GIMP interactions.
    
    Automatically detects if GIMP is running with the MCP Bridge plugin
    and selects the optimal execution path (Live vs. Headless).
    """
    
    def __init__(self, config: GimpConfig, cli_wrapper: GimpCliWrapper):
        """
        Initialize Interaction Manager.
        
        Args:
            config: GIMP configuration object
            cli_wrapper: Existing CLI wrapper instance
        """
        self.config = config
        self.cli = cli_wrapper
        self.bridge = GimpBridgeWrapper(config)
        self._last_mode = "unknown"
        
    async def get_status(self) -> Dict[str, Any]:
        """
        Get current interaction status.
        
        Returns:
            Dict: Status information
        """
        is_live = await self.bridge.is_alive()
        mode = "live" if is_live else "headless"
        
        return {
            "mode": mode,
            "live_available": is_live,
            "headless_available": self.cli is not None,
            "bridge_host": self.config.bridge_host,
            "bridge_port": self.config.bridge_port
        }

    async def execute_python_fu(self, python_content: str, timeout: Optional[int] = None) -> str:
        """
        Unified Python-Fu execution with automatic mode switching.
        
        Args:
            python_content: Python code to execute
            timeout: Operation timeout
            
        Returns:
            str: GIMP output or error message
        """
        # Try Live Mode first if enabled
        if self.config.enable_live_mode:
            if await self.bridge.is_alive():
                logger.info("Executing via GIMP Live Bridge")
                result = await self.bridge.execute_live_python(python_content, timeout)
                
                if "error" not in result:
                    self._last_mode = "live"
                    return f"LIVE_SUCCESS|{result.get('result', '')}"
                else:
                    logger.warning(f"Live Bridge execution failed, falling back: {result['error']}")

        # Fallback to Headless Mode
        if self.cli and self.cli.is_available():
            logger.info("Executing via GIMP Headless CLI")
            self._last_mode = "headless"
            return await self.cli.execute_python_fu(python_content, timeout)
            
        return "ERROR: No GIMP execution method available (Headless CLI failed or not found)"

    async def execute_script_fu(self, script_content: str, timeout: Optional[int] = None) -> str:
        """
        Unified Script-Fu execution. 
        Note: Live Bridge currently prioritizes Python-Fu for GIMP 3.0.
        """
        # For now, Script-Fu always uses CLI as it's the most reliable for batch
        # We can expand Live Bridge to support Script-Fu in the future if needed
        if self.cli and self.cli.is_available():
            self._last_mode = "headless"
            return await self.cli.execute_script_fu(script_content, timeout)
            
        return "ERROR: No GIMP execution method available for Script-Fu"

    @property
    def last_mode(self) -> str:
        """Return the mode used in the last execution."""
        return self._last_mode
