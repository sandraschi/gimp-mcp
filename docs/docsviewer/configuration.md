# ⚙️ Configuration Guide

Complete configuration reference for GIMP MCP server, including environment variables, MCP settings, and performance tuning.

## MCP Server Configuration

### Claude Desktop Setup

#### Basic Configuration
```json
{
  "mcpServers": {
    "gimp-mcp": {
      "command": "uv",
      "args": ["--directory", "D:/Dev/repos/gimp-mcp", "run", "gimp_mcp"],
      "env": {
        "GIMP_EXECUTABLE": "C:\\Program Files\\GIMP 3\\bin\\gimp-3.0.exe"
      }
    }
  }
}
```

#### Windows Path Example
```json
{
  "GIMP_EXECUTABLE": "C:\\Program Files\\GIMP 3\\bin\\gimp-3.0.exe"
}
```

#### macOS Path Example
```json
{
  "GIMP_EXECUTABLE": "/Applications/GIMP.app/Contents/MacOS/GIMP"
}
```

#### Linux Path Example
```json
{
  "GIMP_EXECUTABLE": "/usr/bin/gimp"
}
```

## Environment Variables

### Required Settings

#### `GIMP_EXECUTABLE`
Path to GIMP executable. If not set, the server will attempt auto-detection.
```bash
# Windows
export GIMP_EXECUTABLE="C:\Program Files\GIMP 3\bin\gimp-3.0.exe"

# macOS
export GIMP_EXECUTABLE="/Applications/GIMP.app/Contents/MacOS/GIMP"

# Linux
export GIMP_EXECUTABLE="/usr/bin/gimp"
```

### Performance Settings

#### `OPERATION_TIMEOUT`
Maximum seconds for single operations (default: 30)
```bash
export OPERATION_TIMEOUT=60  # Longer for complex filters
```

#### `MAX_CONCURRENT_PROCESSES`
Concurrent GIMP operations (default: 3)
```bash
export MAX_CONCURRENT_PROCESSES=1   # Conservative (less resource usage)
export MAX_CONCURRENT_PROCESSES=5   # Aggressive (faster batching)
```

### Security Configuration

#### `ALLOWED_DIRECTORIES`
List of directories the server is allowed to access (default: empty, allows all)
```json
{
  "env": {
    "ALLOWED_DIRECTORIES": "C:\\Users\\User\\Pictures,D:\\Projects"
  }
}
```

## Troubleshooting Configuration

### "GIMP executable not found"
1. Verify GIMP is installed.
2. Check if the path is correct in `config.yaml` or environment variables.
3. Use the `GIMP_AUTO_DETECT=true` setting (default) to let the server find it.

---

**Configuration complete! Your GIMP MCP server is optimized for your workflow.** ⚙️🚀

*For advanced users: Check the [development documentation](../development/README.md) for custom configuration options.*
