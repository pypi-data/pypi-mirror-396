# cython: language_level=3
# tinn.pyx - TinnNetwork wrapper

include "_common.pxi"

from . cimport tinn as tinn_c


cdef class TinnNetwork:
    cdef tinn_c.Tinn _impl
    cdef bint _owns_state

    def __cinit__(self, int inputs=0, int hidden=0, int outputs=0):
        self._owns_state = False
        # Only validate and build if parameters are provided (not loading)
        if inputs > 0 or hidden > 0 or outputs > 0:
            if inputs <= 0 or hidden <= 0 or outputs <= 0:
                raise ValueError("network dimensions must be positive")
            # Release GIL during network construction
            with nogil:
                self._impl = tinn_c.xtbuild(inputs, hidden, outputs)
            self._owns_state = True

    def __dealloc__(self):
        if self._owns_state:
            # Release GIL during cleanup
            with nogil:
                tinn_c.xtfree(self._impl)
            self._owns_state = False

    @property
    def input_size(self):
        return self._impl.nips

    @property
    def hidden_size(self):
        return self._impl.nhid

    @property
    def output_size(self):
        return self._impl.nops

    @property
    def shape(self):
        return (self._impl.nips, self._impl.nhid, self._impl.nops)

    cpdef float train(self, object inputs, object targets, float rate):
        # Convert to memoryview - handles buffer protocol objects
        cdef float[::1] input_mv
        cdef float[::1] target_mv
        cdef float result

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

        if input_mv.shape[0] != self._impl.nips:
            raise ValueError(
                f"expected {self._impl.nips} input values, received {input_mv.shape[0]}"
            )
        if target_mv.shape[0] != self._impl.nops:
            raise ValueError(
                f"expected {self._impl.nops} target values, received {target_mv.shape[0]}"
            )

        # Release GIL during expensive C computation
        with nogil:
            result = tinn_c.xttrain(self._impl, &input_mv[0], &target_mv[0], rate)

        return result

    cpdef float evaluate(self, object inputs, object targets):
        """
        Compute loss without training.

        Args:
            inputs: Input values
            targets: Target output values

        Returns:
            Mean squared error between prediction and targets
        """
        # Convert to memoryview
        cdef float[::1] input_mv
        cdef float[::1] target_mv
        cdef float* output_ptr
        cdef float error, diff
        cdef int i, nops

        try:
            input_mv = inputs
        except (TypeError, ValueError):
            input_mv = array.array('f', inputs)

        try:
            target_mv = targets
        except (TypeError, ValueError):
            target_mv = array.array('f', targets)

        if input_mv.shape[0] != self._impl.nips:
            raise ValueError(
                f"expected {self._impl.nips} input values, received {input_mv.shape[0]}"
            )
        if target_mv.shape[0] != self._impl.nops:
            raise ValueError(
                f"expected {self._impl.nops} target values, received {target_mv.shape[0]}"
            )

        nops = self._impl.nops

        # Run prediction and compute MSE
        with nogil:
            output_ptr = tinn_c.xtpredict(self._impl, &input_mv[0])
            error = 0.0
            for i in range(nops):
                diff = output_ptr[i] - target_mv[i]
                error += diff * diff
            error /= nops

        return error

    cpdef dict train_batch(self, list inputs_list, list targets_list, float rate, bint shuffle=False):
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
            loss = self.train(inputs_list[i], targets_list[i], rate)
            total_loss += loss

        return {
            'mean_loss': total_loss / batch_size,
            'total_loss': total_loss,
            'count': batch_size
        }

    cpdef list predict(self, object inputs):
        # Convert to memoryview - handles buffer protocol objects
        cdef float[::1] input_mv
        cdef float* output_ptr
        cdef int i, nops

        # Try to create memoryview from input
        try:
            input_mv = inputs
        except (TypeError, ValueError):
            # Not a buffer, convert via array.array
            input_mv = array.array('f', inputs)

        if input_mv.shape[0] != self._impl.nips:
            raise ValueError(
                f"expected {self._impl.nips} input values, received {input_mv.shape[0]}"
            )

        nops = self._impl.nops

        # Release GIL during expensive C computation
        with nogil:
            output_ptr = tinn_c.xtpredict(self._impl, &input_mv[0])

        # Build output list (requires GIL)
        return [output_ptr[i] for i in range(nops)]

    cpdef void save(self, object path):
        cdef bytes encoded = _as_bytes_path(path)
        cdef const char* c_path = encoded
        # Release GIL during file I/O
        with nogil:
            tinn_c.xtsave(self._impl, c_path)

    @classmethod
    def load(cls, object path):
        cdef TinnNetwork instance = cls.__new__(cls)
        instance._owns_state = False
        cdef bytes encoded = _as_bytes_path(path)
        cdef const char* c_path = encoded
        # Release GIL during file I/O
        with nogil:
            instance._impl = tinn_c.xtload(c_path)
        instance._owns_state = True
        return instance

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager. Cleanup handled by __dealloc__."""
        # Return False to propagate exceptions
        return False
