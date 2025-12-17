#!/usr/bin/env python3
"""
Example 02: Iris Classification with GenannNetwork
===================================================

This example demonstrates training a multi-layer neural network on the classic
Iris flower classification dataset. GenannNetwork allows configurable hidden
layer depth, making it more flexible than TinnNetwork.

Network: GenannNetwork (multi-layer with configurable depth)
Task: Multi-class classification (3 flower species)
Dataset: tests/data/iris.csv (UCI Iris dataset)

Key Concepts:
- Loading data from CSV files
- One-hot encoding for multi-class targets
- Train/test data splitting
- Configuring multiple hidden layers
- Batch training with train_batch()
- Calculating classification accuracy
- Model persistence (save/load)

Usage:
    python tests/examples/genann_iris.py
    python tests/examples/genann_iris.py --epochs 500 --learning-rate 0.3
"""

import argparse
import csv
import random
from pathlib import Path

from cynn.genann import GenannNetwork, seed as genann_seed


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


def load_iris(path):
    """
    Load Iris dataset from CSV file.

    Returns list of (features, label) tuples where:
    - features: list of 4 floats (already normalized to [0,1])
    - label: integer class (0, 1, or 2)
    """
    data = []
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            features = [
                float(row['sepal_length']),
                float(row['sepal_width']),
                float(row['petal_length']),
                float(row['petal_width']),
            ]
            label = int(row['class'])
            data.append((features, label))
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
# Training
# ==============================================================================

def prepare_batch_data(data, num_classes):
    """Convert data to format suitable for train_batch."""
    inputs_list = [features for features, _ in data]
    targets_list = [one_hot_encode(label, num_classes) for _, label in data]
    return inputs_list, targets_list


def train_network(net, train_data, epochs, learning_rate, num_classes, verbose=True):
    """
    Train network on Iris data.

    Returns list of average loss per epoch.
    """
    inputs_list, targets_list = prepare_batch_data(train_data, num_classes)

    losses = []
    for epoch in range(epochs):
        stats = net.train_batch(inputs_list, targets_list, learning_rate, shuffle=True)
        losses.append(stats['mean_loss'])

        if verbose and (epoch + 1) % 50 == 0:
            print(f"  Epoch {epoch + 1:3d}/{epochs}: loss = {stats['mean_loss']:.6f}")

    return losses


# ==============================================================================
# Evaluation
# ==============================================================================

def evaluate_network(net, test_data, num_classes):
    """
    Evaluate network accuracy on test data.

    Returns accuracy (0.0 to 1.0) and confusion details.
    """
    correct = 0
    confusion = [[0] * num_classes for _ in range(num_classes)]

    for features, true_label in test_data:
        output = net.predict(features)
        predicted_label = output.index(max(output))

        confusion[true_label][predicted_label] += 1
        if predicted_label == true_label:
            correct += 1

    accuracy = correct / len(test_data) if test_data else 0.0
    return accuracy, confusion


def print_confusion_matrix(confusion, class_names):
    """Print a confusion matrix."""
    print("\nConfusion Matrix:")
    print("               ", end="")
    for name in class_names:
        print(f"{name:>12}", end="")
    print()

    for i, row in enumerate(confusion):
        print(f"  {class_names[i]:>10} ", end="")
        for val in row:
            print(f"{val:>12}", end="")
        print()


# ==============================================================================
# Main
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Iris Classification with GenannNetwork',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    parser.add_argument('--epochs', type=int, default=300,
                        help='Number of training epochs')
    parser.add_argument('--learning-rate', type=float, default=0.5,
                        help='Learning rate')
    parser.add_argument('--test-split', type=float, default=0.2,
                        help='Fraction of data for testing')
    parser.add_argument('--hidden-layers', type=int, default=2,
                        help='Number of hidden layers')
    parser.add_argument('--hidden-size', type=int, default=8,
                        help='Neurons per hidden layer')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress output')
    parser.add_argument('--data-path', type=str, default=None,
                        help='Path to iris.csv data file')
    return parser.parse_args()


def run(seed=42, epochs=300, learning_rate=0.5, test_split=0.2,
        hidden_layers=2, hidden_size=8, data_path=None, verbose=True):
    """
    Run the Iris classification example.

    Returns:
        dict with keys: accuracy, initial_loss, final_loss, epochs
    """
    genann_seed(seed)
    random.seed(seed)

    input_size = 4
    output_size = 3

    if verbose:
        print("=" * 60)
        print("Example 02: Iris Classification with GenannNetwork")
        print("=" * 60)
        print()
        print("Loading Iris dataset...")

    data_file = get_data_path("iris.csv", data_path)
    data = load_iris(data_file)

    if verbose:
        print(f"  Loaded {len(data)} samples from {data_file}")

    train_data, test_data = split_data(data, test_split)

    if verbose:
        print(f"  Training set: {len(train_data)} samples")
        print(f"  Test set: {len(test_data)} samples")
        print()
        print("Creating network...")
        print(f"  Architecture: {input_size} -> [{hidden_size}]*{hidden_layers} -> {output_size}")

    with GenannNetwork(input_size, hidden_layers, hidden_size, output_size) as net:
        if verbose:
            print(f"  Shape: {net.shape}")
            print(f"  Total weights: {net.total_weights}")
            print(f"  Total neurons: {net.total_neurons}")
            print()
            print(f"Training for {epochs} epochs...")

        losses = train_network(net, train_data, epochs, learning_rate, output_size, verbose)

        if verbose:
            print()
            print("Loss progression:")
            print(f"  Initial: {losses[0]:.6f}")
            print(f"  Final:   {losses[-1]:.6f}")
            print()
            print("Evaluating on test set...")

        accuracy, confusion = evaluate_network(net, test_data, output_size)

        if verbose:
            print(f"  Accuracy: {accuracy * 100:.1f}%")

            class_names = ['setosa', 'versicolor', 'virginica']
            print_confusion_matrix(confusion, class_names)
            print()

            print("Sample predictions (first 5 test samples):")
            print("-" * 60)
            for features, true_label in test_data[:5]:
                output = net.predict(features)
                pred_label = output.index(max(output))
                confidence = max(output)
                status = "OK" if pred_label == true_label else "WRONG"
                print(f"  True: {class_names[true_label]:>10}, "
                      f"Pred: {class_names[pred_label]:>10} "
                      f"(conf: {confidence:.3f}) [{status}]")
            print()

            print("Demonstrating network copy...")
            net_copy = net.copy()
            copy_accuracy, _ = evaluate_network(net_copy, test_data, output_size)
            print(f"  Copy accuracy matches: {abs(accuracy - copy_accuracy) < 1e-6}")

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
        hidden_layers=args.hidden_layers,
        hidden_size=args.hidden_size,
        data_path=args.data_path,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
