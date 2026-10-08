# Troubleshooting — gimp-mcp

| Symptom | Cause | Fix |
|---|---|---|
| Bridge inactive (`just bridge-status`) | Plugin not installed / not started | `just bridge-install`, restart GIMP, Filters > Development > MCP > Start MCP Bridge |
| `gimp-console-3.exe` not found | Store GIMP or missing GIMP 3 | Install standalone GIMP 3.2+ from gimp.org; set `GIMP_BIN` |
| Port 10772/10773 busy | Stale process | `start.ps1` clears them; or `just kill` |
| Dashboard red dot / onboarding cue | Backend down | `just serve`; check `GET :10773/api/health` |
| Biome `unknown key preset` | Old config on Biome 2.x | Fixed: `preset` line removed (recommended is default-on) |
| `tsc` unused-var errors | Dead helpers | Removed `checkBackendHealth` (chat), `addLog` (dashboard) |
| pre-commit not running | Hook never installed | `uv run pre-commit install` (also in `just bootstrap`) |
| NSIS workshop: backend 404 on `/api/health` | Wrong HealthPath | `fleet-start.config.ps1` HealthPath must match a real route in `http_app.py` |
| Batch overwrote masters | Output == input dir | Always set a separate output directory (see skill Safety) |
| `uv lock --check` fails | pyproject/lock drift | `uv lock` then commit `uv.lock` |

GIMP-side errors (PDB arg mismatches, plug-in missing like G'MIC) surface
in the tool result `error` field — read `message` first, it is written for
conversational agents.
