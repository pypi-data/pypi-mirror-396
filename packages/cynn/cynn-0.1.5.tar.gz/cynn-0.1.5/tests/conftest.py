import pytest
import random


@pytest.fixture
def simple_network():
    """Create a small network for basic testing."""
    from cynn.tinn import TinnNetwork
    return TinnNetwork(2, 3, 1)


@pytest.fixture
def xor_network():
    """Create a network suitable for XOR problem."""
    from cynn.tinn import TinnNetwork
    return TinnNetwork(2, 4, 1)


@pytest.fixture
def xor_data():
    """XOR training data."""
    return [
        ([0.0, 0.0], [0.0]),
        ([0.0, 1.0], [1.0]),
        ([1.0, 0.0], [1.0]),
        ([1.0, 1.0], [0.0]),
    ]


@pytest.fixture
def temp_model_path(tmp_path):
    """Temporary path for saving models."""
    return tmp_path / "test_model.tinn"


@pytest.fixture(autouse=True)
def seed_random():
    """Seed random number generator for reproducible tests."""
    random.seed(42)
