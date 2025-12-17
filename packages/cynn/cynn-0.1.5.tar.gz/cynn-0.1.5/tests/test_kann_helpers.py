"""Tests for KANN helper functions and utilities."""

import pytest
import array
import random

from cynn.kann import (
    one_hot_encode,
    one_hot_encode_2d,
    softmax_sample,
    prepare_sequence_data,
    list_to_2d_array,
    Array2D,
    set_seed as kann_set_seed,
    set_verbose as kann_set_verbose,
)


class TestOneHotEncode:
    """Tests for one_hot_encode function."""

    def test_basic_encoding(self):
        """Test basic one-hot encoding."""
        values = array.array('i', [0, 1, 2])
        result = one_hot_encode(values, num_classes=4)

        assert len(result) == 3
        assert list(result[0]) == [1.0, 0.0, 0.0, 0.0]
        assert list(result[1]) == [0.0, 1.0, 0.0, 0.0]
        assert list(result[2]) == [0.0, 0.0, 1.0, 0.0]

    def test_single_value(self):
        """Test encoding a single value."""
        values = array.array('i', [2])
        result = one_hot_encode(values, num_classes=5)

        assert len(result) == 1
        assert list(result[0]) == [0.0, 0.0, 1.0, 0.0, 0.0]

    def test_out_of_range_value(self):
        """Test that out-of-range values produce zero vectors."""
        values = array.array('i', [10])  # out of range
        result = one_hot_encode(values, num_classes=5)

        assert len(result) == 1
        assert list(result[0]) == [0.0, 0.0, 0.0, 0.0, 0.0]

    def test_negative_value(self):
        """Test that negative values produce zero vectors."""
        values = array.array('i', [-1])
        result = one_hot_encode(values, num_classes=5)

        assert len(result) == 1
        assert list(result[0]) == [0.0, 0.0, 0.0, 0.0, 0.0]

    def test_with_numpy(self):
        """Test one-hot encoding with numpy array."""
        np = pytest.importorskip("numpy")
        values = np.array([0, 1, 2], dtype=np.int32)
        result = one_hot_encode(values, num_classes=3)

        assert len(result) == 3


class TestOneHotEncode2D:
    """Tests for one_hot_encode_2d function."""

    def test_basic_encoding(self):
        """Test basic 2D one-hot encoding."""
        values = array.array('i', [0, 1, 2])
        result = one_hot_encode_2d(values, num_classes=4)

        # Result should be flat array of size 3 * 4 = 12
        assert len(result) == 12
        # First row: [1, 0, 0, 0]
        assert list(result[0:4]) == [1.0, 0.0, 0.0, 0.0]
        # Second row: [0, 1, 0, 0]
        assert list(result[4:8]) == [0.0, 1.0, 0.0, 0.0]
        # Third row: [0, 0, 1, 0]
        assert list(result[8:12]) == [0.0, 0.0, 1.0, 0.0]

    def test_returns_array(self):
        """Test that result is array.array."""
        values = array.array('i', [0, 1])
        result = one_hot_encode_2d(values, num_classes=3)
        assert isinstance(result, array.array)


class TestSoftmaxSample:
    """Tests for softmax_sample function."""

    def test_samples_from_distribution(self):
        """Test that sampling returns valid indices."""
        random.seed(42)
        probs = array.array('f', [0.1, 0.2, 0.3, 0.4])

        for _ in range(10):
            idx = softmax_sample(probs)
            assert 0 <= idx < len(probs)

    def test_high_temperature_more_random(self):
        """Test that high temperature produces more uniform distribution."""
        random.seed(42)
        probs = array.array('f', [0.9, 0.05, 0.05])

        # With very high temperature, should sample more uniformly
        samples = [softmax_sample(probs, temperature=10.0) for _ in range(100)]

        # Should have some samples from indices other than 0
        assert any(s != 0 for s in samples)

    def test_low_temperature_more_greedy(self):
        """Test that low temperature is more greedy."""
        random.seed(42)
        probs = array.array('f', [0.6, 0.2, 0.2])

        # With low temperature, should mostly pick highest probability
        samples = [softmax_sample(probs, temperature=0.1) for _ in range(100)]

        # Most samples should be index 0
        count_zero = sum(1 for s in samples if s == 0)
        assert count_zero > 80  # at least 80% should be index 0

    def test_temperature_one_preserves_distribution(self):
        """Test that temperature=1.0 preserves original distribution."""
        random.seed(42)
        probs = array.array('f', [0.5, 0.3, 0.2])

        samples = [softmax_sample(probs, temperature=1.0) for _ in range(1000)]

        # Check rough distribution
        counts = [sum(1 for s in samples if s == i) for i in range(3)]
        # Index 0 should be most common, index 2 least common
        assert counts[0] > counts[1] > counts[2]


class TestPrepareSequenceData:
    """Tests for prepare_sequence_data function."""

    def test_basic_preparation(self):
        """Test basic sequence preparation."""
        sequences = [
            [0, 1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1, 0],
        ]

        x_list, y_list = prepare_sequence_data(
            sequences,
            seq_length=3,
            vocab_size=6
        )

        # Each sequence of length 6 with seq_length 3 produces 3 samples
        # (positions 0, 1, 2 where target is at positions 3, 4, 5)
        assert len(x_list) == 6  # 3 from each sequence

    def test_x_shape(self):
        """Test that x has correct shape."""
        sequences = [[0, 1, 2, 3, 4]]

        x_list, y_list = prepare_sequence_data(
            sequences,
            seq_length=2,
            vocab_size=5
        )

        # x should be flattened one-hot: seq_length * vocab_size
        assert len(x_list[0]) == 2 * 5

    def test_y_shape(self):
        """Test that y has correct shape."""
        sequences = [[0, 1, 2, 3, 4]]

        x_list, y_list = prepare_sequence_data(
            sequences,
            seq_length=2,
            vocab_size=5
        )

        # y should be one-hot of next token: vocab_size
        assert len(y_list[0]) == 5

    def test_y_values(self):
        """Test that y contains correct target values."""
        sequences = [[0, 1, 2]]

        x_list, y_list = prepare_sequence_data(
            sequences,
            seq_length=2,
            vocab_size=3
        )

        # Only one sample: input [0, 1], target 2
        assert len(x_list) == 1
        assert len(y_list) == 1
        # y should be one-hot for class 2
        assert y_list[0][2] == 1.0
        assert sum(y_list[0]) == 1.0

    def test_empty_sequences_raises(self):
        """Test that empty sequences raise error."""
        with pytest.raises(ValueError):
            prepare_sequence_data([], seq_length=2, vocab_size=5)

    def test_short_sequences_skipped(self):
        """Test that sequences shorter than seq_length are skipped."""
        sequences = [
            [0, 1],  # too short for seq_length=3
            [0, 1, 2, 3, 4],  # long enough
        ]

        x_list, y_list = prepare_sequence_data(
            sequences,
            seq_length=3,
            vocab_size=5
        )

        # Only second sequence should contribute samples
        assert len(x_list) == 2  # positions 0 and 1


class TestListTo2DArray:
    """Tests for list_to_2d_array function."""

    def test_basic_conversion(self):
        """Test basic conversion."""
        data = [
            array.array('f', [1.0, 2.0, 3.0]),
            array.array('f', [4.0, 5.0, 6.0]),
        ]

        flat, n_rows, n_cols = list_to_2d_array(data)

        assert n_rows == 2
        assert n_cols == 3
        assert len(flat) == 6
        assert list(flat) == [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

    def test_with_lists(self):
        """Test conversion with Python lists."""
        data = [
            [1.0, 2.0],
            [3.0, 4.0],
            [5.0, 6.0],
        ]

        flat, n_rows, n_cols = list_to_2d_array(data)

        assert n_rows == 3
        assert n_cols == 2

    def test_empty_raises(self):
        """Test that empty list raises error."""
        with pytest.raises(ValueError):
            list_to_2d_array([])


class TestArray2DMemoryview:
    """Tests for Array2D memoryview functionality."""

    def test_as_memoryview(self):
        """Test getting memoryview from Array2D."""
        arr = Array2D(3, 4)
        arr[1, 2] = 5.0

        view = arr.as_memoryview()
        assert view is not None

    def test_memoryview_usable_with_kann(self):
        """Test that numpy arrays work with KANN functions."""
        np = pytest.importorskip("numpy")
        from cynn.kann import KannNeuralNetwork, COST_MSE, set_seed as kann_set_seed

        kann_set_seed(42)
        net = KannNeuralNetwork.mlp(2, [4], 1, cost_type=COST_MSE)

        # Use numpy arrays which provide proper 2D memoryviews
        x = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32)
        y = np.array([[0.0], [1.0]], dtype=np.float32)

        # Should be able to compute cost
        cost = net.cost(x, y)
        assert cost >= 0


class TestKannSetSeed:
    """Tests for kann_set_seed function."""

    def test_reproducibility(self):
        """Test that setting seed produces reproducible results."""
        from cynn.kann import KannNeuralNetwork

        kann_set_seed(12345)
        net1 = KannNeuralNetwork.mlp(4, [8], 2)
        inputs = array.array('f', [0.1, 0.2, 0.3, 0.4])
        out1 = net1.apply(inputs)

        kann_set_seed(12345)
        net2 = KannNeuralNetwork.mlp(4, [8], 2)
        out2 = net2.apply(inputs)

        # Outputs should be identical with same seed
        for i in range(len(out1)):
            assert abs(out1[i] - out2[i]) < 1e-6


class TestKannSetVerbose:
    """Tests for kann_set_verbose function."""

    def test_set_verbose_no_error(self):
        """Test that setting verbose level doesn't raise."""
        kann_set_verbose(0)  # silent
        kann_set_verbose(1)  # normal
        kann_set_verbose(0)  # back to silent
