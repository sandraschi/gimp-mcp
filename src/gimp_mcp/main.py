"""
GIMP MCP Server - FastMCP 3.2 SOTA Portmanteau Architecture

This module serves as the main entry point for the GIMP MCP server, providing
an interface between the MCP protocol and GIMP's functionality.

PORTMANTEAU ARCHITECTURE (v4.0.0):
Instead of 50+ individual tools, GIMP MCP consolidates related operations into 11
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
- gimp_gmic: G'MIC filter integration (list_categories, apply, apply_named)
- gimp_gegl: GEGL operation wrapper (list_ops, apply)
- gimp_color_management: ICC color management (profile_info, assign, convert, proofing)
"""

import asyncio
import logging
import os
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.server import create_proxy
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

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
    gimp_animation,
    gimp_batch,
    gimp_channel,
    gimp_color,
    gimp_color_management,
    gimp_file,
    gimp_filter,
    gimp_gegl,
    gimp_gmic,
    gimp_layer,
    gimp_parasites,
    gimp_paths,
    gimp_system,
    gimp_transform,
    gimp_workspace,
)
from .tools.agent_lab_registration import register_agent_lab_tools
from pydantic import Field

from .sota_registration import get_sota_feature_manifest, register_fastmcp_32_surface
from .transport import run_server, run_server_async

# Legacy imports for backwards compatibility (reserved for future use if needed)
# from .tools_legacy import ...

# Configure structured logging
logger = setup_logging(component="main")


@asynccontextmanager
async def _gimp_mcp_lifespan(mcp: FastMCP) -> AsyncGenerator[None, None]:
    """FastMCP 3.2 server lifespan hook."""
    log = logging.getLogger(__name__)
    log.info("GIMP MCP lifespan: startup")
    try:
        yield
    finally:
        log.info("GIMP MCP lifespan: shutdown")


class GimpMCPServer:
    """Main server class for GIMP MCP integration."""

    def __init__(self, config_path: Path | None = None):
        """Initialize the GIMP MCP server.

        Args:
            config_path: Optional path to configuration file
        """
        self.config = load_config(config_path) if config_path else GimpConfig()

        # Initialize FastMCP 3.2 SOTA instance
        self.mcp = FastMCP(
            name="gimp-mcp",
            version="4.5.2",
            lifespan=_gimp_mcp_lifespan,
            instructions="""You are GIMP MCP Server — FastMCP 3.2 SOTA for professional image editing with GIMP.

FASTMCP 3.2 SURFACE:
- Sampling (ctx.sample / agentic workflows) when the host supports MCP sampling
- Prompts: gimp_edit_session, gimp_batch_folder_prep, gimp_color_grading_pass, gimp_agentic_sampling_hint
- Resources: resource://gimp/documentation/*  |  Skills: skill://gimp-expert/SKILL.md
- Prefab UI tools (gimp_capabilities_card) in capable clients
- Portmanteau tools to limit tool explosion

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
            strict_input_validation=True,
            mask_error_details=True,
            client_log_level="info",
        )

        # MCP Bridge: proxy to external MCP servers via MCP_BRIDGE_URLS env var
        _bridge_urls = os.environ.get("MCP_BRIDGE_URLS", "")
        if _bridge_urls:
            for _bu in _bridge_urls.split(","):
                _bu = _bu.strip()
                if _bu:
                    self.mcp.add_provider(create_proxy(_bu))

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

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_file_tool(
                operation: Annotated[str, Field(description="Operation to execute: load, save, convert, info, validate, list_formats.")],
                input_path: Annotated[str | None, Field(description="Source image file path.")] = None,
                output_path: Annotated[str | None, Field(description="Destination image file path.")] = None,
                format: Annotated[str | None, Field(description="Output format (jpg, png, webp, gif, bmp, tiff).")] = None,
                quality: Annotated[int, Field(description="Output quality 1-100.")] = 95,
                compression: Annotated[int, Field(description="Compression level 0-9.")] = 6,
                progressive: Annotated[bool, Field(description="Enable progressive JPEG.")] = False,
            ) -> dict[str, Any]:
                """Consolidated file operations for GIMP.

                [RATIONALE] All file I/O is consolidated into one portmanteau to prevent
                tool explosion while keeping load, save, convert, and info operations
                discoverable under a single namespace.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_file_tool(operation="info", input_path="/images/photo.png")
                gimp_file_tool(operation="convert", input_path="/images/photo.png", output_path="/images/photo.webp", format="webp")
                """
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

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_transform_tool(
                operation: Annotated[str, Field(description="Operation to execute: resize, crop, rotate, flip, scale, perspective, autocrop.")],
                input_path: Annotated[str, Field(description="Source image file path.")],
                output_path: Annotated[str, Field(description="Destination image file path.")],
                width: Annotated[int | None, Field(description="Target width in pixels.")] = None,
                height: Annotated[int | None, Field(description="Target height in pixels.")] = None,
                maintain_aspect: Annotated[bool, Field(description="Maintain aspect ratio when resizing.")] = True,
                x: Annotated[int, Field(description="Crop start X coordinate.")] = 0,
                y: Annotated[int, Field(description="Crop start Y coordinate.")] = 0,
                degrees: Annotated[float, Field(description="Rotation angle in degrees.")] = 0.0,
                direction: Annotated[str, Field(description="Flip direction: horizontal, vertical, both.")] = "horizontal",
                fill_color: Annotated[str, Field(description="Fill color for transparent areas.")] = "transparent",
            ) -> dict[str, Any]:
                """Consolidated geometric transforms for GIMP.

                [RATIONALE] All geometric transforms are consolidated into one portmanteau to
                prevent tool explosion across resize, crop, rotate, flip, and perspective operations.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_transform_tool(operation="resize", input_path="/images/photo.png", output_path="/images/photo_small.png", width=800, height=600)
                gimp_transform_tool(operation="rotate", input_path="/images/photo.png", output_path="/images/photo_rotated.png", degrees=90)
                """
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

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_color_tool(
                operation: Annotated[str, Field(description="Operation to execute: brightness_contrast, levels, curves, hue_saturation, color_balance, desaturate, auto.")],
                input_path: Annotated[str, Field(description="Source image file path.")],
                output_path: Annotated[str, Field(description="Destination image file path.")],
                brightness: Annotated[float, Field(description="Brightness adjustment (-1.0 to 1.0).")] = 0.0,
                contrast: Annotated[float, Field(description="Contrast adjustment (-1.0 to 1.0).")] = 0.0,
                hue: Annotated[float, Field(description="Hue shift in degrees (-180 to 180).")] = 0.0,
                saturation: Annotated[float, Field(description="Saturation adjustment (-1.0 to 1.0).")] = 0.0,
                lightness: Annotated[float, Field(description="Lightness adjustment (-1.0 to 1.0).")] = 0.0,
                gamma: Annotated[float, Field(description="Gamma correction value (0.1 to 10.0).")] = 1.0,
                levels: Annotated[int, Field(description="Number of levels for posterize operation.")] = 8,
                threshold: Annotated[float, Field(description="Threshold value (0.0 to 1.0).")] = 0.5,
                mode: Annotated[str, Field(description="Blend or conversion mode (luminosity, LCH, HSL).")] = "luminosity",
            ) -> dict[str, Any]:
                """Consolidated color adjustment operations for GIMP.

                [RATIONALE] All color operations are consolidated into one portmanteau to
                prevent tool explosion while keeping brightness, curves, levels, and HSL
                adjustments discoverable under a single namespace.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_color_tool(operation="brightness_contrast", input_path="/images/photo.png", output_path="/images/photo_adjusted.png", brightness=0.2, contrast=0.3)
                gimp_color_tool(operation="hue_saturation", input_path="/images/photo.png", output_path="/images/photo_hsl.png", hue=30, saturation=0.5)
                """
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

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_filter_tool(
                operation: Annotated[str, Field(description="Operation to execute: blur, sharpen, noise, edge_detect, artistic, enhance, distort.")],
                input_path: Annotated[str, Field(description="Source image file path.")],
                output_path: Annotated[str, Field(description="Destination image file path.")],
                radius: Annotated[float, Field(description="Filter radius in pixels.")] = 1.0,
                amount: Annotated[float, Field(description="Filter intensity (0.0 to 1.0).")] = 0.5,
                method: Annotated[str, Field(description="Filter method: gaussian, median, motion_blur, pixelize.")] = "gaussian",
                effect: Annotated[str, Field(description="Artistic effect: oilify, cubism, softglow, apply_canvas.")] = "oilify",
            ) -> dict[str, Any]:
                """Consolidated filter operations for GIMP.

                [RATIONALE] All filter operations are consolidated into one portmanteau to
                prevent tool explosion across blur, sharpen, noise, edge detection, and
                artistic filter categories.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_filter_tool(operation="blur", input_path="/images/photo.png", output_path="/images/photo_blurred.png", radius=3.0)
                gimp_filter_tool(operation="sharpen", input_path="/images/photo.png", output_path="/images/photo_sharp.png", amount=0.8)
                """
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

            @self.mcp.tool(annotations={"destructiveHint": True}, version="4.1.0")
            async def gimp_layer_tool(
                operation: Annotated[str, Field(description="Operation to execute: create, duplicate, delete, merge, flatten, reorder, info.")],
                input_path: Annotated[str, Field(description="Source image file path.")],
                output_path: Annotated[str, Field(description="Destination image file path.")],
                layer_name: Annotated[str, Field(description="Name for the new layer.")] = "New Layer",
                layer_index: Annotated[int, Field(description="Layer index for reorder operations.")] = 0,
                opacity: Annotated[float, Field(description="Layer opacity percentage (0-100).")] = 100.0,
                blend_mode: Annotated[str, Field(description="Layer blend mode: normal, multiply, screen, overlay, etc.")] = "normal",
                visible: Annotated[bool, Field(description="Layer visibility state.")] = True,
            ) -> dict[str, Any]:
                """Consolidated layer management operations for GIMP.

                [RATIONALE] All layer operations are consolidated into one portmanteau to
                prevent tool explosion while keeping create, merge, flatten, and reorder
                operations discoverable under a single namespace.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_layer_tool(operation="info", input_path="/images/photo.xcf", output_path="/images/photo.xcf")
                gimp_layer_tool(operation="flatten", input_path="/images/photo.xcf", output_path="/images/flattened.png")
                """
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

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_analysis_tool(
                operation: Annotated[str, Field(description="Operation to execute: quality, statistics, histogram, compare, detect_issues, report.")],
                input_path: Annotated[str, Field(description="Source image file path.")],
                compare_path: Annotated[str | None, Field(description="Second image path for comparison operations.")] = None,
                include_histogram: Annotated[bool, Field(description="Include histogram data in results.")] = True,
                analysis_type: Annotated[str, Field(description="Analysis scope: comprehensive, quick, technical, aesthetic.")] = "comprehensive",
                report_format: Annotated[str, Field(description="Report verbosity: detailed, summary, json.")] = "detailed",
            ) -> dict[str, Any]:
                """Consolidated image analysis operations for GIMP.

                [RATIONALE] All analysis operations are consolidated into one portmanteau to
                prevent tool explosion across quality assessment, statistics, histogram, and
                comparison features.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_analysis_tool(operation="statistics", input_path="/images/photo.png")
                gimp_analysis_tool(operation="compare", input_path="/images/photo.png", compare_path="/images/photo_edited.png")
                """
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

            @self.mcp.tool(annotations={"destructiveHint": True}, version="4.1.0")
            async def gimp_batch_tool(
                operation: Annotated[str, Field(description="Operation to execute: resize, convert, process, watermark, rename, optimize.")],
                input_directory: Annotated[str, Field(description="Directory containing source images.")],
                output_directory: Annotated[str, Field(description="Directory for processed images.")],
                width: Annotated[int | None, Field(description="Target width in pixels for resize operations.")] = None,
                height: Annotated[int | None, Field(description="Target height in pixels for resize operations.")] = None,
                output_format: Annotated[str, Field(description="Output format for convert operations.")] = "jpg",
                quality: Annotated[int, Field(description="Output quality 1-100.")] = 90,
                file_pattern: Annotated[str, Field(description="Glob pattern for input files.")] = "*.jpg",
                max_workers: Annotated[int, Field(description="Maximum parallel workers.")] = 4,
            ) -> dict[str, Any]:
                """Consolidated batch processing operations for GIMP.

                [RATIONALE] All batch processing is consolidated into one portmanteau to
                prevent tool explosion while keeping resize, convert, watermark, and optimize
                operations discoverable under a single namespace.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_batch_tool(operation="resize", input_directory="/images/input", output_directory="/images/output", width=800, height=600)
                gimp_batch_tool(operation="convert", input_directory="/images/input", output_directory="/images/output", output_format="webp", quality=85)
                """
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

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_system_tool(
                operation: Annotated[str, Field(description="Operation to execute: status, help, diagnostics, cache, config, performance, tools, version.")],
                topic: Annotated[str | None, Field(description="Help topic or diagnostic area.")] = None,
                level: Annotated[str, Field(description="Detail level: basic, detailed, debug.")] = "basic",
                cache_action: Annotated[str, Field(description="Cache action: status, clear, warm.")] = "status",
            ) -> dict[str, Any]:
                """Consolidated system operations for GIMP MCP.

                [RATIONALE] All system-level operations are consolidated into one portmanteau
                to prevent tool explosion across status, help, diagnostics, and cache management.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_system_tool(operation="status")
                gimp_system_tool(operation="help", topic="file_operations", level="detailed")
                """
                return await gimp_system(
                    operation=operation,
                    topic=topic,
                    level=level,
                    cache_action=cache_action,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool(annotations={"destructiveHint": True}, version="4.1.0")
            async def gimp_pdb_tool(
                procedure: Annotated[str, Field(description="GIMP PDB procedure name (e.g. gimp_selection_all, plug_in_gauss).")],
                args: Annotated[list[Any] | None, Field(description="List of arguments for the PDB procedure.")] = None,
            ) -> dict[str, Any]:
                """Call any GIMP PDB procedure by name.

                Universal escape hatch to GIMP full Procedural Database with
                over 1000+ procedures available without individual wrappers.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "procedure": str}

                ## Examples
                gimp_pdb_tool(procedure="gimp_selection_all")
                gimp_pdb_tool(procedure="plug_in_gauss", args=[5.0])
                """
                from .tools import gimp_pdb as _gimp_pdb
                return await _gimp_pdb(
                    procedure=procedure,
                    args=args or [],
                    interaction_manager=self.interaction_manager,
                    cli_wrapper=self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_animation_tool(
                operation: Annotated[str, Field(description="Operation to execute: list_frames, set_frame_delay, optimize_for_gif, export_gif, frame_count.")],
                image_path: Annotated[str, Field(description="Source image file path (XCF or layered image).")],
                output_path: Annotated[str | None, Field(description="Destination path for export/optimize operations.")] = None,
                frame_delay_ms: Annotated[int, Field(description="Frame delay in milliseconds.")] = 100,
                frame_index: Annotated[int | None, Field(description="Frame index for set_frame_delay.")] = None,
                loop_forever: Annotated[bool, Field(description="Loop animation forever on GIF export.")] = True,
                dither: Annotated[bool, Field(description="Apply Floyd-Steinberg dithering on GIF export.")] = True,
            ) -> dict[str, Any]:
                """Frame-based animation operations for GIMP.

                [RATIONALE] Animation operations are consolidated into one portmanteau to
                prevent tool explosion across frame listing, delay setting, and GIF export.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_animation_tool(operation="list_frames", image_path="/images/animation.xcf")
                gimp_animation_tool(operation="export_gif", image_path="/images/animation.xcf", output_path="/images/output.gif")
                """
                return await gimp_animation(
                    operation=operation,
                    image_path=image_path,
                    output_path=output_path,
                    frame_delay_ms=frame_delay_ms,
                    frame_index=frame_index,
                    loop_forever=loop_forever,
                    dither=dither,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_paths_tool(
                operation: Annotated[str, Field(description="Operation to execute: create, delete, list, stroke, import_svg, export_svg, set_name, get_points.")],
                image_path: Annotated[str, Field(description="Source image file path.")],
                svg_path: Annotated[str | None, Field(description="SVG file path for import/export operations.")] = None,
                path_name: Annotated[str, Field(description="Name of the vector path.")] = "Path",
                new_name: Annotated[str | None, Field(description="New name for set_name operation.")] = None,
            ) -> dict[str, Any]:
                """Vector path (SVG) operations for GIMP.

                [RATIONALE] All vector path operations are consolidated into one portmanteau
                to prevent tool explosion across create, delete, stroke, and SVG I/O operations.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_paths_tool(operation="list", image_path="/images/photo.xcf")
                gimp_paths_tool(operation="import_svg", image_path="/images/photo.xcf", svg_path="/paths/design.svg")
                """
                return await gimp_paths(
                    operation=operation,
                    image_path=image_path,
                    svg_path=svg_path,
                    path_name=path_name,
                    new_name=new_name,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_parasites_tool(
                operation: Annotated[str, Field(description="Operation to execute: list_image, list_drawable, attach_image, attach_drawable, detach_image, detach_drawable, get_image, get_drawable, get_animation_delay.")],
                image_path: Annotated[str, Field(description="Source image file path.")],
                parasite_name: Annotated[str | None, Field(description="Name of the parasite.")] = None,
                parasite_data: Annotated[str | None, Field(description="Data payload for attach operations.")] = None,
                frame_delay_ms: Annotated[int, Field(description="Frame delay in milliseconds for get_animation_delay.")] = 100,
            ) -> dict[str, Any]:
                """XCF metadata (parasite) operations for GIMP.

                [RATIONALE] Parasite operations are consolidated into one portmanteau to
                prevent tool explosion across list, attach, detach, and get operations
                for both image-level and drawable-level parasites.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_parasites_tool(operation="list_image", image_path="/images/photo.xcf")
                gimp_parasites_tool(operation="attach_image", image_path="/images/photo.xcf", parasite_name="my-metadata", parasite_data="...")
                """
                return await gimp_parasites(
                    operation=operation,
                    image_path=image_path,
                    parasite_name=parasite_name,
                    parasite_data=parasite_data,
                    frame_delay_ms=frame_delay_ms,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_gmic_tool(
                operation: Annotated[str, Field(description="Operation: list_categories, apply, apply_named, list_filters.")],
                filter_command: Annotated[str | None, Field(description="Raw G'MIC command string (e.g. '-fx_meteor', '-blur_gaussian 5'). Used with operation='apply'.")] = None,
                filter_name: Annotated[str | None, Field(description="Known filter name from presets. Used with operation='apply_named'.")] = None,
                filter_params: Annotated[dict[str, Any] | None, Field(description="Optional parameter overrides for named filter.")] = None,
            ) -> dict[str, Any]:
                """G'MIC filter integration — 500+ filters through plug-in-gmic.

                [RATIONALE] G'MIC provides 500+ filters via a single PDB procedure.
                Consolidating category listing, raw command execution, and named filter
                dispatch prevents tool explosion.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_gmic_tool(operation="list_categories")
                gimp_gmic_tool(operation="apply", filter_command="-fx_meteor")
                gimp_gmic_tool(operation="apply_named", filter_name="blur_gaussian", filter_params={"radius": "10"})
                """
                return await gimp_gmic(
                    operation=operation,
                    filter_command=filter_command,
                    filter_name=filter_name,
                    filter_params=filter_params,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_gegl_tool(
                operation: Annotated[str, Field(description="Operation: list_ops, apply.")],
                operation_name: Annotated[str | None, Field(description="GEGL operation name (e.g. 'gaussian-blur', 'crop'). Used with operation='apply'.")] = None,
                config_string: Annotated[str | None, Field(description="JSON config string for the GEGL operation (e.g. '{\"radius\": 5.0}'). Used with operation='apply'.")] = None,
            ) -> dict[str, Any]:
                """GEGL operation wrapper — GIMP 3 non-destructive editing engine.

                [RATIONALE] GEGL operations power GIMP 3's non-destructive editing.
                Wrapping operation discovery and application into one tool prevents
                tool explosion while keeping the full GEGL surface accessible.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_gegl_tool(operation="list_ops")
                gimp_gegl_tool(operation="apply", operation_name="gaussian-blur", config_string='{"radius": 5.0}')
                """
                return await gimp_gegl(
                    operation=operation,
                    operation_name=operation_name,
                    config_string=config_string,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_color_management_tool(
                operation: Annotated[str, Field(description="Operation: profile_info, assign_profile, convert_profile, get_effective_profile, soft_proofing, simulation_profile, list_profiles.")],
                profile_path: Annotated[str | None, Field(description="Path to ICC profile file. Required for: assign_profile, convert_profile, simulation_profile.")] = None,
                soft_proofing_enabled: Annotated[bool | None, Field(description="Enable/disable soft proofing. Used with operation='soft_proofing'.")] = None,
            ) -> dict[str, Any]:
                """ICC color management — profile info, assignment, conversion, soft proofing.

                [RATIONALE] All color management operations are consolidated into one
                portmanteau to prevent tool explosion across profile info, assignment,
                conversion, and proofing workflows.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_color_management_tool(operation="profile_info")
                gimp_color_management_tool(operation="list_profiles")
                gimp_color_management_tool(operation="assign_profile", profile_path="/path/to/sRGB.icc")
                gimp_color_management_tool(operation="soft_proofing", soft_proofing_enabled=True)
                """
                return await gimp_color_management(
                    operation=operation,
                    profile_path=profile_path,
                    soft_proofing_enabled=soft_proofing_enabled,
                    cli_wrapper=self.interaction_manager or self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool(annotations={"readOnlyHint": True}, version="4.1.0")
            async def gimp_workspace_tool(
                operation: Annotated[str, Field(description="Operation to execute: list_images, current_image, undo_count, undo, redo, undo_group_start, undo_group_end, get_metadata, set_resolution, set_unit.")],
                image_id: Annotated[int | None, Field(description="Target image ID for workspace operations. Required for undo, redo, undo_group_start, undo_group_end, get_metadata, set_resolution, set_unit. Optional for current_image (omit to get active, set to switch).")] = None,
                xresolution: Annotated[float, Field(description="Horizontal resolution in DPI for set_resolution.")] = 72.0,
                yresolution: Annotated[float, Field(description="Vertical resolution in DPI for set_resolution.")] = 72.0,
                unit: Annotated[int, Field(description="Unit ID for set_unit (0=pixels, 1=inches, 2=mm, 3=points, 4=picas).")] = 0,
            ) -> dict[str, Any]:
                """Consolidated image workspace state management for GIMP.

                [RATIONALE] All workspace operations are consolidated into one portmanteau
                to prevent tool explosion while keeping image listing, undo/redo, metadata,
                resolution, and unit ops discoverable under a single namespace.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_workspace_tool(operation="list_images")
                gimp_workspace_tool(operation="current_image")
                gimp_workspace_tool(operation="undo", image_id=42)
                gimp_workspace_tool(operation="get_metadata", image_id=42)
                """
                return await gimp_workspace(
                    operation=operation,
                    image_id=image_id,
                    xresolution=xresolution,
                    yresolution=yresolution,
                    unit=unit,
                    interaction_manager=self.interaction_manager,
                    cli_wrapper=self.cli_wrapper,
                    config=self.config,
                )

            @self.mcp.tool(annotations={"destructiveHint": True}, version="4.1.0")
            async def gimp_channel_tool(
                operation: Annotated[str, Field(description="Operation to execute: create, delete, list, set_color, set_opacity, set_show_masked, duplicate, info.")],
                image_id: Annotated[int, Field(description="Target image ID for channel operations.")],
                channel_id: Annotated[int | None, Field(description="Target channel ID. Required for: delete, set_color, set_opacity, set_show_masked, duplicate, info.")] = None,
                channel_name: Annotated[str, Field(description="Name for the new channel. Used by: create.")] = "New Channel",
                width: Annotated[int, Field(description="Channel width in pixels. 0 = image width. Used by: create.")] = 0,
                height: Annotated[int, Field(description="Channel height in pixels. 0 = image height. Used by: create.")] = 0,
                color: Annotated[str, Field(description="Channel color (CSS color name or hex). Used by: set_color.")] = "red",
                opacity: Annotated[float, Field(description="Channel opacity 0-100. Used by: set_opacity.")] = 100.0,
                show_masked: Annotated[bool, Field(description="Show masked area instead of selection. Used by: set_show_masked.")] = False,
            ) -> dict[str, Any]:
                """Consolidated channel management operations for GIMP.

                [RATIONALE] All channel operations are consolidated into one portmanteau
                to prevent tool explosion while keeping create, delete, list, color,
                opacity, and duplication operations discoverable under a single namespace.

                ## Return Format
                {"success": bool, "message": str, "data": {...}, "operation": str}

                ## Examples
                gimp_channel_tool(operation="list", image_id=42)
                gimp_channel_tool(operation="create", image_id=42, channel_name="Alpha Mask")
                gimp_channel_tool(operation="set_color", image_id=42, channel_id=7, color="blue")
                """
                return await gimp_channel(
                    operation=operation,
                    image_id=image_id,
                    channel_id=channel_id,
                    channel_name=channel_name,
                    width=width,
                    height=height,
                    color=color,
                    opacity=opacity,
                    show_masked=show_masked,
                    interaction_manager=self.interaction_manager,
                    cli_wrapper=self.cli_wrapper,
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
                "gimp_pdb": gimp_pdb_tool,
                "gimp_workspace": gimp_workspace_tool,
                "gimp_channel": gimp_channel_tool,
                "gimp_animation": gimp_animation_tool,
                "gimp_paths": gimp_paths_tool,
                "gimp_parasites": gimp_parasites_tool,
                "gimp_gmic": gimp_gmic_tool,
                "gimp_gegl": gimp_gegl_tool,
                "gimp_color_management": gimp_color_management_tool,
            }

            register_agent_lab_tools(self.mcp, self.interaction_manager, self.config)

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
        """Register Starlette HTTP routes (health, SOTA manifest) on the FastMCP ASGI app."""

        server = self

        @self.mcp.custom_route("/api/health", methods=["GET"])
        async def api_health(_request: Request) -> Response:
            if not server.tools:
                return JSONResponse(
                    {"status": "initializing", "message": "Server is still starting up"},
                )
            live_status: dict[str, Any] = {"mode": "offline"}
            if server.interaction_manager:
                live_status = await server.interaction_manager.get_status()
            payload = {
                "status": "healthy",
                "live_mode": live_status,
                "config": {
                    "gimp_executable": server.config.gimp_executable,
                    "max_concurrent_processes": server.config.max_concurrent_processes,
                },
                "server_name": "gimp-mcp",
                "version": "4.0.0",
                "fastmcp": "3.2",
                "sota": get_sota_feature_manifest(),
            }
            return JSONResponse(payload)

        @self.mcp.custom_route("/api/status", methods=["GET"])
        async def api_status(request: Request) -> Response:
            return await api_health(request)

        @self.mcp.custom_route("/api/sota", methods=["GET"])
        async def api_sota(_request: Request) -> Response:
            return JSONResponse(get_sota_feature_manifest())


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

    try:
        from fastmcp.experimental.transforms import CodeMode
        logger.info("CodeMode enabled for BM25 discovery")
    except ImportError:
        logger.debug("CodeMode not available -- skipping")

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
