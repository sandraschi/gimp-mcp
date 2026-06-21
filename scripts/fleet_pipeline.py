"""CLI for fleet texture pipeline (blender -> gimp -> unity)."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from gimp_mcp.utils.fleet_http import DEFAULT_BLENDER_URL, DEFAULT_UNITY_URL
from gimp_mcp.utils.fleet_import import DEFAULT_STAGING_DIR
from gimp_mcp.utils.fleet_pipeline import run_fleet_pipeline

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fleet texture pipeline: blender render -> gimp validate -> unity import",
    )
    parser.add_argument("--project-path", required=True, help="Unity project path")
    parser.add_argument("--texture-path", default="", help="Skip blender; use existing image")
    parser.add_argument("--blender-url", default=DEFAULT_BLENDER_URL)
    parser.add_argument("--unity-url", default=DEFAULT_UNITY_URL)
    parser.add_argument("--staging-dir", default=str(DEFAULT_STAGING_DIR))
    parser.add_argument("--skip-blender", action="store_true")
    parser.add_argument(
        "--blender-operation",
        default="screenshot_viewport",
        help="blender_render operation (screenshot_viewport, render_multi_angle)",
    )
    parser.add_argument("--blender-angles", type=int, default=4)
    parser.add_argument("--skip-validate", action="store_true")
    parser.add_argument("--skip-review", action="store_true")
    parser.add_argument("--skip-unity", action="store_true")
    parser.add_argument("--texture-type", default="diffuse")
    parser.add_argument("--target-platform", default="unity")
    parser.add_argument("--normalize-size", type=int, default=1024)
    parser.add_argument("--goal", default="", help="Agent review goal string")
    parser.add_argument("--json", action="store_true", help="Print JSON report only")
    return parser


async def _main_async(args: argparse.Namespace) -> int:
    report = await run_fleet_pipeline(
        project_path=args.project_path,
        texture_path=args.texture_path or None,
        blender_url=args.blender_url,
        unity_url=args.unity_url,
        staging_dir=Path(args.staging_dir),
        skip_blender=args.skip_blender or bool(args.texture_path),
        blender_operation=args.blender_operation,
        blender_angles=args.blender_angles,
        skip_validate=args.skip_validate,
        skip_review=args.skip_review,
        skip_unity=args.skip_unity,
        texture_type=args.texture_type,
        target_platform=args.target_platform,
        normalize_size=args.normalize_size,
        goal=args.goal,
    )

    payload = report.to_dict()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload, indent=2))
        print(f"\nPipeline {'SUCCESS' if report.success else 'FAILED'}")

    return 0 if report.success else 1


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = _build_parser()
    args = parser.parse_args()
    try:
        code = asyncio.run(_main_async(args))
    except KeyboardInterrupt:
        code = 130
    sys.exit(code)


if __name__ == "__main__":
    main()
