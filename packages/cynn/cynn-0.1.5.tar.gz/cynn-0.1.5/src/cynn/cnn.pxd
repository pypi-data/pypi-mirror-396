# cython: language_level=3
"""Cython declarations for the CNN C library."""

from libc.stdio cimport FILE

cdef extern from "cnn.h" nogil:
    # Layer types
    ctypedef enum LayerType:
        LAYER_INPUT = 0
        LAYER_FULL = 1
        LAYER_CONV = 2

    # Conv layer params
    ctypedef struct ConvParams:
        int kernsize
        int padding
        int stride

    # Layer structure
    ctypedef struct Layer:
        int lid
        Layer* lprev
        Layer* lnext

        int depth
        int width
        int height

        int nnodes
        double* outputs
        double* gradients
        double* errors

        int nbiases
        double* biases
        double* u_biases

        int nweights
        double* weights
        double* u_weights

        LayerType ltype
        ConvParams conv

    # Layer creation
    Layer* Layer_create_input(int depth, int width, int height)
    Layer* Layer_create_full(Layer* lprev, int nnodes, double std)
    Layer* Layer_create_conv(
        Layer* lprev, int depth, int width, int height,
        int kernsize, int padding, int stride, double std)

    # Layer operations
    void Layer_destroy(Layer* self)
    void Layer_dump(const Layer* self, FILE* fp)
    void Layer_setInputs(Layer* self, const double* values)
    void Layer_getOutputs(const Layer* self, double* outputs)
    double Layer_getErrorTotal(const Layer* self)
    void Layer_learnOutputs(Layer* self, const double* values)
    void Layer_update(Layer* self, double rate)
