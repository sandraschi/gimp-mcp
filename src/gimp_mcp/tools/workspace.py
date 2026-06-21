"""
GIMP Workspace State Management Portmanteau Tool.

Manages GIMP image workspace state including image listing,
undo/redo history, image metadata, resolution, and unit settings.
"""

from __future__ import annotations

import json
import time
from typing import Any, Literal

from pydantic import BaseModel, Field


class WorkspaceResult(BaseModel):
    success: bool
    operation: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: str | None = None


def _make_workspace_fu(operation: str, image_id: int | None, **kw: Any) -> str:
    """Generate Python-Fu code for a workspace operation.

    Handles both GIMP 3 (gi.repository.Gimp) and GIMP 2.x (gimpfu).
    """
    if operation == "list_images":
        return '''
import json as _json, traceback as _tb
try:
    try:
        from gi.repository import Gimp
        _images = Gimp.get_images()
        _result = []
        for _img in _images:
            _result.append({
                "id": _img.get_id(),
                "width": _img.get_width(),
                "height": _img.get_height(),
            })
    except (ImportError, AttributeError):
        from gimpfu import pdb
        _list = pdb.gimp_image_list()
        _result = []
        if _list:
            for _img_id in _list:
                _result.append({
                    "id": _img_id,
                    "width": pdb.gimp_image_width(_img_id),
                    "height": pdb.gimp_image_height(_img_id),
                })
    print('WSP_RESULT:' + _json.dumps({"success": True, "result": _result}))
except Exception as _e:
    print('WSP_RESULT:' + _json.dumps({"success": False, "error": _tb.format_exc()}))
'''

    if operation == "current_image" and image_id is not None:
        return f'''
import json as _json, traceback as _tb
try:
    try:
        from gi.repository import Gimp
        _pdb = Gimp.get_pdb()
        _proc = _pdb.lookup_procedure("gimp-image-set-active")
        _config = _proc.create_config()
        _args = _proc.get_arguments()
        if _args:
            _config.set_property(_args[0].get_name(), {image_id})
        _proc.run(_config)
    except (ImportError, AttributeError):
        from gimpfu import pdb
        pdb.gimp_image_set_active({image_id})
    print('WSP_RESULT:' + _json.dumps({{"success": True, "result": {{"image_id": {image_id}}}}}))
except Exception as _e:
    print('WSP_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "current_image":
        return '''
import json as _json, traceback as _tb
try:
    try:
        from gi.repository import Gimp
        _img = Gimp.get_active_image()
        _result = {"image_id": _img.get_id()} if _img else None
    except (ImportError, AttributeError):
        from gimpfu import pdb
        _id = pdb.gimp_image_get_active()
        _result = {"image_id": _id} if _id else None
    print('WSP_RESULT:' + _json.dumps({"success": True, "result": _result}))
except Exception as _e:
    print('WSP_RESULT:' + _json.dumps({"success": False, "error": _tb.format_exc()}))
'''

    if operation == "undo_count":
        return f'''
import json as _json, traceback as _tb
_img_id = {image_id}
try:
    try:
        from gi.repository import Gimp
        _pdb = Gimp.get_pdb()
        def _g(name):
            _p = _pdb.lookup_procedure(name)
            if _p is None:
                return None
            _c = _p.create_config()
            _a = _p.get_arguments()
            if _a:
                _c.set_property(_a[0].get_name(), _img_id)
            _r = _p.run(_c)
            return _r.index(0)
        _result = {{
            "undo_count": _g("gimp-image-get-undo-count"),
            "redo_count": _g("gimp-image-get-redo-count"),
        }}
    except (ImportError, AttributeError):
        from gimpfu import pdb
        _result = {{
            "undo_count": pdb.gimp_image_get_undo_count(_img_id),
            "redo_count": pdb.gimp_image_get_redo_count(_img_id),
        }}
    print('WSP_RESULT:' + _json.dumps({{"success": True, "result": _result}}))
except Exception as _e:
    print('WSP_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "undo":
        return f'''
import json as _json, traceback as _tb
try:
    try:
        from gi.repository import Gimp
        _pdb = Gimp.get_pdb()
        _proc = _pdb.lookup_procedure("gimp-image-undo")
        _config = _proc.create_config()
        _config.set_property(_proc.get_arguments()[0].get_name(), {image_id})
        _proc.run(_config)
    except (ImportError, AttributeError):
        from gimpfu import pdb
        pdb.gimp_image_undo({image_id})
    print('WSP_RESULT:' + _json.dumps({{"success": True, "result": {{"image_id": {image_id}}}}}))
except Exception as _e:
    print('WSP_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "redo":
        return f'''
import json as _json, traceback as _tb
try:
    try:
        from gi.repository import Gimp
        _pdb = Gimp.get_pdb()
        _proc = _pdb.lookup_procedure("gimp-image-redo")
        _config = _proc.create_config()
        _config.set_property(_proc.get_arguments()[0].get_name(), {image_id})
        _proc.run(_config)
    except (ImportError, AttributeError):
        from gimpfu import pdb
        pdb.gimp_image_redo({image_id})
    print('WSP_RESULT:' + _json.dumps({{"success": True, "result": {{"image_id": {image_id}}}}}))
except Exception as _e:
    print('WSP_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "undo_group_start":
        return f'''
import json as _json, traceback as _tb
try:
    try:
        from gi.repository import Gimp
        _pdb = Gimp.get_pdb()
        _proc = _pdb.lookup_procedure("gimp-image-undo-group-start")
        _config = _proc.create_config()
        _config.set_property(_proc.get_arguments()[0].get_name(), {image_id})
        _proc.run(_config)
    except (ImportError, AttributeError):
        from gimpfu import pdb
        pdb.gimp_image_undo_group_start({image_id})
    print('WSP_RESULT:' + _json.dumps({{"success": True, "result": {{"image_id": {image_id}}}}}))
except Exception as _e:
    print('WSP_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "undo_group_end":
        return f'''
import json as _json, traceback as _tb
try:
    try:
        from gi.repository import Gimp
        _pdb = Gimp.get_pdb()
        _proc = _pdb.lookup_procedure("gimp-image-undo-group-end")
        _config = _proc.create_config()
        _config.set_property(_proc.get_arguments()[0].get_name(), {image_id})
        _proc.run(_config)
    except (ImportError, AttributeError):
        from gimpfu import pdb
        pdb.gimp_image_undo_group_end({image_id})
    print('WSP_RESULT:' + _json.dumps({{"success": True, "result": {{"image_id": {image_id}}}}}))
except Exception as _e:
    print('WSP_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "get_metadata":
        return f'''
import json as _json, traceback as _tb
_img_id = {image_id}
try:
    try:
        from gi.repository import Gimp, GObject
        _img = Gimp.Image.get_by_id(_img_id)
        _result = {{
            "image_id": _img_id,
            "width": _img.get_width(),
            "height": _img.get_height(),
            "resolution_x": float(_img.get_resolution()[0]),
            "resolution_y": float(_img.get_resolution()[1]),
            "unit": int(_img.get_unit()),
            "base_type": int(_img.get_base_type()),
            "precision": int(_img.get_precision()),
        }}
    except (ImportError, AttributeError):
        from gimpfu import pdb
        _result = {{
            "image_id": _img_id,
            "width": pdb.gimp_image_width(_img_id),
            "height": pdb.gimp_image_height(_img_id),
            "resolution_x": float(pdb.gimp_image_get_resolution(_img_id)),
            "resolution_y": float(pdb.gimp_image_get_resolution(_img_id)),
            "unit": int(pdb.gimp_image_get_unit(_img_id)),
            "base_type": int(pdb.gimp_image_base_type(_img_id)),
            "precision": int(pdb.gimp_image_get_precision(_img_id)),
        }}
    print('WSP_RESULT:' + _json.dumps({{"success": True, "result": _result}}))
except Exception as _e:
    print('WSP_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "set_resolution":
        xres = kw.get("xresolution", 72.0)
        yres = kw.get("yresolution", 72.0)
        return f'''
import json as _json, traceback as _tb
_img_id = {image_id}
try:
    try:
        from gi.repository import Gimp
        _pdb = Gimp.get_pdb()
        _proc = _pdb.lookup_procedure("gimp-image-set-resolution")
        _config = _proc.create_config()
        _args = _proc.get_arguments()
        _config.set_property(_args[0].get_name(), _img_id)
        _config.set_property(_args[1].get_name(), float({xres}))
        _config.set_property(_args[2].get_name(), float({yres}))
        _proc.run(_config)
    except (ImportError, AttributeError):
        from gimpfu import pdb
        pdb.gimp_image_set_resolution(_img_id, {xres}, {yres})
    print('WSP_RESULT:' + _json.dumps({{"success": True, "result": {{"resolution_x": {xres}, "resolution_y": {yres}}}}}))
except Exception as _e:
    print('WSP_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "set_unit":
        _unit = kw.get("unit", 0)
        return f'''
import json as _json, traceback as _tb
_img_id = {image_id}
try:
    try:
        from gi.repository import Gimp
        _pdb = Gimp.get_pdb()
        _proc = _pdb.lookup_procedure("gimp-image-set-unit")
        _config = _proc.create_config()
        _args = _proc.get_arguments()
        _config.set_property(_args[0].get_name(), _img_id)
        _config.set_property(_args[1].get_name(), int({_unit}))
        _proc.run(_config)
    except (ImportError, AttributeError):
        from gimpfu import pdb
        pdb.gimp_image_set_unit(_img_id, {_unit})
    print('WSP_RESULT:' + _json.dumps({{"success": True, "result": {{"unit": {_unit}}}}}))
except Exception as _e:
    print('WSP_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    return None


async def gimp_workspace(
    operation: Literal[
        "list_images",
        "current_image",
        "undo_count",
        "undo",
        "redo",
        "undo_group_start",
        "undo_group_end",
        "get_metadata",
        "set_resolution",
        "set_unit",
    ],
    image_id: int | None = None,
    xresolution: float = 72.0,
    yresolution: float = 72.0,
    unit: int = 0,
    *,
    interaction_manager=None,
    cli_wrapper=None,
    config=None,
) -> dict[str, Any]:
    """Comprehensive workspace state management portmanteau for GIMP MCP.

    [RATIONALE] All image workspace operations are consolidated into one portmanteau
    to prevent tool explosion while keeping image listing, undo/redo, metadata,
    resolution, and unit management discoverable under a single namespace.

    SUPPORTED OPERATIONS:
    - list_images: List all open images in GIMP
    - current_image: Get or set the active/frontmost image
    - undo_count: Get undo/redo history state for an image
    - undo: Undo last operation on an image
    - redo: Redo last undo on an image
    - undo_group_start: Start an undo group
    - undo_group_end: End an undo group
    - get_metadata: Get image dimensions, resolution, color mode, precision
    - set_resolution: Set image resolution (X and Y DPI)
    - set_unit: Set image unit (0=pixels, 1=inches, 2=mm, etc.)

    ## Return Format
    {"success": bool, "message": str, "data": {...}, "operation": str, "execution_time_ms": float}

    ## Examples
    gimp_workspace("list_images")
    gimp_workspace("current_image")
    gimp_workspace("current_image", image_id=42)
    gimp_workspace("undo", image_id=42)
    gimp_workspace("get_metadata", image_id=42)
    gimp_workspace("set_resolution", image_id=42, xresolution=300, yresolution=300)
    gimp_workspace("set_unit", image_id=42, unit=1)

    Errors:
    - GIMP execution layer unavailable: No GIMP found
    - image_id required for operations that need it
    - PDB procedure not found for the given GIMP version
    """
    start_time = time.time()

    try:
        requires_image = operation in (
            "undo_count", "undo", "redo", "undo_group_start",
            "undo_group_end", "get_metadata", "set_resolution", "set_unit",
        )
        if requires_image and image_id is None:
            return WorkspaceResult(
                success=False,
                operation=operation,
                message=f"{operation} requires image_id",
                error="Missing required parameter: image_id",
            ).model_dump()

        exec_layer = interaction_manager or cli_wrapper
        if exec_layer is None:
            return WorkspaceResult(
                success=False,
                operation=operation,
                message="No GIMP execution layer available",
                error="GIMP not available",
            ).model_dump()

        code = _make_workspace_fu(operation, image_id, xresolution=xresolution, yresolution=yresolution, unit=unit)
        if code is None:
            return WorkspaceResult(
                success=False,
                operation=operation,
                message=f"Unknown operation: {operation}",
                error="Invalid operation",
            ).model_dump()

        output = await exec_layer.execute_python_fu(code)
        mode = getattr(exec_layer, "last_mode", "headless") if hasattr(exec_layer, "last_mode") else "headless"

        marker = "WSP_RESULT:"
        idx = output.find(marker)
        if idx >= 0:
            payload = json.loads(output[idx + len(marker):])
            execution_time = (time.time() - start_time) * 1000
            return WorkspaceResult(
                success=payload.get("success", False),
                operation=operation,
                message=f"Workspace {operation} completed" if payload.get("success") else f"Workspace {operation} failed",
                data=payload.get("result", payload.get("data", {})),
                execution_time_ms=round(execution_time, 2),
                error=payload.get("error"),
            ).model_dump()

        execution_time = (time.time() - start_time) * 1000
        return WorkspaceResult(
            success=True,
            operation=operation,
            message=f"Workspace {operation} completed",
            data={"mode": mode, "output": output},
            execution_time_ms=round(execution_time, 2),
        ).model_dump()

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return WorkspaceResult(
            success=False,
            operation=operation,
            message=f"Workspace operation failed: {e!s}",
            error=str(e),
            execution_time_ms=round(execution_time, 2),
        ).model_dump()
