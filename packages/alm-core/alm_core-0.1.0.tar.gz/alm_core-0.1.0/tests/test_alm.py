"""
Test suite for ALM Core
"""

import pytest
from alm_core import (
    AgentLanguageModel,
    Constitution,
    PolicyViolationError,
    DataAirlock,
    DualMemory,
    ExecutionVisualizer,
)


class TestConstitution:
    """Test the Constitutional Policy Engine."""
    
    def test_allow_action(self):
        """Test that allowed actions pass validation."""
        rules = [{"action": "search", "allow": True}]
        constitution = Constitution(rules)
        
        # Should not raise
        assert constitution.validate_action("search", {}) == True
    
    def test_deny_action(self):
        """Test that denied actions are blocked."""
        rules = [{"action": "delete_db", "allow": False}]
        constitution = Constitution(rules)
        
        with pytest.raises(PolicyViolationError) as exc_info:
            constitution.validate_action("delete_db", {})
        
        assert "prohibited" in str(exc_info.value).lower()
    
    def test_forbidden_params(self):
        """Test parameter-level restrictions."""
        rules = [{
            "action": "email",
            "forbidden_params": {"domain": "gmail.com"}
        }]
        constitution = Constitution(rules)
        
        # Should block
        with pytest.raises(PolicyViolationError):
            constitution.validate_action("email", {"domain": "gmail.com"})
        
        # Should allow
        assert constitution.validate_action("email", {"domain": "company.com"}) == True
    
    def test_allowed_paths(self):
        """Test path restrictions for file operations."""
        rules = [{
            "action": "file_write",
            "allowed_paths": ["/safe/dir"]
        }]
        constitution = Constitution(rules)
        
        # Should allow
        assert constitution.validate_action(
            "file_write",
            {"path": "/safe/dir/file.txt"}
        ) == True
        
        # Should block
        with pytest.raises(PolicyViolationError):
            constitution.validate_action(
                "file_write",
                {"path": "/etc/passwd"}
            )
    
    def test_add_remove_rules(self):
        """Test dynamic rule management."""
        constitution = Constitution([])
        
        # Add rule
        constitution.add_rule({"action": "test", "allow": False})
        assert len(constitution.rules) == 1
        
        # Remove rule
        constitution.remove_rule("test")
        assert len(constitution.rules) == 0


class TestDataAirlock:
    """Test the Data Airlock PII protection."""
    
    def test_email_sanitization(self):
        """Test email PII sanitization."""
        airlock = DataAirlock()
        
        text = "Contact me at john@example.com"
        sanitized = airlock.sanitize(text)
        
        assert "john@example.com" not in sanitized
        assert "<EMAIL_" in sanitized
    
    def test_phone_sanitization(self):
        """Test phone number sanitization."""
        airlock = DataAirlock()
        
        text = "Call me at 555-123-4567"
        sanitized = airlock.sanitize(text)
        
        assert "555-123-4567" not in sanitized
        assert "<PHONE_" in sanitized
    
    def test_ssn_sanitization(self):
        """Test SSN sanitization."""
        airlock = DataAirlock()
        
        text = "My SSN is 123-45-6789"
        sanitized = airlock.sanitize(text)
        
        assert "123-45-6789" not in sanitized
        assert "<SSN_" in sanitized
    
    def test_rehydration(self):
        """Test PII rehydration after sanitization."""
        airlock = DataAirlock()
        
        original = "Email: john@example.com, Phone: 555-1234"
        sanitized = airlock.sanitize(original)
        rehydrated = airlock.rehydrate(sanitized)
        
        # Should contain original PII after rehydration
        assert "john@example.com" in rehydrated
        # Tokens should be replaced
        assert "<EMAIL_" not in rehydrated
    
    def test_custom_patterns(self):
        """Test custom PII patterns."""
        custom_patterns = {
            "api_key": r"sk-[a-zA-Z0-9]{48}"
        }
        airlock = DataAirlock(custom_patterns)
        
        text = "My key is sk-abc123def456abc123def456abc123def456abc123def456"
        sanitized = airlock.sanitize(text)
        
        assert "sk-abc" not in sanitized
        assert "<API_KEY_" in sanitized


class TestDualMemory:
    """Test the Dual Memory system."""
    
    def test_working_memory(self):
        """Test episodic memory operations."""
        memory = DualMemory()
        
        memory.add_episode("user", "Hello")
        memory.add_episode("assistant", "Hi there")
        
        context = memory.get_context_window(sanitize=False)
        assert len(context) == 2
        assert context[0]["content"] == "Hello"
    
    def test_pii_sanitization_in_context(self):
        """Test that context window sanitizes PII."""
        memory = DualMemory()
        
        memory.add_episode("user", "My email is test@example.com")
        
        # Sanitized context
        context = memory.get_context_window(sanitize=True)
        assert "test@example.com" not in context[0]["content"]
        assert "<EMAIL_" in context[0]["content"]
        
        # Raw context (internal use)
        raw_context = memory.get_context_window(sanitize=False)
        assert "test@example.com" in raw_context[0]["content"]
    
    def test_long_term_memory(self):
        """Test semantic memory operations."""
        memory = DualMemory()
        
        memory.add_to_long_term("user_preference", {"theme": "dark"})
        
        retrieved = memory.recall_from_long_term("user_preference")
        assert retrieved == {"theme": "dark"}
        
        # Non-existent key
        assert memory.recall_from_long_term("nonexistent") is None
    
    def test_memory_overflow(self):
        """Test sliding window for working memory."""
        memory = DualMemory()
        memory.max_working_memory_size = 5
        
        # Add more than max
        for i in range(10):
            memory.add_episode("user", f"Message {i}")
        
        # Should only keep recent messages (plus first one)
        assert len(memory.working_memory) == 5


class TestExecutionVisualizer:
    """Test the execution visualizer."""
    
    def test_add_step(self):
        """Test adding steps to the execution graph."""
        visualizer = ExecutionVisualizer()
        
        root = visualizer.add_step(None, "task", "Main task")
        child = visualizer.add_step(root, "action", "Sub-action")
        
        assert visualizer.graph.number_of_nodes() == 2
        assert visualizer.graph.has_edge(root, child)
    
    def test_update_status(self):
        """Test updating node status."""
        visualizer = ExecutionVisualizer()
        
        node = visualizer.add_step(None, "task", "Test", status="pending")
        visualizer.update_status(node, "success", result="Done")
        
        assert visualizer.graph.nodes[node]["status"] == "success"
        assert visualizer.graph.nodes[node]["result"] == "Done"
    
    def test_stats(self):
        """Test execution statistics."""
        visualizer = ExecutionVisualizer()
        
        root = visualizer.add_step(None, "task", "Root")
        visualizer.add_step(root, "action", "Action 1", status="success")
        visualizer.add_step(root, "action", "Action 2", status="failed")
        
        stats = visualizer.get_stats()
        assert stats["total_steps"] == 3
        assert stats["status_breakdown"]["success"] == 1
        assert stats["status_breakdown"]["failed"] == 1
    
    def test_export_mermaid(self):
        """Test Mermaid diagram export."""
        visualizer = ExecutionVisualizer()
        
        root = visualizer.add_step(None, "task", "Root")
        visualizer.add_step(root, "action", "Action")
        
        mermaid = visualizer.export_mermaid()
        assert "graph TD" in mermaid
        assert "step_0" in mermaid


class TestAgentLanguageModel:
    """Test the basic ALM agent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        rules = [{"action": "test", "allow": True}]
        
        # Should work without API key for basic setup
        agent = AgentLanguageModel(
            openai_key=None,
            rules=rules,
            llm_provider="local"
        )
        
        assert agent.constitution is not None
        assert agent.memory is not None
        assert agent.controller is not None
    
    def test_add_rule(self):
        """Test adding rules dynamically."""
        agent = AgentLanguageModel(openai_key=None, llm_provider="local")
        
        agent.add_rule({"action": "test", "allow": False})
        assert len(agent.constitution.rules) == 1
    
    def test_add_tool(self):
        """Test registering custom tools."""
        agent = AgentLanguageModel(openai_key=None, llm_provider="local")
        
        def custom_tool(param: str) -> str:
            return f"Executed with {param}"
        
        agent.add_tool("custom", custom_tool)
        assert "custom" in agent.controller.tools


# Integration test (requires API key)
@pytest.mark.skip(reason="Requires API key and makes real API calls")
class TestIntegration:
    """Integration tests with real LLM."""
    
    def test_end_to_end(self):
        """Test complete agent workflow."""
        import os
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("No API key available")
        
        agent = AgentLanguageModel(
            openai_key=api_key,
            rules=[{"action": "delete_db", "allow": False}]
        )
        
        response = agent.process("What is 2+2?")
        assert response is not None
        assert len(response) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
