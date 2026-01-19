# GIMP MCP Server

**By FlowEngineer sandraschi**

Professional image editing through Model Context Protocol (MCP) using GIMP.

[![FastMCP](https://img.shields.io/badge/FastMCP-2.14.3%2B-blue)](https://github.com/jlowin/fastmcp)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## Overview

GIMP-MCP provides Claude and other AI agents with professional image editing capabilities through GIMP (GNU Image Manipulation Program). This MCP server enables powerful image processing operations via a clean, standardized interface.

## 🚀 **Coming Soon: AI Image Generation**

**Transform natural language into professional raster images.** Tell Claude "create a fake photo of Benny driving a motorbike through a cyberpunk city" and watch it generate production-ready images automatically.

- **🤖 AI-Powered Image Generation**: Natural language to professional raster graphics
- **🎨 Multi-Model Support**: Integration with Flux, Stable Diffusion, and other AI models
- **🛡️ Enterprise Security**: Validated image generation with content safety
- **🔄 GIMP Post-Processing**: Professional editing and enhancement workflows
- **📚 Image Repository**: Versioned asset management and intelligent search

See [AI Image Generation Plan](docs/AI_IMAGE_GENERATION_PLAN.md) for technical details.

## v3.0.0 - Portmanteau Architecture

**New in v3.0.0:** Instead of 50+ individual tools, GIMP MCP now consolidates related operations into **8 master portmanteau tools**. This design:

- 🎯 **Reduces cognitive load** - 8 tools instead of 50+
- 🔍 **Improves discoverability** - Related operations grouped together  
- ⚡ **Follows FastMCP 2.13+ best practices** - Modern MCP architecture
- 📚 **Better documentation** - Each tool is self-documenting with comprehensive docstrings

### Portmanteau Tools

| Tool | Operations | Description |
|------|------------|-------------|
| `gimp_file` | 6 | File operations: load, save, convert, info, validate |
| `gimp_transform` | 7 | Transforms: resize, crop, rotate, flip, scale, perspective |
| `gimp_color` | 12 | Color: brightness, contrast, levels, curves, HSL, auto |
| `gimp_filter` | 8 | Filters: blur, sharpen, noise, edge, artistic, distort |
| `gimp_layer` | 8 | Layers: create, duplicate, delete, merge, flatten |
| `gimp_analysis` | 8 | Analysis: quality, statistics, histogram, compare |
| `gimp_batch` | 6 | Batch: resize, convert, watermark, optimize |
| `gimp_system` | 8 | System: status, help, diagnostics, cache, config |

## Features

### Core Image Operations
- **File Management**: Load, save, and convert between formats (JPEG, PNG, WebP, TIFF, etc.)
- **Transformations**: Resize, crop, rotate, and flip images with quality preservation
- **Color Adjustments**: Brightness, contrast, hue, saturation, and color balance
- **Filters & Effects**: Blur, sharpen, noise reduction, and artistic filters
- **Batch Processing**: Process multiple images efficiently
- **Image Analysis**: Quality assessment, statistics, histogram, comparison

### Technical Highlights
- **Cross-platform**: Windows, macOS, and Linux support
- **Performance optimized**: Async operations with process management
- **Robust error handling**: Comprehensive validation and recovery
- **Flexible configuration**: YAML-based settings with sensible defaults
- **Security focused**: File validation and access controls
- **FastMCP 2.13+**: Modern MCP architecture with portmanteau tools

## Installation

### Prerequisites
- Python 3.10 or higher
- GIMP 2.10+ (GIMP 3.0+ recommended)

### Quick Install

#### **Option 1: PyPI Package Install (Recommended)** ⭐

**Simple pip installation - no repository cloning required!**

```bash
# Install from PyPI
pip install gimp-mcp

# Verify installation
gimp-mcp --version
```

**Advantages:**
- ✅ **Universal compatibility** - Works with any MCP client
- ✅ **Simple installation** - Just one pip command
- ✅ **Always up-to-date** - Install latest version directly
- ✅ **No repository cloning** - Clean, minimal setup
- ✅ **Easy updates** - `pip install --upgrade gimp-mcp`

---

#### **Option 2: Repository Installation (Development)**

```bash
# Clone the repository
git clone https://github.com/sandraschi/gimp-mcp.git
cd gimp-mcp

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Verify Installation
```bash
# Check GIMP detection
gimp-mcp --validate-only
```

## Configuration

GIMP-MCP works out of the box with automatic GIMP detection and sensible defaults.

### Custom Configuration
Create `config.yaml` in your working directory:

```yaml
# GIMP Configuration
gimp_executable: "/custom/path/to/gimp"  # Optional: auto-detected

# Performance Settings
max_concurrent_processes: 3
process_timeout: 30

# File Handling
temp_directory: "/tmp/gimp-mcp"
max_file_size_mb: 100
preserve_metadata: true
```

## Usage

### Start the Server
```bash
gimp-mcp --host localhost --port 8000
```

### Claude Desktop Integration
Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "gimp-mcp": {
      "command": "gimp-mcp",
      "args": []
    }
  }
}
```

## Available Tools (v3.0.0 Portmanteau)

### gimp_file - File Operations
```python
gimp_file(operation="load", input_path="image.jpg")
gimp_file(operation="save", input_path="image.png", output_path="output.jpg", format="jpeg", quality=90)
gimp_file(operation="convert", input_path="image.png", output_path="output.webp", format="webp")
gimp_file(operation="info", input_path="image.jpg")
```
**Operations**: `load`, `save`, `convert`, `info`, `validate`, `list_formats`

### gimp_transform - Image Transformations
```python
gimp_transform(operation="resize", input_path="img.jpg", output_path="out.jpg", width=1920, height=1080)
gimp_transform(operation="crop", input_path="img.jpg", output_path="out.jpg", x=100, y=100, width=500, height=400)
gimp_transform(operation="rotate", input_path="img.jpg", output_path="out.jpg", degrees=90)
gimp_transform(operation="flip", input_path="img.jpg", output_path="out.jpg", direction="horizontal")
```
**Operations**: `resize`, `crop`, `rotate`, `flip`, `scale`, `perspective`, `autocrop`

### gimp_color - Color Adjustments
```python
gimp_color(operation="brightness_contrast", input_path="img.jpg", output_path="out.jpg", brightness=20, contrast=10)
gimp_color(operation="levels", input_path="img.jpg", output_path="out.jpg", gamma=1.2)
gimp_color(operation="hue_saturation", input_path="img.jpg", output_path="out.jpg", saturation=20)
gimp_color(operation="desaturate", input_path="img.jpg", output_path="out.jpg", mode="luminosity")
```
**Operations**: `brightness_contrast`, `levels`, `curves`, `color_balance`, `hue_saturation`, `colorize`, `threshold`, `posterize`, `desaturate`, `invert`, `auto_levels`, `auto_color`

### gimp_filter - Filters & Effects
```python
gimp_filter(operation="blur", input_path="img.jpg", output_path="out.jpg", method="gaussian", radius=5)
gimp_filter(operation="sharpen", input_path="img.jpg", output_path="out.jpg", amount=0.8)
gimp_filter(operation="artistic", input_path="img.jpg", output_path="out.jpg", effect="oilify")
```
**Operations**: `blur`, `sharpen`, `noise`, `edge_detect`, `artistic`, `enhance`, `distort`, `light_shadow`

### gimp_analysis - Image Analysis
```python
gimp_analysis(operation="quality", input_path="img.jpg")
gimp_analysis(operation="statistics", input_path="img.jpg", include_histogram=True)
gimp_analysis(operation="compare", input_path="img1.jpg", compare_path="img2.jpg")
gimp_analysis(operation="detect_issues", input_path="img.jpg")
```
**Operations**: `quality`, `statistics`, `histogram`, `compare`, `detect_issues`, `report`, `color_profile`, `metadata`

### gimp_batch - Batch Processing
```python
gimp_batch(operation="resize", input_directory="photos/", output_directory="resized/", width=1920)
gimp_batch(operation="convert", input_directory="images/", output_directory="webp/", output_format="webp")
gimp_batch(operation="watermark", input_directory="photos/", output_directory="watermarked/", watermark_path="logo.png")
```
**Operations**: `resize`, `convert`, `process`, `watermark`, `rename`, `optimize`

### gimp_system - System Operations
```python
gimp_system(operation="status")
gimp_system(operation="help", topic="transform", level="intermediate")
gimp_system(operation="diagnostics")
gimp_system(operation="cache", cache_action="clear")
```
**Operations**: `status`, `help`, `diagnostics`, `cache`, `config`, `performance`, `tools`, `version`

## Development Status

**Current Phase**: v3.0.0 Portmanteau Architecture (COMPLETE)
- ✅ FastMCP 2.13+ integration
- ✅ 8 portmanteau tools consolidating 63 operations
- ✅ Comprehensive docstrings with examples
- ✅ MCPB manifest for Claude Desktop
- ✅ Backwards-compatible with legacy tools

**Capabilities**:
- File operations with format conversion
- Transform operations (basic complete)
- Color adjustments (planned)
- Filters and effects (planned)

## Architecture

The server uses a modular architecture with:
- **FastMCP Integration**: Standard MCP protocol implementation
- **CLI Wrapper**: Robust GIMP command-line interface
- **Tool Categories**: Organized by functionality for maintainability
- **Error Handling**: Comprehensive validation and recovery
- **Cross-platform**: Windows, macOS, and Linux support

## Contributing

See the detailed implementation plan in `docs/IMPLEMENTATION_ROADMAP.md` for development guidelines and current status.

## License

MIT License - see LICENSE file for details.
