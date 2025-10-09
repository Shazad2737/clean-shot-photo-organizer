@echo off
echo 🚀 Starting CLEAN SHOT Photo Organizer...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo 📦 Checking dependencies...
pip show PySide6 >nul 2>&1
if errorlevel 1 (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Run the application
echo 🎯 Launching application...
python run_app.py

if errorlevel 1 (
    echo.
    echo ❌ Application failed to start
    echo.
    echo 🔧 Troubleshooting:
    echo 1. Make sure you're in the project directory
    echo 2. Install dependencies: pip install -r requirements.txt
    echo 3. Check that all files are present
    pause
)
