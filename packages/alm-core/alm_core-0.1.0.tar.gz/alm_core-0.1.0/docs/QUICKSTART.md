# ALM Core - Quick Start Guide

## 📦 Installation

### Option 1: Install from PyPI (after publishing)

```bash
pip install alm-core
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/Jalendar10/alm-core.git
cd alm-core

# Install in development mode
pip install -e .

# Or install with all features
pip install -e ".[full]"

# Install Playwright browsers (for web automation)
playwright install chromium
```

## 🚀 Quick Start

### 1. Basic Usage

```python
from alm_core import AgentLanguageModel

# Initialize agent with your API key
agent = AgentLanguageModel(
    openai_key="sk-your-key-here",
    rules=[
        {"action": "delete_db", "allow": False}
    ]
)

# Use the agent
response = agent.process("What is 2+2?")
print(response)
```

### 2. With PII Protection

```python
from alm_core import AgentLanguageModel

agent = AgentLanguageModel(openai_key="sk-...")

# Email is automatically sanitized before going to OpenAI
response = agent.process(
    "My email is john@company.com. Create a professional summary."
)
# Response contains real email (rehydrated), but OpenAI never saw it
```

### 3. Full-Featured OmniAgent

```python
from alm_core import OmniAgent

config = {
    "api_key": "sk-...",
    "provider": "openai",
    "model": "gpt-4",
    "rules": [
        {"action": "delete_db", "allow": False},
        {"action": "file_write", "allowed_paths": ["/tmp"]}
    ]
}

with OmniAgent(config) as agent:
    # Deep research
    research = agent.deep_dive("Quantum Computing", duration_minutes=5)
    
    # Execute tasks
    result = agent.execute_task("Create a summary of recent AI papers")
    
    # Export session
    agent.export_session("my_session")
```

## 🔧 Configuration

### Environment Variables

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Constitutional Rules

```python
rules = [
    # Deny specific actions
    {"action": "delete_db", "allow": False},
    
    # Parameter restrictions
    {"action": "email", "forbidden_params": {"domain": "gmail.com"}},
    
    # Path restrictions
    {"action": "file_write", "allowed_paths": ["/safe/dir"]},
    
    # Domain restrictions
    {"action": "web_request", "forbidden_domains": ["malicious.com"]}
]
```

### LLM Providers

```python
# OpenAI
agent = AgentLanguageModel(
    openai_key="sk-...",
    llm_provider="openai",
    model="gpt-4"
)

# Anthropic
agent = AgentLanguageModel(
    openai_key="sk-ant-...",
    llm_provider="anthropic",
    model="claude-3-opus-20240229"
)

# Local (Ollama)
agent = AgentLanguageModel(
    llm_provider="local",
    model="llama2"
)
```

## 🛠️ Advanced Features

### Custom Tools

```python
def calculate_roi(investment: float, return_value: float) -> str:
    roi = ((return_value - investment) / investment) * 100
    return f"ROI: {roi:.2f}%"

agent.add_tool("calculate_roi", calculate_roi)
```

### Memory Management

```python
# Store in long-term memory
agent.controller.memory.add_to_long_term("user_preference", {"theme": "dark"})

# Recall from long-term memory
pref = agent.controller.memory.recall_from_long_term("user_preference")

# Get memory stats
stats = agent.get_memory_stats()
```

### Execution Visualization

```python
from alm_core import ExecutionVisualizer

visualizer = ExecutionVisualizer()

# Add steps during execution
root = visualizer.add_step(None, "task", "Main Task")
step1 = visualizer.add_step(root, "action", "Sub-action")

# Update status
visualizer.update_status(step1, "success", result="Done")

# Export visualization
visualizer.export_graph("execution.png")
```

## 📊 Publishing to PyPI

### 1. Build the Package

```bash
# Install build tools
pip install build twine

# Build the package
python -m build
```

This creates files in `dist/`:
- `alm-core-0.1.0.tar.gz` (source distribution)
- `alm_core-0.1.0-py3-none-any.whl` (wheel distribution)

### 2. Test Upload (TestPyPI)

```bash
# Create account at https://test.pypi.org
# Get API token from account settings

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ alm-core
```

### 3. Production Upload (PyPI)

```bash
# Create account at https://pypi.org
# Get API token from account settings

# Upload to PyPI
twine upload dist/*

# Install from PyPI
pip install alm-core
```

### 4. Configure API Tokens

Create `~/.pypirc`:

```ini
[pypi]
  username = __token__
  password = pypi-your-api-token-here

[testpypi]
  username = __token__
  password = pypi-your-test-api-token-here
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=alm_core

# Run specific test
pytest tests/test_alm.py::TestConstitution -v
```

## 📖 Examples

Run the examples file:

```bash
export OPENAI_API_KEY="sk-..."
python examples.py
```

## 🐛 Troubleshooting

### Playwright Installation Issues

```bash
# Install Playwright
pip install playwright

# Install browsers
playwright install chromium

# If permission issues on Linux
playwright install-deps
```

### Import Errors

```bash
# Ensure package is installed
pip install -e .

# Check Python path
python -c "import alm_core; print(alm_core.__file__)"
```

### API Key Issues

```bash
# Check environment variable
echo $OPENAI_API_KEY

# Or set in code
agent = AgentLanguageModel(openai_key="sk-...")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📚 Documentation

- **API Reference**: See docstrings in source code
- **Examples**: See `examples.py`
- **Tests**: See `tests/test_alm.py`

## 📧 Support

- GitHub Issues: https://github.com/Jalendar10/alm-core/issues
- Email: jalendarreddy97@gmail.com

## 📄 License

MIT License - see LICENSE file for details
