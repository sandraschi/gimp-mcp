# Configuration — gimp-mcp

## Ports

| Surface  | Port  | Source                              |
|----------|-------|-------------------------------------|
| Frontend | 10772 | `fleet-start.config.ps1`            |
| Backend  | 10773 | `fleet-start.config.ps1`, `MCP_PORT`|
| Bridge   | 10824 | GIMP bridge plugin (TCP)            |
| Metrics  | 11062 | `monitoring/` Prometheus stack      |

Registered in `mcp-central-docs/operations/WEBAPP_PORTS.md`. Never hardcode
a new port — claim one via `claim_ports.py`.

## Environment (`config.yaml` + env)

| Var                   | Default | Purpose                              |
|-----------------------|---------|--------------------------------------|
| `GIMP_BIN`            | autodetect | Path to `gimp-console-3.exe`       |
| `MCP_PORT`            | 10773   | HTTP transport port                  |
| `GIMP_TAURI`          | 0       | `1` inside the Tauri wrapper         |
| `ALLOWED_DIRECTORIES` | —       | Comma-separated file-access whitelist|
| `MAX_FILE_SIZE_MB`    | 100     | Processing cap                       |
| `MCP_BRIDGE_URLS`     | —       | External MCP servers to bridge       |
| `GIMP_MCP_AUTH_TOKEN` | —       | REST auth token (Tauri mode)         |
| `GIMP_MCP_LOG_FORMAT` | text    | `json` for Loki ingestion            |
| `GIMP_PREFAB_TOOLS`   | 1       | `0` disables Prefab UI tools         |

`.env.example` documents every var without secrets. One source of truth:
a single `.env` at repo root (plus the untracked Tauri resource example).

## Launch

`start.ps1` (fleet standard, `-BackendOnly` / `-RestartGimp`) reads
`fleet-start.config.ps1` (uvicorn `gimp_mcp.http_app:app`, health
`/api/health`, vite-npm frontend). `start.bat` delegates to it.
