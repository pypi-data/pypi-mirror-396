#!/usr/bin/env python3
"""
Example 01: XOR Problem with TinnNetwork
========================================

This example demonstrates training a simple neural network on the XOR problem,
the classic non-linearly separable classification task that requires a hidden layer.

Network: TinnNetwork (fixed 3-layer: input -> hidden -> output)
Task: Binary classification (XOR gate)
Dataset: Inline (4 samples)

Key Concepts:
- Creating a TinnNetwork with specified layer sizes
- Training loop with learning rate annealing
- Tracking loss over epochs
- Making predictions after training
- Saving and loading models

Usage:
    python tests/examples/tinn_xor.py
    python tests/examples/tinn_xor.py --epochs 3000 --learning-rate 1.5
"""

import argparse
import random
import tempfile
from pathlib import Path

from cynn.tinn import TinnNetwork, seed as tinn_seed


# ==============================================================================
# Data
# ==============================================================================

# XOR truth table: output is 1 when inputs differ, 0 when same
XOR_DATA = [
    ([0.0, 0.0], [0.0]),  # 0 XOR 0 = 0
    ([0.0, 1.0], [1.0]),  # 0 XOR 1 = 1
    ([1.0, 0.0], [1.0]),  # 1 XOR 0 = 1
    ([1.0, 1.0], [0.0]),  # 1 XOR 1 = 0
]


# ==============================================================================
# Training
# ==============================================================================

def train_network(net, data, epochs, initial_lr, lr_decay, verbose=True):
    """
    Train the network on XOR data with learning rate annealing.

    Args:
        net: TinnNetwork instance
        data: List of (inputs, targets) tuples
        epochs: Number of training epochs
        initial_lr: Starting learning rate
        lr_decay: Learning rate decay factor per epoch
        verbose: Print progress

    Returns:
        List of loss values per epoch
    """
    losses = []
    learning_rate = initial_lr

    for epoch in range(epochs):
        epoch_loss = 0.0

        # Shuffle data each epoch for better convergence
        random.shuffle(data)

        # Train on each sample
        for inputs, targets in data:
            loss = net.train(inputs, targets, learning_rate)
            epoch_loss += loss

        # Record average loss for this epoch
        avg_loss = epoch_loss / len(data)
        losses.append(avg_loss)

        # Decay learning rate
        learning_rate *= lr_decay

        # Progress output every 200 epochs
        if verbose and (epoch + 1) % 200 == 0:
            print(f"  Epoch {epoch + 1:4d}/{epochs}: loss = {avg_loss:.6f}, lr = {learning_rate:.4f}")

    return losses


# ==============================================================================
# Evaluation
# ==============================================================================

def evaluate_network(net, data):
    """
    Evaluate network accuracy on XOR data.

    Args:
        net: Trained TinnNetwork
        data: List of (inputs, targets) tuples

    Returns:
        Tuple of (accuracy, predictions)
    """
    correct = 0
    predictions = []

    for inputs, targets in data:
        output = net.predict(inputs)
        predicted = output[0]
        expected = targets[0]

        # Round to 0 or 1 for classification
        predicted_class = 1.0 if predicted >= 0.5 else 0.0

        predictions.append({
            'inputs': inputs,
            'expected': expected,
            'predicted_raw': predicted,
            'predicted_class': predicted_class,
        })

        if predicted_class == expected:
            correct += 1

    accuracy = correct / len(data)
    return accuracy, predictions


# ==============================================================================
# Main
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='XOR Problem with TinnNetwork',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--seed', type=int, default=123,
                        help='Random seed for reproducibility')
    parser.add_argument('--epochs', type=int, default=2000,
                        help='Number of training epochs')
    parser.add_argument('--learning-rate', type=float, default=2.0,
                        help='Initial learning rate')
    parser.add_argument('--lr-decay', type=float, default=0.998,
                        help='Learning rate decay factor per epoch')
    parser.add_argument('--hidden-size', type=int, default=8,
                        help='Hidden layer size')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress output')
    return parser.parse_args()


def run(seed=123, epochs=2000, learning_rate=2.0, lr_decay=0.998,
        hidden_size=8, verbose=True):
    """
    Run the XOR training example.

    Returns:
        dict with keys: accuracy, initial_loss, final_loss, epochs
    """
    # Set random seeds for reproducibility
    tinn_seed(seed)
    random.seed(seed)

    input_size = 2
    output_size = 1

    if verbose:
        print("=" * 60)
        print("Example 01: XOR Problem with TinnNetwork")
        print("=" * 60)
        print()
        print("Creating network...")
        print(f"  Architecture: {input_size} -> {hidden_size} -> {output_size}")

    # Use context manager for automatic cleanup
    with TinnNetwork(input_size, hidden_size, output_size) as net:
        if verbose:
            print(f"  Shape: {net.shape}")
            print()
            print(f"Training for {epochs} epochs...")

        losses = train_network(
            net,
            XOR_DATA.copy(),
            epochs,
            learning_rate,
            lr_decay,
            verbose=verbose
        )

        if verbose:
            print()
            print("Loss progression:")
            print(f"  Initial: {losses[0]:.6f}")
            print(f"  Final:   {losses[-1]:.6f}")
            print()
            print("Evaluating...")

        accuracy, predictions = evaluate_network(net, XOR_DATA)

        if verbose:
            print("\nPredictions:")
            print("-" * 50)
            for pred in predictions:
                status = "OK" if pred['predicted_class'] == pred['expected'] else "WRONG"
                print(f"  {pred['inputs']} -> {pred['predicted_raw']:.4f} "
                      f"(class: {pred['predicted_class']:.0f}, expected: {pred['expected']:.0f}) [{status}]")

            print("-" * 50)
            print(f"Accuracy: {accuracy * 100:.1f}%")
            print()

            # Demonstrate save/load
            print("Demonstrating save/load...")
            with tempfile.TemporaryDirectory() as tmpdir:
                model_path = Path(tmpdir) / "xor_model.tinn"
                net.save(str(model_path))
                print(f"  Saved model to {model_path}")

                loaded_net = TinnNetwork.load(str(model_path))
                print(f"  Loaded model from {model_path}")

                _, loaded_preds = evaluate_network(loaded_net, XOR_DATA)
                match = all(
                    abs(p1['predicted_raw'] - p2['predicted_raw']) < 1e-6
                    for p1, p2 in zip(predictions, loaded_preds)
                )
                print(f"  Predictions match: {match}")

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
        lr_decay=args.lr_decay,
        hidden_size=args.hidden_size,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
