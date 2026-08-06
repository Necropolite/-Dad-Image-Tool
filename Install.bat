@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Dad Image Tool Installer

echo.
echo Installing Dad Image Tool...
echo This may take several minutes the first time.
echo.

set "REPLACED=0"
set "DAD_IMAGE_TOOL_STARTUP_MARKER="
call :find_python
if not defined PYTHON_EXE (
    echo A required Windows component is missing.
    echo Trying to install it automatically...
    where winget >nul 2>nul
    if errorlevel 1 goto :no_python
    winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
    if errorlevel 1 goto :no_python
    set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python312\python.exe"
    set "PYTHON_ARGS="
    if not exist "%PYTHON_EXE%" goto :no_python
    call :run_python -c "import sys; raise SystemExit(0 if (3, 12) <= sys.version_info[:2] < (3, 14) else 1)"
    if errorlevel 1 goto :no_python
)

if exist ".venv" if not exist ".venv\Scripts\python.exe" (
    echo Removing an incomplete Python environment...
    rmdir /s /q ".venv"
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; assert sys.prefix != sys.base_prefix; raise SystemExit(0 if (3, 12) <= sys.version_info[:2] < (3, 14) else 1)" >nul 2>nul
    if errorlevel 1 (
        echo Repairing an old Python environment...
        rmdir /s /q ".venv"
    )
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m pip --version >nul 2>nul
    if errorlevel 1 (
        echo Repairing an incomplete Python environment...
        rmdir /s /q ".venv"
    )
)

if not exist ".venv\Scripts\python.exe" (
    call :run_python -m venv ".venv"
    if errorlevel 1 goto :failed
)

set "VENV_PY=.venv\Scripts\python.exe"
"%VENV_PY%" -m pip install --disable-pip-version-check --upgrade pip
if errorlevel 1 goto :failed
"%VENV_PY%" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :failed

"%VENV_PY%" -m compileall -q app.py history.py history_window.py main.py ui_layout.py update_ui.py updater.py version.py watcher.py watcher_processing.py watcher_support.py tests
if errorlevel 1 goto :failed
"%VENV_PY%" -m unittest discover -s tests -v
if errorlevel 1 goto :failed

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "Dad Image Tool.spec" del /q "Dad Image Tool.spec"

"%VENV_PY%" -m PyInstaller --noconfirm --clean --onefile --windowed --name "Dad Image Tool" --collect-all pillow_heif main.py
if errorlevel 1 goto :failed
if not exist "dist\Dad Image Tool.exe" goto :failed

set "INSTALL_DIR=%LocalAppData%\Dad Image Tool"
set "PICTURES_DIR="
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('MyPictures')"`) do set "PICTURES_DIR=%%I"
if not defined PICTURES_DIR set "PICTURES_DIR=%UserProfile%\Pictures"
set "DATA_DIR=%PICTURES_DIR%\Dad Image Tool"
set "INCOMING=%DATA_DIR%\Drop Client Pictures Here"
set "FINISHED=%DATA_DIR%\Finished"
set "ARCHIVE=%DATA_DIR%\Originals Archive"
set "ATTENTION=%DATA_DIR%\Needs Attention"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INCOMING%" mkdir "%INCOMING%"
if not exist "%FINISHED%" mkdir "%FINISHED%"
if not exist "%ARCHIVE%" mkdir "%ARCHIVE%"
if not exist "%ATTENTION%" mkdir "%ATTENTION%"

rem Stage the new executable before replacing an older installed copy.
set "CURRENT_EXE=%INSTALL_DIR%\Dad Image Tool.exe"
set "NEW_EXE=%INSTALL_DIR%\Dad Image Tool.exe.new"
set "BACKUP_EXE=%INSTALL_DIR%\Dad Image Tool.exe.backup"
if exist "%NEW_EXE%" del /q "%NEW_EXE%"
copy /y "dist\Dad Image Tool.exe" "%NEW_EXE%" >nul
if errorlevel 1 goto :failed

call :close_running_app
if errorlevel 1 goto :app_busy

set "DAD_CURRENT_EXE=%CURRENT_EXE%"
set "DAD_NEW_EXE=%NEW_EXE%"
set "DAD_BACKUP_EXE=%BACKUP_EXE%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $current=$env:DAD_CURRENT_EXE; $new=$env:DAD_NEW_EXE; $backup=$env:DAD_BACKUP_EXE; if (Test-Path $backup) { Remove-Item $backup -Force }; if (Test-Path $current) { [IO.File]::Replace($new,$current,$backup,$true) } else { Move-Item $new $current -Force }"
if errorlevel 1 goto :failed
set "REPLACED=1"

set "DAD_INSTALL_DIR=%INSTALL_DIR%"
set "DAD_INCOMING=%INCOMING%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $w=New-Object -ComObject WScript.Shell; $desktop=[Environment]::GetFolderPath('Desktop'); $startup=[Environment]::GetFolderPath('Startup'); $app=Join-Path $env:DAD_INSTALL_DIR 'Dad Image Tool.exe'; $s=$w.CreateShortcut((Join-Path $desktop 'Dad Image Tool.lnk')); $s.TargetPath=$app; $s.WorkingDirectory=$env:DAD_INSTALL_DIR; $s.Save(); $d=$w.CreateShortcut((Join-Path $desktop 'Drop Client Pictures Here.lnk')); $d.TargetPath=$env:DAD_INCOMING; $d.Save(); $a=$w.CreateShortcut((Join-Path $startup 'Dad Image Tool.lnk')); $a.TargetPath=$app; $a.WorkingDirectory=$env:DAD_INSTALL_DIR; $a.Save()"
if errorlevel 1 goto :failed

set "START_MARKER=%TEMP%\DadImageTool-Install-%RANDOM%-%RANDOM%.ok"
del /q "%START_MARKER%" >nul 2>nul
set "DAD_IMAGE_TOOL_STARTUP_MARKER=%START_MARKER%"
start "" "%CURRENT_EXE%"
if errorlevel 1 goto :failed
for /l %%I in (1,1,45) do (
    if exist "%START_MARKER%" goto :startup_ok
    timeout /t 1 /nobreak >nul
)
goto :failed

:startup_ok
set "DAD_IMAGE_TOOL_STARTUP_MARKER="
del /q "%START_MARKER%" >nul 2>nul
if exist "%BACKUP_EXE%" del /q "%BACKUP_EXE%" >nul 2>nul

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

:find_python
set "PYTHON_EXE="
set "PYTHON_ARGS="
py -3.12 -c "import sys; raise SystemExit(0 if (3, 12) <= sys.version_info[:2] < (3, 14) else 1)" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_EXE=py"
    set "PYTHON_ARGS=-3.12"
    exit /b 0
)
py -3 -c "import sys; raise SystemExit(0 if (3, 12) <= sys.version_info[:2] < (3, 14) else 1)" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_EXE=py"
    set "PYTHON_ARGS=-3"
    exit /b 0
)
python -c "import sys; raise SystemExit(0 if (3, 12) <= sys.version_info[:2] < (3, 14) else 1)" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    set "PYTHON_ARGS="
)
exit /b 0

:run_python
"%PYTHON_EXE%" %PYTHON_ARGS% %*
exit /b %errorlevel%

:close_running_app
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=@(Get-Process -Name 'Dad Image Tool' -ErrorAction SilentlyContinue); if (-not $p) { exit 0 }; $p | ForEach-Object { $_.CloseMainWindow() | Out-Null }; $deadline=(Get-Date).AddMinutes(10); do { Start-Sleep -Seconds 1; $p=@(Get-Process -Name 'Dad Image Tool' -ErrorAction SilentlyContinue) } while ($p -and (Get-Date) -lt $deadline); if ($p) { exit 1 }"
exit /b %errorlevel%

:no_python
echo.
echo The required component could not be installed automatically.
echo Install Python 3.12 from python.org, then run Install.bat again.
pause
exit /b 1

:app_busy
echo.
echo Dad Image Tool is still processing pictures and was not stopped.
echo Let it finish, close it, and run Install.bat again.
pause
exit /b 1

:failed
set "DAD_IMAGE_TOOL_STARTUP_MARKER="
if defined START_MARKER del /q "%START_MARKER%" >nul 2>nul
if "%REPLACED%"=="1" (
    taskkill /im "Dad Image Tool.exe" /f >nul 2>nul
    if exist "%BACKUP_EXE%" (
        if exist "%CURRENT_EXE%" del /q "%CURRENT_EXE%" >nul 2>nul
        move /y "%BACKUP_EXE%" "%CURRENT_EXE%" >nul 2>nul
        start "" "%CURRENT_EXE%"
    ) else (
        if exist "%CURRENT_EXE%" del /q "%CURRENT_EXE%" >nul 2>nul
    )
) else (
    if defined CURRENT_EXE if exist "%CURRENT_EXE%" start "" "%CURRENT_EXE%"
)
if defined NEW_EXE if exist "%NEW_EXE%" del /q "%NEW_EXE%" >nul 2>nul
echo.
echo Installation did not finish. The previous installed version was kept when possible.
echo Copy the error shown above and send it to Clint.
pause
exit /b 1
