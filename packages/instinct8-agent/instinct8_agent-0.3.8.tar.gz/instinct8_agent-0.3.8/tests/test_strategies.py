"""Tests for compression strategies."""

import pytest
from strategies.strategy_base import CompressionStrategy, Turn


class TestCompressionStrategyBase:
    """Test the base compression strategy interface."""

    def test_turn_dataclass(self):
        """Test Turn dataclass creation."""
        turn = Turn(
            role="user",
            content="Hello, world!",
            timestamp=None,
        )
        assert turn.role == "user"
        assert turn.content == "Hello, world!"

    def test_strategy_is_abstract(self):
        """Test that CompressionStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError):
            CompressionStrategy()


class TestCodexStrategy:
    """Tests for Codex-style checkpoint strategy."""

    def test_import(self):
        """Test that strategy can be imported."""
        from strategies.strategy_b_codex import StrategyB_CodexCheckpoint
        assert StrategyB_CodexCheckpoint is not None

    def test_create_strategy(self):
        """Test strategy creation."""
        from strategies.strategy_b_codex import create_codex_strategy
        strategy = create_codex_strategy(
            system_prompt="You are a helpful assistant.",
            model="gpt-4o-mini",
        )
        assert strategy is not None
        assert strategy.name == "Strategy B - Codex-Style Checkpoint"
