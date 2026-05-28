"""CLI for sim-art pipeline (Gazebo icons / VRChat / atlases)."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from gimp_mcp.utils.fleet_http import DEFAULT_AVATAR_URL, DEFAULT_ROBOTICS_URL
from gimp_mcp.utils.fleet_sim_pipeline import run_sim_art_pipeline
from gimp_mcp.utils.sim_art_templates import DEFAULT_SIM_STAGING

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sim-art pipeline: Gazebo icons, atlases, VRChat handoff")
    parser.add_argument("--input-dir", required=True, help="Folder of source images")
    parser.add_argument("--staging-dir", default=DEFAULT_SIM_STAGING)
    parser.add_argument("--pipeline", choices=["gazebo", "vrchat"], default="gazebo")
    parser.add_argument("--template-id", default="gazebo_icon_256")
    parser.add_argument("--layout", default="4x4")
    parser.add_argument("--cell-size", type=int, default=256)
    parser.add_argument("--skip-atlas", action="store_true")
    parser.add_argument("--skip-robotics", action="store_true")
    parser.add_argument("--skip-avatar", action="store_true")
    parser.add_argument("--no-validate", action="store_true")
    parser.add_argument("--robotics-url", default=DEFAULT_ROBOTICS_URL)
    parser.add_argument("--avatar-url", default=DEFAULT_AVATAR_URL)
    parser.add_argument("--models-root", default="", help="Gazebo models root for auto-import")
    parser.add_argument("--model-id", default="", help="Avatar model id for auto-import")
    parser.add_argument("--vrm-path", default="", help="Avatar VRM path for auto-import")
    parser.add_argument("--auto-import", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print JSON report only")
    return parser


async def _main_async(args: argparse.Namespace) -> int:
    report = await run_sim_art_pipeline(
        input_dir=args.input_dir,
        staging_dir=Path(args.staging_dir),
        pipeline=args.pipeline,
        template_id=args.template_id,
        layout=args.layout,
        cell_size=args.cell_size,
        skip_atlas=args.skip_atlas,
        skip_robotics=args.skip_robotics,
        skip_avatar=args.skip_avatar,
        validate=not args.no_validate,
        robotics_url=args.robotics_url,
        avatar_url=args.avatar_url,
        models_root=args.models_root or None,
        model_id=args.model_id or None,
        vrm_path=args.vrm_path or None,
        auto_import=args.auto_import,
    )
    payload = report.to_dict()
    print(json.dumps(payload, indent=2))
    if not args.json:
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
