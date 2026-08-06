@echo off
setlocal EnableExtensions
cd /d "%~dp0\..\.."
title Dad Image Tool Tests
set "PYTHONPATH=%CD%\internal\src"

echo.
echo Testing Dad Image Tool...
echo.

py -3.12 -m pip install --disable-pip-version-check -r internal\requirements.txt
if errorlevel 1 goto :failed
py -3.12 -m compileall -q internal\src tests
if errorlevel 1 goto :failed
py -3.12 -m unittest discover -s tests -v
if errorlevel 1 goto :failed

echo.
echo All automated tests passed.
echo.
pause
exit /b 0

:failed
echo.
echo One or more tests failed.
echo.
pause
exit /b 1
