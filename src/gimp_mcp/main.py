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

from .config import GimpConfig, load_config
from .gimp_detector import GimpDetector  
from .cli_wrapper import GimpCliWrapper

# Import tool categories
from .tools import (
    FileOperationTools,
    TransformTools,
    ColorAdjustmentTools,
    FilterTools,
    BatchProcessingTools,
    HelpTools,
    LayerManagementTools,
    ImageAnalysisTools,
    PerformanceTools
)

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
        
        # Initialize FastMCP with explicit configuration
        self.mcp = FastMCP(
            name="GIMP MCP Server",
            version="2.0.0"
        )
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        self.logger = logging.getLogger(__name__)
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
        
        # Debug: Log FastMCP version and attributes
        import fastmcp
        logger.info(f"FastMCP version: {fastmcp.__version__}")
        logger.info(f"FastMCP attributes: {dir(fastmcp)}")
        logger.info(f"MCP instance type: {type(self.mcp)}")
        logger.info(f"MCP instance attributes: {dir(self.mcp)}")
        
        logger.info("Starting tool registration...")
        
        try:
            # Initialize and register tool categories
            tool_classes = [
                ("File Operations", FileOperationTools),
                ("Transforms", TransformTools),
                ("Color Adjustments", ColorAdjustmentTools),
                ("Filters", FilterTools),
                ("Batch Processing", BatchProcessingTools),
                ("Help", HelpTools),
                ("Layer Management", LayerManagementTools),
                ("Image Analysis", ImageAnalysisTools),
                ("Performance", PerformanceTools)
            ]
            
            registered_categories = 0
            
            for category_name, tool_class in tool_classes:
                try:
                    logger.info(f"Registering {category_name} tools...")
                    tool_instance = tool_class(self.cli_wrapper, self.config)
                    tool_instance.register_tools(self.mcp)
                    registered_categories += 1
                    logger.info(f"Successfully registered {category_name} tools")
                except Exception as e:
                    logger.error(f"Failed to register {category_name} tools: {e}", exc_info=True)
            
            if registered_categories == 0:
                logger.error("No tool categories were registered successfully")
            else:
                logger.info(f"Successfully registered {registered_categories} tool categories")
                
            # Debug: List all registered tools
            try:
                if hasattr(self.mcp, 'list_tools'):
                    tools = self.mcp.list_tools()
                    logger.info(f"Registered tools: {', '.join(tools) if tools else 'None'}")
            except Exception as e:
                logger.warning(f"Could not list registered tools: {e}")
                
        except Exception as e:
            logger.error(f"Error during tool registration: {e}", exc_info=True)
            raise
    
    def run_stdio(self) -> None:
        """Run the server in stdio mode."""
        self.mcp.run()
        
    def run_http(self, host: str = '0.0.0.0', port: int = 8000) -> None:
        """Run the server in HTTP mode.
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        self.mcp.run(transport="http", host=host, port=port)

def main():
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
        "--port", 
        type=int, 
        default=8000,
        help="Port for HTTP server (default: 8000)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Initialize server
    server = GimpMCPServer(config_path=args.config)
    
    # Initialize the server
    if not server.initialize():
        logger.error("Failed to initialize GIMP MCP Server")
        sys.exit(1)
    
    # Run the appropriate server mode
    try:
        if args.mode == "http":
            logger.info(f"Starting HTTP server on {args.host}:{args.port}")
            server.run_http(host=args.host, port=args.port)
        else:
            logger.info("Starting in stdio mode")
            server.run_stdio()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
