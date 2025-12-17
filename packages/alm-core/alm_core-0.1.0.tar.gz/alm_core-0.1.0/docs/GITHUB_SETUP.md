# GitHub Repository Setup Guide

## 📋 Prerequisites

1. **GitHub Account**: Make sure you're logged in to https://github.com
2. **Git Installed**: Verify with `git --version`
3. **GitHub CLI (optional)**: Install with `brew install gh` (for easier authentication)

## 🚀 Quick Setup (Automated)

### Option 1: Using the Setup Script

```bash
cd /Users/jalendarreddy/Downloads/research/ALM
chmod +x setup_github.sh
./setup_github.sh
```

This script will:
- Initialize Git repository
- Configure your name and email
- Create initial commit
- Guide you through creating the GitHub repository
- Push code to GitHub
- Create version tag

### Option 2: Manual Setup

Follow these steps if you prefer manual control:

## 📝 Manual Setup Steps

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in the details:
   - **Repository name**: `alm-core`
   - **Description**: `Agent Language Model (ALM): A deterministic, policy-driven architecture for robust AI agents`
   - **Visibility**: Public ✅
   - **DO NOT** initialize with README, .gitignore, or license (we already have them)
3. Click **"Create repository"**

### Step 2: Initialize Local Repository

```bash
cd /Users/jalendarreddy/Downloads/research/ALM

# Initialize Git (if not already done)
git init

# Configure Git
git config user.name "Jalendar Reddy Maligireddy"
git config user.email "jalendarreddy97@gmail.com"

# Check configuration
git config --list | grep user
```

### Step 3: Add Files and Commit

```bash
# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: ALM Core - Agent Language Model Architecture

Features:
- Deterministic Controller (BDI architecture)
- Data Airlock (PII protection)
- Constitutional Policy Engine
- Browser automation tools
- Deep research capabilities
- Execution visualization
- Complete PyPI packaging"
```

### Step 4: Connect to GitHub

```bash
# Add remote repository
git remote add origin https://github.com/Jalendar10/alm-core.git

# Verify remote
git remote -v

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 5: Create Release Tag

```bash
# Create annotated tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial ALM Core release"

# Push tag to GitHub
git push origin v0.1.0
```

## 🔐 Authentication

### Using Personal Access Token (PAT)

If prompted for credentials:

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Give it a name: "ALM Core"
4. Select scopes:
   - ✅ repo (all)
   - ✅ workflow
5. Click **"Generate token"**
6. Copy the token (you won't see it again!)
7. When pushing, use the token as your password

### Using GitHub CLI (Recommended)

```bash
# Install GitHub CLI
brew install gh

# Authenticate
gh auth login

# Follow the prompts to authenticate via browser
```

## ✨ Post-Setup Tasks

### 1. Configure Repository Settings

Go to https://github.com/Jalendar10/alm-core/settings

**General Settings:**
- ✅ Allow issues
- ✅ Allow discussions (optional)
- ✅ Allow projects

**Topics:**
Add these topics for discoverability:
- `ai`
- `agent`
- `llm`
- `automation`
- `python`
- `machine-learning`
- `artificial-intelligence`
- `privacy`
- `security`

### 2. Create GitHub Release

1. Go to https://github.com/Jalendar10/alm-core/releases/new
2. Select tag: `v0.1.0`
3. Release title: `ALM Core v0.1.0 - Initial Release`
4. Description (copy from below):

```markdown
# ALM Core v0.1.0 - Initial Release

## 🎉 First Release

This is the initial release of ALM Core - a deterministic, policy-driven architecture for robust AI agents.

## ✨ Key Features

### Core Architecture
- **Deterministic BDI Controller**: Belief-Desire-Intention state machine
- **Constitutional Policy Engine**: Hard constraints enforced programmatically
- **Data Airlock**: PII sanitization before LLM inference

### Capabilities
- 🌐 **Browser Automation**: Secure web automation with Playwright
- 🖥️ **Desktop Control**: OS-level automation
- 🔬 **Deep Research**: Recursive knowledge acquisition
- 📊 **Execution Visualization**: Real-time thought process graphs

### LLM Support
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Local models (Ollama)

## 📦 Installation

```bash
pip install alm-core
```

## 🚀 Quick Start

```python
from alm_core import AgentLanguageModel

agent = AgentLanguageModel(
    openai_key="sk-...",
    rules=[{"action": "delete_db", "allow": False}]
)

response = agent.process("What is 2+2?")
```

## 📚 Documentation

See [README.md](https://github.com/Jalendar10/alm-core#readme) for full documentation.

## 🤝 Contributing

Contributions welcome! Please see our contributing guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.
```

5. Click **"Publish release"**

### 3. Update README Badges (Optional)

Add these badges to the top of README.md:

```markdown
[![GitHub stars](https://img.shields.io/github/stars/Jalendar10/alm-core?style=social)](https://github.com/Jalendar10/alm-core)
[![GitHub forks](https://img.shields.io/github/forks/Jalendar10/alm-core?style=social)](https://github.com/Jalendar10/alm-core/fork)
[![GitHub issues](https://img.shields.io/github/issues/Jalendar10/alm-core)](https://github.com/Jalendar10/alm-core/issues)
```

## 📦 Publishing to PyPI

After GitHub is set up, publish to PyPI:

```bash
# Build the package
python -m build

# Upload to PyPI (production)
twine upload dist/*

# Or test first on TestPyPI
twine upload --repository testpypi dist/*
```

See [QUICKSTART.md](QUICKSTART.md) for detailed PyPI publishing instructions.

## 🎯 Verification Checklist

- [ ] Repository created on GitHub
- [ ] Code pushed to main branch
- [ ] Tag v0.1.0 created and pushed
- [ ] Repository topics added
- [ ] GitHub Release created
- [ ] README displays correctly
- [ ] License file present
- [ ] Repository starred/pinned (optional)

## 🆘 Troubleshooting

### Authentication Failed

```bash
# Use personal access token
git remote set-url origin https://Jalendar10:YOUR_TOKEN@github.com/Jalendar10/alm-core.git

# Or use GitHub CLI
gh auth login
```

### Branch Already Exists

```bash
# If main branch already exists on remote
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Large Files Warning

```bash
# If you have large files, add them to .gitignore
echo "*.png" >> .gitignore
echo "*.jpg" >> .gitignore
git rm --cached -r .
git add .
git commit -m "Remove large files"
```

## 📧 Support

- **Issues**: https://github.com/Jalendar10/alm-core/issues
- **Email**: jalendarreddy97@gmail.com

---

**Author**: Jalendar Reddy Maligireddy  
**Repository**: https://github.com/Jalendar10/alm-core
