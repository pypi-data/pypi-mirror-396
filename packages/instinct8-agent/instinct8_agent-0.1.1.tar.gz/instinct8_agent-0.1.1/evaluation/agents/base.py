"""
Base Agent Interface

This module defines the abstract base class for all agents in the
unified evaluation framework.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentConfig:
    """Configuration for agent initialization."""

    model: str = "claude-sonnet-4-20250514"
    backend: str = "anthropic"  # "anthropic", "openai", "ollama", "sglang"
    system_prompt: str = ""
    # Compression agent specific
    original_goal: str = ""
    constraints: List[str] = field(default_factory=list)
    # A-mem agent specific
    retrieve_k: int = 10
    temperature_c5: float = 0.5
    sglang_host: str = "http://localhost"
    sglang_port: int = 30000


class BaseAgent(ABC):
    """
    Unified agent interface for both compression-based and memory-based agents.

    All agent implementations must provide:
    1. A way to ingest conversation turns
    2. A way to answer questions given context
    3. Token/memory statistics
    4. Compression/consolidation capability
    5. Reset functionality for new evaluation samples

    This abstraction allows the UnifiedHarness to evaluate different agent
    architectures with the same evaluation pipeline.
    """

    @abstractmethod
    def ingest_turn(self, turn: Dict[str, Any]) -> None:
        """
        Ingest a single conversation turn into the agent's context/memory.

        Args:
            turn: Dictionary with at minimum:
                - 'content': str - the turn content
                - 'role': str - speaker role (user/assistant/system)
                - Optional: 'timestamp', 'speaker', 'id', etc.
        """
        pass

    @abstractmethod
    def answer_question(
        self,
        question: str,
        category: Optional[int] = None,
        reference_answer: Optional[str] = None,
    ) -> str:
        """
        Answer a question based on ingested context/memory.

        Args:
            question: The question to answer
            category: Optional question category (for A-mem style evaluation, 1-5)
            reference_answer: Optional reference for category-5 adversarial questions

        Returns:
            The agent's answer string
        """
        pass

    @abstractmethod
    def get_context_size(self) -> int:
        """
        Get current context/memory size metric.

        Returns:
            Token count for compression agents, memory note count for A-mem
        """
        pass

    @abstractmethod
    def compress(self, trigger_point: Optional[int] = None) -> None:
        """
        Trigger compression/consolidation.

        For compression agents: compress context using the strategy
        For memory agents: consolidate memories (or no-op if continuous)

        Args:
            trigger_point: Optional identifier for the compression point
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reset agent state for new evaluation sample.

        This should clear all context/memories and restore initial state.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return human-readable agent name."""
        pass

    def initialize_goal(self, goal: str, constraints: List[str]) -> None:
        """
        Initialize goal and constraints for compression-aware agents.

        Args:
            goal: The original goal statement
            constraints: List of constraints

        Note: This is optional and may be a no-op for memory-based agents.
        """
        pass
