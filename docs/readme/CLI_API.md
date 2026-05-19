# CLI & API Reference

## CLI Batch Mode

The server uses `gimp-console-3.exe` for headless batch operations. This is GIMP's command-line interface that runs without a GUI.

```bash
# Usage (internal — the server handles this automatically)
gimp-console-3.exe -d -f -b "(python-fu-gimp-mcp-run ...)" -i
```

**Requirements**: Standalone GIMP 3.2+ (not Windows Store). The Store version does not include `gimp-console-3.exe`.

**Fast path** — use the provided CLI wrapper:

```bash
# Call any PDB procedure
just pdb "gimp-version"

# List all tools
just tools
```

## PDB Proxy Tool

The `gimp_pdb` tool at `src/gimp_mcp/tools/pdb_proxy.py` calls any GIMP PDB procedure by name.

```
gimp_pdb(procedure: str, args: list[Any] | None = None) -> dict
```

Returns:
```json
{"success": true, "result": "...", "mode": "live"}
```

### Examples

```python
# Get GIMP version
gimp_pdb("gimp-version")

# Feather selection
gimp_pdb("gimp-selection-feather", [image_id, 5.0])

# Apply Gaussian blur
gimp_pdb("plug-in-gauss", [image_id, layer_id, 5.0, 5.0, 0])

# Set text layer font
gimp_pdb("gimp-text-layer-set-font", [layer_id, "Arial"])
```

The proxy tries GIMP 3 GI API (hyphenated names) first, then falls back to `gimpfu` (underscore names).

## Tools Reference

All 17 portmanteau tools and their operations:

| Tool | Ops | Operations |
|------|-----|------------|
| `gimp_file` | 6 | load, save, convert, info, validate, list_formats |
| `gimp_transform` | 7 | resize, crop, rotate, flip, scale, perspective, autocrop |
| `gimp_color` | 12 | brightness_contrast, levels, curves, HSL, balance, invert, threshold, posterize, desaturate, colorize, auto_levels, auto_color |
| `gimp_filter` | 8 | blur, sharpen, noise, edge_detect, artistic, enhance, distort, light_shadow |
| `gimp_layer` | 8 | create, duplicate, delete, merge, flatten, reorder, properties, info |
| `gimp_analysis` | 8 | quality, statistics, histogram, compare, detect_issues, report, color_profile, metadata |
| `gimp_batch` | 6 | resize, convert, process, watermark, rename, optimize |
| `gimp_system` | 8 | status, help, diagnostics, cache, config, performance, tools, version |
| `gimp_pdb` | ∞ | pdb_call — any GIMP PDB procedure by name |
| `gimp_workspace` | 10 | list_images, current_image, undo, redo, undo_count, undo_group_start, undo_group_end, get_metadata, set_resolution, set_unit |
| `gimp_channel` | 8 | create, delete, list, set_color, set_opacity, set_show_masked, duplicate, info |
| `gimp_animation` | 5 | list_frames, set_frame_delay, optimize_for_gif, export_gif, frame_count |
| `gimp_paths` | 8 | create, delete, list, stroke, import_svg, export_svg, set_name, get_points |
| `gimp_parasites` | 9 | list_image, list_drawable, attach_image, attach_drawable, detach_image, detach_drawable, get_image, get_drawable, get_animation_delay |
| `gimp_gmic` | 4 | list_categories, list_filters, apply, apply_named |
| `gimp_gegl` | 2 | list_ops, apply (non-destructive GEGL ops) |
| `gimp_color_management` | 7 | profile_info, assign_profile, convert_profile, get_effective_profile, soft_proofing, simulation_profile, list_profiles |

## Python-Fu vs Script-Fu

| | Python-Fu | Script-Fu |
|---|-----------|-----------|
| Language | Python 3.12+ | Scheme (TinyScheme) |
| GIMP 3 support | `gi.repository` | Limited |
| Complexity | Full Python | Simple scripts |
| When used | All portmanteau tools | `execute_script_fu()` method |

The server prefers Python-Fu for everything. Script-Fu is available via `GimpCliWrapper` for legacy scripts.

## REST API Endpoints

All endpoints are served by the webapp backend on port **10773**.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Server health, GIMP mode, version, SOTA manifest |
| `/api/status` | GET | Same as `/api/health` (alias) |
| `/api/sota` | GET | SOTA feature manifest JSON |
| `/api/skills` | GET | List available GIMP skills |
| `/api/skills/{name}` | GET | Get skill content (SKILL.md) |
| `/api/tools` | GET | List registered tools and operations |
| `/mcp` | HTTP/SSE | FastMCP transport endpoint |
| `/` | Static | Webapp frontend (Vite build) |

### Health Response

```json
{
  "status": "healthy",
  "live_mode": {"mode": "live", "live_available": true},
  "config": {
    "gimp_executable": "C:\\Users\\...\\gimp-console-3.exe",
    "max_concurrent_processes": 3
  },
  "server_name": "gimp-mcp",
  "version": "4.0.0",
  "fastmcp": "3.2",
  "sota": {...}
}
```

## Webapp Frontend Pages

Access the dashboard at `http://localhost:10772` (Vite dev) or via the built frontend.

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | System overview, live status |
| Apps Hub | `/apps` | Installed apps and integrations |
| Chat | `/chat` | Conversational image editing |
| Editor | `/editor` | Image preview and editing |
| Tools | `/tools` | All available tools with docs |
| Skills | `/skills` | GIMP expert skills |
| API Docs | `/api-docs` | REST API reference |
| Status | `/status` | Health checks, diagnostics |
| Settings | `/settings` | Configuration management |
| Help | `/help` | User guide |
| About | `/about` | Version info |

## Justfile Reference

All 21 recipes:

| Category | Recipe | Description |
|----------|--------|-------------|
| **Dashboard** | `default` | Show the SOTA Industrial Dashboard |
| **Startup** | `start` | Start everything (backend + frontend + bridge) |
| | `start-gimp` | Start with GIMP restart |
| | `serve` | Backend only (uvicorn, reload) |
| | `webapp` | Frontend only (Vite dev) |
| | `build` | Build frontend for production |
| **Bridge** | `bridge-status` | Check if bridge is active |
| | `bridge-install` | Install bridge plugin to GIMP |
| **PDB** | `pdb` | Call any GIMP PDB procedure |
| | `tools` | List all registered MCP tools |
| **Testing** | `test` | Run all tests |
| | `test-cov` | Run tests with coverage |
| | `test-cli` | Test CLI batch mode |
| | `test-pdb` | Test PDB proxy |
| **Quality** | `lint` | Lint Python (ruff) + frontend (biome) |
| | `fix` | Auto-fix lint issues |
| **Hardening** | `check-sec` | Bandit security audit |
| | `audit-deps` | Safety audit of dependencies |
| **Cleanup** | `kill` | Kill processes on 10772/10773/10775 |
| | `clean` | Remove node_modules, dist, .venv, caches |
| | `clean-gimp` | Remove bridge plugin from GIMP |
