
# Fast port helpers (scripts/PortHelpers.ps1)
$__RepoRootForPorts = Split-Path -Parent $PSScriptRoot
$__PortHelpers = Join-Path $__RepoRootForPorts 'scripts\PortHelpers.ps1'
if (Test-Path -LiteralPath $__PortHelpers) { . $__PortHelpers }
Param([switch]$Headless) $SkipFrontend = $Headless  # --- SOTA Headless Standard --- if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {     Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden     exit } $WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' } # ------------------------------  # Webapp Start - Standardized SOTA (v4.0.1) $WebPort = 10772 $BackendPort = 10773 $BridgePort = 10824 $ProjectRoot = Split-Path -Parent $PSScriptRoot  # 1. Aggressive port clearing with fallback Write-Host "=== gimp-mcp Webapp Startup ===" -ForegroundColor Cyan Write-Host "Clearing ports $WebPort, $BackendPort, $BridgePort..." -ForegroundColor Yellow  function Clear-Port {     param([int]$Port)     $procIds = Get-PortListenerPidsFast -Port $port
