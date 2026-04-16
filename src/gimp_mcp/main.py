"""
GIMP MCP Server - FastMCP 3.1.1+ Portmanteau Architecture

This module serves as the main entry point for the GIMP MCP server, providing
an interface between the MCP protocol and GIMP's functionality.

PORTMANTEAU ARCHITECTURE (v3.1.1):
Instead of 50+ individual tools, GIMP MCP consolidates related operations into 8
master portmanteau tools. Each tool handles a specific domain with multiple operations.

Tools:
- gimp_file: File operations (load, save, convert, info)
- gimp_transform: Geometric transforms (resize, crop, rotate, flip)
- gimp_color: Color adjustments (brightness, levels, curves, HSL)
- gimp_filter: Filters (blur, sharpen, noise, artistic)
- gimp_layer: Layer management (create, merge, flatten)
- gimp_analysis: Image analysis (quality, statistics, compare)
- gimp_batch: Batch processing (resize, convert, watermark)
- gimp_system: System operations (status, help, cache)
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

# Import agentic workflow tools
from .agentic import register_agentic_tools
from .cli_wrapper import GimpCliWrapper
from .config import GimpConfig, load_config
from .gimp_detector import GimpDetector
from .interaction_manager import GimpInteractionManager
from .logging_config import (
    setup_logging,
)

# Import portmanteau tools (v3.0.0 architecture)
from .tools import (
    PORTMANTEAU_TOOLS,
    gimp_analysis,
    gimp_batch,
    gimp_color,
    gimp_file,
    gimp_filter,
    gimp_layer,
    gimp_system,
    gimp_transform,
)
from .transport import run_server, run_server_async

# Legacy imports for backwards compatibility (reserved for future use if needed)
# from .tools_legacy import ...

# Configure structured logging
logger = setup_logging(component="main")


class GimpMCPServer:
    """Main server class for GIMP MCP integration."""

    def __init__(self, config_path: Path | None = None):
        """Initialize the GIMP MCP server.

        Args:
            config_path: Optional path to configuration file
        """
        self.config = load_config(config_path) if config_path else GimpConfig()

        # Initialize FastMCP with the server name
        self.mcp = FastMCP(
            "GIMP MCP Fleet Server",
            instructions="""You are GIMP MCP Server, a comprehensive FastMCP 3.1.1 server for professional image editing using GIMP.

FASTMCP 3.1.1 FEATURES:
- Conversational tool returns for natural AI interaction
- Sampling capabilities for agentic workflows and complex image processing operations
- Portmanteau design preventing tool explosion while maintaining full functionality

CORE CAPABILITIES:
- **AI Image Generation**: Conversational image creation using advanced AI models with GIMP post-processing
- Professional Image Editing: Advanced photo manipulation, retouching, and creative effects
- File Operations: Load, save, convert between formats, batch processing
- Geometric Transforms: Resize, crop, rotate, flip, perspective correction
- Color Adjustments: Brightness/contrast, levels, curves, color balance, HSL adjustments
- Filters & Effects: Blur, sharpen, noise reduction, artistic filters, edge detection
- Layer Management: Create, duplicate, merge, reorder, and manipulate image layers
- Image Analysis: Quality assessment, statistics, histogram analysis, comparison tools
- Batch Processing: Automated workflows for multiple images with consistent effects
- Image Repository: Versioned asset management with intelligent search and metadata

CONVERSATIONAL FEATURES:
- Tools return natural language responses alongside structured data
- Sampling allows autonomous orchestration of complex editing workflows
- Agentic capabilities for intelligent image processing pipelines

RESPONSE FORMAT:
- All tools return dictionaries with 'success' boolean and 'message' for conversational responses
- Error responses include 'error' field with descriptive message
- Success responses include relevant data fields and natural language summaries

PORTMANTEAU DESIGN:
Tools are consolidated into logical groups to prevent tool explosion while maintaining full functionality.
Each portmanteau tool handles multiple related operations through an 'operation' parameter.
""",
        )

        # Set up tool registration
        self.tools = {}  # Store tool instances for later reference

        # Set up logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        self.logger = logging.getLogger(__name__)
        self.cli_wrapper: GimpCliWrapper | None = None
        self.interaction_manager: GimpInteractionManager | None = None

    def _validate_configuration(self) -> bool:
        """
        Validate server configuration for critical settings.

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            # Check required configuration attributes
            required_attrs = ["allowed_directories", "max_file_size_mb"]
            for attr in required_attrs:
                if not hasattr(self.config, attr):
                    logger.error(f"Missing required configuration attribute: {attr}")
                    return False

            # Validate allowed directories exist and are accessible
            allowed_dirs = getattr(self.config, "allowed_directories", [])
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
            max_size = getattr(self.config, "max_file_size_mb", 100)
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

        This method sets up all portmanteau tools (v3.0.0 architecture) with robust
        error handling to ensure the server can continue operating even if some
        components fail to initialize.

        Returns:
            bool: True if initialization successful, False if critical failure
        """
        try:
            logger.info("Starting GIMP MCP Server v3.0.0 (Portmanteau Architecture)...")

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
                    self.interaction_manager = GimpInteractionManager(self.config, self.cli_wrapper)
                    logger.info("Initialized GIMP interaction manager (Live + Headless)")
                except Exception as e:
                    logger.error(f"Failed to initialize GIMP interaction manager: {e}")
                    self.cli_wrapper = None
                    self.interaction_manager = None
            else:
                logger.warning("GIMP not found. Running in limited functionality mode")
                self.cli_wrapper = None
                self.interaction_manager = None

            # Register portmanteau tools (v3.0.0 architecture)
            logger.info("Registering portmanteau tools...")
            portmanteau_registered = self._register_portmanteau_tools()

            # Register custom FastAPI routes for the dashboard
            self._register_api_routes()

            if portmanteau_registered:
                logger.info(f"Successfully registered {len(PORTMANTEAU_TOOLS)} portmanteau tools")
                # Count total operations
                total_ops = sum(len(t["operations"]) for t in PORTMANTEAU_TOOLS)
                logger.info(f"Total operations available: {total_ops}")
            else:
                logger.warning("Portmanteau registration failed, falling back to legacy tools")
                # Fall back to legacy tool registration
                return await self._initialize_legacy_tools()

            return True

        except Exception as e:
            logger.error(f"Critical error during initialization: {e}", exc_info=True)
            return False

    def _register_portmanteau_tools(self) -> bool:
        """
        Register all portmanteau tools with FastMCP.

        Returns:
            bool: True if registration successful
        """
        try:
            # Register each portmanteau tool with the MCP instance
            # We wrap them to inject cli_wrapper and config

            @self.mcp.tool()
            async def gimp_file_tool(
                operation: str,
                input_path: str | None = None,
                output_path: str | None = None,
                format: str | None = None,
                quality: int = 95,
                compression: int = 6,
                progressive: bool = False,
            ) -> dict[str, Any]:
                """File operations: load, save, convert, info, validate, list_formats."""
                return await gimp_file(
                    operation=operation,
                    input_path=input_path,
                    output_path=output_path,
                    format=format,
                    quality=quality,
                    compression=compression,
                    progressive=progressive,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool()
            async def gimp_transform_tool(
                operation: str,
                input_path: str,
                output_path: str,
                width: int | None = None,
                height: int | None = None,
                maintain_aspect: bool = True,
                x: int = 0,
                y: int = 0,
                degrees: float = 0.0,
                direction: str = "horizontal",
                fill_color: str = "transparent",
            ) -> dict[str, Any]:
                """Transforms: resize, crop, rotate, flip, scale, perspective, autocrop."""
                return await gimp_transform(
                    operation=operation,
                    input_path=input_path,
                    output_path=output_path,
                    width=width,
                    height=height,
                    maintain_aspect=maintain_aspect,
                    x=x,
                    y=y,
                    degrees=degrees,
                    direction=direction,
                    fill_color=fill_color,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool()
            async def gimp_color_tool(
                operation: str,
                input_path: str,
                output_path: str,
                brightness: float = 0.0,
                contrast: float = 0.0,
                hue: float = 0.0,
                saturation: float = 0.0,
                lightness: float = 0.0,
                gamma: float = 1.0,
                levels: int = 8,
                threshold: float = 0.5,
                mode: str = "luminosity",
            ) -> dict[str, Any]:
                """Color adjustments: brightness_contrast, levels, curves, hue_saturation, etc."""
                return await gimp_color(
                    operation=operation,
                    input_path=input_path,
                    output_path=output_path,
                    brightness=brightness,
                    contrast=contrast,
                    hue=hue,
                    saturation=saturation,
                    lightness=lightness,
                    gamma=gamma,
                    levels=levels,
                    threshold=threshold,
                    mode=mode,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool()
            async def gimp_filter_tool(
                operation: str,
                input_path: str,
                output_path: str,
                radius: float = 1.0,
                amount: float = 0.5,
                method: str = "gaussian",
                effect: str = "oilify",
            ) -> dict[str, Any]:
                """Filters: blur, sharpen, noise, edge_detect, artistic, enhance, distort."""
                return await gimp_filter(
                    operation=operation,
                    input_path=input_path,
                    output_path=output_path,
                    radius=radius,
                    amount=amount,
                    method=method,
                    effect=effect,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool()
            async def gimp_layer_tool(
                operation: str,
                input_path: str,
                output_path: str,
                layer_name: str = "New Layer",
                layer_index: int = 0,
                opacity: float = 100.0,
                blend_mode: str = "normal",
                visible: bool = True,
            ) -> dict[str, Any]:
                """Layer management: create, duplicate, delete, merge, flatten, reorder, info."""
                return await gimp_layer(
                    operation=operation,
                    input_path=input_path,
                    output_path=output_path,
                    layer_name=layer_name,
                    layer_index=layer_index,
                    opacity=opacity,
                    blend_mode=blend_mode,
                    visible=visible,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool()
            async def gimp_analysis_tool(
                operation: str,
                input_path: str,
                compare_path: str | None = None,
                include_histogram: bool = True,
                analysis_type: str = "comprehensive",
                report_format: str = "detailed",
            ) -> dict[str, Any]:
                """Image analysis: quality, statistics, histogram, compare, detect_issues, report."""
                return await gimp_analysis(
                    operation=operation,
                    input_path=input_path,
                    compare_path=compare_path,
                    include_histogram=include_histogram,
                    analysis_type=analysis_type,
                    report_format=report_format,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool()
            async def gimp_batch_tool(
                operation: str,
                input_directory: str,
                output_directory: str,
                width: int | None = None,
                height: int | None = None,
                output_format: str = "jpg",
                quality: int = 90,
                file_pattern: str = "*.jpg",
                max_workers: int = 4,
            ) -> dict[str, Any]:
                """Batch processing: resize, convert, process, watermark, rename, optimize."""
                return await gimp_batch(
                    operation=operation,
                    input_directory=input_directory,
                    output_directory=output_directory,
                    width=width,
                    height=height,
                    output_format=output_format,
                    quality=quality,
                    file_pattern=file_pattern,
                    max_workers=max_workers,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool()
            async def gimp_system_tool(
                operation: str,
                topic: str | None = None,
                level: str = "basic",
                cache_action: str = "status",
            ) -> dict[str, Any]:
                """System: status, help, diagnostics, cache, config, performance, tools, version."""
                return await gimp_system(
                    operation=operation,
                    topic=topic,
                    level=level,
                    cache_action=cache_action,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            # Track registered tools
            self.tools = {
                "gimp_file": gimp_file_tool,
                "gimp_transform": gimp_transform_tool,
                "gimp_color": gimp_color_tool,
                "gimp_filter": gimp_filter_tool,
                "gimp_layer": gimp_layer_tool,
                "gimp_analysis": gimp_analysis_tool,
                "gimp_batch": gimp_batch_tool,
                "gimp_system": gimp_system_tool,
            }

            # Add GIMP Live Status tool
            @self.mcp.tool()
            async def gimp_live_status() -> dict[str, Any]:
                """Check the status of the GIMP Live session bridge."""
                if not self.interaction_manager:
                    return {
                        "success": False,
                        "mode": "offline",
                        "message": "GIMP MCP interaction layer not initialized",
                    }

                status = await self.interaction_manager.get_status()
                return {
                    "success": True,
                    "mode": status["mode"],
                    "message": f"GIMP is currently running in {status['mode']} mode",
                    "data": status,
                }

            # Register agentic workflow tools
            register_agentic_tools(self.mcp)

            return True

        except Exception as e:
            logger.error(f"Failed to register portmanteau tools: {e}", exc_info=True)
            return False

    async def _initialize_legacy_tools(self) -> bool:
        """
        Fall back to legacy tool registration (for backwards compatibility).

        Returns:
            bool: True if initialization successful
        """
        try:
            # Import all tool categories from the legacy tools package
            from .tools_legacy import (
                BatchProcessingTools,
                ColorAdjustmentTools,
                FileOperationTools,
                FilterTools,
                HelpTools,
                ImageAnalysisTools,
                LayerManagementTools,
                PerformanceTools,
                StatusTools,
                TransformTools,
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
                ("performance", PerformanceTools, [self.cli_wrapper, self.config]),
            ]

            # Register tool categories with safe error handling
            registration_results = {}
            for category_name, tool_class, init_args in tool_categories:
                success = self._safe_register_tool_category(category_name, tool_class, init_args)
                registration_results[category_name] = success

            # Log registration summary
            successful_count = sum(registration_results.values())
            total_count = len(registration_results)
            logger.info(f"Legacy tool registration: {successful_count}/{total_count} categories registered")

            # Register agentic workflow tools even with legacy tools
            try:
                from .agentic import register_agentic_tools

                register_agentic_tools(self.mcp)
                logger.info("Agentic workflow tools registered with legacy setup")
            except Exception as e:
                logger.warning(f"Failed to register agentic tools with legacy setup: {e}")

            return successful_count > 0

        except Exception as e:
            logger.error(f"Legacy tool initialization failed: {e}", exc_info=True)
            return False

    def run_http(self, host: str = "0.0.0.0", port: int = 8000) -> None:
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
        run_server(self.mcp, server_name="GIMP MCP Server")

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
        run_server(self.mcp, server_name="GIMP MCP Server")

    def _register_api_routes(self) -> None:
        """Register custom FastAPI routes for the web dashboard."""
        import json

        from fastapi import Response

        app = self.mcp.http_app

        @app.get("/api/health")
        @app.get("/api/status")
        async def get_health():
            """Return server health and GIMP connectivity status."""
            if not self.tools:
                return Response(
                    content=json.dumps({"status": "initializing", "message": "Server is still starting up"}),
                    media_type="application/json",
                )

            # Use the internal server's health check if available
            # We'll need a handle to the GimpMcpServer instance from server.py
            # Or just implement it here since we have config and interaction_manager

            status = "healthy"
            live_status = {"mode": "offline"}
            if self.interaction_manager:
                live_status = await self.interaction_manager.get_status()

            return {
                "status": status,
                "live_mode": live_status,
                "config": {
                    "gimp_executable": self.config.gimp_executable,
                    "max_concurrent_processes": self.config.max_concurrent_processes,
                },
                "server_name": "GIMP MCP Fleet Server",
                "version": "3.1.1",
            }


async def main_async():
    # Configure basic logging first to capture early messages
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
        handlers=[
            logging.StreamHandler(sys.stderr)  # Ensure logs go to stderr
        ],
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting GIMP MCP Server...")

    # Create parser using standardized transport parser
    from .transport import create_argument_parser

    parser = create_argument_parser("GIMP MCP Server")

    # Add GIMP-specific arguments
    parser.add_argument("--config", type=str, help="Path to config file", default=None)
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,  # Force reconfiguration of root logger
    )

    logger.info(f"Starting GIMP MCP Server with log level: {args.log_level}")

    # Initialize server
    try:
        server = GimpMCPServer(config_path=Path(args.config) if args.config else None)
    except Exception as e:
        logger.error(f"Error creating server: {e}")
        return 1

    # Initialize server components
    try:
        init_result = await server.initialize()
        if not init_result:
            logger.error("Failed to initialize GIMP MCP Server")
            return 1
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        logger.exception("Failed to initialize GIMP MCP Server")
        return 1

    try:
        # Pass args to run_server_async to let it handle transport selection
        await run_server_async(server.mcp, args=args, server_name="GIMP MCP Server")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception:
        logger.exception("Server error:")
        return 1

    logger.info("Server shutdown complete")
    return 0


def main():
    return asyncio.run(main_async())


if __name__ == "__main__":
    main()
