# Installation Guide

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **GIMP 3.2+** | Standalone install (not Windows Store) |
| **Python 3.12+** | [python.org](https://python.org) |
| **uv** | `pip install uv` or [docs.astral.sh/uv](https://docs.astral.sh/uv/) |

> **Windows Store GIMP** does not include `gimp-console-3.exe`, so CLI batch mode will not work. Always install the standalone version from [gimp.org](https://www.gimp.org/downloads/).

## Quick Start

```powershell
# 1. Install Python dependencies
uv sync

# 2. Start everything (backend + frontend)
.\start.ps1

# 3. With automatic GIMP restart (installs bridge plugin)
.\start.ps1 -RestartGimp
```

## MCPB Package (Cursor / Claude Desktop)

Build the bundle:

```powershell
uv run python build_mcpb.py
```

Output: `dist/gimp-mcp-4.5.1.mcpb`

### Install from MCPB

1. Build or download `dist/gimp-mcp-*.mcpb`
2. In **Cursor**: Settings → MCP → Add server → Install from MCPB → select the `.mcpb` file
3. Or extract manually and point MCP at the bundled `mcp_config` in `mcpb/manifest.json`:

```json
{
  "mcpServers": {
    "gimp-mcp": {
      "command": "uv",
      "args": ["--directory", "D:/Dev/repos/gimp-mcp", "run", "python", "-m", "gimp_mcp.mcp_server"],
      "env": { "PYTHONUNBUFFERED": "1" }
    }
  }
}
```

The MCPB bundle includes `src/`, prompts manifest, `skills/`, and install docs (`docs/readme/INSTALL.md`, fleet/sim-art guides).

### Dev install (no MCPB)

```powershell
uv sync
uv run python -m gimp_mcp.mcp_server
```

## Installing GIMP 3

1. Download GIMP 3.2+ from [gimp.org/downloads](https://www.gimp.org/downloads/)
2. Run the installer — choose **"Standalone install"**, not the Microsoft Store version
3. Default path on Windows: `C:\Users\<you>\AppData\Local\Programs\GIMP 3\bin\gimp-3.exe`
4. Verify by running `gimp-3.exe` or `gimp-console-3.exe` from a terminal

## Starting the Server

| Method | Command | What it does |
|--------|---------|--------------|
| Start script | `.\start.ps1` | Backend (10773) + Frontend (10772) + browser |
| With GIMP | `.\start.ps1 -RestartGimp` | Same + kills old GIMP, launches fresh with bridge |
| Backend only | `.\start.ps1 -BackendOnly` | API server only, no frontend |
| Just recipes | `just start` | Calls start.ps1 |
| Just with GIMP | `just start-gimp` | Calls start.ps1 -RestartGimp |
| Backend dev | `just serve` | uvicorn with hot reload on 10773 |
| Frontend only | `just webapp` | Vite dev server on 10772 |
| MCP stdio | `uv run python -m gimp_mcp.mcp_server` | IDE / Claude Desktop stdio transport |

### Headless Mode

Run everything without visible windows:

```powershell
.\start.ps1 -Headless
```

## Bridge Plugin Installation

The bridge plugin is a GIMP 3 plug-in that opens a TCP server inside GIMP for real-time AI control.

**Automatic**: `start.ps1` and `start.ps1 -RestartGimp` both auto-install the bridge plugin.

**Manual**:

```powershell
just bridge-install
```

This copies `src/gimp_mcp/plugins/gimp_mcp_bridge/gimp_mcp_bridge.py` to:

- `%APPDATA%\GIMP\3.2\plug-ins\gimp_mcp_bridge\`
- `%APPDATA%\GIMP\3.0\plug-ins\gimp_mcp_bridge\`

## Agent Lab & Fleet Pipelines

After the webapp is running (`http://127.0.0.1:10772/agent-tools`):

| Pipeline | Script | MCP tool |
|----------|--------|----------|
| Textures (blender → gimp → unity) | `scripts/run-fleet-pipeline.ps1` | `gimp_import_tool` |
| Sim art (Gazebo / VRChat icons) | `scripts/run-sim-art-pipeline.ps1` | `gimp_sim_art_tool` |

Sim-art **automated import** (Gazebo model thumbnails, avatar `.thumb.png`):

```powershell
.\scripts\run-sim-art-pipeline.ps1 `
  -InputDir "D:\Temp\model_renders" `
  -Pipeline gazebo `
  -ModelsRoot "$env:USERPROFILE\.gz\fuel\fuel.gazebosim.org\OpenRobotics\models" `
  -AutoImport
```

See [SIM_ART_PIPELINE.md](../SIM_ART_PIPELINE.md) and [FLEET_PIPELINE.md](../FLEET_PIPELINE.md).

## Verifying the Setup

```powershell
# Smoke test (Agent Lab tools + metrics)
uv run python scripts/smoke_test.py

# Check bridge status
just bridge-status

# Run full test suite
just test
```

## Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
"mcpServers": {
  "gimp-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/gimp-mcp", "run", "python", "-m", "gimp_mcp.mcp_server"]
  }
}
```

## Ports Reference

| Port | Service | Purpose |
|------|---------|---------|
| 10772 | Frontend | Vite React webapp (Dashboard, Agent Tools) |
| 10773 | Backend | uvicorn FastAPI + FastMCP ASGI |
| 10824 | Bridge | GIMP Live Bridge TCP (inside GIMP plugin) |
| 10892 | robotics-mcp | Optional sim-art handoff probe |
| 10793 | avatar-mcp | Optional avatar thumbnail handoff |

## Troubleshooting

**"Bridge inactive"**: GIMP must be running and the bridge plugin must be started once. Use `just start-gimp` to auto-launch.

**"Port occupied"**: Something else is on 10772/10773/10824. Run `just kill` to force-close, or check with `netstat -ano | findstr ":10772"`.

**"GIMP executable not found"**: Install standalone GIMP 3.2+ or set the path manually in `config.yaml`.

**MCPB install fails**: Ensure `uv` is on PATH and run `uv sync` in the repo before pointing MCP at the bundle.
