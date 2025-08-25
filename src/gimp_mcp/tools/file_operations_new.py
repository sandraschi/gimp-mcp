"""
File Operation Tools for GIMP MCP Server.

This module provides core file handling operations for the GIMP MCP server,
including loading, saving, format conversion, and metadata extraction.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from fastmcp import FastMCP

__all__ = ['FileOperationTools', 'FileOperationResult']

# Type aliases
FilePath = str
ImageMetadata = Dict[str, Any]

# Supported formats
SUPPORTED_RASTER_FORMATS = ['png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp', 'gif', 'webp', 'xcf']
SUPPORTED_VECTOR_FORMATS = ['svg']
SUPPORTED_METADATA = ['exif', 'xmp', 'iptc']

logger = logging.getLogger(__name__)

@dataclass
class FileOperationResult:
    """Result container for file operations."""
    success: bool
    message: str
    data: Dict[str, Any] = None
    error: Optional[str] = None

class FileOperationTools:
    """Tools for file operations in GIMP MCP Server."""
    
    def __init__(self, cli_wrapper: Any, config: Any):
        """Initialize file operation tools."""
        self.cli_wrapper = cli_wrapper
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def create_success_response(self, data: Dict[str, Any], message: str = "") -> Dict[str, Any]:
        """Create a standardized success response."""
        return {
            "success": True,
            "data": data,
            "message": message
        }
    
    def create_error_response(self, error: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a standardized error response."""
        response = {
            "success": False,
            "error": error
        }
        if details:
            response["details"] = details
        return response

    def register_tools(self, mcp: FastMCP) -> None:
        """Register all file operation tools with the MCP server."""
        
        @mcp.tool(
            name="load_image",
            description="Load an image file and return metadata and image handle.",
            parameters={
                "file_path": {"type": "string", "format": "file-path", "required": True},
                "load_metadata": {"type": "boolean", "default": True},
                "max_dimension": {"type": "integer", "minimum": 0, "default": 0}
            }
        )
        async def load_image(file_path: str, load_metadata: bool = True, max_dimension: int = 0) -> Dict[str, Any]:
            """Load an image file and return metadata."""
            try:
                if not os.path.exists(file_path):
                    return self.create_error_response(f"File not found: {file_path}")
                
                path = Path(file_path)
                stat = path.stat()
                
                result = {
                    "success": True,
                    "file_path": str(path.resolve()),
                    "file_name": path.name,
                    "file_size": stat.st_size,
                    "created_date": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "format": path.suffix.lower().lstrip('.')
                }
                
                if hasattr(self.cli_wrapper, 'get_image_metadata'):
                    try:
                        metadata = await self.cli_wrapper.get_image_metadata(
                            str(path),
                            load_metadata=load_metadata,
                            max_dimension=max_dimension
                        )
                        result.update(metadata)
                    except Exception as e:
                        self.logger.warning(f"Could not get image metadata: {e}")
                
                return self.create_success_response(result)
                
            except Exception as e:
                self.logger.error(f"Failed to load image {file_path}: {e}", exc_info=True)
                return self.create_error_response(f"Failed to load image: {str(e)}")
        
        @mcp.tool(
            name="save_image",
            description="Save or convert an image to the specified format and location.",
            parameters={
                "input_path": {"type": "string", "format": "file-path", "required": True},
                "output_path": {"type": "string", "format": "file-path", "required": True},
                "format": {"type": "string", "default": "auto"},
                "quality": {"type": "integer", "minimum": 1, "maximum": 100, "default": 95},
                "preserve_metadata": {"type": "boolean", "default": True},
                "overwrite": {"type": "boolean", "default": False}
            }
        )
        async def save_image(
            input_path: str,
            output_path: str,
            format: str = "auto",
            quality: int = 95,
            preserve_metadata: bool = True,
            overwrite: bool = False
        ) -> Dict[str, Any]:
            """Save or convert an image to the specified format and location."""
            try:
                if not os.path.exists(input_path):
                    return self.create_error_response(f"Input file not found: {input_path}")
                
                if not overwrite and os.path.exists(output_path):
                    return self.create_error_response(
                        f"Output file already exists: {output_path}",
                        details={"suggestion": "Set overwrite=True to replace existing file"}
                    )
                
                if format == "auto":
                    format = Path(output_path).suffix.lower().lstrip('.')
                
                if hasattr(self.cli_wrapper, 'save_image'):
                    result = await self.cli_wrapper.save_image(
                        input_path=input_path,
                        output_path=output_path,
                        format=format,
                        quality=quality,
                        preserve_metadata=preserve_metadata
                    )
                    
                    if result.get('success'):
                        return self.create_success_response({
                            "input_path": input_path,
                            "output_path": output_path,
                            "format": format,
                            "file_size": os.path.getsize(output_path),
                            "file_size_mb": round(os.path.getsize(output_path) / (1024 * 1024), 2),
                            "preserved_metadata": preserve_metadata
                        }, "Image saved successfully")
                    else:
                        return self.create_error_response(
                            result.get('error', 'Failed to save image'),
                            result.get('details')
                        )
                else:
                    return self.create_error_response("Image saving not implemented in CLI wrapper")
                    
            except Exception as e:
                self.logger.error(f"Failed to save image: {e}", exc_info=True)
                return self.create_error_response(f"Failed to save image: {str(e)}")
        
        # Register additional tools here if needed
