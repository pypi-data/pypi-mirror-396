#!/usr/bin/env python3
"""
Example 03: Sine Wave Regression with FannNetwork
==================================================

This example demonstrates training a neural network for function approximation
(regression). FannNetwork provides learning rate and momentum controls that
help with faster convergence on smooth functions like sine waves.

Network: FannNetwork (flexible multi-layer with momentum)
Task: Regression (approximate y = sin(x))
Dataset: tests/data/sine_wave.csv

Key Concepts:
- Function approximation / regression tasks
- Using learning_rate and learning_momentum properties
- Train/test split for regression
- Evaluating with Mean Squared Error (MSE)
- Visualizing predictions vs ground truth

Usage:
    python tests/examples/fann_regression.py
    python tests/examples/fann_regression.py --epochs 2000 --learning-rate 0.5
"""

import argparse
import csv
import random
from pathlib import Path

from cynn.fann import FannNetwork, seed as fann_seed


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


def load_sine_wave(path):
    """Load sine wave dataset from CSV."""
    data = []
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            x = float(row['x'])
            y = float(row['y'])
            data.append((x, y))
    return data


def normalize_data(data):
    """Normalize x and y values to [0, 1] range for better training."""
    x_vals = [x for x, _ in data]
    y_vals = [y for _, y in data]

    x_min, x_max = min(x_vals), max(x_vals)
    y_min, y_max = min(y_vals), max(y_vals)

    normalized = [
        ((x - x_min) / (x_max - x_min), (y - y_min) / (y_max - y_min))
        for x, y in data
    ]
    stats = {'x_min': x_min, 'x_max': x_max, 'y_min': y_min, 'y_max': y_max}
    return normalized, stats


def denormalize_y(y_norm, stats):
    """Convert normalized y back to original scale."""
    return y_norm * (stats['y_max'] - stats['y_min']) + stats['y_min']


def split_data(data, test_fraction):
    """Split data into training and test sets (preserving order for regression)."""
    step = int(1 / test_fraction)
    test_indices = set(range(0, len(data), step))

    train = [d for i, d in enumerate(data) if i not in test_indices]
    test = [d for i, d in enumerate(data) if i in test_indices]
    return train, test


# ==============================================================================
# Training
# ==============================================================================

def train_network(net, train_data, epochs, verbose=True):
    """Train network on sine wave data."""
    inputs_list = [[x] for x, _ in train_data]
    targets_list = [[y] for _, y in train_data]

    losses = []
    for epoch in range(epochs):
        stats = net.train_batch(inputs_list, targets_list, shuffle=True)
        losses.append(stats['mean_loss'])

        if verbose and (epoch + 1) % 200 == 0:
            print(f"  Epoch {epoch + 1:4d}/{epochs}: MSE = {stats['mean_loss']:.6f}")

    return losses


# ==============================================================================
# Evaluation
# ==============================================================================

def evaluate_network(net, test_data, norm_stats=None):
    """Evaluate network on test data."""
    predictions = []
    total_squared_error = 0.0

    for x, y_true in test_data:
        output = net.predict([x])
        y_pred = output[0]

        error = (y_pred - y_true) ** 2
        total_squared_error += error

        if norm_stats:
            y_true_orig = denormalize_y(y_true, norm_stats)
            y_pred_orig = denormalize_y(y_pred, norm_stats)
            predictions.append((x, y_true_orig, y_pred_orig))
        else:
            predictions.append((x, y_true, y_pred))

    mse = total_squared_error / len(test_data) if test_data else 0.0
    return mse, predictions


def print_predictions_sample(predictions, n=10):
    """Print a sample of predictions."""
    step = max(1, len(predictions) // n)
    sample = predictions[::step][:n]

    print("\nSample predictions:")
    print("-" * 50)
    print(f"  {'x':>8}  {'y_true':>10}  {'y_pred':>10}  {'error':>10}")
    print("-" * 50)

    for x, y_true, y_pred in sample:
        error = abs(y_pred - y_true)
        print(f"  {x:>8.4f}  {y_true:>10.4f}  {y_pred:>10.4f}  {error:>10.4f}")


def print_ascii_plot(predictions, width=60, height=15):
    """Print a simple ASCII plot of predictions vs ground truth."""
    sorted_preds = sorted(predictions, key=lambda p: p[0])
    step = max(1, len(sorted_preds) // width)
    sampled = sorted_preds[::step][:width]

    grid = [[' ' for _ in range(width)] for _ in range(height)]

    y_min = min(min(p[1], p[2]) for p in sampled)
    y_max = max(max(p[1], p[2]) for p in sampled)
    y_range = y_max - y_min if y_max > y_min else 1.0

    for col, (x, y_true, y_pred) in enumerate(sampled):
        row_true = int((1 - (y_true - y_min) / y_range) * (height - 1))
        row_true = max(0, min(height - 1, row_true))
        grid[row_true][col] = 'o'

        row_pred = int((1 - (y_pred - y_min) / y_range) * (height - 1))
        row_pred = max(0, min(height - 1, row_pred))
        if grid[row_pred][col] == 'o':
            grid[row_pred][col] = '@'
        else:
            grid[row_pred][col] = '*'

    print("\nPlot (o=true, *=predicted, @=overlap):")
    print("+" + "-" * width + "+")
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "-" * width + "+")


# ==============================================================================
# Main
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Sine Wave Regression with FannNetwork',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--seed', type=int, default=123,
                        help='Random seed for reproducibility')
    parser.add_argument('--epochs', type=int, default=1000,
                        help='Number of training epochs')
    parser.add_argument('--learning-rate', type=float, default=0.7,
                        help='Learning rate')
    parser.add_argument('--momentum', type=float, default=0.1,
                        help='Learning momentum')
    parser.add_argument('--test-split', type=float, default=0.2,
                        help='Fraction of data for testing')
    parser.add_argument('--hidden-size', type=int, default=64,
                        help='Hidden layer size')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress output')
    parser.add_argument('--data-path', type=str, default=None,
                        help='Path to sine_wave.csv data file')
    return parser.parse_args()


def run(seed=123, epochs=1000, learning_rate=0.7, momentum=0.1,
        test_split=0.2, hidden_size=64, data_path=None, verbose=True):
    """
    Run the sine wave regression example.

    Returns:
        dict with keys: mse, rmse, initial_loss, final_loss, epochs
    """
    fann_seed(seed)
    random.seed(seed)

    network_layers = [1, hidden_size, 1]

    if verbose:
        print("=" * 60)
        print("Example 03: Sine Wave Regression with FannNetwork")
        print("=" * 60)
        print()
        print("Loading sine wave dataset...")

    data_file = get_data_path("sine_wave.csv", data_path)
    raw_data = load_sine_wave(data_file)

    if verbose:
        print(f"  Loaded {len(raw_data)} samples from {data_file}")

    data, norm_stats = normalize_data(raw_data)

    if verbose:
        print(f"  X range: [{norm_stats['x_min']:.2f}, {norm_stats['x_max']:.2f}] -> [0, 1]")
        print(f"  Y range: [{norm_stats['y_min']:.2f}, {norm_stats['y_max']:.2f}] -> [0, 1]")

    train_data, test_data = split_data(data, test_split)

    if verbose:
        print(f"  Training set: {len(train_data)} samples")
        print(f"  Test set: {len(test_data)} samples")
        print()
        print("Creating network...")
        print(f"  Architecture: {network_layers}")

    with FannNetwork(network_layers) as net:
        net.learning_rate = learning_rate
        net.learning_momentum = momentum

        if verbose:
            print(f"  Learning rate: {net.learning_rate}")
            print(f"  Momentum: {net.learning_momentum}")
            print(f"  Total neurons: {net.total_neurons}")
            print(f"  Total connections: {net.total_connections}")
            print()
            print(f"Training for {epochs} epochs...")

        losses = train_network(net, train_data, epochs, verbose)

        if verbose:
            print()
            print("Loss progression:")
            print(f"  Initial MSE: {losses[0]:.6f}")
            print(f"  Final MSE:   {losses[-1]:.6f}")
            print()
            print("Evaluating on test set...")

        test_mse, predictions = evaluate_network(net, test_data, norm_stats)

        if verbose:
            print(f"  Test MSE: {test_mse:.6f}")
            print(f"  Test RMSE: {test_mse ** 0.5:.6f}")
            print_predictions_sample(predictions)
            print_ascii_plot(predictions)
            print()
            print("Done!")

    return {
        'mse': test_mse,
        'rmse': test_mse ** 0.5,
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
        momentum=args.momentum,
        test_split=args.test_split,
        hidden_size=args.hidden_size,
        data_path=args.data_path,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
