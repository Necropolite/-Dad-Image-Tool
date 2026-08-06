@echo off
setlocal EnableExtensions
title Dad Image Tool Uninstaller

echo Removing Dad Image Tool...

taskkill /im "Dad Image Tool.exe" /f >nul 2>nul
set "DAD_INSTALL_DIR=%LocalAppData%\Dad Image Tool"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$desktop=[Environment]::GetFolderPath('Desktop'); $startup=[Environment]::GetFolderPath('Startup'); Remove-Item (Join-Path $desktop 'Dad Image Tool.lnk') -Force -ErrorAction SilentlyContinue; Remove-Item (Join-Path $desktop 'Drop Client Pictures Here.lnk') -Force -ErrorAction SilentlyContinue; Remove-Item (Join-Path $startup 'Dad Image Tool.lnk') -Force -ErrorAction SilentlyContinue"

if exist "%DAD_INSTALL_DIR%" rmdir /s /q "%DAD_INSTALL_DIR%"

echo.
echo Dad Image Tool was removed.
echo.
echo Client pictures under Pictures\Dad Image Tool were not deleted.
echo Delete that folder manually only after confirming it is no longer needed.
pause
