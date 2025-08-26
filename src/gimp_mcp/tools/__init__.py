from __future__ import annotations

"""
GIMP MCP Tools Package.

This package contains all the tool categories for the GIMP MCP server,
providing comprehensive image editing capabilities through GIMP integration.
"""

import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import (
    Any, Dict, List, Optional, Type, TypeVar, Union, 
    get_type_hints, get_args, get_origin
)

# Import tool categories with conditional imports
try:
    from .base import BaseToolCategory
    from .file_operations import FileOperationTools
    from .transforms import TransformTools
    from .color_adjustments import ColorAdjustmentTools
    from .filters import FilterTools
    from .batch_processing import BatchProcessingTools
    from .help_tools import HelpTools
    from .layer_management import LayerManagementTools
    from .image_analysis import ImageAnalysisTools
    from .performance_tools import PerformanceTools
    
    # Type variable for tool categories
    ToolCategoryT = TypeVar('ToolCategoryT', bound=BaseToolCategory)
    
    # List of all tool categories
    ALL_TOOL_CATEGORIES = [
        FileOperationTools,
        TransformTools,
        ColorAdjustmentTools,
        FilterTools,
        BatchProcessingTools,
        HelpTools,
        LayerManagementTools,
        ImageAnalysisTools,
        PerformanceTools
    ]
    
    # Check for missing implementations
    MISSING_IMPLEMENTATIONS = False
    
except ImportError as e:
    # Handle missing dependencies or modules
    print(f"Warning: Could not import all tool categories: {e}")
    MISSING_IMPLEMENTATIONS = True
    
    # Define fallback types for type checking
    class BaseToolCategory:  # type: ignore
        pass
    
    ToolCategoryT = TypeVar('ToolCategoryT', bound=BaseToolCategory)
    ALL_TOOL_CATEGORIES: List[Type[BaseToolCategory]] = []

# Version information
__version__ = "0.1.0"
__all__ = [
    "BaseToolCategory",
    "FileOperationTools",
    "TransformTools",
    "ColorAdjustmentTools",
    "FilterTools",
    "BatchProcessingTools",
    "HelpTools",
    "LayerManagementTools",
    "ImageAnalysisTools",
    "PerformanceTools"
]

# Tool category mapping for easy access
TOOL_CATEGORIES = {
    "file_operations": FileOperationTools,
    "transforms": TransformTools,
    "color_adjustments": ColorAdjustmentTools,
    "filters": FilterTools,
    "batch_processing": BatchProcessingTools,
    "help_tools": HelpTools,
    "layer_management": LayerManagementTools,
    "image_analysis": ImageAnalysisTools,
    "performance_tools": PerformanceTools
}

# Additional metadata for tool categories
@dataclass
class ToolCategoryInfo:
    """Metadata and information about a tool category."""
    name: str
    display_name: str
    description: str
    version: str
    category: str = "general"
    experimental: bool = False
    requires_gpu: bool = False

def get_tool_category(category_name: str) -> Type[BaseToolCategory]:
    """
    Get a tool category class by name.
    
    Args:
        category_name: Name of the tool category (case-insensitive)
        
    Returns:
        The tool category class
        
    Raises:
        ValueError: If the category name is invalid
        RuntimeError: If there are missing implementations
    """
    if MISSING_IMPLEMENTATIONS:
        raise RuntimeError("Some tool categories failed to import. Check logs for details.")
        
    category_name = category_name.lower().strip()
    if category_name not in TOOL_CATEGORIES:
        valid_categories = ", ".join(f'"{name}"' for name in TOOL_CATEGORIES)
        raise ValueError(
            f"Unknown tool category: '{category_name}'. "
            f"Valid categories are: {valid_categories}"
        )
    return TOOL_CATEGORIES[category_name]

def list_tool_categories(include_experimental: bool = False) -> List[str]:
    """
    Get a list of all available tool category names.
    
    Args:
        include_experimental: Whether to include experimental tool categories
        
    Returns:
        List of tool category names, optionally filtered by experimental status
    """
    if include_experimental:
        return list(TOOL_CATEGORIES.keys())
        
    # Filter out experimental tools
    return [
        name for name, cls in TOOL_CATEGORIES.items()
        if not getattr(cls, 'EXPERIMENTAL', False)
    ]

def get_tool_category_info(category_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific tool category.
    
    Args:
        category_name: Name of the tool category
        
    Returns:
        Dictionary containing category information including:
        - name: Internal name of the category
        - display_name: Human-readable name
        - description: Detailed description
        - version: Version string
        - experimental: Whether this is an experimental feature
        - requires_gpu: Whether GPU acceleration is required
        - tools: List of available tools in this category
    
    Raises:
        ValueError: If the category name is invalid
    """
    category = get_tool_category(category_name)
    
    # Get basic metadata from the class
    info: Dict[str, Any] = {
        "name": category_name,
        "display_name": getattr(category, "DISPLAY_NAME", category_name.replace("_", " ").title()),
        "description": (getattr(category, "__doc__", "") or "No description available").strip(),
        "version": getattr(category, "VERSION", "0.1.0"),
        "experimental": getattr(category, "EXPERIMENTAL", False),
        "requires_gpu": getattr(category, "REQUIRES_GPU", False),
        "tools": []
    }
    
    # Find all public methods that are marked as tools
    for name in dir(category):
        if name.startswith("_"):
            continue
            
        method = getattr(category, name)
        if callable(method) and hasattr(method, "_tool_metadata"):
            tool_info = {
                "name": name,
                "description": method._tool_metadata.get("description", ""),
                "parameters": method._tool_metadata.get("parameters", {})
            }
            info["tools"].append(tool_info)
    
    return info
