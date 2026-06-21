# GIMP MCP Expert

## When to use

- Multi-step edits (load → transform → color → export) with explicit paths.
- Batch folders: always set **separate output directories**; never overwrite masters.
- When **sampling** is available, use `gimp_agentic_workflow` for a one-shot plan, then execute with portmanteau tools.
- For operations not covered by the 8 portmanteaus, use the **`gimp_pdb` universal proxy** to call any GIMP PDB procedure directly.

## Portmanteau tools

| Tool | Role |
|------|------|
| `gimp_file` | load, save, convert, info, validate, list_formats |
| `gimp_transform` | resize, crop, rotate, flip, scale, perspective, autocrop |
| `gimp_color` | brightness_contrast, levels, curves, hue_saturation, … |
| `gimp_filter` | blur, sharpen, noise, artistic, … |
| `gimp_layer` | create, duplicate, merge, flatten, … |
| `gimp_analysis` | quality, statistics, histogram, compare, … |
| `gimp_batch` | folder resize/convert/watermark |
| `gimp_system` | status, help, diagnostics, version |
| `gimp_pdb` | **Universal PDB proxy** — call any GIMP procedure by name (selections, text, channels, plug-ins, etc.) |
| `gimp_workspace` | list images, undo/redo, undo groups, metadata, resolution |
| `gimp_channel` | create, delete, list, set color/opacity, duplicate channels |
| `gimp_animation` | list frames, set delay, optimize/export GIF |
| `gimp_paths` | create, delete, stroke, import/export SVG, vector paths |
| `gimp_parasites` | XCF metadata: list, attach, detach parasites on images/drawables |
| `gimp_gmic` | G'MIC filter integration — 500+ filters via plug-in-gmic |
| `gimp_gegl` | GEGL non-destructive editing operations |
| `gimp_color_management` | ICC profiles, assignment, conversion, soft proofing |

## gimp_pdb

A generic escape hatch that accepts a **procedure name** (e.g. `gimp-selection-all`, `plug-in-gauss`, `gimp-text-layer-set-font`) and optional **positional args**. Runs via Live Bridge (TCP to running GIMP) or Headless CLI (batch mode). Use this for any operation not yet wrapped by the 8 domain tools.

### Examples
- `gimp_pdb("gimp-selection-all", [image_id])` — select entire image
- `gimp_pdb("gimp-selection-feather", [image_id, 5.0])` — feather selection
- `gimp_pdb("gimp-text-layer-set-font", [layer_id, "Arial"])` — change text font
- `gimp_pdb("plug-in-gauss", [image_id, layer_id, 5.0, 5.0, 0])` — Gaussian blur

## Safety

- Respect **allowed_directories** in server config.
- Prefer **copy-on-write** outputs (`output_path` distinct from `input_path`).
- If GIMP is headless-only, avoid live UI assumptions; use CLI/script-fu operations.

## FastMCP 3.2

- **Resources**: `resource://gimp/documentation/llms`, `resource://gimp/documentation/capabilities`
- **Skills**: this file at `skill://gimp-expert/SKILL.md`
- **Prompts**: `gimp_edit_session`, `gimp_batch_folder_prep`, `gimp_color_grading_pass`, `gimp_agentic_sampling_hint`
- **Prefab**: `gimp_capabilities_card` (rich UI in capable hosts)
