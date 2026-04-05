# Loguru Logging Guide for GIMP-MCP MCP

## Overview

GIMP-MCP MCP uses **Loguru** for structured, colorful, and highly configurable logging throughout the application. This guide explains how logging works, how to view logs, and how to troubleshoot logging issues.

## What is Loguru?

**Loguru** is a Python logging library that provides:

- **Simple API**: Just `from loguru import logger; logger.info("message")`
- **Structured logging**: Consistent format with timestamps, levels, and context
- **Colorful output**: Automatic color coding for different log levels
- **Multiple handlers**: Console, files, rotation, filtering, etc.
- **No configuration needed**: Works out of the box with sensible defaults

## Loguru Configuration in GIMP-MCP MCP

### Default Configuration

```python
def setup_logging(log_level: str = "INFO"):
    """Configure structured logging with loguru."""
    logger.remove()  # Remove default handler

    # Configure log format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Add console handler
    logger.add(
        sys.stderr,        # Output to stderr
        level=log_level,   # Minimum log level
        format=log_format, # Structured format
        colorize=True      # Color output
    )
```

### Log Format Explained

```
2024-01-15 14:30:25.123 | INFO     | GIMP-MCP_mcp.server:main:94 - [START] Starting GIMP-MCP MCP Server
│          │        │     │         │          │         │      │
│          │        │     │         │          │         │      └─ Log message
│          │        │     │         │          │         └─ Line number
│          │        │     │         │          └─ Function name
│          │        │     │         └─ Module name
│          │        │     └─ Log level (padded to 8 chars)
│          └─ Timestamp (YYYY-MM-DD HH:mm:ss.SSS)
└─ Green timestamp
```

## How to View Logs

### 1. When Running the Server Directly

**Basic logging (INFO level):**
```bash
python -m GIMP-MCP_mcp
```

**Debug logging (DEBUG level):**
```bash
python -m GIMP-MCP_mcp --debug
```

**HTTP server mode:**
```bash
python -m GIMP-MCP_mcp --http --debug
```

### 2. When Running via Claude Desktop

Claude Desktop captures logs differently depending on your platform:

#### Windows (PowerShell/Command Prompt)
```powershell
# Start Claude Desktop and check the console window
# Logs appear in the Claude Desktop application console
```

#### macOS
```bash
# Logs are available in Console.app
# Search for "Claude" or "MCP" in Console.app
```

#### Linux
```bash
# Check systemd journal
journalctl -f | grep -i claude

# Or check Claude Desktop logs
tail -f ~/.config/Claude/logs/*.log
```

### 3. When Running via MCP CLI

```bash
# Direct MCP server execution
mcp run GIMP-MCP-mcp

# With debug logging
LOG_LEVEL=DEBUG mcp run GIMP-MCP-mcp
```

### 4. Programmatic Log Access

```python
from GIMP-MCP_mcp.app import get_app
from GIMP-MCP_mcp.server import setup_logging

# Setup logging
setup_logging("DEBUG")

# Get logs programmatically
import io
from loguru import logger

# Capture logs to string
log_stream = io.StringIO()
logger.add(log_stream, format="{time} | {level} | {message}")

# Your code here...

# Get captured logs
logs = log_stream.getvalue()
print(logs)
```

## Log Levels

GIMP-MCP MCP uses standard Python logging levels:

| Level | Numeric | Description | When to Use |
|-------|---------|-------------|-------------|
| `DEBUG` | 10 | Detailed diagnostic information | Development, troubleshooting |
| `INFO` | 20 | General information about operations | Normal operation |
| `WARNING` | 30 | Warning about potential issues | Non-critical issues |
| `ERROR` | 40 | Error that prevents operation | Operation failures |
| `CRITICAL` | 50 | Critical error requiring immediate attention | System failures |

### Changing Log Levels

#### Via Command Line
```bash
# Debug mode (most verbose)
python -m GIMP-MCP_mcp --debug

# Default INFO level
python -m GIMP-MCP_mcp
```

#### Via Environment Variable
```bash
# Override log level
LOG_LEVEL=WARNING python -m GIMP-MCP_mcp
LOG_LEVEL=DEBUG python -m GIMP-MCP_mcp
```

#### Programmatically
```python
from loguru import logger

# Change level at runtime
logger.level("DEBUG")

# Or set via environment
import os
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level)
```

## Where Logs Go

### Console Output (Primary)
- **Destination**: `sys.stderr` (standard error stream)
- **Format**: Colored, structured output
- **Visibility**: Console/terminal where GIMP-MCP MCP is running

### Claude Desktop Integration
- **Windows**: Claude Desktop console window
- **macOS**: Console.app or Claude Desktop logs
- **Linux**: systemd journal or log files

### MCP Protocol Logs
When used through MCP protocol, logs are handled by the MCP client (Claude Desktop) and may appear in:
- Claude Desktop's debug console
- MCP server logs
- Network traffic logs (if applicable)

## Troubleshooting Log Visibility

### Problem: No Logs Visible

**Check if server is running:**
```bash
# Check if process is running
ps aux | grep GIMP-MCP_mcp
netstat -tlnp | grep :8000  # For HTTP mode
```

**Enable debug logging:**
```bash
python -m GIMP-MCP_mcp --debug
```

**Check stderr vs stdout:**
```bash
# Logs go to stderr, not stdout
python -m GIMP-MCP_mcp 2>&1  # Redirect stderr to stdout
```

### Problem: Logs Too Verbose

**Reduce log level:**
```bash
LOG_LEVEL=WARNING python -m GIMP-MCP_mcp
```

**Filter specific modules:**
```python
# In your code
logger.disable("GIMP-MCP_mcp.utils.GIMP-MCP_executor")  # Disable executor logs
```

### Problem: Missing Log Context

**Check log format includes context:**
```python
# Ensure format includes file:function:line
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)
```

### Problem: Logs Not Colorized

**Check terminal supports colors:**
```bash
# Test color support
python -c "import sys; print('Colors supported' if sys.stderr.isatty() else 'No color support')"
```

**Force colorization:**
```python
logger.add(sys.stderr, colorize=True)  # Explicitly enable colors
```

### Problem: Logs Not Appearing in Claude Desktop

**Check MCP configuration:**
```json
{
  "mcpServers": {
    "GIMP-MCP-mcp": {
      "command": "python",
      "args": ["-m", "GIMP-MCP_mcp", "--debug"],
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**Check Claude Desktop version:**
- Ensure Claude Desktop supports MCP logging
- Check Claude Desktop console for MCP errors

## Best Practices

### When to Use Each Log Level

```python
# DEBUG: Internal state, function calls
logger.debug(f"Processing {len(items)} items")

# INFO: User-facing operations, major events
logger.info("Starting GIMP-MCP scene export")

# WARNING: Recoverable issues
logger.warning("GIMP-MCP not found in PATH, using configured executable")

# ERROR: Operation failures
logger.error(f"Failed to create material: {str(e)}")

# CRITICAL: System failures
logger.critical("GIMP-MCP executable not found, cannot continue")
```

### Structured Logging

```python
# Good: Structured information
logger.info(f"Created {count} objects in scene '{scene_name}'")

# Better: With context
logger.bind(scene=scene_name, object_count=count).info("Scene creation completed")

# Best: With timing
import time
start = time.time()
# ... operation ...
duration = time.time() - start
logger.info(f"Operation completed in {duration:.2f}s", extra={"duration": duration})
```

### Performance Considerations

```python
# Avoid expensive operations in log calls
# Bad
logger.debug(f"Processing data: {expensive_operation(data)}")

# Good
if logger.level("DEBUG").no <= logger._core.level:
    expensive_result = expensive_operation(data)
    logger.debug(f"Processing data: {expensive_result}")
```

## Common Log Messages

### Startup Logs
```
2024-01-15 14:30:25.123 | INFO     | GIMP-MCP_mcp.server:main:94 - [START] Starting GIMP-MCP MCP Server
2024-01-15 14:30:25.124 | INFO     | GIMP-MCP_mcp.server:main:95 - Python version: 3.10.0
2024-01-15 14:30:25.125 | INFO     | GIMP-MCP_mcp.server:main:96 - Running in stdio mode
```

### Operation Logs
```
2024-01-15 14:30:26.456 | INFO     | GIMP-MCP_mcp.handlers.mesh_handler:create_cube:44 - Successfully created cube 'MyCube'
2024-01-15 14:30:26.789 | INFO     | GIMP-MCP_mcp.handlers.lighting_handler:create_sun_light:39 - Creating sun light 'Sun' at (0, 0, 10) with energy 5.0
```

### Error Logs
```
2024-01-15 14:30:27.123 | ERROR    | GIMP-MCP_mcp.utils.GIMP-MCP_executor:execute_script:487 - GIMP-MCP process failed with return code 1: script_id_123
2024-01-15 14:30:27.456 | WARNING  | GIMP-MCP_mcp.utils.GIMP-MCP_executor:_process_script_output:563 - Script completed without success marker: script_id_123
```

## Advanced Configuration

### File Logging
```python
# Add file handler
logger.add(
    "GIMP-MCP_mcp.log",
    rotation="10 MB",      # Rotate when file reaches 10MB
    retention="1 week",    # Keep logs for 1 week
    level="DEBUG"
)
```

### JSON Logging
```python
# JSON format for log aggregation
logger.add(
    "logs.json",
    format="{time} | {level} | {name} | {function} | {line} | {message}",
    serialize=True,  # JSON format
    level="INFO"
)
```

### Custom Log Levels
```python
# Add custom level
logger.level("TRACE", 5)  # Below DEBUG

# Use custom level
logger.log("TRACE", "Very detailed trace information")
```

## Quick Reference

### Commands
```bash
# Normal operation
python -m GIMP-MCP_mcp

# Debug mode
python -m GIMP-MCP_mcp --debug

# HTTP server
python -m GIMP-MCP_mcp --http --port 8000 --debug

# Check logs
tail -f GIMP-MCP_mcp.log
```

### Environment Variables
```bash
LOG_LEVEL=DEBUG          # Set log level
LOG_FORMAT=json          # JSON output
LOG_FILE=app.log         # File output
```

### Loguru API
```python
from loguru import logger

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

This logging system provides comprehensive visibility into GIMP-MCP MCP operations, making debugging and monitoring much easier.
