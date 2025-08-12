"""
File Operation Tools for GIMP MCP Server.

Provides core file handling operations including loading, saving,
format conversion, and metadata extraction.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from .base import BaseToolCategory

logger = logging.getLogger(__name__)

class FileOperationTools(BaseToolCategory):
    """
    Core file operation tools for image handling.
    """
    
    def register_tools(self, app: FastMCP) -> None:
        """Register file operation tools with FastMCP."""
        
        @app.tool()
        async def load_image(file_path: str) -> Dict[str, Any]:
            """
            Load an image file and return comprehensive metadata.
            
            Args:
                file_path: Path to the image file to load
                
            Returns:
                Dict containing image metadata and handle for subsequent operations
            """
            try:
                # Validate input file
                if not self.validate_file_path(file_path, must_exist=True):
                    return self.create_error_response(f"Invalid or inaccessible file path: {file_path}")
                
                # Validate file format
                if not self.cli_wrapper.validate_image_file(file_path):
                    return self.create_error_response(f"Unsupported image format or file too large: {file_path}")
                
                # Load image information using GIMP
                image_info = await self.cli_wrapper.load_image_info(file_path)
                
                if not image_info:
                    return self.create_error_response(f"Failed to load image information from: {file_path}")
                
                # Get file system metadata
                path = Path(file_path)
                stat = path.stat()
                
                # Create comprehensive metadata
                metadata = {
                    "file_path": str(path.resolve()),
                    "file_name": path.name,
                    "file_size": stat.st_size,
                    "width": image_info.get("width"),
                    "height": image_info.get("height"),
                    "color_mode": image_info.get("color_mode", "UNKNOWN"),
                    "format": path.suffix.lower().lstrip('.'),
                    "created_date": stat.st_ctime,
                    "modified_date": stat.st_mtime
                }
                
                return self.create_success_response(
                    data=metadata,
                    message=f"Image loaded successfully: {path.name}"
                )
                
            except Exception as e:
                self.logger.error(f"Failed to load image {file_path}: {e}")
                return self.create_error_response(f"Failed to load image: {str(e)}")
        
        @app.tool()
        async def get_image_info(file_path: str) -> Dict[str, Any]:
            """
            Extract comprehensive metadata from an image file without loading it fully.
            
            Args:
                file_path: Path to the image file
                
            Returns:
                Dict containing detailed image metadata
            """
            try:
                # Validate input file
                if not self.validate_file_path(file_path, must_exist=True):
                    return self.create_error_response(f"Invalid or inaccessible file path: {file_path}")
                
                # Get basic file info
                path = Path(file_path)
                stat = path.stat()
                
                # Try to get GIMP metadata
                try:
                    gimp_info = await self.cli_wrapper.load_image_info(file_path)
                except Exception as e:
                    self.logger.warning(f"Could not get GIMP info for {file_path}: {e}")
                    gimp_info = {}
                
                # Compile comprehensive metadata
                metadata = {
                    "file_info": {
                        "path": str(path.resolve()),
                        "name": path.name,
                        "extension": path.suffix.lower().lstrip('.'),
                        "size_bytes": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "created": stat.st_ctime,
                        "modified": stat.st_mtime
                    },
                    "image_info": {
                        "width": gimp_info.get("width"),
                        "height": gimp_info.get("height"),
                        "color_mode": gimp_info.get("color_mode", "UNKNOWN"),
                        "has_transparency": None,  # Will be determined by GIMP
                        "bit_depth": gimp_info.get("precision")
                    },
                    "format_info": {
                        "format": path.suffix.lower().lstrip('.'),
                        "supported": self.config.is_format_supported(path.suffix.lower().lstrip('.')),
                        "can_edit": True if gimp_info else False
                    }
                }
                
                return self.create_success_response(
                    data=metadata,
                    message=f"Image metadata extracted successfully"
                )
                
            except Exception as e:
                self.logger.error(f"Failed to get image info for {file_path}: {e}")
                return self.create_error_response(f"Failed to extract image metadata: {str(e)}")
        
        @app.tool()
        async def save_image(input_path: str, 
                           output_path: str, 
                           format: str = "auto",
                           quality: int = 95) -> Dict[str, Any]:
            """
            Save/convert an image to the specified format and location.
            
            Args:
                input_path: Source image file path
                output_path: Destination file path
                format: Output format (auto-detected from extension if "auto")
                quality: JPEG quality (1-100, only applies to JPEG output)
                
            Returns:
                Dict containing operation status and output file information
            """
            try:
                # Validate input file
                if not self.validate_file_path(input_path, must_exist=True):
                    return self.create_error_response(f"Invalid input file path: {input_path}")
                
                # Validate output path
                if not self.validate_file_path(output_path, must_exist=False):
                    return self.create_error_response(f"Invalid output file path: {output_path}")
                
                # Determine output format
                output_path_obj = Path(output_path)
                if format == "auto":
                    target_format = output_path_obj.suffix.lower().lstrip('.')
                else:
                    target_format = format.lower()
                
                # Validate format support
                if not self.config.is_format_supported(target_format):
                    return self.create_error_response(f"Unsupported output format: {target_format}")
                
                # Validate quality parameter
                if not (1 <= quality <= 100):
                    return self.create_error_response("Quality must be between 1 and 100")
                
                # Perform conversion using GIMP
                success = await self.cli_wrapper.convert_image(
                    input_path=input_path,
                    output_path=output_path,
                    output_format=target_format,
                    quality=quality
                )
                
                if not success:
                    return self.create_error_response("Image conversion failed")
                
                # Get output file info
                output_stat = output_path_obj.stat()
                
                result_data = {
                    "input_path": input_path,
                    "output_path": str(output_path_obj.resolve()),
                    "output_format": target_format,
                    "output_size_bytes": output_stat.st_size,
                    "output_size_mb": round(output_stat.st_size / (1024 * 1024), 2),
                    "quality_used": quality if target_format in ["jpeg", "jpg"] else None
                }
                
                return self.create_success_response(
                    data=result_data,
                    message=f"Image saved successfully to {output_path_obj.name}"
                )
                
            except Exception as e:
                self.logger.error(f"Failed to save image from {input_path} to {output_path}: {e}")
                return self.create_error_response(f"Failed to save image: {str(e)}")
        
        @app.tool()
        async def convert_format(input_path: str,
                               output_path: str,
                               target_format: str,
                               quality: int = 95,
                               preserve_metadata: Optional[bool] = None) -> Dict[str, Any]:
            """
            Convert an image from one format to another with format-specific options.
            
            Args:
                input_path: Source image file path
                output_path: Destination file path
                target_format: Target format (jpeg, png, webp, tiff, etc.)
                quality: Compression quality for lossy formats (1-100)
                preserve_metadata: Whether to preserve EXIF data (None = use config default)
                
            Returns:
                Dict containing conversion results and file information
            """
            try:
                # Validate inputs
                if not self.validate_file_path(input_path, must_exist=True):
                    return self.create_error_response(f"Invalid input file: {input_path}")
                
                if not self.validate_file_path(output_path, must_exist=False):
                    return self.create_error_response(f"Invalid output path: {output_path}")
                
                # Validate target format
                target_format = target_format.lower()
                if not self.config.is_format_supported(target_format):
                    return self.create_error_response(f"Unsupported target format: {target_format}")
                
                # Use configuration default for metadata preservation if not specified
                if preserve_metadata is None:
                    preserve_metadata = self.config.preserve_metadata
                
                # Get input file info for comparison
                input_path_obj = Path(input_path)
                input_stat = input_path_obj.stat()
                input_format = input_path_obj.suffix.lower().lstrip('.')
                
                # Ensure output has correct extension
                output_path_obj = Path(output_path)
                if output_path_obj.suffix.lower().lstrip('.') != target_format:
                    output_path_obj = output_path_obj.with_suffix(f'.{target_format}')
                
                # Perform conversion
                success = await self.cli_wrapper.convert_image(
                    input_path=input_path,
                    output_path=str(output_path_obj),
                    output_format=target_format,
                    quality=quality
                )
                
                if not success:
                    return self.create_error_response("Format conversion failed")
                
                # Get output file info
                output_stat = output_path_obj.stat()
                
                # Calculate conversion statistics
                size_reduction = ((input_stat.st_size - output_stat.st_size) / input_stat.st_size) * 100
                
                conversion_data = {
                    "conversion": {
                        "input_format": input_format,
                        "output_format": target_format,
                        "quality": quality if target_format in ["jpeg", "jpg", "webp"] else None,
                        "metadata_preserved": preserve_metadata
                    },
                    "file_sizes": {
                        "input_bytes": input_stat.st_size,
                        "output_bytes": output_stat.st_size,
                        "size_change_percent": round(size_reduction, 2)
                    },
                    "paths": {
                        "input": input_path,
                        "output": str(output_path_obj.resolve())
                    }
                }
                
                return self.create_success_response(
                    data=conversion_data,
                    message=f"Successfully converted {input_format.upper()} to {target_format.upper()}"
                )
                
            except Exception as e:
                self.logger.error(f"Format conversion failed from {input_path}: {e}")
                return self.create_error_response(f"Format conversion failed: {str(e)}")
