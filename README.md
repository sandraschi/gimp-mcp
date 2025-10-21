# GIMP MCP Server

Professional image editing through Model Context Protocol (MCP) using GIMP.

## Overview

GIMP-MCP provides Claude and other AI agents with professional image editing capabilities through GIMP (GNU Image Manipulation Program). This MCP server enables powerful image processing operations via a clean, standardized interface.

## Features

### Core Image Operations
- **File Management**: Load, save, and convert between formats (JPEG, PNG, WebP, TIFF, etc.)
- **Transformations**: Resize, crop, rotate, and flip images with quality preservation
- **Color Adjustments**: Brightness, contrast, hue, saturation, and color balance
- **Filters & Effects**: Blur, sharpen, noise reduction, and artistic filters
- **Batch Processing**: Process multiple images efficiently

### Technical Highlights
- **Cross-platform**: Windows, macOS, and Linux support
- **Performance optimized**: Async operations with process management
- **Robust error handling**: Comprehensive validation and recovery
- **Flexible configuration**: YAML-based settings with sensible defaults
- **Security focused**: File validation and access controls

## Installation

### Prerequisites
- Python 3.10 or higher
- GIMP 2.10+ (GIMP 3.0+ recommended)

### Quick Install
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

## Available Tools

### File Operations
- `load_image` - Load and analyze image files
- `get_image_info` - Extract comprehensive metadata
- `save_image` - Save with format conversion
- `convert_format` - Format conversion with quality options

### Transformations
- `resize_image` - Smart resizing with aspect ratio preservation
- `crop_image` - Precise rectangular cropping
- `rotate_image` - Rotation with background fill options
- `flip_image` - Horizontal and vertical flipping

### Color Adjustments
- `adjust_brightness_contrast` - Basic tonal adjustments
- `adjust_hue_saturation` - HSL color manipulation
- `color_balance` - Professional color grading

### Filters & Effects
- `apply_blur` - Gaussian, motion, and radial blur
- `apply_sharpen` - Unsharp mask sharpening
- `noise_reduction` - Intelligent noise filtering

### Batch Processing
- `batch_resize` - Bulk image resizing
- `batch_convert` - Mass format conversion
- `batch_apply_filter` - Apply filters to multiple images

## Development Status

**Current Phase**: Foundation Complete (SUCCESS)
- Repository scaffolding
- GIMP detection system
- Configuration management
- CLI wrapper framework
- Core tool structure

**Next Phase**: Tool Implementation
- File operations (in progress)
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
