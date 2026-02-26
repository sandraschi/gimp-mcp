$ErrorActionPreference = "Stop"

# Configuration
$VENV_PATH = "$PSScriptRoot\backend\venv"
$PYTHON = "$VENV_PATH\Scripts\python.exe"
# Backend Source: backend/src/gimp_mcp
$env:PYTHONPATH = "$PSScriptRoot\backend\src"
$MODULE = "gimp_mcp.main"
$PORT = 10773
$BIND_HOST = "127.0.0.1"

# Check venv
if (-not (Test-Path $VENV_PATH)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv $VENV_PATH
    & "$VENV_PATH\Scripts\pip.exe" install -e "$PSScriptRoot\backend"
}

# Kill existing process on port
$existing = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Killing process on port $PORT..." -ForegroundColor Yellow
    Stop-Process -Id $existing.OwningProcess -Force -ErrorAction SilentlyContinue
}

# Start Backend
Write-Host "Starting Backend on port $PORT..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$PYTHON' -m $MODULE --http --port $PORT --host $BIND_HOST"

# Start Frontend
Write-Host "Starting Frontend on port 10772..." -ForegroundColor Green
$FrontendDir = "$PSScriptRoot\frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendDir'; npm run dev"

# Launch Browser
Start-Sleep -Seconds 3
Start-Process "http://localhost:10772"
