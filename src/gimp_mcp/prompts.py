"""
GIMP MCP — FastMCP 3.2 prompt templates (registry for agents and IDE hosts).
"""

from fastmcp import FastMCP


def register_all_prompts(mcp: FastMCP) -> None:
    """Register parameterized prompts for GIMP editing workflows."""

    @mcp.prompt(
        name="gimp_edit_session",
        description="Plan a safe, step-by-step GIMP session for a stated editing goal.",
        tags={"gimp", "workflow", "editing"},
    )
    def gimp_edit_session(goal: str = "prepare images for web") -> str:
        return f"""
### GIMP MCP — Editing session plan

**Goal:** {goal}

**Use the portmanteau tools** (`gimp_file`, `gimp_transform`, `gimp_color`, `gimp_filter`, `gimp_layer`, `gimp_analysis`, `gimp_batch`, `gimp_system`):
1. **Ingest**: `gimp_file` — validate paths, load, inspect metadata (`operation=info` / `validate`).
2. **Geometry**: `gimp_transform` — resize/crop to target dimensions; keep backups via separate output paths.
3. **Color**: `gimp_color` — levels / brightness_contrast before heavy filters.
4. **Creative**: `gimp_filter` — blur/sharpen/artistic as needed.
5. **Layers**: `gimp_layer` — non-destructive edits where possible; merge when final.
6. **QC**: `gimp_analysis` — histogram / quality before export.
7. **Ship**: `gimp_file` — convert to delivery format; `gimp_batch` for folders.

**Safety:** Stay within configured allowed directories; never overwrite sources without a new path.
"""

    @mcp.prompt(
        name="gimp_batch_folder_prep",
        description="Checklist for batch-processing a directory of images with GIMP MCP.",
        tags={"gimp", "batch", "automation"},
    )
    def gimp_batch_folder_prep(input_glob: str = "*.jpg", output_format: str = "webp") -> str:
        return f"""
### Batch folder workflow (GIMP MCP)

**Inputs:** pattern `{input_glob}` → **Output format:** `{output_format}`

1. List files under an allowed directory (host file tools or `gimp_system` diagnostics).
2. `gimp_batch` — `operation=resize` or `convert` with explicit `input_directory` / `output_directory`.
3. Spot-check with `gimp_analysis` on 1-2 samples.
4. Verify disk space and paths before large runs.

Use `gimp_system` `operation=help` if operation names are unclear.
"""

    @mcp.prompt(
        name="gimp_color_grading_pass",
        description="Order of operations for a cinematic color pass (levels → grade → export).",
        tags={"gimp", "color", "grading"},
    )
    def gimp_color_grading_pass(mood: str = "neutral documentary") -> str:
        return f"""
### Color grading pass — mood: **{mood}**

Recommended order on a flattened or duplicate layer:
1. `gimp_color` `brightness_contrast` — small moves.
2. `gimp_color` `levels` or `curves` — set black/white points.
3. `gimp_color` `hue_saturation` — separate hue vs saturation.
4. Optional `gimp_filter` `sharpen` — mild, after resize.
5. Export with `gimp_file` `convert` — embed profile if required.

If sampling is available, ask the model for a short rationale before destructive merges.
"""

    @mcp.prompt(
        name="gimp_agentic_sampling_hint",
        description="When to use server-side sampling vs client-only tool loops (SEP-1577).",
        tags={"gimp", "sampling", "agentic"},
    )
    def gimp_agentic_sampling_hint() -> str:
        return """
### Agentic workflows & sampling (FastMCP 3.2)

- **Sampling** (`ctx.sample` / `gimp_agentic_workflow`): Use when the host supports MCP sampling and you want the **server-side model** to plan or explain the next GIMP steps in one turn.
- **Tool loops**: Use portmanteau tools directly when the **client LLM** already orchestrates the sequence.
- **Prefab tools** (`gimp_capabilities_card`): Rich cards in hosts that render MCP app UI.
- **Skills**: Read `skill://gimp-expert/SKILL.md` for full conventions.

Prefer explicit output paths and non-destructive duplicates until the final export.
"""


__all__ = ["register_all_prompts"]
