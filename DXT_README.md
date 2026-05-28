# GIMP MCP DXT Package

This directory contains the DXT (Developer Extension) package for the GIMP MCP Server, which enables AI agents to perform professional image editing operations using GIMP.

## Prerequisites

- Node.js 14+ (for DXT CLI)
- Python 3.8+
- GIMP 2.10+ installed on the system

## Building the DXT Package

1. Install the DXT CLI globally:
   ```bash
   npm install -g @anthropic-ai/dxt
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Build the DXT package:
   ```bash
   python build_dxt.py
   ```

The built package will be available in the `dist` directory as `gimp-mcp-<version>.dxt`.

## Installation

1. In your AI development environment (Windsurf, Cursor, etc.), navigate to the Extensions/Plugins section.
2. Choose "Install from File" and select the `.dxt` package.
3. Configure the extension by providing the path to your GIMP executable and other settings.

## Configuration

The following settings can be configured during installation:

- **GIMP Executable**: Path to the GIMP executable (e.g., `C:\Program Files\GIMP 3\bin\gimp-3.0.exe` on Windows)
- **Temporary Directory**: Directory for temporary files (defaults to system temp)
- **Max Concurrent Processes**: Number of concurrent GIMP processes (1-10, default: 3)
- **Process Timeout**: Timeout for GIMP operations in seconds (5-300, default: 30)
- **Allowed Directories**: List of directories that GIMP MCP can access

## Development

### Directory Structure

- `dxt/`: DXT package contents
  - `assets/`: Icons and other static files
  - `manifest.json`: Extension manifest (auto-generated)
- `src/`: Python source code
- `dist/`: Output directory for built packages
- `build_dxt.py`: Build script
- `manifest.json`: Source manifest (copied to dxt/ during build)

### Testing

To test the DXT package locally:

1. Build the package using `python build_dxt.py`
2. In your AI development environment, install the package from the `dist` directory
3. Configure the extension with your GIMP path
4. Test the available tools and functionality

## License

MIT License - See [LICENSE](../LICENSE) for details.

## Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/sandraschi/gimp-mcp/issues) page.
