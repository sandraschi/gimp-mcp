# Tools — gimp-mcp

18 portmanteau MCP tools; every tool takes an `operation` param and returns
`{success, message, data, operation}`. Full schemas: Tools Explorer page
(`http://localhost:10772`) or `GET /api/tools`.

| Tool | Ops | Mode |
|------|-----|------|
| `gimp_file` | load, save, convert, info, validate, list_formats | mixed |
| `gimp_transform` | resize, crop, rotate, flip, scale, perspective, autocrop | MUTATING |
| `gimp_color` | brightness_contrast, levels, curves, HSL, balance, auto, invert, threshold, posterize, desaturate, colorize | MUTATING |
| `gimp_filter` | blur, sharpen, noise, edge_detect, artistic, enhance, distort, light_shadow | MUTATING |
| `gimp_layer` | create, duplicate, merge, flatten, opacity, blend, reorder, info | MUTATING |
| `gimp_analysis` | quality, statistics, histogram, compare, detect_issues, report, color_profile, metadata | READ_ONLY |
| `gimp_batch` | resize, convert, process, watermark, rename, optimize, pbr_pack | MUTATING |
| `gimp_system` | status, help, diagnostics, cache, config, performance, tools, version | READ_ONLY |
| `gimp_workspace` | list_images, current_image, undo, redo, metadata, resolution | READ_ONLY |
| `gimp_channel` | create, delete, list, set_color, set_opacity, duplicate, info | MUTATING |
| `gimp_animation` | list_frames, set_frame_delay, optimize_for_gif, export_gif, frame_count | MUTATING |
| `gimp_paths` | create, delete, list, stroke, import/export SVG, set_name, get_points | MUTATING |
| `gimp_parasites` | list, attach, detach (image/drawable XCF metadata) | MUTATING |
| `gimp_gmic` | list_categories, apply, apply_named, list_filters (500+ filters) | MUTATING |
| `gimp_gegl` | list_ops, apply (non-destructive) | MUTATING |
| `gimp_color_management` | profile_info, assign, convert, soft_proofing | MUTATING |
| `gimp_pdb` | **universal proxy**: any GIMP PDB procedure by name + args | MUTATING |
| `gimp_snapshot` | `get_state_snapshot`: live base64 PNG (region crop, max_size) | READ_ONLY |

## Agentic

`gimp_agentic_workflow` plans multi-step edits via `ctx.sample()` with
client-side fallback. Prompts: `gimp_edit_session`, `gimp_batch_folder_prep`,
`gimp_color_grading_pass`, `gimp_agentic_sampling_hint`. Resources:
`resource://gimp/documentation/*`, `skill://gimp-expert/SKILL.md`.
Prefab card: `gimp_capabilities_card` (`app=True`).

## REST (webapp-consumed)

`/api/health`, `/api/status`, `/api/capabilities`, `/api/sota`,
`/api/skills`, `/api/tools`, `/api/demos`, `/api/llm/detect`,
`/api/llm/chat`, `/api/llm/understand`, `/api/llm/suggest`,
`/api/v1/tool`, `/api/v1/diagnostics`, `POST /api/shutdown`.
