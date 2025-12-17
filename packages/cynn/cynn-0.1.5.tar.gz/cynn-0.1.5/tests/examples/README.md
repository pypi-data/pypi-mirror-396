# cynn Examples

This directory contains practical, educational examples demonstrating each neural network library in cynn.

## Quick Start

```bash
# Make sure cynn is installed
make build

# Download datasets (required for most examples)
python scripts/download_datasets.py

# Run any example
uv run python examples/tinn_xor.py
```

## Examples Overview

| Example | Network | Task | Dataset |
|---------|---------|------|---------|
| [tinn_xor.py](tinn_xor.py) | TinnNetwork | XOR classification | Inline |
| [genann_iris.py](genann_iris.py) | GenannNetwork | Iris classification | iris.csv |
| [fann_regression.py](fann_regression.py) | FannNetwork | Sine wave regression | sine_wave.csv |
| [cnn_mnist.py](cnn_mnist.py) | CNNNetwork | Digit classification | mnist_subset.csv |
| [kann_mlp_iris.py](kann_mlp_iris.py) | KannNeuralNetwork.mlp() | Iris classification | iris.csv |
| [kann_lstm_sequence.py](kann_lstm_sequence.py) | KannNeuralNetwork.lstm() | Sequence prediction | sequences.csv |
| [kann_gru_text.py](kann_gru_text.py) | KannNeuralNetwork.gru() | Text modeling | shakespeare_tiny.txt |
| [kann_rnn_timeseries.py](kann_rnn_timeseries.py) | KannNeuralNetwork.mlp() | Time series | sine_wave.csv |
| [kann_text_generation.py](kann_text_generation.py) | KannNeuralNetwork.lstm() | Text generation | shakespeare_tiny.txt |

## Network Types

### Basic Networks

- **TinnNetwork** - Simple fixed 3-layer network (input, hidden, output). Float32.
- **GenannNetwork** - Multi-layer with configurable hidden layer depth. Float64.
- **FannNetwork** - Flexible multi-layer with momentum. Float32.
- **CNNNetwork** - Convolutional neural network with conv and fully-connected layers. Float64.

### KANN Networks

- **KannNeuralNetwork.mlp()** - Multi-layer perceptron with dropout support
- **KannNeuralNetwork.lstm()** - Long Short-Term Memory for sequences
- **KannNeuralNetwork.gru()** - Gated Recurrent Unit (faster than LSTM)
- **KannNeuralNetwork.rnn()** - Simple recurrent network

## Datasets

Datasets are stored in `tests/data/`. Run the download script to fetch them:

```bash
python scripts/download_datasets.py
```

| File | Source | Description |
|------|--------|-------------|
| iris.csv | UCI ML Repository | 150 flower samples, 4 features, 3 classes |
| sine_wave.csv | Generated | 1000 samples of sin(x) |
| mnist_subset.csv | MNIST Database | 500 handwritten digit images (28x28) |
| shakespeare_tiny.txt | Project Gutenberg | ~47KB of Shakespeare text |
| sequences.csv | Generated | 15 mathematical integer sequences |

## Key Concepts Demonstrated

### Training Patterns
- Single-sample training with learning rate decay
- Batch training with `train_batch()`
- KANN's built-in `train()` with early stopping
- RNN training with `train_rnn()` (BPTT)

### Data Handling
- CSV loading and parsing
- Normalization to [0, 1] range
- One-hot encoding for classification
- Train/test splitting
- Character tokenization for text

### Model Features
- Save/load model persistence
- Network copying
- Learning rate and momentum tuning
- Dropout regularization
- Temperature-controlled sampling

## Requirements

- Python 3.11+
- cynn package (installed via `make build`)
- NumPy (optional, recommended for KANN examples)
