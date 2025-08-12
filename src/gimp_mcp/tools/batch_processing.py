"""
Batch Processing Tools for GIMP MCP Server.

Provides bulk operation capabilities for processing multiple images
with the same operations efficiently.
"""

import asyncio
import glob
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from .base import BaseToolCategory

logger = logging.getLogger(__name__)

class BatchProcessingTools(BaseToolCategory):
    """
    Batch processing tools for bulk operations.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._supported_formats = {
            'jpg', 'jpeg', 'png', 'tif', 'tiff', 'bmp', 'gif', 'webp', 'xcf'
        }
    
    def _get_supported_files(self, directory: str, pattern: str = "*") -> List[str]:
        """Get list of supported image files matching pattern."""
        path = Path(directory) / pattern
        files = []
        
        for ext in self._supported_formats:
            files.extend(glob.glob(f"{path}.{ext}", recursive=True))
            files.extend(glob.glob(f"{path}.{ext.upper()}", recursive=True))
        
        return sorted(list(set(files)))
    
    def _ensure_output_dir(self, path: str) -> None:
        """Ensure output directory exists."""
        os.makedirs(path, exist_ok=True)
    
    async def _process_batch_operation(self, 
                                     input_files: List[str], 
                                     output_dir: str, 
                                     operation_name: str,
                                     operation_func,
                                     **operation_kwargs) -> Dict[str, Any]:
        """
        Process a batch operation on multiple files.
        
        Args:
            input_files: List of input file paths
            output_dir: Output directory for processed files
            operation_name: Name of the operation for logging
            operation_func: Async function to call for each file
            **operation_kwargs: Additional arguments to pass to operation_func
            
        Returns:
            Dict with operation results
        """
        if not input_files:
            return self.create_error_response("No matching files found")
        
        self._ensure_output_dir(output_dir)
        processed = []
        failed = []
        
        for input_file in input_files:
            try:
                # Create output path
                input_path = Path(input_file)
                output_path = Path(output_dir) / input_path.name
                
                # Process the file
                result = await operation_func(
                    input_path=str(input_path),
                    output_path=str(output_path),
                    **operation_kwargs
                )
                
                if result.get('success', False):
                    processed.append(str(input_path))
                else:
                    failed.append({
                        'file': str(input_path),
                        'error': result.get('message', 'Unknown error')
                    })
                    
            except Exception as e:
                error_msg = f"Error processing {input_file}: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                failed.append({
                    'file': str(input_file),
                    'error': str(e)
                })
        
        # Prepare response
        response = {
            'operation': operation_name,
            'total_files': len(input_files),
            'processed': len(processed),
            'failed': len(failed),
            'processed_files': processed,
            'failed_files': failed
        }
        
        if failed:
            return self.create_partial_success_response(
                data=response,
                message=f"Completed with {len(failed)} failures"
            )
        
        return self.create_success_response(
            data=response,
            message=f"Successfully processed {len(processed)} files"
        )
    
    def register_tools(self, app: FastMCP) -> None:
        """Register batch processing tools with FastMCP."""
        
        @app.tool()
        async def batch_resize(input_pattern: str,
                             output_directory: str,
                             width: int,
                             height: int,
                             maintain_aspect: bool = True,
                             interpolation: str = "auto") -> Dict[str, Any]:
            """
            Resize multiple images matching a pattern.
            
            Args:
                input_pattern: File pattern to match (e.g., "*.jpg", "/path/to/images/*")
                output_directory: Directory to save resized images
                width: Target width in pixels
                height: Target height in pixels
                maintain_aspect: Whether to maintain aspect ratio
                interpolation: Interpolation method (auto, none, linear, cubic, lanczos)
                
            Returns:
                Dict containing batch operation results
            """
            try:
                # Validate parameters
                if width <= 0 or height <= 0:
                    return self.create_error_response("Width and height must be positive integers")
                
                # Get matching files
                input_dir = os.path.dirname(input_pattern) or "."
                file_pattern = os.path.basename(input_pattern) or "*"
                input_files = self._get_supported_files(input_dir, file_pattern)
                
                if not input_files:
                    return self.create_error_response("No matching image files found")
                
                # Process each file
                return await self._process_batch_operation(
                    input_files=input_files,
                    output_dir=output_directory,
                    operation_name="batch_resize",
                    operation_func=self.cli_wrapper.resize_image,
                    width=width,
                    height=height,
                    maintain_aspect=maintain_aspect,
                    interpolation=interpolation
                )
                
            except Exception as e:
                self.logger.error(f"Batch resize operation failed: {e}", exc_info=True)
                return self.create_error_response(f"Batch resize failed: {str(e)}")
        
        @app.tool()
        async def batch_convert(input_pattern: str,
                              output_directory: str,
                              output_format: str,
                              quality: int = 90) -> Dict[str, Any]:
            """
            Convert multiple images to a different format.
            
            Args:
                input_pattern: File pattern to match (e.g., "*.png", "/path/to/images/*")
                output_directory: Directory to save converted images
                output_format: Target format (jpg, png, webp, etc.)
                quality: Output quality (1-100) for lossy formats
                
            Returns:
                Dict containing batch operation results
            """
            try:
                # Validate parameters
                output_format = output_format.lower()
                if output_format not in self._supported_formats:
                    return self.create_error_response(
                        f"Unsupported output format. Supported formats: {', '.join(self._supported_formats)}"
                    )
                
                if not 1 <= quality <= 100:
                    return self.create_error_response("Quality must be between 1 and 100")
                
                # Get matching files
                input_dir = os.path.dirname(input_pattern) or "."
                file_pattern = os.path.basename(input_pattern) or "*"
                input_files = self._get_supported_files(input_dir, file_pattern)
                
                if not input_files:
                    return self.create_error_response("No matching image files found")
                
                # Process each file
                results = []
                processed = 0
                failed = 0
                
                for input_file in input_files:
                    try:
                        # Create output path with new extension
                        input_path = Path(input_file)
                        output_path = Path(output_directory) / f"{input_path.stem}.{output_format}"
                        
                        # Convert the file
                        success = await self.cli_wrapper.convert_image(
                            input_path=str(input_path),
                            output_path=str(output_path),
                            quality=quality
                        )
                        
                        if success:
                            results.append({
                                'input': str(input_path),
                                'output': str(output_path),
                                'success': True
                            })
                            processed += 1
                        else:
                            results.append({
                                'input': str(input_path),
                                'error': 'Conversion failed',
                                'success': False
                            })
                            failed += 1
                            
                    except Exception as e:
                        self.logger.error(f"Error converting {input_file}: {e}", exc_info=True)
                        results.append({
                            'input': str(input_file),
                            'error': str(e),
                            'success': False
                        })
                        failed += 1
                
                # Prepare response
                response = {
                    'operation': 'batch_convert',
                    'output_format': output_format,
                    'total_files': len(input_files),
                    'processed': processed,
                    'failed': failed,
                    'results': results
                }
                
                if failed > 0:
                    return self.create_partial_success_response(
                        data=response,
                        message=f"Completed with {failed} failures"
                    )
                
                return self.create_success_response(
                    data=response,
                    message=f"Successfully converted {processed} files to {output_format}"
                )
                
            except Exception as e:
                self.logger.error(f"Batch convert operation failed: {e}", exc_info=True)
                return self.create_error_response(f"Batch convert failed: {str(e)}")
        
        @app.tool()
        async def batch_apply_filter(input_pattern: str,
                                   output_directory: str,
                                   filter_name: str,
                                   **filter_params) -> Dict[str, Any]:
            """
            Apply a filter to multiple images.
            
            Args:
                input_pattern: File pattern to match (e.g., "*.jpg", "/path/to/images/*")
                output_directory: Directory to save filtered images
                filter_name: Name of the filter to apply
                **filter_params: Additional parameters specific to the filter
                
            Returns:
                Dict containing batch operation results
            """
            try:
                # Get matching files
                input_dir = os.path.dirname(input_pattern) or "."
                file_pattern = os.path.basename(input_pattern) or "*"
                input_files = self._get_supported_files(input_dir, file_pattern)
                
                if not input_files:
                    return self.create_error_response("No matching image files found")
                
                # Process each file
                results = []
                processed = 0
                failed = 0
                
                for input_file in input_files:
                    try:
                        # Create output path
                        input_path = Path(input_file)
                        output_path = Path(output_directory) / input_path.name
                        
                        # Apply the filter
                        result = await self.cli_wrapper.apply_filter(
                            input_path=str(input_path),
                            output_path=str(output_path),
                            filter_name=filter_name,
                            **filter_params
                        )
                        
                        if result.get('success', False):
                            results.append({
                                'input': str(input_path),
                                'output': str(output_path),
                                'success': True
                            })
                            processed += 1
                        else:
                            error = result.get('message', 'Filter application failed')
                            results.append({
                                'input': str(input_path),
                                'error': error,
                                'success': False
                            })
                            failed += 1
                            
                    except Exception as e:
                        self.logger.error(f"Error applying filter to {input_file}: {e}", exc_info=True)
                        results.append({
                            'input': str(input_file),
                            'error': str(e),
                            'success': False
                        })
                        failed += 1
                
                # Prepare response
                response = {
                    'operation': 'batch_apply_filter',
                    'filter': filter_name,
                    'parameters': filter_params,
                    'total_files': len(input_files),
                    'processed': processed,
                    'failed': failed,
                    'results': results
                }
                
                if failed > 0:
                    return self.create_partial_success_response(
                        data=response,
                        message=f"Completed with {failed} failures"
                    )
                
                return self.create_success_response(
                    data=response,
                    message=f"Successfully applied {filter_name} to {processed} files"
                )
                
            except Exception as e:
                self.logger.error(f"Batch filter operation failed: {e}", exc_info=True)
                return self.create_error_response(f"Batch filter failed: {str(e)}")
