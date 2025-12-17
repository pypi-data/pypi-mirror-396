"""
Instinct8 Agent - Selective Salience Compression

A compression strategy for long-running LLM agents that preserves goal-critical
information by using model-judged salience extraction.

Usage:
    from selective_salience import Instinct8Agent
    
    # Use as a coding agent
    agent = Instinct8Agent()
    agent.initialize(goal="Build FastAPI app", constraints=["Use JWT"])
    agent.ingest_turn({"role": "user", "content": "Create endpoint"})
    response = agent.answer_question("What are we building?")
"""

from .compressor import SelectiveSalienceCompressor
from .codex_integration import Instinct8Agent, create_instinct8_agent

__version__ = "0.1.0"
__all__ = ["SelectiveSalienceCompressor", "Instinct8Agent", "create_instinct8_agent"]
