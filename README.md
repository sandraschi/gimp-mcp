# GIMP MCP Server

**By FlowEngineer sandraschi**

Professional image editing through Model Context Protocol (MCP) using GIMP.

[![FastMCP](https://img.shields.io/badge/FastMCP-3.1.1-blue)](https://github.com/jlowin/fastmcp)
[![Python](https://img.shields.io/badge/Python-3.12%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Status](https://img.shields.io/badge/Status-v4.0.0_SOTA-purple)](#)

## Overview

GIMP-MCP provides Claude and other AI agents with professional image editing capabilities through GIMP (GNU Image Manipulation Program). This MCP server enables powerful image processing operations via a clean, standardized interface.

###  **SOTA v14.0 Industrial Modernization**
 
The GIMP MCP Server has been promoted to **SOTA v14.0 (March 2026)** industrial standards, featuring a complete control plane refactor for high-fidelity agentic workflows.

- ** Pydantic validation**: Every tool now uses strict Pydantic `BaseModel` schemas for input validation.
- ** Standardized Output**: Uses `GimpToolOutput[T]` generic wrapper for consistent telemetry and error handling.
- ** Dual-Mode API**: Intelligent auto-switching between **Live Bridge** (interactive) and **Headless CLI** (batch).
- ** FastMCP 3.1.1**: Leverages the latest asynchronous patterns and improved schema introspection.

##  **Portmanteau Architecture**

GIMP MCP consolidates 60+ legacy operations into **8 master portmanteau tools**. This design:

-  **Reduces cognitive load** - 8 tools instead of 60+
-  **Improves discoverability** - Related operations grouped together  
-  **SOTA 2026 patterns** - Optimized for AI agent reasoning
-  **Self-Documenting** - Each tool provides comprehensive introspection through the **Tools Explorer**.

### Master Tools

| Tool | Operations | Description |
|------|------------|-------------|
| `gimp_file` | 6 | **File**: load, save, convert, info, validate, list_formats |
| `gimp_transform` | 7 | **Transform**: resize, crop, rotate, flip, scale, perspective, autocrop |
| `gimp_color` | 12 | **Color**: brightness, contrast, levels, curves, HSL, balance, autocorr |
| `gimp_filter` | 8 | **Filter**: blur, sharpen, noise, edge, artistic, enhance, distort |
| `gimp_layer` | 8 | **Layer**: create, duplicate, delete, merge, flatten, opacity, blend |
| `gimp_analysis` | 8 | **Analysis**: quality, statistics, histogram, compare, detect, metadata |
| `gimp_batch` | 6 | **Batch**: multi-resize, convert, watermark, rename, optimize |
| `gimp_system` | 8 | **System**: health, help, diagnostics, cache, config, performance, version |

##  Installation & Setup

### Prerequisites
- [uv](https://docs.astral.sh/uv/) (RECOMMENDED) or Python 3.12+
- **GIMP 2.10+** (GIMP 3.0+ strongly recommended)

###  Quick Start
The easiest way to run the server is using `uvx`:
```bash
uvx gimp-mcp
```

###  Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "gimp-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/gimp-mcp", "run", "gimp_mcp"]
  }
}
```

##  Webapp Dashboard

This MCP server includes a free, premium web interface for monitoring and control.
*(Assigned ports: **10772** (Frontend), **10773** (Backend))*

To start the webapp locally:
1. Navigate to the `webapp` directory.
2. Run `start.bat` (Windows) or `./start.ps1` (PowerShell).
3. Access at `http://localhost:10772`.

## Features

- **Smart GIMP Detection**: Automated executable locating across all platforms with manual `config.yaml` override.
- **Performance optimized**: Async operations with process management.
- **Robust error handling**: Comprehensive validation and recovery.
- **Security focused**: File validation and access controls.

## Development Status

**Current Version**: `v4.0.0` (SOTA v14.0 / Industrial Modernization)
-  ✅ 100% Core tool implementation (Pydantic-backed)
-  ✅ 100% Schema validation coverage
-  ✅ 100% Standardized response formatting
-  ✅ SOTA v14.0 Documentation & Changelog

## Technical Highlights
- **Architecture**: Modular FastMCP server with plugin-based tool system.
- **Code Quality**: 100% type-hint coverage, Ruff-formatted.
- **Distribution**: Officially validated `.mcpb` distribution patterns.

## Contributing
See [ROADMAP](docs/IMPLEMENTATION_ROADMAP.md) for development guidelines.

## License
MIT License - see LICENSE file for details.
