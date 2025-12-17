#!/bin/bash

# ALM Core - GitHub Repository Setup Script
# Author: Jalendar Reddy Maligireddy
# Email: jalendarreddy97@gmail.com

set -e

echo "========================================="
echo "ALM Core - GitHub Setup"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_note() {
    echo -e "${YELLOW}[NOTE]${NC} $1"
}

# Step 1: Initialize Git
print_step "1. Initializing Git repository..."

if [ -d ".git" ]; then
    print_note "Git repository already exists. Skipping initialization."
else
    git init
    print_info "Git initialized!"
fi

# Step 2: Configure Git
print_step "2. Configuring Git..."

git config user.name "Jalendar Reddy Maligireddy"
git config user.email "jalendarreddy97@gmail.com"

print_info "Git configured with:"
print_info "  Name: $(git config user.name)"
print_info "  Email: $(git config user.email)"

# Step 3: Add files
print_step "3. Adding files to Git..."

git add .
print_info "All files staged!"

# Step 4: Create initial commit
print_step "4. Creating initial commit..."

git commit -m "Initial commit: ALM Core - Agent Language Model Architecture

- Implemented Deterministic Controller (BDI architecture)
- Implemented Data Airlock (PII protection)
- Implemented Constitutional Policy Engine
- Added browser automation tools
- Added deep research capabilities
- Added execution visualization
- Complete PyPI packaging setup
"

print_info "Initial commit created!"

# Step 5: Create GitHub repository instructions
print_step "5. Creating GitHub repository..."
echo ""
print_note "You need to create the repository on GitHub first!"
echo ""
echo "Follow these steps:"
echo ""
echo "1. Go to: https://github.com/new"
echo "2. Repository name: alm-core"
echo "3. Description: Agent Language Model (ALM): A deterministic, policy-driven architecture for robust AI agents"
echo "4. Choose: Public (or Private if you prefer)"
echo "5. Do NOT initialize with README, .gitignore, or license (we already have them)"
echo "6. Click 'Create repository'"
echo ""
read -p "Press ENTER after you've created the repository on GitHub..."

# Step 6: Add remote
print_step "6. Adding GitHub remote..."

if git remote | grep -q "origin"; then
    print_note "Remote 'origin' already exists. Removing it..."
    git remote remove origin
fi

git remote add origin https://github.com/Jalendar10/alm-core.git

print_info "Remote added: $(git remote -v | grep origin | head -1)"

# Step 7: Create and push to main branch
print_step "7. Pushing to GitHub..."

# Rename branch to main if needed
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    git branch -M main
fi

# Push to GitHub
git push -u origin main

print_info "Code pushed to GitHub!"

# Step 8: Create tags
print_step "8. Creating release tag..."

git tag -a v0.1.0 -m "Release v0.1.0 - Initial ALM Core release

Features:
- Deterministic BDI Controller
- Data Airlock with PII protection
- Constitutional Policy Engine
- Browser automation (Playwright)
- Desktop control
- Deep research engine
- Execution visualization
- Multi-LLM support (OpenAI, Anthropic, local)
"

git push origin v0.1.0

print_info "Tag v0.1.0 created and pushed!"

# Step 9: Display next steps
echo ""
echo "========================================="
echo -e "${GREEN}✅ GitHub Repository Setup Complete!${NC}"
echo "========================================="
echo ""
echo "Your repository is now live at:"
echo "🔗 https://github.com/Jalendar10/alm-core"
echo ""
echo "Next Steps:"
echo ""
echo "1. 📝 Update repository settings on GitHub:"
echo "   - Add topics: ai, agent, llm, automation, python"
echo "   - Set description"
echo "   - Add website: https://github.com/Jalendar10/alm-core"
echo ""
echo "2. 📦 Publish to PyPI:"
echo "   ./publish.sh"
echo ""
echo "3. 🌟 Create a GitHub Release:"
echo "   - Go to: https://github.com/Jalendar10/alm-core/releases/new"
echo "   - Tag: v0.1.0"
echo "   - Title: ALM Core v0.1.0 - Initial Release"
echo "   - Add release notes from README.md"
echo ""
echo "4. 📋 Add to your GitHub profile:"
echo "   - Star the repository"
echo "   - Pin it to your profile"
echo ""
echo "========================================="
