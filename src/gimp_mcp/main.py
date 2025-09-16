"""
GIMP MCP Server - FastMCP 2.x Implementation

This module serves as the main entry point for the GIMP MCP server, providing
an interface between the MCP protocol and GIMP's functionality through a CLI wrapper.
"""

import argparse
import asyncio
import json
import logging
import os
import signal
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
        
        # Initialize FastMCP with the server name
        self.mcp = FastMCP("GIMP MCP Server")
        
        # Set up tool registration
        self.tools = {}  # Store tool instances for later reference
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        self.logger = logging.getLogger(__name__)
        self.cli_wrapper: Optional[GimpCliWrapper] = None
    
    async def initialize(self) -> bool:
        """Initialize the GIMP MCP Server."""
        try:
            # Initialize GIMP detector
            self.gimp_detector = GimpDetector()
            
            # Try to detect GIMP installation
            gimp_path = None
            try:
                gimp_path = self.gimp_detector.detect_gimp_installation()
            except Exception as e:
                logger.warning(f"Error detecting GIMP installation: {e}")
            
            if gimp_path:
                logger.info(f"Found GIMP at: {gimp_path}")
                self.config.gimp_executable = str(gimp_path)
                
                # Initialize CLI wrapper
                try:
                    self.cli_wrapper = GimpCliWrapper(self.config)
                    logger.info("Initialized GIMP CLI wrapper")
                except Exception as e:
                    logger.error(f"Failed to initialize GIMP CLI wrapper: {e}")
                    self.cli_wrapper = None
            else:
                logger.warning("GIMP not found. Running in limited functionality mode")
                self.cli_wrapper = None
            
            # Import all tool categories from the tools package
            from .tools import (
                HelpTools, FileOperationTools, TransformTools, ColorAdjustmentTools,
                LayerManagementTools, ImageAnalysisTools, FilterTools, BatchProcessingTools,
                PerformanceTools
            )
            
            # Define tool categories with their constructors
            tool_categories = [
                ("help", HelpTools, [self.cli_wrapper, self.config, {}]),
                ("file", FileOperationTools, [self.cli_wrapper, self.config]),
                ("transform", TransformTools, [self.cli_wrapper, self.config]),
                ("color", ColorAdjustmentTools, [self.cli_wrapper, self.config]),
                ("layer", LayerManagementTools, [self.cli_wrapper, self.config]),
                ("image", ImageAnalysisTools, [self.cli_wrapper, self.config]),
                ("filter", FilterTools, [self.cli_wrapper, self.config]),
                ("batch", BatchProcessingTools, [self.cli_wrapper, self.config]),
                ("performance", PerformanceTools, [self.cli_wrapper, self.config])
            ]
            
            # Register tool categories
            for category_name, tool_class, init_args in tool_categories:
                try:
                    logger.info(f"Initializing {category_name} tools...")
                    tool_instance = tool_class(*init_args)
                    self.tools[category_name] = tool_instance
                    
                    # Register the tool instance with FastMCP
                    if hasattr(tool_instance, 'register_tools'):
                        tool_instance.register_tools(self.mcp)
                        logger.info(f"Registered tools from {category_name} category")
                    else:
                        logger.warning(f"Tool category {category_name} has no register_tools method")
                        
                except Exception as e:
                    logger.error(f"Failed to register {category_name} tools: {e}", exc_info=True)
            
            # Verify tool registration
            try:
                # Note: FastMCP 2.11.3 doesn't have a direct list_tools method
                # The tools are registered and will be available through the MCP protocol
                logger.info("Tool registration completed successfully")
                total_tools = len(self.tools)
                logger.info(f"Initialized {total_tools} tool categories")
                
            except Exception as e:
                logger.warning(f"Could not verify tool registration: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Critical error during initialization: {e}", exc_info=True)
            return False
    
    def run_http(self, host: str = '0.0.0.0', port: int = 8000) -> None:
        """Run the server in HTTP mode.
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        # Check if we have tool categories registered
        if not self.tools:
            logger.warning("No tool categories were registered. Running in limited functionality mode.")
        else:
            tool_count = len(self.tools)
            logger.info(f"Starting HTTP server with {tool_count} tool categories registered")
            
        # Start the server
        logger.info(f"Starting HTTP server on {host}:{port}")
        self.mcp.run(transport="http", host=host, port=port)

    def run_stdio(self) -> None:
        """Run the server in stdio mode."""
        # Check if we have tool categories registered
        if not self.tools:
            logger.warning("No tool categories were registered. Running in limited functionality mode.")
        else:
            tool_count = len(self.tools)
            logger.info(f"Starting stdio server with {tool_count} tool categories registered")
            
        # Start the server
        logger.info("Starting stdio server")
        self.mcp.run(transport="stdio")

def main():
    # Configure basic logging first to capture early messages
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True,
        handlers=[
            logging.StreamHandler(sys.stderr)  # Ensure logs go to stderr
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting GIMP MCP Server...")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='GIMP MCP Server')
    parser.add_argument(
        "--config", 
        type=str, 
        help='Path to config file',
        default=None
    )
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
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    logger.debug(f"Command line arguments: {args}")
    
    # Configure logging
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Force reconfiguration of root logger
    )
    
    logger.debug(f"Logging configured at level: {args.log_level}")
    logger.info(f"Starting GIMP MCP Server with log level: {args.log_level}")
    
    # Initialize server
    logger.debug("Initializing server...")
    try:
        server = GimpMCPServer(config_path=Path(args.config) if args.config else None)
        logger.debug("Server instance created")
    except Exception as e:
        logger.error(f"Error creating server: {e}")
        raise
    
    # Initialize server components
    logger.debug("Initializing server components...")
    try:
        init_result = asyncio.run(server.initialize())
        logger.debug(f"Server initialization result: {init_result}")
        if not init_result:
            logger.error("Failed to initialize GIMP MCP Server")
            return 1
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        logger.exception("Failed to initialize GIMP MCP Server")
        return 1
        
    try:
        if args.mode == "http":
            logger.info(f"Starting HTTP server on {args.host}:{args.port}")
            server.run_http(host=args.host, port=args.port)
        else:
            logger.info("Starting stdio server")
            server.run_stdio()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception("Server error:")
        logger.error(f"Server error: {e}")
        return 1
        
    logger.info("Server shutdown complete")
    return 0

if __name__ == "__main__":
    main()
