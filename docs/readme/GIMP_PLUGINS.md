# GIMP Plugins

## GIMP MCP Bridge Plugin

The bridge plugin (`src/gimp_mcp/plugins/gimp_mcp_bridge/gimp_mcp_bridge.py`) is a GIMP 3 plug-in that opens a TCP server inside GIMP's process, enabling real-time AI control.

### Installation

**Automatic**: Run `.\start.ps1` or `.\start.ps1 -RestartGimp` — the script auto-installs the bridge to GIMP's plug-ins directory.

**Manual**:
```bash
just bridge-install
```

This copies the bridge plugin to:
- `%APPDATA%\GIMP\3.2\plug-ins\gimp_mcp_bridge\`
- `%APPDATA%\GIMP\3.0\plug-ins\gimp_mcp_bridge\`

**Verification**: After starting GIMP, check the bridge is listening:
```bash
just bridge-status
# Expected: "Bridge active on port 10824"
```

### First-Time Activation

The bridge plugin must be started once per GIMP session. Either:
1. Use `.\start.ps1 -RestartGimp` (auto-starts the bridge)
2. Or manually: `Filters > Development > MCP > Start MCP Bridge`

After this, the bridge stays active until GIMP is closed.

### Plugin Architecture

```python
class GimpMcpBridge(Gimp.PlugIn):
```

| Aspect | Detail |
|--------|--------|
| **Base class** | `Gimp.PlugIn` (GIMP 3 API) |
| **Menu registration** | `<Image>/Filters/Development/MCP/Start MCP Bridge` |
| **TCP server** | `127.0.0.1:10824` |
| **Threading** | Background thread for TCP listener, `GLib.idle_add` for main-thread execution |
| **Protocol** | JSON over TCP |
| **Max message size** | 16 KB |

### Plugin Lifecycle

1. GIMP loads `gimp_mcp_bridge.py` from the plug-ins directory at startup
2. `do_query_procedures()` registers the `"gimp-mcp-bridge-start"` procedure
3. `do_create_procedure()` creates the procedure with menu placement
4. When triggered, `run()` starts the TCP server thread and registers `GLib.idle_add` for command processing
5. The TCP server accepts connections, reads JSON, and queues commands
6. `_process_commands()` (called by `GLib.idle_add`) executes queued commands on GIMP's main thread

### Bridge Protocol

```json
Request:  {"code": "from gi.repository import Gimp; print(Gimp.get_version())"}
Response: {"result": "success", "error": null}
```

The `code` field contains arbitrary Python that runs inside GIMP's Python environment. The bridge provides these globals:

| Global | Source | Purpose |
|--------|--------|---------|
| `Gimp` | `gi.repository.Gimp` | GIMP API |
| `GObject` | `gi.repository.GObject` | GObject base |
| `GLib` | `gi.repository.GLib` | GLib utilities |
| `pdb` | `Gimp.get_pdb()` | PDB access |

### Extending the Bridge

To add new bridge capabilities:

1. Edit `src/gimp_mcp/plugins/gimp_mcp_bridge/gimp_mcp_bridge.py`
2. Add new globals to the `exec_globals` dict in `_process_commands()` (line 128)
3. For structured commands beyond raw code, add a handler pattern in the `_process_commands` method
4. Re-install: `just bridge-install`
5. Restart GIMP

Example — adding a `GimpMcpBridge.run_structured_command()` method:

```python
# In _process_commands, add after the 'code' handler:
command = request.get("command")
if command == "get_layers":
    image = Gimp.get_image()
    layers = image.get_layers()
    result = [{"name": l.get_name(), "visible": l.get_visible()} for l in layers]
```

### GIMP 3 Plugin Directory Locations

| OS | Path |
|----|------|
| Windows | `%APPDATA%\GIMP\3.2\plug-ins\` |
| Linux | `~/.config/GIMP/3.2/plug-ins/` |
| macOS | `~/Library/Application Support/GIMP/3.2/plug-ins/` |

### Cleaning Up

```bash
# Remove the bridge plugin
just clean-gimp
```

This deletes `%APPDATA%\GIMP\3.0\plug-ins\gimp_mcp_bridge` and `%APPDATA%\GIMP\3.2\plug-ins\gimp_mcp_bridge`.
