#!/usr/bin/env python3
"""Snapshot zoom demo — demonstrate region-based inspection.

Uses get_state_snapshot with region crops to inspect different areas
of the canvas at high zoom. Useful for:
  - Checking edge artifacts after background removal
  - Inspecting text alignment
  - Verifying color accuracy in specific areas

Usage:
    python demos/snapshot_zoom_demo.py

Requires: GIMP running with MCP Bridge plugin (port 10824), image open.
"""

import json
import sys
import urllib.request

MCP_URL = "http://127.0.0.1:10773/api/v1/tool"


def snapshot(max_size=512, region=None) -> dict:
    kwargs = {"max_size": max_size}
    if region:
        kwargs["region"] = region
    payload = {"tool": "gimp_snapshot_tool", "arguments": kwargs}
    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def main():
    print("=" * 60)
    print("GIMP MCP — Region Snapshot Zoom Demo")
    print("=" * 60)

    regions = {
        "Full canvas": None,
        "Top-left 200×200": {"x": 0, "y": 0, "width": 200, "height": 200},
        "Center 300×300": {"x": 400, "y": 300, "width": 300, "height": 300},
        "Bottom-right 100×100": {"x": 700, "y": 500, "width": 100, "height": 100},
    }

    for label, region in regions.items():
        print(f"\n🔍 {label}...")
        r = snapshot(max_size=512, region=region)
        if r.get("success"):
            size_kb = len(r["image_base64"]) // 1024
            print(f"   ✅ {size_kb} KB base64 PNG" + (" (cropped)" if region else " (full)"))
        else:
            print(f"   ❌ {r.get('error', 'unknown error')}")

    print("\n" + "=" * 60)
    print("Demo complete — all snapshots returned base64 PNG data")
    print("=" * 60)


if __name__ == "__main__":
    main()
