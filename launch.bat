@echo off
setlocal

set VENV_DIR=%~dp0.venv
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
set MAIN_SCRIPT=%~dp0main.py
set DAEMON_SCRIPT=%~dp0daemon.py

if not exist "%PYTHON_EXE%" (
    echo Error: Virtual environment not found
    pause
    exit /b 1
)

if "%1"=="" (
    goto show_help
)

if /i "%1"=="run" (
    goto run_bot
) else if /i "%1"=="daemon" (
    goto run_daemon
) else if /i "%1"=="help" (
    goto show_help
) else (
    echo Error: Invalid argument: %1
    goto show_help
)

:run_bot
if not exist "%MAIN_SCRIPT%" (
    echo Error: main.py not found
    pause
    exit /b 1
)

echo Starting ntchat_bot...
"%PYTHON_EXE%" "%MAIN_SCRIPT%"
echo Bot exited
pause
goto end

:run_daemon
if not exist "%DAEMON_SCRIPT%" (
    echo Error: daemon.py not found
    pause
    exit /b 1
)

echo Starting ntchat_bot with daemon...
echo Press Ctrl+C to stop daemon
"%PYTHON_EXE%" "%DAEMON_SCRIPT%"
echo Daemon exited
pause
goto end

:show_help
echo Usage: launch.bat [run^|daemon^|help]
echo.
echo Arguments:
echo   run     - Run bot directly
echo   daemon  - Run bot with daemon monitoring
echo   help    - Show this help message
echo.
echo Examples:
echo   launch.bat run
echo   launch.bat daemon
pause
goto end

:end