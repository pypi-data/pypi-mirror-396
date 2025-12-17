"""
Research Test - Multi-step deep research with memory
"""
import os
from alm_core import AgentLanguageModel

# Check for API key
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY environment variable not set")
    exit(1)

print("🔬 ALM Core - Deep Research Test")
print("=" * 70)
print()

# Initialize agent
agent = AgentLanguageModel(
    api_key=api_key,
    llm_provider="openai",
    model="gpt-3.5-turbo"
)

print(f"✓ Agent initialized: {agent.llm.model}")
print()

# Research Topic
topic = "Fiserv"
print(f"Research Topic: {topic}")
print("=" * 70)
print()

# Step 1: Initial Question
print("Step 1: What is Fiserv?")
print("-" * 70)
question1 = "What is Fiserv and what does the company do? Answer in 2-3 sentences."
messages = [{"role": "user", "content": question1}]
response1 = agent.llm.generate(messages)
print(f"Q: {question1}")
print(f"A: {response1}")
print()

# Store in memory
agent.memory.add_episode("user", question1)
agent.memory.add_episode("assistant", response1, {"type": "research", "topic": topic})
print("✓ Stored in episodic memory")
print()

# Step 2: Follow-up Question
print("Step 2: What are their products?")
print("-" * 70)
question2 = "What are Fiserv's main products and services? List 3-4 key offerings."
messages = agent.memory.get_context_window(sanitize=False)  # Get conversation history
messages.append({"role": "user", "content": question2})
response2 = agent.llm.generate(messages)
print(f"Q: {question2}")
print(f"A: {response2}")
print()

# Store in memory
agent.memory.add_episode("user", question2)
agent.memory.add_episode("assistant", response2, {"type": "research", "topic": topic})
print("✓ Stored in episodic memory")
print()

# Step 3: Competitive Analysis
print("Step 3: Who are the competitors?")
print("-" * 70)
question3 = "Who are Fiserv's main competitors in the fintech space?"
messages = agent.memory.get_context_window(sanitize=False)
messages.append({"role": "user", "content": question3})
response3 = agent.llm.generate(messages)
print(f"Q: {question3}")
print(f"A: {response3}")
print()

# Store in memory
agent.memory.add_episode("user", question3)
agent.memory.add_episode("assistant", response3, {"type": "research", "topic": topic})
print("✓ Stored in episodic memory")
print()

# Consolidate to long-term memory
print("Step 4: Consolidating to Long-term Memory")
print("-" * 70)
summary = f"""
RESEARCH ON: {topic}

Q1: {question1}
A1: {response1}

Q2: {question2}
A2: {response2}

Q3: {question3}
A3: {response3}

Research completed with 3 levels of depth.
"""

agent.memory.add_to_long_term(f"research_{topic}", summary)
print("✓ Research consolidated to long-term memory")
print()

# Retrieve from long-term memory
print("Step 5: Retrieving Research")
print("-" * 70)
retrieved = agent.memory.recall_from_long_term(f"research_{topic}")
print(f"Retrieved: {retrieved[:300]}...")
print()

# Memory stats
print("Memory Statistics")
print("-" * 70)
stats = agent.memory.get_memory_stats()
for key, value in stats.items():
    print(f"  {key}: {value}")
print()

# Summary
print("=" * 70)
print("✅ DEEP RESEARCH TEST COMPLETED!")
print("=" * 70)
print()
print("Research Summary:")
print(f"  Topic: {topic}")
print(f"  Questions explored: 3")
print(f"  Depth levels: 3")
print(f"  Memory episodes: {stats['working_memory_size']}")
print(f"  Long-term entries: {stats['long_term_memory_size']}")
print()
print("Questions Asked:")
print(f"  1. {question1}")
print(f"  2. {question2}")
print(f"  3. {question3}")
print()
print("Demonstrated Features:")
print("  ✅ Multi-step research with context")
print("  ✅ Episodic memory (conversation history)")
print("  ✅ Long-term memory (knowledge consolidation)")
print("  ✅ Memory retrieval")
print("  ✅ Context-aware follow-up questions")
