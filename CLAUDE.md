# CLAUDE.md — gimp-mcp

FastMCP 3.2+ server for professional image editing using GIMP.

## Quick Start
```powershell
uv run python -m gimp_mcp.main          # stdio
set MCP_PORT=10773 && uv run python -m gimp_mcp.main  # SSE
just lint                                # Ruff + Biome
```

## Ports
- Frontend: 10772, Backend: 10773, GIMP Bridge: 10824, Logging: 11062

## 17 Portmanteau Tools
| Tool | Operations | Mode |
|------|-----------|------|
| `gimp_file` | load, save, convert, info, validate, list_formats | READ_ONLY / MUTATING |
| `gimp_transform` | resize, crop, rotate, flip, scale, perspective, autocrop | MUTATING |
| `gimp_color` | brightness_contrast, levels, curves, color_balance, HSL, colorize, threshold, posterize, desaturate, invert, auto_levels, auto_color | MUTATING |
| `gimp_filter` | blur, sharpen, noise, edge_detect, artistic, enhance, distort, light_shadow | MUTATING |
| `gimp_layer` | create, duplicate, delete, merge, flatten, reorder, properties, info | MUTATING |
| `gimp_analysis` | quality, statistics, histogram, compare, detect_issues, report, color_profile, metadata | READ_ONLY |
| `gimp_batch` | resize, convert, process, watermark, rename, optimize, pbr_pack | MUTATING |
| `gimp_system` | status, help, diagnostics, cache, config, performance, tools, version | READ_ONLY |
| `gimp_workspace` | list_images, current_image, undo/redo, metadata, resolution | READ_ONLY |
| `gimp_channel` | create, delete, list, set_color, set_opacity, show_masked, duplicate, info | MUTATING |
| `gimp_animation` | list_frames, set_frame_delay, optimize_for_gif, export_gif, frame_count | MUTATING |
| `gimp_paths` | create, delete, list, stroke, import/export SVG, set_name, get_points | MUTATING |
| `gimp_parasites` | list/attach/detach image/drawable parasites | MUTATING |
| `gimp_color_management` | profile_info, assign/convert profile, soft_proofing, simulation, list_profiles | READ_ONLY |
| `gimp_gegl` | list_ops, apply (non-destructive GEGL graph) | MUTATING |
| `gimp_gmic` | list_categories, apply, apply_named (500+ G'MIC filters) | MUTATING |
| `gimp_pdb` | Call ANY GIMP PDB procedure by name | MUTATING |

## Linting
- Python: `ruff` (E/F/W/I/B/S/UP/RUF, line length 120)
- Webapp: `biome` (no console.log)
