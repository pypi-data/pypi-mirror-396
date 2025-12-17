# ALM Core - Complete Deployment Guide

## 🚀 Production Setup & Installation

Your ALM Core package is fully ready for production deployment across all platforms.

---

## Installation by Platform

### 🍎 macOS

**One-Command Installation:**
```bash
git clone https://github.com/Jalendar10/alm-core.git
cd alm-core
bash install.sh
```

**What it does:**
- ✅ Detects macOS automatically
- ✅ Installs Homebrew (if needed)
- ✅ Installs Python dependencies
- ✅ Installs ALM Core package
- ✅ Optionally installs Playwright for browser automation
- ✅ Verifies installation

**Requirements:**
- Python 3.8+ (installed automatically if using Homebrew)
- macOS 10.13+

---

### �� Linux

**One-Command Installation:**
```bash
git clone https://github.com/Jalendar10/alm-core.git
cd alm-core
bash install.sh
```

**Supported Distributions:**
- Ubuntu 18.04+
- Debian 10+
- Fedora 30+
- RHEL 7+
- CentOS 7+
- Arch Linux

**What it does:**
- ✅ Auto-detects Linux distribution
- ✅ Installs distribution-specific dependencies
- ✅ Installs Python 3.8+ (if needed)
- ✅ Installs ALM Core package
- ✅ Optionally installs Playwright
- ✅ Verifies installation

**Requirements:**
- Python 3.8+
- sudo access (for system dependencies)

---

### 🪟 Windows 10+

**One-Command Installation:**

**Option 1: GUI (Easiest)**
1. Download repository: https://github.com/Jalendar10/alm-core
2. Extract to a folder
3. Double-click `install.bat`
4. Follow prompts

**Option 2: Command Prompt**
```batch
git clone https://github.com/Jalendar10/alm-core.git
cd alm-core
install.bat
```

**What it does:**
- ✅ Detects Windows version
- ✅ Checks Python installation
- ✅ Upgrades pip/setuptools
- ✅ Installs ALM Core package
- ✅ Optionally installs Playwright
- ✅ Verifies installation

**Requirements:**
- Python 3.8+ (add to PATH during installation)
- Windows 10 or later
- Administrator access (recommended)

---

## Post-Installation Setup

### 1. Set API Keys

**macOS/Linux:**
```bash
# Temporary (session only)
export OPENAI_API_KEY='sk-your-key-here'

# Permanent (add to ~/.zshrc or ~/.bashrc)
echo "export OPENAI_API_KEY='sk-your-key-here'" >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
```batch
REM Temporary (session only)
set OPENAI_API_KEY=sk-your-key-here

REM Permanent (System Environment Variables)
setx OPENAI_API_KEY sk-your-key-here
```

### 2. Get Your API Key

1. Visit: https://platform.openai.com/api-keys
2. Create new API key
3. Copy the key (starts with `sk-`)
4. Set as environment variable (see above)

### 3. Verify Installation

```bash
python -c "from alm_core import AgentLanguageModel; print('✓ Ready!')"
```

---

## Running Applications

### Interactive Browser Chatbot

```bash
export OPENAI_API_KEY='sk-...'
python interactive_browser_bot.py
```

**Try these commands:**
- `open gmail`
- `open github`
- `open search for machine learning`
- `fill form`
- `my details`
- Ask questions about current page

### Run All Tests

```bash
# Test 1: Real API functionality
python test_real_api.py

# Test 2: Browser & Desktop control
python test_browser_desktop.py

# Test 3: Deep research engine
python test_research_working.py

# Test 4: Browser chatbot
python interactive_browser_bot.py
```

---

## Package Structure

```
alm-core/
├── alm_core/                 # Main package
│   ├── __init__.py
│   ├── agent.py             # Main agent classes
│   ├── policy.py            # Constitutional Policy Engine
│   ├── memory.py            # Episodic & Semantic Memory
│   ├── controller.py        # BDI Controller
│   ├── llm_client.py        # Multi-LLM support
│   ├── visualizer.py        # Execution visualization
│   ├── research.py          # Deep research engine
│   └── tools/               # Tools
│       ├── browser.py       # Playwright integration
│       └── desktop.py       # OS/Desktop control
├── tests/                   # Unit tests
├── setup.py                 # PyPI configuration
├── pyproject.toml          # Modern Python packaging
├── requirements.txt        # Dependencies
├── install.sh              # Linux/macOS installer
├── install.bat             # Windows installer
├── INSTALLATION.md         # Installation guide
└── README.md               # Main documentation
```

---

## Deployment Scenarios

### 1. Individual User

1. Run: `bash install.sh` (macOS/Linux) or `install.bat` (Windows)
2. Set API key: `export OPENAI_API_KEY='...'`
3. Use: `python interactive_browser_bot.py`

### 2. Docker Container

```dockerfile
FROM python:3.10
WORKDIR /app
RUN git clone https://github.com/Jalendar10/alm-core.git .
RUN python -m pip install -e ".[dev]"
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
CMD ["python", "interactive_browser_bot.py"]
```

### 3. Cloud Deployment (AWS Lambda)

```python
from alm_core import AgentLanguageModel

def lambda_handler(event, context):
    agent = AgentLanguageModel(
        api_key=os.environ['OPENAI_API_KEY'],
        llm_provider='openai',
        model='gpt-3.5-turbo'
    )
    
    messages = [{"role": "user", "content": event['query']}]
    response = agent.llm.generate(messages)
    
    return {'statusCode': 200, 'body': response}
```

### 4. Development Server

```bash
# Clone repo
git clone https://github.com/Jalendar10/alm-core.git
cd alm-core

# Install with development tools
python -m pip install -e ".[dev]"

# Run tests
pytest tests/

# Start development server
python interactive_browser_bot.py
```

---

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|------------|
| **OS** | macOS 10.13, Ubuntu 18.04, Windows 10 | Latest versions |
| **Python** | 3.8 | 3.10+ |
| **RAM** | 2 GB | 8 GB+ |
| **Disk** | 500 MB | 2 GB+ |
| **Internet** | Required (for API calls) | 5+ Mbps |

---

## Optional Dependencies

### Playwright (Browser Automation)

```bash
python -m pip install playwright
playwright install
```

Enables:
- Secure DOM extraction
- PII protection in web content
- Full browser automation

### Development Tools

```bash
python -m pip install -e ".[dev]"
```

Includes:
- pytest (testing)
- black (code formatting)
- pylint (linting)
- sphinx (documentation)

---

## Troubleshooting

### "Module not found" Error

**Solution:**
```bash
# Reinstall package
python -m pip install --upgrade --force-reinstall -e .
```

### API Key Not Working

**Solution:**
```bash
# Verify key is set
echo $OPENAI_API_KEY  # macOS/Linux
echo %OPENAI_API_KEY%  # Windows

# Test with explicit key
python test_real_api.py
# Edit test file to use key directly
```

### Playwright Browser Issues

**Solution:**
```bash
# Reinstall Playwright
python -m pip install --upgrade playwright
playwright install --with-deps
```

### Permission Denied (Linux)

**Solution:**
```bash
# Use sudo
sudo python3 -m pip install -e ".[dev]"

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
python -m pip install -e ".[dev]"
```

---

## Production Best Practices

1. **Use Virtual Environments**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

2. **Use .env Files (not version control)**
```bash
# .env (never commit to git)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

3. **Implement Error Handling**
```python
try:
    agent = AgentLanguageModel(api_key=api_key)
except Exception as e:
    logger.error(f"Agent initialization failed: {e}")
```

4. **Use Logging**
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

5. **Rate Limiting**
```python
import time
time.sleep(0.5)  # Avoid API rate limits
response = agent.llm.generate(messages)
```

6. **Monitor Usage**
```python
stats = agent.memory.get_memory_stats()
print(f"Memory usage: {stats['memory_usage_percent']}%")
```

---

## Support & Resources

- **GitHub:** https://github.com/Jalendar10/alm-core
- **Issues:** https://github.com/Jalendar10/alm-core/issues
- **Documentation:** See INSTALLATION.md, README.md
- **Examples:** Check examples.py and test files

---

## Version Information

- **ALM Core:** v0.1.0
- **Python:** 3.8+
- **License:** MIT
- **Author:** Jalendar Reddy Maligireddy

---

## Quick Reference

| Task | Command |
|------|---------|
| Install | `bash install.sh` or `install.bat` |
| Test | `python test_real_api.py` |
| Run Chatbot | `python interactive_browser_bot.py` |
| View Docs | `cat INSTALLATION.md` |
| Update | `git pull && python -m pip install -e . --upgrade` |

---

**Ready to deploy! 🚀**
