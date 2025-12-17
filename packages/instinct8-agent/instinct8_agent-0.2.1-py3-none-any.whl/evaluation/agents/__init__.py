"""
Agent Abstractions for Unified Evaluation

This module provides a unified interface for different agent types,
allowing both compression-based agents and memory-based agents to be
evaluated with the same harness.
"""

from .amem_agent import AMemAgent
from .base import AgentConfig, BaseAgent
from .codex_agent import CodexAgent, create_codex_agent
from .compression_agent import CompressionAgent

__all__ = [
    "BaseAgent",
    "AgentConfig",
    "CompressionAgent",
    "AMemAgent",
    "CodexAgent",
    "create_codex_agent",
]
