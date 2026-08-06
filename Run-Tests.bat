@echo off
chcp 65001 >nul 2>nul
setlocal EnableExtensions
cd /d "%~dp0"
title D.A.D. - Dad Image Tool Tests

echo.
echo D.A.D. - Dad's Automated Downloader
echo Download • Archive • Deliver
echo.
echo Testing Dad Image Tool...
echo.

call :find_python
if not defined PYTHON_EXE (
    echo Python could not be found.
    echo Run Install.bat first, then try again.
    pause
    exit /b 1
)

if exist ".venv" if not exist ".venv\Scripts\python.exe" rmdir /s /q ".venv"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; assert sys.prefix != sys.base_prefix; raise SystemExit(0 if (3, 12) <= sys.version_info[:2] < (3, 14) else 1)" >nul 2>nul
    if errorlevel 1 rmdir /s /q ".venv"
)
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m pip --version >nul 2>nul
    if errorlevel 1 rmdir /s /q ".venv"
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating the test environment...
    call :run_python -m venv ".venv"
    if errorlevel 1 goto :failed
)

".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements-dev.txt
if errorlevel 1 goto :failed

".venv\Scripts\python.exe" -m compileall -q app.py history.py history_window.py main.py ui_layout.py update_ui.py updater.py version.py watcher.py watcher_processing.py watcher_support.py tests tools
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m ruff check .
if errorlevel 1 goto :failed

".venv\Scripts\python.exe" -m coverage erase
".venv\Scripts\python.exe" -m coverage run -m unittest discover -s tests -v
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m coverage report -m
if errorlevel 1 goto :failed

".venv\Scripts\python.exe" tools\generate_version_info.py "generated\Dad-Image-Tool-Version.txt"
if errorlevel 1 goto :failed

echo.
echo All D.A.D. automated checks passed.
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
if not errorlevel 1 set "PYTHON_EXE=python"
exit /b 0

:run_python
"%PYTHON_EXE%" %PYTHON_ARGS% %*
exit /b %errorlevel%

:failed
echo.
echo One or more D.A.D. checks failed.
echo Copy the failure shown above before closing this window.
echo.
pause
exit /b 1
