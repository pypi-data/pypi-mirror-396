#!/usr/bin/env python3
"""
Example 07: Sequence Prediction with KANN LSTM
===============================================

This example demonstrates using KANN's LSTM (Long Short-Term Memory) network
for learning sequential patterns. LSTMs excel at capturing long-range
dependencies in sequences through their gating mechanisms.

Network: KannNeuralNetwork.lstm() factory method
Task: Sequence prediction (predict next element in pattern)
Dataset: tests/data/sequences.csv (mathematical integer sequences)

Key Concepts:
- Using the lstm() factory method
- Training with train_rnn() for backpropagation through time (BPTT)
- Sequence generation after training
- One-hot encoding for discrete sequences

Usage:
    python tests/examples/kann_lstm_sequence.py
    python tests/examples/kann_lstm_sequence.py --epochs 100 --hidden-size 64
    python tests/examples/kann_lstm_sequence.py --data-path custom_sequences.csv
"""

import argparse
import array
import csv
import os
import random

from cynn.kann import (
    KannNeuralNetwork,
    COST_MULTI_CROSS_ENTROPY,
    set_seed as kann_set_seed,
    softmax_sample,
)


def one_hot_encode(value, num_classes):
    """Create one-hot encoded vector for a single value."""
    vec = array.array('f', [0.0] * num_classes)
    if 0 <= value < num_classes:
        vec[value] = 1.0
    return vec


# ==============================================================================
# Data Loading
# ==============================================================================

# Default path relative to this file
DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'sequences.csv'
)


def load_sequences(filepath):
    """
    Load sequences from a CSV file.

    Expected format: CSV with header row. First column is sequence name,
    remaining columns are integer values (s0, s1, s2, ...).

    Returns:
        tuple: (sequences, vocab_size) where sequences is a list of integer lists
    """
    sequences = []
    max_val = 0

    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header

        for row in reader:
            # First column is name, rest are integer values
            seq = [int(x) for x in row[1:]]
            sequences.append(seq)
            max_val = max(max_val, max(seq))

    vocab_size = max_val + 1
    return sequences, vocab_size


def generate_sequences_fallback(seq_length):
    """Generate fallback sequences if CSV file is not available."""
    seq_len = seq_length + 1

    sequences = [
        [i % 8 for i in range(seq_len)],
        [(7 - i) % 8 for i in range(seq_len)],
        [(2 * i) % 8 for i in range(seq_len)],
        [(2 * i + 1) % 8 for i in range(seq_len)],
        [0 if i % 2 == 0 else 7 for i in range(seq_len)],
        [i // 2 for i in range(seq_len)],
        [0, 1, 1, 2, 3, 5, 0, 5, 5, 2, 7, 1, 0, 1, 1, 2, 3],
        [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2],
    ]

    return sequences, 8  # vocab_size = 8


def get_sequences(data_file, seq_length, verbose=True):
    """
    Load sequences from file or generate fallback if file not found.

    Returns:
        tuple: (sequences, vocab_size)
    """
    if data_file and os.path.exists(data_file):
        if verbose:
            print(f"Loading sequences from: {data_file}")
        return load_sequences(data_file)
    else:
        if verbose:
            if data_file:
                print(f"Data file not found: {data_file}")
            print("Using fallback generated sequences")
        return generate_sequences_fallback(seq_length)


# ==============================================================================
# Training
# ==============================================================================

def train_lstm(sequences, seq_length, hidden_size, vocab_size, epochs,
               learning_rate, batch_size, verbose=True):
    """Train LSTM on sequences and return trained network."""
    if verbose:
        print("Creating LSTM network...")
        print(f"  Vocab size: {vocab_size}")
        print(f"  Hidden size: {hidden_size}")
        print(f"  Sequence length: {seq_length}")
        print()

    net = KannNeuralNetwork.lstm(
        input_size=vocab_size,
        hidden_size=hidden_size,
        output_size=vocab_size,
        cost_type=COST_MULTI_CROSS_ENTROPY
    )

    if verbose:
        print(f"  Network created: {net.n_var} trainable parameters")
        print()
        print(f"Training for max {epochs} epochs...")
        print(f"  Learning rate: {learning_rate}")
        print(f"  Mini-batch size: {batch_size}")
        print()

    history = net.train_rnn(
        sequences,
        seq_length=seq_length,
        vocab_size=vocab_size,
        learning_rate=learning_rate,
        mini_batch_size=batch_size,
        max_epochs=epochs,
        validation_fraction=0.0,
        verbose=1 if verbose else 0
    )

    if verbose:
        print()
        print("Training history:")
        print(f"  Initial loss: {history['loss'][0]:.4f}")
        print(f"  Final loss: {history['loss'][-1]:.4f}")

    return net, history


# ==============================================================================
# Evaluation
# ==============================================================================

def evaluate_predictions(net, sequences, vocab_size, seq_length, verbose=True):
    """Evaluate the network's ability to predict next elements."""
    if verbose:
        print("\nEvaluating predictions on training sequences...")

    total_correct = 0
    total_predictions = 0

    for seq_idx, seq in enumerate(sequences):
        correct = 0
        net.rnn_start()

        for i in range(min(len(seq) - 1, seq_length)):
            inp = one_hot_encode(seq[i], vocab_size)
            output = net.apply(inp)
            pred = list(output).index(max(output))
            expected = seq[i + 1]

            if pred == expected:
                correct += 1
                total_correct += 1
            total_predictions += 1

        net.rnn_end()

        if verbose:
            accuracy = correct / min(len(seq) - 1, seq_length) * 100
            print(f"  Sequence {seq_idx + 1}: {correct}/{min(len(seq)-1, seq_length)} correct ({accuracy:.1f}%)")

    overall_accuracy = total_correct / total_predictions * 100 if total_predictions > 0 else 0.0

    if verbose:
        print(f"\nOverall accuracy: {total_correct}/{total_predictions} ({overall_accuracy:.1f}%)")

    return overall_accuracy


def generate_sequence(net, seed_token, vocab_size, length=16, temperature=0.5):
    """Generate a sequence starting from a seed token."""
    generated = [seed_token]

    net.rnn_start()

    inp = one_hot_encode(seed_token, vocab_size)
    output = net.apply(inp)

    for _ in range(length - 1):
        if temperature > 0:
            next_token = softmax_sample(output, temperature)
        else:
            next_token = list(output).index(max(output))

        generated.append(next_token)

        inp = one_hot_encode(next_token, vocab_size)
        output = net.apply(inp)

    net.rnn_end()

    return generated


# ==============================================================================
# Main
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Sequence Prediction with KANN LSTM',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    parser.add_argument('--epochs', type=int, default=50,
                        help='Number of training epochs')
    parser.add_argument('--learning-rate', type=float, default=0.05,
                        help='Learning rate')
    parser.add_argument('--batch-size', type=int, default=8,
                        help='Mini-batch size')
    parser.add_argument('--hidden-size', type=int, default=32,
                        help='LSTM hidden state size')
    parser.add_argument('--seq-length', type=int, default=16,
                        help='Sequence length for BPTT')
    parser.add_argument('--data-path', type=str, default=DEFAULT_DATA_PATH,
                        help='Path to sequences CSV file')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress output')
    return parser.parse_args()


def run(seed=42, epochs=50, learning_rate=0.05, batch_size=8,
        hidden_size=32, seq_length=16, data_path=DEFAULT_DATA_PATH, verbose=True):
    """
    Run the LSTM sequence prediction example.

    Returns:
        dict with keys: accuracy, initial_loss, final_loss
    """
    kann_set_seed(seed)
    random.seed(seed)

    if verbose:
        print("=" * 60)
        print("Example 07: Sequence Prediction with KANN LSTM")
        print("=" * 60)
        print()

    sequences, vocab_size = get_sequences(data_path, seq_length, verbose)

    if verbose:
        print(f"  Loaded {len(sequences)} sequences")
        print(f"  Vocabulary size: {vocab_size}")
        print()
        print("Sample sequences:")
        for i, seq in enumerate(sequences[:4]):
            print(f"  [{i+1}] {seq}")
        print()

    net, history = train_lstm(
        sequences, seq_length, hidden_size, vocab_size,
        epochs, learning_rate, batch_size, verbose
    )

    accuracy = evaluate_predictions(net, sequences, vocab_size, seq_length, verbose)

    if verbose:
        print("\n" + "=" * 60)
        print("Generating new sequences from different seeds:")
        print("=" * 60)

        for seed_tok in [0, 3, 7]:
            print(f"\n  Seed={seed_tok}, temp=0.0 (greedy): ", end="")
            gen = generate_sequence(net, seed_tok, vocab_size, length=16, temperature=0.0)
            print(" -> ".join(str(x) for x in gen))

            print(f"  Seed={seed_tok}, temp=0.5 (sample): ", end="")
            gen = generate_sequence(net, seed_tok, vocab_size, length=16, temperature=0.5)
            print(" -> ".join(str(x) for x in gen))

    net.close()

    if verbose:
        print()
        print("Done!")

    return {
        'accuracy': accuracy / 100.0,
        'initial_loss': history['loss'][0],
        'final_loss': history['loss'][-1],
    }


def main():
    args = parse_args()
    return run(
        seed=args.seed,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        hidden_size=args.hidden_size,
        seq_length=args.seq_length,
        data_path=args.data_path,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
