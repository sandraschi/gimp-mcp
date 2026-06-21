"""Generic GIMP PDB proxy — calls any PDB procedure by name."""

from __future__ import annotations

import json
from typing import Any


def _make_python_fu(procedure: str, args: list) -> str:
    """Generate Python-Fu code to call a PDB procedure with serialization.

    GIMP 3 PDB uses hyphenated names (gimp-version), gimpfu uses underscores (gimp_version).
    We try both: hyphen for GI lookup, underscore for gimpfu direct call."""
    import json as _json

    args_repr = _json.dumps(args)
    proc_hyphen = procedure.replace("_", "-")
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
            _proc = _pdb.lookup_procedure("{proc_hyphen}")
            if _proc is None:
                _proc = _pdb.lookup_procedure("{procedure}")
            _config = _proc.create_config()
            _arg_specs = _proc.get_arguments()
            _args = {args_repr}
            for _i, _val in enumerate(_args):
                if _i < len(_arg_specs):
                    _config.set_property(_arg_specs[_i].get_name(), _val)
            _result = _proc.run(_config)
            _serialized = str(_result)
        except (ImportError, AttributeError, TypeError):
            from gimpfu import pdb
            _args = {args_repr}
            _result = pdb.{procedure}(*_args)
            if hasattr(_result, 'ID'):
                _serialized = {{"type": "gimp_object", "id": _result.ID, "repr": str(_result)}}
            elif isinstance(_result, (int, float, str, bool)):
                _serialized = _result
            elif _result is None:
                _serialized = None
            elif hasattr(_result, '__iter__'):
                _serialized = [str(x) for x in _result]
            else:
                _serialized = str(_result)

    print('PDB_RESULT:' + _json.dumps({{"success": True, "result": _serialized}}))
except Exception as _e:
    print('PDB_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
"""


async def gimp_pdb(
    procedure: str,
    args: list[Any] | None = None,
    *,
    interaction_manager=None,
    cli_wrapper=None,
    config=None,
) -> dict[str, Any]:
    """Call any GIMP PDB procedure by name. Universal escape hatch to GIMP's
    full Procedural Database (~1000+ procedures).

    ## Return Format
    {"success": bool, "result": Any, "error": str | None, "mode": "live" | "headless" | "offline"}

    ## Examples
    gimp_pdb("gimp_selection_all", [image_id])
    gimp_pdb("gimp_text_layer_set_font", [layer_id, "Arial"])
    gimp_pdb("plug_in_gauss", [image_id, layer_id, 5.0, 5.0, 0])
    """
    args = args or []
    code = _make_python_fu(procedure, args)

    exec_layer = interaction_manager or cli_wrapper
    if exec_layer is None:
        return {"success": False, "error": "No GIMP execution layer available", "mode": "offline"}

    try:
        if hasattr(exec_layer, "execute_python_fu"):
            output = await exec_layer.execute_python_fu(code)
        else:
            return {"success": False, "error": "Execution layer has no execute_python_fu", "mode": "offline"}
    except Exception as e:
        return {"success": False, "error": str(e), "mode": "error"}

    mode = getattr(exec_layer, "last_mode", "headless") if hasattr(exec_layer, "last_mode") else "headless"

    try:
        marker = "PDB_RESULT:"
        idx = output.find(marker)
        if idx >= 0:
            payload = json.loads(output[idx + len(marker) :])
            payload["mode"] = mode
            return payload
        return {"success": True, "result": output, "mode": mode}
    except Exception as e:
        return {"success": False, "error": f"Failed to parse PDB response: {e}", "raw": output, "mode": mode}
