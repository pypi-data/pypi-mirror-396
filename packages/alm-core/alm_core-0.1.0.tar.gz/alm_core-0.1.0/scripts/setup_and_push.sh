#!/bin/bash

# Complete Setup: Test Locally, Setup GitHub, and Push
# Run this script to do everything automatically

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║    ALM Core - Complete Setup & Deploy                     ║"
echo "║    Author: Jalendar Reddy Maligireddy                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "\n${BLUE}▶${NC} $1\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Make scripts executable
chmod +x test_local.sh setup_github.sh publish.sh quickstart.sh

# STEP 1: Test locally first
print_step "STEP 1/4: Testing locally..."
./test_local.sh

# STEP 2: Initialize Git repository
print_step "STEP 2/4: Initializing Git repository..."

if [ -d ".git" ]; then
    print_warning "Git repository already exists"
else
    git init
    print_success "Git initialized"
fi

git config user.name "Jalendar Reddy Maligireddy"
git config user.email "jalendarreddy97@gmail.com"
print_success "Git configured"

# STEP 3: Create .env.example file
print_step "STEP 3/4: Creating environment configuration..."

cat > .env.example << 'EOF'
# ALM Core Environment Variables
# Copy this file to .env and fill in your values

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-opus-20240229

# Default LLM Provider
LLM_PROVIDER=openai
EOF

print_success "Created .env.example"

# Update .gitignore to exclude .env
if ! grep -q "^.env$" .gitignore 2>/dev/null; then
    echo -e "\n# Environment variables\n.env" >> .gitignore
    print_success "Updated .gitignore"
fi

# STEP 4: Commit and prepare for GitHub
print_step "STEP 4/4: Committing code..."

git add .
git commit -m "Initial commit: ALM Core v0.1.0

Features:
- ✨ Flexible LLM model configuration (any OpenAI/Anthropic model)
- 🔒 Environment variable support for API keys
- 🛡️ Constitutional Policy Engine (hard constraints)
- 🔐 Data Airlock (PII protection)
- 🧠 Deterministic BDI Controller
- 🌐 Browser automation with Playwright
- 🖥️ Desktop/OS control
- 🔬 Deep research engine
- 📊 Execution visualization
- ✅ Complete test suite

Author: Jalendar Reddy Maligireddy <jalendarreddy97@gmail.com>
Repository: https://github.com/Jalendar10/alm-core"

print_success "Initial commit created"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Ready to Push to GitHub! 🚀                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next Steps:"
echo ""
echo "1️⃣  Create GitHub repository:"
echo "   → Go to: https://github.com/new"
echo "   → Repository name: alm-core"
echo "   → Description: Agent Language Model - Deterministic, policy-driven AI agents"
echo "   → Make it: ✅ Public"
echo "   → Don't initialize with README"
echo ""
echo "2️⃣  Push to GitHub:"
echo ""
echo "   git remote add origin https://github.com/Jalendar10/alm-core.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3️⃣  Create a release tag:"
echo ""
echo "   git tag -a v0.1.0 -m 'Initial release - Flexible LLM support'"
echo "   git push origin v0.1.0"
echo ""
echo "4️⃣  Test the installation:"
echo ""
echo "   # Set up environment"
echo "   export OPENAI_API_KEY='sk-...'"
echo "   export OPENAI_MODEL='gpt-3.5-turbo'  # Or any model you want"
echo ""
echo "   # Test it"
echo "   python test_simple.py"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Supported Models (any OpenAI or Anthropic model):     ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  OpenAI:                                                   ║"
echo "║    • gpt-4                                                 ║"
echo "║    • gpt-4-turbo-preview                                   ║"
echo "║    • gpt-3.5-turbo                                         ║"
echo "║    • gpt-3.5-turbo-16k                                     ║"
echo "║                                                            ║"
echo "║  Anthropic:                                                ║"
echo "║    • claude-3-opus-20240229                                ║"
echo "║    • claude-3-sonnet-20240229                              ║"
echo "║    • claude-3-haiku-20240307                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
