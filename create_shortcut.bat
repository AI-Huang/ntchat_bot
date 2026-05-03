@echo off
setlocal

set SCRIPT_NAME=ntchat_bot
set TARGET_BAT=%~dp0launch.bat

if not exist "%TARGET_BAT%" (
    echo Error: launch.bat not found
    pause
    exit /b 1
)

set DESKTOP_DIR=%USERPROFILE%\Desktop
set SHORTCUT_PATH=%DESKTOP_DIR%\%SCRIPT_NAME%.lnk

set VBSCRIPT="%TEMP%\create_shortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > %VBSCRIPT%
echo sLinkFile = "%SHORTCUT_PATH%" >> %VBSCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %VBSCRIPT%
echo oLink.TargetPath = "%TARGET_BAT%" >> %VBSCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %VBSCRIPT%
echo oLink.Description = "Start ntchat_bot" >> %VBSCRIPT%
echo oLink.Save >> %VBSCRIPT%

cscript /nologo %VBSCRIPT%

del %VBSCRIPT%

echo Shortcut created: %SHORTCUT_PATH%
pause