"""
Baseline compression strategies for comparison.

These baseline strategies provide reference points for evaluating
compression strategies:
- NoCompressionBaseline: Upper bound (full context)
- RandomTruncationBaseline: Lower bound (random selection)
- RecencyOnlyBaseline: Simple recency heuristic
- FirstLastBaseline: Primacy + recency heuristic
"""

import random
from typing import List, Dict, Any, Optional

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from strategies.strategy_base import CompressionStrategy


class NoCompressionBaseline(CompressionStrategy):
    """
    Keep full context without any compression.

    This serves as an UPPER BOUND baseline - the best possible performance
    since no information is lost. If a compression strategy performs close
    to this baseline, it's doing well.

    Note: This may exceed context limits in practice.
    """

    def __init__(self):
        self.original_goal: Optional[str] = None
        self.constraints: List[str] = []

    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        self.original_goal = original_goal
        self.constraints = constraints

    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        self.original_goal = new_goal

    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """Return full context without compression."""
        turns = context[:trigger_point]
        return self.format_context(turns)

    def name(self) -> str:
        return "NoCompression (Full Context)"


class RandomTruncationBaseline(CompressionStrategy):
    """
    Randomly select a subset of turns to keep.

    This serves as a LOWER BOUND baseline - random selection should
    perform poorly. Any reasonable compression strategy should beat this.

    Args:
        keep_ratio: Fraction of turns to keep (default 0.3 = 30%)
        seed: Random seed for reproducibility (default None)
    """

    def __init__(self, keep_ratio: float = 0.3, seed: Optional[int] = None):
        self.keep_ratio = keep_ratio
        self.seed = seed
        self.original_goal: Optional[str] = None
        self.constraints: List[str] = []

    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        self.original_goal = original_goal
        self.constraints = constraints

    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        self.original_goal = new_goal

    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """Randomly select turns to keep."""
        turns = context[:trigger_point]

        if not turns:
            return "(No context)"

        # Set seed if provided for reproducibility
        if self.seed is not None:
            random.seed(self.seed)

        n_keep = max(1, int(len(turns) * self.keep_ratio))
        kept = random.sample(turns, min(n_keep, len(turns)))

        # Sort by turn_id to maintain chronological order
        kept.sort(key=lambda t: t.get("turn_id", t.get("id", 0)))

        return self.format_context(kept)

    def name(self) -> str:
        return f"RandomTruncation ({self.keep_ratio:.0%})"


class RecencyOnlyBaseline(CompressionStrategy):
    """
    Keep only the most recent N turns.

    This is a simple heuristic baseline based on the assumption that
    recent context is most relevant. Often performs reasonably well.

    Args:
        n_recent: Number of recent turns to keep (default 10)
    """

    def __init__(self, n_recent: int = 10):
        self.n_recent = n_recent
        self.original_goal: Optional[str] = None
        self.constraints: List[str] = []

    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        self.original_goal = original_goal
        self.constraints = constraints

    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        self.original_goal = new_goal

    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """Keep only the most recent turns."""
        turns = context[:trigger_point]

        if not turns:
            return "(No context)"

        # Keep last n_recent turns
        if len(turns) > self.n_recent:
            kept = turns[-self.n_recent:]
        else:
            kept = turns

        return self.format_context(kept)

    def name(self) -> str:
        return f"RecencyOnly (last {self.n_recent})"


class FirstLastBaseline(CompressionStrategy):
    """
    Keep first N and last M turns (primacy + recency).

    This heuristic preserves both the initial context (primacy - often
    contains goals and setup) and recent context (recency - current state).

    Args:
        n_first: Number of initial turns to keep (default 5)
        n_last: Number of recent turns to keep (default 5)
    """

    def __init__(self, n_first: int = 5, n_last: int = 5):
        self.n_first = n_first
        self.n_last = n_last
        self.original_goal: Optional[str] = None
        self.constraints: List[str] = []

    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        self.original_goal = original_goal
        self.constraints = constraints

    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        self.original_goal = new_goal

    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """Keep first N and last M turns."""
        turns = context[:trigger_point]

        if not turns:
            return "(No context)"

        # If we have fewer turns than n_first + n_last, keep all
        if len(turns) <= self.n_first + self.n_last:
            return self.format_context(turns)

        # Keep first n_first and last n_last
        first_turns = turns[:self.n_first]
        last_turns = turns[-self.n_last:]

        # Add separator to indicate truncation
        separator = {
            "role": "system",
            "content": f"[... {len(turns) - self.n_first - self.n_last} turns omitted ...]"
        }

        kept = first_turns + [separator] + last_turns

        return self.format_context(kept)

    def name(self) -> str:
        return f"FirstLast ({self.n_first}+{self.n_last})"


class SlidingWindowBaseline(CompressionStrategy):
    """
    Keep a sliding window of the most recent tokens.

    Similar to RecencyOnly but operates on token budget rather than
    turn count.

    Args:
        max_tokens: Maximum tokens to keep (default 20000)
    """

    def __init__(self, max_tokens: int = 20000):
        self.max_tokens = max_tokens
        self.original_goal: Optional[str] = None
        self.constraints: List[str] = []

    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        self.original_goal = original_goal
        self.constraints = constraints

    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        self.original_goal = new_goal

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (4 chars per token heuristic)."""
        return len(text) // 4

    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """Keep most recent turns within token budget."""
        turns = context[:trigger_point]

        if not turns:
            return "(No context)"

        # Select turns from most recent, staying within budget
        kept = []
        total_tokens = 0

        for turn in reversed(turns):
            content = turn.get("content", "")
            turn_tokens = self._estimate_tokens(content)

            if total_tokens + turn_tokens > self.max_tokens:
                break

            kept.insert(0, turn)
            total_tokens += turn_tokens

        if not kept and turns:
            # At minimum keep the last turn
            kept = [turns[-1]]

        return self.format_context(kept)

    def name(self) -> str:
        return f"SlidingWindow ({self.max_tokens // 1000}k tokens)"


# Convenience function to get all baselines
def get_all_baselines() -> List[CompressionStrategy]:
    """
    Get all baseline strategies for comparison.

    Returns:
        List of baseline strategy instances
    """
    return [
        NoCompressionBaseline(),
        RandomTruncationBaseline(keep_ratio=0.3),
        RecencyOnlyBaseline(n_recent=10),
        FirstLastBaseline(n_first=5, n_last=5),
        SlidingWindowBaseline(max_tokens=20000),
    ]


def get_baseline_by_name(name: str) -> Optional[CompressionStrategy]:
    """
    Get a specific baseline strategy by name.

    Args:
        name: One of "no_compression", "random", "recency", "first_last", "sliding_window"

    Returns:
        Baseline strategy instance or None if not found
    """
    baselines = {
        "no_compression": NoCompressionBaseline(),
        "random": RandomTruncationBaseline(keep_ratio=0.3),
        "recency": RecencyOnlyBaseline(n_recent=10),
        "first_last": FirstLastBaseline(n_first=5, n_last=5),
        "sliding_window": SlidingWindowBaseline(max_tokens=20000),
    }
    return baselines.get(name.lower())
