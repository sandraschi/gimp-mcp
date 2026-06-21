# GIMP MCP Server — User Guide

## Getting Started

### Prerequisites
- Python 3.12 or later
- GIMP 3.0 or later (including gimp-console-3.exe on Windows)
- uv package manager (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/sandraschi/gimp-mcp.git
cd gimp-mcp

# Install with uv
uv sync

# Or with pip
pip install -e .
```

### Starting the Server

```bash
# Start with default settings (stdio transport)
uv run gimp-mcp

# Start with HTTP transport
uv run uvicorn gimp_mcp.http_app:app --host 127.0.0.1 --port 10773

# Start with web dashboard
.\start.ps1
```

### Verifying the Installation

```bash
# Check GIMP availability
uv run python -c "from gimp_mcp.gimp_detector import GimpDetector; print(GimpDetector().detect_gimp_installation())"
```

If GIMP is detected, the server will use it for all image operations. If not, some tools will report GIMP as unavailable but the server itself will still start.

## Image Editing Tutorials

### Tutorial 1: Basic Image Resizing

Resizing images is one of the most common operations. The gimp_transform portmanteau tool handles this along with other geometric transforms.

```python
# Resize an image to 800x600 while maintaining aspect ratio
gimp_transform(operation="resize", input_path="/path/to/input.jpg", output_path="/path/to/output.jpg", width=800, height=600)
```

The result includes metadata about the operation: original dimensions, new dimensions, and the resampling method used.

### Tutorial 2: Color Correction Workflow

Professional color correction follows a specific order of operations. Always correct brightness and contrast first, then adjust color balance.

```python
# Step 1: Fix exposure
gimp_color(operation="brightness_contrast", input_path="/path/to/photo.jpg", output_path="/path/to/step1.jpg", brightness=0.1, contrast=0.2)

# Step 2: Adjust white balance
gimp_color(operation="levels", input_path="/path/to/step1.jpg", output_path="/path/to/step2.jpg", gamma=1.2)

# Step 3: Boost saturation
gimp_color(operation="hue_saturation", input_path="/path/to/step2.jpg", output_path="/path/to/final.jpg", saturation=0.3)
```

### Tutorial 3: Applying Creative Filters

GIMP MCP provides access to GIMP's rich filter library through the gimp_filter tool.

```python
# Apply a gaussian blur for background softening
gimp_filter(operation="blur", input_path="/path/to/portrait.jpg", output_path="/path/to/blurred.jpg", method="gaussian", radius=5.0)

# Apply artistic oilify effect
gimp_filter(operation="artistic", input_path="/path/to/photo.jpg", output_path="/path/to/oil.jpg", effect="oilify")
```

### Tutorial 4: Layer-Based Editing

For non-destructive editing, use the gimp_layer tool:

```python
# Create a new transparent layer
gimp_layer(operation="create", input_path="/path/to/base.xcf", output_path="/path/to/layered.xcf", layer_name="Adjustments")

# Merge visible layers
gimp_layer(operation="flatten", input_path="/path/to/layered.xcf", output_path="/path/to/merged.png")
```

### Tutorial 5: Batch Processing a Directory

Process an entire directory of images with a single command:

```python
# Resize all JPGs to 1024px wide
gimp_batch(operation="resize", input_directory="/path/to/input", output_directory="/path/to/output", width=1024, file_pattern="*.jpg")

# Convert all PNGs to WebP
gimp_batch(operation="convert", input_directory="/path/to/input", output_directory="/path/to/output", output_format="webp", quality=85)
```

### Tutorial 6: Image Analysis for Quality Control

Analyze image quality and detect potential issues:

```python
# Comprehensive image quality analysis
gimp_analysis(operation="quality", input_path="/path/to/photo.jpg")

# Compare two images
gimp_analysis(operation="compare", input_path="/path/to/original.jpg", compare_path="/path/to/edited.jpg")
```

### Tutorial 7: G'MIC Filters

G'MIC provides over 500 filters through a single integration point:

```python
# List all filter categories
gimp_gmic(operation="list_categories")

# Apply a specific filter with raw command
gimp_gmic(operation="apply", filter_command="-fx_meteor")

# Apply a named filter with parameters
gimp_gmic(operation="apply_named", filter_name="blur_gaussian", filter_params={"radius": 10})
```

### Tutorial 8: ICC Color Management

Professional color-managed workflows:

```python
# Get current color profile info
gimp_color_management(operation="profile_info")

# Assign an ICC profile to an image
gimp_color_management(operation="assign_profile", profile_path="/path/to/sRGB.icc")

# Convert to another color space
gimp_color_management(operation="convert_profile", profile_path="/path/to/AdobeRGB.icc")

# Enable soft proofing
gimp_color_management(operation="soft_proofing", soft_proofing_enabled=True)
```

### Tutorial 9: PDB Direct Access

For operations not covered by portmanteau tools, use the universal PDB escape hatch:

```python
# Select all
gimp_pdb(procedure="gimp_selection_all")

# Apply Gaussian blur via PDB
gimp_pdb(procedure="plug_in_gauss", args=[0, 1, 5.0, 5.0, 0])

# Get image dimensions
gimp_pdb(procedure="gimp_image_width", args=[image_id])
```

### Tutorial 10: Animation and GIF Export

Create and export frame-based animations:

```python
# List frames in an animated XCF
gimp_animation(operation="list_frames", image_path="/path/to/animation.xcf")

# Set frame delay
gimp_animation(operation="set_frame_delay", image_path="/path/to/animation.xcf", frame_delay_ms=150)

# Export as animated GIF
gimp_animation(operation="export_gif", image_path="/path/to/animation.xcf", output_path="/path/to/output.gif", loop_forever=True, dither=True)
```

## Advanced Workflows

### AI-Powered Image Generation

Generate images using AI models with post-processing in GIMP:

```python
# The agentic workflow tool orchestrates multi-step operations
# First generate, then enhance with GIMP filters
```

### PBR Material Pack Generation

Create PBR (Physically Based Rendering) material packs from source textures:

```python
gimp_batch(operation="pbr_pack", input_directory="/path/to/textures", output_directory="/path/to/pbr", map_size=2048, pack_prefix="brick")
```

### Cross-Server Integration

Bridging with other MCP servers for extended workflows:

```python
# Bridge to ink scape MCP for vector operations
# Bridge to godot-mcp for 3D texture import
# Configured via MCP_BRIDGE_URLS environment variable
```

## Performance Optimization

### Caching
The server maintains a result cache to speed up repeated operations. Clear the cache with:
```python
gimp_system(operation="cache", cache_action="clear")
```

### Parallel Processing
Batch operations use a configurable thread pool. Adjust `max_workers` in config.yaml or set the MAX_WORKERS environment variable.

### Memory Management
Large images can consume significant memory. The server automatically cleans up temporary files after each operation. For very large batch operations, consider processing in smaller groups.

## Troubleshooting

### GIMP Not Found
If GIMP is not automatically detected:
1. Set the `GIMP_BIN` environment variable to the full path of gimp-console-3.exe (Windows) or gimp-console (Linux/Mac)
2. Or place the executable in a standard location:
   - Windows: `C:\Program Files\GIMP 3\bin\`
   - Linux: `/usr/bin/gimp-console`
   - Mac: `/Applications/GIMP.app/Contents/MacOS/gimp-console`

### Bridge Connection Issues
The TCP bridge plugin must be installed in GIMP's plug-ins directory:
```bash
just bridge-install
# Or manually copy src/gimp_mcp/plugins/gimp_mcp_bridge/gimp_mcp_bridge.py
#   to %APPDATA%/GIMP/3.0/plug-ins/gimp_mcp_bridge/
```

### Permission Errors
All file operations are restricted to directories listed in `ALLOWED_DIRECTORIES`. Add your working directories to this list in the config file or environment variable.

### Slow Operations
- Reduce image resolution before complex filter operations
- Use batch mode for multiple files
- Check that GIMP is not already busy with another operation
- Adjust `gimp_timeout` in config.yaml for long-running operations

## API Reference Summary

### gimp_file
Operations: load, save, convert, info, validate, list_formats
Parameters: input_path, output_path, format, quality (1-100), compression (0-9), progressive

### gimp_transform
Operations: resize, crop, rotate, flip, scale, perspective, autocrop
Parameters: width, height, maintain_aspect, x, y, degrees, direction, fill_color

### gimp_color
Operations: brightness_contrast, levels, curves, hue_saturation, color_balance, desaturate, auto
Parameters: brightness (-1 to 1), contrast (-1 to 1), hue (-180 to 180), saturation (-1 to 1), lightness (-1 to 1), gamma (0.1 to 10.0)

### gimp_filter
Operations: blur, sharpen, noise, edge_detect, artistic, enhance, distort
Parameters: radius (pixels), amount (0 to 1), method, effect

### gimp_layer
Operations: create, duplicate, delete, merge, flatten, reorder, info
Parameters: layer_name, layer_index, opacity (0-100), blend_mode, visible

### gimp_analysis
Operations: quality, statistics, histogram, compare, detect_issues, report
Parameters: compare_path, include_histogram, analysis_type, report_format

### gimp_batch
Operations: resize, convert, process, watermark, rename, optimize, pbr_pack
Parameters: input_directory, output_directory, file_pattern, width, height, output_format, quality

### gimp_system
Operations: status, help, diagnostics, cache, config, performance, tools, version
Parameters: topic, level, cache_action

### gimp_pdb
Any GIMP PDB procedure by name
Parameters: procedure (string), args (list)

### gimp_gmic
Operations: list_categories, apply, apply_named, list_filters
Parameters: filter_command, filter_name, filter_params

### gimp_gegl
Operations: list_ops, apply
Parameters: operation_name, config_string

### gimp_color_management
Operations: profile_info, assign_profile, convert_profile, get_effective_profile, soft_proofing, simulation_profile, list_profiles
Parameters: profile_path, soft_proofing_enabled

### gimp_animation
Operations: list_frames, set_frame_delay, optimize_for_gif, export_gif, frame_count
Parameters: frame_delay_ms, frame_index, loop_forever, dither

### gimp_workspace
Operations: list_images, current_image, undo, redo, undo_group, metadata, resolution, unit
Parameters: image_id, xresolution, yresolution, unit

### gimp_channel
Operations: create, delete, list, set_color, set_opacity, set_show_masked, duplicate, info
Parameters: channel_name, width, height, color, opacity

### gimp_paths
Operations: create, delete, list, stroke, import_svg, export_svg, set_name, get_points
Parameters: svg_path, path_name, new_name

### gimp_parasites
Operations: list_image, list_drawable, attach_image, attach_drawable, detach_image, detach_drawable, get_image, get_drawable, get_animation_delay
Parameters: parasite_name, parasite_data, frame_delay_ms
