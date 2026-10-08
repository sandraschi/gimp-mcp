@echo off
setlocal
REM gimp-mcp launcher - delegates to start.ps1 (fleet standard)
cd /d "%~dp0"
if not exist "start.ps1" (
  echo [ERROR] start.ps1 not found in %CD%
  exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%CD%\start.ps1" %*
if errorlevel 1 (
  echo.
  echo [gimp-mcp start.bat] exited with error
  exit /b 1
)
endlocal
exit /b 0
