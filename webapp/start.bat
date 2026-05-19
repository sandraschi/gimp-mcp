@echo off
cd /d "%~dp0..\..\gimp-mcp"
powershell -ExecutionPolicy Bypass -File "%~dp0..\..\gimp-mcp\start.ps1"
pause