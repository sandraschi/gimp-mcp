# Monitoring

Prometheus metrics, JSON logs for Loki, optional Docker monitoring profile.

## Metrics

| Endpoint | Port | Notes |
|----------|------|-------|
| `/api/metrics` | 10773 | HTTP app (Prometheus scrape) |
| `/metrics` | 9073 | Sidecar scrape port (`PROMETHEUS_PORT`) |

Enable optional dependency:

```powershell
uv sync --extra monitoring
```

Environment:

| Variable | Default | Purpose |
|----------|---------|---------|
| `GIMP_MCP_METRICS_ENABLED` | `true` | Disable with `false` |
| `PROMETHEUS_PORT` | `9073` | Sidecar metrics port |
| `GIMP_MCP_LOG_FORMAT` | text | Set `json` for Loki |
| `GIMP_MCP_LOG_LEVEL` | INFO | Log level |

Gauges:

- `gimp_mcp_bridge_connected` — live bridge TCP reachable
- `gimp_mcp_execution_mode` — Hands-In vs Hands-Off
- `gimp_mcp_tool_calls_total` / `gimp_mcp_tool_duration_seconds` — per-tool telemetry

## Docker monitoring stack

```powershell
docker compose --profile monitoring up -d
```

| Service | Host port |
|---------|-----------|
| Grafana | 3001 |
| Prometheus | 9091 |
| Loki | 3101 |

## Smoke test

```powershell
uv run python scripts/smoke_test.py
```

See [DOCKER.md](DOCKER.md) for container-only MCP deployment.
