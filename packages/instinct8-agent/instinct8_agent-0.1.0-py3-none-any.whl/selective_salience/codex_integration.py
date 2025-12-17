"""
Instinct8 Agent - Codex-style agent with Selective Salience Compression

This module provides the Instinct8Agent, a coding agent that uses Selective Salience
Compression to preserve goal-critical information in long-running conversations.
"""

from typing import Optional, List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .compressor import SelectiveSalienceCompressor
from evaluation.agents.codex_agent import CodexAgent, AgentConfig


class Instinct8Agent:
    """
    Instinct8 Agent - Coding agent with Selective Salience Compression
    
    A coding agent that uses Selective Salience Compression to preserve goal-critical
    information verbatim while compressing background context. Perfect for long-running
    coding tasks where goal coherence is critical.
    
    Example:
        >>> from selective_salience import Instinct8Agent
        >>> 
        >>> agent = Instinct8Agent()
        >>> agent.initialize(
        ...     goal="Build a FastAPI auth system",
        ...     constraints=["Use JWT", "Hash passwords"]
        ... )
        >>> 
        >>> # Use like a normal coding agent
        >>> agent.ingest_turn({"role": "user", "content": "Create login endpoint"})
        >>> response = agent.answer_question("What are we building?")
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        compaction_threshold: int = 80000,
        extraction_model: str = "gpt-4o",
        compression_model: str = "gpt-4o-mini",
    ):
        """
        Initialize Instinct8 agent with Selective Salience Compression.
        
        Args:
            model: Model for agent responses
            compaction_threshold: Token count at which to trigger compression
            extraction_model: Model for salience extraction
            compression_model: Model for background compression
        """
        # Create Selective Salience compressor
        self._compressor = SelectiveSalienceCompressor(
            extraction_model=extraction_model,
            compression_model=compression_model,
        )
        
        # Create a strategy adapter that wraps our compressor
        from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy
        strategy = SelectiveSalienceStrategy(
            extraction_model=extraction_model,
            compression_model=compression_model,
        )
        
        # Create underlying agent with our strategy
        config = AgentConfig(model=model)
        self._agent = CodexAgent(
            config=config,
            strategy=strategy,
            compaction_threshold=compaction_threshold,
        )
    
    def initialize(self, goal: str, constraints: List[str]) -> None:
        """
        Initialize the agent with goal and constraints.
        
        Args:
            goal: The task's original goal
            constraints: List of constraints
        """
        self._agent.initialize_goal(goal, constraints)
        self._compressor.initialize(goal, constraints)
    
    def ingest_turn(self, turn: Dict[str, Any]) -> None:
        """
        Add a turn to the conversation.
        
        Args:
            turn: Turn dict with "role" and "content" keys
        """
        self._agent.ingest_turn(turn)
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question using the current context.
        
        Args:
            question: The question to answer
        
        Returns:
            Agent's response
        """
        return self._agent.answer_question(question)
    
    def compress(self, trigger_point: Optional[int] = None) -> None:
        """
        Manually trigger compression.
        
        Args:
            trigger_point: Optional turn ID to compress up to
        """
        self._agent.compress(trigger_point)
    
    @property
    def salience_set(self) -> List[str]:
        """Get the current salience set."""
        return self._compressor.salience_set
    
    @property
    def context_length(self) -> int:
        """Get current context length in tokens."""
        return self._agent._total_tokens
    
    def reset(self) -> None:
        """Reset agent state."""
        self._agent.reset()
        self._compressor.reset()


def create_instinct8_agent(
    goal: str,
    constraints: List[str],
    model: str = "gpt-4o",
    compaction_threshold: int = 80000,
) -> Instinct8Agent:
    """
    Factory function to create an Instinct8 agent with Selective Salience Compression.
    
    Args:
        goal: The task's original goal
        constraints: List of constraints
        model: Model for agent responses
        compaction_threshold: Token count at which to trigger compression
    
    Returns:
        Configured Instinct8Agent instance
    
    Example:
        >>> agent = create_instinct8_agent(
        ...     goal="Build a FastAPI auth system",
        ...     constraints=["Use JWT", "Hash passwords"],
        ... )
        >>> agent.ingest_turn({"role": "user", "content": "Create login endpoint"})
    """
    agent = Instinct8Agent(
        model=model,
        compaction_threshold=compaction_threshold,
    )
    agent.initialize(goal, constraints)
    return agent
