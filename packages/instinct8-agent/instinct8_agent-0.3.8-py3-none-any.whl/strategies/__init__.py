# Context Compression Strategies
# This package contains implementations of different compression strategies
# for long-running LLM agents.

# Base imports (no circular dependencies)
from .strategy_base import CompressionStrategy, Turn, ToolCall, ProbeResults

# Strategy imports - lazy to avoid circular dependencies with evaluation module
# Import these directly from their modules when needed, or use the __all__ exports
# Example: from strategies.strategy_b_codex import StrategyB_CodexCheckpoint

# Lazy imports to avoid circular dependencies
# Import these directly from their modules:
#   from strategies.strategy_b_codex import StrategyB_CodexCheckpoint
#   from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy
# etc.

__all__ = [
    # Base (always available)
    "CompressionStrategy",
    "Turn",
    "ToolCall",
    "ProbeResults",
    # Strategy classes (import directly from their modules to avoid circular imports)
    # "StrategyB_CodexCheckpoint",  # from strategies.strategy_b_codex import StrategyB_CodexCheckpoint
    # "SelectiveSalienceStrategy",  # from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy
    # etc.
]

