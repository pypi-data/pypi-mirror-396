"""
Instinct8 Agent - Selective Salience Compression

A compression strategy for long-running LLM agents that preserves goal-critical
information by using model-judged salience extraction.

Usage:
    from selective_salience import Instinct8Agent
    
    # Use as a coding agent (full Codex replacement)
    agent = Instinct8Agent()
    agent.initialize(goal="Build FastAPI app", constraints=["Use JWT"])
    response = agent.execute("create a login endpoint")
    # Now generates actual code!
"""

from .compressor import SelectiveSalienceCompressor
from .codex_integration import Instinct8Agent, create_instinct8_agent

__version__ = "0.4.1"
__all__ = ["SelectiveSalienceCompressor", "Instinct8Agent", "create_instinct8_agent"]
