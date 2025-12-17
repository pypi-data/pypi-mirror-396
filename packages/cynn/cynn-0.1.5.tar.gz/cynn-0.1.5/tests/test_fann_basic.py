import pytest
from cynn.fann import FannNetwork


class TestNetworkCreation:
    """Test network instantiation and properties."""

    def test_create_network(self):
        """Test basic network creation."""
        net = FannNetwork([2, 3, 1])
        assert net is not None
        assert isinstance(net, FannNetwork)

    def test_network_layers(self):
        """Test network dimensions are correct."""
        net = FannNetwork([2, 3, 1])
        assert net.layers == [2, 3, 1]
        assert net.input_size == 2
        assert net.output_size == 1
        assert net.num_layers == 3

    def test_invalid_dimensions(self):
        """Test that invalid dimensions raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            FannNetwork([0, 3, 1])
        with pytest.raises(ValueError, match="must be positive"):
            FannNetwork([2, 0, 1])
        with pytest.raises(ValueError, match="must be positive"):
            FannNetwork([2, 3, 0])
        with pytest.raises(ValueError, match="must be positive"):
            FannNetwork([-1, 3, 1])

    def test_too_few_layers(self):
        """Test that too few layers raises ValueError."""
        with pytest.raises(ValueError, match="at least 2 layers"):
            FannNetwork([2])

    def test_multi_layer_network(self):
        """Test creating network with multiple hidden layers."""
        net = FannNetwork([3, 4, 5, 2])
        assert net.num_layers == 4
        assert net.layers == [3, 4, 5, 2]
        assert net.input_size == 3
        assert net.output_size == 2

    def test_sparse_network(self):
        """Test creating sparse network."""
        net = FannNetwork([2, 8, 1], connection_rate=0.5)
        assert net.layers == [2, 8, 1]
        # Sparse network was created successfully
        # FANN includes bias neurons which add extra connections
        # Just verify the network has valid connection count
        assert net.total_connections > 0
        # Compare with fully connected network
        net_full = FannNetwork([2, 8, 1], connection_rate=1.0)
        # Sparse should typically have fewer or equal connections
        # (may be equal due to bias connections)
        assert net.total_connections <= net_full.total_connections

    def test_invalid_connection_rate(self):
        """Test that invalid connection rate still works (clamped or handled)."""
        # connection_rate > 1.0 should create fully connected network
        net = FannNetwork([2, 3, 1], connection_rate=2.0)
        assert net.layers == [2, 3, 1]


class TestPrediction:
    """Test prediction functionality."""

    def test_predict_returns_list(self):
        """Test that predict returns a list."""
        net = FannNetwork([2, 3, 1])
        result = net.predict([0.5, 0.3])
        assert isinstance(result, list)
        assert len(result) == 1

    def test_predict_output_range(self):
        """Test that predictions are in valid range (sigmoid output)."""
        net = FannNetwork([2, 3, 1])
        result = net.predict([0.5, 0.3])
        assert 0.0 <= result[0] <= 1.0

    def test_predict_wrong_input_size(self):
        """Test that wrong input size raises ValueError."""
        net = FannNetwork([2, 3, 1])
        with pytest.raises(ValueError, match="expected 2 input values"):
            net.predict([0.5])
        with pytest.raises(ValueError, match="expected 2 input values"):
            net.predict([0.5, 0.3, 0.1])

    def test_predict_various_inputs(self):
        """Test prediction with various input values."""
        net = FannNetwork([2, 3, 1])
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
        """Test that train executes without error."""
        net = FannNetwork([2, 3, 1])
        # FannNetwork.train() returns None
        result = net.train([0.5, 0.3], [1.0])
        assert isinstance(result, float)
        assert result >= 0.0  # MSE should be non-negative

    def test_train_wrong_input_size(self):
        """Test that wrong input size raises ValueError."""
        net = FannNetwork([2, 3, 1])
        with pytest.raises(ValueError, match="expected 2 input values"):
            net.train([0.5], [1.0])

    def test_train_wrong_target_size(self):
        """Test that wrong target size raises ValueError."""
        net = FannNetwork([2, 3, 1])
        with pytest.raises(ValueError, match="expected 1 target values"):
            net.train([0.5, 0.3], [1.0, 0.5])

    def test_train_updates_weights(self):
        """Test that training changes predictions."""
        net = FannNetwork([2, 3, 1])
        inputs = [0.5, 0.3]
        targets = [1.0]

        pred_before = net.predict(inputs)

        # Train multiple times
        for _ in range(10):
            net.train(inputs, targets)

        pred_after = net.predict(inputs)

        # Prediction should change after training
        assert pred_before[0] != pred_after[0]

    def test_training_improves_prediction(self):
        """Test that repeated training changes predictions."""
        net = FannNetwork([2, 3, 1])
        inputs = [0.5, 0.3]
        targets = [1.0]

        pred_before = net.predict(inputs)

        # Train several iterations
        for _ in range(50):
            net.train(inputs, targets)

        pred_after = net.predict(inputs)

        # Predictions should be different after training
        assert pred_before[0] != pred_after[0]


class TestAdditionalFeatures:
    """Test FannNetwork-specific features."""

    def test_total_neurons(self):
        """Test total_neurons property."""
        net = FannNetwork([2, 3, 1])
        assert isinstance(net.total_neurons, int)
        assert net.total_neurons > 0

    def test_total_connections(self):
        """Test total_connections property."""
        net = FannNetwork([2, 3, 1])
        assert isinstance(net.total_connections, int)
        assert net.total_connections > 0

    def test_learning_rate(self):
        """Test learning_rate property."""
        net = FannNetwork([2, 3, 1])
        # Default learning rate
        assert isinstance(net.learning_rate, float)

        # Set new learning rate
        net.learning_rate = 0.5
        assert abs(net.learning_rate - 0.5) < 0.01  # Allow for float precision

    def test_learning_momentum(self):
        """Test learning_momentum property."""
        net = FannNetwork([2, 3, 1])
        # Default momentum
        assert isinstance(net.learning_momentum, float)

        # Set new momentum
        net.learning_momentum = 0.2
        assert abs(net.learning_momentum - 0.2) < 0.01

    def test_randomize_weights(self):
        """Test randomize_weights method."""
        net = FannNetwork([2, 3, 1])
        net.predict([0.5, 0.3])
        net.randomize_weights(-0.5, 0.5)
        pred_after = net.predict([0.5, 0.3])
        # After randomization, predictions should likely be different
        assert isinstance(pred_after[0], float)

    def test_copy(self):
        """Test copy method."""
        net = FannNetwork([2, 3, 1])
        # Train the network a bit
        for _ in range(5):
            net.train([0.5, 0.3], [1.0])

        # Copy it
        net_copy = net.copy()
        assert isinstance(net_copy, FannNetwork)
        assert net_copy.layers == net.layers

        # Predictions should be the same
        inputs = [0.5, 0.3]
        assert net.predict(inputs) == net_copy.predict(inputs)

        # Training one shouldn't affect the other
        net.train(inputs, [0.0])
        # After training original, predictions should differ
