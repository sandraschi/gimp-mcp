# Onboarding — gimp-mcp

First-timer path from zero to AI-edited image. Assumes Windows + Goliath,
but every step works on macOS/Linux with adjusted paths.

## What this is for

gimp-mcp lets an AI agent edit images through GIMP 3: 18 portmanteau MCP
tools plus a universal `gimp_pdb` proxy covering ~1000 GIMP procedures.
Two modes: **headless CLI** (always works) and **live bridge** (GIMP GUI
open, real-time canvas snapshots for the vision loop).

## Money / accounts

None. GIMP 3 is free software, everything runs locally (Python + uv +
optional Node for the dashboard). No cloud key is required; the Settings
page accepts local Ollama (`:11434`) / LM Studio (`:1234`) or cloud keys
only if you want chat completions through them.

## Pitfalls

- Install **standalone GIMP 3.2+ from gimp.org**, NOT the Windows Store
  build (Store sandboxing breaks `gimp-console-3.exe` batch mode).
- The bridge plugin must live at
  `%APPDATA%\GIMP\3.2\plug-ins\gimp_mcp_bridge\` (`just bridge-install`
  does this), then Filters > Development > MCP > Start MCP Bridge.
- Ports 10772 (frontend), 10773 (backend), 10824 (bridge) must be free;
  `start.ps1` clears them automatically.
- Never point batch output at your masters folder — always use a separate
  output directory (the skill enforces copy-on-write).

## Sanity check

```powershell
just bootstrap   # deps + hooks + frontend
just serve       # backend on :10773
```

Then: `GET http://127.0.0.1:10773/api/health` → `{"status":"healthy"}`.
Open `http://localhost:10772`, run `just bridge-status`, and resize one
photo via `gimp_transform(operation="resize", ...)`. If the dashboard hero
dot is green, onboarding is done and the red cue above disappears.
