@echo off
setlocal
title Dad Image Tool Uninstaller

echo Removing Dad Image Tool...

taskkill /im "Dad Image Tool.exe" /f >nul 2>nul

if exist "%UserProfile%\Desktop\Dad Image Tool.lnk" del /q "%UserProfile%\Desktop\Dad Image Tool.lnk"
if exist "%UserProfile%\Desktop\Drop Client Pictures Here.lnk" del /q "%UserProfile%\Desktop\Drop Client Pictures Here.lnk"
if exist "%AppData%\Microsoft\Windows\Start Menu\Programs\Startup\Dad Image Tool.lnk" del /q "%AppData%\Microsoft\Windows\Start Menu\Programs\Startup\Dad Image Tool.lnk"
if exist "%LocalAppData%\Dad Image Tool" rmdir /s /q "%LocalAppData%\Dad Image Tool"

echo.
echo Dad Image Tool was removed.
echo.
echo Client pictures under Pictures\Dad Image Tool were not deleted.
echo Delete that folder manually only after confirming it is no longer needed.
pause
