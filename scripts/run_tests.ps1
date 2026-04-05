# GIMP MCP Test Runner (SOTA Standard)
# Clears environment, sets up PYTHONPATH, and runs pytest with coverage

$RepoRoot = Resolve-Path ".."
$Env:PYTHONPATH = "$RepoRoot\src"

Write-Host "--- GIMP MCP Testing Scaffold ---" -ForegroundColor Cyan
Write-Host "Root: $RepoRoot"
Write-Host "Running pytest..."

# Ensure pytest and coverage are installed
py -3 -m pip install pytest pytest-asyncio pytest-cov httpx -q

# Run tests
py -3 -m pytest `
    --cov=gimp_mcp `
    --cov-report=term-missing `
    --cov-report=html:tests/coverage_report `
    tests/

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] All tests passed!" -ForegroundColor Green
} else {
    Write-Host "`n[FAILURE] Tests failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}
