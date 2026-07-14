#!/usr/bin/env python3
"""Agentic edit demo: open → snapshot → edit → snapshot → refine → export.

Demonstrates the full AI vision loop with get_state_snapshot used between
each edit step for visual verification.

Usage:
    python demos/agentic_edit_demo.py <image_path>

Requires: GIMP running with MCP Bridge plugin (port 10824).
"""

import json
import sys
import urllib.request

MCP_URL = "http://127.0.0.1:10773/api/v1/tool"


def call_tool(tool: str, **kwargs) -> dict:
    payload = {"tool": tool, "arguments": kwargs}
    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def snapshot(max_size=512, region=None) -> dict:
    kwargs = {"max_size": max_size}
    if region:
        kwargs["region"] = region
    return call_tool("gimp_snapshot_tool", **kwargs)


def step(n, label, result):
    status = "✅" if result.get("success") else "⚠️"
    print(f"  {status} [{n}] {label}: {result.get('message', result.get('error', 'done'))}")


def main():
    image_path = sys.argv[1] if len(sys.argv) > 1 else None

    print("=" * 60)
    print("GIMP MCP — Agentic Edit Pipeline Demo")
    print("=" * 60)

    # 1. Open image
    if image_path:
        r = call_tool("gimp_file", operation="load", path=image_path)
        step(1, f"Open {image_path}", r)
    else:
        step(1, "Using open image", {"success": True})

    # 2. Snapshot before
    r = snapshot(max_size=512)
    step(2, "Snapshot (before)", r)
    before_size = len(r.get("image_base64", "")) // 1024 if r.get("success") else 0
    print(f"       📸 {before_size} KB base64 PNG")

    # 3. Auto-levels
    r = call_tool("gimp_color", operation="auto_levels")
    step(3, "Auto levels", r)

    # 4. Snapshot check
    r = snapshot(max_size=512)
    step(4, "Snapshot (after levels)", r)

    # 5. Brightness/contrast boost
    r = call_tool("gimp_color", operation="brightness_contrast",
                  brightness=0.15, contrast=0.25)
    step(5, "Brightness +15%, contrast +25%", r)

    # 6. Snapshot check
    r = snapshot(max_size=512)
    step(6, "Snapshot (after brightness)", r)

    # 7. Sharpen
    r = call_tool("gimp_filter", operation="sharpen", amount=0.5)
    step(7, "Sharpen 50%", r)

    # 8. Zoom-in snapshot at center region
    r = snapshot(max_size=256, region={"x": 200, "y": 200, "width": 300, "height": 300})
    step(8, "Zoom snapshot (center region)", r)

    # 9. Export
    output = "output_edited.png"
    r = call_tool("gimp_file", operation="save", output_path=output)
    step(9, f"Export {output}", r)

    # 10. Snapshot after
    r = snapshot(max_size=512)
    step(10, "Snapshot (final)", r)
    after_size = len(r.get("image_base64", "")) // 1024 if r.get("success") else 0
    print(f"       📸 {after_size} KB base64 PNG")

    print("\n" + "=" * 60)
    print(f"Pipeline complete: {image_path or 'open image'} → {output}")
    print(f"Snapshot sizes: {before_size} KB before → {after_size} KB after")
    print("=" * 60)


if __name__ == "__main__":
    main()
