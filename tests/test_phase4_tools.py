"""Tests for Phase 4 telemetry, logging, and smoke helpers."""

from __future__ import annotations

from unittest.mock import patch


class TestTelemetry:
    def test_metrics_disabled_render(self):
        from gimp_mcp.utils import telemetry

        telemetry._metrics_initialized = False
        with patch.object(telemetry, "metrics_enabled", return_value=False):
            telemetry.init_metrics()
        body = telemetry.render_metrics()
        assert b"disabled" in body

    def test_json_log_formatter(self):
        import logging

        from gimp_mcp.utils.structured_logging import JsonLogFormatter

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="hello",
            args=(),
            exc_info=None,
        )
        line = JsonLogFormatter().format(record)
        assert '"service": "gimp-mcp"' in line
        assert "hello" in line


class TestMetricsRoutes:
    def test_metrics_routes_registered(self):
        from gimp_mcp.http_app import app

        paths = {getattr(r, "path", None) for r in app.routes}
        assert "/api/metrics" in paths
        assert "/metrics" in paths
