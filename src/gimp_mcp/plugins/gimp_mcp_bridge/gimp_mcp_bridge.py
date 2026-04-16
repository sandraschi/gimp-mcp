#!/usr/bin/env python3
"""
GIMP MCP Bridge Plugin (v3.1.1)
High-performance JSON-RPC bridge for real-time AI control of GIMP 3.0.
"""

import json
import logging
import queue
import socket
import sys
import threading
import traceback

import gi

# Require GIMP 3.0
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, GLib, GObject  # noqa: E402

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GimpMcpBridge")

PORT = 10774
HOST = "127.0.0.1"


class GimpMcpBridge(Gimp.PlugIn):
    """
    GIMP 3.0 Plugin that provides an MCP bridge server.
    """

    def __init__(self):
        super().__init__()
        self.command_queue = queue.Queue()
        self.server_thread = None
        self.is_running = False

    def do_query_procedures(self):
        """Register the bridge procedure."""
        return ["gimp-mcp-bridge-start"]

    def do_create_procedure(self, name):
        """Create the bridge start procedure."""
        procedure = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, self.run, None)
        procedure.set_image_types("*")
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.ALWAYS)
        procedure.set_menu_label("Start MCP Bridge")
        procedure.set_documentation(
            "Starts the MCP JSON-RPC server",
            "Initializes a background thread that listens for MCP commands on port 10774",
            name,
        )
        procedure.set_attribution("Sandra Schipal", "Sandra Schipal", "2026")
        procedure.add_menu_path("<Image>/Filters/Development/MCP")

        return procedure

    def run(self, procedure, run_mode, image, n_drawables, drawables, config, data):
        """Main entry point to start the bridge."""
        if self.is_running:
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

        logger.info(f"Starting GIMP MCP Bridge on {HOST}:{PORT}")

        self.is_running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

        # Register an idle callback to process commands on the main thread
        GLib.idle_add(self._process_commands)

        # Display message to user
        Gimp.message(f"GIMP MCP Bridge Active on port {PORT}")

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

    def _run_server(self):
        """Background thread running the TCP listener."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((HOST, PORT))
                s.listen(5)
                while self.is_running:
                    conn, _addr = s.accept()
                    with conn:
                        data = conn.recv(16384)
                        if not data:
                            continue

                        try:
                            request = json.loads(data.decode("utf-8"))
                            self.command_queue.put((request, conn))
                        except Exception as e:
                            logger.error(f"Failed to parse request: {e}")
                            conn.sendall(json.dumps({"error": str(e)}).encode("utf-8"))
            except Exception as e:
                logger.error(f"Server error: {e}")
                self.is_running = False

    def _process_commands(self):
        """
        Polls the command queue and executes snippets on GIMP's main thread.
        This is called by GLib.idle_add.
        """
        if not self.is_running:
            return False  # Stop polling

        try:
            while not self.command_queue.empty():
                request, conn = self.command_queue.get_nowait()
                code = request.get("code")

                logger.info(f"Executing live command: {code[:50]}...")

                result = None
                error = None

                try:
                    # Provide essential globals for the script
                    # This allows the script to use 'Gimp', 'image', 'drawables' etc.
                    # We fetch current context to ensure snippets work as expected
                    # pdb_result = Gimp.get_pdb().run_procedure('gimp-image-list', [])

                    # Execution sandbox (limited but powerful)
                    exec_globals = {
                        "Gimp": Gimp,
                        "GObject": GObject,
                        "GLib": GLib,
                        "pdb": Gimp.get_pdb(),
                        "logger": logger,
                    }

                    # Execute the code
                    exec(code, exec_globals)
                    result = "success"
                except Exception:
                    error = traceback.format_exc()
                    logger.error(f"Execution error: {error}")

                # Send response back to MCP server
                response = {"result": result, "error": error}
                try:
                    conn.sendall(json.dumps(response).encode("utf-8"))
                except (OSError, json.JSONDecodeError):
                    pass

        except queue.Empty:
            pass

        return True  # Continue polling


# Entry point
if __name__ == "__main__":
    Gimp.main(GimpMcpBridge.__gtype__, sys.argv)
