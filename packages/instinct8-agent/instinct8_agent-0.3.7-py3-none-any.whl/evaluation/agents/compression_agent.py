"""
Compression Agent Adapter

This module wraps the existing MockAgent to conform to the BaseAgent interface.
"""

from typing import Any, Dict, List, Optional

from strategies import CompressionStrategy

from .base import AgentConfig, BaseAgent


class CompressionAgent(BaseAgent):
    """
    Adapter wrapping the existing MockAgent for the unified interface.

    This agent uses a CompressionStrategy to manage context and performs
    compression at designated trigger points.
    """

    def __init__(self, config: AgentConfig, strategy: CompressionStrategy):
        """
        Initialize the compression agent.

        Args:
            config: Agent configuration
            strategy: The compression strategy to use
        """
        # Import MockAgent here to avoid circular imports
        from evaluation.harness import MockAgent

        self._config = config
        self._strategy = strategy
        self._mock_agent = MockAgent(
            strategy=strategy,
            system_prompt=config.system_prompt,
            original_goal=config.original_goal,
            constraints=config.constraints,
            model=config.model,
        )

    def ingest_turn(self, turn: Dict[str, Any]) -> None:
        """Add a turn to the agent's context."""
        # Convert to expected format if needed
        formatted_turn = {
            "id": turn.get("id", turn.get("turn_id", 0)),
            "role": turn.get("role", "user"),
            "content": turn.get("content", turn.get("text", "")),
            "is_compression_point": turn.get("is_compression_point", False),
            "tool_call": turn.get("tool_call"),
        }
        self._mock_agent.add_turn(formatted_turn)

    def answer_question(
        self,
        question: str,
        category: Optional[int] = None,
        reference_answer: Optional[str] = None,
    ) -> str:
        """
        Answer a question based on current context.

        Args:
            question: The question to answer
            category: Ignored for compression agent
            reference_answer: Ignored for compression agent

        Returns:
            The agent's response
        """
        return self._mock_agent.call(question)

    def get_context_size(self) -> int:
        """Get approximate token count of current context."""
        return self._mock_agent.get_token_count()

    def compress(self, trigger_point: Optional[int] = None) -> None:
        """Compress the context using the configured strategy."""
        self._mock_agent.compress(trigger_point or 0)

    def reset(self) -> None:
        """Reset the agent for a new evaluation sample."""
        self._mock_agent.context = []
        self._mock_agent.total_tokens = 0
        self._strategy.initialize(
            self._config.original_goal,
            self._config.constraints,
        )

    def initialize_goal(self, goal: str, constraints: List[str]) -> None:
        """Initialize goal and constraints for the strategy."""
        self._config.original_goal = goal
        self._config.constraints = constraints
        self._mock_agent.original_goal = goal
        self._mock_agent.constraints = constraints
        self._strategy.initialize(goal, constraints)

    @property
    def name(self) -> str:
        """Return human-readable agent name."""
        return f"CompressionAgent({self._strategy.name()})"

    @property
    def strategy(self) -> CompressionStrategy:
        """Access the underlying compression strategy."""
        return self._strategy

    @property
    def context(self) -> List[Dict[str, Any]]:
        """Access the current context."""
        return self._mock_agent.context
