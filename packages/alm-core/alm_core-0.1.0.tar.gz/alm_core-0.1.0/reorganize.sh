#!/bin/bash
# Reorganize ALM project structure

echo "🔧 Reorganizing ALM Core Project..."

# Create clean directory structure
mkdir -p examples
mkdir -p scripts
mkdir -p docs
mkdir -p tests

# Move example files
mv -f test_real_api.py examples/ 2>/dev/null || true
mv -f test_browser_desktop.py examples/ 2>/dev/null || true
mv -f test_browser_chat.py examples/ 2>/dev/null || true
mv -f interactive_browser_bot.py examples/ 2>/dev/null || true
mv -f test_research_working.py examples/ 2>/dev/null || true
mv -f examples.py examples/examples_basic.py 2>/dev/null || true

# Remove old test files
rm -f test_research.py test_research_simple.py test_simple.py 2>/dev/null || true

# Move scripts
mv -f install.sh scripts/ 2>/dev/null || true
mv -f install.bat scripts/ 2>/dev/null || true
mv -f publish.sh scripts/ 2>/dev/null || true
mv -f setup_github.sh scripts/ 2>/dev/null || true
mv -f setup_and_push.sh scripts/ 2>/dev/null || true
mv -f test_local.sh scripts/ 2>/dev/null || true
mv -f quickstart.sh scripts/ 2>/dev/null || true

# Move documentation
mv -f DEPLOYMENT.md docs/ 2>/dev/null || true
mv -f INSTALLATION.md docs/ 2>/dev/null || true
mv -f GITHUB_SETUP.md docs/ 2>/dev/null || true
mv -f QUICKSTART.md docs/ 2>/dev/null || true
mv -f START_HERE.md docs/ 2>/dev/null || true
mv -f PROJECT_SUMMARY.md docs/ 2>/dev/null || true
mv -f READY_TO_PUSH.txt docs/ 2>/dev/null || true

# Remove generated PNG files
rm -f *.png 2>/dev/null || true

# Remove .egg-info (will be regenerated)
rm -rf alm_core.egg-info 2>/dev/null || true
rm -rf .pytest_cache 2>/dev/null || true

echo "✅ Project reorganized!"
echo ""
echo "New structure:"
echo "  alm_core/        - Core package code"
echo "  examples/        - Example scripts and tests"
echo "  scripts/         - Installation and deployment scripts"
echo "  docs/            - Documentation files"
echo "  tests/           - Unit tests"
echo ""
