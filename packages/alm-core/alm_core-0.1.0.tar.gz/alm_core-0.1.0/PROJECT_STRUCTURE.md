# ALM Core - Project Structure

```
alm-core/
│
├── SETUP.sh                    # One-command setup for Linux/macOS
├── SETUP.bat                   # One-command setup for Windows
├── setup_project.py            # Cross-platform Python setup script
│
├── README.md                   # Main documentation
├── LICENSE                     # MIT License
├── requirements.txt            # Python dependencies
├── setup.py                    # Package installation config
├── pyproject.toml              # Modern Python packaging
├── MANIFEST.in                 # Package distribution files
│
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
│
├── alm_core/                   # Core package
│   ├── __init__.py             # Package exports
│   ├── agent.py                # Main agent interfaces
│   ├── controller.py           # BDI controller (state machine)
│   ├── policy.py               # Constitutional Policy Engine
│   ├── memory.py               # Data Airlock + Dual Memory
│   ├── llm_client.py           # Multi-LLM provider support
│   ├── visualizer.py           # Execution visualization
│   ├── research.py             # Deep research engine
│   └── tools/
│       ├── browser.py          # Secure browser automation
│       └── desktop.py          # Desktop/OS control
│
├── examples/                   # Example scripts
│   ├── examples_basic.py       # 7 basic usage examples
│   ├── test_real_api.py        # Real OpenAI API test
│   ├── test_browser_desktop.py # Desktop & browser control
│   ├── test_browser_chat.py    # Browser chat demonstration
│   ├── interactive_browser_bot.py # Interactive chatbot
│   └── test_research_working.py # Deep research example
│
├── tests/                      # Unit tests
│   └── test_alm.py             # Comprehensive test suite
│
├── scripts/                    # Utility scripts
│   ├── install.sh              # Linux/macOS installer
│   ├── install.bat             # Windows installer
│   ├── publish.sh              # PyPI publishing
│   └── quickstart.sh           # Quick start demo
│
└── docs/                       # Documentation
    ├── QUICKSTART.md           # Quick start guide
    ├── INSTALLATION.md         # Detailed installation
    ├── DEPLOYMENT.md           # Deployment guide
    ├── GITHUB_SETUP.md         # GitHub setup instructions
    ├── PROJECT_SUMMARY.md      # Project overview
    └── READY_TO_PUSH.txt       # Pre-deployment checklist
```

## Key Files

### Setup Files
- **SETUP.sh / SETUP.bat**: One-command setup for all platforms
- **setup_project.py**: Cross-platform Python setup automation
- **requirements.txt**: Production dependencies
- **.env.example**: Environment variable template

### Core Package (`alm_core/`)
- **agent.py**: High-level agent interfaces (AgentLanguageModel, OmniAgent)
- **controller.py**: BDI state machine (Belief-Desire-Intention)
- **policy.py**: Constitutional Policy Engine (hard constraints)
- **memory.py**: Data Airlock (PII protection) + Dual Memory
- **llm_client.py**: LLM abstraction (OpenAI, Anthropic, local)
- **visualizer.py**: Execution graph generation
- **research.py**: Deep recursive research engine

### Tools (`alm_core/tools/`)
- **browser.py**: Playwright-based browser automation
- **desktop.py**: OS-level operations (files, commands, apps)

### Examples (`examples/`)
- **examples_basic.py**: 7 usage scenarios
- **test_real_api.py**: Real API integration test
- **interactive_browser_bot.py**: Chatbot for web browsing
- **test_research_working.py**: Multi-step research demo

### Tests (`tests/`)
- **test_alm.py**: Comprehensive unit tests

### Scripts (`scripts/`)
- **install.sh/bat**: Package installation
- **publish.sh**: PyPI deployment
- **quickstart.sh**: Demo script

### Documentation (`docs/`)
- **QUICKSTART.md**: Get started in 5 minutes
- **INSTALLATION.md**: Detailed setup instructions
- **DEPLOYMENT.md**: Production deployment
- **PROJECT_SUMMARY.md**: Complete overview

## File Permissions

All `.sh` scripts should be executable:
```bash
chmod +x SETUP.sh
chmod +x scripts/*.sh
```

Windows `.bat` files don't need special permissions.

## Generated Files (Not in Git)

These are created during setup/usage:
- `venv/` - Virtual environment
- `.env` - Your API keys (never commit!)
- `alm_core.egg-info/` - Package metadata
- `.pytest_cache/` - Test cache
- `*.png` - Visualization outputs
- `__pycache__/` - Python bytecode

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-opus-20240229

# Default LLM Provider
LLM_PROVIDER=openai
```

## Development Workflow

1. **Setup**: Run `./SETUP.sh` or `SETUP.bat`
2. **Activate**: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
3. **Code**: Edit files in `alm_core/`
4. **Test**: Run `pytest tests/`
5. **Examples**: Try `python examples/*.py`
6. **Commit**: Add, commit, push changes
7. **Deploy**: Run `scripts/publish.sh` for PyPI

## Package Distribution

The package is distributed as:
- Source distribution (`.tar.gz`)
- Wheel distribution (`.whl`)
- PyPI package: `pip install alm-core`
- GitHub: `pip install git+https://github.com/Jalendar10/alm-core.git`

## Platform Support

- ✅ Linux (Ubuntu, Debian, Fedora, etc.)
- ✅ macOS (10.14+)
- ✅ Windows (10/11)

## Python Version

- Required: Python 3.8 or higher
- Recommended: Python 3.10+
- Tested on: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

## Dependencies

See `requirements.txt` for complete list. Key dependencies:
- `openai>=1.0.0` - OpenAI API
- `anthropic>=0.7.0` - Anthropic API
- `networkx>=3.0` - Graph visualization
- `requests>=2.28.0` - HTTP client
- `playwright>=1.40.0` - Browser automation (optional)

## Next Steps

After setup:
1. Check `docs/QUICKSTART.md`
2. Try `examples/examples_basic.py`
3. Read `README.md` for architecture details
4. Explore `examples/` directory
5. Run tests with `pytest tests/`
