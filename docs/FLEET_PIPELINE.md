# Fleet Texture Pipeline

End-to-end handoff for **blender-mcp -> gimp-mcp -> unity3d-mcp** texture workflows.

```text
blender_render (viewport / multi-angle)
        |
        v
gimp staging + normalize (power-of-two PNG)
        |
        v
gimp_validation audit_texture
        |
        v
gimp_vision_refine review_bundle (optional)
        |
        v
Assets/GimpImports + unity3d-mcp import_texture
```

## Prerequisites

| Service | Port | Start |
|---------|------|-------|
| blender-mcp HTTP | 10849 | `blender-mcp` root `start.ps1` |
| gimp-mcp webapp | 10773 | `gimp-mcp/webapp/start.ps1` |
| unity3d-mcp HTTP | 10831 | `unity3d-mcp` `uv run python -m unity3d_mcp --http --port 10831` |

## CLI

```powershell
cd D:\Dev\repos\gimp-mcp
.\scripts\run-fleet-pipeline.ps1 -ProjectPath "D:\Unity\MyProject" -TexturePath "D:\Temp\albedo.png"

# Or with blender render step:
.\scripts\run-fleet-pipeline.ps1 -ProjectPath "D:\Unity\MyProject" -BlenderOperation render_multi_angle -BlenderAngles 4
```

```powershell
uv run python scripts/fleet_pipeline.py --project-path D:\Unity\MyProject --texture-path D:\Temp\albedo.png --skip-blender
```

## MCP tools

| Tool | Operations |
|------|------------|
| `gimp_import_tool` | `import_file`, `from_blender_render`, `list_staging`, `push_unity` |
| `gimp_vision_refine_tool` | `review_bundle`, `texture_review`, `validate_folder` |
| `gimp_validation_tool` | `audit_texture` (Unity-ready checks) |

## Staging layout

Default: `D:/Temp/fleet_pipeline/gimp_staging/`

- `incoming/` — copied source textures
- `blender_renders/` — blender-mcp outputs
- `processed/` — power-of-two PNG ready for Unity

## Related

- [unity3d-mcp FLEET_PIPELINE.md](https://github.com/sandraschi/unity3d-mcp/blob/master/docs/FLEET_PIPELINE.md) — mesh pipeline (Gazebo + blender GLB)
- [ROADMAP.md](ROADMAP.md) — Phase 5 complete at v4.5.0
- [SIM_ART_PIPELINE.md](SIM_ART_PIPELINE.md) — Gazebo icons, atlases, VRChat handoff
