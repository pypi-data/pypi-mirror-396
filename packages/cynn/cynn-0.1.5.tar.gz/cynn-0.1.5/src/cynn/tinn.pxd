cdef extern from "Tinn.h":

    ctypedef struct Tinn:
        # All the weights.
        float* w
        # Hidden to output layer weights.
        float* x
        # Biases.
        float* b
        # Hidden layer.
        float* h
        # Output layer.
        float* o
        # Number of biases - always two - Tinn only supports a single hidden layer.
        int nb
        # Number of weights.
        int nw
        # Number of inputs.
        int nips
        # Number of hidden neurons.
        int nhid
        # Number of outputs.
        int nops

    cdef float* xtpredict(Tinn, const float* in_) nogil
    cdef float xttrain(Tinn, const float* in_, const float* tg, float rate) nogil
    cdef Tinn xtbuild(int nips, int nhid, int nops) nogil
    cdef void xtsave(Tinn, const char* path) nogil
    cdef Tinn xtload(const char* path) nogil
    cdef void xtfree(Tinn) nogil
    cdef void xtprint(const float* arr, const int size) nogil

