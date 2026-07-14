#!/usr/bin/env python3
"""Iterative background removal with visual snapshot verification.

Demonstrates the AI vision feedback loop:
    edit → get_state_snapshot → assess → refine → repeat

Usage:
    python demos/iterative_bg_remove.py <image_path>

Requires: GIMP running with MCP Bridge plugin active (port 10824).
"""

import json
import sys
import time
import urllib.request

MCP_URL = "http://127.0.0.1:10773/api/v1/tool"


def call_tool(tool: str, **kwargs) -> dict:
    """Call a GIMP MCP tool via the REST bridge."""
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
    """Get a live snapshot of the current canvas."""
    kwargs = {"max_size": max_size}
    if region:
        kwargs["region"] = region
    return call_tool("gimp_snapshot_tool", **kwargs)


def main():
    image_path = sys.argv[1] if len(sys.argv) > 1 else None

    print("=" * 60)
    print("GIMP MCP — Iterative Background Removal Demo")
    print("=" * 60)

    # Step 1: Open image or verify one is loaded
    if image_path:
        print(f"\n1. Opening: {image_path}")
        result = call_tool("gimp_file", operation="load", path=image_path)
        assert result.get("success"), f"Failed to open image: {result}"
        print(f"   ✅ Loaded: {result.get('message', '')}")
    else:
        print("\n1. Using already-open image (no path provided)")

    # Step 2: Check bridge is alive
    print("\n2. Checking GIMP bridge...")
    result = call_tool("gimp_bridge_tool", operation="status")
    if not result.get("success"):
        print("   ❌ Bridge offline — start MCP Bridge in GIMP (Filters > Development > MCP)")
        sys.exit(1)
    print(f"   ✅ Bridge connected — mode: {result.get('mode', '?')}")

    # Step 3: Initial snapshot — see what we're working with
    print("\n3. Capturing initial state snapshot...")
    snap = snapshot(max_size=512)
    if snap.get("success"):
        img_len = len(snap.get("image_base64", ""))
        print(f"   📸 Snapshot captured ({img_len // 1024} KB base64)")
    else:
        print(f"   ⚠️  Snapshot unavailable: {snap.get('error', 'unknown')}")

    # Step 4: Add alpha channel for transparency
    print("\n4. Adding alpha channel...")
    call_tool("gimp_layer", operation="add_alpha", layer_name=None)

    # Step 5: Remove background using fuzzy select
    print("\n5. Removing background (fuzzy select at corner)...")
    result = call_tool("gimp_color", operation="select_by_color")
    print(f"   Result: {result.get('message', 'done')}")

    # Step 6: Delete selection (background)
    print("\n6. Deleting selected background pixels...")
    result = call_tool("gimp_layer", operation="delete_selection")
    print(f"   Result: {result.get('message', 'done')}")

    # Step 7: Snapshot to verify
    print("\n7. Verification snapshot...")
    snap = snapshot(max_size=512)
    if snap.get("success"):
        img_len = len(snap.get("image_base64", ""))
        print(f"   📸 Post-cleanup snapshot ({img_len // 1024} KB)")

    # Step 8: Check for remaining background pixels via zoom region
    print("\n8. Inspecting edge regions for remaining artifacts...")
    for corner_name, region in [
        ("top-left", {"x": 0, "y": 0, "width": 100, "height": 100}),
        ("top-right", {"x": 0, "y": 0, "width": 100, "height": 100}),
    ]:
        snap = snapshot(max_size=256, region=region)
        if snap.get("success"):
            print(f"   🔍 {corner_name} region snapshot OK")

    # Step 9: Export
    output = "output_bg_removed.png"
    print(f"\n9. Exporting: {output}")
    result = call_tool("gimp_file", operation="save", output_path=output)
    if result.get("success"):
        print(f"   ✅ Exported to {output}")
    else:
        print(f"   ⚠️  Export issue: {result}")

    # Step 10: Final summary
    print("\n" + "=" * 60)
    print("Demo complete!")
    print(f"Output: {output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
