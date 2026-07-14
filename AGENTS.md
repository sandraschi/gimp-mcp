# gimp-mcp — Agent Context

FastMCP 3.2+ server for professional image editing using GIMP.

## Quick Start
```powershell
uv run python -m gimp_mcp.main          # stdio mode (Claude Desktop)
uv run python -m gimp_mcp.main          # SSE mode (MCP_PORT=10773)
uv run ruff check src/                   # Lint
```

## Ports
- Frontend: 10772
- Backend: 10773
- GIMP Bridge: 10824
- Logging: 11062

## Architecture
- 17 portmanteau tools (gimp_file, gimp_transform, gimp_color, gimp_filter, gimp_layer, gimp_analysis, gimp_batch, gimp_system, gimp_workspace, gimp_channel, gimp_animation, gimp_paths, gimp_parasites, gimp_color_management, gimp_gegl, gimp_gmic, gimp_pdb)
- Dual transport: stdio (default) and SSE/HTTP
- Live bridge (port 10824) + headless CLI modes
- FastMCP 3.2+ sampling, prompts, resources, skills, Prefab UI

## Code Rules
- Ruff Python linting (line length 120)
- No bare `except: pass` — log exceptions
- Use `from gimp_mcp.logging_config import get_logger` for logging
- Tauri native wrapper at `native/`

## Key Files
| File | Purpose |
|------|---------|
| `main.py` | Portmanteau tool registration |
| `http_app.py` | FastAPI web backend |
| `bridge_wrapper.py` | Live GIMP TCP bridge |
| `cli_wrapper.py` | Headless GIMP CLI |
| `gimp_detector.py` | Cross-platform GIMP detection |
