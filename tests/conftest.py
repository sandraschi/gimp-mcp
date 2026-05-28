import json
import socket
import threading
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from gimp_mcp.cli_wrapper import GimpCliWrapper
from gimp_mcp.config import GimpConfig
from gimp_mcp.interaction_manager import GimpInteractionManager
from gimp_mcp.main import GimpMCPServer


class MockBridgeServer:
    """A realistic mock of the GIMP 3.0 Bridge socket server."""

    def __init__(self, host="127.0.0.1", port=5001):
        self.host = host
        self.port = port
        self.running = False
        self.server_thread = None
        self.last_request = None
        self.response_data = {"result": "success"}

    def start(self):
        self.running = True
        self.server_thread = threading.Thread(target=self._run)
        self.server_thread.daemon = True
        self.server_thread.start()
        # Small delay to ensure server is bound
        time.sleep(0.1)

    def stop(self):
        self.running = False
        # Connect once to break the accept() loop if needed
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((self.host, self.port))
        except Exception:
             pass
        if self.server_thread:
            self.server_thread.join(timeout=1.0)

    def _run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(1)
            s.settimeout(0.5)

            while self.running:
                try:
                    conn, _addr = s.accept()
                    with conn:
                        data = conn.recv(4096)
                        if data:
                            self.last_request = json.loads(data.decode("utf-8"))
                            conn.sendall(json.dumps(self.response_data).encode("utf-8"))
                except TimeoutError:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Mock server error: {e}")


@pytest.fixture
def mock_bridge():
    """Fixture that provides a running mock bridge server."""
    server = MockBridgeServer()
    server.start()
    yield server
    server.stop()


@pytest.fixture
def mock_subprocess():
    """Fixture to mock subprocess.run for CLI testing."""
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "GIMP CLI success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture
def mock_cli_wrapper():
    """Fixture that provides a mocked GimpCliWrapper."""
    mock = MagicMock(spec=GimpCliWrapper)

    async def _exec_python(code, timeout=None):
        return "CLI_SUCCESS|done"

    async def _exec_script(code, timeout=None):
        return "CLI_SUCCESS|done"

    mock.execute_python_fu.side_effect = _exec_python
    mock.execute_script_fu.side_effect = _exec_script
    mock.is_available.return_value = True
    return mock


@pytest.fixture
def interaction_manager(mock_cli_wrapper):
    """Fixture for GimpInteractionManager with mocked CLI and real config."""
    config = GimpConfig(bridge_port=5001, enable_live_mode=True)
    manager = GimpInteractionManager(config, mock_cli_wrapper)
    return manager


@pytest.fixture
def mcp_server():
    """Fixture for GimpMCPServer instance."""
    # Mock CLI detection to avoid actual GimpCliWrapper exception
    with patch("gimp_mcp.main.GimpDetector.detect_gimp_installation", return_value="/mock/gimp"):
        server = GimpMCPServer()
        return server


@pytest.fixture
def api_client(mcp_server):
    """Fixture for FastAPI TestClient."""
    # FastMCP nesting: server.mcp.app is the FastAPI instance
    return TestClient(mcp_server.mcp.http_app)
