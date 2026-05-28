#!/usr/bin/env python3
"""Build MCPB bundle for gimp-mcp (FastMCP 3.2 SOTA)."""

from __future__ import annotations

import json
import os
import zipfile
from pathlib import Path


def create_mcpb_package() -> bool:
    project_root = Path(__file__).parent
    mcpb_dir = project_root / "mcpb"
    dist_dir = project_root / "dist"
    src_dir = project_root / "src"
    skills_dir = project_root / "skills"

    dist_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = mcpb_dir / "manifest.json"
    if not manifest_path.exists():
        print("[ERROR] MCPB manifest not found in mcpb/manifest.json")
        return False

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    package_name = manifest.get("name", "gimp-mcp")
    version = manifest.get("version", "4.0.0")
    output_file = dist_dir / f"{package_name}-{version}.mcpb"

    print(f"[BUILD] Packaging {package_name}-{version}")

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("manifest.json", json.dumps(manifest, indent=2))

        if src_dir.exists():
            for root, _, files in os.walk(src_dir):
                for file in files:
                    if file.endswith((".py", ".md", ".json", ".typed")):
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(project_root)
                        zipf.write(str(file_path), str(arcname))
        else:
            print("[ERROR] src/ directory not found")
            return False

        if skills_dir.exists():
            for root, _, files in os.walk(skills_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(project_root)
                    zipf.write(str(file_path), str(arcname))

        for doc in (
            "README.md",
            "CHANGELOG.md",
            "LICENSE",
            "llms.txt",
            "docs/readme/INSTALL.md",
            "docs/SIM_ART_PIPELINE.md",
            "docs/FLEET_PIPELINE.md",
        ):
            doc_path = project_root / doc
            if doc_path.exists():
                zipf.write(str(doc_path), doc)

    print("\n[SUCCESS] MCPB package created")
    print(f"Package: {output_file}")
    print(f"Size: {os.path.getsize(output_file) / 1024:.2f} KB")
    return True


def main() -> None:
    print("\n=== Building gimp-mcp MCPB ===\n")
    if not create_mcpb_package():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
