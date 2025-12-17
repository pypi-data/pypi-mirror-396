"""
ALM Controller - The Deterministic Brain
Implements the BDI (Belief-Desire-Intention) state machine.
"""

from typing import Dict, Any, List, Optional, Callable
import json
from datetime import datetime

from .policy import Constitution, PolicyViolationError
from .memory import DualMemory, DataAirlock
from .llm_client import LLMClient


class ALMController:
    """
    The Deterministic Controller is the core of ALM.
    
    Unlike standard agents where the LLM controls execution flow,
    here the Controller is in charge. The LLM is merely a cognitive tool.
    
    This implements the BDI (Belief-Desire-Intention) cycle:
    - Beliefs: Current world state
    - Desires: Goal stack
    - Intentions: Current plan
    """
    
    def __init__(
        self,
        constitution: Constitution,
        llm: LLMClient,
        memory: Optional[DualMemory] = None,
        tools: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the ALM Controller.
        
        Args:
            constitution: Policy enforcement engine
            llm: LLM client for cognitive operations
            memory: Memory system (created if not provided)
            tools: Dictionary of available tools
        """
        self.constitution = constitution
        self.llm = llm
        self.memory = memory or DualMemory()
        self.tools = tools or {}
        
        # BDI State
        self.state = {
            "beliefs": {},      # Current world state
            "desires": [],      # Goal stack
            "intentions": []    # Current plan
        }
        
        # Execution history
        self.execution_log: List[Dict[str, Any]] = []
        
        # Register built-in tools
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register standard tools."""
        self.tools.update({
            "memory_store": self._tool_memory_store,
            "memory_recall": self._tool_memory_recall,
        })
    
    def _tool_memory_store(self, key: str, value: Any) -> str:
        """Store information in long-term memory."""
        self.memory.add_to_long_term(key, value)
        return f"Stored '{key}' in long-term memory"
    
    def _tool_memory_recall(self, key: str) -> Any:
        """Recall information from long-term memory."""
        value = self.memory.recall_from_long_term(key)
        return value if value is not None else f"No memory found for '{key}'"
    
    def set_goal(self, goal: str, priority: int = 0):
        """
        Add a new goal to the desire stack.
        
        Args:
            goal: Description of the goal
            priority: Priority level (higher = more urgent)
        """
        self.state["desires"].append({
            "goal": goal,
            "priority": priority,
            "created_at": datetime.now().isoformat()
        })
        
        # Sort by priority
        self.state["desires"].sort(key=lambda x: x["priority"], reverse=True)
        
        # Add to memory
        self.memory.add_episode("user", goal, {"type": "goal"})
    
    def update_belief(self, key: str, value: Any):
        """
        Update the agent's belief about the world state.
        
        Args:
            key: Belief identifier
            value: Belief value
        """
        self.state["beliefs"][key] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }
    
    def run_cycle(self, max_steps: int = 10) -> Dict[str, Any]:
        """
        Execute one complete BDI cycle: Observe -> Orient -> Decide -> Act.
        
        Args:
            max_steps: Maximum number of action steps to take
            
        Returns:
            Result summary
        """
        if not self.state["desires"]:
            return {"status": "idle", "message": "No goals pending"}
        
        current_goal = self.state["desires"][0]["goal"]
        results = []
        
        for step in range(max_steps):
            # 1. OBSERVE: Get current state
            context = self.memory.get_context_window(sanitize=True)
            
            # 2. ORIENT: Ask LLM for next action
            action = self._decide_next_action(current_goal, context)
            
            if action is None or action.get("type") == "goal_complete":
                # Goal achieved
                self.state["desires"].pop(0)
                results.append({"step": step, "status": "goal_complete"})
                break
            
            # 3. DECIDE: Validate with Constitution
            try:
                self.constitution.validate_action(
                    action.get("tool", "unknown"),
                    action.get("params", {})
                )
            except PolicyViolationError as e:
                # Log violation and ask LLM to reconsider
                self.memory.add_episode(
                    "system",
                    f"Action blocked by policy: {str(e)}",
                    {"type": "policy_violation"}
                )
                results.append({
                    "step": step,
                    "status": "policy_violation",
                    "error": str(e)
                })
                continue
            
            # 4. ACT: Execute the action
            result = self._execute_action(action)
            results.append({
                "step": step,
                "action": action,
                "result": result,
                "status": "success" if result.get("success") else "failure"
            })
            
            # Update memory with result
            self.memory.add_episode(
                "assistant",
                f"Executed {action.get('tool')}: {result.get('output', 'No output')}",
                {"action": action, "result": result}
            )
            
            # Check if goal is complete
            if result.get("goal_complete"):
                self.state["desires"].pop(0)
                break
        
        return {
            "status": "complete" if not self.state["desires"] else "in_progress",
            "steps_taken": len(results),
            "results": results
        }
    
    def _decide_next_action(
        self,
        goal: str,
        context: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Use LLM to decide the next action.
        
        Returns structured action plan.
        """
        # Create schema for structured output
        action_schema = {
            "type": "object",
            "properties": {
                "tool": {"type": "string", "description": "Tool name to use"},
                "params": {"type": "object", "description": "Parameters for the tool"},
                "reasoning": {"type": "string", "description": "Why this action"},
                "type": {"type": "string", "enum": ["action", "goal_complete"]}
            },
            "required": ["tool", "params", "reasoning", "type"]
        }
        
        # Build decision prompt
        available_tools = list(self.tools.keys())
        decision_prompt = f"""Current Goal: {goal}

Available Tools: {', '.join(available_tools)}

Based on the conversation history and current goal, determine the NEXT SINGLE ACTION to take.

If the goal is already complete, respond with type: "goal_complete".
Otherwise, specify which tool to use and its parameters."""
        
        try:
            action = self.llm.generate_structured(
                messages=context + [{"role": "user", "content": decision_prompt}],
                schema=action_schema,
                system_prompt="You are a precise action planner. Output only valid JSON."
            )
            
            self._log_execution("decision", action)
            return action
            
        except Exception as e:
            # Fallback: Let LLM know it failed
            self.memory.add_episode(
                "system",
                f"Failed to parse LLM decision: {str(e)}",
                {"type": "error"}
            )
            return None
    
    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a validated action using the appropriate tool.
        
        Args:
            action: Action specification
            
        Returns:
            Execution result
        """
        tool_name = action.get("tool")
        params = action.get("params", {})
        
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "output": None
            }
        
        try:
            tool = self.tools[tool_name]
            
            # Execute tool (can be function or object with __call__)
            if callable(tool):
                output = tool(**params)
            else:
                output = tool.execute(**params)
            
            result = {
                "success": True,
                "output": output,
                "tool": tool_name,
                "goal_complete": False  # Tool can set this to True
            }
            
            self._log_execution("action", result)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": None,
                "tool": tool_name
            }
    
    def _log_execution(self, event_type: str, data: Any):
        """Log execution events for debugging/audit."""
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        })
    
    def register_tool(self, name: str, tool: Callable):
        """
        Register a new tool.
        
        Args:
            name: Tool identifier
            tool: Callable that implements the tool
        """
        self.tools[name] = tool
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get current BDI state summary."""
        return {
            "active_goals": len(self.state["desires"]),
            "beliefs": list(self.state["beliefs"].keys()),
            "memory_stats": self.memory.get_memory_stats(),
            "execution_steps": len(self.execution_log)
        }
    
    def execute_task(self, task_description: str) -> str:
        """
        High-level task execution (used by other modules).
        
        Args:
            task_description: Natural language task
            
        Returns:
            Task result as string
        """
        self.set_goal(task_description)
        result = self.run_cycle()
        
        # Extract final output
        if result["results"]:
            last_result = result["results"][-1]
            return last_result.get("result", {}).get("output", "Task completed")
        
        return "No action taken"
    
    def run_interactive_session(self, goal: str, context: Dict[str, Any]) -> bool:
        """
        Run an interactive session with external context.
        
        Args:
            goal: Session goal
            context: External context (e.g., browser DOM)
            
        Returns:
            Success status
        """
        # Add context to beliefs
        self.update_belief("external_context", context)
        
        # Set goal and run
        self.set_goal(goal)
        result = self.run_cycle(max_steps=20)
        
        return result["status"] == "complete"
