@echo off
setlocal
cd /d "%~dp0"
title Dad Image Tool Installer

echo.
echo Installing Dad Image Tool...
echo This may take several minutes the first time.
echo.

where py >nul 2>nul
if errorlevel 1 (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Python is needed to build the app.
        echo Trying to install it automatically with Windows Package Manager...
        where winget >nul 2>nul
        if errorlevel 1 (
            echo.
            echo Automatic installation is not available on this computer.
            echo Install Python 3 from python.org, then run Install.bat again.
            pause
            exit /b 1
        )
        winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
        if errorlevel 1 (
            echo Python could not be installed automatically.
            pause
            exit /b 1
        )
        set "PATH=%LocalAppData%\Programs\Python\Python312;%LocalAppData%\Programs\Python\Python312\Scripts;%PATH%"
    )
)

set "PYTHON=python"
where py >nul 2>nul && set "PYTHON=py -3"

if not exist ".venv\Scripts\python.exe" (
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :failed
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto :failed
pip install -r requirements.txt
if errorlevel 1 goto :failed

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Dad Image Tool.spec" del /q "Dad Image Tool.spec"

pyinstaller --noconfirm --clean --onefile --windowed --name "Dad Image Tool" --collect-all tkinterdnd2 --collect-all pillow_heif app.py
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
echo One browser step remains. The instructions will open now.
start "" "https://github.com/Necropolite/-Dad-Image-Tool#add-the-right-click-option"
pause
exit /b 0

:failed
echo.
echo Installation did not finish. Copy the error shown above and send it to Clint.
pause
exit /b 1
