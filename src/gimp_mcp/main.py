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
from .logging_config import (
    setup_logging, get_logger, log_server_start, log_server_stop,
    log_tool_registration, log_gimp_detection, log_config_load,
    log_operation_start, log_operation_success, log_operation_error
)

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

# Configure structured logging
logger = setup_logging(component="main")

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

    def _validate_configuration(self) -> bool:
        """
        Validate server configuration for critical settings.

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            # Check required configuration attributes
            required_attrs = ['allowed_directories', 'max_file_size_mb']
            for attr in required_attrs:
                if not hasattr(self.config, attr):
                    logger.error(f"Missing required configuration attribute: {attr}")
                    return False

            # Validate allowed directories exist and are accessible
            allowed_dirs = getattr(self.config, 'allowed_directories', [])
            if not allowed_dirs:
                logger.warning("No allowed directories configured - this may limit functionality")
            else:
                for dir_path in allowed_dirs:
                    path = Path(dir_path)
                    if not path.exists():
                        logger.warning(f"Allowed directory does not exist: {path}")
                    elif not path.is_dir():
                        logger.error(f"Allowed path is not a directory: {path}")
                        return False

            # Validate max file size is reasonable
            max_size = getattr(self.config, 'max_file_size_mb', 100)
            if not isinstance(max_size, (int, float)) or max_size <= 0:
                logger.error(f"Invalid max_file_size_mb: {max_size}")
                return False

            logger.info("Configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False

    def _safe_register_tool_category(self, category_name: str, tool_class, init_args: list) -> bool:
        """
        Safely register a tool category with comprehensive error handling.

        Args:
            category_name: Name of the tool category
            tool_class: Tool class to instantiate
            init_args: Arguments for tool initialization

        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            logger.info(f"Initializing {category_name} tools...")

            # Create tool instance with error handling
            tool_instance = tool_class(*init_args)
            logger.info(f"Created {category_name} tool instance")

            # Register tools with the MCP app
            tool_instance.register_tools(self.mcp)
            logger.info(f"Registered {category_name} tools successfully")

            # Store reference for status tracking
            self.tools[category_name] = tool_instance

            return True

        except Exception as e:
            logger.error(f"Failed to register {category_name} tools: {e}", exc_info=True)
            # Don't crash - continue with other categories
            return False
    
    async def initialize(self) -> bool:
        """
        Initialize the GIMP MCP Server with comprehensive error handling and recovery.

        This method sets up all tool categories with robust error handling to ensure
        the server can continue operating even if some components fail to initialize.

        Returns:
            bool: True if initialization successful, False if critical failure
        """
        try:
            logger.info("Starting GIMP MCP Server initialization...")

            # Validate configuration first
            if not self._validate_configuration():
                logger.error("Configuration validation failed - aborting initialization")
                return False
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
                HelpTools, StatusTools, FileOperationTools, TransformTools, ColorAdjustmentTools,
                LayerManagementTools, ImageAnalysisTools, FilterTools, BatchProcessingTools,
                PerformanceTools
            )
            
            # Define tool categories with their constructors
            tool_categories = [
                ("help", HelpTools, [self.cli_wrapper, self.config, {}]),
                ("status", StatusTools, [self.cli_wrapper, self.config]),
                ("file", FileOperationTools, [self.cli_wrapper, self.config]),
                ("transform", TransformTools, [self.cli_wrapper, self.config]),
                ("color", ColorAdjustmentTools, [self.cli_wrapper, self.config]),
                ("layer", LayerManagementTools, [self.cli_wrapper, self.config]),
                ("image", ImageAnalysisTools, [self.cli_wrapper, self.config]),
                ("filter", FilterTools, [self.cli_wrapper, self.config]),
                ("batch", BatchProcessingTools, [self.cli_wrapper, self.config]),
                ("performance", PerformanceTools, [self.cli_wrapper, self.config])
            ]
            
            # Register tool categories with safe error handling
            registration_results = {}
            for category_name, tool_class, init_args in tool_categories:
                success = self._safe_register_tool_category(category_name, tool_class, init_args)
                registration_results[category_name] = success

            # Log registration summary
            successful_count = sum(registration_results.values())
            total_count = len(registration_results)
            logger.info(f"Tool registration complete: {successful_count}/{total_count} categories registered")

            if successful_count == 0:
                logger.error("No tool categories could be registered - server will not function")
                return False
            elif successful_count < total_count:
                logger.warning(f"Some tool categories failed to register: {', '.join([cat for cat, success in registration_results.items() if not success])}")
                # Continue anyway if at least one category registered
            
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
