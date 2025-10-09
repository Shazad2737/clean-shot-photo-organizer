#!/bin/bash

echo "🚀 Starting CLEAN SHOT Photo Organizer..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.11+ from https://python.org"
    exit 1
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import PySide6" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Run the application
echo "🎯 Launching application..."
python3 run_app.py

if [ $? -ne 0 ]; then
    echo
    echo "❌ Application failed to start"
    echo
    echo "🔧 Troubleshooting:"
    echo "1. Make sure you're in the project directory"
    echo "2. Install dependencies: pip3 install -r requirements.txt"
    echo "3. Check that all files are present"
fi
