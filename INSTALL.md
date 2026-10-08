# Installation

## 🚀 Quick Start (recommended)

```powershell
# Install just if you don't have it
winget install Casey.Just    # Windows
# scoop install just          # Windows (alternative)
# brew install just           # macOS
# sudo apt install just       # Debian/Ubuntu
# cargo install just          # Linux (Rust)

git clone https://github.com/sandraschi/gimp-mcp
cd gimp-mcp
just
```

The interactive recipe dashboard opens in your browser. From there:

```powershell
just bootstrap   # install all dependencies
just serve       # start the server
just web         # start the frontend (if applicable)
```

> **Why not `pip install`?** MCP servers bundle webapps, configs, project scaffolding, and tooling that a flat Python package can't deliver. PyPI offers no safety advantage — it doesn't audit packages either. `just` gives you the complete, ready-to-run stack.

---

## 🐌 Traditional Setup

If you prefer not to use `just`:

1. Install [Python 3.13+](https://python.org) and [uv](https://docs.astral.sh/uv/)
2. Clone and enter the repo:
   ```powershell
   git clone https://github.com/sandraschi/gimp-mcp
   cd gimp-mcp
   ```
3. Install dependencies:
   ```powershell
   uv sync --all-extras
   ```
4. Start the server:
   ```powershell
   # stdio mode (for MCP clients like Claude Desktop)
   uv run python -m gimp_mcp.server

   # HTTP mode (for web dashboard)
   uv run uvicorn gimp_mcp.server:app --port 10773
   ```

4. (optional) Start the frontend:
   ```powershell
   cd webapp
   npm install
   npm run dev
   ```

5. Open `http://localhost:10773` or the frontend URL.

---

## Claude Desktop

Claude-only one-liner (Windows, installs the released `.mcpb` bundle):

```powershell
irm https://github.com/sandraschi/gimp-mcp/releases/latest/download/install.ps1 | iex
```

Every other client (manual config):

```json
{
  "mcpServers": {
    "gimp-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/sandraschi/gimp-mcp", "gimp-mcp"]
    }
  }
}
```

Developer fallback (local checkout, stdio): same `uv run python -m
gimp_mcp.main` entry used above, with `"cwd": "D:\\Dev\\repos\\gimp-mcp"`.

Windows desktop users can also run the NSIS installer from `dist/`
for the Tauri-wrapped app.

---

## ❓ Troubleshooting

| Issue | Fix |
|---|---|
| `just` not found | Install via `winget install Casey.Just`, `scoop install just`, or `brew install just` |
| Port conflict | Run `just kill-all` to clear fleet ports (10700–11000) |
| Dependencies out of sync | `uv sync --all-extras` |
| Something else | [Open a GitHub issue](https://github.com/sandraschi/gimp-mcp/issues) |

---

*See the main [README](README.md) for feature overview and documentation.*
