# cython: language_level=3
# fann.pyx - FannNetwork wrapper for FANN library (float32)

include "_common.pxi"

from . cimport ffann


cdef class FannNetwork:
    cdef ffann.fann* _impl
    cdef bint _owns_state

    def __cinit__(self, layers=None, connection_rate=1.0):
        cdef unsigned int num_layers
        cdef unsigned int* layer_array
        cdef unsigned int i
        cdef float c_rate
        cdef bint is_fully_connected

        self._owns_state = False
        self._impl = NULL

        if layers is not None:
            if not isinstance(layers, (list, tuple)):
                raise TypeError("layers must be a list or tuple")
            if len(layers) < 2:
                raise ValueError("network must have at least 2 layers (input and output)")
            for size in layers:
                if size <= 0:
                    raise ValueError("all layer sizes must be positive")

            num_layers = len(layers)
            c_rate = connection_rate
            is_fully_connected = (c_rate >= 1.0)
            layer_array = <unsigned int*>malloc(num_layers * sizeof(unsigned int))
            if layer_array == NULL:
                raise MemoryError("failed to allocate layer array")

            try:
                for i in range(num_layers):
                    layer_array[i] = layers[i]

                # Release GIL during network construction
                with nogil:
                    if is_fully_connected:
                        self._impl = ffann.fann_create_standard_array(num_layers, layer_array)
                    else:
                        self._impl = ffann.fann_create_sparse_array(c_rate, num_layers, layer_array)

                if self._impl == NULL:
                    raise MemoryError("failed to allocate FANN network")
                self._owns_state = True
            finally:
                free(layer_array)

    def __dealloc__(self):
        if self._owns_state and self._impl != NULL:
            # Release GIL during cleanup
            with nogil:
                ffann.fann_destroy(self._impl)
            self._impl = NULL
            self._owns_state = False

    @property
    def input_size(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return ffann.fann_get_num_input(self._impl)

    @property
    def output_size(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return ffann.fann_get_num_output(self._impl)

    @property
    def total_neurons(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return ffann.fann_get_total_neurons(self._impl)

    @property
    def total_connections(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return ffann.fann_get_total_connections(self._impl)

    @property
    def num_layers(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return ffann.fann_get_num_layers(self._impl)

    @property
    def layers(self):
        cdef unsigned int num_layers
        cdef unsigned int* layer_array
        cdef unsigned int i

        if self._impl == NULL:
            raise RuntimeError("network not initialized")

        num_layers = ffann.fann_get_num_layers(self._impl)
        layer_array = <unsigned int*>malloc(num_layers * sizeof(unsigned int))
        if layer_array == NULL:
            raise MemoryError("failed to allocate layer array")
        try:
            ffann.fann_get_layer_array(self._impl, layer_array)
            return [layer_array[i] for i in range(num_layers)]
        finally:
            free(layer_array)

    @property
    def learning_rate(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return ffann.fann_get_learning_rate(self._impl)

    @learning_rate.setter
    def learning_rate(self, float rate):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        ffann.fann_set_learning_rate(self._impl, rate)

    @property
    def learning_momentum(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return ffann.fann_get_learning_momentum(self._impl)

    @learning_momentum.setter
    def learning_momentum(self, float momentum):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        ffann.fann_set_learning_momentum(self._impl, momentum)

    cpdef list predict(self, object inputs):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")

        # Convert to memoryview - handles buffer protocol objects
        cdef float[::1] input_mv
        cdef ffann.fann_type* output_ptr
        cdef int i
        cdef unsigned int num_outputs

        # Try to create memoryview from input
        try:
            input_mv = inputs
        except (TypeError, ValueError):
            # Not a buffer, convert via array.array
            input_mv = array.array('f', inputs)

        if input_mv.shape[0] != self._impl.num_input:
            raise ValueError(
                f"expected {self._impl.num_input} input values, received {input_mv.shape[0]}"
            )

        num_outputs = self._impl.num_output

        # Release GIL during expensive C computation
        with nogil:
            output_ptr = ffann.fann_run(self._impl, &input_mv[0])

        # Build output list (requires GIL)
        return [output_ptr[i] for i in range(num_outputs)]

    cpdef float train(self, object inputs, object targets):
        """
        Train the network on one example.

        Args:
            inputs: Input values
            targets: Target output values

        Returns:
            Mean squared error for this training example
        """
        if self._impl == NULL:
            raise RuntimeError("network not initialized")

        # Convert to memoryview - handles buffer protocol objects
        cdef float[::1] input_mv
        cdef float[::1] target_mv
        cdef ffann.fann_type* output_ptr
        cdef float error, diff
        cdef int i
        cdef unsigned int num_outputs

        # Try to create memoryview from input
        try:
            input_mv = inputs
        except (TypeError, ValueError):
            # Not a buffer, convert via array.array
            input_mv = array.array('f', inputs)

        try:
            target_mv = targets
        except (TypeError, ValueError):
            # Not a buffer, convert via array.array
            target_mv = array.array('f', targets)

        if input_mv.shape[0] != self._impl.num_input:
            raise ValueError(
                f"expected {self._impl.num_input} input values, received {input_mv.shape[0]}"
            )
        if target_mv.shape[0] != self._impl.num_output:
            raise ValueError(
                f"expected {self._impl.num_output} target values, received {target_mv.shape[0]}"
            )

        num_outputs = self._impl.num_output

        # Release GIL during expensive C computation
        # First get outputs to compute error, then train
        with nogil:
            output_ptr = ffann.fann_run(self._impl, &input_mv[0])
            error = 0.0
            for i in range(num_outputs):
                diff = output_ptr[i] - target_mv[i]
                error += diff * diff
            error /= num_outputs
            ffann.fann_train(self._impl, &input_mv[0], &target_mv[0])

        return error

    cpdef float evaluate(self, object inputs, object targets):
        """
        Compute loss without training.

        Args:
            inputs: Input values
            targets: Target output values

        Returns:
            Mean squared error between prediction and targets
        """
        if self._impl == NULL:
            raise RuntimeError("network not initialized")

        # Convert to memoryview
        cdef float[::1] input_mv
        cdef float[::1] target_mv
        cdef ffann.fann_type* output_ptr
        cdef float error, diff
        cdef int i
        cdef unsigned int num_outputs

        try:
            input_mv = inputs
        except (TypeError, ValueError):
            input_mv = array.array('f', inputs)

        try:
            target_mv = targets
        except (TypeError, ValueError):
            target_mv = array.array('f', targets)

        if input_mv.shape[0] != self._impl.num_input:
            raise ValueError(
                f"expected {self._impl.num_input} input values, received {input_mv.shape[0]}"
            )
        if target_mv.shape[0] != self._impl.num_output:
            raise ValueError(
                f"expected {self._impl.num_output} target values, received {target_mv.shape[0]}"
            )

        num_outputs = self._impl.num_output

        # Run prediction and compute MSE
        with nogil:
            output_ptr = ffann.fann_run(self._impl, &input_mv[0])
            error = 0.0
            for i in range(num_outputs):
                diff = output_ptr[i] - target_mv[i]
                error += diff * diff
            error /= num_outputs

        return error

    cpdef dict train_batch(self, list inputs_list, list targets_list, bint shuffle=False):
        """
        Train on multiple examples in batch.

        Args:
            inputs_list: List of input arrays
            targets_list: List of target arrays
            shuffle: Whether to shuffle the batch before training

        Returns:
            dict with keys: 'mean_loss', 'total_loss', 'count'
        """
        cdef int batch_size = len(inputs_list)
        cdef float total_loss = 0.0
        cdef float loss
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
            loss = self.train(inputs_list[i], targets_list[i])
            total_loss += loss

        return {
            'mean_loss': total_loss / batch_size,
            'total_loss': total_loss,
            'count': batch_size
        }

    cpdef void randomize_weights(self, float min_weight=-0.1, float max_weight=0.1):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        # Release GIL during randomization
        with nogil:
            ffann.fann_randomize_weights(self._impl, min_weight, max_weight)

    def copy(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        cdef FannNetwork new_network = FannNetwork.__new__(FannNetwork)
        new_network._owns_state = False
        # Release GIL during copy
        with nogil:
            new_network._impl = ffann.fann_copy(self._impl)
        if new_network._impl == NULL:
            raise MemoryError("failed to copy FANN network")
        new_network._owns_state = True
        return new_network

    cpdef void save(self, object path):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        cdef bytes encoded = _as_bytes_path(path)
        cdef const char* c_path = encoded
        cdef int result
        # Release GIL during file I/O
        with nogil:
            result = ffann.fann_save(self._impl, c_path)
        if result == -1:
            raise IOError(f"failed to save FANN network to {path}")

    @classmethod
    def load(cls, object path):
        cdef FannNetwork instance = cls.__new__(cls)
        instance._owns_state = False
        instance._impl = NULL
        cdef bytes encoded = _as_bytes_path(path)
        cdef const char* c_path = encoded
        # Release GIL during file I/O
        with nogil:
            instance._impl = ffann.fann_create_from_file(c_path)
        if instance._impl == NULL:
            raise IOError(f"failed to load FANN network from {path}")
        instance._owns_state = True
        return instance

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager. Cleanup handled by __dealloc__."""
        # Return False to propagate exceptions
        return False
