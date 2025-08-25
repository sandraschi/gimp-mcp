"""
Main entry point for GIMP MCP Server.

This module provides the main FastMCP server implementation with stdio transport
for MCP client connections, following FastMCP 2.10 standards.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP
from fastmcp.transports.stdio import stdio_transport

from .config import GimpConfig
from .gimp_detector import GimpDetector
from .server import GimpMcpServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_server() -> FastMCP:
    """
    Create and configure the GIMP MCP server.
    
    Returns:
        FastMCP: Configured server instance
        
    Raises:
        RuntimeError: If GIMP installation cannot be found or configured
    """
    try:
        # Load configuration
        config = GimpConfig.load_default()
        logger.info(f"Loaded configuration: {config.temp_directory}")
        
        # Detect GIMP installation
        detector = GimpDetector()
        gimp_path = detector.detect_gimp_installation()
        
        if not gimp_path:
            raise RuntimeError(
                "GIMP installation not found. Please install GIMP 3.0+ "
                "or configure the path manually in config.yaml"
            )
            
        config.gimp_executable = gimp_path
        logger.info(f"Detected GIMP at: {gimp_path}")
        
        # Validate GIMP version
        version = detector.validate_gimp_version(gimp_path)
        logger.info(f"GIMP version: {version}")
        
        # Create server
        server = GimpMcpServer(config)
        app = FastMCP("GIMP MCP Server")
        
        # Register tools
        server.register_tools(app)
        
        logger.info("GIMP MCP Server initialized successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to initialize GIMP MCP Server: {e}")
        raise

async def run_stdio_server() -> None:
    """
    Run the GIMP MCP server using stdio transport for MCP client connections.
    This is the primary mode for Claude Desktop and other MCP clients.
    """
    try:
        app = create_server()
        logger.info("Starting GIMP MCP Server with stdio transport...")
        
        # Run with stdio transport
        await app.run(stdio_transport())
        
    except Exception as e:
        logger.error(f"Stdio server failed: {e}")
        sys.exit(1)

def main() -> None:
    """
    Main CLI entry point supporting both stdio and HTTP modes.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="GIMP MCP Server - Professional Image Editing via MCP"
    )
    parser.add_argument(
        "--config", 
        type=Path,
        help="Path to configuration file (default: config.yaml)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to for HTTP mode (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to for HTTP mode (default: 8000)"
    )
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Run in stdio mode for MCP client connections (default)"
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run in HTTP mode for web-based access"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate GIMP installation and exit"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        if args.validate_only:
            # Validation mode
            detector = GimpDetector()
            gimp_path = detector.detect_gimp_installation()
            
            if gimp_path:
                version = detector.validate_gimp_version(gimp_path)
                print(f"✅ GIMP found at: {gimp_path}")
                print(f"✅ Version: {version}")
                print("✅ GIMP MCP Server is ready to use")
                sys.exit(0)
            else:
                print("❌ GIMP installation not found")
                print("Please install GIMP 3.0+ or configure the path manually")
                sys.exit(1)
        
        # Determine run mode
        if args.http:
            # HTTP mode
            app = create_server()
            logger.info("Starting GIMP MCP Server in HTTP mode...")
            
            import uvicorn
            uvicorn.run(
                app,
                host=args.host,
                port=args.port,
                log_level=args.log_level.lower()
            )
        else:
            # Stdio mode (default) - for MCP client connections
            asyncio.run(run_stdio_server())
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
