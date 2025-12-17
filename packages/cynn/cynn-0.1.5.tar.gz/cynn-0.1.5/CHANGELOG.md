# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.5]

### Added

- **Cross-Platform CI/CD Wheel Building** - Full support for building wheels on Linux, macOS, and Windows
  - GitHub Actions workflow (`build-wheels.yml`) using cibuildwheel for Python 3.9-3.13
  - Builds for Linux (x86_64, aarch64), macOS (x86_64, arm64), and Windows (AMD64)
  - Automated testing on all platforms after wheel build
  - Enables publishing to TestPyPI and PyPI via workflow dispatch

- **External Sequence Dataset** - `tests/data/sequences.csv` with 15 mathematical integer sequences
  - Patterns include: forward/reverse counting, Fibonacci mod 8, pi digits, triangular numbers, primes mod 8, Collatz sequence, popcount
  - Used by `kann_lstm_sequence.py` for LSTM sequence prediction training
  - Vocab size computed dynamically from data (currently 10)

- **Comprehensive Example Scripts** - 9 documented examples in `tests/examples/` demonstrating all network types
  - `tinn_xor.py` - TinnNetwork solving XOR problem
  - `genann_iris.py` - GenannNetwork classifying Iris dataset
  - `fann_regression.py` - FannNetwork for regression tasks
  - `cnn_mnist.py` - CNNNetwork for image classification
  - `kann_mlp_iris.py` - KannNeuralNetwork MLP for Iris classification
  - `kann_lstm_sequence.py` - KannNeuralNetwork LSTM for sequence modeling
  - `kann_gru_text.py` - KannNeuralNetwork GRU for text processing
  - `kann_rnn_timeseries.py` - KannNeuralNetwork RNN for time series
  - `kann_text_generation.py` - KannNeuralNetwork for text generation
  - `run_all_examples.py` - Script to execute all examples with summary report
  - `README.md` - Documentation for running and understanding examples

### Changed

- **kann_lstm_sequence.py** - Now loads sequences from external CSV file instead of inline data
  - Added `--data-path` CLI argument to specify custom sequence file
  - Falls back to inline generation if file not found
  - Integrated with `run_all_examples.py` data file handling

### Fixed

- **macOS Cross-Compilation** - Removed `-march=native` from CMakeLists.txt files
  - Was causing "unknown target CPU 'apple-m1'" errors when building x86_64 wheels on ARM runners
  - Affected: tinn, genann, nn1 libraries

- **Linux Shared Object Linking** - Added `-fPIC` to KANN library CMakeLists.txt
  - Static libraries linked into shared objects require position-independent code on Linux

- **Python ABI Compatibility** - Removed `wheel.py-api = "cp312"` from pyproject.toml
  - Was causing module import failures due to ABI tag mismatch between build and runtime Python versions
  - Now builds version-specific wheels for each Python version

- **Windows MSVC Compatibility** - Multiple fixes for Visual Studio builds:
  - Added Windows-compatible headers in `kann_data.c` (`io.h` instead of `unistd.h`)
  - Platform-specific compiler flags using CMake generator expressions (MSVC: `/W4 /O2`, GCC/Clang: `-Wall -Wextra -O3`)
  - Added `FANN_NO_DLL` definition for static library builds (fixes `dllimport` linker errors)
  - Added dummy member to empty struct in `cnn.h` (MSVC requires at least one member)
  - Conditional math library linking (`-lm` not needed on Windows)

- **Windows Test Command** - Changed single quotes to escaped double quotes in pytest `-k` argument
  - Windows cmd doesn't recognize single quotes for argument grouping

- **Windows Timer Resolution** - Changed `time.time()` to `time.perf_counter()` in threading tests
  - `time.time()` has ~15.6ms resolution on Windows, causing fast operations to appear as 0.0 seconds

### Removed

- **FannNetworkDouble class** - Removed due to C symbol conflicts and maintenance complexity
  - Float64 users should use GenannNetwork instead (also float64 precision)
  - Simplifies FANN integration by building only floatfann library
  - Removed `dfann.pxd` declaration file

## [0.1.4]

### Changed

- **Modular Package Structure (BREAKING CHANGE)** - Split monolithic `_core.pyx` into separate modules per library
  - Each network type now has its own `.pyx` file: `tinn.pyx`, `genann.pyx`, `fann.pyx`, `cnn.pyx`, `kann.pyx`
  - Shared code extracted to `_common.pxi` (seed function, path handling utilities)
  - **Import paths changed** - must now import from submodules:
    - `from cynn.tinn import TinnNetwork, seed`
    - `from cynn.genann import GenannNetwork`
    - `from cynn.fann import FannNetwork`
    - `from cynn.cnn import CNNNetwork, CNNLayer`
    - `from cynn.kann import KannNeuralNetwork, GraphBuilder, ...`
  - `__init__.py` no longer exports anything - enables lazy loading (modules only loaded when imported)
  - Benefits: faster startup, reduced memory when using only one network type, cleaner separation

- **Renamed `NeuralNetwork` to `KannNeuralNetwork`** - More explicit naming to distinguish from other network types
  - All factory methods now use `KannNeuralNetwork.mlp()`, `KannNeuralNetwork.lstm()`, etc.
  - This is a **breaking change** for code using the KANN neural network class

- **KannNeuralNetwork path handling** - `save()` and `load()` methods now accept `str`, `bytes`, or `os.PathLike`
  - Consistent with other network types (TinnNetwork, GenannNetwork, etc.)
  - `DataSet.load()` also updated for consistency

## [0.1.3]

### Added

- **KANN Neural Network Library Integration** - Advanced neural networks with LSTM, GRU, and RNN support
  - `NeuralNetwork` class with factory methods for creating MLPs, LSTMs, GRUs, and simple RNNs
  - `NeuralNetwork.mlp()`: Create multi-layer perceptrons with arbitrary hidden layer configuration
  - `NeuralNetwork.lstm()`: Create LSTM networks for sequence modeling
  - `NeuralNetwork.gru()`: Create GRU networks for sequence modeling
  - `NeuralNetwork.rnn()`: Create simple RNN networks
  - Built-in RMSprop optimizer with configurable learning rate
  - Early stopping with validation fraction and max drop streak
  - `train()` method for feedforward networks with automatic train/validation splitting
  - `train_rnn()` method for recurrent networks with backpropagation through time (BPTT)
  - Gradient clipping support for stable RNN training
  - `apply()` method for single-example inference
  - `cost()` method for computing loss over datasets
  - Save/load functionality for trained models
  - `clone()` and `unroll()` methods for RNN manipulation
  - Context manager support (`with` statement)

- **GraphBuilder** - Low-level API for building custom network architectures
  - Create computational graphs with automatic differentiation
  - Layer operations: `input()`, `dense()`, `dropout()`, `layernorm()`
  - Activation functions: `relu()`, `sigmoid()`, `tanh()`, `softmax()`
  - Recurrent layers: `lstm()`, `gru()`, `rnn()`
  - Convolutional layers: `conv1d()`, `conv2d()`
  - Arithmetic operations: `add()`, `sub()`, `mul()`, `matmul()`
  - Cost layers: `softmax_cross_entropy()`, `sigmoid_cross_entropy()`, `mse_layer()`
  - `build()` method to create NeuralNetwork from cost node

- **DataSet** - Wrapper for loading tabular data from TSV files
  - `load()` class method for reading TSV files with row/column names
  - `split_xy()` for separating features and labels
  - `to_2d_array()` for converting to Array2D format
  - Group boundary support for structured data

- **Helper Functions** for sequence modeling
  - `kann_set_seed()`: Set random seed for reproducibility
  - `kann_set_verbose()`: Control verbosity of KANN operations
  - `one_hot_encode()`: Encode integer arrays to one-hot vectors
  - `one_hot_encode_2d()`: Encode to flat 2D buffer format
  - `softmax_sample()`: Sample from probability distribution with temperature
  - `prepare_sequence_data()`: Prepare sequences for RNN training
  - `list_to_2d_array()`: Convert list of arrays to flat array
  - `Array2D`: Simple 2D array wrapper for use with memoryviews

- **KANN Constants** - Exposed for network configuration
  - Cost functions: `COST_BINARY_CROSS_ENTROPY`, `COST_MULTI_CROSS_ENTROPY`, `COST_BINARY_CROSS_ENTROPY_NEG`, `COST_MSE`
  - Node flags: `KANN_FLAG_IN`, `KANN_FLAG_OUT`, `KANN_FLAG_TRUTH`, `KANN_FLAG_COST`
  - RNN flags: `RNN_VAR_H0` (variable initial hidden states), `RNN_NORM` (layer normalization)
  - KAD flags: `KAD_FLAG_VAR`, `KAD_FLAG_CONST`

- **Exception Classes** for KANN-specific error handling
  - `KannError`: Base exception for KANN errors
  - `KannModelError`: Error related to model operations
  - `KannTrainingError`: Error during training

- Vendored KANN C library in `thirdparty/kann/`
- `kann.pyx` Cython implementation for KANN bindings
- `kann.pxd` declaration file for KANN C library API
- Updated CMakeLists.txt to build KANN module with proper include paths
- Comprehensive README.md documentation with usage examples for all KANN features
- Updated comparison table to include NeuralNetwork (KANN)
- Added "Use NeuralNetwork (KANN) when" guidance section

### Fixed

- Fixed Cython compilation error where `kann.pxd` was not found by adding `-I` include path to CMake build

## [0.1.2]

### Added

- **Batch Training Support** - All network types now support efficient batch training
  - `train_batch(inputs_list, targets_list, [rate], shuffle=False)` method for all networks
  - Returns dict with `'mean_loss'`, `'total_loss'`, and `'count'` statistics
  - Optional shuffling for improved convergence
  - Reduces Python/C overhead compared to training examples individually
  - GIL-free execution per training example
  - Comprehensive tests in `tests/test_batch_training.py` (16 new tests)

- **Loss Evaluation Without Training** - All network types now support validation without weight updates
  - `evaluate(inputs, targets)` method for all networks (TinnNetwork, GenannNetwork, FannNetwork, CNNNetwork)
  - Computes mean squared error without modifying network weights
  - Perfect for validation sets and monitoring generalization
  - GIL-free execution
  - Returns same loss type as `train()` (float32 or float64 depending on network)

- **Context Manager Support** - All network types now implement Python's context manager protocol
  - `__enter__()` and `__exit__()` methods for all networks (TinnNetwork, GenannNetwork, FannNetwork, CNNNetwork)
  - Enables use of `with` statement for cleaner, more Pythonic code
  - Networks remain usable after exiting context
  - Automatic resource cleanup via existing `__dealloc__` methods
  - Comprehensive tests in `tests/test_context_managers.py`
  - Type stubs updated with context manager protocol

### Changed

- **Standardized Training Interface (BREAKING CHANGE)** - Consistent return values across all network types
  - `GenannNetwork.train()` now returns `float` (mean squared error) instead of `None`
  - `FannNetwork.train()` now returns `float` (mean squared error) instead of `None`
  - `TinnNetwork.train()` and `CNNNetwork.train()` already returned loss (no change)
  - **Migration**: Code ignoring return values continues to work. Only code explicitly checking for `None` needs updating.
  - All `train()` methods now have consistent semantics: train on one example, return loss

- **Enhanced Documentation**
  - Added "Batch Training", "Evaluating Without Training", "Training with Validation", and "Context Manager Support" sections to README.md
  - Updated API Reference with `evaluate()`, `train_batch()`, `__enter__()`, and `__exit__()` for all network types
  - Updated comparison table to reflect all networks now return loss
  - Added Training API and Context Manager Support sections to CLAUDE.md
  - Updated type stubs in `_core.pyi` for all network classes
  - Created `docs/implementation_summary.md` with detailed usage examples and migration guide

- **Test Suite Enhancements**
  - Updated 13 existing tests to handle new loss return values
  - All 273 tests passing (224 original + 16 batch training tests + 33 context manager tests)
  - Tests cover evaluate(), train_batch(), context managers, shuffling, edge cases, and consistency

### Fixed

- Removed non-existent `square` function from `__init__.py` exports

## [0.1.1]

### Added

- CNNNetwork class wrapping the nn1 Convolutional Neural Network C library
  - Layer-based architecture with support for input, convolutional, and fully-connected layers
  - Flexible network building API with `create_input_layer()`, `add_conv_layer()`, `add_full_layer()`
  - Support for arbitrary CNN architectures (e.g., MNIST-like, multi-conv networks)
  - Float64 precision for all computations
  - Convolutional layer parameters: kernel_size, padding, stride, std for weight initialization
  - Full layer parameters: num_nodes, std for weight initialization
  - CNNLayer class exposing layer properties (shape, type, weights, biases, conv parameters)
  - Network properties: `input_shape`, `output_size`, `num_layers`, `layers`
  - ReLU activation for convolutional layers, Tanh for hidden fully-connected layers, Softmax for output layer
  - GIL-free execution for parallel training and inference
  - Debug functionality with `dump()` method for network introspection
  - 31 comprehensive tests covering creation, validation, training, prediction, and complex architectures
- GenannNetwork class wrapping the GENANN C library
  - Multi-layer neural network support with arbitrary depth
  - Float64 precision for higher accuracy
  - Support for inputs, hidden_layers, hidden neurons per layer, and outputs
  - Additional properties: `total_weights`, `total_neurons`, `hidden_layers`
  - New methods: `randomize()` for re-randomizing weights, `copy()` for deep copying
  - Full buffer protocol support (lists, tuples, arrays, NumPy arrays)
  - GIL-free execution for parallel training and inference
  - Save/load functionality using FILE* based I/O
- FannNetwork class wrapping the FANN (Fast Artificial Neural Network) C library
  - Flexible multi-layer architecture with arbitrary layer configurations
  - Float32 precision for efficient computation
  - Support for fully connected and sparse networks (via connection_rate parameter)
  - Flexible constructor accepting list of layer sizes (e.g., `[2, 4, 3, 1]`)
  - Properties: `input_size`, `output_size`, `total_neurons`, `total_connections`, `num_layers`, `layers`
  - Settable learning parameters: `learning_rate`, `learning_momentum`
  - New methods: `randomize_weights()` for weight initialization, `copy()` for deep copying
  - Full buffer protocol support (lists, tuples, arrays, NumPy arrays)
  - GIL-free execution for parallel training and inference
  - Native FANN format save/load (text-based .fann files)
- Comprehensive type stubs for CNNNetwork, CNNLayer, GenannNetwork, and FannNetwork in _core.pyi
- nn1, GENANN and FANN library integration in CMake build system
- Created `cnn.pxd` for nn1 CNN C library declarations
- API comparison documentation in README.md

### Changed

- Refactored Cython declarations for better modularity and maintainability
  - Split monolithic `nnet.pxd` into library-specific declaration files
  - Created `tinn.pxd` for Tinn C library declarations
  - Created `genann.pxd` for GENANN C library declarations
  - Created `ffann.pxd` for float32 FANN C library declarations
  - Updated `_core.pyx` imports to use new modular declaration files
  - Improved code organization and reduced coupling between neural network backends
- Updated README.md to document TinnNetwork, GenannNetwork, and FannNetwork
- Project description now mentions Tinn, GENANN, and FANN libraries
- Added "Choosing Between Network Implementations" section to README
- Expanded feature comparison table with precision information

## [0.1.0]

### Added

- Initial release
- TinnNetwork class wrapping the Tinn C library
- Basic 3-layer neural network (input, hidden, output)
- Backpropagation training with configurable learning rate
- Save/load functionality for trained models
- Buffer protocol support for various input types
- GIL-free execution for multithreading
- Comprehensive test suite with 54 tests
- Type stubs for static type checking
- CMake-based build system with scikit-build-core
- Thread-safety tests demonstrating parallel execution
- NumPy compatibility tests
