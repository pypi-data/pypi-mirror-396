# cynn

cynn is a thin Cython wrapper around a set of minimal, dependency-free neural network libraries written in C, providing a zero-dependency Python library for learning about neural networks and for embedding lightweight models in applications where large machine-learning frameworks are impractical or unnecessary.

## Overview

cynn provides Python bindings to five lightweight neural network libraries:

- [Tinn](https://github.com/glouw/tinn) – A tiny 3-layer neural network library.
- [GENANN](https://github.com/codeplea/genann) – A minimal multi-layer neural network library.
- [FANN](https://github.com/libfann/fann) – Fast Artificial Neural Network library.
- [nn1](https://github.com/euske/nn1) – Convolutional Neural Network library.
- [kann](https://github.com/attractivechaos/kann) – Multi-layer perceptrons, convolutional neural networks, and recurrent neural networks (including LSTM and GRU).

The project uses Cython to create efficient Python bindings to these C implementations, enabling training and inference with minimal overhead and no dependencies.

## When to Use cynn

- **Learning neural network fundamentals** - Simple C implementations make it easier to understand what's happening compared to opaque framework internals
- **Embedded/resource-constrained environments** - No required dependencies beyond Python and a C compiler (NumPy is optional)
- **Simple prediction tasks** - Small classifiers, basic regression, sequence modeling where a full ML stack is overkill
- **Minimal footprint applications** - Ship trained models without pulling in hundreds of MB of dependencies
- **Parallel inference workloads** - GIL-free execution enables true multithreading for batch predictions

## When NOT to Use cynn

- **Production ML at scale** - Use PyTorch, TensorFlow, or JAX for GPU acceleration and ecosystem support
- **Large datasets** - No GPU parallelism; training is CPU-bound
- **Complex architectures** - Transformers, attention mechanisms, and modern architectures aren't available
- **Pre-trained models** - No ecosystem of pre-trained weights or model hubs
- **Research requiring flexibility** - Framework autograd is far more flexible for novel architectures

## Choosing a Network

| Use Case | Recommended | Why |
|----------|-------------|-----|
| Learning basics | Tinn | Simplest API, single hidden layer, easy to understand |
| Simple classification/regression | Tinn, Genann | Lightweight, fast training |
| Deep feedforward networks | Genann, FANN | Multiple hidden layers, flexible architecture |
| Need momentum/learning rate tuning | FANN | Settable learning parameters |
| Image processing / CNNs | nn1, KANN | Convolutional layer support |
| Sequence modeling (text, time series) | KANN | LSTM, GRU, RNN with BPTT |
| Custom architectures | KANN | GraphBuilder API for computational graphs |
| Numerical precision critical | Genann, nn1 | Float64 precision |
| Memory constrained | Tinn, FANN | Float32, minimal overhead |
| Sparse/partially connected networks | FANN | Configurable connection rate |

### Library Comparison

| Library | Architecture | Precision | Key Strength |
|---------|--------------|-----------|--------------|
| **Tinn** | Fixed 3-layer (in, hidden, out) | float32 | Simplicity |
| **Genann** | Multi-layer MLP | float64 | Deep networks, precision |
| **FANN** | Flexible MLP | float32 | Learning parameters, sparse networks |
| **nn1** | CNN (conv + dense layers) | float64 | Image/spatial data |
| **KANN** | MLP, CNN, LSTM, GRU, RNN | float32 | Recurrent networks, custom graphs |

## Features

- **Five network implementations:**
  - `TinnNetwork`: Simple 3-layer architecture (input, hidden, output) using float32
  - `GenannNetwork`: Flexible multi-layer architecture with arbitrary depth using float64
  - `FannNetwork`: Flexible multi-layer architecture with settable learning parameters using float32
  - `CNNNetwork`: Layer-based convolutional neural network with input, conv, and fully-connected layers using float64
  - `KannNeuralNetwork` (KANN): Advanced neural networks including MLPs, LSTMs, GRUs, and RNNs using float32
- Backpropagation training with configurable learning rate
- Save/load trained models to disk
- Buffer protocol support - works with lists, tuples, array.array, NumPy arrays, etc.
- **GIL-free execution** - true multithreading support for parallel inference/training
- Fast C implementation with Python convenience
- Zero required dependencies (NumPy is optional)

## Installation

### Requirements

- Python >= 3.13
- uv (recommended) or pip
- CMake >= 3.15
- C compiler

### Build from source

```bash
# Clone the repository
git clone https://github.com/shakfu/cynn
cd cynn

# Build and install to a local .venv (using uv)
make
```

## Usage

### Basic Example - TinnNetwork

```python
from cynn.tinn import TinnNetwork

# Create a network: 2 inputs, 4 hidden neurons, 1 output
net = TinnNetwork(2, 4, 1)

# Make a prediction
inputs = [0.5, 0.3]
output = net.predict(inputs)
print(f"Prediction: {output}")

# Train the network
targets = [0.8]
learning_rate = 0.5
loss = net.train(inputs, targets, learning_rate)
print(f"Loss: {loss}")
```

### Basic Example - GenannNetwork

```python
from cynn.genann import GenannNetwork

# Create a network: 2 inputs, 2 hidden layers with 4 neurons each, 1 output
net = GenannNetwork(2, 2, 4, 1)

# Make a prediction
inputs = [0.5, 0.3]
output = net.predict(inputs)
print(f"Prediction: {output}")

# Train the network
targets = [0.8]
learning_rate = 0.1
loss = net.train(inputs, targets, learning_rate)
print(f"Loss: {loss}")

# GenannNetwork has additional features
print(f"Total weights: {net.total_weights}")
print(f"Total neurons: {net.total_neurons}")

# Create a copy of the network
net_copy = net.copy()

# Randomize weights
net.randomize()
```

### Basic Example - CNNNetwork

```python
from cynn.cnn import CNNNetwork

# Create a convolutional neural network
net = CNNNetwork()
net.create_input_layer(1, 28, 28)  # 28x28 grayscale image input
net.add_conv_layer(8, 24, 24, kernel_size=5, stride=1)  # 8 filters, 5x5 kernel
net.add_conv_layer(16, 12, 12, kernel_size=5, stride=2)  # 16 filters, stride 2
net.add_full_layer(10)  # 10 output classes

# Prepare input (flattened 28x28 image)
inputs = [0.5] * (28 * 28)  # 784 values
targets = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # one-hot encoded

# Train the network
error = net.train(inputs, targets, learning_rate=0.01)
print(f"Training error: {error}")

# Make predictions
outputs = net.predict(inputs)
predicted_class = outputs.index(max(outputs))
print(f"Predicted class: {predicted_class}")

# CNNNetwork has additional features
print(f"Network layers: {net.num_layers}")
print(f"Input shape: {net.input_shape}")
print(f"Output size: {net.output_size}")

# Access individual layers
for layer in net.layers:
    print(f"Layer {layer.layer_id}: type={layer.layer_type}, shape={layer.shape}")
```

### Basic Example - FannNetwork

```python
from cynn.fann import FannNetwork

# Create a network: [2 inputs, 4 hidden layer 1, 3 hidden layer 2, 1 output]
net = FannNetwork([2, 4, 3, 1])

# Make a prediction
inputs = [0.5, 0.3]
output = net.predict(inputs)
print(f"Prediction: {output}")

# Adjust learning parameters
net.learning_rate = 0.7
net.learning_momentum = 0.1

# Train the network
targets = [0.8]
loss = net.train(inputs, targets)
print(f"Loss: {loss}")

# FannNetwork has additional features
print(f"Network layers: {net.layers}")
print(f"Total connections: {net.total_connections}")
print(f"Learning rate: {net.learning_rate}")

# Create a sparse network (50% connectivity)
sparse_net = FannNetwork([2, 8, 1], connection_rate=0.5)

# Create a copy of the network
net_copy = net.copy()

# Randomize weights to specific range
net.randomize_weights(-0.5, 0.5)
```

### Basic Example - KannNeuralNetwork (KANN)

```python
from cynn.kann import KannNeuralNetwork, COST_MSE, COST_MULTI_CROSS_ENTROPY
import array

# Create a multi-layer perceptron
net = KannNeuralNetwork.mlp(
    input_size=4,
    hidden_sizes=[16, 8],  # Two hidden layers
    output_size=3,
    cost_type=COST_MULTI_CROSS_ENTROPY,
    dropout=0.1
)

# Network properties
print(f"Input dimension: {net.input_dim}")
print(f"Output dimension: {net.output_dim}")
print(f"Number of trainable variables: {net.n_var}")

# Prepare data (KANN uses float32 typed memoryviews)
x_train = array.array('f', [0.1, 0.2, 0.3, 0.4] * 100)  # 100 samples
y_train = array.array('f', [1.0, 0.0, 0.0] * 100)       # One-hot labels

# Reshape for 2D memoryview (100 samples x 4 features)
# In practice, use numpy or Array2D helper
import numpy as np
x = np.array(x_train, dtype=np.float32).reshape(100, 4)
y = np.array(y_train, dtype=np.float32).reshape(100, 3)

# Train (returns number of epochs)
epochs = net.train(x, y, learning_rate=0.001, max_epochs=50)
print(f"Trained for {epochs} epochs")

# Single inference
inputs = array.array('f', [0.1, 0.2, 0.3, 0.4])
output = net.apply(inputs)
print(f"Prediction: {list(output)}")

# Save and load models
net.save("model.kann")
loaded = KannNeuralNetwork.load("model.kann")
```

### KANN - LSTM for Sequence Modeling

```python
from cynn.kann import KannNeuralNetwork, COST_MULTI_CROSS_ENTROPY

# Create an LSTM network for sequence modeling
lstm = KannNeuralNetwork.lstm(
    input_size=128,    # Vocabulary size (one-hot)
    hidden_size=256,   # LSTM hidden state size
    output_size=128,   # Output vocabulary size
    cost_type=COST_MULTI_CROSS_ENTROPY
)

# Train on sequences (e.g., for text generation)
sequences = [
    [10, 20, 30, 40, 50, 60],  # Token sequences
    [15, 25, 35, 45, 55, 65],
    # ... more sequences
]

history = lstm.train_rnn(
    sequences,
    seq_length=32,       # BPTT sequence length
    vocab_size=128,
    learning_rate=0.001,
    max_epochs=100,
    grad_clip=5.0,       # Gradient clipping
    verbose=1
)

print(f"Final loss: {history['loss'][-1]}")
```

### KANN - Custom Network with GraphBuilder

```python
from cynn.kann import GraphBuilder

# Build a custom architecture
builder = GraphBuilder()

# Define network graph
x = builder.input(10)
h = builder.dense(x, 32)
h = builder.relu(h)
h = builder.dropout(h, 0.2)
h = builder.dense(h, 16)
h = builder.tanh(h)
cost = builder.softmax_cross_entropy(h, 5)

# Create network from graph
net = builder.build(cost)

# Use like any other KANN network
print(f"Variables: {net.n_var}")
```

### Batch Training

All network types support batch training for improved efficiency:

```python
from cynn.genann import GenannNetwork

net = GenannNetwork(2, 1, 4, 1)

# Prepare batch data (XOR problem)
inputs_list = [
    [0.0, 0.0],
    [0.0, 1.0],
    [1.0, 0.0],
    [1.0, 1.0]
]
targets_list = [
    [0.0],
    [1.0],
    [1.0],
    [0.0]
]

# Train on entire batch with optional shuffling
stats = net.train_batch(inputs_list, targets_list, rate=0.1, shuffle=True)

print(f"Batch mean loss: {stats['mean_loss']}")
print(f"Batch total loss: {stats['total_loss']}")
print(f"Examples trained: {stats['count']}")

# Train for multiple epochs
for epoch in range(100):
    stats = net.train_batch(inputs_list, targets_list, rate=0.1, shuffle=True)
    if epoch % 10 == 0:
        print(f"Epoch {epoch}: loss = {stats['mean_loss']:.4f}")
```

### Evaluating Without Training

Use `evaluate()` to compute loss without updating weights (useful for validation):

```python
from cynn.tinn import TinnNetwork

net = TinnNetwork(2, 4, 1)

# Training data
train_inputs = [0.5, 0.3]
train_targets = [0.8]

# Validation data
val_inputs = [0.4, 0.6]
val_targets = [0.7]

# Train on training data
train_loss = net.train(train_inputs, train_targets, rate=0.5)
print(f"Training loss: {train_loss}")

# Evaluate on validation data (no weight updates)
val_loss = net.evaluate(val_inputs, val_targets)
print(f"Validation loss: {val_loss}")

# Verify evaluate doesn't change weights
val_loss2 = net.evaluate(val_inputs, val_targets)
assert val_loss == val_loss2  # Should be identical
```

### Training with Validation

Combine batch training with evaluation for train/validation splits:

```python
from cynn.fann import FannNetwork

net = FannNetwork([2, 8, 1])
net.learning_rate = 0.5

# Split data into train/validation
train_inputs = [[0.0, 0.0], [0.0, 1.0]]
train_targets = [[0.0], [1.0]]

val_inputs = [[1.0, 0.0], [1.0, 1.0]]
val_targets = [[1.0], [0.0]]

for epoch in range(50):
    # Train on training set
    train_stats = net.train_batch(train_inputs, train_targets, shuffle=True)

    # Evaluate on validation set (no weight updates)
    val_losses = [net.evaluate(inp, tgt) for inp, tgt in zip(val_inputs, val_targets)]
    val_loss = sum(val_losses) / len(val_losses)

    if epoch % 10 == 0:
        print(f"Epoch {epoch}: train_loss={train_stats['mean_loss']:.4f}, val_loss={val_loss:.4f}")
```

### Context Manager Support

All network types support Python's context manager protocol (`with` statement) for cleaner code:

```python
from cynn.tinn import TinnNetwork, GenannNetwork, CNNNetwork

# Automatic resource management with context manager
with TinnNetwork(2, 4, 1) as net:
    output = net.predict([0.5, 0.3])
    loss = net.train([0.5, 0.3], [0.8], rate=0.5)
    print(f"Loss: {loss}")

# Works with all network types
with GenannNetwork(2, 1, 4, 1) as net:
    loss = net.train([0.5, 0.3], [0.8], rate=0.1)

# Useful for temporary networks
with CNNNetwork() as net:
    net.create_input_layer(1, 4, 4)
    net.add_full_layer(2)
    result = net.predict([0.5] * 16)

# Networks remain usable after exiting context
net = TinnNetwork(2, 4, 1)
with net as network:
    network.train([0.5, 0.3], [0.8], rate=0.5)
# Network 'net' is still valid and usable here
output = net.predict([0.5, 0.3])
```

Note: The context manager protocol ensures clean resource handling, but cynn networks already handle cleanup automatically via `__dealloc__`, so using `with` is optional and primarily for code clarity. This may be used for other purposes in the future, such as triggering graph drawing.

### XOR Problem

```python
from cynn.tinn import TinnNetwork, seed
import random
import time

# Seed random number generators
seed(int(time.time()))
random.seed(int(time.time()))

# XOR training data
xor_data = [
    ([0.0, 0.0], [0.0]),
    ([0.0, 1.0], [1.0]),
    ([1.0, 0.0], [1.0]),
    ([1.0, 1.0], [0.0]),
]

# Create network
net = TinnNetwork(2, 4, 1)

# Train with constant learning rate
rate = 0.5

for epoch in range(3000):
    random.shuffle(xor_data)
    total_error = 0.0

    for inputs, targets in xor_data:
        error = net.train(inputs, targets, rate)
        total_error += error

    avg_error = total_error / len(xor_data)

    if epoch % 500 == 0:
        print(f"Epoch {epoch}: avg error = {avg_error:.6f}")

# Test predictions
for inputs, expected in xor_data:
    pred = net.predict(inputs)
    result = "✓" if abs(pred[0] - expected[0]) < 0.3 else "✗"
    print(f"{result} {inputs} -> {pred[0]:.4f} (expected {expected[0]})")
```

Example output:

```text
% uv run python tests/examples/xor_problem.py
Epoch 0: avg error = 0.129680
Epoch 500: avg error = 0.127645
Epoch 1000: avg error = 0.123747
Epoch 1500: avg error = 0.029109
Epoch 2000: avg error = 0.008168
Epoch 2500: avg error = 0.004388
✓ [0.0, 0.0] -> 0.0893 (expected 0.0)
✓ [1.0, 0.0] -> 0.9285 (expected 1.0)
✓ [0.0, 1.0] -> 0.9284 (expected 1.0)
✓ [1.0, 1.0] -> 0.0721 (expected 0.0)
```

### NumPy Support

The library supports any object implementing the buffer protocol, including NumPy arrays:

```python
import numpy as np
from cynn.tinn import TinnNetwork

# Create network
net = TinnNetwork(2, 4, 1)

# Use NumPy arrays (float32 recommended, but float64 works too)
inputs = np.array([0.5, 0.3], dtype=np.float32)
targets = np.array([0.8], dtype=np.float32)

# Train with numpy arrays
loss = net.train(inputs, targets, 0.1)

# Predict with numpy arrays
prediction = net.predict(inputs)

# Batch processing
batch = np.array([
    [0.1, 0.2],
    [0.3, 0.4],
    [0.5, 0.6],
], dtype=np.float32)

predictions = [net.predict(row) for row in batch]
```

### Save and Load Models

```python
from cynn.tinn import TinnNetwork

# Train a network
net = TinnNetwork(2, 4, 1)
# ... training code ...

# Save to disk
net.save("model.tinn")

# Load from disk
loaded_net = TinnNetwork.load("model.tinn")

# Use loaded network
prediction = loaded_net.predict([0.5, 0.3])
```

## Examples

The `tests/examples/` directory contains 9 documented examples demonstrating each network type with real tasks:

| Example | Network | Task | Dataset |
|---------|---------|------|---------|
| `tinn_xor.py` | TinnNetwork | XOR classification | Inline |
| `genann_iris.py` | GenannNetwork | Iris classification | `iris.csv` |
| `fann_regression.py` | FannNetwork | Sine wave regression | `sine_wave.csv` |
| `cnn_mnist.py` | CNNNetwork | Digit classification | `mnist_subset.csv` |
| `kann_mlp_iris.py` | KannNeuralNetwork.mlp() | Iris classification | `iris.csv` |
| `kann_lstm_sequence.py` | KannNeuralNetwork.lstm() | Sequence prediction | `sequences.csv` |
| `kann_gru_text.py` | KannNeuralNetwork.gru() | Text modeling | `shakespeare_tiny.txt` |
| `kann_rnn_timeseries.py` | KannNeuralNetwork.mlp() | Time series | `sine_wave.csv` |
| `kann_text_generation.py` | KannNeuralNetwork.lstm() | Text generation | `shakespeare_tiny.txt` |

```bash
# Run any example
uv run python tests/examples/tinn_xor.py

# Run with options
uv run python tests/examples/kann_lstm_sequence.py --epochs 100 --hidden-size 64

# Run all examples with summary
uv run python tests/examples/run_all_examples.py

# Run at 50% training intensity (faster)
uv run python tests/examples/run_all_examples.py --ratio 0.5

# Run at 200% training intensity (slower)
uv run python tests/examples/run_all_examples.py --ratio 2.0
```

Datasets are stored in `tests/data/`. See `tests/examples/README.md` for detailed documentation.

## Development

### Building

```bash
# Standard build
make build

# CMake build (for debugging)
make cmake

# Clean build artifacts
make clean
```

### Testing

```bash
# Run all tests
make test

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_basic.py -v
```

### Project Structure

```text
cynn/
├── src/
│   └── cynn/
│       ├── __init__.py       # Package entry (lazy imports)
│       ├── _common.pxi       # Shared Cython code
│       ├── tinn.pyx          # TinnNetwork wrapper
│       ├── genann.pyx        # GenannNetwork wrapper
│       ├── fann.pyx          # FannNetwork wrapper
│       ├── cnn.pyx           # CNNNetwork, CNNLayer wrappers
│       ├── kann.pyx          # KannNeuralNetwork, GraphBuilder, etc.
│       ├── tinn.pxd          # Tinn C declarations
│       ├── genann.pxd        # Genann C declarations
│       ├── ffann.pxd         # FANN C declarations
│       ├── cnn.pxd           # nn1 CNN C declarations
│       ├── kann.pxd          # KANN C declarations
│       └── CMakeLists.txt    # Build configuration
├── thirdparty/
│   ├── tinn/                 # Vendored Tinn C library
│   ├── genann/               # Vendored Genann C library
│   ├── fann/                 # Vendored FANN C library
│   ├── nn1/                  # Vendored nn1 CNN C library
│   └── kann/                 # Vendored KANN C library
├── tests/                    # pytest test suite
├── CMakeLists.txt            # Root CMake config
├── Makefile                  # Build shortcuts
└── pyproject.toml            # Python package metadata
```

## API Reference

### seed()

```python
def seed(seed_value: int = 0) -> None
```

Seed the C random number generator used for weight initialization. If seed_value is 0 (default), uses current time. Call this before creating networks for reproducible results.

### TinnNetwork

```python
class TinnNetwork:
    def __init__(self, inputs: int, hidden: int, outputs: int)
```

Create a new 3-layer neural network (float32 precision).

**Parameters:**

- `inputs`: Number of input neurons
- `hidden`: Number of hidden layer neurons
- `outputs`: Number of output neurons

**Properties:**

- `input_size`: Number of inputs
- `hidden_size`: Number of hidden neurons
- `output_size`: Number of outputs
- `shape`: Tuple of (inputs, hidden, outputs)

**Methods:**

#### predict()

```python
def predict(self, inputs: list[float]) -> list[float]
```

Make a prediction given input values.

#### train()

```python
def train(self, inputs: list[float], targets: list[float], rate: float) -> float
```

Train the network on one example. Returns the mean squared error for this training step.

#### evaluate()

```python
def evaluate(self, inputs: list[float], targets: list[float]) -> float
```

Compute loss without training. Returns mean squared error between prediction and targets.

#### train_batch()

```python
def train_batch(
    self,
    inputs_list: list,
    targets_list: list,
    rate: float,
    shuffle: bool = False
) -> dict[str, float]
```

Train on multiple examples in batch. Returns dict with keys: `'mean_loss'`, `'total_loss'`, `'count'`.

#### save()

```python
def save(self, path: str | bytes | os.PathLike) -> None
```

Save the network weights to a file.

#### load()

```python
@classmethod
def load(cls, path: str | bytes | os.PathLike) -> TinnNetwork
```

Load a network from a file.

#### \_\_enter\_\_() / \_\_exit\_\_()

```python
def __enter__(self) -> TinnNetwork
def __exit__(self, exc_type, exc_val, exc_tb) -> bool
```

Context manager protocol support. Enables use of `with` statement for cleaner code. The network handles cleanup automatically via `__dealloc__`, so context manager usage is optional.

### GenannNetwork

```python
class GenannNetwork:
    def __init__(self, inputs: int, hidden_layers: int, hidden: int, outputs: int)
```

Create a new multi-layer neural network (float64 precision).

**Parameters:**

- `inputs`: Number of input neurons
- `hidden_layers`: Number of hidden layers
- `hidden`: Number of neurons per hidden layer
- `outputs`: Number of output neurons

**Properties:**

- `input_size`: Number of inputs
- `hidden_layers`: Number of hidden layers
- `hidden_size`: Number of neurons per hidden layer
- `output_size`: Number of outputs
- `shape`: Tuple of (inputs, hidden_layers, hidden, outputs)
- `total_weights`: Total number of weights in the network
- `total_neurons`: Total number of neurons plus inputs

**Methods:**

#### predict()

```python
def predict(self, inputs: list[float]) -> list[float]
```

Make a prediction given input values.

#### train()

```python
def train(self, inputs: list[float], targets: list[float], rate: float) -> float
```

Train the network on one example using backpropagation. Returns mean squared error.

#### evaluate()

```python
def evaluate(self, inputs: list[float], targets: list[float]) -> float
```

Compute loss without training. Returns mean squared error between prediction and targets.

#### train_batch()

```python
def train_batch(
    self,
    inputs_list: list,
    targets_list: list,
    rate: float,
    shuffle: bool = False
) -> dict[str, float]
```

Train on multiple examples in batch. Returns dict with keys: `'mean_loss'`, `'total_loss'`, `'count'`.

#### randomize()

```python
def randomize(self) -> None
```

Randomize all network weights.

#### copy()

```python
def copy(self) -> GenannNetwork
```

Create a deep copy of the network.

#### save()

```python
def save(self, path: str | bytes | os.PathLike) -> None
```

Save the network weights to a file.

#### load()

```python
@classmethod
def load(cls, path: str | bytes | os.PathLike) -> GenannNetwork
```

Load a network from a file.

#### \_\_enter\_\_() / \_\_exit\_\_()

```python
def __enter__(self) -> GenannNetwork
def __exit__(self, exc_type, exc_val, exc_tb) -> bool
```

Context manager protocol support. Enables use of `with` statement for cleaner code. The network handles cleanup automatically via `__dealloc__`, so context manager usage is optional.

### FannNetwork

```python
class FannNetwork:
    def __init__(self, layers: list[int] | None = None, connection_rate: float = 1.0)
```

Create a new multi-layer neural network (float32 precision) using the FANN library.

**Parameters:**

- `layers`: List of layer sizes [input, hidden1, ..., hiddenN, output]. Must have at least 2 layers.
- `connection_rate`: Connection density (0.0 to 1.0). 1.0 = fully connected, < 1.0 = sparse network.

**Properties:**

- `input_size`: Number of inputs
- `output_size`: Number of outputs
- `total_neurons`: Total number of neurons
- `total_connections`: Total number of connections
- `num_layers`: Number of layers
- `layers`: List of neuron counts for each layer
- `learning_rate`: Get or set the learning rate
- `learning_momentum`: Get or set the learning momentum

**Methods:**

#### predict()

```python
def predict(self, inputs: list[float]) -> list[float]
```

Make a prediction given input values.

#### train()

```python
def train(self, inputs: list[float], targets: list[float]) -> float
```

Train the network on one example using backpropagation. Uses current `learning_rate` and `learning_momentum`. Returns mean squared error.

#### evaluate()

```python
def evaluate(self, inputs: list[float], targets: list[float]) -> float
```

Compute loss without training. Returns mean squared error between prediction and targets.

#### train_batch()

```python
def train_batch(
    self,
    inputs_list: list,
    targets_list: list,
    shuffle: bool = False
) -> dict[str, float]
```

Train on multiple examples in batch. Uses current `learning_rate` and `learning_momentum`. Returns dict with keys: `'mean_loss'`, `'total_loss'`, `'count'`.

#### randomize_weights()

```python
def randomize_weights(self, min_weight: float = -0.1, max_weight: float = 0.1) -> None
```

Randomize all network weights to values in [min_weight, max_weight].

#### copy()

```python
def copy(self) -> FannNetwork
```

Create a deep copy of the network.

#### save()

```python
def save(self, path: str | bytes | os.PathLike) -> None
```

Save the network to a file (FANN text format).

#### load()

```python
@classmethod
def load(cls, path: str | bytes | os.PathLike) -> FannNetwork
```

Load a network from a file.

#### \_\_enter\_\_() / \_\_exit\_\_()

```python
def __enter__(self) -> FannNetwork
def __exit__(self, exc_type, exc_val, exc_tb) -> bool
```

Context manager protocol support. Enables use of `with` statement for cleaner code. The network handles cleanup automatically via `__dealloc__`, so context manager usage is optional.

### CNNNetwork

```python
class CNNNetwork:
    def __init__(self)
```

Create a new convolutional neural network (float64 precision). Networks are built by adding layers sequentially.

**Properties:**

- `input_shape`: Tuple of (depth, width, height) for the input layer
- `output_size`: Number of output nodes in the final layer
- `num_layers`: Total number of layers in the network
- `layers`: List of CNNLayer wrappers

**Methods:**

#### create_input_layer()

```python
def create_input_layer(self, depth: int, width: int, height: int) -> CNNLayer
```

Create an input layer. Must be called first when building a network.

#### add_conv_layer()

```python
def add_conv_layer(
    self,
    depth: int,
    width: int,
    height: int,
    kernel_size: int,
    padding: int = 0,
    stride: int = 1,
    std: float = 0.1
) -> CNNLayer
```

Add a convolutional layer with specified output dimensions and convolution parameters.

#### add_full_layer()

```python
def add_full_layer(self, num_nodes: int, std: float = 0.1) -> CNNLayer
```

Add a fully-connected layer.

#### predict()

```python
def predict(self, inputs: list[float]) -> list[float]
```

Make a prediction. Input should be a flat array of size depth × width × height.

#### train()

```python
def train(
    self,
    inputs: list[float],
    targets: list[float],
    learning_rate: float
) -> float
```

Train the network on one example. Returns mean squared error.

#### evaluate()

```python
def evaluate(self, inputs: list[float], targets: list[float]) -> float
```

Compute loss without training. Returns mean squared error between prediction and targets.

#### train_batch()

```python
def train_batch(
    self,
    inputs_list: list,
    targets_list: list,
    learning_rate: float,
    shuffle: bool = False
) -> dict[str, float]
```

Train on multiple examples in batch. Returns dict with keys: `'mean_loss'`, `'total_loss'`, `'count'`.

#### dump()

```python
def dump(self) -> None
```

Print debug information about all layers to stdout.

#### \_\_enter\_\_() / \_\_exit\_\_()

```python
def __enter__(self) -> CNNNetwork
def __exit__(self, exc_type, exc_val, exc_tb) -> bool
```

Context manager protocol support. Enables use of `with` statement for cleaner code. The network handles cleanup automatically via `__dealloc__`, so context manager usage is optional.

### CNNLayer

```python
class CNNLayer
```

Represents a single layer in a CNN. Created by CNNNetwork methods, not directly instantiated.

**Properties:**

- `layer_id`: Layer ID in the network
- `shape`: Tuple of (depth, width, height)
- `depth`, `width`, `height`: Individual dimensions
- `num_nodes`: Total nodes (depth × width × height)
- `num_weights`, `num_biases`: Weight and bias counts
- `layer_type`: String ('input', 'conv', or 'full')
- `kernel_size`, `padding`, `stride`: Conv layer parameters (raises ValueError for non-conv layers)

**Methods:**

#### get_outputs()

```python
def get_outputs(self) -> list[float]
```

Get the output values of this layer.

### KannNeuralNetwork (KANN)

```python
class KannNeuralNetwork
```

Advanced neural network class supporting MLPs, LSTMs, GRUs, and simple RNNs (float32 precision). Based on the KANN (Klib Artificial Neural Network) library.

**Factory Methods:**

#### mlp()

```python
@staticmethod
def mlp(
    input_size: int,
    hidden_sizes: list[int],
    output_size: int,
    cost_type: int = COST_MULTI_CROSS_ENTROPY,
    dropout: float = 0.0
) -> KannNeuralNetwork
```

Create a multi-layer perceptron with arbitrary hidden layer configuration.

#### lstm()

```python
@staticmethod
def lstm(
    input_size: int,
    hidden_size: int,
    output_size: int,
    cost_type: int = COST_MULTI_CROSS_ENTROPY,
    rnn_flags: int = 0
) -> KannNeuralNetwork
```

Create an LSTM network for sequence modeling.

#### gru()

```python
@staticmethod
def gru(
    input_size: int,
    hidden_size: int,
    output_size: int,
    cost_type: int = COST_MULTI_CROSS_ENTROPY,
    rnn_flags: int = 0
) -> KannNeuralNetwork
```

Create a GRU network for sequence modeling.

#### rnn()

```python
@staticmethod
def rnn(
    input_size: int,
    hidden_size: int,
    output_size: int,
    cost_type: int = COST_MULTI_CROSS_ENTROPY,
    rnn_flags: int = 0
) -> KannNeuralNetwork
```

Create a simple RNN network.

#### load()

```python
@staticmethod
def load(filename: str) -> KannNeuralNetwork
```

Load a network from a file.

**Properties:**

- `n_nodes`: Number of nodes in the computational graph
- `input_dim`: Input dimension
- `output_dim`: Output dimension
- `n_var`: Total number of trainable variables
- `n_const`: Total number of constants

**Methods:**

#### train()

```python
def train(
    self,
    x: float[:, :],
    y: float[:, :],
    learning_rate: float = 0.001,
    mini_batch_size: int = 64,
    max_epochs: int = 100,
    min_epochs: int = 0,
    max_drop_streak: int = 10,
    validation_fraction: float = 0.1
) -> int
```

Train the network using built-in feedforward trainer with RMSprop optimizer and early stopping. Returns number of epochs trained.

#### train_rnn()

```python
def train_rnn(
    self,
    sequences: list,
    seq_length: int,
    vocab_size: int,
    learning_rate: float = 0.001,
    mini_batch_size: int = 32,
    max_epochs: int = 100,
    grad_clip: float = 10.0,
    validation_fraction: float = 0.1,
    verbose: int = 1
) -> dict
```

Train RNN/LSTM/GRU using backpropagation through time (BPTT). Returns dict with `'loss'` and `'val_loss'` history lists.

#### apply()

```python
def apply(self, x: float[:]) -> array.array
```

Apply the network to a single input. Returns output as `array.array('f', ...)`.

#### cost()

```python
def cost(self, x: float[:, :], y: float[:, :]) -> float
```

Compute the cost over a dataset.

#### save()

```python
def save(self, filename: str) -> None
```

Save the network to a file.

#### clone()

```python
def clone(self, batch_size: int = 1) -> KannNeuralNetwork
```

Clone the network with a different batch size.

#### unroll()

```python
def unroll(self, length: int) -> KannNeuralNetwork
```

Unroll an RNN for a specified number of time steps.

#### switch_mode()

```python
def switch_mode(self, is_training: bool) -> None
```

Switch between training and inference mode.

#### close()

```python
def close(self) -> None
```

Explicitly release resources.

#### \_\_enter\_\_() / \_\_exit\_\_()

Context manager protocol support.

### GraphBuilder

```python
class GraphBuilder
```

Low-level graph builder for creating custom network architectures.

**Methods:**

- `input(size)`: Create an input layer
- `dense(inp, output_size)`: Create a dense (fully connected) layer
- `dropout(inp, rate)`: Create a dropout layer
- `layernorm(inp)`: Create a layer normalization layer
- `relu(inp)`, `sigmoid(inp)`, `tanh(inp)`, `softmax(inp)`: Activation functions
- `lstm(inp, hidden_size, flags)`, `gru(inp, hidden_size, flags)`, `rnn(inp, hidden_size, flags)`: Recurrent layers
- `conv1d(inp, n_filters, kernel_size, stride, pad)`: 1D convolution
- `conv2d(inp, n_filters, k_rows, k_cols, stride_r, stride_c, pad_r, pad_c)`: 2D convolution
- `add(x, y)`, `sub(x, y)`, `mul(x, y)`, `matmul(x, y)`: Arithmetic operations
- `softmax_cross_entropy(inp, n_out)`: Softmax + cross-entropy cost
- `sigmoid_cross_entropy(inp, n_out)`: Sigmoid + binary cross-entropy cost
- `mse_layer(inp, n_out)`: MSE cost layer
- `build(cost)`: Build the neural network from the cost node

### DataSet

```python
class DataSet
```

Wrapper for loading tabular data from TSV files.

**Methods:**

- `load(filename)`: Load data from a TSV file
- `get_row(index)`: Get a single row of data
- `get_row_name(index)`, `get_col_name(index)`: Get row/column names
- `split_xy(label_cols)`: Split data into features and labels
- `to_2d_array()`: Convert to Array2D

**Properties:**

- `n_rows`, `n_cols`, `n_groups`, `shape`, `row_names`, `col_names`

### KANN Helper Functions

```python
kann_set_seed(seed: int) -> None
```

Set the random seed for reproducibility.

```python
kann_set_verbose(level: int) -> None
```

Set verbosity level for KANN operations.

```python
one_hot_encode(values: int[:], num_classes: int) -> list
```

One-hot encode an array of integer values.

```python
softmax_sample(probs: float[:], temperature: float = 1.0) -> int
```

Sample from a probability distribution with temperature scaling.

```python
prepare_sequence_data(sequences, seq_length: int, vocab_size: int) -> tuple
```

Prepare sequence data for RNN training.

### KANN Constants

**Cost Functions:**

- `COST_BINARY_CROSS_ENTROPY`: Binary cross-entropy (sigmoid)
- `COST_MULTI_CROSS_ENTROPY`: Multi-class cross-entropy (softmax)
- `COST_BINARY_CROSS_ENTROPY_NEG`: Binary cross-entropy for tanh (-1,1)
- `COST_MSE`: Mean square error

**Node Flags:**

- `KANN_FLAG_IN`, `KANN_FLAG_OUT`, `KANN_FLAG_TRUTH`, `KANN_FLAG_COST`

**RNN Flags:**

- `RNN_VAR_H0`: Variable initial hidden states
- `RNN_NORM`: Layer normalization

## Choosing Between Network Implementations

| Feature | TinnNetwork | GenannNetwork | FannNetwork | CNNNetwork | KannNeuralNetwork (KANN) |
|---------|-------------|---------------|-------------|------------|---------------------|
| **Precision** | float32 | float64 | float32 | float64 | float32 |
| **Architecture** | Fixed 3-layer | Multi-layer | Flexible | Layer-based CNN | MLP/LSTM/GRU/RNN |
| **Layer Spec** | (in, hid, out) | (in, nlayers, hid, out) | [in, h1, h2, out] | Build API | Factory methods |
| **Learning Rate** | Per-train | Per-train | Settable property | Per-train | Per-train |
| **Momentum** | No | No | Yes | No | RMSprop built-in |
| **Sparse Networks** | No | No | Yes | No | No |
| **Convolutional** | No | No | No | Yes | Yes (via GraphBuilder) |
| **Recurrent (RNN)** | No | No | No | No | Yes (LSTM/GRU/RNN) |
| **Returns Loss** | Yes | Yes | Yes | Yes | Yes |
| **Memory** | Low | Medium | Low | High | Medium |
| **NumPy Default** | Converts | Native | Converts | Native | Converts |

**Use TinnNetwork when:**

- You need a simple 3-layer network
- Memory efficiency is important (float32 uses less memory)
- You want the training method to return loss values
- You prefer a simpler API with fixed architecture

**Use GenannNetwork when:**

- You need multiple hidden layers (deep networks)
- Higher precision is required (float64)
- You need to copy networks
- You want to randomize weights after creation
- You need to query total weights/neurons
- You prefer the constructor pattern: `GenannNetwork(inputs, hidden_layers, hidden_size, outputs)`

**Use FannNetwork when:**

- You need flexible multi-layer architectures
- You want to control learning rate and momentum during training
- You need sparse networks (partial connectivity)
- You prefer list-based layer specification: `FannNetwork([2, 4, 3, 1])`
- You want settable learning parameters
- Memory efficiency is important (float32 uses less memory than float64)

**Use CNNNetwork when:**

- You need convolutional layers for image processing or spatial data
- Building custom CNN architectures (e.g., MNIST, CIFAR-10 style networks)
- You want fine-grained control over layer configuration (kernel size, stride, padding)
- Working with 2D/3D structured input data
- Need to inspect individual layer properties and outputs
- Implementing image classification, object detection, or computer vision tasks
- Higher precision is required (float64)
- You prefer a layer-by-layer building API over fixed architecture

**Use KannNeuralNetwork (KANN) when:**

- You need recurrent networks (LSTM, GRU, or simple RNN) for sequence modeling
- Building text generation, time series prediction, or language models
- You want built-in RMSprop optimizer with early stopping
- You need backpropagation through time (BPTT) support
- You want a computational graph approach with automatic differentiation
- Building custom architectures with the GraphBuilder API
- You need convolution layers combined with recurrent layers
- Training with gradient clipping for RNNs
- You want built-in train/validation splitting

## Performance Considerations

- The C implementation is fast but operates on single examples (no batch processing)
- **GIL-free execution**: All computational operations (`train`, `predict`, network creation) release the Python GIL, enabling true parallel execution across multiple threads
- Thread-safe: Multiple threads can safely share the same network for predictions
- For production machine learning, consider TensorFlow, PyTorch, or JAX
- This library is ideal for:
  - Learning neural network fundamentals
  - Embedded systems with limited resources
  - Simple prediction tasks
  - Parallel inference workloads
  - Environments where large ML frameworks aren't available

### Multithreading Example

```python
from concurrent.futures import ThreadPoolExecutor
from cynn.tinn import TinnNetwork
import numpy as np

# Create a shared network
net = TinnNetwork(100, 50, 10)

def process_batch(batch_data):
    """Process a batch of inputs in parallel."""
    results = []
    for inputs in batch_data:
        pred = net.predict(inputs)
        results.append(pred)
    return results

# Prepare data batches
data = [np.random.rand(100).astype(np.float32) for _ in range(1000)]
batches = [data[i:i+250] for i in range(0, 1000, 250)]

# Process batches in parallel (GIL-free!)
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_batch, batches))
```

## Credits

- [Tinn](https://github.com/glouw/tinn) - Original C neural network library by glouw
- [GENANN](https://github.com/codeplea/genann) - Minimal C neural network library by codeplea
- [FANN](https://github.com/libfann/fann) - Fast Artificial Neural Network library by Steffen Nissen
- [nn1](https://github.com/euske/nn1) - Convolutional Neural Network in C by euske
- [KANN](https://github.com/attractivechaos/kann) - Klib Artificial Neural Network library by Attractive Chaos
- Built with [Cython](https://cython.org/)
- Build system uses [scikit-build-core](https://scikit-build-core.readthedocs.io/)

## License

See LICENSE file for details.
