"""Tests for KANN neural network basic functionality."""

import pytest
import array
import tempfile
from pathlib import Path

from cynn.kann import (
    KannNeuralNetwork,
    GraphBuilder,
    Array2D,
    KannModelError,
    COST_MSE,
    COST_MULTI_CROSS_ENTROPY,
    COST_BINARY_CROSS_ENTROPY,
    KANN_FLAG_IN,
    KANN_FLAG_OUT,
    RNN_NORM,
    RNN_VAR_H0,
    set_seed as kann_set_seed,
)


class TestMLPCreation:
    """Tests for MLP network creation."""

    def test_create_simple_mlp(self):
        """Test creating a basic MLP."""
        net = KannNeuralNetwork.mlp(
            input_size=4,
            hidden_sizes=[8],
            output_size=2
        )
        assert net is not None
        assert net.input_dim == 4
        assert net.output_dim == 2
        assert net.n_var > 0

    def test_create_deep_mlp(self):
        """Test creating an MLP with multiple hidden layers."""
        net = KannNeuralNetwork.mlp(
            input_size=10,
            hidden_sizes=[32, 16, 8],
            output_size=3
        )
        assert net is not None
        assert net.input_dim == 10
        assert net.output_dim == 3

    def test_create_mlp_with_dropout(self):
        """Test creating an MLP with dropout."""
        net = KannNeuralNetwork.mlp(
            input_size=4,
            hidden_sizes=[8, 4],
            output_size=2,
            dropout=0.2
        )
        assert net is not None
        assert net.input_dim == 4

    def test_create_mlp_with_mse_cost(self):
        """Test creating an MLP with MSE cost function."""
        net = KannNeuralNetwork.mlp(
            input_size=4,
            hidden_sizes=[8],
            output_size=1,
            cost_type=COST_MSE
        )
        assert net is not None

    def test_create_mlp_with_binary_cross_entropy(self):
        """Test creating an MLP with binary cross-entropy cost."""
        net = KannNeuralNetwork.mlp(
            input_size=4,
            hidden_sizes=[8],
            output_size=1,
            cost_type=COST_BINARY_CROSS_ENTROPY
        )
        assert net is not None


class TestRNNCreation:
    """Tests for RNN network creation."""

    def test_create_lstm(self):
        """Test creating an LSTM network."""
        net = KannNeuralNetwork.lstm(
            input_size=10,
            hidden_size=32,
            output_size=10
        )
        assert net is not None
        assert net.input_dim == 10
        assert net.output_dim == 10

    def test_create_gru(self):
        """Test creating a GRU network."""
        net = KannNeuralNetwork.gru(
            input_size=10,
            hidden_size=32,
            output_size=10
        )
        assert net is not None
        assert net.input_dim == 10

    def test_create_simple_rnn(self):
        """Test creating a simple RNN network."""
        net = KannNeuralNetwork.rnn(
            input_size=10,
            hidden_size=32,
            output_size=10
        )
        assert net is not None

    def test_create_lstm_with_flags(self):
        """Test creating LSTM with RNN flags."""
        net = KannNeuralNetwork.lstm(
            input_size=10,
            hidden_size=32,
            output_size=10,
            rnn_flags=RNN_VAR_H0
        )
        assert net is not None


class TestNetworkProperties:
    """Tests for network property access."""

    def test_n_nodes(self):
        """Test accessing number of nodes."""
        net = KannNeuralNetwork.mlp(4, [8], 2)
        assert net.n_nodes > 0

    def test_n_var(self):
        """Test accessing number of trainable variables."""
        net = KannNeuralNetwork.mlp(4, [8], 2)
        # Should have weights and biases
        assert net.n_var > 0

    def test_n_const(self):
        """Test accessing number of constants."""
        net = KannNeuralNetwork.mlp(4, [8], 2)
        # n_const should be >= 0
        assert net.n_const >= 0


class TestInference:
    """Tests for network inference (apply)."""

    def test_apply_with_array(self):
        """Test inference with array.array input."""
        kann_set_seed(42)
        net = KannNeuralNetwork.mlp(4, [8], 3)
        inputs = array.array('f', [0.1, 0.2, 0.3, 0.4])
        output = net.apply(inputs)
        assert len(output) == 3
        # Softmax output should sum to ~1.0
        assert abs(sum(output) - 1.0) < 0.01

    def test_apply_with_numpy(self):
        """Test inference with numpy array input."""
        pytest.importorskip("numpy")
        import numpy as np

        kann_set_seed(42)
        net = KannNeuralNetwork.mlp(4, [8], 3)
        inputs = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
        output = net.apply(inputs)
        assert len(output) == 3

    def test_apply_deterministic(self):
        """Test that inference is deterministic."""
        kann_set_seed(42)
        net = KannNeuralNetwork.mlp(4, [8], 3)
        inputs = array.array('f', [0.1, 0.2, 0.3, 0.4])

        # Switch to inference mode
        net.switch_mode(False)

        output1 = net.apply(inputs)
        output2 = net.apply(inputs)

        for i in range(len(output1)):
            assert output1[i] == output2[i]


class TestSaveLoad:
    """Tests for model persistence."""

    def test_save_creates_file(self, temp_model_path):
        """Test that save creates a file."""
        net = KannNeuralNetwork.mlp(4, [8], 2)
        net.save(str(temp_model_path))
        assert temp_model_path.exists()

    def test_load_restores_network(self, temp_model_path):
        """Test that load restores a working network."""
        kann_set_seed(42)
        net = KannNeuralNetwork.mlp(4, [8], 2)
        inputs = array.array('f', [0.1, 0.2, 0.3, 0.4])
        original_output = net.apply(inputs)

        net.save(str(temp_model_path))
        loaded = KannNeuralNetwork.load(str(temp_model_path))

        loaded_output = loaded.apply(inputs)
        for i in range(len(original_output)):
            assert abs(original_output[i] - loaded_output[i]) < 1e-6

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file raises error."""
        with pytest.raises(KannModelError):
            KannNeuralNetwork.load("/nonexistent/path/model.kann")


class TestClone:
    """Tests for network cloning."""

    def test_clone_creates_copy(self):
        """Test that clone creates a working copy."""
        kann_set_seed(42)
        net = KannNeuralNetwork.mlp(4, [8], 2)
        cloned = net.clone()

        inputs = array.array('f', [0.1, 0.2, 0.3, 0.4])
        output1 = net.apply(inputs)
        output2 = cloned.apply(inputs)

        for i in range(len(output1)):
            assert abs(output1[i] - output2[i]) < 1e-6


class TestContextManager:
    """Tests for context manager protocol."""

    def test_with_statement(self):
        """Test network in with statement."""
        with KannNeuralNetwork.mlp(4, [8], 2) as net:
            inputs = array.array('f', [0.1, 0.2, 0.3, 0.4])
            output = net.apply(inputs)
            assert len(output) == 2

    def test_close_explicit(self):
        """Test explicit close."""
        net = KannNeuralNetwork.mlp(4, [8], 2)
        net.close()
        # After close, operations should fail
        with pytest.raises(KannModelError):
            inputs = array.array('f', [0.1, 0.2, 0.3, 0.4])
            net.apply(inputs)


class TestGraphBuilder:
    """Tests for GraphBuilder custom architectures."""

    def test_build_simple_network(self):
        """Test building a simple network with GraphBuilder."""
        builder = GraphBuilder()
        x = builder.input(4)
        h = builder.dense(x, 8)
        h = builder.relu(h)
        cost = builder.softmax_cross_entropy(h, 2)
        net = builder.build(cost)

        assert net is not None
        assert net.input_dim == 4
        assert net.output_dim == 2

    def test_build_with_sigmoid(self):
        """Test building network with sigmoid activation."""
        builder = GraphBuilder()
        x = builder.input(4)
        h = builder.dense(x, 8)
        h = builder.sigmoid(h)
        cost = builder.sigmoid_cross_entropy(h, 1)
        net = builder.build(cost)
        assert net is not None

    def test_build_with_tanh(self):
        """Test building network with tanh activation."""
        builder = GraphBuilder()
        x = builder.input(4)
        h = builder.dense(x, 8)
        h = builder.tanh(h)
        cost = builder.mse_layer(h, 1)
        net = builder.build(cost)
        assert net is not None

    def test_build_with_dropout(self):
        """Test building network with dropout."""
        builder = GraphBuilder()
        x = builder.input(4)
        h = builder.dense(x, 8)
        h = builder.relu(h)
        h = builder.dropout(h, 0.2)
        h = builder.dense(h, 4)
        cost = builder.softmax_cross_entropy(h, 2)
        net = builder.build(cost)
        assert net is not None

    def test_build_lstm_network(self):
        """Test building LSTM network with GraphBuilder."""
        builder = GraphBuilder()
        x = builder.input(10)
        h = builder.lstm(x, 32)
        cost = builder.softmax_cross_entropy(h, 10)
        net = builder.build(cost)
        assert net is not None

    def test_build_gru_network(self):
        """Test building GRU network with GraphBuilder."""
        builder = GraphBuilder()
        x = builder.input(10)
        h = builder.gru(x, 32)
        cost = builder.softmax_cross_entropy(h, 10)
        net = builder.build(cost)
        assert net is not None


class TestArray2D:
    """Tests for Array2D helper class."""

    def test_create_empty(self):
        """Test creating empty Array2D."""
        arr = Array2D(10, 5)
        assert arr.rows == 10
        assert arr.cols == 5

    def test_getitem_setitem(self):
        """Test indexing operations."""
        arr = Array2D(3, 4)
        arr[1, 2] = 5.0
        assert arr[1, 2] == 5.0

    def test_from_list(self):
        """Test creating from list of lists."""
        data = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
        arr = Array2D.from_list(data)
        assert arr.rows == 3
        assert arr.cols == 2
        assert arr[0, 0] == 1.0
        assert arr[2, 1] == 6.0

    def test_data_property(self):
        """Test accessing underlying data."""
        arr = Array2D(2, 3)
        arr[0, 0] = 1.0
        arr[1, 2] = 2.0
        data = arr.data
        assert len(data) == 6


class TestConstants:
    """Tests for exported constants."""

    def test_cost_constants_exist(self):
        """Test that cost constants are exported."""
        assert COST_MSE is not None
        assert COST_MULTI_CROSS_ENTROPY is not None
        assert COST_BINARY_CROSS_ENTROPY is not None

    def test_flag_constants_exist(self):
        """Test that flag constants are exported."""
        assert KANN_FLAG_IN is not None
        assert KANN_FLAG_OUT is not None

    def test_rnn_flag_constants_exist(self):
        """Test that RNN flag constants are exported."""
        assert RNN_NORM is not None
        assert RNN_VAR_H0 is not None


@pytest.fixture
def temp_model_path():
    """Create a temporary file path for model save/load tests."""
    with tempfile.NamedTemporaryFile(suffix='.kann', delete=False) as f:
        path = Path(f.name)
    yield path
    if path.exists():
        path.unlink()
