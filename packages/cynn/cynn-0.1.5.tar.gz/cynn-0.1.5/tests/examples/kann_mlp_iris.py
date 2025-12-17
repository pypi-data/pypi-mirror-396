#!/usr/bin/env python3
"""
Example 06: Iris Classification with KANN MLP
==============================================

This example demonstrates KANN's Multi-Layer Perceptron (MLP) factory method
for classification. KANN provides a high-level API for creating neural networks
with built-in training loops, dropout regularization, and early stopping.

Network: KannNeuralNetwork.mlp() factory method
Task: Multi-class classification (3 flower species)
Dataset: tests/data/iris.csv

Key Concepts:
- Using the mlp() factory method
- Cost function selection (COST_MULTI_CROSS_ENTROPY for classification)
- Dropout regularization
- Built-in train() method with early stopping
- Working with numpy arrays (optional, falls back to array.array)

Usage:
    python tests/examples/kann_mlp_iris.py
    python tests/examples/kann_mlp_iris.py --epochs 300 --learning-rate 0.005
"""

import argparse
import array
import csv
import random
from pathlib import Path

from cynn.kann import (
    KannNeuralNetwork,
    COST_MULTI_CROSS_ENTROPY,
    set_seed as kann_set_seed,
)

# Optional numpy support
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


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
    """Load Iris dataset from CSV file."""
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


def prepare_numpy_data(data, num_classes):
    """Convert data to numpy arrays for KANN training."""
    x = np.array([d[0] for d in data], dtype=np.float32)
    y = np.array([one_hot_encode(d[1], num_classes) for d in data], dtype=np.float32)
    return x, y


# ==============================================================================
# Evaluation
# ==============================================================================

def evaluate_network(net, test_data, num_classes):
    """Evaluate network accuracy on test data."""
    correct = 0
    predictions = []

    for features, true_label in test_data:
        if HAS_NUMPY:
            inp = np.array(features, dtype=np.float32)
        else:
            inp = array.array('f', features)
        output = net.apply(inp)
        pred_label = list(output).index(max(output))

        predictions.append({
            'true': true_label,
            'pred': pred_label,
            'confidence': max(output),
        })

        if pred_label == true_label:
            correct += 1

    accuracy = correct / len(test_data) if test_data else 0.0
    return accuracy, predictions


# ==============================================================================
# Main
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Iris Classification with KANN MLP',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    parser.add_argument('--epochs', type=int, default=200,
                        help='Maximum training epochs')
    parser.add_argument('--learning-rate', type=float, default=0.01,
                        help='Learning rate')
    parser.add_argument('--batch-size', type=int, default=16,
                        help='Mini-batch size')
    parser.add_argument('--dropout', type=float, default=0.1,
                        help='Dropout rate')
    parser.add_argument('--test-split', type=float, default=0.2,
                        help='Fraction of data for testing')
    parser.add_argument('--hidden-sizes', type=int, nargs='+', default=[16, 8],
                        help='Hidden layer sizes')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress output')
    parser.add_argument('--data-path', type=str, default=None,
                        help='Path to iris.csv data file')
    return parser.parse_args()


def run(seed=42, epochs=200, learning_rate=0.01, batch_size=16,
        dropout=0.1, test_split=0.2, hidden_sizes=None, data_path=None, verbose=True):
    """
    Run the Iris classification example.

    Returns:
        dict with keys: accuracy, epochs_trained
    """
    if hidden_sizes is None:
        hidden_sizes = [16, 8]

    kann_set_seed(seed)
    random.seed(seed)
    if HAS_NUMPY:
        np.random.seed(seed)

    input_size = 4
    output_size = 3

    if verbose:
        print("=" * 60)
        print("Example 06: Iris Classification with KANN MLP")
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
        print("Creating KANN MLP network...")
        print(f"  Architecture: {input_size} -> {hidden_sizes} -> {output_size}")
        print("  Cost function: COST_MULTI_CROSS_ENTROPY (softmax + cross-entropy)")
        print(f"  Dropout: {dropout}")

    with KannNeuralNetwork.mlp(
        input_size=input_size,
        hidden_sizes=hidden_sizes,
        output_size=output_size,
        cost_type=COST_MULTI_CROSS_ENTROPY,
        dropout=dropout
    ) as net:
        if verbose:
            print(f"  Input dim: {net.input_dim}")
            print(f"  Output dim: {net.output_dim}")
            print(f"  Trainable parameters: {net.n_var}")
            print()
            print("Preparing training data...")

        if HAS_NUMPY:
            x_train, y_train = prepare_numpy_data(train_data, output_size)
            if verbose:
                print(f"  Using NumPy arrays: x={x_train.shape}, y={y_train.shape}")
        else:
            x_train, y_train = prepare_numpy_data(train_data, output_size)

        if verbose:
            print()
            print(f"Training (max {epochs} epochs, early stopping enabled)...")
            print(f"  Learning rate: {learning_rate}")
            print(f"  Mini-batch size: {batch_size}")
            print()

        epochs_trained = net.train(
            x_train, y_train,
            learning_rate=learning_rate,
            mini_batch_size=batch_size,
            max_epochs=epochs,
            max_drop_streak=20,
            validation_fraction=0.2
        )

        if verbose:
            print(f"\n  Training completed in {epochs_trained} epochs")
            print()
            print("Evaluating on test set...")

        accuracy, predictions = evaluate_network(net, test_data, output_size)

        if verbose:
            print(f"  Accuracy: {accuracy * 100:.1f}%")

            class_names = ['setosa', 'versicolor', 'virginica']

            per_class = {i: {'correct': 0, 'total': 0} for i in range(output_size)}
            for pred in predictions:
                per_class[pred['true']]['total'] += 1
                if pred['true'] == pred['pred']:
                    per_class[pred['true']]['correct'] += 1

            print("\nPer-class accuracy:")
            for i, name in enumerate(class_names):
                c = per_class[i]['correct']
                t = per_class[i]['total']
                acc = c / t if t > 0 else 0.0
                print(f"  {name:>12}: {c:2d}/{t:2d} = {acc * 100:5.1f}%")

            print("\nSample predictions (first 10 test samples):")
            print("-" * 55)
            for pred in predictions[:10]:
                true_name = class_names[pred['true']]
                pred_name = class_names[pred['pred']]
                status = "OK" if pred['true'] == pred['pred'] else "WRONG"
                print(f"  True: {true_name:>12}, Pred: {pred_name:>12} "
                      f"(conf: {pred['confidence']:.3f}) [{status}]")

            print()
            print("Done!")

    return {
        'accuracy': accuracy,
        'epochs_trained': epochs_trained,
    }


def main():
    args = parse_args()
    return run(
        seed=args.seed,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        dropout=args.dropout,
        test_split=args.test_split,
        hidden_sizes=args.hidden_sizes,
        data_path=args.data_path,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
