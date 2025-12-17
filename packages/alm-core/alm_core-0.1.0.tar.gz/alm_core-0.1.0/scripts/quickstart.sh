#!/bin/bash

# Quick Start - ALM Core Setup
# Run this script to get started immediately

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         ALM Core - Complete Setup Assistant               ║"
echo "║         Author: Jalendar Reddy Maligireddy                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check current directory
if [ ! -f "setup.py" ]; then
    echo "❌ Error: Please run this from the ALM directory"
    echo "Run: cd /Users/jalendarreddy/Downloads/research/ALM"
    exit 1
fi

echo "✅ You are in the correct directory"
echo ""

# Display menu
echo "What would you like to do?"
echo ""
echo "1. 🚀 Setup GitHub Repository (First Time)"
echo "2. 📦 Publish to PyPI"
echo "3. 🧪 Run Tests"
echo "4. 📖 View Documentation"
echo "5. 💻 Run Examples"
echo "6. 📊 Show Project Structure"
echo "7. 🔍 Verify Installation"
echo "8. ❌ Exit"
echo ""
read -p "Enter your choice (1-8): " choice

case $choice in
    1)
        echo ""
        echo "Setting up GitHub repository..."
        if [ ! -x "setup_github.sh" ]; then
            chmod +x setup_github.sh
        fi
        ./setup_github.sh
        ;;
    2)
        echo ""
        echo "Publishing to PyPI..."
        if [ ! -x "publish.sh" ]; then
            chmod +x publish.sh
        fi
        ./publish.sh
        ;;
    3)
        echo ""
        echo "Running tests..."
        if command -v pytest &> /dev/null; then
            pytest tests/ -v
        else
            echo "Installing pytest..."
            pip install pytest pytest-cov
            pytest tests/ -v
        fi
        ;;
    4)
        echo ""
        echo "Opening documentation..."
        echo ""
        echo "📖 Available Documentation:"
        echo "  - START_HERE.md (You are here!)"
        echo "  - README.md (Main documentation)"
        echo "  - QUICKSTART.md (Quick start guide)"
        echo "  - GITHUB_SETUP.md (GitHub setup instructions)"
        echo ""
        read -p "Which file to open? (press Enter for README): " doc
        doc=${doc:-README.md}
        if [ -f "$doc" ]; then
            cat "$doc" | less
        else
            echo "File not found: $doc"
        fi
        ;;
    5)
        echo ""
        echo "Running examples..."
        echo "⚠️  You need OPENAI_API_KEY environment variable"
        read -p "Do you have an API key set? (y/n): " has_key
        if [[ $has_key =~ ^[Yy]$ ]]; then
            python examples.py
        else
            echo ""
            echo "Set your API key first:"
            echo "  export OPENAI_API_KEY='sk-...'"
            echo "Then run: python examples.py"
        fi
        ;;
    6)
        echo ""
        echo "Project Structure:"
        echo ""
        tree -L 2 -I '__pycache__|*.pyc|*.egg-info|build|dist' || find . -type f -not -path '*/\.*' -not -path '*/__pycache__/*' | head -30
        ;;
    7)
        echo ""
        echo "Verifying installation..."
        echo ""
        echo "✓ Checking Python..."
        python --version
        echo ""
        echo "✓ Checking pip..."
        pip --version
        echo ""
        echo "✓ Checking git..."
        git --version
        echo ""
        echo "✓ Checking project files..."
        [ -f "setup.py" ] && echo "  ✓ setup.py" || echo "  ✗ setup.py missing"
        [ -f "README.md" ] && echo "  ✓ README.md" || echo "  ✗ README.md missing"
        [ -d "alm_core" ] && echo "  ✓ alm_core/" || echo "  ✗ alm_core/ missing"
        [ -d "tests" ] && echo "  ✓ tests/" || echo "  ✗ tests/ missing"
        echo ""
        echo "✓ Checking dependencies..."
        pip install -q -e . && echo "  ✓ Package installable" || echo "  ✗ Installation issues"
        ;;
    8)
        echo "Goodbye! 👋"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    All Done! ✅                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
