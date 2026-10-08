# Fleet shim for the canonical MCPB pack (mcp-central-docs/scripts/fleet-mcpb-pack.ps1).
# Never vendor pack logic here - this file only forwards -RepoRoot so fleet fixes land at once.
param([string]$RepoRoot = (Split-Path -Parent $PSScriptRoot))
$FleetDocs = if ($env:MCP_CENTRAL_DOCS) { $env:MCP_CENTRAL_DOCS } else { 'D:\Dev\repos\mcp-central-docs' }
& (Join-Path $FleetDocs 'scripts\fleet-mcpb-pack.ps1') -RepoRoot $RepoRoot
