@echo off
setlocal

REM Define name and folders
set "APPNAME=RailGunner"
set "ENV_DIR=.venv"
set "SCRIPT=timer.py"
set "ICON=%~dp0RailGunner.ico"

REM Create venv
python -m venv %ENV_DIR%

REM Activate and install
call %ENV_DIR%\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo Creating shortcut on Desktop...

REM Create shortcut with PowerShell
set "SHORTCUT=%USERPROFILE%\Desktop\%APPNAME%.lnk"
powershell.exe -NoProfile -Command "$WScriptShell = New-Object -ComObject WScript.Shell; $Shortcut = $WScriptShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%CD%\%ENV_DIR%\Scripts\pythonw.exe'; $Shortcut.Arguments = '"%CD%\%SCRIPT%"'; $Shortcut.WorkingDirectory = '%CD%'; if (Test-Path '%ICON%') { $Shortcut.IconLocation = '%ICON%' }; $Shortcut.Save()"

echo Done!
exit /b
