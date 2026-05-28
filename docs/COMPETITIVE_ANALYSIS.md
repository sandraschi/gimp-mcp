# Competitive Analysis — GIMP MCP Ecosystem

Last updated: 2026-05-28 (Phase 3 complete)

Compares **sandraschi/gimp-mcp** (this repo) with other GIMP automation and MCP projects.

## Summary

| Project | Scale | Architecture | Standout |
|---------|-------|--------------|----------|
| GIMP built-in Script-Fu / Python-Fu | Native | In-process PDB | Full API, steep learning curve |
| GIMP batch (`gimp-console -b`) | Native | Headless CLI | Reliable batch, no live canvas |
| Generic MCP image servers | Various | HTTP/stdio + external APIs | No GIMP PDB depth |
| **sandraschi/gimp-mcp** | 17 portmanteau + agentic | FastMCP 3.2 + **dual mode** (bridge + CLI) | Fleet webapp, G'MIC/GEGL, robotics textures |

## Where we lead

- **Dual-mode execution** — live TCP bridge (:10824) **and** headless `gimp-console` fallback
- **Portmanteau design** — 17 domain tools instead of 50+ atomic MCP tools
- **FastMCP 3.2 SOTA** — sampling, skills, prefab UI, structured dialogic returns
- **Fleet integration** — webapp (10772/10773), `just` recipes, composition with blender-mcp / unity3d-mcp
- **Professional extensions** — G'MIC, GEGL, ICC color management, animation/GIF, paths/SVG
- **Agent Lab alignment** — `gimp_bridge`, `gimp_render` for vision loops (Phase 1)

## Gaps we are closing (roadmap)

See [ROADMAP.md](ROADMAP.md).

| Gap | Our response | Phase |
|-----|--------------|-------|
| Unified bridge status vs scattered `gimp_live_status` | `gimp_bridge` portmanteau | 1 (done) |
| Agent vision capture from open canvas | `gimp_render` → `capture_active` | 1 (done) |
| Hands-In vs Hands-Off agent guidance | `gimp_bridge` → `execution_mode` | 1 (done) |
| Stale port docs (10775 vs 10824) | Reconcile to **10824** fleet standard | 1 (done) |
| Webapp Agent Lab page | `/agent-tools` tabs (mirror blender/unity) | 2 (done) |
| Fleet texture pipeline (blender UV → gimp → unity) | `gimp_import_tool` + `scripts/fleet_pipeline.py` | 3 (done) |
| Prometheus / Docker monitoring | telemetry + GHCR image | 4 |

## What we deliberately skip

- **Replacing GIMP UI** — agents augment GIMP, not rebuild it
- **Cloud-only image APIs as primary path** — local-first GIMP + optional AI gen
- **One tool per PDB procedure** — portmanteau + `gimp_pdb` escape hatch instead

## Architecture comparison

```text
Typical batch scripts:  shell → gimp-console -b → Script-Fu → files on disk

sandraschi:             MCP client → stdio OR HTTP (:10773)
                              → Hands-In: TCP bridge plugin :10824
                              → Hands-Off: gimp-console Python-Fu / PIL helpers
                              → 17 portmanteau tools + agentic workflows
```

## Fleet pipeline role

```text
blender-mcp (UV bake / render) → gimp-mcp (textures, atlases, QA) → unity3d-mcp (materials)
gazebo-mcp (sim meshes)        → unity3d-mcp (import)              → gimp-mcp (decals/icons)
```

## References

- [ROADMAP.md](ROADMAP.md)
- [docs/readme/ARCHITECTURE.md](readme/ARCHITECTURE.md)
- [docs/readme/GIMP_INTEGRATION.md](readme/GIMP_INTEGRATION.md)
- [unity3d-mcp competitive analysis](https://github.com/sandraschi/unity3d-mcp/blob/main/docs/COMPETITIVE_ANALYSIS.md)
- [blender-mcp competitive analysis](https://github.com/sandraschi/blender-mcp/blob/main/docs/COMPETITIVE_ANALYSIS.md)
