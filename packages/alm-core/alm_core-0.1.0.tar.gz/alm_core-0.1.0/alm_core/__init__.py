"""
ALM Core - Agent Language Model
A deterministic, policy-driven architecture for robust AI agents.
"""

from .agent import AgentLanguageModel, OmniAgent
from .controller import ALMController
from .memory import DataAirlock, DualMemory
from .policy import Constitution, PolicyViolationError
from .visualizer import ExecutionVisualizer
from .research import DeepResearcher

__version__ = "0.1.0"
__all__ = [
    "AgentLanguageModel",
    "OmniAgent",
    "ALMController",
    "DataAirlock",
    "DualMemory",
    "Constitution",
    "PolicyViolationError",
    "ExecutionVisualizer",
    "DeepResearcher",
]
