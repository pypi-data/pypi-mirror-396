"""
Tests for the selective_salience package API
"""

import pytest
import os
from unittest.mock import Mock, patch

# Skip tests if OpenAI API key not set
pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)


def test_import():
    """Test that the package can be imported."""
    from selective_salience import SelectiveSalienceCompressor
    assert SelectiveSalienceCompressor is not None


def test_compressor_initialization():
    """Test compressor can be initialized."""
    from selective_salience import SelectiveSalienceCompressor
    
    compressor = SelectiveSalienceCompressor()
    assert compressor is not None


def test_compressor_initialize():
    """Test compressor can be initialized with goal and constraints."""
    from selective_salience import SelectiveSalienceCompressor
    
    compressor = SelectiveSalienceCompressor()
    compressor.initialize(
        original_goal="Test goal",
        constraints=["Constraint 1", "Constraint 2"]
    )
    
    assert compressor.salience_set == []


def test_compressor_reset():
    """Test compressor can be reset."""
    from selective_salience import SelectiveSalienceCompressor
    
    compressor = SelectiveSalienceCompressor()
    compressor.initialize("Test goal", ["Constraint 1"])
    compressor.reset()
    
    # After reset, salience set should be empty
    assert compressor.salience_set == []


def test_compressor_compress_simple():
    """Test compressor can compress simple context."""
    from selective_salience import SelectiveSalienceCompressor
    
    compressor = SelectiveSalienceCompressor()
    compressor.initialize(
        original_goal="Research frameworks",
        constraints=["Budget $10K"]
    )
    
    context = [
        {"id": 1, "role": "user", "content": "What frameworks exist?"},
        {"id": 2, "role": "assistant", "content": "FastAPI, Django..."},
    ]
    
    # This will make actual API calls, so it's a real integration test
    compressed = compressor.compress(context, trigger_point=2)
    
    assert isinstance(compressed, str)
    assert len(compressed) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
