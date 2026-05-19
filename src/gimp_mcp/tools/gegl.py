"""
GIMP GEGL Operation Portmanteau Tool.

GEGL (Generic Graphics Library) is GIMP 3's non-destructive image processing
engine. GEGL operations are available via PDB procedures with the "gegl-" prefix.
"""

from __future__ import annotations

import json
import time
from typing import Any, Literal

from pydantic import BaseModel, Field


class GeglResult(BaseModel):
    """Result model for GEGL operations."""

    success: bool
    operation: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: str | None = None


def _make_list_ops_fu() -> str:
    """Generate Python-Fu code to list available GEGL operations."""
    return """
import json as _json
import traceback as _tb
try:
    try:
        _pdb
    except NameError:
        try:
            from gi.repository import Gimp
            _pdb = Gimp.get_pdb()
            _procs = _pdb.get_procedures()
            _gegl_ops = [p for p in _procs if 'gegl' in p.lower()]
            _ops = sorted(_gegl_ops)
            print('PDB_RESULT:' + _json.dumps({"success": True, "operations": _ops, "count": len(_ops)}))
        except (ImportError, AttributeError, TypeError):
            from gimpfu import pdb
            _procs = [p for p in dir(pdb) if 'gegl' in p.lower()]
            print('PDB_RESULT:' + _json.dumps({"success": True, "operations": sorted(_procs), "count": len(_procs)}))
except Exception as _e:
    print('PDB_RESULT:' + _json.dumps({"success": False, "error": _tb.format_exc()}))
"""


def _make_apply_fu(operation_name: str, config_string: str) -> str:
    """Generate Python-Fu code to apply a GEGL operation."""
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
            _images = Gimp.get_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({{"success": False, "error": "No image open in GIMP"}}))
            else:
                _image = _images[0]
                _drawable = _image.get_active_drawable()
                _proc = _pdb.lookup_procedure("gegl-apply")
                if _proc is None:
                    _proc = _pdb.lookup_procedure("gegl_apply")
                _config = _proc.create_config()
                _config.set_property("image", _image)
                _config.set_property("drawable", _drawable)
                _config.set_property("operation", {json.dumps(operation_name)})
                _config.set_property("config", {json.dumps(config_string)})
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
                pdb.gegl_apply(_image, _drawable, {json.dumps(operation_name)}, {json.dumps(config_string)})
                print('PDB_RESULT:' + _json.dumps({{"success": True, "result": "GEGL operation applied"}}))
except Exception as _e:
    print('PDB_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
"""


async def gimp_gegl(
    operation: Literal["list_ops", "apply"],
    operation_name: str | None = None,
    config_string: str | None = None,
    cli_wrapper: Any = None,
    config: Any = None,
) -> dict[str, Any]:
    """GEGL (Generic Graphics Library) operation portmanteau for GIMP MCP.

    [RATIONALE] GEGL operations power GIMP 3's non-destructive editing. This tool
    wraps the gegl-apply PDB procedure and operation discovery into a single interface.

    ## Return Format
    {"success": bool, "message": str, "data": {...}, "operation": str}

    ## Examples
    gimp_gegl(operation="list_ops")
    gimp_gegl(operation="apply", operation_name="gaussian-blur", config_string='{"radius": 5.0}')
    gimp_gegl(operation="apply", operation_name="crop", config_string='{"x": 0, "y": 0, "width": 800, "height": 600}')
    """
    start_time = time.time()

    try:
        if operation == "list_ops":
            result = await _list_gegl_ops(cli_wrapper)
        elif operation == "apply":
            if not operation_name:
                result = GeglResult(
                    success=False,
                    operation=operation,
                    message="operation_name is required for apply",
                    error="Missing parameter",
                ).model_dump()
            else:
                result = await _apply_gegl(operation_name, config_string or "{}", cli_wrapper)
        else:
            result = GeglResult(
                success=False,
                operation=operation,
                message=f"Unknown operation: {operation}",
                error="Invalid operation",
            ).model_dump()

        execution_time = (time.time() - start_time) * 1000
        result["execution_time_ms"] = round(execution_time, 2)
        return result

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return GeglResult(
            success=False,
            operation=operation,
            message=f"GEGL operation failed: {e!s}",
            error=str(e),
            execution_time_ms=round(execution_time, 2),
        ).model_dump()


async def _list_gegl_ops(cli_wrapper: Any) -> dict[str, Any]:
    """Query PDB for GEGL-related procedures."""
    exec_layer = cli_wrapper
    if exec_layer is None:
        return GeglResult(
            success=False,
            operation="list_ops",
            message="No GIMP execution layer available",
            error="GIMP offline",
        ).model_dump()

    code = _make_list_ops_fu()

    try:
        if hasattr(exec_layer, "execute_python_fu"):
            output = await exec_layer.execute_python_fu(code)
        else:
            return GeglResult(
                success=False, operation="list_ops", message="No execute_python_fu method", error="Missing method"
            ).model_dump()
    except Exception as e:
        return GeglResult(
            success=False, operation="list_ops", message=f"GIMP execution failed: {e!s}", error=str(e)
        ).model_dump()

    try:
        marker = "PDB_RESULT:"
        idx = output.find(marker)
        if idx >= 0:
            payload = json.loads(output[idx + len(marker) :])
            if payload.get("success"):
                ops = payload.get("operations", [])
                return GeglResult(
                    success=True,
                    operation="list_ops",
                    message=f"{len(ops)} GEGL operations available",
                    data={"operations": ops, "count": len(ops)},
                ).model_dump()
            return GeglResult(
                success=False,
                operation="list_ops",
                message=f"Failed to list GEGL ops: {payload.get('error')}",
                error=payload.get("error"),
            ).model_dump()
        return GeglResult(
            success=True,
            operation="list_ops",
            message="GEGL operations listed",
            data={"raw_output": output},
        ).model_dump()
    except Exception as e:
        return GeglResult(
            success=False,
            operation="list_ops",
            message=f"Failed to parse response: {e!s}",
            error=str(e),
            data={"raw": output},
        ).model_dump()


async def _apply_gegl(operation_name: str, config_string: str, cli_wrapper: Any) -> dict[str, Any]:
    """Apply a GEGL operation."""
    code = _make_apply_fu(operation_name, config_string)

    exec_layer = cli_wrapper
    if exec_layer is None:
        return GeglResult(
            success=False,
            operation="apply",
            message="No GIMP execution layer available",
            error="GIMP offline",
        ).model_dump()

    try:
        if hasattr(exec_layer, "execute_python_fu"):
            output = await exec_layer.execute_python_fu(code)
        else:
            return GeglResult(
                success=False, operation="apply", message="No execute_python_fu method", error="Missing method"
            ).model_dump()
    except Exception as e:
        return GeglResult(
            success=False, operation="apply", message=f"GIMP execution failed: {e!s}", error=str(e)
        ).model_dump()

    try:
        marker = "PDB_RESULT:"
        idx = output.find(marker)
        if idx >= 0:
            payload = json.loads(output[idx + len(marker) :])
            if payload.get("success"):
                return GeglResult(
                    success=True,
                    operation="apply",
                    message=f"GEGL operation '{operation_name}' applied",
                    data={"operation_name": operation_name, "config": config_string, "gimp_result": payload.get("result")},
                ).model_dump()
            return GeglResult(
                success=False,
                operation="apply",
                message=f"GEGL operation failed: {payload.get('error')}",
                error=payload.get("error"),
            ).model_dump()
        return GeglResult(
            success=True,
            operation="apply",
            message=f"GEGL operation '{operation_name}' applied",
            data={"operation_name": operation_name, "config": config_string, "raw_output": output},
        ).model_dump()
    except Exception as e:
        return GeglResult(
            success=False,
            operation="apply",
            message=f"Failed to parse response: {e!s}",
            error=str(e),
            data={"raw": output},
        ).model_dump()
