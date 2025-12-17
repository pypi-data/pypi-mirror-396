# cython: language_level=3
# cnn.pyx - CNNNetwork and CNNLayer wrappers

include "_common.pxi"

from . cimport cnn as cnn_c


cdef class CNNLayer:
    """
    Represents a single layer in a convolutional neural network.

    This class wraps the C Layer structure and should not be instantiated directly.
    Use CNNNetwork methods to build layers.
    """
    cdef cnn_c.Layer* _impl
    cdef bint _owns_state

    def __cinit__(self):
        self._impl = NULL
        self._owns_state = False

    def __dealloc__(self):
        # Layers are owned and destroyed by the network, not individual layer objects
        # Only destroy if this layer explicitly owns its state
        if self._owns_state and self._impl != NULL:
            with nogil:
                cnn_c.Layer_destroy(self._impl)
            self._impl = NULL
            self._owns_state = False

    @property
    def layer_id(self):
        """Layer ID in the network."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        return self._impl.lid

    @property
    def shape(self):
        """Layer shape as (depth, width, height)."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        return (self._impl.depth, self._impl.width, self._impl.height)

    @property
    def depth(self):
        """Layer depth dimension."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        return self._impl.depth

    @property
    def width(self):
        """Layer width dimension."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        return self._impl.width

    @property
    def height(self):
        """Layer height dimension."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        return self._impl.height

    @property
    def num_nodes(self):
        """Total number of nodes (depth * width * height)."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        return self._impl.nnodes

    @property
    def num_weights(self):
        """Number of weights in this layer."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        return self._impl.nweights

    @property
    def num_biases(self):
        """Number of biases in this layer."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        return self._impl.nbiases

    @property
    def layer_type(self):
        """Layer type as string: 'input', 'full', or 'conv'."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        if self._impl.ltype == cnn_c.LAYER_INPUT:
            return 'input'
        elif self._impl.ltype == cnn_c.LAYER_FULL:
            return 'full'
        elif self._impl.ltype == cnn_c.LAYER_CONV:
            return 'conv'
        return 'unknown'

    @property
    def kernel_size(self):
        """Kernel size for convolutional layers (raises error for non-conv layers)."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        if self._impl.ltype != cnn_c.LAYER_CONV:
            raise ValueError("kernel_size only available for convolutional layers")
        return self._impl.conv.kernsize

    @property
    def padding(self):
        """Padding for convolutional layers (raises error for non-conv layers)."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        if self._impl.ltype != cnn_c.LAYER_CONV:
            raise ValueError("padding only available for convolutional layers")
        return self._impl.conv.padding

    @property
    def stride(self):
        """Stride for convolutional layers (raises error for non-conv layers)."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        if self._impl.ltype != cnn_c.LAYER_CONV:
            raise ValueError("stride only available for convolutional layers")
        return self._impl.conv.stride

    def get_outputs(self):
        """Get the output values of this layer as a list."""
        if self._impl == NULL:
            raise RuntimeError("layer not initialized")
        cdef int i
        return [self._impl.outputs[i] for i in range(self._impl.nnodes)]


cdef class CNNNetwork:
    """
    A convolutional neural network with support for input, convolutional, and fully-connected layers.

    This class wraps the nn1 CNN C library. Networks are built by chaining layers together
    starting from an input layer.
    """
    cdef cnn_c.Layer* _input_layer
    cdef cnn_c.Layer* _output_layer
    cdef bint _owns_state
    cdef list _layer_refs  # Keep Python references to prevent GC

    def __cinit__(self):
        self._input_layer = NULL
        self._output_layer = NULL
        self._owns_state = False
        self._layer_refs = []

    def __dealloc__(self):
        cdef cnn_c.Layer* current
        cdef cnn_c.Layer* next_layer

        if self._owns_state and self._input_layer != NULL:
            # Destroy all layers starting from the input
            current = self._input_layer
            with nogil:
                while current != NULL:
                    next_layer = current.lnext
                    cnn_c.Layer_destroy(current)
                    current = next_layer
            self._input_layer = NULL
            self._output_layer = NULL
            self._owns_state = False
        self._layer_refs.clear()

    def create_input_layer(self, int depth, int width, int height):
        """
        Create an input layer. This must be called first to start building a network.

        Args:
            depth: Input depth (number of channels)
            width: Input width
            height: Input height

        Returns:
            CNNLayer wrapper for the created layer

        Raises:
            ValueError: If network already has an input layer or dimensions invalid
        """
        if self._input_layer != NULL:
            raise ValueError("network already has an input layer")
        if depth <= 0 or width <= 0 or height <= 0:
            raise ValueError("all dimensions must be positive")

        cdef cnn_c.Layer* layer
        with nogil:
            layer = cnn_c.Layer_create_input(depth, width, height)

        if layer == NULL:
            raise MemoryError("failed to create input layer")

        self._input_layer = layer
        self._output_layer = layer
        self._owns_state = True

        # Create Python wrapper
        cdef CNNLayer py_layer = CNNLayer.__new__(CNNLayer)
        py_layer._impl = layer
        py_layer._owns_state = False  # Network owns the C layer
        self._layer_refs.append(py_layer)

        return py_layer

    def add_conv_layer(self, int depth, int width, int height,
                       int kernel_size, int padding=0, int stride=1, double std=0.1):
        """
        Add a convolutional layer to the network.

        Args:
            depth: Number of output channels (filters)
            width: Output width
            height: Output height
            kernel_size: Size of the convolution kernel (must be odd)
            padding: Padding size (default: 0)
            stride: Stride for convolution (default: 1)
            std: Standard deviation for weight initialization (default: 0.1)

        Returns:
            CNNLayer wrapper for the created layer

        Raises:
            ValueError: If network has no input layer or parameters are invalid
            MemoryError: If layer creation fails
        """
        if self._output_layer == NULL:
            raise ValueError("must create input layer first")
        if depth <= 0 or width <= 0 or height <= 0:
            raise ValueError("all dimensions must be positive")
        if kernel_size <= 0 or kernel_size % 2 == 0:
            raise ValueError("kernel_size must be positive and odd")
        if stride <= 0:
            raise ValueError("stride must be positive")

        cdef cnn_c.Layer* layer
        with nogil:
            layer = cnn_c.Layer_create_conv(
                self._output_layer, depth, width, height,
                kernel_size, padding, stride, std)

        if layer == NULL:
            raise MemoryError("failed to create convolutional layer")

        self._output_layer = layer

        # Create Python wrapper
        cdef CNNLayer py_layer = CNNLayer.__new__(CNNLayer)
        py_layer._impl = layer
        py_layer._owns_state = False  # Network owns the C layer
        self._layer_refs.append(py_layer)

        return py_layer

    def add_full_layer(self, int num_nodes, double std=0.1):
        """
        Add a fully-connected layer to the network.

        Args:
            num_nodes: Number of nodes in this layer
            std: Standard deviation for weight initialization (default: 0.1)

        Returns:
            CNNLayer wrapper for the created layer

        Raises:
            ValueError: If network has no input layer or num_nodes invalid
            MemoryError: If layer creation fails
        """
        if self._output_layer == NULL:
            raise ValueError("must create input layer first")
        if num_nodes <= 0:
            raise ValueError("num_nodes must be positive")

        cdef cnn_c.Layer* layer
        with nogil:
            layer = cnn_c.Layer_create_full(self._output_layer, num_nodes, std)

        if layer == NULL:
            raise MemoryError("failed to create fully-connected layer")

        self._output_layer = layer

        # Create Python wrapper
        cdef CNNLayer py_layer = CNNLayer.__new__(CNNLayer)
        py_layer._impl = layer
        py_layer._owns_state = False  # Network owns the C layer
        self._layer_refs.append(py_layer)

        return py_layer

    @property
    def input_shape(self):
        """Shape of the input layer as (depth, width, height)."""
        if self._input_layer == NULL:
            raise RuntimeError("network has no input layer")
        return (self._input_layer.depth, self._input_layer.width, self._input_layer.height)

    @property
    def output_size(self):
        """Number of output nodes in the final layer."""
        if self._output_layer == NULL:
            raise RuntimeError("network has no layers")
        return self._output_layer.nnodes

    @property
    def num_layers(self):
        """Total number of layers in the network."""
        if self._input_layer == NULL:
            return 0
        return len(self._layer_refs)

    @property
    def layers(self):
        """List of all layer wrappers in the network."""
        return list(self._layer_refs)

    cpdef list predict(self, object inputs):
        """
        Make a prediction given input values.

        Args:
            inputs: Input values (length must match input layer size: depth * width * height)

        Returns:
            List of output values from the final layer

        Raises:
            RuntimeError: If network has no layers
            ValueError: If input size doesn't match
        """
        if self._input_layer == NULL:
            raise RuntimeError("network has no input layer")
        if self._output_layer == NULL:
            raise RuntimeError("network has no output layer")

        # Convert to memoryview
        cdef double[::1] input_mv
        try:
            input_mv = inputs
        except (TypeError, ValueError):
            input_mv = array.array('d', inputs)

        cdef int expected_size = self._input_layer.nnodes
        if input_mv.shape[0] != expected_size:
            raise ValueError(
                f"expected {expected_size} input values, received {input_mv.shape[0]}"
            )

        # Set inputs and perform forward pass
        with nogil:
            cnn_c.Layer_setInputs(self._input_layer, &input_mv[0])

        # Get outputs from final layer
        cdef int output_size = self._output_layer.nnodes
        cdef int i
        return [self._output_layer.outputs[i] for i in range(output_size)]

    cpdef double train(self, object inputs, object targets, double learning_rate):
        """
        Train the network on one example using backpropagation.

        Args:
            inputs: Input values (length must match input layer size)
            targets: Target output values (length must match output layer size)
            learning_rate: Learning rate for weight updates

        Returns:
            Total squared error for this training example

        Raises:
            RuntimeError: If network has no layers
            ValueError: If input or target size doesn't match
        """
        if self._input_layer == NULL:
            raise RuntimeError("network has no input layer")
        if self._output_layer == NULL:
            raise RuntimeError("network has no output layer")

        # Convert inputs to memoryview
        cdef double[::1] input_mv
        try:
            input_mv = inputs
        except (TypeError, ValueError):
            input_mv = array.array('d', inputs)

        # Convert targets to memoryview
        cdef double[::1] target_mv
        try:
            target_mv = targets
        except (TypeError, ValueError):
            target_mv = array.array('d', targets)

        cdef int expected_input_size = self._input_layer.nnodes
        if input_mv.shape[0] != expected_input_size:
            raise ValueError(
                f"expected {expected_input_size} input values, received {input_mv.shape[0]}"
            )

        cdef int expected_output_size = self._output_layer.nnodes
        if target_mv.shape[0] != expected_output_size:
            raise ValueError(
                f"expected {expected_output_size} target values, received {target_mv.shape[0]}"
            )

        cdef double error
        # Perform forward pass, backpropagation, and weight update
        with nogil:
            cnn_c.Layer_setInputs(self._input_layer, &input_mv[0])
            cnn_c.Layer_learnOutputs(self._output_layer, &target_mv[0])
            error = cnn_c.Layer_getErrorTotal(self._output_layer)
            cnn_c.Layer_update(self._output_layer, learning_rate)

        return error

    cpdef double evaluate(self, object inputs, object targets):
        """
        Compute loss without training.

        Args:
            inputs: Input values (length must match input layer size)
            targets: Target output values (length must match output layer size)

        Returns:
            Mean squared error between prediction and targets

        Raises:
            RuntimeError: If network has no layers
            ValueError: If input or target size doesn't match
        """
        if self._input_layer == NULL:
            raise RuntimeError("network has no input layer")
        if self._output_layer == NULL:
            raise RuntimeError("network has no output layer")

        # Convert inputs to memoryview
        cdef double[::1] input_mv
        try:
            input_mv = inputs
        except (TypeError, ValueError):
            input_mv = array.array('d', inputs)

        # Convert targets to memoryview
        cdef double[::1] target_mv
        try:
            target_mv = targets
        except (TypeError, ValueError):
            target_mv = array.array('d', targets)

        cdef int expected_input_size = self._input_layer.nnodes
        if input_mv.shape[0] != expected_input_size:
            raise ValueError(
                f"expected {expected_input_size} input values, received {input_mv.shape[0]}"
            )

        cdef int expected_output_size = self._output_layer.nnodes
        if target_mv.shape[0] != expected_output_size:
            raise ValueError(
                f"expected {expected_output_size} target values, received {target_mv.shape[0]}"
            )

        cdef double error, diff
        cdef int i
        # Perform forward pass only and compute error manually
        with nogil:
            cnn_c.Layer_setInputs(self._input_layer, &input_mv[0])

        # Compute MSE manually
        error = 0.0
        for i in range(expected_output_size):
            diff = self._output_layer.outputs[i] - target_mv[i]
            error += diff * diff
        error /= expected_output_size

        return error

    cpdef dict train_batch(self, list inputs_list, list targets_list, double learning_rate, bint shuffle=False):
        """
        Train on multiple examples in batch.

        Args:
            inputs_list: List of input arrays
            targets_list: List of target arrays
            learning_rate: Learning rate for weight updates
            shuffle: Whether to shuffle the batch before training

        Returns:
            dict with keys: 'mean_loss', 'total_loss', 'count'
        """
        cdef int batch_size = len(inputs_list)
        cdef double total_loss = 0.0
        cdef double loss
        cdef int i
        cdef list indices

        if len(targets_list) != batch_size:
            raise ValueError(
                f"inputs_list and targets_list must have same length: {batch_size} vs {len(targets_list)}"
            )

        if batch_size == 0:
            return {'mean_loss': 0.0, 'total_loss': 0.0, 'count': 0}

        # Create indices for shuffling
        indices = list(range(batch_size))
        if shuffle:
            import random
            random.shuffle(indices)

        # Train on each example
        for i in indices:
            loss = self.train(inputs_list[i], targets_list[i], learning_rate)
            total_loss += loss

        return {
            'mean_loss': total_loss / batch_size,
            'total_loss': total_loss,
            'count': batch_size
        }

    def dump(self):
        """
        Print debug information about all layers to stdout.

        Raises:
            RuntimeError: If network has no layers
        """
        if self._input_layer == NULL:
            raise RuntimeError("network has no input layer")

        cdef cnn_c.Layer* current = self._input_layer
        with nogil:
            while current != NULL:
                cnn_c.Layer_dump(current, stdout)
                current = current.lnext

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager. Cleanup handled by __dealloc__."""
        # Return False to propagate exceptions
        return False
