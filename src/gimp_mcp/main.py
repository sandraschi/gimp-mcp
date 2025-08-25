"""
GIMP MCP Server - FastMCP 2.x Implementation

This module serves as the main entry point for the GIMP MCP server, providing
an interface between the MCP protocol and GIMP's functionality through a CLI wrapper.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from fastmcp import FastMCP
from fastmcp.transports import stdio_transport, http_transport

from .config import GimpConfig, load_config
from .gimp_detector import GimpDetector  
from .cli_wrapper import GimpCliWrapper

# Import tool registration functions
from .tools.file_operations import register_file_tools
from .tools.transforms import register_transform_tools
from .tools.color_adjustments import register_color_tools
from .tools.filters import register_filter_tools
from .tools.batch_processing import register_batch_tools
from .tools.help_tools import register_help_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class GimpMCPServer:
    """Main server class for GIMP MCP integration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the GIMP MCP server.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config = load_config(config_path) if config_path else GimpConfig()
        self.mcp = FastMCP(
            name="GIMP MCP Server",
            description="MCP server for GIMP image manipulation",
            version="2.0.0"
        )
        self.cli_wrapper: Optional[GimpCliWrapper] = None
    
    async def initialize(self) -> bool:
        """Initialize the server and its components.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Detect GIMP installation
            detector = GimpDetector()
            gimp_path = detector.detect_gimp_installation()
            
            if not gimp_path:
                logger.error("GIMP installation not found")
                return False
                
            self.config.gimp_executable = gimp_path
            logger.info(f"Using GIMP at: {gimp_path}")
            
            # Initialize CLI wrapper
            self.cli_wrapper = GimpCliWrapper(self.config)
            
            # Register all tool categories
            self._register_tools()
            
            logger.info("GIMP MCP Server initialized successfully")
            return True
            
        except Exception as e:
            logger.exception("Failed to initialize GIMP MCP Server")
            return False
    
    def _register_tools(self) -> None:
        """Register all available tools with the MCP server."""
        if not self.cli_wrapper:
            raise RuntimeError("CLI wrapper not initialized")
        
        # Register tool categories
        register_file_tools(self.mcp, self.cli_wrapper, self.config)
        register_transform_tools(self.mcp, self.cli_wrapper, self.config)
        register_color_tools(self.mcp, self.cli_wrapper, self.config)
        register_filter_tools(self.mcp, self.cli_wrapper, self.config)
        register_batch_tools(self.mcp, self.cli_wrapper, self.config)
        register_help_tools(self.mcp, self.cli_wrapper, self.config)
        
        logger.info("All tools registered successfully")
    
    async def run_stdio(self) -> None:
        """Run the server in stdio mode."""
        if not await self.initialize():
            sys.exit(1)
            
        logger.info("Starting GIMP MCP Server in stdio mode")
        await self.mcp.run(stdio_transport())
    
    async def run_http(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the server in HTTP mode.
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        if not await self.initialize():
            sys.exit(1)
            
        logger.info(f"Starting GIMP MCP Server in HTTP mode on {host}:{port}")
        await self.mcp.run(http_transport(host=host, port=port))

async def main():
    """Main entry point for the GIMP MCP Server."""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="GIMP MCP Server")
    parser.add_argument(
        "--mode", 
        choices=["stdio", "http"], 
        default="stdio",
        help="Server mode (default: stdio)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="Host to bind to (HTTP mode only, default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to listen on (HTTP mode only, default: 8000)"
    )
    parser.add_argument(
        "--config", 
        type=Path,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Create and run server
    try:
        server = GimpMCPServer(config_path=args.config)
        
        if args.mode == "http":
            await server.run_http(host=args.host, port=args.port)
        else:  # stdio
            await server.run_stdio()
            
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
