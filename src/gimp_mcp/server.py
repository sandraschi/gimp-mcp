"""
GIMP MCP Server implementation.

This module provides the main FastMCP server class that registers and handles
all GIMP image processing tools via the Model Context Protocol.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from .cli_wrapper import GimpCliWrapper
from .config import GimpConfig
from .tools import (
    FileOperationTools,
    TransformTools, 
    ColorAdjustmentTools,
    FilterTools,
    BatchProcessingTools
)

logger = logging.getLogger(__name__)

class GimpMcpServer:
    """
    Main GIMP MCP Server class.
    
    Coordinates all GIMP operations and provides MCP tool registration.
    """
    
    def __init__(self, config: GimpConfig):
        """
        Initialize GIMP MCP Server.
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize GIMP CLI wrapper
        self.cli_wrapper = GimpCliWrapper(config)
        
        # Initialize tool categories
        self.file_tools = FileOperationTools(self.cli_wrapper, config)
        self.transform_tools = TransformTools(self.cli_wrapper, config)
        self.color_tools = ColorAdjustmentTools(self.cli_wrapper, config)
        self.filter_tools = FilterTools(self.cli_wrapper, config)
        self.batch_tools = BatchProcessingTools(self.cli_wrapper, config)
        
        self.logger.info("GIMP MCP Server initialized")
    
    def register_tools(self, app: FastMCP) -> None:
        """
        Register all GIMP tools with the FastMCP app.
        
        Args:
            app: FastMCP application instance
        """
        self.logger.info("Registering GIMP MCP tools...")
        
        # Register file operation tools
        self.file_tools.register_tools(app)
        
        # Register transform tools
        self.transform_tools.register_tools(app)
        
        # Register color adjustment tools
        self.color_tools.register_tools(app)
        
        # Register filter tools
        self.filter_tools.register_tools(app)
        
        # Register batch processing tools (if enabled)
        if self.config.enable_batch_operations:
            self.batch_tools.register_tools(app)
        
        self.logger.info("All GIMP MCP tools registered successfully")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform server health check.
        
        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            # Test GIMP CLI wrapper
            test_result = await self._test_gimp_connection()
            
            return {
                "status": "healthy" if test_result else "unhealthy",
                "gimp_executable": self.config.gimp_executable,
                "gimp_available": test_result,
                "temp_directory": self.config.temp_directory,
                "supported_formats": len(self.config.supported_formats),
                "max_concurrent_processes": self.config.max_concurrent_processes,
                "batch_operations_enabled": self.config.enable_batch_operations
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _test_gimp_connection(self) -> bool:
        """
        Test GIMP connection with a simple operation.
        
        Returns:
            bool: True if GIMP is responsive
        """
        try:
            # Simple Script-Fu test
            test_script = '(gimp-message "GIMP_MCP_TEST:OK")'
            output = await self.cli_wrapper.execute_script_fu(test_script, timeout=10)
            return "GIMP_MCP_TEST:OK" in output
            
        except Exception as e:
            self.logger.error(f"GIMP connection test failed: {e}")
            return False
