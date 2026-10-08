# Development — gimp-mcp

## Layout

- `src/gimp_mcp/main.py` — FastMCP server, portmanteau registration, lifespan
- `src/gimp_mcp/http_app.py` — uvicorn ASGI app + `/api/*` routes
- `src/gimp_mcp/tools/` — 18 domain modules (file, transform, color, filter,
  layer, analysis, batch, system, pdb_proxy, workspace, channel, animation,
  paths, parasites, gmic, gegl, color_mgmt, bridge/vision/sim-art)
- `src/gimp_mcp/bridge_wrapper.py` — live TCP bridge (`:10824`)
- `src/gimp_mcp/cli_wrapper.py` — headless `gimp-console-3.exe` fallback
- `webapp/frontend/` — React 19 + Vite 7 + Tailwind 3 + Zustand dashboard
- `native/` — Tauri 2 wrapper + NSIS installer config
- `skills/gimp-expert/SKILL.md` — agent guidance (mirrored to `/api/skills`)

Onboarding: N/A is false here — wrappee GIMP 3 is required, so
`docs/ONBOARDING.md` + dashboard `data-testid="onboarding-cue"` apply.

## Workflow

```powershell
just bootstrap  # uv sync + pre-commit install + npm ci
just serve      # backend with reload
just webapp     # frontend dev (or start.ps1 for everything)
just test       # pytest
just lint       # ruff + biome
just fix        # auto-fix
```

## Gates (must all pass before push)

1. `uv run ruff check src/` + `ruff format --check src/`
2. `uv run pytest tests/ -q` (currently 50 passed, 2 skipped)
3. Frontend `tsc --noEmit` + `bun run biome:ci`
4. `just --list` parses (fleet.just import provides mcpb-pack,
   cua-nsis-test, cua-webapp-test)

Python floor is 3.12 (`requires-python = ">=3.12"`); FastMCP pinned
`>=3.4.4,<4`. Line length 200 for ruff (120 in AGENTS code rules is
aspirational — ruff config is authoritative).
