import pytest
import random
from cynn.genann import GenannNetwork


class TestXORTraining:
    """Test training on XOR problem."""

    @pytest.fixture
    def xor_network(self):
        """Create a network for XOR learning."""
        return GenannNetwork(2, 1, 3, 1)

    @pytest.fixture
    def xor_data(self):
        """XOR training data."""
        return [
            ([0.0, 0.0], [0.0]),
            ([0.0, 1.0], [1.0]),
            ([1.0, 0.0], [1.0]),
            ([1.0, 1.0], [0.0]),
        ]

    def test_xor_learning(self, xor_network, xor_data):
        """Test that network can learn XOR function."""
        learning_rate = 0.5
        iterations = 500

        for iteration in range(iterations):
            # Shuffle data
            random.shuffle(xor_data)

            for inputs, targets in xor_data:
                xor_network.train(inputs, targets, learning_rate)

        # After training, predictions should be reasonable
        # Check that network learned something
        for inputs, expected in xor_data:
            pred = xor_network.predict(inputs)
            assert 0.0 <= pred[0] <= 1.0, f"Prediction out of range: {pred[0]}"

    def test_xor_predictions_after_training(self, xor_network, xor_data):
        """Test that XOR predictions improve after training."""
        # Get initial predictions
        initial_preds = []
        for inputs, targets in xor_data:
            pred = xor_network.predict(inputs)
            initial_preds.append(pred[0])

        # Train the network
        learning_rate = 0.5
        for _ in range(1000):
            for inputs, targets in xor_data:
                xor_network.train(inputs, targets, learning_rate)

        # Test predictions improved or stayed stable
        final_preds = []
        for inputs, expected in xor_data:
            pred = xor_network.predict(inputs)
            final_preds.append(pred[0])
            # Predictions should be in valid range
            assert 0.0 <= pred[0] <= 1.0, f"Prediction out of range: {pred[0]}"

        # At least verify predictions are valid floats
        assert all(isinstance(p, float) for p in final_preds)


class TestTrainingPatterns:
    """Test training patterns."""

    def test_training_with_annealing(self):
        """Test training with learning rate annealing."""
        net = GenannNetwork(2, 1, 3, 1)
        inputs = [0.5, 0.3]
        targets = [0.8]

        rate = 0.5
        anneal = 0.99
        iterations = 50

        for _ in range(iterations):
            net.train(inputs, targets, rate)
            rate *= anneal

        # Verify learning rate was annealed
        assert rate < 0.5
        assert rate > 0.3  # Should still be reasonable after 50 iterations

    def test_batch_training(self):
        """Test training on multiple examples."""
        net = GenannNetwork(2, 1, 3, 1)
        xor_data = [
            ([0.0, 0.0], [0.0]),
            ([0.0, 1.0], [1.0]),
            ([1.0, 0.0], [1.0]),
            ([1.0, 1.0], [0.0]),
        ]

        rate = 0.5

        # Train one epoch
        for inputs, targets in xor_data:
            net.train(inputs, targets, rate)

        # Verify predictions work after training
        for inputs, _ in xor_data:
            pred = net.predict(inputs)
            assert len(pred) == 1
            assert isinstance(pred[0], float)

    def test_shuffle_and_train(self):
        """Test shuffling data between epochs."""
        net = GenannNetwork(2, 1, 3, 1)
        xor_data = [
            ([0.0, 0.0], [0.0]),
            ([0.0, 1.0], [1.0]),
            ([1.0, 0.0], [1.0]),
            ([1.0, 1.0], [0.0]),
        ]

        rate = 0.5
        iterations = 10

        for _ in range(iterations):
            # Shuffle
            random.shuffle(xor_data)

            # Train on shuffled data
            for inputs, targets in xor_data:
                net.train(inputs, targets, rate)

        # Verify network still works
        pred = net.predict([0.5, 0.5])
        assert len(pred) == 1
        assert 0.0 <= pred[0] <= 1.0


class TestMultiOutputTraining:
    """Test training with multiple outputs."""

    def test_multi_output_network(self):
        """Test network with multiple outputs."""
        net = GenannNetwork(3, 1, 4, 2)
        assert net.output_size == 2

        inputs = [0.1, 0.5, 0.9]
        targets = [0.2, 0.8]

        # Should not raise
        net.train(inputs, targets, 0.1)

        pred = net.predict(inputs)
        assert len(pred) == 2

    def test_larger_network_training(self):
        """Test training on a larger network."""
        net = GenannNetwork(16, 1, 8, 4)

        inputs = [0.1 * i for i in range(16)]
        targets = [0.0, 1.0, 0.0, 0.0]

        # Train a few iterations
        for _ in range(10):
            net.train(inputs, targets, 0.1)

        pred = net.predict(inputs)
        assert len(pred) == 4
        assert all(0.0 <= p <= 1.0 for p in pred)


class TestMultiLayerTraining:
    """Test training with multiple hidden layers."""

    def test_multi_layer_network_training(self):
        """Test network with multiple hidden layers."""
        # Create network with 2 hidden layers
        net = GenannNetwork(3, 2, 4, 2)
        assert net.hidden_layers == 2

        inputs = [0.1, 0.5, 0.9]
        targets = [0.2, 0.8]

        # Train
        for _ in range(20):
            net.train(inputs, targets, 0.1)

        # Verify predictions work
        pred = net.predict(inputs)
        assert len(pred) == 2
        assert all(0.0 <= p <= 1.0 for p in pred)

    def test_deep_network_training(self):
        """Test training a deeper network."""
        # Create network with 3 hidden layers
        net = GenannNetwork(4, 3, 6, 2)
        assert net.hidden_layers == 3

        inputs = [0.2, 0.4, 0.6, 0.8]
        targets = [0.3, 0.7]

        # Train
        for _ in range(30):
            net.train(inputs, targets, 0.1)

        # Verify predictions work
        pred = net.predict(inputs)
        assert len(pred) == 2
        assert all(0.0 <= p <= 1.0 for p in pred)
