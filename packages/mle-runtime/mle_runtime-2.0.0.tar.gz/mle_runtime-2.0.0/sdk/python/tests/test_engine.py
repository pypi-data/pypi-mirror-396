"""
Unit tests for MLE Python SDK
"""

import pytest
import numpy as np
import mle_runtime


def test_engine_creation():
    """Test engine creation"""
    engine = mle_runtime.MLEEngine(mle_runtime.Device.CPU)
    assert engine is not None
    assert engine.device == mle_runtime.Device.CPU


def test_load_nonexistent_model():
    """Test loading nonexistent model"""
    engine = mle_runtime.MLEEngine()
    
    with pytest.raises(RuntimeError):
        engine.load_model("nonexistent.mle")


def test_run_without_model():
    """Test running inference without loading model"""
    engine = mle_runtime.MLEEngine()
    input_data = np.random.randn(1, 20).astype(np.float32)
    
    with pytest.raises(RuntimeError):
        engine.run([input_data])


def test_context_manager():
    """Test context manager support"""
    with mle_runtime.MLEEngine(mle_runtime.Device.CPU) as engine:
        assert engine is not None


def test_metadata_before_load():
    """Test metadata is None before loading"""
    engine = mle_runtime.MLEEngine()
    assert engine.metadata is None


def test_peak_memory_usage():
    """Test peak memory usage tracking"""
    engine = mle_runtime.MLEEngine()
    memory = engine.peak_memory_usage()
    assert isinstance(memory, int)
    assert memory >= 0


if __name__ == "__main__":
    pytest.main([__file__])
