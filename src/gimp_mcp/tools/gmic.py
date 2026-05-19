"""
GIMP G'MIC Filter Integration Portmanteau Tool.

G'MIC is a plugin providing 500+ image filters. This tool provides
access to G'MIC filters through GIMP's plug-in-gmic PDB procedure.
"""

from __future__ import annotations

import json
import time
from typing import Any, Literal

from pydantic import BaseModel, Field


class GmicResult(BaseModel):
    """Result model for G'MIC operations."""

    success: bool
    operation: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: str | None = None


GMIC_CATEGORIES: dict[str, str] = {
    "artistic": "Artistic filters (oil paint, watercolor, sketch, etc.)",
    "blur": "Blur and smoothing filters",
    "colors": "Color adjustments and corrections",
    "contours": "Edge detection and contour extraction",
    "deform": "Deformation and warping effects",
    "degrade": "Degradation effects (film grain, dust, etc.)",
    "details": "Detail enhancement and sharpening",
    "frames": "Frames and borders",
    "layers": "Layer effects and compositing",
    "light": "Lighting and glow effects",
    "patterns": "Pattern generation and texturing",
    "repair": "Restoration and repair filters",
    "rendered": "Rendered 3D effects",
    "filmic": "Filmic tone mapping and HDR",
}

KNOWN_FILTERS: dict[str, str] = {
    "fx_meteor": "-fx_meteor",
    "fx_rays": "-fx_rays",
    "fx_light_glow": "-fx_light_glow",
    "blur_gaussian": "-blur_gaussian 5",
    "blur_motion": "-blur_motion 10,45",
    "colors_balance": "-colors_balance 50,50",
    "colors_curves": "-colors_curves 0,0,255,255",
    "details_sharpen": "-details_sharpen 50",
    "repair_denoise": "-repair_denoise 10,1",
    "repair_hotpixels": "-repair_hotpixels 3",
    "rendered_clouds": "-rendered_clouds 128,128,128,0.5",
    "rendered_flame": "-rendered_flame",
    "artistic_oilpaint": "-artistic_oilpaint 4,60",
    "artistic_watercolor": "-artistic_watercolor 20,0.5",
    "artistic_pencil": "-artistic_pencil 30,60,0",
    "filmic_tone_map": "-filmic_tone_map 0.5,1,0.5",
    "light_glow": "-light_glow 5,50,0.5",
    "light_shadows": "-light_shadows 50,50",
    "patterns_halftone": "-patterns_halftone 4,0,45",
    "deform_spherize": "-deform_spherize 50,0,0",
    "deform_twirl": "-deform_twirl 50,0,0,0",
}


def _make_gmic_fu(filter_command: str) -> str:
    """Generate Python-Fu code to apply a G'MIC filter."""
    return f"""
import json as _json
import traceback as _tb
try:
    try:
        _pdb
    except NameError:
        try:
            from gi.repository import Gimp
            _pdb = Gimp.get_pdb()
            _proc = _pdb.lookup_procedure("plug-in-gmic")
            _images = Gimp.get_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({{"success": False, "error": "No image open in GIMP"}}))
            else:
                _image = _images[0]
                _drawable = _image.get_active_drawable()
                _config = _proc.create_config()
                _config.set_property("run-mode", 0)
                _config.set_property("image", _image)
                _config.set_property("drawable", _drawable)
                _config.set_property("filter-string", {json.dumps(filter_command)})
                _result = _proc.run(_config)
                print('PDB_RESULT:' + _json.dumps({{"success": True, "result": str(_result)}}))
        except (ImportError, AttributeError, TypeError):
            from gimpfu import pdb
            _images = pdb.gimp_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({{"success": False, "error": "No image open in GIMP"}}))
            else:
                _image = _images[0]
                _drawable = pdb.gimp_image_get_active_drawable(_image)
                pdb.plug_in_gmic(_image, _drawable, {json.dumps(filter_command)})
                print('PDB_RESULT:' + _json.dumps({{"success": True, "result": "G'MIC filter applied"}}))
except Exception as _e:
    print('PDB_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
"""


async def gimp_gmic(
    operation: Literal["list_categories", "apply", "apply_named", "list_filters"],
    filter_command: str | None = None,
    filter_name: str | None = None,
    filter_params: dict[str, Any] | None = None,
    cli_wrapper: Any = None,
    config: Any = None,
) -> dict[str, Any]:
    """G'MIC filter integration portmanteau for GIMP MCP.

    [RATIONALE] G'MIC provides 500+ filters through a single PDB procedure
    (plug-in-gmic). This tool consolidates category listing, raw filter execution,
    and named filter dispatch into one interface.

    ## Return Format
    {"success": bool, "message": str, "data": {...}, "operation": str}

    ## Examples
    gimp_gmic(operation="list_categories")
    gimp_gmic(operation="apply", filter_command="-fx_meteor")
    gimp_gmic(operation="apply_named", filter_name="blur_gaussian", filter_params={"radius": "10"})
    """
    start_time = time.time()

    try:
        if operation == "list_categories":
            result = _list_categories()
        elif operation == "list_filters":
            result = _list_filters()
        elif operation == "apply":
            if not filter_command:
                result = GmicResult(
                    success=False, operation=operation, message="filter_command is required for apply", error="Missing parameter"
                ).model_dump()
            else:
                result = await _apply_filter(filter_command, cli_wrapper)
        elif operation == "apply_named":
            if not filter_name:
                result = GmicResult(
                    success=False, operation=operation, message="filter_name is required for apply_named", error="Missing parameter"
                ).model_dump()
            else:
                resolved = _resolve_named_filter(filter_name, filter_params)
                if not resolved["success"]:
                    result = GmicResult(
                        success=False, operation=operation, message=resolved["message"], error=resolved.get("error")
                    ).model_dump()
                else:
                    result = await _apply_filter(resolved["command"], cli_wrapper)
        else:
            result = GmicResult(
                success=False, operation=operation, message=f"Unknown operation: {operation}", error="Invalid operation"
            ).model_dump()

        execution_time = (time.time() - start_time) * 1000
        result["execution_time_ms"] = round(execution_time, 2)
        return result

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return GmicResult(
            success=False,
            operation=operation,
            message=f"G'MIC operation failed: {e!s}",
            error=str(e),
            execution_time_ms=round(execution_time, 2),
        ).model_dump()


def _list_categories() -> dict[str, Any]:
    """Return known G'MIC filter categories."""
    categories = [{"name": k, "description": v} for k, v in GMIC_CATEGORIES.items()]
    return GmicResult(
        success=True,
        operation="list_categories",
        message=f"{len(categories)} G'MIC filter categories available",
        data={"categories": categories, "total": len(categories)},
    ).model_dump()


def _list_filters() -> dict[str, Any]:
    """Return known G'MIC filter presets."""
    filters = [{"name": k, "command": v} for k, v in KNOWN_FILTERS.items()]
    return GmicResult(
        success=True,
        operation="list_filters",
        message=f"{len(filters)} G'MIC filter presets available",
        data={"filters": filters, "total": len(filters)},
    ).model_dump()


def _resolve_named_filter(name: str, params: dict[str, Any] | None) -> dict[str, Any]:
    """Resolve a named filter to a G'MIC command string with optional params."""
    base = KNOWN_FILTERS.get(name)
    if base is None:
        return {"success": False, "message": f"Unknown filter: {name}", "error": "Filter not found in presets"}

    if params:
        parts = base.split(None, 1)
        if len(parts) == 2:
            base_name = parts[0]
            existing_args = parts[1]
            existing_values = existing_args.split(",")
            for i, (k, v) in enumerate(params.items()):
                if i < len(existing_values):
                    existing_values[i] = str(v)
                else:
                    existing_values.append(str(v))
            base = f"{base_name} {','.join(existing_values)}"

    return {"success": True, "command": base}


async def _apply_filter(filter_command: str, cli_wrapper: Any) -> dict[str, Any]:
    """Execute a G'MIC filter via generated Python-Fu code."""
    code = _make_gmic_fu(filter_command)

    exec_layer = cli_wrapper
    if exec_layer is None:
        return GmicResult(
            success=False, operation="apply", message="No GIMP execution layer available", error="GIMP offline"
        ).model_dump()

    try:
        if hasattr(exec_layer, "execute_python_fu"):
            output = await exec_layer.execute_python_fu(code)
        else:
            return GmicResult(
                success=False, operation="apply", message="Execution layer has no execute_python_fu", error="Missing method"
            ).model_dump()
    except Exception as e:
        return GmicResult(
            success=False, operation="apply", message=f"GIMP execution failed: {e!s}", error=str(e)
        ).model_dump()

    try:
        marker = "PDB_RESULT:"
        idx = output.find(marker)
        if idx >= 0:
            payload = json.loads(output[idx + len(marker) :])
            if payload.get("success"):
                return GmicResult(
                    success=True,
                    operation="apply",
                    message=f"G'MIC filter applied: {filter_command}",
                    data={"filter_command": filter_command, "gimp_result": payload.get("result")},
                ).model_dump()
            return GmicResult(
                success=False,
                operation="apply",
                message=f"G'MIC filter failed: {payload.get('error', 'unknown error')}",
                error=payload.get("error"),
            ).model_dump()
        return GmicResult(
            success=True,
            operation="apply",
            message=f"G'MIC filter applied: {filter_command}",
            data={"filter_command": filter_command, "raw_output": output},
        ).model_dump()
    except Exception as e:
        return GmicResult(
            success=False,
            operation="apply",
            message=f"Failed to parse GIMP response: {e!s}",
            error=str(e),
            data={"raw": output},
        ).model_dump()
