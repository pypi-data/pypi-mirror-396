#!/bin/bash
# ALM Core - One-Command Setup for Linux/macOS
# Usage: ./SETUP.sh

set -e

echo "🚀 ALM Core - Automated Setup"
echo "=============================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Run setup script
python3 setup_project.py

echo ""
echo "✅ Setup complete! Follow the next steps above."
