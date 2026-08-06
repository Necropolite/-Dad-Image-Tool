@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title D.A.D. - Dad Image Tool Installer

echo.
echo Installing D.A.D. - Dad's Automated Downloader...
echo The application and shortcut names remain Dad Image Tool.
echo This may take several minutes the first time.
echo.

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
    call :run_python -c "import sys"
    if errorlevel 1 goto :no_python
)

if exist ".venv" if not exist ".venv\Scripts\python.exe" (
    echo Removing an incomplete Python environment...
    rmdir /s /q ".venv"
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; assert sys.prefix != sys.base_prefix" >nul 2>nul
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

"%VENV_PY%" -m compileall -q app.py build_version_info.py history.py history_window.py main.py ui_layout.py update_ui.py updater.py version.py watcher.py watcher_processing.py watcher_support.py tests
if errorlevel 1 goto :failed
"%VENV_PY%" -m unittest discover -s tests -v
if errorlevel 1 goto :failed
"%VENV_PY%" build_version_info.py
if errorlevel 1 goto :failed

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "Dad Image Tool.spec" del /q "Dad Image Tool.spec"

"%VENV_PY%" -m PyInstaller --noconfirm --clean --onefile --windowed --name "Dad Image Tool" --version-file "version_info.txt" --collect-all pillow_heif main.py
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

taskkill /im "Dad Image Tool.exe" /f >nul 2>nul
timeout /t 2 /nobreak >nul
set "DAD_CURRENT_EXE=%CURRENT_EXE%"
set "DAD_NEW_EXE=%NEW_EXE%"
set "DAD_BACKUP_EXE=%BACKUP_EXE%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$current=$env:DAD_CURRENT_EXE; $new=$env:DAD_NEW_EXE; $backup=$env:DAD_BACKUP_EXE; if (Test-Path $backup) { Remove-Item $backup -Force }; if (Test-Path $current) { [IO.File]::Replace($new,$current,$backup,$true) } else { Move-Item $new $current -Force }"
if errorlevel 1 goto :failed

set "DAD_INSTALL_DIR=%INSTALL_DIR%"
set "DAD_INCOMING=%INCOMING%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell; $desktop=[Environment]::GetFolderPath('Desktop'); $startup=[Environment]::GetFolderPath('Startup'); $app=Join-Path $env:DAD_INSTALL_DIR 'Dad Image Tool.exe'; $s=$w.CreateShortcut((Join-Path $desktop 'Dad Image Tool.lnk')); $s.TargetPath=$app; $s.WorkingDirectory=$env:DAD_INSTALL_DIR; $s.Description=\"D.A.D. - Dad's Automated Downloader\"; $s.Save(); $d=$w.CreateShortcut((Join-Path $desktop 'Drop Client Pictures Here.lnk')); $d.TargetPath=$env:DAD_INCOMING; $d.Description='Download, Archive, and Deliver client pictures'; $d.Save(); $a=$w.CreateShortcut((Join-Path $startup 'Dad Image Tool.lnk')); $a.TargetPath=$app; $a.WorkingDirectory=$env:DAD_INSTALL_DIR; $a.Description=\"D.A.D. - Dad's Automated Downloader\"; $a.Save()"
if errorlevel 1 goto :failed

start "" "%INSTALL_DIR%\Dad Image Tool.exe"

echo.
echo D.A.D. is installed.
echo Dad Image Tool is ready to use.
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
py -3.12 -c "import sys" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_EXE=py"
    set "PYTHON_ARGS=-3.12"
    exit /b 0
)
py -3 -c "import sys" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_EXE=py"
    set "PYTHON_ARGS=-3"
    exit /b 0
)
python -c "import sys" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    set "PYTHON_ARGS="
)
exit /b 0

:run_python
"%PYTHON_EXE%" %PYTHON_ARGS% %*
exit /b %errorlevel%

:no_python
echo.
echo The required component could not be installed automatically.
echo Install Python 3.12 from python.org, then run Install.bat again.
pause
exit /b 1

:failed
if defined NEW_EXE if exist "%NEW_EXE%" del /q "%NEW_EXE%" >nul 2>nul
if defined CURRENT_EXE if exist "%CURRENT_EXE%" start "" "%CURRENT_EXE%"
echo.
echo Installation did not finish.
echo Copy the error shown above and send it to Clint.
pause
exit /b 1
