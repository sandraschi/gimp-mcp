# gimp-mcp HTTP MCP server (no GIMP GUI in container).
#
# Build:
#   docker build --target production -t ghcr.io/sandraschi/gimp-mcp:local .
#
# Run:
#   docker run --rm -p 10773:10773 -p 9073:9073 ghcr.io/sandraschi/gimp-mcp:local
#
# Live GIMP (Hands-In) requires GIMP + bridge plugin on the HOST (port 10824).

FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=10773
ENV PROMETHEUS_PORT=9073
ENV GIMP_MCP_METRICS_ENABLED=true
ENV GIMP_MCP_LOG_FORMAT=json
ENV GIMP_MCP_LOG_LEVEL=INFO
ENV GIMP_MCP_BRIDGE_HOST=host.docker.internal
ENV GIMP_MCP_BRIDGE_PORT=10824

WORKDIR /app

FROM base AS production

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e ".[monitoring]"

RUN useradd --create-home --shell /bin/bash mcp \
    && mkdir -p /app/logs \
    && chown -R mcp:mcp /app

USER mcp

EXPOSE 10773 9073

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:10773/api/health', timeout=5)"

CMD ["uvicorn", "gimp_mcp.http_app:app", "--host", "0.0.0.0", "--port", "10773"]

ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.title="GIMP MCP" \
      org.opencontainers.image.description="Agentic GIMP MCP server (live bridge + headless dual mode)" \
      org.opencontainers.image.vendor="FlowEngineer sandraschi" \
      org.opencontainers.image.source="https://github.com/sandraschi/gimp-mcp" \
      org.opencontainers.image.licenses="MIT"
