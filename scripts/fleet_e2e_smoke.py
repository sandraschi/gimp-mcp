"""Fleet E2E smoke: texture + sim-art paths (best-effort when services offline)."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from gimp_mcp.utils.fleet_http import (
    DEFAULT_AVATAR_URL,
    DEFAULT_BLENDER_URL,
    DEFAULT_ROBOTICS_URL,
    DEFAULT_UNITY_URL,
    check_http_health,
    call_http_tool,
)
from gimp_mcp.utils.fleet_sim_handoff import import_icon_to_gazebo_model
from gimp_mcp.utils.sim_art_templates import DEFAULT_SIM_STAGING


async def _probe(name: str, url: str) -> dict[str, object]:
    ok = await check_http_health(url, health_path="/api/v1/health")
    if not ok:
        ok = await check_http_health(url, health_path="/api/health")
    if not ok:
        ok = await check_http_health(url, health_path="/health")
    return {"service": name, "url": url, "online": ok}


async def run_e2e_smoke(
    *,
    texture_path: str | None,
    unity_project: str | None,
    sim_input_dir: str | None,
    gazebo_model_dir: str | None,
    skip_unity: bool,
    skip_sim: bool,
) -> dict[str, object]:
    report: dict[str, object] = {"success": True, "steps": []}
    steps: list[dict[str, object]] = []

    probes = await asyncio.gather(
        _probe("blender-mcp", DEFAULT_BLENDER_URL),
        _probe("gimp-mcp", "http://127.0.0.1:10773"),
        _probe("unity3d-mcp", DEFAULT_UNITY_URL),
        _probe("robotics-mcp", DEFAULT_ROBOTICS_URL),
        _probe("avatar-mcp", DEFAULT_AVATAR_URL),
    )
    steps.append({"name": "fleet_probe", "success": True, "detail": probes})

    gimp_online = next(p for p in probes if p["service"] == "gimp-mcp")["online"]
    if gimp_online:
        templates = await call_http_tool(
            "http://127.0.0.1:10773",
            "gimp_sim_art_tool",
            {"operation": "list_templates"},
        )
        steps.append({"name": "gimp_sim_art_templates", "success": bool(templates.get("success")), "detail": templates})
    else:
        steps.append({"name": "gimp_sim_art_templates", "success": False, "detail": {"skipped": "gimp offline"}})

    if texture_path and Path(texture_path).is_file() and gimp_online:
        audit = await call_http_tool(
            "http://127.0.0.1:10773",
            "gimp_validation_tool",
            {"operation": "audit_texture", "input_path": texture_path, "target_platform": "unity"},
        )
        steps.append({"name": "gimp_texture_audit", "success": bool(audit.get("success")), "detail": audit})

    if not skip_unity and texture_path and unity_project and gimp_online:
        push = await call_http_tool(
            "http://127.0.0.1:10773",
            "gimp_import_tool",
            {
                "operation": "push_unity",
                "source_path": texture_path,
                "project_path": unity_project,
            },
        )
        steps.append({"name": "unity_texture_push", "success": bool(push.get("success")), "detail": push})

    if not skip_sim and sim_input_dir and Path(sim_input_dir).is_dir() and gimp_online:
        batch = await call_http_tool(
            "http://127.0.0.1:10773",
            "gimp_sim_art_tool",
            {
                "operation": "gazebo_model_icons",
                "input_dir": sim_input_dir,
                "output_dir": str(Path(DEFAULT_SIM_STAGING) / "gazebo_icons"),
                "validate": False,
            },
        )
        steps.append({"name": "sim_art_batch", "success": bool(batch.get("success")), "detail": batch})

        if gazebo_model_dir and batch.get("success"):
            icons = batch.get("files") or batch.get("data", {}).get("files") or []
            if icons:
                imported = await import_icon_to_gazebo_model(
                    icon_path=str(icons[0]),
                    model_dir=gazebo_model_dir,
                )
                steps.append(
                    {"name": "gazebo_model_import", "success": bool(imported.get("success")), "detail": imported},
                )

    robotics_online = next(p for p in probes if p["service"] == "robotics-mcp")["online"]
    if robotics_online:
        import httpx

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{DEFAULT_ROBOTICS_URL.rstrip('/')}/api/v1/tools/robotics_sim_art",
                    json={"operation": "gimp_status"},
                )
                body = response.json() if response.status_code == 200 else {"error": response.text}
                steps.append(
                    {
                        "name": "robotics_gimp_bridge",
                        "success": response.status_code == 200,
                        "detail": body,
                    },
                )
        except Exception as exc:
            steps.append({"name": "robotics_gimp_bridge", "success": False, "detail": {"error": str(exc)}})

    report["steps"] = steps
    report["success"] = all(bool(s.get("success")) for s in steps if s.get("name") != "fleet_probe")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Fleet E2E smoke (best-effort)")
    parser.add_argument("--texture-path", default="")
    parser.add_argument("--unity-project", default="")
    parser.add_argument("--sim-input-dir", default="")
    parser.add_argument("--gazebo-model-dir", default="")
    parser.add_argument("--skip-unity", action="store_true")
    parser.add_argument("--skip-sim", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Fail if any step fails")
    args = parser.parse_args()

    report = asyncio.run(
        run_e2e_smoke(
            texture_path=args.texture_path or None,
            unity_project=args.unity_project or None,
            sim_input_dir=args.sim_input_dir or None,
            gazebo_model_dir=args.gazebo_model_dir or None,
            skip_unity=args.skip_unity,
            skip_sim=args.skip_sim,
        ),
    )
    print(json.dumps(report, indent=2))
    if not args.json:
        print(f"\nE2E smoke {'SUCCESS' if report['success'] else 'FAILED (see steps)'}")
    if args.strict and not report.get("success"):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
