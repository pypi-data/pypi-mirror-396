# Context Compression Strategies
# This package contains implementations of different compression strategies
# for long-running LLM agents.

from .strategy_base import CompressionStrategy, Turn, ToolCall, ProbeResults
from .strategy_b_codex import StrategyB_CodexCheckpoint, create_codex_strategy
from .strategy_d_amem import StrategyD_AMemStyle, create_amem_strategy
from .strategy_f_protected_core import StrategyF_ProtectedCore, create_protected_core_strategy
from .strategy_g_hybrid import StrategyG_Hybrid, create_hybrid_strategy
from .strategy_h_selective_salience import SelectiveSalienceStrategy
from .strategy_h_keyframe import StrategyH_Keyframe, create_keyframe_strategy
from .strategy_i_hybrid_amem_protected import StrategyI_AMemProtectedCore, create_amem_protected_strategy

__all__ = [
    # Base
    "CompressionStrategy",
    "Turn",
    "ToolCall",
    "ProbeResults",
    # Strategy B - Codex
    "StrategyB_CodexCheckpoint",
    "create_codex_strategy",
    # Strategy D - A-MEM
    "StrategyD_AMemStyle",
    "create_amem_strategy",
    # Strategy F - Protected Core + Goal Re-assertion (Novel)
    "StrategyF_ProtectedCore",
    "create_protected_core_strategy",
    # Strategy G - Hybrid GraphRAG
    "StrategyG_Hybrid",
    "create_hybrid_strategy",
    # Strategy H - Selective Salience Compression (Agent-as-Judge)
    "SelectiveSalienceStrategy",
    # Strategy H - Keyframe Compression (alternative implementation)
    "StrategyH_Keyframe",
    "create_keyframe_strategy",
    # Strategy I - A-MEM + Protected Core Hybrid
    "StrategyI_AMemProtectedCore",
    "create_amem_protected_strategy",
]

