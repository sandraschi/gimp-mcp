"""
File Operation Tools for GIMP MCP Server.

This module provides core file handling operations for the GIMP MCP server,
including loading, saving, format conversion, and metadata extraction.

Key Features:
- Image loading with format detection and validation
- Saving images in various formats with quality control
- File format conversion with automatic format detection
- Comprehensive metadata extraction and manipulation
- File validation and security checks

Supported Formats:
- Raster: PNG, JPEG, TIFF, BMP, GIF, WebP, XCF (GIMP native)
- Vector: SVG (read-only)
- Metadata: EXIF, XMP, IPTC
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List, Union, Tuple
from datetime import datetime

from fastmcp import FastMCP

from .base import BaseToolCategory, tool

logger = logging.getLogger(__name__)

# Type aliases for better readability
FilePath = str
ImageMetadata = Dict[str, Any]

class FileOperationTools(BaseToolCategory):
    """
    Core file operation tools for image handling in GIMP MCP.
    
    This class provides methods for loading, saving, and manipulating image files
    with support for various formats and metadata operations. It serves as the
    foundation for all file-based operations in the GIMP MCP server.
    
    Features:
    - Thread-safe file operations
    - Automatic format detection
    - Metadata preservation
    - Security validation
    - Progress reporting
    """
    
    def __init__(self, cli_wrapper, config):
        """Initialize file operation tools with dependencies."""
        super().__init__(cli_wrapper, config)
        self._supported_formats = {
            'raster': ['png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp', 'gif', 'webp', 'xcf'],
            'vector': ['svg'],
            'metadata': ['exif', 'xmp', 'iptc']
        }
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Convert a timestamp to a human-readable format."""
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    @tool(
        name="load_image",
        description="""
        Load an image file and return comprehensive metadata.
        
        This method loads an image file from the specified path, validates it,
        extracts metadata, and returns a structured response with image details.
        The returned handle can be used for subsequent operations on the image.
        """,
        parameters={
            "file_path": {
                "type": "string",
                "description": "Path to the image file to load",
                "required": True,
                "format": "file"
            },
            "load_metadata": {
                "type": "boolean",
                "description": "Whether to load image metadata (EXIF, XMP, etc.)",
                "default": True
            },
            "max_dimension": {
                "type": "integer",
                "description": "Maximum dimension for loaded images (0 for no limit)",
                "default": 0,
                "minimum": 0
            }
        },
        returns={
            "type": "object",
            "description": "Image metadata and handle for subsequent operations",
            "properties": {
                "success": {"type": "boolean"},
                "file_path": {"type": "string"},
                "file_name": {"type": "string"},
                "file_size": {"type": "integer"},
                "width": {"type": "integer"},
                "height": {"type": "integer"},
                "color_mode": {"type": "string"},
                "format": {"type": "string"},
                "created_date": {"type": "string"},
                "modified_date": {"type": "string"},
                "message": {"type": "string"}
            }
        },
        examples=[
            {
                "description": "Load a single image",
                "code": "await load_image('path/to/image.jpg')"
            },
            {
                "description": "Load image with options",
                "code": "await load_image('image.jpg', load_metadata=True, max_dimension=4096)"
            }
        ]
    )
    async def load_image(
        self, 
        file_path: str,
        load_metadata: bool = True,
        max_dimension: int = 0
    ) -> Dict[str, Any]:
        """
        Load an image file and return comprehensive metadata.
        
        This method performs the following operations:
        1. Validates the input file path and permissions
        2. Verifies the file format is supported
        3. Loads the image using GIMP's backend
        4. Extracts metadata if requested
        5. Returns a structured response
        
        Args:
            file_path: Path to the image file to load
            load_metadata: Whether to extract and include metadata
            max_dimension: Maximum width/height for loaded images (0 = no limit)
            
        Returns:
            Dictionary containing image metadata and handle
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If file access is denied
            ValueError: For unsupported or invalid image formats
        """
        try:
            # Validate input file
            if not self.validate_file_path(file_path, must_exist=True):
                return self.create_error_response(
                    f"Invalid or inaccessible file path: {file_path}",
                    details={
                        "file_path": file_path,
                        "allowed_directories": self.config.allowed_directories
                    }
                )
            
            # Check file size limit
            path = Path(file_path)
            stat = path.stat()
            
            if hasattr(self.config, 'max_file_size') and stat.st_size > self.config.max_file_size:
                return self.create_error_response(
                    f"File too large: {stat.st_size} bytes (max: {self.config.max_file_size})",
                    details={"file_size": stat.st_size}
                )
            
            # Validate file format
            if not self.cli_wrapper.validate_image_file(file_path):
                return self.create_error_response(
                    f"Unsupported image format or corrupted file: {file_path}",
                    details={
                        "file_path": file_path,
                        "supported_formats": self._supported_formats
                    }
                )
            
            # Load image information using GIMP
            image_info = await self.cli_wrapper.load_image_info(
                file_path,
                load_metadata=load_metadata,
                max_dimension=max_dimension
            )
            
            if not image_info:
                return self.create_error_response(
                    f"Failed to load image information from: {file_path}",
                    details={"file_path": file_path}
                )
            
            # Create comprehensive metadata
            metadata = {
                "file_path": str(path.resolve()),
                "file_name": path.name,
                "file_size": stat.st_size,
                "width": image_info.get("width"),
                "height": image_info.get("height"),
                "color_mode": image_info.get("color_mode", "UNKNOWN"),
                "format": path.suffix.lower().lstrip('.') or image_info.get("format", "unknown"),
                "created_date": self._format_timestamp(stat.st_ctime),
                "modified_date": self._format_timestamp(stat.st_mtime)
            }
            
            # Add metadata if available
            if load_metadata and "metadata" in image_info:
                metadata["metadata"] = image_info["metadata"]
            
            return self.create_success_response(
                data=metadata,
                message=f"Image loaded successfully: {path.name}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to load image {file_path}: {e}", exc_info=True)
            return self.create_error_response(
                f"Failed to load image: {str(e)}",
                details={"file_path": file_path, "error": str(e)}
            )
        
    @tool(
        name="get_image_info",
        description="""
        Extract comprehensive metadata from an image file without fully loading it.
        
        This method provides a lightweight way to retrieve detailed metadata about
        an image file without the overhead of loading the full image data. It's
        particularly useful for getting information about multiple files quickly.
        """,
        parameters={
            "file_path": {
                "type": "string",
                "description": "Path to the image file to analyze",
                "required": True,
                "format": "file"
            },
            "include_metadata": {
                "type": "boolean",
                "description": "Whether to include EXIF/XMP/IPTC metadata (slower)",
                "default": False
            },
            "calculate_hashes": {
                "type": "boolean",
                "description": "Whether to calculate perceptual hashes for the image",
                "default": False
            }
        },
        returns={
            "type": "object",
            "description": "Structured metadata about the image file",
            "properties": {
                "success": {"type": "boolean"},
                "file_info": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "name": {"type": "string"},
                        "extension": {"type": "string"},
                        "size_bytes": {"type": "integer"},
                        "size_mb": {"type": "number"},
                        "created": {"type": "string"},
                        "modified": {"type": "string"}
                    }
                },
                "image_info": {
                    "type": "object",
                    "properties": {
                        "width": {"type": ["integer", "null"]},
                        "height": {"type": ["integer", "null"]},
                        "color_mode": {"type": "string"},
                        "has_transparency": {"type": ["boolean", "null"]},
                        "bit_depth": {"type": ["integer", "string", "null"]}
                    }
                },
                "format_info": {
                    "type": "object",
                    "properties": {
                        "format": {"type": "string"},
                        "supported": {"type": "boolean"},
                        "can_edit": {"type": "boolean"}
                    }
                },
                "message": {"type": "string"}
            }
        },
        examples=[
            {
                "description": "Get basic image info",
                "code": "await get_image_info('path/to/image.jpg')"
            },
            {
                "description": "Get image info with metadata",
                "code": "await get_image_info('image.png', include_metadata=True)"
            },
            {
                "description": "Get image info with perceptual hashes",
                "code": "await get_image_info('photo.jpg', calculate_hashes=True)"
            }
        ]
    )
    async def get_image_info(
        self, 
        file_path: str,
        include_metadata: bool = False,
        calculate_hashes: bool = False
    ) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from an image file without fully loading it.
        
        This method performs the following operations:
        1. Validates the input file path and permissions
        2. Extracts basic file system metadata
        3. Attempts to get image metadata using GIMP (if available)
        4. Optionally includes EXIF/XMP/IPTC metadata
        5. Returns a structured response with all collected information
        
        Args:
            file_path: Path to the image file to analyze
            include_metadata: Whether to include EXIF/XMP/IPTC metadata (slower)
            calculate_hashes: Whether to calculate perceptual hashes for the image
            
        Returns:
            Dictionary containing structured metadata about the image
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If file access is denied
            ValueError: For unsupported or invalid image formats
        """
        try:
            # Validate input file
            if not self.validate_file_path(file_path, must_exist=True):
                return self.create_error_response(
                    f"Invalid or inaccessible file path: {file_path}",
                    details={
                        "file_path": file_path,
                        "allowed_directories": self.config.allowed_directories
                    }
                )
            
            # Get basic file info
            path = Path(file_path)
            stat = path.stat()
            
            # Check file size limit
            if hasattr(self.config, 'max_file_size') and stat.st_size > self.config.max_file_size:
                return self.create_error_response(
                    f"File too large: {stat.st_size} bytes (max: {self.config.max_file_size})",
                    details={"file_size": stat.st_size}
                )
            
            # Initialize result structure
            file_info = {
                "path": str(path.resolve()),
                "name": path.name,
                "extension": path.suffix.lower().lstrip('.'),
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": self._format_timestamp(stat.st_ctime),
                "modified": self._format_timestamp(stat.st_mtime)
            }
            
            # Try to get GIMP metadata (faster than full load)
            gimp_info = {}
            try:
                gimp_info = await self.cli_wrapper.load_image_info(
                    file_path,
                    load_metadata=include_metadata,
                    fast_scan=True
                )
            except Exception as e:
                self.logger.warning(f"Could not get GIMP info for {file_path}: {e}")
            
            # Compile comprehensive metadata
            result = {
                "file_info": file_info,
                "image_info": {
                    "width": gimp_info.get("width"),
                    "height": gimp_info.get("height"),
                    "color_mode": gimp_info.get("color_mode", "UNKNOWN"),
                    "has_transparency": gimp_info.get("has_alpha"),
                    "bit_depth": gimp_info.get("precision")
                },
                "format_info": {
                    "format": path.suffix.lower().lstrip('.') or gimp_info.get("format", "unknown"),
                    "supported": self.config.is_format_supported(path.suffix.lower().lstrip('.')),
                    "can_edit": bool(gimp_info)
                }
            }
            
            # Add metadata if available and requested
            if include_metadata and "metadata" in gimp_info:
                result["metadata"] = gimp_info["metadata"]
            
            # Calculate perceptual hashes if requested
            if calculate_hashes and gimp_info:
                try:
                    hashes = await self.cli_wrapper.calculate_image_hashes(file_path)
                    if hashes:
                        result["image_info"]["hashes"] = hashes
                except Exception as e:
                    self.logger.warning(f"Could not calculate image hashes: {e}")
            
            return self.create_success_response(
                data=result,
                message=f"Image metadata extracted successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get image info for {file_path}: {e}", exc_info=True)
            return self.create_error_response(
                f"Failed to extract image metadata: {str(e)}",
                details={"file_path": file_path, "error": str(e)}
            )
        
    @tool(
        name="save_image",
        description="""
        Save or convert an image to the specified format and location.
        
        This method provides a flexible way to save images in various formats with
        configurable quality settings. It can automatically detect the output format
        from the file extension or use a specified format. The method handles format
        conversion, quality settings, and metadata preservation based on the provided
        parameters and configuration.
        """,
        parameters={
            "input_path": {
                "type": "string",
                "description": "Source image file path",
                "required": True,
                "format": "file"
            },
            "output_path": {
                "type": "string",
                "description": "Destination file path (directory must exist)",
                "required": True,
                "format": "file"
            },
            "format": {
                "type": "string",
                "description": "Output format (e.g., 'jpg', 'png', 'webp'); 'auto' to detect from output_path extension",
                "default": "auto",
                "enum": ["auto"] + SUPPORTED_OUTPUT_FORMATS
            },
            "quality": {
                "type": "integer",
                "description": "Compression quality (1-100) for lossy formats",
                "default": 95,
                "minimum": 1,
                "maximum": 100
            },
            "preserve_metadata": {
                "type": "boolean",
                "description": "Whether to preserve EXIF/XMP/IPTC metadata (if supported by format)",
                "default": True
            },
            "progressive": {
                "type": "boolean",
                "description": "Use progressive encoding (for JPEG/WebP)",
                "default": False
            },
            "overwrite": {
                "type": "boolean",
                "description": "Overwrite output file if it exists",
                "default": False
            }
        },
        returns={
            "type": "object",
            "description": "Operation status and output file information",
            "properties": {
                "success": {"type": "boolean"},
                "input_path": {"type": "string"},
                "output_path": {"type": "string"},
                "output_format": {"type": "string"},
                "output_size_bytes": {"type": "integer"},
                "output_size_mb": {"type": "number"},
                "quality_used": {"type": ["integer", "null"]},
                "metadata_preserved": {"type": "boolean"},
                "message": {"type": "string"}
            }
        },
        examples=[
            {
                "description": "Save as JPEG with default quality",
                "code": "await save_image('input.png', 'output.jpg')"
            },
            {
                "description": "Save as WebP with custom quality",
                "code": "await save_image('input.jpg', 'output.webp', quality=80)"
            },
            {
                "description": "Save with format auto-detection",
                "code": "await save_image('input.tiff', 'output.png')"
            }
        ]
    )
    async def save_image(
        self,
        input_path: str,
        output_path: str,
        format: str = "auto",
        quality: int = 95,
        preserve_metadata: bool = True,
        progressive: bool = False,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Save or convert an image to the specified format and location.
        
        This method performs the following operations:
        1. Validates input and output file paths
        2. Determines the output format (auto-detected or specified)
        3. Validates format support and parameters
        4. Performs the conversion using GIMP's backend
        5. Handles metadata preservation if requested
        6. Returns detailed information about the saved file
        
        Args:
            input_path: Path to the source image file
            output_path: Path where the output image will be saved
            format: Output format ('auto' to detect from output_path extension)
            quality: Compression quality (1-100) for lossy formats
            preserve_metadata: Whether to preserve image metadata (EXIF, XMP, etc.)
            progressive: Use progressive encoding for JPEG/WebP
            overwrite: Overwrite output file if it exists
            
        Returns:
            Dictionary containing operation status and file information:
            - success: Boolean indicating if the operation succeeded
            - input_path: Original input file path
            - output_path: Path where the file was saved
            - output_format: Actual output format used
            - output_size_bytes: Size of the output file in bytes
            - output_size_mb: Size of the output file in megabytes
            - quality_used: Quality setting used (if applicable)
            - metadata_preserved: Whether metadata was preserved
            - message: Human-readable status message
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            PermissionError: If output directory is not writable
            ValueError: For invalid parameters or unsupported formats
            RuntimeError: If the conversion fails
        """
        try:
            # Validate input file
            if not self.validate_file_path(input_path, must_exist=True):
                return self.create_error_response(f"Invalid input file path: {input_path}")
            
            # Validate output path
            if not self.validate_file_path(output_path, must_exist=False):
                return self.create_error_response(f"Invalid output file path: {output_path}")
            
            # Check if output file exists and handle overwrite
            output_path_obj = Path(output_path)
            if output_path_obj.exists() and not overwrite:
                return self.create_error_response(
                    f"Output file already exists and overwrite is False: {output_path}",
                    details={"output_path": str(output_path_obj.resolve())}
                )
            
            # Determine output format
            if format == "auto":
                target_format = output_path_obj.suffix.lower().lstrip('.')
                if not target_format:
                    return self.create_error_response(
                        "Could not determine output format from file extension",
                        details={"output_path": str(output_path_obj)}
                    )
            else:
                target_format = format.lower()
            
            # Validate format support
            if not self.config.is_format_supported(target_format):
                return self.create_error_response(
                    f"Unsupported output format: {target_format}",
                    details={
                        "supported_formats": self._supported_formats['raster'] + self._supported_formats['vector'],
                        "requested_format": target_format
                    }
                )
            
            # Validate quality parameter
            if not (1 <= quality <= 100):
                return self.create_error_response(
                    "Quality must be between 1 and 100",
                    details={"provided_quality": quality}
                )
            
            # Ensure output directory exists
            output_dir = output_path_obj.parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Perform conversion using GIMP
            success = await self.cli_wrapper.convert_image(
                input_path=input_path,
                output_path=str(output_path_obj),
                output_format=target_format,
                quality=quality,
                preserve_metadata=preserve_metadata,
                progressive=progressive
            )
            
            if not success:
                return self.create_error_response(
                    "Image conversion failed",
                    details={
                        "input_path": input_path,
                        "output_path": str(output_path_obj),
                        "format": target_format
                    }
                )
            
            # Verify output file was created
            if not output_path_obj.exists():
                return self.create_error_response(
                    "Output file was not created",
                    details={"output_path": str(output_path_obj.resolve())}
                )
            
            # Get output file info
            output_stat = output_path_obj.stat()
            
            result_data = {
                "input_path": input_path,
                "output_path": str(output_path_obj.resolve()),
                "output_format": target_format,
                "output_size_bytes": output_stat.st_size,
                "output_size_mb": round(output_stat.st_size / (1024 * 1024), 2),
                "quality_used": quality if target_format in ["jpeg", "jpg", "webp"] else None,
                "metadata_preserved": preserve_metadata and target_format in ["jpeg", "jpg", "tiff", "tif", "png", "webp"],
                "progressive": progressive if target_format in ["jpeg", "jpg", "webp"] else None
            }
            
            return self.create_success_response(
                data=result_data,
                message=f"Image saved successfully to {output_path_obj.name}"
            )
            
        except Exception as e:
            self.logger.error(
                f"Failed to save image from {input_path} to {output_path}: {e}",
                exc_info=True
            )
            return self.create_error_response(
                f"Failed to save image: {str(e)}",
                details={
                    "input_path": input_path,
                    "output_path": output_path,
                    "error": str(e)
                }
            )
        
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
