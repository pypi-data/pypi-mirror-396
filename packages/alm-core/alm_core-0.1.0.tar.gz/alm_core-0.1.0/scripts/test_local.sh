#!/bin/bash

# Test ALM Core Locally
# This script tests the package installation and basic functionality

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         ALM Core - Local Testing Script                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

echo "Step 1: Installing package in development mode..."
pip install -e . -q
print_success "Package installed"

echo ""
echo "Step 2: Running unit tests..."
if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short
    print_success "Tests passed"
else
    print_warning "pytest not found, installing..."
    pip install pytest -q
    pytest tests/ -v --tb=short
    print_success "Tests passed"
fi

echo ""
echo "Step 3: Testing imports..."
python -c "
from alm_core import AgentLanguageModel, OmniAgent
from alm_core import Constitution, DataAirlock, DualMemory
from alm_core import ExecutionVisualizer, DeepResearcher
print('✓ All imports successful')
"
print_success "Imports working"

echo ""
echo "Step 4: Testing basic functionality..."
python -c "
import os
from alm_core import AgentLanguageModel

# Test without API key (should work for initialization)
agent = AgentLanguageModel(
    api_key='test-key',  # Dummy key for testing
    llm_provider='local',  # Use local to avoid API calls
    model='test-model'
)

print('✓ Agent initialization successful')
print(f'✓ LLM Provider: {agent.llm.provider}')
print(f'✓ Model: {agent.llm.model}')

# Test memory
agent.controller.memory.add_episode('user', 'test message')
stats = agent.get_memory_stats()
print(f'✓ Memory working: {stats[\"working_memory_size\"]} messages')
"
print_success "Basic functionality working"

echo ""
echo "Step 5: Testing environment variable configuration..."
export OPENAI_MODEL="gpt-3.5-turbo"
python -c "
import os
from alm_core import AgentLanguageModel

# Test environment variable reading
agent = AgentLanguageModel(
    api_key='test-key',
    llm_provider='openai'
)

assert agent.llm.model == 'gpt-3.5-turbo', f'Expected gpt-3.5-turbo, got {agent.llm.model}'
print('✓ Environment variable OPENAI_MODEL correctly read')
print(f'✓ Model set to: {agent.llm.model}')
"
print_success "Environment variables working"

echo ""
echo "Step 6: Testing policy enforcement..."
python -c "
from alm_core import Constitution
from alm_core.policy import PolicyViolationError

rules = [
    {'action': 'delete_db', 'allow': False},
    {'action': 'file_write', 'allowed_paths': ['/tmp']}
]

constitution = Constitution(rules)

# Test blocking
try:
    constitution.validate_action('delete_db', {})
    print('✗ Should have blocked delete_db')
    exit(1)
except PolicyViolationError:
    print('✓ Policy correctly blocked dangerous action')

# Test allowing
try:
    constitution.validate_action('file_write', {'path': '/tmp/test.txt'})
    print('✓ Policy correctly allowed safe action')
except PolicyViolationError:
    print('✗ Should have allowed safe action')
    exit(1)
"
print_success "Policy enforcement working"

echo ""
echo "Step 7: Testing Data Airlock (PII protection)..."
python -c "
from alm_core import DataAirlock

airlock = DataAirlock()

# Test email sanitization
text = 'Contact me at john@example.com or call 555-123-4567'
sanitized = airlock.sanitize(text)

assert 'john@example.com' not in sanitized, 'Email not sanitized'
assert '555-123-4567' not in sanitized, 'Phone not sanitized'
assert '<EMAIL_' in sanitized, 'Email token missing'
assert '<PHONE_' in sanitized, 'Phone token missing'

print('✓ PII sanitization working')

# Test rehydration
rehydrated = airlock.rehydrate(sanitized)
assert 'john@example.com' in rehydrated, 'Email not rehydrated'
print('✓ PII rehydration working')
"
print_success "Data Airlock working"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              All Tests Passed! ✅                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Package is ready for production!"
echo ""
echo "Environment Variables (Optional):"
echo "  export OPENAI_API_KEY='sk-...'     # Your OpenAI API key"
echo "  export OPENAI_MODEL='gpt-4'        # Default: gpt-4"
echo "  export ANTHROPIC_API_KEY='sk-...' # Your Anthropic API key"
echo "  export LLM_PROVIDER='openai'       # Provider to use"
echo ""
echo "Quick Test with Real API:"
echo "  export OPENAI_API_KEY='sk-...'"
echo "  python -c \"from alm_core import AgentLanguageModel; agent = AgentLanguageModel(); print(agent.process('What is 2+2?'))\""
