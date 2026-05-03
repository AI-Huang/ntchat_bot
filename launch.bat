@echo off
setlocal

set VENV_DIR=%~dp0.venv
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
set MAIN_SCRIPT=%~dp0main.py

if not exist "%PYTHON_EXE%" (
    echo Error: Virtual environment not found
    pause
    exit /b 1
)

if not exist "%MAIN_SCRIPT%" (
    echo Error: main.py not found
    pause
    exit /b 1
)

echo Starting ntchat_bot...
"%PYTHON_EXE%" "%MAIN_SCRIPT%"

echo Bot exited
pause