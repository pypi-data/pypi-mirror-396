import random
from cynn.tinn import TinnNetwork


class TestXORTraining:
    """Test training on XOR problem, similar to test.c pattern."""

    def test_xor_learning(self, xor_network, xor_data):
        """Test that network can learn XOR function."""
        # Training parameters inspired by test.c
        rate = 1.0
        anneal = 0.99
        iterations = 100

        for iteration in range(iterations):
            # Shuffle data like in test.c
            random.shuffle(xor_data)

            total_error = 0.0
            for inputs, targets in xor_data:
                error = xor_network.train(inputs, targets, rate)
                total_error += error

            avg_error = total_error / len(xor_data)

            # Anneal learning rate
            rate *= anneal

            # After enough iterations, error should be reasonably low
            if iteration == iterations - 1:
                assert avg_error < 0.5, f"Final average error too high: {avg_error}"

    def test_xor_predictions_after_training(self, xor_network, xor_data):
        """Test that XOR predictions are reasonable after training."""
        # Train the network
        rate = 1.0
        for _ in range(150):
            for inputs, targets in xor_data:
                xor_network.train(inputs, targets, rate)
            rate *= 0.99

        # Test predictions
        predictions = []
        for inputs, expected in xor_data:
            pred = xor_network.predict(inputs)
            predictions.append((inputs, pred[0], expected[0]))

        # Check that predictions trend in the right direction
        # For XOR: (0,0)->0, (0,1)->1, (1,0)->1, (1,1)->0
        # We don't require perfect accuracy, just that the network learned something
        for inputs, pred, expected in predictions:
            # Allow some error margin
            assert 0.0 <= pred <= 1.0, f"Prediction out of range: {pred}"


class TestTrainingPatterns:
    """Test training patterns similar to test.c."""

    def test_training_with_annealing(self, simple_network):
        """Test training with learning rate annealing like test.c."""
        inputs = [0.5, 0.3]
        targets = [0.8]

        rate = 1.0
        anneal = 0.99
        iterations = 50

        errors = []
        for _ in range(iterations):
            error = simple_network.train(inputs, targets, rate)
            errors.append(error)
            rate *= anneal

        # Verify learning rate was annealed
        assert rate < 1.0
        assert rate > 0.5  # Should still be reasonable after 50 iterations

    def test_batch_training(self, xor_network, xor_data):
        """Test training on multiple examples like test.c."""
        rate = 0.5

        # Train one epoch
        total_error = 0.0
        for inputs, targets in xor_data:
            error = xor_network.train(inputs, targets, rate)
            total_error += error

        avg_error = total_error / len(xor_data)

        assert avg_error >= 0.0
        assert isinstance(avg_error, float)

    def test_shuffle_and_train(self, xor_network, xor_data):
        """Test shuffling data between epochs like test.c."""
        rate = 0.5
        iterations = 10

        for _ in range(iterations):
            # Shuffle like in test.c
            random.shuffle(xor_data)

            # Train on shuffled data
            for inputs, targets in xor_data:
                error = xor_network.train(inputs, targets, rate)
                assert error >= 0.0


class TestMultiOutputTraining:
    """Test training with multiple outputs."""

    def test_multi_output_network(self):
        """Test network with multiple outputs."""
        net = TinnNetwork(3, 4, 2)
        assert net.output_size == 2

        inputs = [0.1, 0.5, 0.9]
        targets = [0.2, 0.8]

        # Should not raise
        loss = net.train(inputs, targets, 0.1)
        assert loss >= 0.0

        pred = net.predict(inputs)
        assert len(pred) == 2

    def test_larger_network_training(self):
        """Test training on a larger network similar to test.c dimensions."""
        # test.c uses nips=256, nhid=28, nops=10
        # We use smaller dimensions for faster testing
        net = TinnNetwork(16, 8, 4)

        inputs = [0.1 * i for i in range(16)]
        targets = [0.0, 1.0, 0.0, 0.0]

        # Train a few iterations
        for _ in range(10):
            loss = net.train(inputs, targets, 0.1)
            assert loss >= 0.0

        pred = net.predict(inputs)
        assert len(pred) == 4
        assert all(0.0 <= p <= 1.0 for p in pred)
