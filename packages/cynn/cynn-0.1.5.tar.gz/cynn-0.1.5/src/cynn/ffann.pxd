
cdef extern from "floatfann.h":

    ctypedef float fann_type

    cdef struct fann:
        # Basic network properties
        unsigned int num_input
        unsigned int num_output
        unsigned int total_neurons
        unsigned int total_connections
        # Learning parameters
        float learning_rate
        float learning_momentum
        float connection_rate
        # Internal pointers (not accessed directly from Python)
        fann_type* weights
        fann_type* output

    # Network creation and destruction
    cdef fann* fann_create_standard_array(unsigned int num_layers, const unsigned int* layers) nogil
    cdef fann* fann_create_sparse_array(float connection_rate, unsigned int num_layers, const unsigned int* layers) nogil
    cdef fann* fann_copy(fann* ann) nogil
    cdef void fann_destroy(fann* ann) nogil

    # Training and prediction
    cdef fann_type* fann_run(fann* ann, fann_type* input) nogil
    cdef void fann_train(fann* ann, fann_type* input, fann_type* desired_output) nogil
    cdef void fann_randomize_weights(fann* ann, fann_type min_weight, fann_type max_weight) nogil

    # File I/O
    cdef fann* fann_create_from_file(const char* configuration_file) nogil
    cdef int fann_save(fann* ann, const char* configuration_file) nogil

    # Network queries
    cdef unsigned int fann_get_num_input(fann* ann) nogil
    cdef unsigned int fann_get_num_output(fann* ann) nogil
    cdef unsigned int fann_get_total_neurons(fann* ann) nogil
    cdef unsigned int fann_get_total_connections(fann* ann) nogil
    cdef unsigned int fann_get_num_layers(fann* ann) nogil
    cdef void fann_get_layer_array(fann* ann, unsigned int* layers) nogil

    # Learning parameter accessors
    cdef float fann_get_learning_rate(fann* ann) nogil
    cdef void fann_set_learning_rate(fann* ann, float learning_rate) nogil
    cdef float fann_get_learning_momentum(fann* ann) nogil
    cdef void fann_set_learning_momentum(fann* ann, float learning_momentum) nogil

