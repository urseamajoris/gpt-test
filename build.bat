@echo off
REM Build script for Windows systems

echo Agentic Model Framework - Build Script
echo ======================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is required but not found.
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is required but not found.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt

REM Install PyInstaller if not present
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo Building executable...

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
del /q *.pyc 2>nul

REM Build the application
pyinstaller agentic_gui.spec

if errorlevel 0 (
    echo.
    echo Build completed successfully!
    echo Executable location: dist\AgenticFrameworkGUI\
    echo.
    echo To run the application:
    echo   cd dist\AgenticFrameworkGUI
    echo   AgenticFrameworkGUI.exe
    echo.
    echo The application will start a web server and open your browser.
    echo If the browser doesn't open automatically, navigate to:
    echo   http://localhost:5000
    echo.
    pause
) else (
    echo Build failed!
    pause
    exit /b 1
)