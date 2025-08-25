"""
Transform Tools for GIMP MCP Server.

Provides geometric transformation operations including resize, crop, rotate,
and other spatial manipulations.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from fastmcp import FastMCP

from .base import BaseToolCategory

logger = logging.getLogger(__name__)

class TransformTools(BaseToolCategory):
    """
    Geometric transformation tools for image manipulation.
    """
    
    def register_tools(self, app: FastMCP) -> None:
        """Register transform tools with FastMCP."""
        
        @app.tool()
        async def resize_image(input_path: str,
                             output_path: str,
                             width: int,
                             height: int,
                             maintain_aspect: bool = True,
                             interpolation: str = "auto") -> Dict[str, Any]:
            """
            Resize an image to specified dimensions.
            
            Args:
                input_path: Source image file path
                output_path: Destination file path
                width: Target width in pixels
                height: Target height in pixels
                maintain_aspect: Whether to maintain aspect ratio
                interpolation: Interpolation method (auto, none, linear, cubic, lanczos)
                
            Returns:
                Dict containing resize operation results
            """
            try:
                # Validate inputs
                if not self.validate_file_path(input_path, must_exist=True):
                    return self.create_error_response(f"Invalid input file: {input_path}")
                
                if not self.validate_file_path(output_path, must_exist=False):
                    return self.create_error_response(f"Invalid output path: {output_path}")
                
                # Validate dimensions
                if width <= 0 or height <= 0:
                    return self.create_error_response("Width and height must be positive integers")
                
                if width > 10000 or height > 10000:
                    return self.create_error_response("Maximum dimensions are 10000x10000 pixels")
                
                # Set interpolation method
                if interpolation == "auto":
                    interpolation = self.config.default_interpolation
                
                # Get original image info for comparison
                original_info = await self.cli_wrapper.load_image_info(input_path)
                original_width = original_info.get("width", 0)
                original_height = original_info.get("height", 0)
                
                # Calculate actual dimensions if maintaining aspect ratio
                if maintain_aspect and original_width > 0 and original_height > 0:
                    aspect_ratio = original_width / original_height
                    
                    # Calculate dimensions that fit within the specified bounds
                    if width / height > aspect_ratio:
                        # Height is the limiting dimension
                        actual_width = int(height * aspect_ratio)
                        actual_height = height
                    else:
                        # Width is the limiting dimension
                        actual_width = width
                        actual_height = int(width / aspect_ratio)
                else:
                    actual_width = width
                    actual_height = height
                
                # Perform resize using GIMP
                success = await self.cli_wrapper.resize_image(
                    input_path=input_path,
                    output_path=output_path,
                    width=actual_width,
                    height=actual_height,
                    maintain_aspect=maintain_aspect
                )
                
                if not success:
                    return self.create_error_response("Image resize operation failed")
                
                # Get output file info
                output_path_obj = Path(output_path)
                output_stat = output_path_obj.stat()
                
                resize_data = {
                    "original_dimensions": {
                        "width": original_width,
                        "height": original_height
                    },
                    "target_dimensions": {
                        "width": width,
                        "height": height
                    },
                    "actual_dimensions": {
                        "width": actual_width,
                        "height": actual_height
                    },
                    "settings": {
                        "maintain_aspect_ratio": maintain_aspect,
                        "interpolation": interpolation
                    },
                    "output": {
                        "path": str(output_path_obj.resolve()),
                        "size_bytes": output_stat.st_size
                    }
                }
                
                return self.create_success_response(
                    data=resize_data,
                    message=f"Image resized to {actual_width}x{actual_height} pixels"
                )
                
            except Exception as e:
                self.logger.error(f"Resize operation failed for {input_path}: {e}")
                return self.create_error_response(f"Resize operation failed: {str(e)}")
        
        @app.tool()
        async def crop_image(input_path: str,
                           output_path: str,
                           x: int,
                           y: int,
                           width: int,
                           height: int) -> Dict[str, Any]:
            """
            Crop an image to the specified rectangular region.
            
            Args:
                input_path: Source image file path
                output_path: Destination file path
                x: Left edge of crop rectangle (pixels from left)
                y: Top edge of crop rectangle (pixels from top)
                width: Width of crop rectangle in pixels
                height: Height of crop rectangle in pixels
                
            Returns:
                Dict containing crop operation results
            """
            try:
                # Validate inputs
                if not self.validate_file_path(input_path, must_exist=True):
                    return self.create_error_response(f"Invalid input file: {input_path}")
                
                if not self.validate_file_path(output_path, must_exist=False):
                    return self.create_error_response(f"Invalid output path: {output_path}")
                
                # Validate crop parameters
                if x < 0 or y < 0:
                    return self.create_error_response("Crop coordinates must be non-negative")
                
                if width <= 0 or height <= 0:
                    return self.create_error_response("Crop dimensions must be positive")
                
                # Get original image dimensions to validate crop area
                original_info = await self.cli_wrapper.load_image_info(input_path)
                original_width = original_info.get("width", 0)
                original_height = original_info.get("height", 0)
                
                if original_width == 0 or original_height == 0:
                    return self.create_error_response("Could not determine original image dimensions")
                
                # Validate crop area is within image bounds
                if x + width > original_width:
                    return self.create_error_response(f"Crop area extends beyond image width ({original_width}px)")
                
                if y + height > original_height:
                    return self.create_error_response(f"Crop area extends beyond image height ({original_height}px)")
                
                # Build GIMP Script-Fu for cropping
                input_abs = str(Path(input_path).resolve())
                output_abs = str(Path(output_path).resolve())
                
                # Ensure output directory exists
                Path(output_abs).parent.mkdir(parents=True, exist_ok=True)
                
                crop_script = f"""
(let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{input_abs}" "{input_abs}")))
       (drawable (car (gimp-image-get-active-layer image))))
  (gimp-image-crop image {width} {height} {x} {y})
  (gimp-file-save RUN-NONINTERACTIVE image drawable "{output_abs}" "{output_abs}")
  (gimp-image-delete image)
  (gimp-message "CROP:SUCCESS"))
"""
                
                # Execute crop operation
                output = await self.cli_wrapper.execute_script_fu(crop_script)
                
                if "CROP:SUCCESS" not in output:
                    return self.create_error_response("Crop operation failed")
                
                # Get output file info
                output_path_obj = Path(output_path)
                output_stat = output_path_obj.stat()
                
                crop_data = {
                    "original_dimensions": {
                        "width": original_width,
                        "height": original_height
                    },
                    "crop_region": {
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height
                    },
                    "cropped_dimensions": {
                        "width": width,
                        "height": height
                    },
                    "output": {
                        "path": str(output_path_obj.resolve()),
                        "size_bytes": output_stat.st_size
                    }
                }
                
                return self.create_success_response(
                    data=crop_data,
                    message=f"Image cropped to {width}x{height} pixels"
                )
                
            except Exception as e:
                self.logger.error(f"Crop operation failed for {input_path}: {e}")
                return self.create_error_response(f"Crop operation failed: {str(e)}")
        
        @app.tool()
        async def rotate_image(input_path: str,
                             output_path: str,
                             degrees: float,
                             fill_color: str = "transparent") -> Dict[str, Any]:
            """
            Rotate an image by the specified angle.
            
            Args:
                input_path: Source image file path
                output_path: Destination file path
                degrees: Rotation angle in degrees (positive = clockwise)
                fill_color: Background fill color (transparent, white, black)
                
            Returns:
                Dict containing rotation operation results
            """
            try:
                # Validate inputs
                if not self.validate_file_path(input_path, must_exist=True):
                    return self.create_error_response(f"Invalid input file: {input_path}")
                
                if not self.validate_file_path(output_path, must_exist=False):
                    return self.create_error_response(f"Invalid output path: {output_path}")
                
                # Normalize rotation angle
                degrees = degrees % 360
                
                # Validate fill color
                valid_colors = ["transparent", "white", "black"]
                if fill_color not in valid_colors:
                    return self.create_error_response(f"Invalid fill color. Use: {valid_colors}")
                
                # Get original image info
                original_info = await self.cli_wrapper.load_image_info(input_path)
                original_width = original_info.get("width", 0)
                original_height = original_info.get("height", 0)
                
                if original_width == 0 or original_height == 0:
                    return self.create_error_response("Could not determine original image dimensions")
                
                # Build GIMP Script-Fu for rotation
                input_abs = str(Path(input_path).resolve())
                output_abs = str(Path(output_path).resolve())
                
                # Ensure output directory exists
                Path(output_abs).parent.mkdir(parents=True, exist_ok=True)
                
                # Convert degrees to radians for GIMP
                radians = degrees * 3.14159 / 180
                
                # Set background color based on fill_color
                if fill_color == "white":
                    bg_color = '(255 255 255)'
                elif fill_color == "black":
                    bg_color = '(0 0 0)'
                else:  # transparent
                    bg_color = '(255 255 255)'  # Will be made transparent
                
                rotate_script = f"""
(let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{input_abs}" "{input_abs}")))
       (drawable (car (gimp-image-get-active-layer image))))
  (gimp-context-set-background {bg_color})
  (gimp-item-transform-rotate drawable {radians} TRUE 0 0)
  (gimp-file-save RUN-NONINTERACTIVE image drawable "{output_abs}" "{output_abs}")
  (gimp-image-delete image)
  (gimp-message "ROTATE:SUCCESS"))
"""
                
                # Execute rotation
                output = await self.cli_wrapper.execute_script_fu(rotate_script)
                
                if "ROTATE:SUCCESS" not in output:
                    return self.create_error_response("Rotation operation failed")
                
                # Get output file info
                output_path_obj = Path(output_path)
                output_stat = output_path_obj.stat()
                
                rotate_data = {
                    "original_dimensions": {
                        "width": original_width,
                        "height": original_height
                    },
                    "rotation": {
                        "degrees": degrees,
                        "fill_color": fill_color
                    },
                    "output": {
                        "path": str(output_path_obj.resolve()),
                        "size_bytes": output_stat.st_size
                    }
                }
                
                return self.create_success_response(
                    data=rotate_data,
                    message=f"Image rotated by {degrees} degrees"
                )
                
            except Exception as e:
                self.logger.error(f"Rotation operation failed for {input_path}: {e}")
                return self.create_error_response(f"Rotation operation failed: {str(e)}")
        
        @app.tool()
        async def flip_image(input_path: str,
                           output_path: str,
                           direction: str) -> Dict[str, Any]:
            """
            Flip an image horizontally or vertically.
            
            Args:
                input_path: Source image file path
                output_path: Destination file path
                direction: Flip direction ("horizontal" or "vertical")
                
            Returns:
                Dict containing flip operation results
            """
            try:
                # Validate inputs
                if not self.validate_file_path(input_path, must_exist=True):
                    return self.create_error_response(f"Invalid input file: {input_path}")
                
                if not self.validate_file_path(output_path, must_exist=False):
                    return self.create_error_response(f"Invalid output path: {output_path}")
                
                # Validate direction
                if direction.lower() not in ["horizontal", "vertical"]:
                    return self.create_error_response("Direction must be 'horizontal' or 'vertical'")
                
                # Build GIMP Script-Fu for flipping
                input_abs = str(Path(input_path).resolve())
                output_abs = str(Path(output_path).resolve())
                
                # Ensure output directory exists
                Path(output_abs).parent.mkdir(parents=True, exist_ok=True)
                
                # Set flip type based on direction
                flip_type = "ORIENTATION-HORIZONTAL" if direction.lower() == "horizontal" else "ORIENTATION-VERTICAL"
                
                flip_script = f"""
(let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{input_abs}" "{input_abs}")))
       (drawable (car (gimp-image-get-active-layer image))))
  (gimp-item-transform-flip-simple drawable {flip_type} TRUE 0)
  (gimp-file-save RUN-NONINTERACTIVE image drawable "{output_abs}" "{output_abs}")
  (gimp-image-delete image)
  (gimp-message "FLIP:SUCCESS"))
"""
                
                # Execute flip operation
                output = await self.cli_wrapper.execute_script_fu(flip_script)
                
                if "FLIP:SUCCESS" not in output:
                    return self.create_error_response("Flip operation failed")
                
                # Get output file info
                output_path_obj = Path(output_path)
                output_stat = output_path_obj.stat()
                
                flip_data = {
                    "operation": {
                        "type": "flip",
                        "direction": direction.lower()
                    },
                    "output": {
                        "path": str(output_path_obj.resolve()),
                        "size_bytes": output_stat.st_size
                    }
                }
                
                return self.create_success_response(
                    data=flip_data,
                    message=f"Image flipped {direction.lower()}"
                )
                
            except Exception as e:
                self.logger.error(f"Flip operation failed for {input_path}: {e}")
                return self.create_error_response(f"Flip operation failed: {str(e)}")
