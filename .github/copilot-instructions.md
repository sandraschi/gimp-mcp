# gimp-mcp — GitHub Copilot instructions

## Session Context

Before starting work in this repo, load tool awareness for gimp-mcp (see `.cursorrules` for the full prompt):

- 18 portmanteau tools led by `gimp_file`, `gimp_transform`, `gimp_color`, `gimp_filter`, `gimp_layer`, `gimp_analysis`, `gimp_batch`, `gimp_system`, plus the universal `gimp_pdb` proxy for any of GIMP's ~1000 PDB procedures.
- Transports: stdio via `uv run python -m gimp_mcp.main`; HTTP backend on port 10773 (`src/gimp_mcp/http_app.py`); frontend on 10772; live GIMP bridge on 10824 with headless CLI fallback.
- Key files: `src/gimp_mcp/main.py`, `src/gimp_mcp/http_app.py`, `src/gimp_mcp/bridge_wrapper.py`, `skills/gimp-expert/SKILL.md`.
- Gates: `uv run ruff check src/`, `uv run pytest tests/ -q`, frontend `tsc --noEmit` + `biome ci`.
