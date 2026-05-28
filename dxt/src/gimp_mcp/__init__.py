"""
GIMP MCP Server - Professional Image Editing through Model Context Protocol

This package provides a FastMCP server that enables AI agents like Claude
to perform professional image editing operations using GIMP (GNU Image
Manipulation Program).

Key Features:
- Cross-platform GIMP integration (Windows, macOS, Linux)
- Professional image editing tools via MCP protocol
- Batch processing capabilities
- Format conversion and optimization
- Color adjustment and filtering
- Geometric transformations
- Error handling and recovery

Author: Sandra Schieder
License: MIT
"""

__version__ = "0.1.0"
__author__ = "Sandra Schieder"
__email__ = "sandra@sandraschi.dev"

from .server import GimpMcpServer

__all__ = ["GimpMcpServer"]
