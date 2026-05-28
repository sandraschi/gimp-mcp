# Sim-Art Pipeline

Batch Gazebo model icons, sim texture atlases, and VRChat social icon handoff.

```text
source renders / photos
        |
        v
gimp_sim_art (gazebo_model_icons | vrchat_icon_batch)
        |
        v
gimp_validation audit_texture (optional)
        |
        v
build_atlas + manifest JSON (Gazebo path)
        |
        v
robotics_staging / avatar_staging
```

## Prerequisites

| Service | Port | Role |
|---------|------|------|
| gimp-mcp HTTP | 10773 | Sim-art tools |
| robotics-mcp | 10892 | Gazebo composition (optional) |
| avatar-mcp | 10793 | VRChat handoff staging (optional) |

## CLI

```powershell
cd D:\Dev\repos\gimp-mcp
.\scripts\run-sim-art-pipeline.ps1 -InputDir "D:\Temp\model_renders" -Pipeline gazebo

# VRChat profile icons
.\scripts\run-sim-art-pipeline.ps1 -InputDir "D:\Temp\avatars" -Pipeline vrchat -TemplateId vrchat_profile_256 -SkipAvatar:$false
```

```powershell
uv run python scripts/sim_art_pipeline.py --input-dir D:\Temp\model_renders --pipeline gazebo --json
```

## MCP tool

| Tool | Operations |
|------|------------|
| `gimp_sim_art_tool` | `list_templates`, `gazebo_model_icons`, `build_atlas`, `vrchat_icon_batch`, `stage_for_robotics`, `push_avatar_handoff`, `import_gazebo_model`, `import_avatar_model`, `batch_import_gazebo` |

## Templates

| ID | Size | Target |
|----|------|--------|
| `gazebo_icon_256` | 256x256 | Gazebo model thumbnail |
| `gazebo_icon_512` | 512x512 | Gazebo model thumbnail |
| `gazebo_decal_512` | 512x512 | Sim decal |
| `vrchat_profile_256` | 256x256 | VRChat profile |
| `vrchat_world_512` | 512x512 | VRChat world thumbnail |

Atlas layouts: `2x2`, `3x3`, `4x4`, `4x2`, `8x8` — outputs PNG + `.manifest.json` with UV rects.

## Staging layout

Default: `D:/Temp/fleet_pipeline/sim_art/`

- `gazebo_icons/` — normalized icons
- `atlases/` — texture atlases + manifests
- `robotics_staging/` — copy for robotics-mcp / Gazebo models
- `vrchat_icons/` — social icons
- `avatar_staging/` — avatar-mcp handoff folder

## Automated import

| Operation | What it does |
|-----------|----------------|
| `import_gazebo_model` | Copy `icon_path` into `{model_dir}/thumbnails/1.png` (+ `model_thumb.png`) |
| `batch_import_gazebo` | Match icon filenames to model folders under `models_root` |
| `import_avatar_model` | Write `{model_id}.thumb.png` next to the VRM (uses avatar-mcp `/api/v1/avatars` when online) |
| `stage_for_robotics` + `auto_import=true` | Stage + batch import when `models_root` is set |
| `push_avatar_handoff` + `auto_import=true` | Stage + import when `model_id` or `vrm_path` is set |

```powershell
# Full pipeline with Gazebo auto-import
.\scripts\run-sim-art-pipeline.ps1 `
  -InputDir "D:\Temp\model_renders" `
  -ModelsRoot "C:\Users\you\.gz\fuel\fuel.gazebosim.org\OpenRobotics\models" `
  -AutoImport
```

## Related

- [FLEET_PIPELINE.md](FLEET_PIPELINE.md) — blender → gimp → unity textures
- [ROADMAP.md](ROADMAP.md) — Phase 5 complete at v4.5.0
