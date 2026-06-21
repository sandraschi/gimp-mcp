# Docker

MCP HTTP server container (no GIMP GUI inside the image).

## Build and run

```powershell
docker build --target production -t ghcr.io/sandraschi/gimp-mcp:local .
docker run --rm -p 10773:10773 -p 9073:9073 ghcr.io/sandraschi/gimp-mcp:local
```

Health: `http://127.0.0.1:10773/api/health`

## Compose

```powershell
# MCP only
docker compose up gimp-mcp

# With Prometheus/Grafana/Loki
docker compose --profile monitoring up -d
```

Image: `ghcr.io/sandraschi/gimp-mcp:latest`

## Hands-In vs container

The container runs the **MCP server only**. Live GIMP GUI and the bridge plugin (`:10824`) stay on the host.

Set for Docker → host bridge:

```text
GIMP_MCP_BRIDGE_HOST=host.docker.internal
GIMP_MCP_BRIDGE_PORT=10824
```

Headless batch (`gimp-console`) paths still work when GIMP is installed on the host and paths are mounted.

## Related

- [MONITORING.md](MONITORING.md)
- [FLEET_PIPELINE.md](FLEET_PIPELINE.md)
