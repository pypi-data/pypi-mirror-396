#!/bin/bash
# ALM Core - Universal Installation Script
# Supports: Linux, macOS, Windows (WSL/Git Bash)
# Auto-detects OS and installs dependencies

set -e  # Exit on error

echo "=========================================="
echo "🤖 ALM Core - Universal Installer"
echo "=========================================="
echo ""

# Detect OS
OS_TYPE=$(uname -s)
echo "Detected OS: $OS_TYPE"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Python 3.8+ check
echo "Checking Python installation..."
if command_exists python3; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    echo "✓ Python $PYTHON_VERSION found"
else
    echo "❌ Python 3.8+ is required but not installed"
    echo ""
    echo "Install Python from: https://www.python.org/downloads/"
    exit 1
fi

echo ""

# Install pip dependencies
echo "Installing Python dependencies..."
echo ""

if [ "$OS_TYPE" = "Darwin" ]; then
    # macOS specific
    echo "Setting up for macOS..."
    
    # Check for Homebrew
    if ! command_exists brew; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install system dependencies
    echo "Installing system dependencies..."
    brew install openssl sqlite3 xz zlib 2>/dev/null || true
    
elif [ "$OS_TYPE" = "Linux" ]; then
    # Linux specific
    echo "Setting up for Linux..."
    
    # Detect Linux distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    else
        DISTRO="unknown"
    fi
    
    echo "Distribution: $DISTRO"
    
    # Install system dependencies based on distro
    if [ "$DISTRO" = "ubuntu" ] || [ "$DISTRO" = "debian" ]; then
        echo "Installing system dependencies (apt)..."
        sudo apt-get update -qq
        sudo apt-get install -y python3-pip python3-venv build-essential libssl-dev libffi-dev 2>/dev/null || true
        
    elif [ "$DISTRO" = "fedora" ] || [ "$DISTRO" = "rhel" ] || [ "$DISTRO" = "centos" ]; then
        echo "Installing system dependencies (dnf/yum)..."
        sudo dnf install -y python3-pip python3-devel openssl-devel libffi-devel gcc 2>/dev/null || \
        sudo yum install -y python3-pip python3-devel openssl-devel libffi-devel gcc 2>/dev/null || true
        
    elif [ "$DISTRO" = "arch" ]; then
        echo "Installing system dependencies (pacman)..."
        sudo pacman -S --noconfirm python-pip base-devel openssl libffi 2>/dev/null || true
    fi
fi

echo ""
echo "Installing ALM Core package and dependencies..."
echo ""

# Upgrade pip
$PYTHON_CMD -m pip install --upgrade pip setuptools wheel -q

# Install the package in editable mode
if [ -f "setup.py" ]; then
    $PYTHON_CMD -m pip install -e ".[dev]" -q
    echo "✓ ALM Core installed (editable mode)"
else
    echo "❌ setup.py not found"
    exit 1
fi

# Optional: Install development dependencies
echo ""
read -p "Install optional dependencies (Playwright for browser automation)? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Playwright..."
    $PYTHON_CMD -m pip install playwright -q
    echo "Setting up Playwright browsers..."
    playwright install -q
    echo "✓ Playwright installed"
fi

echo ""
echo "Verifying installation..."
$PYTHON_CMD -c "from alm_core import AgentLanguageModel; print('✓ ALM Core imported successfully')" && {
    echo ""
    echo "=========================================="
    echo "✅ Installation Complete!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Set your API key:"
    echo "   export OPENAI_API_KEY='your-key-here'"
    echo ""
    echo "2. Try the interactive chatbot:"
    echo "   python interactive_browser_bot.py"
    echo ""
    echo "3. Run tests:"
    echo "   python test_real_api.py"
    echo "   python test_browser_desktop.py"
    echo "   python test_research_working.py"
    echo ""
    echo "4. Documentation: README.md"
    echo ""
    echo "GitHub: https://github.com/Jalendar10/alm-core"
} || {
    echo "❌ Installation verification failed"
    exit 1
}
