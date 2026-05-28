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
| `gimp_sim_art_tool` | `list_templates`, `gazebo_model_icons`, `build_atlas`, `vrchat_icon_batch`, `stage_for_robotics`, `push_avatar_handoff` |

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

## Related

- [FLEET_PIPELINE.md](FLEET_PIPELINE.md) — blender → gimp → unity textures
- [ROADMAP.md](ROADMAP.md) — Phase 5 complete at v4.5.0
