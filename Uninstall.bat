@echo off
setlocal
title Dad Image Tool Uninstaller

echo Removing Dad Image Tool...
reg delete "HKCU\Software\Classes\dadimage" /f >nul 2>nul
if exist "%UserProfile%\Desktop\Dad Image Tool.lnk" del /q "%UserProfile%\Desktop\Dad Image Tool.lnk"
if exist "%LocalAppData%\Dad Image Tool" rmdir /s /q "%LocalAppData%\Dad Image Tool"

echo.
echo Dad Image Tool was removed.
echo The browser extension can be removed from the browser's Extensions page.
pause
