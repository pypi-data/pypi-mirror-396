"""
Selective Salience Compressor - User-facing API

This module provides a clean, simple interface for using Selective Salience
Compression in your LLM agent applications.
"""

from typing import Any, Dict, List, Optional

# Import strategy - works when installed as package
from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy


class SelectiveSalienceCompressor:
    """
    Selective Salience Compression for LLM Agents
    
    Preserves goal-critical information in long-running conversations by:
    1. Extracting salient information verbatim using GPT-4o
    2. Compressing background context using GPT-4o-mini
    3. Maintaining a cumulative salience set across compressions
    
    Example:
        >>> compressor = SelectiveSalienceCompressor()
        >>> compressor.initialize(
        ...     original_goal="Research async frameworks",
        ...     constraints=["Budget $10K", "Timeline 2 weeks"]
        ... )
        >>> 
        >>> # After accumulating context...
        >>> compressed = compressor.compress(
        ...     context=[
        ...         {"id": 1, "role": "user", "content": "What frameworks exist?"},
        ...         {"id": 2, "role": "assistant", "content": "FastAPI, Django..."},
        ...     ],
        ...     trigger_point=2
        ... )
        >>> print(compressed)
    """
    
    def __init__(
        self,
        extraction_model: str = "gpt-4o",
        compression_model: str = "gpt-4o-mini",
        similarity_threshold: float = 0.85,
    ):
        """
        Initialize the Selective Salience Compressor.
        
        Args:
            extraction_model: Model for salience extraction (default: "gpt-4o")
            compression_model: Model for background compression (default: "gpt-4o-mini")
            similarity_threshold: Cosine similarity threshold for deduplication (default: 0.85)
        
        Note: Requires OPENAI_API_KEY environment variable to be set.
        """
        self._strategy = SelectiveSalienceStrategy(
            extraction_model=extraction_model,
            compression_model=compression_model,
            similarity_threshold=similarity_threshold,
        )
    
    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        """
        Initialize the compressor with the task's goal and constraints.
        
        This should be called once at the start of your agent's task.
        
        Args:
            original_goal: The task's original goal statement
            constraints: List of hard constraints the agent must follow
        
        Example:
            >>> compressor.initialize(
            ...     original_goal="Research async frameworks and recommend one",
            ...     constraints=["Budget max $10K", "Timeline 2 weeks", "Must support WebSockets"]
            ... )
        """
        self._strategy.initialize(original_goal, constraints)
    
    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """
        Compress conversation context while preserving goal-critical information.
        
        Args:
            context: List of conversation turns, each as a dict with:
                - "id": Turn ID (int)
                - "role": "user", "assistant", or "system" (str)
                - "content": Turn content (str)
                - Optional: "tool_call", "decision", etc.
            trigger_point: Turn ID to compress up to (all turns <= this ID)
        
        Returns:
            Compressed context string ready to use as agent context
        
        Example:
            >>> context = [
            ...     {"id": 1, "role": "user", "content": "What frameworks exist?"},
            ...     {"id": 2, "role": "assistant", "content": "FastAPI, Django..."},
            ...     {"id": 3, "role": "user", "content": "Which supports WebSockets?"},
            ... ]
            >>> compressed = compressor.compress(context, trigger_point=2)
            >>> # Use compressed as your agent's context
        """
        return self._strategy.compress(context, trigger_point)
    
    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        """
        Update the goal if it evolves during the task.
        
        Args:
            new_goal: The updated goal statement
            rationale: Optional explanation for why the goal changed
        """
        self._strategy.update_goal(new_goal, rationale)
    
    @property
    def salience_set(self) -> List[str]:
        """
        Get the current salience set (goal-critical information preserved verbatim).
        
        Returns:
            List of salient information items
        """
        return self._strategy.salience_set.copy() if hasattr(self._strategy, 'salience_set') else []
    
    def reset(self) -> None:
        """
        Reset the compressor state (clears salience set).
        
        Useful when starting a new task or conversation.
        """
        if hasattr(self._strategy, 'salience_set'):
            self._strategy.salience_set = []
        if hasattr(self._strategy, 'original_goal'):
            self._strategy.original_goal = None
        if hasattr(self._strategy, 'constraints'):
            self._strategy.constraints = []
