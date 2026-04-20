# GIMP MCP Expert

## When to use

- Multi-step edits (load → transform → color → export) with explicit paths.
- Batch folders: always set **separate output directories**; never overwrite masters.
- When **sampling** is available, use `gimp_agentic_workflow` for a one-shot plan, then execute with portmanteau tools.

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

## Safety

- Respect **allowed_directories** in server config.
- Prefer **copy-on-write** outputs (`output_path` distinct from `input_path`).
- If GIMP is headless-only, avoid live UI assumptions; use CLI/script-fu operations.

## FastMCP 3.2

- **Resources**: `resource://gimp/documentation/llms`, `resource://gimp/documentation/capabilities`
- **Skills**: this file at `skill://gimp-expert/SKILL.md`
- **Prompts**: `gimp_edit_session`, `gimp_batch_folder_prep`, `gimp_color_grading_pass`, `gimp_agentic_sampling_hint`
- **Prefab**: `gimp_capabilities_card` (rich UI in capable hosts)
