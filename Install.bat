@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Dad Image Tool Installer

echo.
echo Installing Dad Image Tool...
echo This may take several minutes the first time.
echo.

set "PYTHON_CMD="

rem Prefer a working Python launcher, but do not trust that py.exe points to an installed version.
py -3 -c "import sys" >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3"

rem Fall back to a working python.exe on PATH.
if not defined PYTHON_CMD (
    python -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)

rem Try common per-user Python 3.12 and 3.13 locations.
if not defined PYTHON_CMD if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python312\python.exe"
if not defined PYTHON_CMD if exist "%LocalAppData%\Programs\Python\Python313\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python313\python.exe"

rem Install Python when no working interpreter can be found.
if not defined PYTHON_CMD (
    echo Python is needed to install the app.
    echo Trying to install it automatically...
    where winget >nul 2>nul
    if errorlevel 1 (
        echo.
        echo Automatic installation is not available on this computer.
        echo Install Python 3.12 from python.org, then run Install.bat again.
        pause
        exit /b 1
    )

    winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo Python could not be installed automatically.
        pause
        exit /b 1
    )

    if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
        set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python312\python.exe"
    ) else (
        echo Python was installed, but its program file could not be found.
        echo Restart the computer, then run Install.bat again.
        pause
        exit /b 1
    )
)

echo Using Python: %PYTHON_CMD%

rem A copied or previously created virtual environment may point to a Python version
rem that no longer exists. Test it and rebuild it automatically when necessary.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys" >nul 2>nul
    if errorlevel 1 (
        echo Repairing an old Python environment...
        rmdir /s /q ".venv"
    )
) else if exist ".venv" (
    echo Repairing an incomplete Python environment...
    rmdir /s /q ".venv"
)

if not exist ".venv\Scripts\python.exe" (
    %PYTHON_CMD% -m venv ".venv"
    if errorlevel 1 goto :failed
)

set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"
set "VENV_PIP=%CD%\.venv\Scripts\pip.exe"

"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto :failed
"%VENV_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 goto :failed

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Dad Image Tool.spec" del /q "Dad Image Tool.spec"

"%VENV_PYTHON%" -m PyInstaller --noconfirm --clean --onefile --windowed --name "Dad Image Tool" --collect-all tkinterdnd2 --collect-all pillow_heif --collect-all bs4 main.py
if errorlevel 1 goto :failed

set "INSTALL_DIR=%LocalAppData%\Dad Image Tool"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
copy /y "dist\Dad Image Tool.exe" "%INSTALL_DIR%\Dad Image Tool.exe" >nul
xcopy /e /i /y "extension" "%INSTALL_DIR%\extension" >nul

reg add "HKCU\Software\Classes\dadimage" /ve /d "URL:Dad Image Tool" /f >nul
reg add "HKCU\Software\Classes\dadimage" /v "URL Protocol" /d "" /f >nul
reg add "HKCU\Software\Classes\dadimage\DefaultIcon" /ve /d "\"%INSTALL_DIR%\Dad Image Tool.exe\",0" /f >nul
reg add "HKCU\Software\Classes\dadimage\shell\open\command" /ve /d "\"%INSTALL_DIR%\Dad Image Tool.exe\" \"%%1\"" /f >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\Dad Image Tool.lnk');$s.TargetPath='%INSTALL_DIR%\Dad Image Tool.exe';$s.WorkingDirectory='%INSTALL_DIR%';$s.Save()"

start "" "%INSTALL_DIR%\Dad Image Tool.exe"

echo.
echo Dad Image Tool is installed.
echo A shortcut was added to the desktop.
echo.
pause
exit /b 0

:failed
echo.
echo Installation did not finish. Copy the error shown above and send it to Clint.
pause
exit /b 1
