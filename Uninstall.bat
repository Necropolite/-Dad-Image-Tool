@echo off
setlocal EnableExtensions
title Dad Image Tool Uninstaller

echo Removing Dad Image Tool...

powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=@(Get-Process -Name 'Dad Image Tool' -ErrorAction SilentlyContinue); if ($p) { $p | ForEach-Object { $_.CloseMainWindow() | Out-Null }; $deadline=(Get-Date).AddMinutes(10); do { Start-Sleep -Seconds 1; $p=@(Get-Process -Name 'Dad Image Tool' -ErrorAction SilentlyContinue) } while ($p -and (Get-Date) -lt $deadline); if ($p) { exit 1 } }"
if errorlevel 1 goto :still_running

set "DAD_INSTALL_DIR=%LocalAppData%\Dad Image Tool"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$desktop=[Environment]::GetFolderPath('Desktop'); $startup=[Environment]::GetFolderPath('Startup'); Remove-Item (Join-Path $desktop 'Dad Image Tool.lnk') -Force -ErrorAction SilentlyContinue; Remove-Item (Join-Path $desktop 'Drop Client Pictures Here.lnk') -Force -ErrorAction SilentlyContinue; Remove-Item (Join-Path $startup 'Dad Image Tool.lnk') -Force -ErrorAction SilentlyContinue"

if exist "%DAD_INSTALL_DIR%" rmdir /s /q "%DAD_INSTALL_DIR%"

echo.
echo Dad Image Tool was removed.
echo.
echo Client pictures in your Windows Pictures folder were not deleted.
echo Delete the Dad Image Tool data folder manually only after confirming it is no longer needed.
pause
exit /b 0

:still_running
echo.
echo Dad Image Tool is still processing pictures and was not stopped.
echo Let it finish, close it, and run Uninstall.bat again.
pause
exit /b 1
