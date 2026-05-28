# Improvement Roadmap

Phased plan derived from [COMPETITIVE_ANALYSIS.md](COMPETITIVE_ANALYSIS.md).
Mirrors the blender-mcp / unity3d-mcp Agent Lab phases, adapted for GIMP live + batch pipelines.

## Phase 1 — Bridge wiring and agent vision (4.1.0)

**Status: complete (v4.1.1)**

| Item | Tool / module |
|------|----------------|
| Bridge-first runtime | `utils/gimp_runtime.py` |
| Hands-In vs Hands-Off guidance | `utils/execution_mode.py` |
| Live bridge portmanteau | `gimp_bridge` → status, execution_mode, ping, list_open_images |
| Canvas capture for agents | `gimp_render` → capture_active, get_image_summary |
| Port reconciliation | Bridge TCP **10824** (fleet standard) |
| Phase 1 tests | `tests/test_phase1_tools.py` |

### Live GUI workflow

```powershell
# HTTP MCP (webapp / IDE)
cd D:\Dev\repos\gimp-mcp\webapp
.\start.ps1

# GIMP: Filters > Development > MCP > Start MCP Bridge (:10824)

# Agent:
# gimp_bridge operation=status
# gimp_bridge operation=execution_mode
# gimp_render operation=capture_active output_path=D:/Temp/gimp_review.png
```

## Phase 2 — Webapp Agent Lab and validation (4.2.0)

**Status: complete (v4.2.0)**

| Item | Tool / module |
|------|----------------|
| Webapp `/agent-tools` page | mirror blender-mcp / unity3d-mcp |
| `POST /api/v1/tool` proxy | webapp backend |
| Image QA validation portmanteau | `gimp_validation` (resolution, alpha, ICC) |
| Bridge screenshot history | webapp gallery tab |

## Phase 3 — Fleet handoff (4.3.0)

**Status: complete (v4.3.0)**

| Item | Tool / module |
|------|----------------|
| Blender → GIMP texture handoff | `gimp_import` + fleet HTTP |
| Unity material texture push | unity REST + gimp export |
| Multi-angle texture review | `gimp_vision_refine` |
| Fleet pipeline script | `scripts/fleet_pipeline.py` (blender → gimp → unity) |

## Phase 4 — Telemetry, Docker, monitoring (4.4.0)

**Status: complete (v4.4.0)**

| Item | Tool / module |
|------|----------------|
| Prometheus `/metrics` | optional monitoring extra |
| JSON structured logs | Loki-friendly |
| Docker + GHCR image | MCP server container |
| Smoke test script | `scripts/smoke_test.py` |

## Phase 5 — Robotics and sim art (4.5.0)

**Status: complete (v4.5.0)**

| Item | Tool / module |
|------|----------------|
| Gazebo model icon/decal batch | `gimp_sim_art` → `gazebo_model_icons` |
| Sim texture atlases | `gimp_sim_art` → `build_atlas` + manifest JSON |
| VRChat / social icon pipelines | `gimp_sim_art` → `vrchat_icon_batch`, `push_avatar_handoff` |
| Robotics staging | `stage_for_robotics` + `scripts/sim_art_pipeline.py` |
