"""
GIMP MCP Tools Package.

This package contains all the tool categories for the GIMP MCP server,
providing comprehensive image editing capabilities through GIMP integration.
"""

from .base import BaseToolCategory
from .file_operations import FileOperationTools
from .transforms import TransformTools
from .color_adjustments import ColorAdjustmentTools
from .filters import FilterTools
from .batch_processing import BatchProcessingTools
from .help_tools import HelpTools

# New tool categories
from .layer_management import LayerManagementTools
from .image_analysis import ImageAnalysisTools
from .performance_tools import PerformanceTools

__all__ = [
    "BaseToolCategory",
    "FileOperationTools",
    "TransformTools", 
    "ColorAdjustmentTools",
    "FilterTools",
    "BatchProcessingTools",
    "HelpTools",
    "LayerManagementTools",      # New: Layer management tools
    "ImageAnalysisTools",        # New: Image analysis tools
    "PerformanceTools"           # New: Performance optimization tools
]

# Tool category mapping for easy access
TOOL_CATEGORIES = {
    "file_operations": FileOperationTools,
    "transforms": TransformTools,
    "color_adjustments": ColorAdjustmentTools,
    "filters": FilterTools,
    "batch_processing": BatchProcessingTools,
    "help_tools": HelpTools,
    "layer_management": LayerManagementTools,      # New
    "image_analysis": ImageAnalysisTools,          # New
    "performance_tools": PerformanceTools          # New
}

def get_tool_category(category_name: str) -> Type[BaseToolCategory]:
    """
    Get a tool category class by name.
    
    Args:
        category_name: Name of the tool category
        
    Returns:
        Tool category class
        
    Raises:
        KeyError: If category name is not found
    """
    if category_name not in TOOL_CATEGORIES:
        raise KeyError(f"Unknown tool category: {category_name}")
    return TOOL_CATEGORIES[category_name]

def list_tool_categories() -> List[str]:
    """
    Get a list of all available tool category names.
    
    Returns:
        List of tool category names
    """
    return list(TOOL_CATEGORIES.keys())

def get_tool_category_info(category_name: str) -> Dict[str, Any]:
    """
    Get information about a specific tool category.
    
    Args:
        category_name: Name of the tool category
        
    Returns:
        Dictionary containing category information
    """
    category_class = get_tool_category(category_name)
    
    return {
        "name": category_name,
        "class_name": category_class.__name__,
        "description": getattr(category_class, '__doc__', 'No description available'),
        "module": category_class.__module__
    }
