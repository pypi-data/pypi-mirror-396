@echo off
REM ALM Core - Windows Installer Script
REM Supports: Windows 10+, Windows Server 2016+

echo ==========================================
echo ^&# ALM Core - Windows Installer
echo ==========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ^!^ Python 3.8+ is required but not installed
    echo.
    echo Install Python from: https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ^*^ Python %PYTHON_VERSION% found
echo.

REM Detect Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo Detected Windows: %VERSION%
echo.

echo Installing Python dependencies...
echo.

REM Upgrade pip, setuptools, wheel
python -m pip install --upgrade pip setuptools wheel -q
if %errorlevel% neq 0 (
    echo ^!^ Failed to upgrade pip
    pause
    exit /b 1
)

REM Install ALM Core
if exist "setup.py" (
    python -m pip install -e ".[dev]" -q
    if %errorlevel% neq 0 (
        echo ^!^ Failed to install ALM Core
        pause
        exit /b 1
    )
    echo ^*^ ALM Core installed (editable mode)
) else (
    echo ^!^ setup.py not found
    pause
    exit /b 1
)

echo.

REM Optional: Install Playwright
setlocal enabledelayedexpansion
set /p INSTALL_PLAYWRIGHT="Install optional dependencies (Playwright for browser automation)? (y/n) "
if /i "!INSTALL_PLAYWRIGHT!"=="y" (
    echo Installing Playwright...
    python -m pip install playwright -q
    if %errorlevel% neq 0 (
        echo ^!^ Failed to install Playwright
        pause
        exit /b 1
    )
    echo Setting up Playwright browsers...
    playwright install -q
    if %errorlevel% neq 0 (
        echo Warning: Playwright browser setup had issues, but core is installed
    )
    echo ^*^ Playwright installed
)
endlocal

echo.
echo Verifying installation...
python -c "from alm_core import AgentLanguageModel; print('^*^ ALM Core imported successfully')"
if %errorlevel% neq 0 (
    echo ^!^ Installation verification failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [SUCCESS] Installation Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Set your API key:
echo    set OPENAI_API_KEY=your-key-here
echo.
echo 2. Try the interactive chatbot:
echo    python interactive_browser_bot.py
echo.
echo 3. Run tests:
echo    python test_real_api.py
echo    python test_browser_desktop.py
echo    python test_research_working.py
echo.
echo 4. Documentation: README.md
echo.
echo GitHub: https://github.com/Jalendar10/alm-core
echo.
pause
