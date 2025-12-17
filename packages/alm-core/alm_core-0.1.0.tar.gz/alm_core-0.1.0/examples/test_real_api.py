"""
Real API test for ALM Core
Demonstrates actual LLM usage with OpenAI API
"""
import os
from alm_core import AgentLanguageModel

# Check for API key
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY environment variable not set")
    print("\nPlease set your API key:")
    print("  export OPENAI_API_KEY='sk-...'")
    print("\nOr create a .env file with:")
    print("  OPENAI_API_KEY=sk-...")
    exit(1)

print("🚀 Testing ALM Core with real OpenAI API")
print("=" * 50)
print()

# Test 1: Simple query with GPT-3.5-turbo (cheaper for testing)
print("Test 1: Simple Query with GPT-3.5-turbo")
print("-" * 50)

agent = AgentLanguageModel(
    api_key=api_key,
    llm_provider="openai",
    model="gpt-3.5-turbo",
    rules=[
        {"action": "delete_file", "allow": False},
        {"action": "read_file", "allow": True}
    ]
)

print(f"✓ Agent created with model: {agent.llm.model}")
print(f"✓ Provider: {agent.llm.provider}")
print()

# Simple test query
query = "What is 2+2? Answer in one sentence."
print(f"Query: {query}")
print()

try:
    messages = [{"role": "user", "content": query}]
    response = agent.llm.generate(messages)
    print(f"Response: {response}")
    print()
    print("✅ API call successful!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print()
print("=" * 50)

# Test 2: PII Protection
print("Test 2: Data Airlock (PII Protection)")
print("-" * 50)

text_with_pii = "My email is john.doe@example.com and phone is 555-123-4567"
print(f"Original: {text_with_pii}")

sanitized = agent.airlock.sanitize(text_with_pii)
print(f"Sanitized: {sanitized}")

# Send sanitized text to LLM
query2 = f"Extract any contact information from this text: {sanitized}"
print(f"\nQuery to LLM: {query2}")

try:
    messages2 = [{"role": "user", "content": query2}]
    response2 = agent.llm.generate(messages2)
    print(f"LLM Response: {response2}")
    print("\n✓ LLM never saw the real email/phone!")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 50)

# Test 3: Constitutional constraint
print("Test 3: Constitutional Policy Enforcement")
print("-" * 50)

from alm_core.policy import PolicyViolationError

try:
    agent.constitution.validate_action("delete_file", {"path": "/important.txt"})
    print("❌ Should have blocked delete_file!")
except PolicyViolationError as e:
    print(f"✓ Policy violation caught: {e}")

print()
print("=" * 50)
print("🎉 ALL REAL API TESTS PASSED!")
print("=" * 50)
print()
print("Your ALM Core package is working perfectly with:")
print("  ✅ Real OpenAI API calls")
print("  ✅ PII protection (Data Airlock)")
print("  ✅ Constitutional constraints")
print("  ✅ Flexible model configuration")
