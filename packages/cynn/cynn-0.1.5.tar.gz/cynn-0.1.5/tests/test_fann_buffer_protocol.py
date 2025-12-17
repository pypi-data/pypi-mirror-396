import pytest
import array
from cynn.fann import FannNetwork


class TestBufferProtocol:
    """Test that train() and predict() work with buffer protocol objects."""

    def test_train_with_list(self):
        """Test training with Python lists."""
        net = FannNetwork([2, 3, 1])
        inputs = [0.5, 0.3]
        targets = [0.8]
        result = net.train(inputs, targets)
        # FannNetwork.train() returns None
        assert isinstance(result, float)
        assert result >= 0.0  # MSE should be non-negative

    def test_predict_with_list(self):
        """Test prediction with Python lists."""
        net = FannNetwork([2, 3, 1])
        inputs = [0.5, 0.3]
        result = net.predict(inputs)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_train_with_tuple(self):
        """Test training with tuples."""
        net = FannNetwork([2, 3, 1])
        inputs = (0.5, 0.3)
        targets = (0.8,)
        result = net.train(inputs, targets)
        assert isinstance(result, float)
        assert result >= 0.0  # MSE should be non-negative

    def test_predict_with_tuple(self):
        """Test prediction with tuples."""
        net = FannNetwork([2, 3, 1])
        inputs = (0.5, 0.3)
        result = net.predict(inputs)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_train_with_array(self):
        """Test training with array.array (float32)."""
        net = FannNetwork([2, 3, 1])
        inputs = array.array('f', [0.5, 0.3])
        targets = array.array('f', [0.8])
        result = net.train(inputs, targets)
        assert isinstance(result, float)
        assert result >= 0.0  # MSE should be non-negative

    def test_predict_with_array(self):
        """Test prediction with array.array (float32)."""
        net = FannNetwork([2, 3, 1])
        inputs = array.array('f', [0.5, 0.3])
        result = net.predict(inputs)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_train_with_memoryview(self):
        """Test training with memoryview."""
        net = FannNetwork([2, 3, 1])
        inputs_arr = array.array('f', [0.5, 0.3])
        targets_arr = array.array('f', [0.8])
        inputs = memoryview(inputs_arr)
        targets = memoryview(targets_arr)
        result = net.train(inputs, targets)
        assert isinstance(result, float)
        assert result >= 0.0  # MSE should be non-negative

    def test_predict_with_memoryview(self):
        """Test prediction with memoryview."""
        net = FannNetwork([2, 3, 1])
        inputs_arr = array.array('f', [0.5, 0.3])
        inputs = memoryview(inputs_arr)
        result = net.predict(inputs)
        assert isinstance(result, list)
        assert len(result) == 1


class TestNumpyCompatibility:
    """Test NumPy array compatibility (if NumPy is available)."""

    @pytest.mark.skipif(
        not pytest.importorskip("numpy", minversion=None),
        reason="NumPy not available"
    )
    def test_train_with_numpy_array(self):
        """Test training with NumPy arrays."""
        import numpy as np
        net = FannNetwork([2, 3, 1])
        inputs = np.array([0.5, 0.3], dtype=np.float32)
        targets = np.array([0.8], dtype=np.float32)
        result = net.train(inputs, targets)
        assert isinstance(result, float)
        assert result >= 0.0  # MSE should be non-negative

    @pytest.mark.skipif(
        not pytest.importorskip("numpy", minversion=None),
        reason="NumPy not available"
    )
    def test_predict_with_numpy_array(self):
        """Test prediction with NumPy arrays."""
        import numpy as np
        net = FannNetwork([2, 3, 1])
        inputs = np.array([0.5, 0.3], dtype=np.float32)
        result = net.predict(inputs)
        assert isinstance(result, list)
        assert len(result) == 1


class TestMixedInputTypes:
    """Test mixing different input types."""

    def test_train_mixed_types(self):
        """Test training with mixed input types."""
        net = FannNetwork([2, 3, 1])
        # List for inputs, tuple for targets
        net.train([0.5, 0.3], (0.8,))
        # Array for inputs, list for targets
        inputs = array.array('f', [0.5, 0.3])
        net.train(inputs, [0.8])

    def test_predict_mixed_types(self):
        """Test prediction with mixed input types."""
        net = FannNetwork([2, 3, 1])
        result1 = net.predict([0.5, 0.3])
        result2 = net.predict((0.5, 0.3))
        inputs = array.array('f', [0.5, 0.3])
        result3 = net.predict(inputs)
        # All should return valid results
        assert isinstance(result1, list)
        assert isinstance(result2, list)
        assert isinstance(result3, list)
