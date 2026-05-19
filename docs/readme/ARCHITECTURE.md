# Architecture

## Four-Layer Design

```
┌──────────────────────────────────────────────────┐
│                    MCP Client                     │
│          (Claude Desktop, Cursor, etc.)           │
└──────────────────────┬───────────────────────────┘
                       │ JSON-RPC (stdio or HTTP/SSE)
┌──────────────────────▼───────────────────────────┐
│             1. MCP Server (FastMCP 3.2)           │
│              gimp_mcp/main.py:79                  │
│  ┌──────────┬──────────┬──────────┬────────────┐  │
│  │ Tools    │ Prompts  │Resources │   Skills   │  │
│  │(17 port-  │(4 edit   │(docu-    │(gimp-expert│  │
│  │manteaux) │sessions) │mentation)│  SKILL.md) │  │
│  └──────────┴──────────┴──────────┴────────────┘  │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│         2. Webapp Backend (FastAPI + ASGI)        │
│              gimp_mcp/http_app.py:9               │
│  /api/health  /api/status  /api/sota              │
│  /api/skills  /api/tools                          │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│         3. Webapp Frontend (Vite + React)         │
│              webapp/frontend/                     │
│  Dashboard  Apps Hub  Chat  Editor  Tools         │
│  Skills  API Docs  Status  Settings  Help         │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│           4. GIMP Bridge (TCP Plugin)             │
│        gimp_mcp/plugins/gimp_mcp_bridge.py        │
│  JSON over TCP :10775  →  GIMP PDB execution      │
└──────────────────────────────────────────────────┘
```

### Layer 1: MCP Server (`gimp_mcp/main.py`)

The core FastMCP 3.2 server (class `GimpMCPServer`) that registers all tools, prompts, resources, and skills. It communicates with MCP clients via stdio or HTTP/SSE transport. The `GimpInteractionManager` (`gimp_mcp/interaction_manager.py:15`) acts as the decision layer that chooses between Live Bridge and Headless CLI for each operation.

### Layer 2: Webapp Backend (`gimp_mcp/http_app.py`)

A uvicorn-served FastAPI app that wraps the FastMCP server and adds REST endpoints for the dashboard frontend. Runs on port **10773**.

### Layer 3: Webapp Frontend (`webapp/frontend/`)

A Vite + React SPA with 12 pages:

| Page | Description |
|------|-------------|
| Dashboard | System overview, live status |
| Apps Hub | Installed apps and integrations |
| Chat | Conversational image editing |
| Editor | Image preview and editing |
| Tools | All available tools with docs |
| Skills | GIMP expert skills |
| API Docs | REST API reference |
| Status | Health checks, diagnostics |
| Settings | Configuration management |
| Help | User guide |

### Layer 4: GIMP Bridge (`gimp_mcp/plugins/gimp_mcp_bridge/`)

A GIMP 3 plug-in (Gimp.PlugIn subclass) that opens a TCP server on port **10775** inside GIMP's main process. Accepts JSON payloads with a `"code"` field and executes them as Python inside GIMP.

## Portmanteau Design Pattern

Instead of registering 50+ individual tools (one per GIMP PDB procedure), GIMP MCP consolidates related operations into **17 logical groups** called *portmanteau tools*:

| Tool | Ops | Category |
|------|-----|----------|
| `gimp_file` | 6 | load, save, convert, info, validate, list_formats |
| `gimp_transform` | 7 | resize, crop, rotate, flip, scale, perspective, autocrop |
| `gimp_color` | 12 | brightness_contrast, levels, curves, HSL, balance, invert, etc. |
| `gimp_filter` | 8 | blur, sharpen, noise, edge, artistic, enhance, distort, light_shadow |
| `gimp_layer` | 8 | create, duplicate, merge, flatten, opacity, blend, reorder, info |
| `gimp_analysis` | 8 | quality, statistics, histogram, compare, detect, report, metadata |
| `gimp_batch` | 6 | resize, convert, process, watermark, rename, optimize |
| `gimp_system` | 8 | health, help, diagnostics, cache, config, performance, tools, version |
| `gimp_pdb` | ∞ | *any GIMP PDB procedure by name* |
| `gimp_workspace` | 10 | list_images, undo/redo, undo_groups, metadata, resolution |
| `gimp_channel` | 8 | create, delete, list, set_color, set_opacity, duplicate |
| `gimp_animation` | 5 | list_frames, set_delay, optimize_gif, export_gif |
| `gimp_paths` | 8 | create, delete, stroke, import/export SVG, vector points |
| `gimp_parasites` | 9 | list/attach/detach/get image + drawable parasites |
| `gimp_gmic` | 4 | list_categories, list_filters, apply, apply_named |
| `gimp_gegl` | 2 | list_ops, apply (GEGL non-destructive editing) |
| `gimp_color_management` | 7 | profile_info, assign/convert profile, proofing |

This reduces discovery surface for LLMs while preserving full GIMP capabilities.

## Tool Registration Flow

1. `GimpMCPServer.initialize()` at `main.py:227` runs on startup
2. `GimpDetector` finds the GIMP executable (`gimp_mcp/gimp_detector.py`)
3. `GimpInteractionManager` is initialized with `GimpCliWrapper` + `GimpBridgeWrapper`
4. Portmanteau tools are registered via `@self.mcp.tool()` decorators (lines 308-559)
5. REST routes are registered via `@self.mcp.custom_route()` (lines 664-693)
6. Legacy fallback (`_initialize_legacy_tools`) exists for backwards compatibility

## Live Bridge vs Headless CLI

The `GimpInteractionManager` (`interaction_manager.py:15`) handles mode selection:

```
execute_python_fu(code)
  ├─ enable_live_mode AND bridge.is_alive()? → Live Bridge (TCP :10775)
  │     Returns immediately, GIMP stays open
  └─ otherwise? → Headless CLI (gimp-console-3.exe)
        Spawns new process, runs script, returns output
```

- **Live Bridge**: Real-time, persistent GIMP session. Launch GIMP once, then execute many commands. Requires the bridge plugin to be installed and GIMP to be running.
- **Headless CLI**: Batch-only. Spawns `gimp-console-3.exe` for each operation. No GUI shown. Requires standalone GIMP (not Store version).

## Port Registration

| Port | Layer | Service |
|------|-------|---------|
| 10772 | Frontend | Vite React webapp |
| 10773 | Backend | uvicorn + FastAPI + FastMCP ASGI |
| 10775 | Bridge | GIMP plugin TCP socket |

All ports are in the fleet-reserved range (10700-11000) per fleet standards.
