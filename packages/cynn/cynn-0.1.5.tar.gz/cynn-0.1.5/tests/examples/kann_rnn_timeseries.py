#!/usr/bin/env python3
"""
Example 09: Time Series Prediction with KANN MLP
==================================================

This example demonstrates using KANN's MLP for time series prediction using
a sliding window approach. While KANN supports RNN/LSTM for sequences, an
MLP with windowed features can also work well for periodic patterns.

Network: KannNeuralNetwork.mlp() factory method
Task: Time series forecasting (sine wave prediction)
Dataset: tests/data/sine_wave.csv

Key Concepts:
- Windowed time series approach (using past N values to predict next)
- Feature engineering for time series
- MLP for sequence-to-value prediction
- Comparing predicted vs actual values

Usage:
    python tests/examples/kann_rnn_timeseries.py
    python tests/examples/kann_rnn_timeseries.py --window-size 20 --epochs 200
"""

import argparse
import csv
import random
from pathlib import Path

import numpy as np

from cynn.kann import (
    KannNeuralNetwork,
    COST_MSE,
    set_seed as kann_set_seed,
)


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
            data.append(float(row['y']))
    return data


def normalize_values(values):
    """Normalize values to [0, 1] range."""
    v_min, v_max = min(values), max(values)
    normalized = [(v - v_min) / (v_max - v_min) for v in values]
    return normalized, v_min, v_max


def denormalize_value(v_norm, v_min, v_max):
    """Convert normalized value back to original scale."""
    return v_norm * (v_max - v_min) + v_min


def create_windowed_sequences(values, window_size):
    """Create input/output pairs using sliding window."""
    sequences = []
    for i in range(len(values) - window_size):
        inp = values[i:i + window_size]
        out = values[i + window_size]
        sequences.append((inp, out))
    return sequences


# ==============================================================================
# Evaluation
# ==============================================================================

def evaluate_predictions(net, test_seqs, v_min, v_max, verbose=True):
    """Evaluate prediction accuracy on test sequences."""
    predictions = []
    total_squared_error = 0.0

    for inp, expected in test_seqs:
        inp_array = np.array(inp, dtype=np.float32)
        output = net.apply(inp_array)
        predicted = output[0]

        error = (predicted - expected) ** 2
        total_squared_error += error

        pred_denorm = denormalize_value(predicted, v_min, v_max)
        exp_denorm = denormalize_value(expected, v_min, v_max)
        predictions.append((exp_denorm, pred_denorm))

    mse = total_squared_error / len(test_seqs) if test_seqs else 0.0
    return mse, predictions


# ==============================================================================
# Main
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Time Series Prediction with KANN MLP',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Maximum training epochs')
    parser.add_argument('--learning-rate', type=float, default=0.01,
                        help='Learning rate')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Mini-batch size')
    parser.add_argument('--window-size', type=int, default=10,
                        help='Sliding window size')
    parser.add_argument('--test-split', type=float, default=0.2,
                        help='Fraction of data for testing')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress output')
    parser.add_argument('--data-path', type=str, default=None,
                        help='Path to sine_wave.csv data file')
    return parser.parse_args()


def run(seed=42, epochs=100, learning_rate=0.01, batch_size=32,
        window_size=10, test_split=0.2, data_path=None, verbose=True):
    """
    Run the time series prediction example.

    Returns:
        dict with keys: mse, rmse, epochs_trained
    """
    kann_set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    if verbose:
        print("=" * 60)
        print("Example 09: Time Series Prediction with KANN MLP")
        print("=" * 60)
        print()
        print("Loading sine wave data...")

    data_file = get_data_path("sine_wave.csv", data_path)
    raw_values = load_sine_wave(data_file)

    if verbose:
        print(f"  Loaded {len(raw_values)} values from {data_file}")

    values, v_min, v_max = normalize_values(raw_values)

    if verbose:
        print(f"  Value range: [{v_min:.2f}, {v_max:.2f}] -> [0, 1]")
        print()
        print("Creating windowed sequences...")
        print(f"  Window size: {window_size}")

    sequences = create_windowed_sequences(values, window_size)

    if verbose:
        print(f"  Created {len(sequences)} sequences")

    split_idx = int(len(sequences) * (1 - test_split))
    train_seqs = sequences[:split_idx]
    test_seqs = sequences[split_idx:]

    if verbose:
        print(f"  Training sequences: {len(train_seqs)}")
        print(f"  Test sequences: {len(test_seqs)}")
        print()

    x_train = np.array([s[0] for s in train_seqs], dtype=np.float32)
    y_train = np.array([[s[1]] for s in train_seqs], dtype=np.float32)

    if verbose:
        print("Creating KANN MLP network...")
        print(f"  Architecture: {window_size} -> [32, 16] -> 1")

    with KannNeuralNetwork.mlp(
        input_size=window_size,
        hidden_sizes=[32, 16],
        output_size=1,
        cost_type=COST_MSE,
        dropout=0.0
    ) as net:
        if verbose:
            print(f"  Trainable parameters: {net.n_var}")
            print()
            print(f"Training for max {epochs} epochs...")
            print(f"  Learning rate: {learning_rate}")
            print(f"  Mini-batch size: {batch_size}")
            print()

        epochs_trained = net.train(
            x_train, y_train,
            learning_rate=learning_rate,
            mini_batch_size=batch_size,
            max_epochs=epochs,
            max_drop_streak=20,
            validation_fraction=0.1
        )

        if verbose:
            print(f"\n  Training completed in {epochs_trained} epochs")
            print()
            print("Evaluating on test set...")

        mse, predictions = evaluate_predictions(net, test_seqs, v_min, v_max, verbose)
        rmse = mse ** 0.5

        if verbose:
            print(f"  Test MSE: {mse:.6f}")
            print(f"  Test RMSE: {rmse:.4f}")

            print("\nSample predictions (first 10):")
            print("-" * 45)
            print(f"  {'Expected':>12}  {'Predicted':>12}  {'Error':>12}")
            print("-" * 45)
            for expected, predicted in predictions[:10]:
                error = abs(predicted - expected)
                print(f"  {expected:>12.4f}  {predicted:>12.4f}  {error:>12.4f}")

            errors = [abs(p[1] - p[0]) for p in predictions]
            print()
            print("Error statistics:")
            print(f"  Mean absolute error: {np.mean(errors):.4f}")
            print(f"  Max absolute error: {np.max(errors):.4f}")
            print(f"  Min absolute error: {np.min(errors):.4f}")

            print()
            print("Done!")

    return {
        'mse': mse,
        'rmse': rmse,
        'epochs_trained': epochs_trained,
    }


def main():
    args = parse_args()
    return run(
        seed=args.seed,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        window_size=args.window_size,
        test_split=args.test_split,
        data_path=args.data_path,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
