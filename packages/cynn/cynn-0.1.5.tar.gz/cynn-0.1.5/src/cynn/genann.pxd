from libc.stdio cimport FILE

cdef extern from "genann.h":

    ctypedef struct genann:
        # How many inputs, outputs, and hidden neurons.
        int inputs
        int hidden_layers
        int hidden
        int outputs
        # Total number of weights, and size of weights buffer.
        int total_weights
        # Total number of neurons + inputs and size of output buffer.
        int total_neurons
        # All weights (total_weights long).
        double* weight
        # Stores input array and output of each neuron (total_neurons long).
        double* output
        # Stores delta of each hidden and output neuron (total_neurons - inputs long).
        double* delta

    cdef genann* genann_init(int inputs, int hidden_layers, int hidden, int outputs) nogil
    cdef void genann_free(genann* ann) nogil
    cdef const double* genann_run(const genann* ann, const double* inputs) nogil
    cdef void genann_train(const genann* ann, const double* inputs, const double* desired_outputs, double learning_rate) nogil
    cdef void genann_randomize(genann* ann) nogil
    cdef genann* genann_copy(const genann* ann) nogil
    cdef void genann_write(const genann* ann, FILE* out) nogil
    cdef genann* genann_read(FILE* in_file) nogil
