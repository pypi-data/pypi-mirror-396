# cython: language_level=3
# genann.pyx - GenannNetwork wrapper

include "_common.pxi"

from . cimport genann as genn


cdef class GenannNetwork:
    cdef genn.genann* _impl
    cdef bint _owns_state

    def __cinit__(self, int inputs=0, int hidden_layers=0, int hidden=0, int outputs=0):
        self._owns_state = False
        self._impl = NULL
        # Only validate and build if parameters are provided (not loading)
        if inputs > 0 or hidden_layers > 0 or hidden > 0 or outputs > 0:
            if inputs <= 0 or hidden_layers <= 0 or hidden <= 0 or outputs <= 0:
                raise ValueError("network dimensions must be positive")
            # Release GIL during network construction
            with nogil:
                self._impl = genn.genann_init(inputs, hidden_layers, hidden, outputs)
            if self._impl == NULL:
                raise MemoryError("failed to allocate genann network")
            self._owns_state = True

    def __dealloc__(self):
        if self._owns_state and self._impl != NULL:
            # Release GIL during cleanup
            with nogil:
                genn.genann_free(self._impl)
            self._impl = NULL
            self._owns_state = False

    @property
    def input_size(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return self._impl.inputs

    @property
    def hidden_layers(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return self._impl.hidden_layers

    @property
    def hidden_size(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return self._impl.hidden

    @property
    def output_size(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return self._impl.outputs

    @property
    def shape(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return (self._impl.inputs, self._impl.hidden_layers, self._impl.hidden, self._impl.outputs)

    @property
    def total_weights(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return self._impl.total_weights

    @property
    def total_neurons(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        return self._impl.total_neurons

    cpdef double train(self, object inputs, object targets, double rate):
        """
        Train the network on one example.

        Args:
            inputs: Input values
            targets: Target output values
            rate: Learning rate

        Returns:
            Mean squared error for this training example
        """
        if self._impl == NULL:
            raise RuntimeError("network not initialized")

        # Convert to memoryview - handles buffer protocol objects
        cdef double[::1] input_mv
        cdef double[::1] target_mv
        cdef const double* output_ptr
        cdef double error, diff
        cdef int i, nops

        # Try to create memoryview from input
        try:
            input_mv = inputs
        except (TypeError, ValueError):
            # Not a buffer, convert via array.array
            input_mv = array.array('d', inputs)

        try:
            target_mv = targets
        except (TypeError, ValueError):
            # Not a buffer, convert via array.array
            target_mv = array.array('d', targets)

        if input_mv.shape[0] != self._impl.inputs:
            raise ValueError(
                f"expected {self._impl.inputs} input values, received {input_mv.shape[0]}"
            )
        if target_mv.shape[0] != self._impl.outputs:
            raise ValueError(
                f"expected {self._impl.outputs} target values, received {target_mv.shape[0]}"
            )

        nops = self._impl.outputs

        # Release GIL during expensive C computation
        # First get outputs to compute error, then train
        with nogil:
            output_ptr = genn.genann_run(self._impl, &input_mv[0])
            error = 0.0
            for i in range(nops):
                diff = output_ptr[i] - target_mv[i]
                error += diff * diff
            error /= nops
            genn.genann_train(self._impl, &input_mv[0], &target_mv[0], rate)

        return error

    cpdef double evaluate(self, object inputs, object targets):
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
        cdef double[::1] input_mv
        cdef double[::1] target_mv
        cdef const double* output_ptr
        cdef double error, diff
        cdef int i, nops

        try:
            input_mv = inputs
        except (TypeError, ValueError):
            input_mv = array.array('d', inputs)

        try:
            target_mv = targets
        except (TypeError, ValueError):
            target_mv = array.array('d', targets)

        if input_mv.shape[0] != self._impl.inputs:
            raise ValueError(
                f"expected {self._impl.inputs} input values, received {input_mv.shape[0]}"
            )
        if target_mv.shape[0] != self._impl.outputs:
            raise ValueError(
                f"expected {self._impl.outputs} target values, received {target_mv.shape[0]}"
            )

        nops = self._impl.outputs

        # Run prediction and compute MSE
        with nogil:
            output_ptr = genn.genann_run(self._impl, &input_mv[0])
            error = 0.0
            for i in range(nops):
                diff = output_ptr[i] - target_mv[i]
                error += diff * diff
            error /= nops

        return error

    cpdef dict train_batch(self, list inputs_list, list targets_list, double rate, bint shuffle=False):
        """
        Train on multiple examples in batch.

        Args:
            inputs_list: List of input arrays
            targets_list: List of target arrays
            rate: Learning rate
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
            loss = self.train(inputs_list[i], targets_list[i], rate)
            total_loss += loss

        return {
            'mean_loss': total_loss / batch_size,
            'total_loss': total_loss,
            'count': batch_size
        }

    cpdef list predict(self, object inputs):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")

        # Convert to memoryview - handles buffer protocol objects
        cdef double[::1] input_mv
        cdef const double* output_ptr
        cdef int i, nops

        # Try to create memoryview from input
        try:
            input_mv = inputs
        except (TypeError, ValueError):
            # Not a buffer, convert via array.array
            input_mv = array.array('d', inputs)

        if input_mv.shape[0] != self._impl.inputs:
            raise ValueError(
                f"expected {self._impl.inputs} input values, received {input_mv.shape[0]}"
            )

        nops = self._impl.outputs

        # Release GIL during expensive C computation
        with nogil:
            output_ptr = genn.genann_run(self._impl, &input_mv[0])

        # Build output list (requires GIL)
        return [output_ptr[i] for i in range(nops)]

    cpdef void randomize(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        # Release GIL during randomization
        with nogil:
            genn.genann_randomize(self._impl)

    def copy(self):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        cdef GenannNetwork new_network = GenannNetwork.__new__(GenannNetwork)
        new_network._owns_state = False
        # Release GIL during copy
        with nogil:
            new_network._impl = genn.genann_copy(self._impl)
        if new_network._impl == NULL:
            raise MemoryError("failed to copy genann network")
        new_network._owns_state = True
        return new_network

    cpdef void save(self, object path):
        if self._impl == NULL:
            raise RuntimeError("network not initialized")
        cdef bytes encoded = _as_bytes_path(path)
        cdef const char* c_path = encoded
        # Open file for writing
        cdef FILE* file_ptr
        with nogil:
            file_ptr = fopen(c_path, b"w")
        if file_ptr == NULL:
            raise IOError(f"failed to open file for writing: {path}")
        try:
            with nogil:
                genn.genann_write(self._impl, file_ptr)
        finally:
            with nogil:
                fclose(file_ptr)

    @classmethod
    def load(cls, object path):
        cdef GenannNetwork instance = cls.__new__(cls)
        instance._owns_state = False
        instance._impl = NULL
        cdef bytes encoded = _as_bytes_path(path)
        cdef const char* c_path = encoded
        # Open file for reading
        cdef FILE* file_ptr
        with nogil:
            file_ptr = fopen(c_path, b"r")
        if file_ptr == NULL:
            raise IOError(f"failed to open file for reading: {path}")
        try:
            with nogil:
                instance._impl = genn.genann_read(file_ptr)
        finally:
            with nogil:
                fclose(file_ptr)
        if instance._impl == NULL:
            raise ValueError(f"failed to load genann network from {path}")
        instance._owns_state = True
        return instance

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager. Cleanup handled by __dealloc__."""
        # Return False to propagate exceptions
        return False
