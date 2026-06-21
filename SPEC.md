# GIMP MCP — Gap Analysis & Expansion Plan

## 1. Executive Summary

**Current**: 8 portmanteau tools covering ~63 operations across file, transform, color, filter, layer, analysis, batch, and system domains. No live bridge integration to running GIMP.

**Reality**: GIMP's Python-Fu PDB exposes **~1000+ procedure calls**. Current coverage is **~6%** of the available API surface.

**Critical gaps**: Entire API domains are untouched — text layers, vector paths, channels, selections (programmatic), brushes, palettes, gradients, patterns, floating selections, color management, plug-in calls, display management, and the full Context API.

---

## 2. Current Coverage

| Tool | Operations | API Domain Coverage |
|------|-----------|-------------------|
| `gimp_file` | load, save, convert, info, validate, list_formats | Mimics existing Python PIL (not GIMP-native file ops) |
| `gimp_transform` | resize, crop, rotate, flip, scale, perspective, autocrop | Uses PIL, not `gimp_image_scale` / `plug_in_autocrop` |
| `gimp_color` | brightness_contrast, levels, curves, HSL, etc. | Thin PIL wrappers, not `gimp_drawable_levels` etc. |
| `gimp_filter` | blur, sharpen, noise, edge, artistic, enhance, distort | PIL-only, misses 50+ `plug_in_*` filters |
| `gimp_layer` | create, duplicate, delete, merge, flatten, etc. | Basic layer CRUD, no masks, channels, blend modes |
| `gimp_analysis` | quality, statistics, histogram, compare | Thin PIL wrappers |
| `gimp_batch` | resize, convert, process, watermark, rename, optimize | No GIMP batch integration |
| `gimp_system` | status, help, diagnostics, cache, config | Basic system info |

**Key problem**: Most operations go through Pillow (PIL), not through GIMP's own Python-Fu PDB. This means:
- GIMP-specific image features are unavailable (layers, channels, paths, etc.)
- Format support is limited to PIL, not GIMP's 40+ file formats
- No Script-Fu / plug-in ecosystem access

---

## 3. Gap Matrix

| GIMP API Domain | Total Ops | Covered | % | Priority | Notes |
|---|---|---|---|---|---|
| **Image** | ~40 | 3 | 8% | P0 | Missing resize_to_image, undo groups, metadata, grids |
| **Layer** | ~60 | 8 | 13% | P0 | Masks, lock, linked, blend modes, floating sel, alpha |
| **Drawable** | ~20 | 0 | 0% | P0 | fill, get/set pixel, update, offsets, type detection |
| **Selection** | ~30 | 0 | 0% | **P0** | **Entirely missing** — all/ none/ invert/ feather/ grow/ shrink/ border/ by-color/ rectangle/ ellipse |
| **Channel** | ~15 | 0 | 0% | **P0** | **Entirely missing** — create, delete, color, opacity |
| **Color** | ~20 | 6 | 30% | P0 | Best-covered, but missing threshold, posterize, colorize, color-balance via GIMP PDB |
| **Filter (plug-in)** | ~80 | 0 | 0% | **P0** | **Entirely missing** — 50+ GIMP plug-in filters untouched |
| **Text** | ~25 | 0 | 0% | **P0** | **Entirely missing** — text layers, fonts, sizing, kerning |
| **Vectors/Paths** | ~20 | 0 | 0% | P1 | SVG import/export, stroke paths, B�zier |
| **File (GIMP-native)** | ~50 | 0 | 0% | P1 | 40+ GIMP-native file format handlers, XCF format |
| **Brush** | ~10 | 0 | 0% | P1 | Brush selection, creation, spacing |
| **Font** | ~5 | 0 | 0% | P1 | Font listing, selection |
| **Gradient** | ~5 | 0 | 0% | P1 | Gradient selection, color-at-point |
| **Palette** | ~5 | 0 | 0% | P1 | Palette listing, color extraction |
| **Pattern** | ~5 | 0 | 0% | P1 | Pattern selection, info |
| **Context** | ~20 | 0 | 0% | P1 | Push/pop, foreground/background, feather, interpolation |
| **Color Management** | ~15 | 0 | 0% | P1 | ICC profiles, proofing, conversion |
| **Display/UI** | ~10 | 0 | 0% | P2 | Display new/ delete, progress bar, messages |
| **Plug-in Registration** | ~5 | 0 | 0% | P2 | Extend GIMP with custom plug-ins |
| **Floating Selection** | ~5 | 0 | 0% | P1 | Anchor, attach, to-layer |
| **Image Metadata** | ~5 | 0 | 0% | P1 | EXIF, XMP, parasites |
| **Totals** | **~450+** | **~17** | **~4%** | | |

---

## 4. Critical Gaps (Top 10)

### 1. Selection API — COMPLETELY MISSING
No programmatic selections. Can't select by color, feather, grow, shrink, border, or create rectangle/ellipse selections.
- `gimp_selection_all`, `gimp_selection_none`, `gimp_selection_invert`
- `gimp_selection_feather`, `gimp_selection_grow`, `gimp_selection_shrink`, `gimp_selection_border`
- `gimp_image_select_rectangle`, `gimp_image_select_ellipse`, `gimp_image_select_color`, `gimp_image_select_contiguous_color`
- `gimp_free_select`, `gimp_fuzzy_select`, `gimp_by_color_select`
- `gimp_selection_save`, `gimp_selection_load`
- `gimp_selection_float`

### 2. Text Layers — COMPLETELY MISSING
No text layer creation, editing, or formatting.
- `gimp_text_layer_new`, `gimp_text_layer_set_text`, `gimp_text_layer_get_text`
- `gimp_text_layer_set_font`, `gimp_text_layer_set_font_size`
- `gimp_text_layer_set_color`, `gimp_text_layer_set_justification`
- `gimp_text_layer_set_letter_spacing`, `gimp_text_layer_set_line_spacing`
- `gimp_text_layer_set_box`, `gimp_text_layer_get_bounds`

### 3. Layer Masks — COMPLETELY MISSING
No layer mask support.
- `gimp_layer_add_mask`, `gimp_layer_remove_mask`, `gimp_layer_apply_mask`
- `gimp_layer_get_mask`, `gimp_layer_get_edit_mask`, `gimp_layer_set_edit_mask`
- `gimp_layer_get_show_mask`, `gimp_layer_set_show_mask`
- `gimp_layer_get_lock_alpha`, `gimp_layer_set_lock_alpha`

### 4. Channels — COMPLETELY MISSING
Can't create or manipulate channels.
- `gimp_channel_new`, `gimp_channel_copy`, `gimp_channel_delete`
- `gimp_channel_set_color`, `gimp_channel_set_opacity`, `gimp_channel_set_show_masked`

### 5. GIMP Native Plug-in Filters — COMPLETELY MISSING
Current filters use PIL. GIMP has 50+ plug-in filters untouched.
- `plug_in_gauss`, `plug_in_gauss_iir`, `plug_in_gauss_rle`
- `plug_in_unsharp_mask`, `plug_in_sharpen`
- `plug_in_noise_hsv/rgb/pick/solid/spread/cie_lch`
- `plug_in_edge_laplace/sobel/dog`
- `plug_in_oilify`, `plug_in_cartoon`, `plug_in_cubism`, `plug_in_weave`
- `plug_in_drop_shadow`, `plug_in_perspective_shadow`
- `plug_in_emboss`, `plug_in_engrave`
- `plug_in_red_eye_removal`
- `plug_in_whirl_pinch`, `plug_in_ripple`, `plug_in_waves`, `plug_in_wind`, `plug_in_warp`
- `plug_in_pixelize`, `plug_in_mblur`
- `plug_in_lighting_effects`, `plug_in_gradient_flare`
- `plug_in_mosaic`, `plug_in_newsprint`
- `plug_in_normalize`, `plug_in_stretch_contrast`, `plug_in_stretch_hsv`
- `plug_in_autocrop_layer`, `plug_in_autocrop_image`, `plug_in_guillotine`

### 6. Vector Paths — COMPLETELY MISSING
No SVG path operations.
- `gimp_vectors_new`, `gimp_vectors_delete`, `gimp_vectors_copy`
- `gimp_vectors_stroke_new_from_points`
- `gimp_vectors_import_from_file`, `gimp_vectors_export_to_file`
- `gimp_vectors_stroke_draw`
- `gimp_drawable_edit_stroke_item`, `gimp_drawable_edit_stroke_selection`

### 7. GIMP-Native File Formats — COMPLETELY MISSING
Current file ops use PIL. GIMP has 40+ native format handlers.
- `file_psd_load/save`, `file_webp_load/save`, `file_pdf_load/save`
- `file_svg_load`, `file_exr_load`
- `file_xcf_load/save` (GIMP native format)
- `file_ico_load/save`, `file_tiff_load/save`
- `plug_in_jpeg_save`, `plug_in_png_save`, `plug_in_gif_save`, `plug_in_webp_save`

### 8. Blend Modes (27 modes) — PARTIAL
Current layer tool doesn't expose GIMP's 27 blend modes.
- `gimp_context_set_paint_mode` with all `LAYER_MODE_*` constants
- `gimp_layer_set_mode` with proper mode enum
- Forward-compatible with GIMP 3.0 `GimpLayerMode` enum

### 9. Context API — COMPLETELY MISSING
No context management, which is essential for complex operations.
- `gimp_context_push`, `gimp_context_pop`
- `gimp_context_set_foreground`, `gimp_context_set_background`
- `gimp_context_set_opacity`, `gimp_context_set_paint_mode`
- `gimp_context_set_antialias`, `gimp_context_set_feather`
- `gimp_context_set_interpolation`, `gimp_context_set_transform_direction`
- `gimp_context_set_sample_merged`, `gimp_context_set_sample_criterion`
- `gimp_context_set_brush`, `gimp_context_set_pattern`, `gimp_context_set_gradient`, `gimp_context_set_font`

### 10. Color Management — COMPLETELY MISSING
No ICC profile support.
- `gimp_image_get_color_profile`, `gimp_image_set_color_profile`
- `gimp_image_convert_color_profile`, `gimp_image_convert_precision`
- `gimp_image_get_effective_color_profile`
- `gimp_color_profile_new_from_file`, `gimp_color_profile_get_info`
- `gimp_image_get_simulation_profile`, `gimp_image_set_soft_proofing`

---

## 5. Missing API Domains (Complete)

| Domain | Ops | Impact |
|---|---|---|
| Selection | ~30 | Every filter/color operation benefits from programmatic selections |
| Text | ~25 | users need labels, watermarks, captions |
| Channels | ~15 | Advanced compositing, alpha manipulation |
| Vectors/Paths | ~20 | SVG workflows, precision masking |
| Filters (plug-ins) | ~80 | 50+ GIMP effects not reproducible in PIL |
| Brushes | ~10 | Custom brush workflows |
| Fonts | ~5 | Font discovery for text layers |
| Gradients | ~5 | Gradient fills |
| Palettes | ~5 | Color palette extraction |
| Patterns | ~5 | Pattern fills |
| Context | ~20 | Required for safe stateful operations |
| Color Management | ~15 | Professional print/display workflows |
| Floating Selection | ~5 | Floater operations |
| File (native) | ~50 | 40+ GIMP-native format support |
| Display/UI | ~10 | Headless vs visible mode |
| Plug-in Registration | ~5 | Extending GIMP |

---

## 6. Priority Implementation Plan

### Phase 1 — P0: Must-Have (core infrastructure)

| # | Feature | Files | Effort |
|---|---------|-------|--------|
| 1 | **Live Bridge integration** — connect to running GIMP via TCP bridge, not PIL fallback | `bridge_wrapper.py`, `cli_wrapper.py`, `interaction_manager.py` | 2d |
| 2 | **GIMP PDB proxy** — generic `call_pdb(procedure, *args)` tool that proxies any PDB call | `tools/pdb.py` new | 1d |
| 3 | **Selection API** — new portmanteau `gimp_selection` with all selection operations | `tools/selection.py` new | 2d |
| 4 | **Text Layer API** — new portmanteau `gimp_text` with full text layer control | `tools/text.py` new | 2d |
| 5 | **Layer Mask API** — extend `gimp_layer` with mask operations | `tools/layer.py` extend | 1d |
| 6 | **Channel API** — new portmanteau `gimp_channel` or extend `gimp_layer` | `tools/channel.py` new | 1d |
| 7 | **Plug-in Filter bridge** — universal `gimp_filter_plugin` that calls any `plug_in_*` by name | `tools/filter_plugins.py` new | 2d |
| 8 | **Context API** — `gimp_context_push/pop` wrapper around all context operations | `tools/context.py` new | 1d |

### Phase 2 — P1: High-Value

| # | Feature | Effort |
|---|---------|--------|
| 9 | **Drawable Operations** — fill, pixel get/set, update, offsets, type | 1d |
| 10 | **Vector Path API** — SVG path creation, import, export, stroke | 2d |
| 11 | **GIMP File Format API** — native PSD/SVG/WebP/PDF/EXR/XCF via GIMP | 2d |
| 12 | **Floating Selection** — float/anchor/to-layer | 0.5d |
| 13 | **Brush/Font/Gradient/Palette/Pattern** — discovery and selection | 1d |
| 14 | **Blend Mode Enum** — all 27 `GimpLayerMode` values properly typed | 0.5d |
| 15 | **Metadata API** — EXIF/XMP via GIMP's metadata handlers | 1d |
| 16 | **Color Management** — ICC profiles, proofing, conversion | 2d |

### Phase 3 — P2: Surface Expansion

| # | Feature | Effort |
|---|---------|--------|
| 17 | **Display/UI API** — open/close displays, progress bars | 1d |
| 18 | **Plug-in Registration** — register custom GIMP plug-ins from MCP | 2d |
| 19 | **Undo Groups** — bracket operations in undo groups | 0.5d |
| 20 | **Image Grid/Guides** — grid config, guide creation | 1d |

---

## 7. Architecture Recommendations

### Replace PIL with GIMP PDB

Current: `PIL.Image.open() -> numpy -> PIL.Image.save()`
Target: `bridge.execute_python_fu("gimp_file_load", ...) -> bridge.execute_python_fu("gimp_file_save", ...)`

All tools should default to GIMP PDB calls when bridge is live, falling back to PIL only when headless.

### Generic PDB Proxy Tool

```python
@mcp.tool()
async def gimp_pdb_call(
    procedure: Annotated[str, "GIMP PDB procedure name (e.g. 'gimp_selection_feather')"],
    args: Annotated[list, "Positional arguments for the procedure"],
    kwargs: Annotated[dict | None, "Keyword arguments"] = None,
) -> dict:
    """Call any GIMP PDB procedure by name. Universal escape hatch."""
```

This single tool immediately unlocks the entire ~1000-procedure PDB without needing individual wrappers.

### Bridge-First, PIL-Fallback Pattern

```
GimpInteractionManager
  ├── Live mode → bridge_wrapper.execute_python_fu(code)
  └── Headless mode → cli_wrapper.execute_script_fu(script) or PIL fallback
```

### New Portmanteau Strategy

Instead of creating 10 more portmanteau tools (which increases the agent's cognitive load), add the **generic PDB proxy** as a universal escape hatch, then build domain-specific portmanteaus only for the most common workflows (selection, text, channels, filters).

---

## 8. GIMP Detection & Bridge Gap

Current broken state:
- **GIMP 3.2.4** is installed (Windows Store AppX)
- **Bridge port 10774** is squatted by a node process (windows-operations-mcp drift)
- **Cannot kill** the squatter because it's inside the Windows Store AppContainer sandbox
- **GIMP's bundled Python 3.14** cannot be invoked from outside the sandbox

Fix:
1. The `start.ps1` must kill ALL squatters including on port 10774
2. Alternative: start GIMP with `--no-interface` and `--python-fu` flags to bypass the Store sandbox issue
3. Or: use the `gimp-3.exe -b` (batch) interface directly instead of the TCP bridge

---

## 9. Effort Estimates

| Phase | Tools | Days |
|-------|-------|------|
| Phase 1 — P0 | 8 features | ~12 days |
| Phase 2 — P1 | 8 features | ~10 days |
| Phase 3 — P2 | 4 features | ~4 days |
| **Total** | **20 features** | **~26 days** |

---

## 10. Quick Wins (do first)

1. **Generic PDB proxy tool** (`gimp_pdb_call`) — unlocks 1000+ procedures instantly. 1 day.
2. **Start.ps1 fix** — include port 10774 in port clearing. 0.5 day.
3. **Fix bridge detection** — correctly detect running GIMP 3.2 via process list and Windows Store paths. 0.5 day.
