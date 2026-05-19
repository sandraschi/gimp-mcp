# GIMP Integration Guide

## Requirements

**GIMP 3.2+ standalone** is required. The Windows Store version of GIMP does not include `gimp-console-3.exe`, which means CLI batch mode will not work. Always download from [gimp.org](https://www.gimp.org/downloads/).

- GIMP 3.2 is the minimum — the bridge plugin uses `gi.repository.Gimp` (GIMP 3 API)
- GIMP 2.x is **not supported** (uses `gimpfu` instead of `gi.repository`)

## How the GIMP Live Bridge Works

The Live Bridge is a TCP server that runs **inside** GIMP's process:

1. GIMP starts and loads the bridge plugin (`gimp_mcp_bridge.py`)
2. The plugin creates a `GimpMcpBridge` (subclass of `Gimp.PlugIn`) which opens a TCP socket on `127.0.0.1:10775`
3. The MCP server's `GimpBridgeWrapper` (`bridge_wrapper.py:20`) connects to this socket
4. Python code snippets are sent as JSON `{"code": "..."}` over TCP
5. The bridge executes them on GIMP's main thread via `GLib.idle_add` and returns the result

This means the GIMP UI remains responsive and the same GIMP session can handle many sequential operations without restarting.

### Bridge Protocol

```
Request:  {"code": "from gi.repository import Gimp; print(Gimp.get_version())"}
Response: {"result": "success", "error": null}
```

The bridge provides these globals to all executed code:
- `Gimp` — `gi.repository.Gimp`
- `GObject` — `gi.repository.GObject`
- `GLib` — `gi.repository.GLib`
- `pdb` — `Gimp.get_pdb()` (the Procedural Database interface)

## GIMP PDB Proxy

The `gimp_pdb` tool at `tools/pdb_proxy.py:61` is a universal escape hatch to call **any** of GIMP's ~1000+ PDB procedures by name.

```python
# Selection feather
gimp_pdb("gimp_selection_feather", [image_id, 5.0])

# Gaussian blur
gimp_pdb("plug_in_gauss", [image_id, layer_id, 5.0, 5.0, 0])

# Set font on a text layer
gimp_pdb("gimp_text_layer_set_font", [layer_id, "Arial"])
```

The proxy handles both GIMP 3's GI API (hyphenated names like `gimp-version`) and the legacy `gimpfu` (underscore names like `gimp_version`). It tries GI first, falls back to `gimpfu`.

## Additional Tool Domains

Beyond the universal proxy, the following dedicated portmanteau tools wrap specific GIMP domains:

| Tool | Purpose | Uses PDB |
|------|---------|----------|
| `gimp_workspace` | List open images, undo/redo groups, metadata, resolution | `gimp-image-list`, `gimp-image-undo`, `gimp-image-get-metadata` |
| `gimp_channel` | Create/delete/set color/opacity on channels | `gimp-channel-new`, `gimp-channel-set-color`, etc. |
| `gimp_animation` | Frame-based GIF animation (layers as frames) | `gimp-image-set-`, export via `file-gif-save` |
| `gimp_paths` | SVG vector paths: create, stroke, import, export | `gimp-vectors-new`, `gimp-vectors-import-from-file` |
| `gimp_parasites` | XCF metadata (parasites) on images/drawables | `gimp-image-get-parasite`, `gimp-image-attach-parasite` |
| `gimp_gmic` | 500+ G'MIC filters via plug-in-gmic | `plug-in-gmic` with filter command strings |
| `gimp_gegl` | GEGL non-destructive editing operations | `gegl-*` PDB procedures |
| `gimp_color_management` | ICC profiles, assignment, conversion, soft proofing | `gimp-image-get-color-profile`, `gimp-image-convert-color-profile` |

## GIMP Python-Fu Differences (GIMP 3)

| Aspect | GIMP 2.x (gimpfu) | GIMP 3 (gi.repository) |
|--------|-------------------|----------------------|
| Import | `from gimpfu import *` | `from gi.repository import Gimp, GLib, GObject` |
| PDB access | `pdb.gimp_version()` | `pdb = Gimp.get_pdb(); proc = pdb.lookup_procedure("gimp-version")` |
| Image IDs | `image.ID` integer | `Gimp.Image` objects |
| Menu registration | `register()` function | `Gimp.PlugIn` subclass |
| Python version | Python 2.7 | Python 3.12+ |

The GIMP MCP bridge handles both APIs transparently via the PDB proxy. You don't need to worry about these differences when using the portmanteau tools.

## Known Limitations

- **Windows Store GIMP** — CLI batch mode is unavailable. Only Live Bridge works.
- **Bridge requires manual first-start** — The bridge plugin only activates after being run once via `Filters > Development > MCP > Start MCP Bridge`. `start.ps1 -RestartGimp` handles this automatically.
- **Single GIMP instance** — The bridge binds to a single TCP port (10775). Only one GIMP instance with bridge can run at a time.
- **Headless mode** — CLI batch (`gimp-console-3.exe`) spawns a new process for each operation. It's slower than Live Bridge but more reliable for automated pipelines.

## Troubleshooting Bridge Connection

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Bridge inactive` | GIMP not running or bridge not started | `just start-gimp` to auto-launch |
| `Connection refused` | Bridge plugin not installed | `just bridge-install` |
| `Bridge inactive on port 10775` | Bridge never started in this GIMP session | Run `Filters > Development > MCP > Start MCP Bridge` once |
| `PDB_RESULT error` | Invalid PDB procedure or args | Check procedure name (hyphen vs underscore) and argument types |
| `No GIMP execution method available` | GIMP not detected | Install standalone GIMP 3.2+ from gimp.org |
| Port still occupied | Previous GIMP instance not fully killed | `just kill` or Task Manager |

## Verification

```bash
# Check live bridge
just bridge-status

# Call GIMP version via PDB
just pdb "gimp-version"

# Run full PDB test
just test-pdb
```
