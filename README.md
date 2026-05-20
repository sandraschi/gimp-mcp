# GIMP MCP Server

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://biomejs.dev"><img src="https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white" alt="Biome"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>

**Professional image editing through GIMP 3 — controlled by AI agents via the Model Context Protocol.** 17 portmanteau tools consolidate GIMP's ~1000 PDB procedures into clean, discoverable operations.

## Quick Start

```powershell
git clone https://github.com/sandraschi/gimp-mcp
cd gimp-mcp
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:
1. Install GIMP 3.2+ (standalone, not Windows Store) from gimp.org
2. Run `uv sync` to install Python dependencies
3. Launch GIMP with the bridge plugin: `.\start.ps1 -RestartGimp`
4. Open http://localhost:10772

## Table of Contents

| Document | What's inside |
|----------|---------------|
| [📦 Installation](docs/readme/INSTALL.md) | Prerequisites, GIMP 3 install, uv sync, start methods, bridge install, verifications |
| [🏗️ Architecture](docs/readme/ARCHITECTURE.md) | 4-layer design, portmanteau pattern, tool registration flow, Live vs Headless, ports |
| [🖼️ GIMP Integration](docs/readme/GIMP_INTEGRATION.md) | Live Bridge mechanics, PDB proxy, GIMP 3 Python-Fu, known limitations, troubleshooting |
| [🧩 GIMP Plugins](docs/readme/GIMP_PLUGINS.md) | Bridge plugin architecture, installation, lifecycle, protocol, extending, directory locations |
| [⚙️ CLI & API](docs/readme/CLI_API.md) | CLI batch mode, PDB proxy ref, REST API, webapp pages, all 21 justfile recipes |

## Tools

| Tool | Ops | Description |
|------|-----|-------------|
| `gimp_file` | 6 | load, save, convert, info, validate, list_formats |
| `gimp_transform` | 7 | resize, crop, rotate, flip, scale, perspective, autocrop |
| `gimp_color` | 12 | brightness, contrast, levels, curves, HSL, balance, auto, invert, threshold, posterize, desaturate, colorize |
| `gimp_filter` | 8 | blur, sharpen, noise, edge_detect, artistic, enhance, distort, light_shadow |
| `gimp_layer` | 8 | create, duplicate, merge, flatten, opacity, blend, reorder, info |
| `gimp_analysis` | 8 | quality, statistics, histogram, compare, detect_issues, report, color_profile, metadata |
| `gimp_batch` | 6 | resize, convert, process, watermark, rename, optimize |
| `gimp_system` | 8 | status, help, diagnostics, cache, config, performance, tools, version |
| `gimp_pdb` | ∞ | **Universal PDB proxy** — call any of ~1000+ GIMP procedures by name |
| `gimp_workspace` | 10 | list images, undo/redo, undo groups, metadata, resolution |
| `gimp_channel` | 8 | create, delete, list, set color/opacity, duplicate channels |
| `gimp_animation` | 5 | list frames, set delay, optimize/export GIF |
| `gimp_paths` | 8 | create, delete, stroke, import/export SVG, vector paths |
| `gimp_parasites` | 9 | XCF metadata: list, attach, detach parasites on images/drawables |
| `gimp_gmic` | 4 | G'MIC filter integration — 500+ filters via plug-in-gmic |
| `gimp_gegl` | 2 | GEGL non-destructive editing operations |
| `gimp_color_management` | 7 | ICC profiles, assignment, conversion, soft proofing |

## Example: Resize an Image

```
User: "Resize this photo to 1920x1080"

Agent calls: gimp_transform(operation="resize",
  input_path="C:/photos/sunset.jpg",
  output_path="C:/photos/sunset_1920.jpg",
  width=1920, height=1080)

Response: {"success": true, "message": "Resized sunset.jpg from
  4000x2250 to 1920x1080 (lanczos, 95% quality)", ...}
```

Behind the scenes — the tool detects whether GIMP is running (Live Bridge via TCP :10775) or not (Headless CLI via `gimp-console-3.exe`), and routes the operation accordingly.

## License

MIT — see [LICENSE](LICENSE) for details.

---

*Built with [FastMCP 3.2](https://github.com/jlowin/fastmcp) by [sandraschi](https://github.com/sandraschi)*
