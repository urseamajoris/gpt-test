#!/bin/bash
# Build script for Unix/Linux/Mac systems

echo "Agentic Model Framework - Build Script"
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not found."
    exit 1
fi

echo "Installing dependencies..."
pip3 install --user -r requirements.txt

# Install PyInstaller if not present
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip3 install --user pyinstaller
fi

echo "Building executable..."

# Clean previous builds
rm -rf build dist __pycache__ *.pyc

# Build the application
if pyinstaller agentic_gui.spec; then
    echo ""
    echo "Build completed successfully!"
    echo "Executable location: dist/AgenticFrameworkGUI/"
    echo ""
    echo "To run the application:"
    echo "  cd dist/AgenticFrameworkGUI"
    echo "  ./AgenticFrameworkGUI"
    echo ""
    echo "The application will start a web server and open your browser."
    echo "If the browser doesn't open automatically, navigate to:"
    echo "  http://localhost:5000"
else
    echo "Build failed!"
    exit 1
fi