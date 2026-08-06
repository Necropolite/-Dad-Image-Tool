@echo off
setlocal
cd /d "%~dp0"
title Dad Image Tool Tests

echo.
echo Testing Dad Image Tool...
echo.

set "PYTHON="
py -3.12 -c "import sys" >nul 2>nul && set "PYTHON=py -3.12"
if not defined PYTHON py -3 -c "import sys" >nul 2>nul && set "PYTHON=py -3"
if not defined PYTHON python -c "import sys" >nul 2>nul && set "PYTHON=python"

if not defined PYTHON (
    echo Python could not be found.
    echo Run Install.bat first, then try again.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating the test environment...
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :failed
)

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :failed

".venv\Scripts\python.exe" -m unittest discover -s tests -v
if errorlevel 1 goto :failed

echo.
echo All automated tests passed.
echo.
pause
exit /b 0

:failed
echo.
echo One or more tests failed.
echo Copy the failure shown above before closing this window.
echo.
pause
exit /b 1
