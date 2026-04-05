# 🛠️ Installation & Setup (v3.1.1)

Follow these steps to set up the GIMP MCP Server with FastMCP 3.1.1 and the Fleet Standard web application.

## Prerequisites

- **Python 3.12+**: Required for FastMCP 3.1 functionalities.
- **[uv](https://docs.astral.sh/uv/)**: Recommended for high-performance dependency management.
- **GIMP 2.10+**: (GIMP 3.0+ strongly recommended) installed on your system.

## 📦 Quick Start

The easiest way to run the server directly:

```bash
uvx gimp-mcp
```

## 🛠️ Local Development Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sandraschi/gimp-mcp.git
   cd gimp-mcp
   ```

2. **Initialize Environment**:
   ```bash
   uv sync
   ```

3. **Configure Settings (Optional)**:
   Create a `config.yaml` to manually point to your GIMP executable if not automatically detected:
   ```yaml
   gimp_executable: "C:\\Program Files\\GIMP 3\\bin\\gimp-console-3.0.exe"
   ```

## 🎯 Claude Desktop Integration

Add the following configuration to your `claude_desktop_config.json`:

```json
"mcpServers": {
  "gimp-mcp": {
    "command": "uv",
    "args": [
      "--directory", 
      "D:/Dev/repos/gimp-mcp", 
      "run", 
      "gimp_mcp"
    ]
  }
}
```

## 🌐 Webapp Dashboard Setup

To run the **Fleet Standard** web application monitoring:

1. **Navigate to the webapp directory**:
   ```bash
   cd webapp
   ```

2. **Start the application**:
   - **Windows (Recommended)**: Run `start.bat` or `.\start.ps1`.
   - **Manual**: 
     - Backend: `uv run python -m gimp_mcp.main --http --port 10773`
     - Frontend: `npm run dev` (in `webapp/frontend`)

3. **Access the Dashboard**:
   Open `http://localhost:10772` in your browser.

## ✅ Verification

To verify the installation:

1. **Server Logs**: Check that the server initializes with "GIMP MCP Fleet Server (v3.1.1)".
2. **Tools Explorer**: Visit the dashboard and verify that all 8 portmanteau tools are listed.
3. **Claude Discovery**: In Claude Desktop, type "list gimp tools" to verify integration.
