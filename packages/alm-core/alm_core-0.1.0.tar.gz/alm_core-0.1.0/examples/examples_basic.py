"""
Example usage of ALM Core
"""

import os
from alm_core import AgentLanguageModel, OmniAgent


def example_1_basic_usage():
    """Basic usage with PII protection."""
    print("\n" + "="*60)
    print("Example 1: Basic Usage with PII Protection")
    print("="*60 + "\n")
    
    # Initialize basic agent
    agent = AgentLanguageModel(
        openai_key=os.environ.get("OPENAI_API_KEY"),
        rules=[
            {"action": "delete_db", "allow": False}
        ]
    )
    
    # Process request with PII
    # The email is automatically sanitized before going to OpenAI
    response = agent.process(
        "My email is john.doe@company.com. "
        "Can you create a professional summary?"
    )
    
    print(f"Response: {response}")
    print(f"\nMemory Stats: {agent.get_memory_stats()}")


def example_2_policy_enforcement():
    """Demonstrate policy enforcement."""
    print("\n" + "="*60)
    print("Example 2: Constitutional Policy Enforcement")
    print("="*60 + "\n")
    
    from alm_core.policy import PolicyViolationError
    
    # Define strict rules
    rules = [
        {"action": "delete_db", "allow": False},
        {"action": "file_write", "allowed_paths": ["/tmp"]},
        {"action": "web_request", "forbidden_domains": ["malicious.com"]}
    ]
    
    agent = AgentLanguageModel(
        openai_key=os.environ.get("OPENAI_API_KEY"),
        rules=rules
    )
    
    # Try to perform restricted action
    print("Attempting restricted action...")
    try:
        agent.controller.constitution.validate_action("delete_db", {})
        print("❌ Action should have been blocked!")
    except PolicyViolationError as e:
        print(f"✅ Action blocked as expected: {e}")
    
    # Try allowed action
    print("\nAttempting allowed action...")
    try:
        agent.controller.constitution.validate_action(
            "file_write",
            {"path": "/tmp/test.txt"}
        )
        print("✅ Action allowed")
    except PolicyViolationError as e:
        print(f"❌ Unexpected block: {e}")


def example_3_custom_tools():
    """Add custom tools to the agent."""
    print("\n" + "="*60)
    print("Example 3: Custom Tool Integration")
    print("="*60 + "\n")
    
    agent = AgentLanguageModel(
        openai_key=os.environ.get("OPENAI_API_KEY")
    )
    
    # Define custom tool
    def calculate_profit(revenue: float, costs: float) -> str:
        profit = revenue - costs
        margin = (profit / revenue * 100) if revenue > 0 else 0
        return f"Profit: ${profit:,.2f} (Margin: {margin:.1f}%)"
    
    # Register tool
    agent.add_tool("calculate_profit", calculate_profit)
    
    print("Custom tool 'calculate_profit' registered")
    print(f"Available tools: {list(agent.controller.tools.keys())}")


def example_4_omniagent():
    """Full-featured OmniAgent with all capabilities."""
    print("\n" + "="*60)
    print("Example 4: OmniAgent with Full Capabilities")
    print("="*60 + "\n")
    
    config = {
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "provider": "openai",
        "model": "gpt-4",
        "rules": [
            {"action": "delete_db", "allow": False}
        ],
        "headless": True  # Run browser in headless mode
    }
    
    with OmniAgent(config) as agent:
        print("OmniAgent initialized with:")
        print(f"  - Browser: {'Headless' if config['headless'] else 'Visual'}")
        print(f"  - Desktop Controller: Active")
        print(f"  - Research Engine: Ready")
        print(f"  - Visualizer: Active")
        
        # Get stats
        stats = agent.get_stats()
        print(f"\nAgent Stats: {stats}")


def example_5_deep_research():
    """Demonstrate deep research capability."""
    print("\n" + "="*60)
    print("Example 5: Deep Research Engine")
    print("="*60 + "\n")
    
    config = {
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "provider": "openai",
        "model": "gpt-4",
    }
    
    with OmniAgent(config) as agent:
        print("Starting deep research on 'Agent Language Models'...")
        print("This will:")
        print("  1. Search the main topic")
        print("  2. Identify subtopics")
        print("  3. Recursively explore for 2 minutes")
        print("  4. Generate a knowledge graph")
        print("  5. Create a visual map\n")
        
        # Conduct research (simplified for example)
        # In real use, this would search the web
        print("Note: This example uses simulated search results")
        print("For real web research, integrate with browser tools")
        
        print("\n✅ Research complete. Would generate:")
        print("   - research_map_agent_language_models.png")
        print("   - knowledge_graph.json")


def example_6_memory_management():
    """Demonstrate memory system."""
    print("\n" + "="*60)
    print("Example 6: Memory Management")
    print("="*60 + "\n")
    
    from alm_core import DualMemory, DataAirlock
    
    memory = DualMemory()
    
    # Add episodes to working memory
    print("Adding conversation to working memory...")
    memory.add_episode("user", "My name is John and I live in New York")
    memory.add_episode("assistant", "Nice to meet you, John!")
    memory.add_episode("user", "What's my name?")
    
    # Store in long-term memory
    print("Storing fact in long-term memory...")
    memory.add_to_long_term("user_name", "John")
    memory.add_to_long_term("user_location", "New York")
    
    # Retrieve
    print("\nRetrieving from long-term memory:")
    print(f"  Name: {memory.recall_from_long_term('user_name')}")
    print(f"  Location: {memory.recall_from_long_term('user_location')}")
    
    # Get stats
    stats = memory.get_memory_stats()
    print(f"\nMemory Stats:")
    print(f"  Working memory: {stats['working_memory_size']} messages")
    print(f"  Long-term memory: {stats['long_term_memory_size']} entries")
    print(f"  PII tokens: {stats['pii_tokens_stored']}")


def example_7_visualization():
    """Demonstrate execution visualization."""
    print("\n" + "="*60)
    print("Example 7: Execution Visualization")
    print("="*60 + "\n")
    
    from alm_core import ExecutionVisualizer
    
    visualizer = ExecutionVisualizer()
    
    # Build execution graph
    print("Building execution graph...")
    root = visualizer.add_step(None, "task", "Research AI Safety", status="in_progress")
    
    step1 = visualizer.add_step(root, "search", "Search academic papers", status="success")
    step2 = visualizer.add_step(root, "search", "Search industry reports", status="success")
    
    substep1 = visualizer.add_step(step1, "analysis", "Analyze paper 1", status="success")
    substep2 = visualizer.add_step(step1, "analysis", "Analyze paper 2", status="failed")
    
    visualizer.update_status(root, "success", result="Research complete")
    
    # Get stats
    stats = visualizer.get_stats()
    print(f"\nExecution Stats:")
    print(f"  Total steps: {stats['total_steps']}")
    print(f"  Max depth: {stats['max_depth']}")
    print(f"  Status breakdown: {stats['status_breakdown']}")
    
    # Export
    print("\n✅ Would export to: execution_map.png")
    
    # Show Mermaid diagram
    print("\nMermaid Diagram:")
    print(visualizer.export_mermaid())


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("ALM Core - Usage Examples")
    print("="*60)
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not set")
        print("Some examples will be skipped")
        print("Set it with: export OPENAI_API_KEY='sk-...'")
    
    # Run examples
    try:
        example_1_basic_usage()
    except Exception as e:
        print(f"Example 1 skipped: {e}")
    
    example_2_policy_enforcement()
    example_3_custom_tools()
    
    try:
        example_4_omniagent()
    except Exception as e:
        print(f"Example 4 skipped: {e}")
    
    example_5_deep_research()
    example_6_memory_management()
    example_7_visualization()
    
    print("\n" + "="*60)
    print("Examples Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
