@echo off
echo Starting CogniSentinel Mental Health Chatbot...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

:: Run the server script
echo Running server script...
python run_server.py

:: If the script exits, wait for user input before closing
pause