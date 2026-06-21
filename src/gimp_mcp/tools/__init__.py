"""
GIMP MCP Tools - FastMCP 2.13+ Portmanteau Architecture.

Consolidated tools for reduced cognitive load and better discoverability.

Instead of 50+ individual tools, GIMP MCP consolidates related operations into 17
master tools. Each tool handles a specific domain with multiple operations.

TOOLS:
- gimp_file: File operations (load, save, convert, info)
- gimp_transform: Geometric transforms (resize, crop, rotate, flip)
- gimp_color: Color adjustments (brightness, levels, curves, HSL)
- gimp_filter: Filters (blur, sharpen, noise, artistic)
- gimp_layer: Layer management (create, merge, flatten)
- gimp_analysis: Image analysis (quality, statistics, compare)
- gimp_batch: Batch processing (resize, convert, watermark)
- gimp_system: System operations (status, help, cache)
- gimp_workspace: Workspace state (list images, undo/redo, metadata, resolution)
- gimp_channel: Channel management (create, delete, list, color, opacity)
- gimp_gmic: G'MIC filter integration (list_categories, apply, apply_named)
- gimp_gegl: GEGL operation wrapper (list_ops, apply)
- gimp_color_management: ICC color management (profile_info, assign, convert, proofing)
"""

from .analysis import gimp_analysis
from .animation import gimp_animation
from .batch import gimp_batch
from .channel import gimp_channel
from .color import gimp_color
from .color_mgmt import gimp_color_management
from .file_operations import gimp_file
from .filter import gimp_filter
from .gegl import gimp_gegl
from .gmic import gimp_gmic
from .layer import gimp_layer
from .parasites import gimp_parasites
from .paths import gimp_paths
from .pdb_proxy import gimp_pdb
from .system import gimp_system
from .transform import gimp_transform
from .workspace import gimp_workspace

__all__ = [
    "gimp_analysis",
    "gimp_animation",
    "gimp_batch",
    "gimp_channel",
    "gimp_color",
    "gimp_color_management",
    "gimp_file",
    "gimp_filter",
    "gimp_gegl",
    "gimp_gmic",
    "gimp_layer",
    "gimp_parasites",
    "gimp_paths",
    "gimp_pdb",
    "gimp_system",
    "gimp_transform",
    "gimp_workspace",
]

# Tool metadata for discovery
PORTMANTEAU_TOOLS = [
    {
        "name": "gimp_file",
        "function": gimp_file,
        "category": "file_operations",
        "operations": ["load", "save", "convert", "info", "validate", "list_formats"],
    },
    {
        "name": "gimp_transform",
        "function": gimp_transform,
        "category": "transforms",
        "operations": [
            "resize",
            "crop",
            "rotate",
            "flip",
            "scale",
            "perspective",
            "autocrop",
        ],
    },
    {
        "name": "gimp_color",
        "function": gimp_color,
        "category": "color_adjustments",
        "operations": [
            "brightness_contrast",
            "levels",
            "curves",
            "color_balance",
            "hue_saturation",
            "colorize",
            "threshold",
            "posterize",
            "desaturate",
            "invert",
            "auto_levels",
            "auto_color",
        ],
    },
    {
        "name": "gimp_filter",
        "function": gimp_filter,
        "category": "filters",
        "operations": [
            "blur",
            "sharpen",
            "noise",
            "edge_detect",
            "artistic",
            "enhance",
            "distort",
            "light_shadow",
        ],
    },
    {
        "name": "gimp_layer",
        "function": gimp_layer,
        "category": "layer_management",
        "operations": [
            "create",
            "duplicate",
            "delete",
            "merge",
            "flatten",
            "reorder",
            "properties",
            "info",
        ],
    },
    {
        "name": "gimp_analysis",
        "function": gimp_analysis,
        "category": "image_analysis",
        "operations": [
            "quality",
            "statistics",
            "histogram",
            "compare",
            "detect_issues",
            "report",
            "color_profile",
            "metadata",
        ],
    },
    {
        "name": "gimp_batch",
        "function": gimp_batch,
        "category": "batch_processing",
        "operations": [
            "resize",
            "convert",
            "process",
            "watermark",
            "rename",
            "optimize",
        ],
    },
    {
        "name": "gimp_system",
        "function": gimp_system,
        "category": "system",
        "operations": [
            "status",
            "help",
            "diagnostics",
            "cache",
            "config",
            "performance",
            "tools",
            "version",
        ],
    },
    {
        "name": "gimp_pdb",
        "function": gimp_pdb,
        "category": "pdb_proxy",
        "operations": ["pdb_call"],
        "description": "Generic GIMP PDB proxy — calls any procedure by name. Universal escape hatch to the full ~1000-procedure PDB.",
    },
    {
        "name": "gimp_workspace",
        "function": gimp_workspace,
        "category": "workspace",
        "operations": [
            "list_images",
            "current_image",
            "undo_count",
            "undo",
            "redo",
            "undo_group_start",
            "undo_group_end",
            "get_metadata",
            "set_resolution",
            "set_unit",
        ],
    },
    {
        "name": "gimp_channel",
        "function": gimp_channel,
        "category": "channel_management",
        "operations": [
            "create",
            "delete",
            "list",
            "set_color",
            "set_opacity",
            "set_show_masked",
            "duplicate",
            "info",
        ],
    },
    {
        "name": "gimp_animation",
        "function": gimp_animation,
        "category": "animation",
        "operations": [
            "list_frames",
            "set_frame_delay",
            "optimize_for_gif",
            "export_gif",
            "frame_count",
        ],
    },
    {
        "name": "gimp_paths",
        "function": gimp_paths,
        "category": "vector_paths",
        "operations": [
            "create",
            "delete",
            "list",
            "stroke",
            "import_svg",
            "export_svg",
            "set_name",
            "get_points",
        ],
    },
    {
        "name": "gimp_parasites",
        "function": gimp_parasites,
        "category": "xcf_parasites",
        "operations": [
            "list_image",
            "list_drawable",
            "attach_image",
            "attach_drawable",
            "detach_image",
            "detach_drawable",
            "get_image",
            "get_drawable",
            "get_animation_delay",
        ],
    },
    {
        "name": "gimp_gmic",
        "function": gimp_gmic,
        "category": "gmic_filters",
        "operations": ["list_categories", "apply", "apply_named", "list_filters"],
        "description": "G'MIC filter integration — 500+ filters via plug-in-gmic PDB procedure.",
    },
    {
        "name": "gimp_gegl",
        "function": gimp_gegl,
        "category": "gegl_operations",
        "operations": ["list_ops", "apply"],
        "description": "GEGL operation wrapper — GIMP 3 non-destructive editing engine.",
    },
    {
        "name": "gimp_color_management",
        "function": gimp_color_management,
        "category": "color_management",
        "operations": [
            "profile_info",
            "assign_profile",
            "convert_profile",
            "get_effective_profile",
            "soft_proofing",
            "simulation_profile",
            "list_profiles",
        ],
        "description": "ICC color management — profile info, assignment, conversion, soft proofing.",
    },
]


def get_all_tools():
    """Return all portmanteau tool functions for registration."""
    return [tool["function"] for tool in PORTMANTEAU_TOOLS]


def get_tool_metadata():
    """Return metadata for all portmanteau tools."""
    return PORTMANTEAU_TOOLS
