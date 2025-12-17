"""
Token budget utilities for artificial context window management.

Provides token estimation and budget management for testing compaction
at specific context window thresholds, even with large-context models.
"""

from dataclasses import dataclass
from math import ceil, floor
from typing import Optional

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.

    Uses tiktoken for accurate estimation if available, otherwise falls back
    to a deterministic heuristic: ceil(len(text) / 4).

    Args:
        text: The text to estimate tokens for

    Returns:
        Estimated token count
    """
    if TIKTOKEN_AVAILABLE:
        # Use tiktoken for accurate estimation (OpenAI-style tokenization)
        try:
            # Use OpenAI tokenizer (GPT-4/Claude compatible)
            encoding = tiktoken.get_encoding("cl100k_base")  # OpenAI/GPT-4 tokenizer
            return len(encoding.encode(text))
        except Exception:
            # Fallback to heuristic if tiktoken fails
            pass

    # Deterministic fallback heuristic: ~4 chars per token
    return ceil(len(text) / 4)


@dataclass
class TokenBudget:
    """
    Configuration for artificial context window budget.

    Defines the artificial context window size and compaction trigger thresholds.
    Used to test compaction behavior at specific token limits.
    """

    window_tokens: int
    """Total artificial context window size in tokens"""

    trigger_ratio: float
    """Ratio of window tokens at which to trigger compaction (0.0-1.0)"""

    output_reserve_tokens: int
    """Tokens reserved for model output to avoid exceeding window"""

    @property
    def trigger_tokens(self) -> int:
        """
        Calculate the token threshold that triggers compaction.

        Formula: floor(window_tokens * trigger_ratio) - output_reserve_tokens

        Returns:
            Token count threshold for triggering compaction
        """
        return floor(self.window_tokens * self.trigger_ratio) - self.output_reserve_tokens


def should_compact(prompt_text: str, budget: TokenBudget) -> bool:
    """
    Determine if compaction should be triggered based on prompt token count.

    Args:
        prompt_text: The reconstructed prompt text to check
        budget: Token budget configuration

    Returns:
        True if estimated prompt tokens exceed the trigger threshold
    """
    estimated_tokens = estimate_tokens(prompt_text)
    return estimated_tokens >= budget.trigger_tokens


# Pre-configured budgets for common testing scenarios
BUDGET_8K = TokenBudget(
    window_tokens=8192,
    trigger_ratio=0.90,
    output_reserve_tokens=1024,
)

BUDGET_16K = TokenBudget(
    window_tokens=16384,
    trigger_ratio=0.90,
    output_reserve_tokens=1024,
)

BUDGET_32K = TokenBudget(
    window_tokens=32768,
    trigger_ratio=0.90,
    output_reserve_tokens=1024,
)
