"""
Agent Language Model - Main Orchestrator
High-level agent interfaces for different use cases.
"""

import os
from typing import Dict, Any, Optional, List
from .controller import ALMController
from .memory import DualMemory, DataAirlock
from .policy import Constitution
from .llm_client import LLMClient
from .visualizer import ExecutionVisualizer
from .research import DeepResearcher
from .tools.browser import SecureBrowser
from .tools.desktop import DesktopController


class AgentLanguageModel:
    """
    Basic ALM agent for simple tasks.
    
    This is the simplest interface - suitable for:
    - Text processing with PII protection
    - Policy-enforced task execution
    - Basic automation
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        rules: Optional[List[Dict[str, Any]]] = None,
        llm_provider: str = "openai",
        model: Optional[str] = None
    ):
        """
        Initialize a basic ALM agent.
        
        Args:
            api_key: LLM API key (reads from OPENAI_API_KEY or ANTHROPIC_API_KEY env var if not provided)
            rules: Constitutional rules
            llm_provider: LLM provider ('openai', 'anthropic', 'local')
            model: Model identifier (e.g., 'gpt-4', 'gpt-3.5-turbo', 'claude-3-opus-20240229')
                   If not provided, uses defaults based on provider
        """
        # Get API key from environment if not provided
        if api_key is None:
            if llm_provider == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
            elif llm_provider == "anthropic":
                api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        # Set default model based on provider if not specified
        if model is None:
            if llm_provider == "openai":
                model = os.environ.get("OPENAI_MODEL", "gpt-4")
            elif llm_provider == "anthropic":
                model = os.environ.get("ANTHROPIC_MODEL", "claude-3-opus-20240229")
            else:
                model = "default"
        
        # Initialize components
        self.airlock = DataAirlock()
        self.llm = LLMClient(
            provider=llm_provider,
            api_key=api_key,
            model=model
        )
        self.constitution = Constitution(rules or [])
        self.memory = DualMemory(airlock=self.airlock)
        self.controller = ALMController(
            constitution=self.constitution,
            llm=self.llm,
            memory=self.memory
        )
    
    def process(self, user_input: str) -> str:
        """
        Process a user request.
        
        Args:
            user_input: User's message or task
            
        Returns:
            Agent's response (with PII rehydrated)
        """
        # Set goal
        self.controller.set_goal(user_input)
        
        # Execute
        result = self.controller.run_cycle()
        
        # Extract response
        if result["results"]:
            last_result = result["results"][-1]
            response = last_result.get("result", {}).get("output", "Task completed")
        else:
            response = "No action was taken"
        
        # Rehydrate PII before returning to user
        final_response = self.airlock.rehydrate(str(response))
        
        return final_response
    
    def add_rule(self, rule: Dict[str, Any]):
        """Add a constitutional rule."""
        self.constitution.add_rule(rule)
    
    def add_tool(self, name: str, tool_function):
        """Register a custom tool."""
        self.controller.register_tool(name, tool_function)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        return self.memory.get_memory_stats()
    
    def clear_session(self):
        """Clear the current session."""
        self.memory.clear_working_memory()


class OmniAgent:
    """
    Full-featured ALM agent with all capabilities.
    
    Includes:
    - Web browsing
    - Desktop control
    - Deep research
    - Visual execution tracking
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the OmniAgent.
        
        Args:
            config: Configuration dictionary with:
                - api_key: LLM API key
                - provider: LLM provider
                - model: Model name
                - rules: Constitutional rules
                - headless: Browser headless mode
        """
        config = config or {}
        
        # Core components
        self.airlock = DataAirlock()
        self.visualizer = ExecutionVisualizer()
        
        # Get provider and API key
        provider = config.get('provider', os.environ.get('LLM_PROVIDER', 'openai'))
        api_key = config.get('api_key')
        
        # Get API key from environment if not in config
        if api_key is None:
            if provider == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
            elif provider == "anthropic":
                api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        # Get model from config or environment
        model = config.get('model')
        if model is None:
            if provider == "openai":
                model = os.environ.get("OPENAI_MODEL", "gpt-4")
            elif provider == "anthropic":
                model = os.environ.get("ANTHROPIC_MODEL", "claude-3-opus-20240229")
            else:
                model = "default"
        
        # LLM
        self.llm = LLMClient(
            provider=provider,
            api_key=api_key,
            model=model
        )
        
        # Policy
        self.constitution = Constitution(config.get('rules', []))
        
        # Memory
        self.memory = DualMemory(airlock=self.airlock)
        
        # Tools
        self.browser = SecureBrowser(
            airlock=self.airlock,
            headless=config.get('headless', False)
        )
        self.desktop = DesktopController()
        
        # Controller
        self.controller = ALMController(
            constitution=self.constitution,
            llm=self.llm,
            memory=self.memory,
            tools={
                "browser_navigate": self._tool_browser_navigate,
                "browser_interact": self._tool_browser_interact,
                "browser_get_content": self._tool_browser_get_content,
                "file_read": self._tool_file_read,
                "file_write": self._tool_file_write,
                "execute_command": self._tool_execute_command,
            }
        )
        
        # Research engine
        self.researcher = DeepResearcher(self.controller, self.visualizer)
    
    # Tool wrappers for controller
    def _tool_browser_navigate(self, url: str) -> str:
        """Navigate browser to URL."""
        if not self.browser.session_active:
            self.browser.start()
        result = self.browser.navigate(url)
        return f"Navigated to {result.get('url', url)}"
    
    def _tool_browser_interact(
        self,
        action: str,
        selector: str = None,
        value: str = None
    ) -> str:
        """Interact with browser element."""
        result = self.browser.interact(action, selector=selector, value=value)
        if result.get("success"):
            return f"Successfully {result.get('action', 'completed action')}"
        return f"Failed: {result.get('error', 'Unknown error')}"
    
    def _tool_browser_get_content(self) -> Dict[str, Any]:
        """Get sanitized page content."""
        return self.browser.get_sanitized_dom()
    
    def _tool_file_read(self, file_path: str) -> str:
        """Read a file."""
        result = self.desktop.read_file(file_path)
        if result.get("success"):
            return result.get("content", "")
        return f"Error: {result.get('error', 'Unknown error')}"
    
    def _tool_file_write(self, file_path: str, content: str) -> str:
        """Write to a file."""
        result = self.desktop.write_file(file_path, content)
        if result.get("success"):
            return f"Wrote {result.get('size', 0)} characters to {file_path}"
        return f"Error: {result.get('error', 'Unknown error')}"
    
    def _tool_execute_command(self, command: str) -> str:
        """Execute a shell command."""
        result = self.desktop.execute_command(command)
        if result.get("success"):
            return result.get("stdout", "Command executed successfully")
        return f"Error: {result.get('error', 'Unknown error')}\n{result.get('stderr', '')}"
    
    # High-level methods
    def login_to_service(self, service_name: str, url: str) -> bool:
        """
        Autonomous login to a web service.
        
        Args:
            service_name: Name of the service (for visualization)
            url: Login page URL
            
        Returns:
            Success status
        """
        # Visualize task
        root = self.visualizer.add_step(
            None,
            "task_root",
            f"Login to {service_name}",
            status="in_progress"
        )
        
        # Start browser
        step1 = self.visualizer.add_step(root, "action", "Starting browser")
        self.browser.start()
        self.visualizer.update_status(step1, "success")
        
        # Navigate
        step2 = self.visualizer.add_step(root, "action", f"Navigating to {url}")
        self.browser.navigate(url)
        self.visualizer.update_status(step2, "success")
        
        # Autonomous interaction
        step3 = self.visualizer.add_step(root, "action", "Analyzing login page")
        dom = self.browser.get_sanitized_dom()
        self.controller.update_belief("current_page", dom)
        self.visualizer.update_status(step3, "success")
        
        # Run interactive session
        success = self.controller.run_interactive_session(
            goal=f"Complete login to {service_name}",
            context=dom
        )
        
        # Finalize
        self.visualizer.update_status(
            root,
            "success" if success else "failed",
            result="Login complete" if success else "Login failed"
        )
        
        # Export visualization
        self.visualizer.export_graph(f"login_{service_name}.png")
        
        return success
    
    def deep_dive(
        self,
        topic: str,
        duration_minutes: int = 5,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Conduct deep research on a topic.
        
        Args:
            topic: Research topic
            duration_minutes: Research duration
            max_depth: Maximum recursion depth
            
        Returns:
            Research results
        """
        return self.researcher.conduct_research(
            topic,
            duration_minutes=duration_minutes,
            max_depth=max_depth
        )
    
    def execute_task(self, task_description: str) -> str:
        """
        Execute a general task.
        
        Args:
            task_description: Natural language task description
            
        Returns:
            Task result
        """
        # Visualize
        root = self.visualizer.add_step(
            None,
            "task",
            task_description,
            status="in_progress"
        )
        
        # Execute
        result = self.controller.execute_task(task_description)
        
        # Update visualization
        self.visualizer.update_status(root, "success", result=result)
        
        return result
    
    def add_rule(self, rule: Dict[str, Any]):
        """Add a constitutional rule."""
        self.constitution.add_rule(rule)
    
    def add_custom_tool(self, name: str, tool_function):
        """Register a custom tool."""
        self.controller.register_tool(name, tool_function)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive agent statistics."""
        return {
            "memory": self.memory.get_memory_stats(),
            "execution": self.visualizer.get_stats(),
            "research": self.researcher.get_research_stats(),
            "controller": self.controller.get_state_summary()
        }
    
    def export_session(self, filename_prefix: str = "session"):
        """
        Export complete session data.
        
        Args:
            filename_prefix: Prefix for output files
        """
        # Export memory
        import json
        
        session_data = self.memory.export_session()
        with open(f"{filename_prefix}_memory.json", 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Export visualization
        self.visualizer.export_graph(f"{filename_prefix}_execution.png")
        
        # Export knowledge graph if research was done
        if self.researcher.knowledge_graph:
            self.researcher.export_knowledge_graph(f"{filename_prefix}_knowledge.json")
        
        print(f"✅ Session exported with prefix: {filename_prefix}")
    
    def cleanup(self):
        """Clean up resources."""
        if self.browser.session_active:
            self.browser.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
