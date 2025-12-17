#!/usr/bin/env python3
"""
Example 05: MNIST Digit Classification with CNNNetwork
=======================================================

This example demonstrates training a Convolutional Neural Network (CNN) on
handwritten digit recognition. CNNs are particularly effective for image
data because convolutional layers learn spatial patterns and hierarchies.

Network: CNNNetwork (layer-based CNN with conv and fully-connected layers)
Task: Multi-class classification (10 digit classes)
Dataset: tests/data/mnist_subset.csv (500 samples from MNIST)

Key Concepts:
- Building CNNs with create_input_layer, add_conv_layer, add_full_layer
- Understanding layer shapes and parameters
- Processing image data (flattening, normalization)
- Multi-class classification with CNNs

Usage:
    python tests/examples/cnn_mnist.py
    python tests/examples/cnn_mnist.py --epochs 100 --learning-rate 0.005
"""

import argparse
import csv
import random
from pathlib import Path

from cynn.cnn import CNNNetwork, seed as cnn_seed


# Image dimensions
IMAGE_DEPTH = 1   # Grayscale
IMAGE_HEIGHT = 28
IMAGE_WIDTH = 28
NUM_CLASSES = 10


# ==============================================================================
# Data Loading
# ==============================================================================

def get_data_path(filename, data_path=None):
    """Get path to data file, using data_path if provided or searching tests/data/."""
    if data_path:
        path = Path(data_path)
        if path.exists():
            return path
        raise FileNotFoundError(f"Data file not found: {data_path}")

    base_paths = [
        Path(__file__).parent.parent / "data",
        Path("tests/data"),
        Path("../tests/data"),
    ]
    for base in base_paths:
        path = base / filename
        if path.exists():
            return path
    raise FileNotFoundError(f"Data file not found: {filename}")


def load_mnist(path):
    """Load MNIST subset from CSV."""
    data = []
    with open(path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header

        for row in reader:
            label = int(row[0])
            pixels = [float(p) for p in row[1:]]
            data.append((pixels, label))

    return data


def one_hot_encode(label, num_classes):
    """Convert integer label to one-hot encoded vector."""
    return [1.0 if i == label else 0.0 for i in range(num_classes)]


def split_data(data, test_fraction, shuffle=True):
    """Split data into training and test sets."""
    if shuffle:
        data = data.copy()
        random.shuffle(data)

    split_idx = int(len(data) * (1 - test_fraction))
    return data[:split_idx], data[split_idx:]


# ==============================================================================
# Network Creation
# ==============================================================================

def create_cnn(verbose=True):
    """Create a CNN for MNIST digit classification."""
    net = CNNNetwork()

    input_layer = net.create_input_layer(IMAGE_DEPTH, IMAGE_HEIGHT, IMAGE_WIDTH)
    if verbose:
        print(f"    Input layer: shape={input_layer.shape}")

    conv1 = net.add_conv_layer(
        depth=8, height=24, width=24,
        kernel_size=5, padding=0, stride=1
    )
    if verbose:
        print(f"    Conv1 layer: shape={conv1.shape}, "
              f"kernel={conv1.kernel_size}, stride={conv1.stride}")

    conv2 = net.add_conv_layer(
        depth=16, height=10, width=10,
        kernel_size=5, padding=0, stride=2
    )
    if verbose:
        print(f"    Conv2 layer: shape={conv2.shape}, "
              f"kernel={conv2.kernel_size}, stride={conv2.stride}")

    output_layer = net.add_full_layer(NUM_CLASSES)
    if verbose:
        print(f"    Output layer: nodes={output_layer.num_nodes}")

    return net


# ==============================================================================
# Training
# ==============================================================================

def train_network(net, train_data, epochs, learning_rate, verbose=True):
    """Train CNN on MNIST data."""
    losses = []

    for epoch in range(epochs):
        epoch_loss = 0.0
        random.shuffle(train_data)

        for pixels, label in train_data:
            target = one_hot_encode(label, NUM_CLASSES)
            loss = net.train(pixels, target, learning_rate)
            epoch_loss += loss

        avg_loss = epoch_loss / len(train_data)
        losses.append(avg_loss)

        if verbose and (epoch + 1) % 10 == 0:
            print(f"    Epoch {epoch + 1:3d}/{epochs}: loss = {avg_loss:.6f}")

    return losses


# ==============================================================================
# Evaluation
# ==============================================================================

def evaluate_network(net, test_data):
    """Evaluate CNN accuracy on test data."""
    correct = 0
    confusion = [[0] * NUM_CLASSES for _ in range(NUM_CLASSES)]

    for pixels, true_label in test_data:
        output = net.predict(pixels)
        pred_label = output.index(max(output))

        confusion[true_label][pred_label] += 1
        if pred_label == true_label:
            correct += 1

    accuracy = correct / len(test_data) if test_data else 0.0

    per_class = []
    for digit in range(NUM_CLASSES):
        total = sum(confusion[digit])
        correct_class = confusion[digit][digit]
        class_acc = correct_class / total if total > 0 else 0.0
        per_class.append((digit, correct_class, total, class_acc))

    return accuracy, confusion, per_class


def print_confusion_matrix(confusion, class_names):
    """Print a compact confusion matrix."""
    print("\nConfusion Matrix (rows=true, cols=predicted):")
    print("     ", end="")
    for name in class_names:
        print(f"{name:>4}", end="")
    print()

    for i, row in enumerate(confusion):
        print(f"  {class_names[i]:>2} ", end="")
        for val in row:
            if val == 0:
                print("   .", end="")
            else:
                print(f"{val:>4}", end="")
        print()


# ==============================================================================
# Main
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='MNIST Digit Classification with CNNNetwork',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    parser.add_argument('--epochs', type=int, default=50,
                        help='Number of training epochs')
    parser.add_argument('--learning-rate', type=float, default=0.01,
                        help='Learning rate')
    parser.add_argument('--test-split', type=float, default=0.2,
                        help='Fraction of data for testing')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress output')
    parser.add_argument('--data-path', type=str, default=None,
                        help='Path to mnist_subset.csv data file')
    return parser.parse_args()


def run(seed=42, epochs=50, learning_rate=0.01, test_split=0.2, data_path=None, verbose=True):
    """
    Run the MNIST classification example.

    Returns:
        dict with keys: accuracy, initial_loss, final_loss, epochs
    """
    cnn_seed(seed)
    random.seed(seed)

    if verbose:
        print("=" * 60)
        print("Example 05: MNIST Digit Classification with CNNNetwork")
        print("=" * 60)
        print()
        print("Loading MNIST subset...")

    data_file = get_data_path("mnist_subset.csv", data_path)
    data = load_mnist(data_file)

    if verbose:
        print(f"  Loaded {len(data)} samples from {data_file}")
        class_counts = {}
        for _, label in data:
            class_counts[label] = class_counts.get(label, 0) + 1
        print(f"  Class distribution: {dict(sorted(class_counts.items()))}")

    train_data, test_data = split_data(data, test_split)

    if verbose:
        print(f"  Training set: {len(train_data)} samples")
        print(f"  Test set: {len(test_data)} samples")
        print()
        print("Creating CNN...")

    with create_cnn(verbose) as net:
        if verbose:
            print()
            print(f"  Total layers: {net.num_layers}")
            print(f"  Input shape: {net.input_shape}")
            print(f"  Output size: {net.output_size}")
            print()
            print("  Layer details:")
            for i, layer in enumerate(net.layers):
                print(f"    [{i}] {layer.layer_type:>5}: shape={layer.shape}, "
                      f"nodes={layer.num_nodes}, weights={layer.num_weights}")
            print()
            print(f"Training for {epochs} epochs...")

        losses = train_network(net, train_data, epochs, learning_rate, verbose)

        if verbose:
            print()
            print("Loss progression:")
            print(f"  Initial: {losses[0]:.6f}")
            print(f"  Final:   {losses[-1]:.6f}")
            print()
            print("Evaluating on test set...")

        accuracy, confusion, per_class = evaluate_network(net, test_data)

        if verbose:
            print(f"  Overall accuracy: {accuracy * 100:.1f}%")

            print("\nPer-class accuracy:")
            for digit, correct, total, acc in per_class:
                bar = "#" * int(acc * 20) + "." * (20 - int(acc * 20))
                print(f"  Digit {digit}: {correct:2d}/{total:2d} = {acc * 100:5.1f}% [{bar}]")

            class_names = [str(i) for i in range(10)]
            print_confusion_matrix(confusion, class_names)

            print("\nSample predictions (first 10 test samples):")
            print("-" * 50)
            for pixels, true_label in test_data[:10]:
                output = net.predict(pixels)
                pred_label = output.index(max(output))
                confidence = max(output)
                status = "OK" if pred_label == true_label else "WRONG"
                print(f"  True: {true_label}, Pred: {pred_label} "
                      f"(conf: {confidence:.3f}) [{status}]")

            print()
            print("Done!")

    return {
        'accuracy': accuracy,
        'initial_loss': losses[0],
        'final_loss': losses[-1],
        'epochs': epochs,
    }


def main():
    args = parse_args()
    return run(
        seed=args.seed,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        test_split=args.test_split,
        data_path=args.data_path,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
