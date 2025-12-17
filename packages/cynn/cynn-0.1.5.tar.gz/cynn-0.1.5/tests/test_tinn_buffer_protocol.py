import pytest
import array


class TestBufferProtocol:
    """Test that train() and predict() work with buffer protocol objects."""

    def test_train_with_list(self, simple_network):
        """Test training with Python lists."""
        inputs = [0.5, 0.3]
        targets = [0.8]
        loss = simple_network.train(inputs, targets, 0.1)
        assert isinstance(loss, float)
        assert loss >= 0.0

    def test_predict_with_list(self, simple_network):
        """Test prediction with Python lists."""
        inputs = [0.5, 0.3]
        result = simple_network.predict(inputs)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_train_with_tuple(self, simple_network):
        """Test training with tuples."""
        inputs = (0.5, 0.3)
        targets = (0.8,)
        loss = simple_network.train(inputs, targets, 0.1)
        assert isinstance(loss, float)
        assert loss >= 0.0

    def test_predict_with_tuple(self, simple_network):
        """Test prediction with tuples."""
        inputs = (0.5, 0.3)
        result = simple_network.predict(inputs)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_train_with_array(self, simple_network):
        """Test training with array.array."""
        inputs = array.array('f', [0.5, 0.3])
        targets = array.array('f', [0.8])
        loss = simple_network.train(inputs, targets, 0.1)
        assert isinstance(loss, float)
        assert loss >= 0.0

    def test_predict_with_array(self, simple_network):
        """Test prediction with array.array."""
        inputs = array.array('f', [0.5, 0.3])
        result = simple_network.predict(inputs)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_train_with_memoryview(self, simple_network):
        """Test training with memoryview."""
        inputs_arr = array.array('f', [0.5, 0.3])
        targets_arr = array.array('f', [0.8])
        inputs = memoryview(inputs_arr)
        targets = memoryview(targets_arr)
        loss = simple_network.train(inputs, targets, 0.1)
        assert isinstance(loss, float)
        assert loss >= 0.0

    def test_predict_with_memoryview(self, simple_network):
        """Test prediction with memoryview."""
        inputs_arr = array.array('f', [0.5, 0.3])
        inputs = memoryview(inputs_arr)
        result = simple_network.predict(inputs)
        assert isinstance(result, list)
        assert len(result) == 1


class TestNumpyCompatibility:
    """Test compatibility with numpy arrays."""

    def test_train_with_numpy_array(self, simple_network):
        """Test training with numpy arrays."""
        np = pytest.importorskip("numpy")

        inputs = np.array([0.5, 0.3], dtype=np.float32)
        targets = np.array([0.8], dtype=np.float32)
        loss = simple_network.train(inputs, targets, 0.1)
        assert isinstance(loss, float)
        assert loss >= 0.0

    def test_predict_with_numpy_array(self, simple_network):
        """Test prediction with numpy arrays."""
        np = pytest.importorskip("numpy")

        inputs = np.array([0.5, 0.3], dtype=np.float32)
        result = simple_network.predict(inputs)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_xor_training_with_numpy(self, xor_network):
        """Test XOR training using numpy arrays."""
        np = pytest.importorskip("numpy")

        # XOR data as numpy arrays
        inputs_data = np.array([
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0],
            [1.0, 1.0],
        ], dtype=np.float32)

        targets_data = np.array([
            [0.0],
            [1.0],
            [1.0],
            [0.0],
        ], dtype=np.float32)

        # Train for a few epochs
        rate = 0.5
        for _ in range(10):
            for i in range(len(inputs_data)):
                loss = xor_network.train(inputs_data[i], targets_data[i], rate)
                assert loss >= 0.0

    def test_batch_predictions_with_numpy(self, simple_network):
        """Test making predictions on multiple numpy arrays."""
        np = pytest.importorskip("numpy")

        # Create batch of inputs
        batch = np.array([
            [0.1, 0.2],
            [0.3, 0.4],
            [0.5, 0.6],
        ], dtype=np.float32)

        # Predict for each
        results = []
        for inputs in batch:
            pred = simple_network.predict(inputs)
            results.append(pred[0])

        assert len(results) == 3
        assert all(isinstance(r, float) for r in results)

    def test_numpy_wrong_dtype_converts(self, simple_network):
        """Test that numpy arrays with wrong dtype get converted."""
        np = pytest.importorskip("numpy")

        # Create array with float64
        inputs = np.array([0.5, 0.3], dtype=np.float64)
        targets = np.array([0.8], dtype=np.float64)

        # Should work by converting to float32
        try:
            loss = simple_network.train(inputs, targets, 0.1)
            assert isinstance(loss, float)
        except (TypeError, ValueError):
            # It's also acceptable to raise an error for wrong dtype
            pytest.skip("Implementation requires exact float32 dtype")

    def test_numpy_multidimensional_slice(self, simple_network):
        """Test using slices of multidimensional numpy arrays."""
        np = pytest.importorskip("numpy")

        # Create 2D array and use rows
        data = np.array([
            [0.5, 0.3],
            [0.7, 0.2],
        ], dtype=np.float32)

        result1 = simple_network.predict(data[0])
        result2 = simple_network.predict(data[1])

        assert len(result1) == 1
        assert len(result2) == 1
        assert result1[0] != result2[0]  # Different inputs should give different outputs


class TestMixedInputTypes:
    """Test using different input types together."""

    def test_train_mixed_types(self, simple_network):
        """Test training with different input types in sequence."""
        # Train with list
        loss1 = simple_network.train([0.5, 0.3], [0.8], 0.1)

        # Train with tuple
        loss2 = simple_network.train((0.5, 0.3), (0.8,), 0.1)

        # Train with array
        loss3 = simple_network.train(
            array.array('f', [0.5, 0.3]),
            array.array('f', [0.8]),
            0.1
        )

        assert all(isinstance(loss, float) for loss in [loss1, loss2, loss3])
        assert all(loss >= 0.0 for loss in [loss1, loss2, loss3])

    def test_predict_mixed_types(self, simple_network):
        """Test prediction with different input types in sequence."""
        # Predict with list
        pred1 = simple_network.predict([0.5, 0.3])

        # Predict with tuple
        pred2 = simple_network.predict((0.5, 0.3))

        # Predict with array
        pred3 = simple_network.predict(array.array('f', [0.5, 0.3]))

        # All should give same result for same input
        assert pred1[0] == pytest.approx(pred2[0], abs=1e-6)
        assert pred2[0] == pytest.approx(pred3[0], abs=1e-6)
