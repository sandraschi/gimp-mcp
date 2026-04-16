"""
GIMP MCP Server - Professional Image Editing through Model Context Protocol

This package provides a FastMCP 2.13+ server that enables AI agents like Claude
to perform professional image editing operations using GIMP (GNU Image
Manipulation Program).

v3.0.0 - Portmanteau Architecture:
Instead of 50+ individual tools, GIMP MCP consolidates related operations into 8
master portmanteau tools for reduced cognitive load and better discoverability.

Portmanteau Tools:
- gimp_file: File operations (load, save, convert, info)
- gimp_transform: Geometric transforms (resize, crop, rotate, flip)
- gimp_color: Color adjustments (brightness, levels, curves, HSL)
- gimp_filter: Filters (blur, sharpen, noise, artistic)
- gimp_layer: Layer management (create, merge, flatten)
- gimp_analysis: Image analysis (quality, statistics, compare)
- gimp_batch: Batch processing (resize, convert, watermark)
- gimp_system: System operations (status, help, cache)

Author: Sandra Schipal
License: MIT
"""

__version__ = "3.0.0"
__author__ = "Sandra Schipal"
__email__ = "sandra@sandraschi.dev"

from .server import GimpMcpServer

# Export portmanteau tools for direct use
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

__all__ = [
    "PORTMANTEAU_TOOLS",
    "GimpMcpServer",
    "gimp_analysis",
    "gimp_batch",
    "gimp_color",
    # Portmanteau tools
    "gimp_file",
    "gimp_filter",
    "gimp_layer",
    "gimp_system",
    "gimp_transform",
]
