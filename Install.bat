@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Dad Image Tool Installer

echo.
echo Installing Dad Image Tool...
echo This may take several minutes the first time.
echo.

set "PYTHON_CMD="
py -3 -c "import sys" >nul 2>nul && set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD python -c "import sys" >nul 2>nul && set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
    echo Python is needed to build the app.
    echo Trying to install Python automatically...
    where winget >nul 2>nul
    if errorlevel 1 goto :no_python
    winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
    if errorlevel 1 goto :no_python
    set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python312\python.exe"
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys" >nul 2>nul
    if errorlevel 1 (
        echo Repairing an old Python environment...
        rmdir /s /q .venv
    )
)

if not exist ".venv\Scripts\python.exe" (
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :failed
)

set "VENV_PY=.venv\Scripts\python.exe"
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 goto :failed
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 goto :failed

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Dad Image Tool.spec" del /q "Dad Image Tool.spec"

"%VENV_PY%" -m PyInstaller --noconfirm --clean --onefile --windowed --name "Dad Image Tool" --collect-all tkinterdnd2 --collect-all pillow_heif --collect-all bs4 main.py
if errorlevel 1 goto :failed

set "INSTALL_DIR=%LocalAppData%\Dad Image Tool"
set "DATA_DIR=%UserProfile%\Pictures\Dad Image Tool"
set "INCOMING=%DATA_DIR%\Drop Client Pictures Here"
set "FINISHED=%DATA_DIR%\Finished"
set "ARCHIVE=%DATA_DIR%\Originals Archive"
set "ATTENTION=%DATA_DIR%\Needs Attention"
set "STARTUP=%AppData%\Microsoft\Windows\Start Menu\Programs\Startup"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INCOMING%" mkdir "%INCOMING%"
if not exist "%FINISHED%" mkdir "%FINISHED%"
if not exist "%ARCHIVE%" mkdir "%ARCHIVE%"
if not exist "%ATTENTION%" mkdir "%ATTENTION%"

copy /y "dist\Dad Image Tool.exe" "%INSTALL_DIR%\Dad Image Tool.exe" >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut([Environment]::GetFolderPath('Desktop')+'\Dad Image Tool.lnk'); $s.TargetPath='%INSTALL_DIR%\Dad Image Tool.exe'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.Save(); $d=$w.CreateShortcut([Environment]::GetFolderPath('Desktop')+'\Drop Client Pictures Here.lnk'); $d.TargetPath='%INCOMING%'; $d.Save(); $a=$w.CreateShortcut('%STARTUP%\Dad Image Tool.lnk'); $a.TargetPath='%INSTALL_DIR%\Dad Image Tool.exe'; $a.WorkingDirectory='%INSTALL_DIR%'; $a.Save()"
if errorlevel 1 goto :failed

start "" "%INSTALL_DIR%\Dad Image Tool.exe"

echo.
echo Dad Image Tool is installed.
echo.
echo Use the desktop shortcut named:
echo Drop Client Pictures Here
echo.
echo Save client pictures, folders, and ZIP files there.
echo Dad Image Tool will process them automatically.
echo.
pause
exit /b 0

:no_python
echo.
echo Python could not be installed automatically.
echo Install Python 3.12 from python.org, then run Install.bat again.
pause
exit /b 1

:failed
echo.
echo Installation did not finish.
echo Copy the error shown above and send it to Clint.
pause
exit /b 1
