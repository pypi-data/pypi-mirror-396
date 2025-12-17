import pytest
from cynn.cnn import CNNNetwork, CNNLayer


class TestNetworkCreation:
    """Test CNN network creation and layer building."""

    def test_create_empty_network(self):
        """Test creating an empty network."""
        net = CNNNetwork()
        assert net is not None
        assert isinstance(net, CNNNetwork)
        assert net.num_layers == 0

    def test_create_input_layer(self):
        """Test creating an input layer."""
        net = CNNNetwork()
        layer = net.create_input_layer(1, 28, 28)
        assert isinstance(layer, CNNLayer)
        assert layer.layer_id == 0
        assert layer.shape == (1, 28, 28)
        assert layer.depth == 1
        assert layer.width == 28
        assert layer.height == 28
        assert layer.num_nodes == 1 * 28 * 28
        assert layer.layer_type == 'input'
        assert net.num_layers == 1

    def test_create_input_layer_invalid_dimensions(self):
        """Test that invalid input dimensions raise ValueError."""
        net = CNNNetwork()
        with pytest.raises(ValueError, match="must be positive"):
            net.create_input_layer(0, 28, 28)
        with pytest.raises(ValueError, match="must be positive"):
            net.create_input_layer(1, -5, 28)
        with pytest.raises(ValueError, match="must be positive"):
            net.create_input_layer(1, 28, 0)

    def test_create_duplicate_input_layer(self):
        """Test that creating a second input layer raises ValueError."""
        net = CNNNetwork()
        net.create_input_layer(1, 28, 28)
        with pytest.raises(ValueError, match="already has an input layer"):
            net.create_input_layer(1, 28, 28)

    def test_add_conv_layer(self):
        """Test adding a convolutional layer."""
        net = CNNNetwork()
        net.create_input_layer(1, 28, 28)
        conv = net.add_conv_layer(8, 24, 24, kernel_size=5, stride=1, padding=0)
        assert isinstance(conv, CNNLayer)
        assert conv.layer_id == 1
        assert conv.shape == (8, 24, 24)
        assert conv.layer_type == 'conv'
        assert conv.kernel_size == 5
        assert conv.stride == 1
        assert conv.padding == 0
        assert net.num_layers == 2

    def test_add_conv_layer_no_input(self):
        """Test that adding conv layer without input raises ValueError."""
        net = CNNNetwork()
        with pytest.raises(ValueError, match="must create input layer first"):
            net.add_conv_layer(8, 24, 24, kernel_size=5)

    def test_add_conv_layer_invalid_kernel(self):
        """Test that even kernel size raises ValueError."""
        net = CNNNetwork()
        net.create_input_layer(1, 28, 28)
        with pytest.raises(ValueError, match="must be positive and odd"):
            net.add_conv_layer(8, 24, 24, kernel_size=4)
        with pytest.raises(ValueError, match="must be positive and odd"):
            net.add_conv_layer(8, 24, 24, kernel_size=0)

    def test_add_full_layer(self):
        """Test adding a fully-connected layer."""
        net = CNNNetwork()
        net.create_input_layer(1, 28, 28)
        full = net.add_full_layer(10)
        assert isinstance(full, CNNLayer)
        assert full.layer_id == 1
        assert full.layer_type == 'full'
        assert full.num_nodes == 10
        assert net.num_layers == 2

    def test_add_full_layer_no_input(self):
        """Test that adding full layer without input raises ValueError."""
        net = CNNNetwork()
        with pytest.raises(ValueError, match="must create input layer first"):
            net.add_full_layer(10)

    def test_add_full_layer_invalid_size(self):
        """Test that invalid node count raises ValueError."""
        net = CNNNetwork()
        net.create_input_layer(1, 28, 28)
        with pytest.raises(ValueError, match="must be positive"):
            net.add_full_layer(0)
        with pytest.raises(ValueError, match="must be positive"):
            net.add_full_layer(-5)


class TestNetworkProperties:
    """Test CNN network properties."""

    def test_input_shape(self):
        """Test input_shape property."""
        net = CNNNetwork()
        net.create_input_layer(3, 32, 32)
        assert net.input_shape == (3, 32, 32)

    def test_input_shape_no_input(self):
        """Test input_shape raises error with no input layer."""
        net = CNNNetwork()
        with pytest.raises(RuntimeError, match="no input layer"):
            _ = net.input_shape

    def test_output_size(self):
        """Test output_size property."""
        net = CNNNetwork()
        net.create_input_layer(1, 28, 28)
        net.add_full_layer(10)
        assert net.output_size == 10

    def test_output_size_conv_layer(self):
        """Test output_size with convolutional output layer."""
        net = CNNNetwork()
        net.create_input_layer(1, 28, 28)
        net.add_conv_layer(8, 24, 24, kernel_size=5)
        assert net.output_size == 8 * 24 * 24

    def test_layers_list(self):
        """Test layers property returns list of all layers."""
        net = CNNNetwork()
        net.create_input_layer(1, 28, 28)
        net.add_conv_layer(8, 24, 24, kernel_size=5)
        net.add_full_layer(10)
        layers = net.layers
        assert len(layers) == 3
        assert all(isinstance(layer, CNNLayer) for layer in layers)
        assert layers[0].layer_type == 'input'
        assert layers[1].layer_type == 'conv'
        assert layers[2].layer_type == 'full'


class TestLayerProperties:
    """Test CNNLayer properties and access controls."""

    def test_layer_type_specific_properties_conv(self):
        """Test that conv-specific properties work on conv layers."""
        net = CNNNetwork()
        net.create_input_layer(1, 28, 28)
        conv = net.add_conv_layer(8, 24, 24, kernel_size=5, stride=1, padding=0)
        assert conv.kernel_size == 5
        assert conv.stride == 1
        assert conv.padding == 0

    def test_layer_type_specific_properties_full(self):
        """Test that conv-specific properties raise error on full layers."""
        net = CNNNetwork()
        net.create_input_layer(1, 28, 28)
        full = net.add_full_layer(10)
        with pytest.raises(ValueError, match="only available for convolutional layers"):
            _ = full.kernel_size
        with pytest.raises(ValueError, match="only available for convolutional layers"):
            _ = full.stride
        with pytest.raises(ValueError, match="only available for convolutional layers"):
            _ = full.padding

    def test_layer_type_specific_properties_input(self):
        """Test that conv-specific properties raise error on input layers."""
        net = CNNNetwork()
        inp = net.create_input_layer(1, 28, 28)
        with pytest.raises(ValueError, match="only available for convolutional layers"):
            _ = inp.kernel_size

    def test_layer_weight_counts(self):
        """Test that weight and bias counts are correct."""
        net = CNNNetwork()
        inp = net.create_input_layer(1, 28, 28)
        assert inp.num_weights == 0
        assert inp.num_biases == 0

        conv = net.add_conv_layer(8, 24, 24, kernel_size=5)
        # Conv layer: depth * prev_depth * kernsize * kernsize weights
        # and depth biases
        expected_weights = 8 * 1 * 5 * 5
        assert conv.num_weights == expected_weights
        assert conv.num_biases == 8

        full = net.add_full_layer(10)
        # Full layer: num_nodes * prev_num_nodes weights
        # and num_nodes biases
        expected_weights = 10 * (8 * 24 * 24)
        assert full.num_weights == expected_weights
        assert full.num_biases == 10


class TestPrediction:
    """Test CNN prediction functionality."""

    def test_predict_simple(self):
        """Test basic prediction."""
        net = CNNNetwork()
        net.create_input_layer(1, 4, 4)
        net.add_full_layer(2)
        inputs = [0.5] * 16  # 1 * 4 * 4 = 16 inputs
        outputs = net.predict(inputs)
        assert isinstance(outputs, list)
        assert len(outputs) == 2

    def test_predict_wrong_input_size(self):
        """Test that wrong input size raises ValueError."""
        net = CNNNetwork()
        net.create_input_layer(1, 4, 4)
        net.add_full_layer(2)
        with pytest.raises(ValueError, match="expected 16 input values"):
            net.predict([0.5] * 10)

    def test_predict_no_input_layer(self):
        """Test that predict raises error with no input layer."""
        net = CNNNetwork()
        with pytest.raises(RuntimeError, match="no input layer"):
            net.predict([0.5])

    def test_predict_conv_network(self):
        """Test prediction with convolutional layers."""
        net = CNNNetwork()
        net.create_input_layer(1, 8, 8)
        net.add_conv_layer(4, 6, 6, kernel_size=3, stride=1)
        net.add_full_layer(2)
        inputs = [0.5] * 64  # 1 * 8 * 8 = 64
        outputs = net.predict(inputs)
        assert isinstance(outputs, list)
        assert len(outputs) == 2


class TestTraining:
    """Test CNN training functionality."""

    def test_train_simple(self):
        """Test basic training."""
        net = CNNNetwork()
        net.create_input_layer(1, 4, 4)
        net.add_full_layer(2)
        inputs = [0.5] * 16
        targets = [1.0, 0.0]
        error = net.train(inputs, targets, learning_rate=0.01)
        assert isinstance(error, float)
        assert error >= 0.0

    def test_train_wrong_input_size(self):
        """Test that wrong input size raises ValueError."""
        net = CNNNetwork()
        net.create_input_layer(1, 4, 4)
        net.add_full_layer(2)
        with pytest.raises(ValueError, match="expected 16 input values"):
            net.train([0.5] * 10, [1.0, 0.0], 0.01)

    def test_train_wrong_target_size(self):
        """Test that wrong target size raises ValueError."""
        net = CNNNetwork()
        net.create_input_layer(1, 4, 4)
        net.add_full_layer(2)
        with pytest.raises(ValueError, match="expected 2 target values"):
            net.train([0.5] * 16, [1.0], 0.01)

    def test_train_updates_weights(self):
        """Test that training changes predictions."""
        net = CNNNetwork()
        net.create_input_layer(1, 4, 4)
        net.add_full_layer(2)
        inputs = [0.5] * 16
        targets = [1.0, 0.0]

        pred_before = net.predict(inputs)

        # Train multiple times
        for _ in range(10):
            net.train(inputs, targets, learning_rate=0.1)

        pred_after = net.predict(inputs)

        # Prediction should change
        assert pred_before != pred_after

    def test_train_conv_network(self):
        """Test training with convolutional layers."""
        net = CNNNetwork()
        net.create_input_layer(1, 8, 8)
        net.add_conv_layer(4, 6, 6, kernel_size=3, stride=1)
        net.add_full_layer(2)
        inputs = [0.5] * 64
        targets = [1.0, 0.0]

        error = net.train(inputs, targets, learning_rate=0.01)
        assert isinstance(error, float)
        assert error >= 0.0


class TestComplexNetworks:
    """Test building and using complex CNN architectures."""

    def test_mnist_like_network(self):
        """Test creating a MNIST-like network architecture."""
        net = CNNNetwork()
        net.create_input_layer(1, 28, 28)  # Grayscale 28x28
        net.add_conv_layer(8, 24, 24, kernel_size=5, stride=1)
        net.add_conv_layer(16, 12, 12, kernel_size=5, stride=2)
        net.add_full_layer(10)  # 10 classes

        assert net.num_layers == 4
        assert net.input_shape == (1, 28, 28)
        assert net.output_size == 10

        # Test prediction
        inputs = [0.5] * (28 * 28)
        outputs = net.predict(inputs)
        assert len(outputs) == 10

    def test_multi_conv_layers(self):
        """Test network with multiple convolutional layers."""
        net = CNNNetwork()
        net.create_input_layer(3, 32, 32)  # RGB 32x32
        net.add_conv_layer(16, 30, 30, kernel_size=3, stride=1)
        net.add_conv_layer(32, 28, 28, kernel_size=3, stride=1)
        net.add_conv_layer(64, 14, 14, kernel_size=3, stride=2)
        net.add_full_layer(128)
        net.add_full_layer(10)

        assert net.num_layers == 6
        inputs = [0.5] * (3 * 32 * 32)
        outputs = net.predict(inputs)
        assert len(outputs) == 10
