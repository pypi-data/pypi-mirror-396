@echo off
REM ALM Core - One-Command Setup for Windows
REM Usage: SETUP.bat

echo ================================
echo ALM Core - Automated Setup
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Python not found. Please install Python 3.8 or higher.
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

REM Run setup script
%PYTHON_CMD% setup_project.py

echo.
echo Setup complete! Follow the next steps above.
pause
