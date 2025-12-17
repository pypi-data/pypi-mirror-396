# ALM Core - Installation Guide

Complete installation instructions for Linux, macOS, and Windows.

## Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **git** (for cloning from GitHub)

## Quick Start

### macOS & Linux

```bash
# 1. Clone the repository
git clone https://github.com/Jalendar10/alm-core.git
cd alm-core

# 2. Run the installer
bash install.sh

# 3. Set your API key
export OPENAI_API_KEY='sk-your-key-here'

# 4. Test the installation
python test_real_api.py
```

### Windows

```batch
REM 1. Clone the repository
git clone https://github.com/Jalendar10/alm-core.git
cd alm-core

REM 2. Run the installer
install.bat

REM 3. Set your API key
set OPENAI_API_KEY=sk-your-key-here

REM 4. Test the installation
python test_real_api.py
```

---

## Detailed Installation by OS

### macOS

**Automatic Installation:**
```bash
bash install.sh
```

**Manual Installation:**

1. **Install Homebrew (if not installed):**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install Python 3:**
```bash
brew install python3
```

3. **Clone and install:**
```bash
git clone https://github.com/Jalendar10/alm-core.git
cd alm-core
python3 -m pip install -e ".[dev]"
```

**Optional - Browser Automation:**
```bash
python3 -m pip install playwright
playwright install
```

---

### Linux (Ubuntu/Debian)

**Automatic Installation:**
```bash
bash install.sh
```

**Manual Installation:**

1. **Update package manager:**
```bash
sudo apt-get update
```

2. **Install Python 3 and dependencies:**
```bash
sudo apt-get install python3 python3-pip python3-venv build-essential libssl-dev libffi-dev
```

3. **Clone and install:**
```bash
git clone https://github.com/Jalendar10/alm-core.git
cd alm-core
python3 -m pip install -e ".[dev]"
```

**For Fedora/RHEL/CentOS:**
```bash
sudo dnf install python3 python3-pip python3-devel openssl-devel libffi-devel gcc
python3 -m pip install -e ".[dev]"
```

**Optional - Browser Automation:**
```bash
python3 -m pip install playwright
playwright install
```

---

### Windows 10+

**Automatic Installation:**
1. Download repository from GitHub or use Git Bash:
```bash
git clone https://github.com/Jalendar10/alm-core.git
cd alm-core
```

2. Double-click `install.bat` or run in Command Prompt:
```batch
install.bat
```

**Manual Installation:**

1. **Install Python 3:**
   - Visit https://www.python.org/downloads/
   - Download Python 3.10+
   - **IMPORTANT:** Check "Add Python to PATH" during installation

2. **Clone repository:**
```batch
git clone https://github.com/Jalendar10/alm-core.git
cd alm-core
```

3. **Install ALM Core:**
```batch
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

**Optional - Browser Automation:**
```batch
python -m pip install playwright
playwright install
```

---

## Verify Installation

Test that everything is installed correctly:

```python
python -c "from alm_core import AgentLanguageModel; print('✓ ALM Core installed')"
```

**Expected output:**
```
✓ ALM Core installed
```

---

## Set Up API Keys

### For OpenAI

1. Get your API key from: https://platform.openai.com/api-keys
2. Create a `.env` file in the project directory:

```bash
# .env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
```

3. Or set environment variable (temporary):

**macOS/Linux:**
```bash
export OPENAI_API_KEY='sk-your-key-here'
```

**Windows:**
```batch
set OPENAI_API_KEY=sk-your-key-here
```

### For Anthropic (Optional)

```bash
export ANTHROPIC_API_KEY='your-key-here'
```

---

## Run Tests

After installation, verify everything works:

```bash
# Test 1: Real API call
python test_real_api.py

# Test 2: Desktop and browser control
python test_browser_desktop.py

# Test 3: Deep research
python test_research_working.py

# Test 4: Interactive chatbot
python interactive_browser_bot.py
```

---

## Using ALM Core

### Example 1: Simple Query

```python
from alm_core import AgentLanguageModel
import os

api_key = os.environ.get("OPENAI_API_KEY")
agent = AgentLanguageModel(
    api_key=api_key,
    llm_provider="openai",
    model="gpt-3.5-turbo"
)

messages = [{"role": "user", "content": "What is ALM?"}]
response = agent.llm.generate(messages)
print(response)
```

### Example 2: With PII Protection

```python
from alm_core import AgentLanguageModel

agent = AgentLanguageModel(api_key=api_key)

# Sensitive data is automatically protected
text = "Email: user@example.com, Phone: 555-123-4567"
sanitized = agent.airlock.sanitize(text)
print(sanitized)  # Outputs: Email: <EMAIL_xxx>, Phone: 555-123-4567
```

### Example 3: Interactive Chatbot

```bash
export OPENAI_API_KEY='your-key-here'
python interactive_browser_bot.py
```

Then try:
- `open gmail`
- `fill form`
- `my details`
- Or ask any question about the current page!

---

## Troubleshooting

### Issue: "Python not found"
**Solution:** Make sure Python 3.8+ is installed and in PATH
```bash
python3 --version
```

### Issue: "pip install fails"
**Solution:** Upgrade pip first
```bash
python -m pip install --upgrade pip
```

### Issue: "OPENAI_API_KEY not set"
**Solution:** Set environment variable before running:
```bash
export OPENAI_API_KEY='sk-your-key-here'
python test_real_api.py
```

### Issue: "Playwright not found"
**Solution:** Install Playwright browsers:
```bash
python -m pip install playwright
playwright install
```

### Issue: Permission denied on Linux
**Solution:** Use `sudo` for system-wide installation:
```bash
sudo python3 -m pip install -e ".[dev]"
```

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8 | 3.10+ |
| RAM | 2GB | 8GB+ |
| Disk Space | 500MB | 2GB+ |
| OS | macOS 10.13+, Ubuntu 18.04+, Windows 10+ | Latest versions |

---

## Getting Help

- **GitHub Issues:** https://github.com/Jalendar10/alm-core/issues
- **Documentation:** See README.md
- **Examples:** Check `examples.py`

---

## Next Steps

1. ✅ Install ALM Core
2. ✅ Set API key
3. ✅ Run tests
4. 📖 Read README.md for usage examples
5. 🚀 Build your own agents!

Happy coding! 🤖
