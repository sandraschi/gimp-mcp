"""
Build script for creating the GIMP MCP DXT package.

This script automates the process of creating a DXT package from the GIMP MCP source code.
"""

import json
import shutil
import sys
from pathlib import Path
from typing import List, Optional

# Project root directory
ROOT_DIR = Path(__file__).parent
DXT_DIR = ROOT_DIR / "dxt"
DIST_DIR = ROOT_DIR / "dist"

# Required files and directories to include in the DXT package
INCLUDE_PATTERNS = [
    "src/gimp_mcp/**/*.py",
    "pyproject.toml",
    "requirements.txt"
]

# Files to exclude from the package
EXCLUDE_PATTERNS = [
    "**/__pycache__/*",
    "**/*.pyc",
    "**/.DS_Store",
    "**/.*",
]

def clean_build() -> None:
    """Clean up build directories."""
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(exist_ok=True)
    
    # Ensure DXT directory exists
    DXT_DIR.mkdir(exist_ok=True, parents=True)

def copy_source_files() -> None:
    """Copy source files to the DXT package directory."""
    from glob import glob
    import os
    
    # Copy Python package
    src_dir = ROOT_DIR / "src"
    dst_dir = DXT_DIR / "src"
    
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    
    shutil.copytree(src_dir, dst_dir)
    
    # Copy other required files
    for pattern in ["pyproject.toml", "requirements.txt", "README.md"]:
        for file in ROOT_DIR.glob(pattern):
            if file.is_file():
                shutil.copy2(file, DXT_DIR)

def create_package() -> None:
    """Create the DXT package."""
    import subprocess
    
    # Ensure DXT CLI is installed
    try:
        subprocess.run(["dxt", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: DXT CLI is not installed. Please install it with: npm install -g @anthropic-ai/dxt")
        sys.exit(1)
    
    # Validate the manifest
    print("Validating manifest...")
    result = subprocess.run(
        ["dxt", "validate", "--manifest", str(ROOT_DIR / "manifest.json")],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Error validating manifest:")
        print(result.stderr)
        sys.exit(1)
    
    print("Manifest is valid.")
    
    # Copy manifest to DXT directory
    shutil.copy2(ROOT_DIR / "manifest.json", DXT_DIR / "manifest.json")
    
    # Create the package
    print("Creating DXT package...")
    result = subprocess.run(
        ["dxt", "pack", "--output", str(DIST_DIR), str(DXT_DIR)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Error creating DXT package:")
        print(result.stderr)
        sys.exit(1)
    
    print(f"DXT package created successfully in {DIST_DIR}")

def main() -> int:
    """Main function to build the DXT package."""
    try:
        print("Starting DXT package build...")
        clean_build()
        copy_source_files()
        create_package()
        print("Build completed successfully!")
        return 0
    except Exception as e:
        print(f"Error building DXT package: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
