from __future__ import annotations

"""
Help Tools for GIMP MCP Server.

Provides documentation and help information about the GIMP MCP tools
at different technical levels for users, developers, and AI systems.
"""

import logging
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any, Dict, List, Literal, Optional, Type, TypedDict, Union, 
    get_type_hints, cast
)

from fastmcp import FastMCP

from .base import BaseToolCategory

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

logger = logging.getLogger(__name__)

# Type aliases
HelpLevel = Literal["basic", "intermediate", "advanced"]
ToolName: TypeAlias = str
CategoryName: TypeAlias = str
HelpContent: TypeAlias = Dict[HelpLevel, str]

class HelpSection(TypedDict):
    """Structure for help documentation sections."""
    basic: str
    intermediate: str
    advanced: str
    examples: List[Dict[str, str]]
    parameters: Dict[str, Dict[str, Any]]

@dataclass
class ToolDocumentation:
    """Complete documentation for a tool."""
    name: str
    description: str
    category: str
    help_levels: HelpContent
    examples: List[Dict[str, str]] = field(default_factory=list)
    parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "help_levels": self.help_levels,
            "examples": self.examples,
            "parameters": self.parameters
        }

class HelpTools(BaseToolCategory):
    """
    Help system for GIMP MCP tools.
    
    Provides documentation and usage examples for all tools at different
    technical levels (basic, intermediate, advanced).
    """
    
    def __init__(self, cli_wrapper, config, tool_categories):
        """
        Initialize help tools with references to other tool categories.
        
        Args:
            cli_wrapper: GIMP CLI wrapper instance
            config: Server configuration
            tool_categories: Dictionary of all tool categories
        """
        super().__init__(cli_wrapper, config)
        self.tool_categories = tool_categories
        self._help_data = self._initialize_help_data()
    
    def _initialize_help_data(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the help documentation structure."""
        return {
            "overview": {
                "basic": "GIMP MCP Server provides professional image editing capabilities through Claude AI. "
                        "You can edit images using natural language commands.",
                "intermediate": "The GIMP MCP Server exposes GIMP's powerful image editing capabilities "
                              "through a structured API. It supports common operations like resizing, "
                              "cropping, color adjustments, and filters.",
                "advanced": "The GIMP MCP Server is built on FastMCP and provides a programmatic interface to "
                          "GIMP's functionality. It uses GIMP's batch mode and Script-Fu for operations, "
                          "with proper error handling and resource management."
            },
            "categories": {
                "file_operations": {
                    "description": "Operations for loading, saving, and converting image files.",
                    "tools": {
                        "load_image": {
                            "description": "Load an image file into the editor.",
                            "parameters": {
                                "file_path": "Path to the image file to load"
                            },
                            "example": "Load the image at 'path/to/image.jpg'"
                        },
                        "save_image": {
                            "description": "Save the current image to a file.",
                            "parameters": {
                                "output_path": "Path where to save the image",
                                "format": "(Optional) Output format (jpg, png, etc.)"
                            },
                            "example": "Save the image as 'output.png'"
                        }
                    }
                },
                "transforms": {
                    "description": "Geometric transformations for images.",
                    "tools": {
                        "resize_image": {
                            "description": "Resize the current image.",
                            "parameters": {
                                "width": "New width in pixels",
                                "height": "New height in pixels",
                                "maintain_aspect_ratio": "(Optional) Whether to maintain aspect ratio"
                            },
                            "example": "Resize the image to 800x600 pixels"
                        },
                        "crop_image": {
                            "description": "Crop the current image.",
                            "parameters": {
                                "x": "X coordinate of top-left corner",
                                "y": "Y coordinate of top-left corner",
                                "width": "Width of the crop area",
                                "height": "Height of the crop area"
                            },
                            "example": "Crop the image to a 500x500 square starting at (100,100)"
                        }
                    }
                },
                "color_adjustments": {
                    "description": "Color manipulation tools.",
                    "tools": {
                        "adjust_brightness_contrast": {
                            "description": "Adjust image brightness and contrast.",
                            "parameters": {
                                "brightness": "Brightness adjustment (-100 to 100)",
                                "contrast": "Contrast adjustment (-100 to 100)"
                            },
                            "example": "Increase brightness by 20 and contrast by 10"
                        }
                    }
                },
                "filters": {
                    "description": "Image filters and effects.",
                    "tools": {
                        "apply_blur": {
                            "description": "Apply a blur effect to the image.",
                            "parameters": {
                                "blur_type": "Type of blur (gaussian, motion, etc.)",
                                "radius": "Blur radius in pixels"
                            },
                            "example": "Apply a gaussian blur with 5px radius"
                        }
                    }
                },
                "batch_processing": {
                    "description": "Process multiple images at once.",
                    "tools": {
                        "batch_resize": {
                            "description": "Resize multiple images to the same dimensions.",
                            "parameters": {
                                "input_dir": "Directory containing images to process",
                                "output_dir": "Directory to save processed images",
                                "width": "Target width in pixels",
                                "height": "Target height in pixels"
                            },
                            "example": "Resize all images in 'input' to 800x600 and save to 'output'"
                        },
                        "batch_convert": {
                            "description": "Convert multiple images to a different format.",
                            "parameters": {
                                "input_dir": "Directory containing images to convert",
                                "output_dir": "Directory to save converted images",
                                "output_format": "Target format (jpg, png, etc.)"
                            },
                            "example": "Convert all PNGs in 'input' to JPG in 'output'"
                        }
                    }
                }
            },
            "examples": {
                "basic": [
                    "Load an image: 'Load the image from path/to/image.jpg'",
                    "Resize an image: 'Resize the image to 800x600 pixels'",
                    "Apply a filter: 'Apply a gaussian blur with radius 5'",
                    "Save the image: 'Save the image as output.jpg'"
                ],
                "intermediate": [
                    "Batch processing: 'Resize all images in the input folder to 1024x768'",
                    "Color correction: 'Adjust brightness by +20 and contrast by +10'",
                    "Advanced filters: 'Apply unsharp mask with radius 1.0, amount 0.8, threshold 0'"
                ],
                "advanced": [
                    "Using the API directly: 'await client.tools.file_operations.load_image(file_path=...)'",
                    "Chaining operations: 'Load, resize, apply filter, and save in one operation'",
                    "Custom scripts: 'Execute custom GIMP Script-Fu commands"
                ]
            }
        }
    
    def register_tools(self, app: FastMCP) -> None:
        """Register help tools with FastMCP."""
        
        @app.tool()
        async def get_help(
            topic: str = "overview", 
            level: str = "basic",
            tool_name: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Get help documentation for GIMP MCP tools.
            
            Args:
                topic: Help topic (overview, categories, examples, or category name)
                level: Detail level (basic, intermediate, advanced)
                tool_name: Specific tool to get help for (optional)
                
            Returns:
                Help content in a structured format
            """
            try:
                # Validate level
                level = level.lower()
                if level not in ["basic", "intermediate", "advanced"]:
                    return self.create_error_response(
                        "Invalid help level. Must be 'basic', 'intermediate', or 'advanced'"
                    )
                
                # Handle different help topics
                topic = topic.lower()
                if topic == "overview":
                    return self.create_success_response({
                        "topic": "overview",
                        "level": level,
                        "content": self._help_data["overview"][level]
                    })
                
                elif topic == "categories":
                    # Return all categories
                    categories = {
                        cat: {"description": info["description"]} 
                        for cat, info in self._help_data["categories"].items()
                    }
                    return self.create_success_response({
                        "topic": "categories",
                        "level": level,
                        "content": categories
                    })
                
                elif topic == "examples":
                    return self.create_success_response({
                        "topic": "examples",
                        "level": level,
                        "content": self._help_data["examples"][level]
                    })
                
                elif topic in self._help_data["categories"]:
                    # Return help for a specific category
                    category = self._help_data["categories"][topic]
                    
                    if tool_name:
                        # Return help for a specific tool in the category
                        if tool_name in category["tools"]:
                            return self.create_success_response({
                                "topic": f"{topic}.{tool_name}",
                                "level": level,
                                "content": category["tools"][tool_name]
                            })
                        else:
                            return self.create_error_response(
                                f"Tool '{tool_name}' not found in category '{topic}'"
                            )
                    else:
                        # Return all tools in the category
                        return self.create_success_response({
                            "topic": topic,
                            "level": level,
                            "description": category["description"],
                            "tools": list(category["tools"].keys())
                        })
                
                else:
                    return self.create_error_response(
                        f"Unknown help topic: {topic}. Try 'overview', 'categories', or a category name."
                    )
            
            except Exception as e:
                logger.error(f"Error in help system: {e}", exc_info=True)
                return self.create_error_response("An error occurred while fetching help")
        
        @app.tool()
        async def list_tools() -> Dict[str, Any]:
            """
            List all available tools in the GIMP MCP server.
            
            Returns:
                Dictionary mapping category names to lists of tool names
            """
            try:
                tools = {}
                for category_name, category in self._help_data["categories"].items():
                    tools[category_name] = {
                        "description": category["description"],
                        "tools": list(category["tools"].keys())
                    }
                
                return self.create_success_response({
                    "tools": tools,
                    "count": sum(len(cat["tools"]) for cat in self._help_data["categories"].values())
                })
            
            except Exception as e:
                logger.error(f"Error listing tools: {e}", exc_info=True)
                return self.create_error_response("Failed to list tools")
