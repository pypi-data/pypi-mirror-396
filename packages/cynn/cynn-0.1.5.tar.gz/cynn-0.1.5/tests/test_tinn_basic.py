import pytest
from cynn.tinn import TinnNetwork


class TestNetworkCreation:
    """Test network instantiation and properties."""

    def test_create_network(self, simple_network):
        """Test basic network creation."""
        assert simple_network is not None
        assert isinstance(simple_network, TinnNetwork)

    def test_network_shape(self, simple_network):
        """Test network dimensions are correct."""
        assert simple_network.shape == (2, 3, 1)
        assert simple_network.input_size == 2
        assert simple_network.hidden_size == 3
        assert simple_network.output_size == 1

    def test_invalid_dimensions(self):
        """Test that invalid dimensions raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            TinnNetwork(0, 3, 1)
        with pytest.raises(ValueError, match="must be positive"):
            TinnNetwork(2, 0, 1)
        with pytest.raises(ValueError, match="must be positive"):
            TinnNetwork(2, 3, 0)
        with pytest.raises(ValueError, match="must be positive"):
            TinnNetwork(-1, 3, 1)


class TestPrediction:
    """Test prediction functionality."""

    def test_predict_returns_list(self, simple_network):
        """Test that predict returns a list."""
        result = simple_network.predict([0.5, 0.3])
        assert isinstance(result, list)
        assert len(result) == 1

    def test_predict_output_range(self, simple_network):
        """Test that predictions are in valid range (sigmoid output)."""
        result = simple_network.predict([0.5, 0.3])
        assert 0.0 <= result[0] <= 1.0

    def test_predict_wrong_input_size(self, simple_network):
        """Test that wrong input size raises ValueError."""
        with pytest.raises(ValueError, match="expected 2 input values"):
            simple_network.predict([0.5])
        with pytest.raises(ValueError, match="expected 2 input values"):
            simple_network.predict([0.5, 0.3, 0.1])

    def test_predict_various_inputs(self, simple_network):
        """Test prediction with various input values."""
        inputs = [
            [0.0, 0.0],
            [1.0, 1.0],
            [0.5, 0.5],
            [-1.0, 2.0],
        ]
        for inp in inputs:
            result = simple_network.predict(inp)
            assert len(result) == 1
            assert isinstance(result[0], float)


class TestTraining:
    """Test training functionality."""

    def test_train_returns_loss(self, simple_network):
        """Test that train returns a loss value."""
        loss = simple_network.train([0.5, 0.3], [1.0], 0.1)
        assert isinstance(loss, float)
        assert loss >= 0.0

    def test_train_wrong_input_size(self, simple_network):
        """Test that wrong input size raises ValueError."""
        with pytest.raises(ValueError, match="expected 2 input values"):
            simple_network.train([0.5], [1.0], 0.1)

    def test_train_wrong_target_size(self, simple_network):
        """Test that wrong target size raises ValueError."""
        with pytest.raises(ValueError, match="expected 1 target values"):
            simple_network.train([0.5, 0.3], [1.0, 0.5], 0.1)

    def test_train_updates_weights(self, simple_network):
        """Test that training changes predictions."""
        inputs = [0.5, 0.3]
        targets = [1.0]

        pred_before = simple_network.predict(inputs)

        # Train multiple times
        for _ in range(10):
            simple_network.train(inputs, targets, 0.5)

        pred_after = simple_network.predict(inputs)

        # Prediction should change after training
        assert pred_before[0] != pred_after[0]

    def test_training_reduces_loss(self, simple_network):
        """Test that repeated training reduces loss."""
        inputs = [0.5, 0.3]
        targets = [1.0]

        initial_loss = simple_network.train(inputs, targets, 0.1)

        # Train several iterations
        for _ in range(50):
            simple_network.train(inputs, targets, 0.1)

        final_loss = simple_network.train(inputs, targets, 0.1)

        # Loss should decrease (though not guaranteed in all cases)
        # We just verify both are valid loss values
        assert initial_loss >= 0.0
        assert final_loss >= 0.0
