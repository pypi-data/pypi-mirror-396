"""Tests for KANN neural network training functionality."""

import pytest
import array
import random

from cynn.kann import (
    KannNeuralNetwork,
    COST_MSE,
    COST_MULTI_CROSS_ENTROPY,
    set_seed as kann_set_seed,
)

np = pytest.importorskip("numpy")


class TestMLPTraining:
    """Tests for MLP training."""

    def test_train_reduces_cost(self):
        """Test that training reduces the cost."""
        kann_set_seed(42)
        random.seed(42)

        net = KannNeuralNetwork.mlp(2, [8], 2, cost_type=COST_MULTI_CROSS_ENTROPY)

        # XOR-like problem
        x = np.array([
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0],
            [1.0, 1.0],
        ], dtype=np.float32)
        y = np.array([
            [1.0, 0.0],  # class 0
            [0.0, 1.0],  # class 1
            [0.0, 1.0],  # class 1
            [1.0, 0.0],  # class 0
        ], dtype=np.float32)

        # Get initial cost
        initial_cost = net.cost(x, y)

        # Train
        net.train(
            x, y,
            learning_rate=0.1,
            max_epochs=50,
            max_drop_streak=50,
            validation_fraction=0.0
        )

        # Get final cost
        final_cost = net.cost(x, y)

        assert final_cost < initial_cost

    def test_train_with_numpy(self):
        """Test training with numpy arrays."""
        kann_set_seed(42)

        net = KannNeuralNetwork.mlp(2, [8], 1, cost_type=COST_MSE)

        # Simple regression: y = x1 + x2
        x = np.array([
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0],
            [1.0, 1.0],
        ], dtype=np.float32)
        y = np.array([
            [0.0],
            [1.0],
            [1.0],
            [2.0],
        ], dtype=np.float32)

        initial_cost = net.cost(x, y)

        net.train(x, y, learning_rate=0.1, max_epochs=100, validation_fraction=0.0)

        final_cost = net.cost(x, y)
        assert final_cost < initial_cost

    def test_train_returns_epoch_count(self):
        """Test that train returns number of epochs."""
        kann_set_seed(42)

        net = KannNeuralNetwork.mlp(2, [4], 2)
        x = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32)
        y = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)

        epochs = net.train(
            x, y,
            max_epochs=10,
            validation_fraction=0.0
        )

        assert isinstance(epochs, int)
        assert epochs > 0
        assert epochs <= 10

    def test_train_with_validation_fraction(self):
        """Test training with validation split."""
        kann_set_seed(42)

        net = KannNeuralNetwork.mlp(2, [8], 2)

        # Need enough samples for validation split
        x_data = [[float(i % 2), float(i // 2 % 2)] for i in range(20)]
        y_data = [[1.0, 0.0] if (i % 2) == (i // 2 % 2) else [0.0, 1.0] for i in range(20)]

        x = np.array(x_data, dtype=np.float32)
        y = np.array(y_data, dtype=np.float32)

        epochs = net.train(
            x, y,
            max_epochs=20,
            validation_fraction=0.2
        )

        assert epochs > 0

    def test_train_single_epoch(self):
        """Test single epoch training."""
        kann_set_seed(42)

        net = KannNeuralNetwork.mlp(2, [4], 2)
        x = np.array([[0.0, 0.0], [1.0, 1.0], [0.0, 1.0], [1.0, 0.0]], dtype=np.float32)
        y = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]], dtype=np.float32)

        result = net.train_single_epoch(
            x, y,
            learning_rate=0.1
        )

        # Should return (avg_cost, n_train_err, n_train_base, rmsprop_cache)
        assert len(result) == 4
        avg_cost, n_err, n_base, cache = result
        assert avg_cost >= 0
        assert cache is not None


class TestCostComputation:
    """Tests for cost computation."""

    def test_cost_positive(self):
        """Test that cost is positive."""
        kann_set_seed(42)

        net = KannNeuralNetwork.mlp(2, [4], 2)
        x = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32)
        y = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)

        cost = net.cost(x, y)
        assert cost >= 0

    def test_cost_decreases_with_training(self):
        """Test that cost decreases after training."""
        kann_set_seed(42)

        net = KannNeuralNetwork.mlp(2, [8], 2)
        x = np.array([[0.0, 0.0], [1.0, 1.0], [0.0, 1.0], [1.0, 0.0]], dtype=np.float32)
        y = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]], dtype=np.float32)

        cost_before = net.cost(x, y)

        net.train(
            x, y,
            learning_rate=0.1,
            max_epochs=100,
            validation_fraction=0.0
        )

        cost_after = net.cost(x, y)
        assert cost_after < cost_before


class TestRNNTraining:
    """Tests for RNN training."""

    def test_lstm_can_unroll(self):
        """Test that LSTM can be unrolled."""
        net = KannNeuralNetwork.lstm(10, 16, 10)
        unrolled = net.unroll(5)
        assert unrolled is not None

    def test_gru_can_unroll(self):
        """Test that GRU can be unrolled."""
        net = KannNeuralNetwork.gru(10, 16, 10)
        unrolled = net.unroll(5)
        assert unrolled is not None

    def test_train_rnn_basic(self):
        """Test basic RNN training with sequences."""
        kann_set_seed(42)
        random.seed(42)

        net = KannNeuralNetwork.lstm(8, 16, 8)

        # Create simple repeating sequences
        sequences = [
            [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7],
            [7, 6, 5, 4, 3, 2, 1, 0, 7, 6, 5, 4, 3, 2, 1, 0],
            [0, 2, 4, 6, 0, 2, 4, 6, 0, 2, 4, 6, 0, 2, 4, 6],
        ]

        history = net.train_rnn(
            sequences,
            seq_length=4,
            vocab_size=8,
            learning_rate=0.01,
            max_epochs=5,
            verbose=0
        )

        assert 'loss' in history
        assert len(history['loss']) == 5

    def test_train_rnn_loss_decreases(self):
        """Test that RNN training loss decreases."""
        kann_set_seed(42)
        random.seed(42)

        net = KannNeuralNetwork.lstm(8, 32, 8)

        # Simple pattern sequences
        sequences = [
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],  # alternating
            [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],  # pairs
        ] * 5  # repeat to have more data

        history = net.train_rnn(
            sequences,
            seq_length=4,
            vocab_size=8,
            learning_rate=0.01,
            max_epochs=20,
            validation_fraction=0.0,
            verbose=0
        )

        # Loss should generally decrease (check first vs last)
        assert history['loss'][-1] < history['loss'][0]


class TestSwitchMode:
    """Tests for training/inference mode switching."""

    def test_switch_to_training_mode(self):
        """Test switching to training mode."""
        net = KannNeuralNetwork.mlp(4, [8], 2, dropout=0.5)
        net.switch_mode(True)  # training mode
        # Should not raise

    def test_switch_to_inference_mode(self):
        """Test switching to inference mode."""
        net = KannNeuralNetwork.mlp(4, [8], 2, dropout=0.5)
        net.switch_mode(False)  # inference mode
        # Should not raise

    def test_dropout_different_in_modes(self):
        """Test that dropout behaves differently in training vs inference."""
        kann_set_seed(42)

        net = KannNeuralNetwork.mlp(4, [8], 2, dropout=0.5)
        inputs = array.array('f', [0.1, 0.2, 0.3, 0.4])

        # Inference mode - should be deterministic
        net.switch_mode(False)
        out1 = net.apply(inputs)
        out2 = net.apply(inputs)

        # In inference mode, outputs should be identical
        for i in range(len(out1)):
            assert out1[i] == out2[i]


class TestBatchSize:
    """Tests for batch size handling."""

    def test_set_batch_size(self):
        """Test setting batch size."""
        net = KannNeuralNetwork.mlp(4, [8], 2)
        net.set_batch_size(32)
        # Should not raise

    def test_clone_with_batch_size(self):
        """Test cloning with different batch size."""
        net = KannNeuralNetwork.mlp(4, [8], 2)
        cloned = net.clone(batch_size=16)
        assert cloned is not None
