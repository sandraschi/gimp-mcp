"""Smoke test for gimp-mcp Agent Lab tool surface and dual-mode reporting."""

from __future__ import annotations

import asyncio


async def main() -> int:
    from gimp_mcp.http_app import _mcp
    from gimp_mcp.utils.execution_mode import describe_execution_mode
    from gimp_mcp.utils.telemetry import metrics_enabled, render_metrics

    print("=== gimp-mcp smoke test ===")
    tools = await _mcp.list_tools()
    names = {t.name for t in tools}
    required = {
        "gimp_bridge_tool",
        "gimp_render_tool",
        "gimp_validation_tool",
        "gimp_import_tool",
        "gimp_vision_refine_tool",
        "gimp_sim_art_tool",
    }
    missing = required - names
    print(f"Tools registered: {len(names)}")
    if missing:
        print(f"FAIL missing tools: {sorted(missing)}")
        return 1
    print(f"OK phase tools present: {sorted(required)}")

    mode = await describe_execution_mode()
    print(
        f"Execution mode: {mode.get('label')} ({mode.get('mode')}) "
        f"bridge={mode.get('bridge_connected')}"
    )

    for tool_name, args in [
        ("gimp_bridge_tool", {"operation": "execution_mode"}),
        ("gimp_import_tool", {"operation": "list_staging"}),
        ("gimp_validation_tool", {"operation": "validate_image", "input_path": "D:/Temp/gimp_smoke_missing.png"}),
        ("gimp_sim_art_tool", {"operation": "list_templates"}),
    ]:
        result = await _mcp.call_tool(tool_name, args)
        text = result.content[0].text if result.content else str(result)
        print(f"OK {tool_name}: {text[:140].replace(chr(10), ' ')}")

    metrics_body = render_metrics()
    if metrics_enabled() and b"gimp_mcp" not in metrics_body and b"disabled" in metrics_body:
        print("WARN metrics enabled but prometheus_client may be missing")
    else:
        print(f"OK metrics endpoint bytes={len(metrics_body)}")

    print("=== smoke test passed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
