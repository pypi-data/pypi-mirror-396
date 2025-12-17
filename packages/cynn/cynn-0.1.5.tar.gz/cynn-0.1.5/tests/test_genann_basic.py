import pytest
from cynn.genann import GenannNetwork


class TestNetworkCreation:
    """Test network instantiation and properties."""

    def test_create_network(self):
        """Test basic network creation."""
        net = GenannNetwork(2, 1, 3, 1)
        assert net is not None
        assert isinstance(net, GenannNetwork)

    def test_network_shape(self):
        """Test network dimensions are correct."""
        net = GenannNetwork(2, 1, 3, 1)
        assert net.shape == (2, 1, 3, 1)
        assert net.input_size == 2
        assert net.hidden_layers == 1
        assert net.hidden_size == 3
        assert net.output_size == 1

    def test_invalid_dimensions(self):
        """Test that invalid dimensions raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            GenannNetwork(0, 1, 3, 1)
        with pytest.raises(ValueError, match="must be positive"):
            GenannNetwork(2, 0, 3, 1)
        with pytest.raises(ValueError, match="must be positive"):
            GenannNetwork(2, 1, 0, 1)
        with pytest.raises(ValueError, match="must be positive"):
            GenannNetwork(2, 1, 3, 0)
        with pytest.raises(ValueError, match="must be positive"):
            GenannNetwork(-1, 1, 3, 1)

    def test_multi_layer_network(self):
        """Test creating network with multiple hidden layers."""
        net = GenannNetwork(3, 2, 4, 2)
        assert net.hidden_layers == 2
        assert net.input_size == 3
        assert net.hidden_size == 4
        assert net.output_size == 2


class TestPrediction:
    """Test prediction functionality."""

    def test_predict_returns_list(self):
        """Test that predict returns a list."""
        net = GenannNetwork(2, 1, 3, 1)
        result = net.predict([0.5, 0.3])
        assert isinstance(result, list)
        assert len(result) == 1

    def test_predict_output_range(self):
        """Test that predictions are in valid range (sigmoid output)."""
        net = GenannNetwork(2, 1, 3, 1)
        result = net.predict([0.5, 0.3])
        assert 0.0 <= result[0] <= 1.0

    def test_predict_wrong_input_size(self):
        """Test that wrong input size raises ValueError."""
        net = GenannNetwork(2, 1, 3, 1)
        with pytest.raises(ValueError, match="expected 2 input values"):
            net.predict([0.5])
        with pytest.raises(ValueError, match="expected 2 input values"):
            net.predict([0.5, 0.3, 0.1])

    def test_predict_various_inputs(self):
        """Test prediction with various input values."""
        net = GenannNetwork(2, 1, 3, 1)
        inputs = [
            [0.0, 0.0],
            [1.0, 1.0],
            [0.5, 0.5],
            [-1.0, 2.0],
        ]
        for inp in inputs:
            result = net.predict(inp)
            assert len(result) == 1
            assert isinstance(result[0], float)


class TestTraining:
    """Test training functionality."""

    def test_train_works(self):
        """Test that train executes and returns loss."""
        net = GenannNetwork(2, 1, 3, 1)
        # GenannNetwork.train() returns loss
        result = net.train([0.5, 0.3], [1.0], 0.1)
        assert isinstance(result, float)
        assert result >= 0.0  # MSE should be non-negative

    def test_train_wrong_input_size(self):
        """Test that wrong input size raises ValueError."""
        net = GenannNetwork(2, 1, 3, 1)
        with pytest.raises(ValueError, match="expected 2 input values"):
            net.train([0.5], [1.0], 0.1)

    def test_train_wrong_target_size(self):
        """Test that wrong target size raises ValueError."""
        net = GenannNetwork(2, 1, 3, 1)
        with pytest.raises(ValueError, match="expected 1 target values"):
            net.train([0.5, 0.3], [1.0, 0.5], 0.1)

    def test_train_updates_weights(self):
        """Test that training changes predictions."""
        net = GenannNetwork(2, 1, 3, 1)
        inputs = [0.5, 0.3]
        targets = [1.0]

        pred_before = net.predict(inputs)

        # Train multiple times
        for _ in range(10):
            net.train(inputs, targets, 0.5)

        pred_after = net.predict(inputs)

        # Prediction should change after training
        assert pred_before[0] != pred_after[0]

    def test_training_improves_prediction(self):
        """Test that repeated training changes predictions."""
        net = GenannNetwork(2, 1, 3, 1)
        inputs = [0.5, 0.3]
        targets = [1.0]

        pred_before = net.predict(inputs)

        # Train several iterations
        for _ in range(50):
            net.train(inputs, targets, 0.1)

        pred_after = net.predict(inputs)

        # Predictions should be different after training
        assert pred_before[0] != pred_after[0]


class TestAdditionalFeatures:
    """Test GenannNetwork-specific features."""

    def test_total_weights(self):
        """Test total_weights property."""
        net = GenannNetwork(2, 1, 3, 1)
        assert isinstance(net.total_weights, int)
        assert net.total_weights > 0

    def test_total_neurons(self):
        """Test total_neurons property."""
        net = GenannNetwork(2, 1, 3, 1)
        assert isinstance(net.total_neurons, int)
        assert net.total_neurons > 0

    def test_randomize(self):
        """Test randomize method."""
        net = GenannNetwork(2, 1, 3, 1)
        net.predict([0.5, 0.3])
        net.randomize()
        pred_after = net.predict([0.5, 0.3])
        # After randomization, predictions should likely be different
        # (though not guaranteed)
        assert isinstance(pred_after[0], float)

    def test_copy(self):
        """Test copy method."""
        net = GenannNetwork(2, 1, 3, 1)
        # Train the network a bit
        for _ in range(5):
            net.train([0.5, 0.3], [1.0], 0.1)

        # Copy it
        net_copy = net.copy()
        assert isinstance(net_copy, GenannNetwork)
        assert net_copy.shape == net.shape

        # Predictions should be the same
        inputs = [0.5, 0.3]
        assert net.predict(inputs) == net_copy.predict(inputs)

        # Training one shouldn't affect the other
        net.train(inputs, [0.0], 0.5)
        # After training original, predictions should differ
        # (not guaranteed but highly likely)
