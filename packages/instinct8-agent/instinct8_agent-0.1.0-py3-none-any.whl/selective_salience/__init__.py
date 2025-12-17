"""
Selective Salience Compression

A compression strategy for long-running LLM agents that preserves goal-critical
information by using model-judged salience extraction.

Usage:
    from selective_salience import SelectiveSalienceCompressor, Instinct8Agent
    
    # Use as a compressor
    compressor = SelectiveSalienceCompressor()
    compressor.initialize(
        original_goal="Research async frameworks and recommend one",
        constraints=["Budget max $10K", "Timeline 2 weeks"]
    )
    compressed = compressor.compress(context, trigger_point=10)
    
    # Or use as a coding agent
    agent = Instinct8Agent()
    agent.initialize(goal="Build FastAPI app", constraints=["Use JWT"])
    agent.ingest_turn({"role": "user", "content": "Create endpoint"})
"""

from .compressor import SelectiveSalienceCompressor
from .codex_integration import Instinct8Agent, create_instinct8_agent

__version__ = "0.1.0"
__all__ = ["SelectiveSalienceCompressor", "Instinct8Agent", "create_instinct8_agent"]
