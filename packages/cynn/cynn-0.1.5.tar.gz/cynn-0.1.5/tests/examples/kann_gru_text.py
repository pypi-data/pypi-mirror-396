#!/usr/bin/env python3
"""
Example 08: Character-Level Text Modeling with KANN GRU
========================================================

This example demonstrates using KANN's GRU (Gated Recurrent Unit) network
for character-level language modeling. GRUs are similar to LSTMs but with
fewer parameters, making them faster to train while still capturing
sequential dependencies effectively.

Network: KannNeuralNetwork.gru() factory method
Task: Character-level language modeling
Dataset: tests/data/shakespeare_tiny.txt

Key Concepts:
- Using the gru() factory method
- Character tokenization (char <-> index mapping)
- Training on text sequences with train_rnn()
- Text generation with temperature sampling
- Using softmax_sample() for diverse generation

Usage:
    python tests/examples/kann_gru_text.py
    python tests/examples/kann_gru_text.py --epochs 50 --hidden-size 256
"""

import argparse
import array
import random
from pathlib import Path

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


def load_text(path, max_size=None):
    """Load text file and return content."""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    if max_size and len(text) > max_size:
        text = text[:max_size]
    return text


def build_vocabulary(text):
    """Build character-to-index and index-to-character mappings."""
    chars = sorted(set(text))
    char_to_idx = {c: i for i, c in enumerate(chars)}
    idx_to_char = {i: c for i, c in enumerate(chars)}
    return char_to_idx, idx_to_char, len(chars)


def text_to_sequences(text, char_to_idx, seq_length):
    """Convert text to sequences of token indices."""
    sequences = []
    actual_len = seq_length + 1
    for i in range(0, len(text) - actual_len, seq_length // 2):
        seq = [char_to_idx[c] for c in text[i:i + actual_len]]
        if len(seq) == actual_len:
            sequences.append(seq)
    return sequences


# ==============================================================================
# Text Generation
# ==============================================================================

def generate_text(net, seed_text, char_to_idx, idx_to_char, vocab_size,
                  length=200, temperature=0.7):
    """Generate text starting from seed."""
    generated = list(seed_text)

    net.rnn_start()

    for char in seed_text:
        idx = char_to_idx.get(char, 0)
        inp = one_hot_encode(idx, vocab_size)
        output = net.apply(inp)

    for _ in range(length):
        if temperature > 0:
            next_idx = softmax_sample(output, temperature)
        else:
            next_idx = list(output).index(max(output))

        next_char = idx_to_char.get(next_idx, '?')
        generated.append(next_char)

        inp = one_hot_encode(next_idx, vocab_size)
        output = net.apply(inp)

    net.rnn_end()

    return ''.join(generated)


# ==============================================================================
# Main
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Character-Level Text Modeling with KANN GRU',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    parser.add_argument('--epochs', type=int, default=30,
                        help='Number of training epochs')
    parser.add_argument('--learning-rate', type=float, default=0.01,
                        help='Learning rate')
    parser.add_argument('--batch-size', type=int, default=16,
                        help='Mini-batch size')
    parser.add_argument('--hidden-size', type=int, default=128,
                        help='GRU hidden state size')
    parser.add_argument('--seq-length', type=int, default=64,
                        help='Sequence length for BPTT')
    parser.add_argument('--max-text-size', type=int, default=20000,
                        help='Maximum text size to load')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress output')
    parser.add_argument('--data-path', type=str, default=None,
                        help='Path to shakespeare_tiny.txt data file')
    return parser.parse_args()


def run(seed=42, epochs=30, learning_rate=0.01, batch_size=16,
        hidden_size=128, seq_length=64, max_text_size=20000, data_path=None, verbose=True):
    """
    Run the GRU text modeling example.

    Returns:
        dict with keys: initial_loss, final_loss, val_loss
    """
    kann_set_seed(seed)
    random.seed(seed)

    if verbose:
        print("=" * 60)
        print("Example 08: Character-Level Text Modeling with KANN GRU")
        print("=" * 60)
        print()
        print("Loading Shakespeare text...")

    data_file = get_data_path("shakespeare_tiny.txt", data_path)
    text = load_text(data_file, max_text_size)

    if verbose:
        print(f"  Loaded {len(text)} characters from {data_file}")

    char_to_idx, idx_to_char, vocab_size = build_vocabulary(text)

    if verbose:
        print(f"  Vocabulary size: {vocab_size} unique characters")
        sample_chars = list(char_to_idx.keys())[:20]
        print(f"  Sample chars: {repr(''.join(sample_chars))}")
        print()
        print("Preparing training sequences...")

    sequences = text_to_sequences(text, char_to_idx, seq_length)

    if verbose:
        print(f"  Created {len(sequences)} sequences of length {seq_length}")
        print()
        print("Creating GRU network...")
        print(f"  Input/Output size: {vocab_size}")
        print(f"  Hidden size: {hidden_size}")

    net = KannNeuralNetwork.gru(
        input_size=vocab_size,
        hidden_size=hidden_size,
        output_size=vocab_size,
        cost_type=COST_MULTI_CROSS_ENTROPY
    )

    if verbose:
        print(f"  Trainable parameters: {net.n_var}")
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
        validation_fraction=0.1,
        verbose=1 if verbose else 0
    )

    if verbose:
        print()
        print("Training completed!")
        print(f"  Initial loss: {history['loss'][0]:.4f}")
        print(f"  Final loss: {history['loss'][-1]:.4f}")
        if history.get('val_loss'):
            print(f"  Final val loss: {history['val_loss'][-1]:.4f}")

        print("\n" + "=" * 60)
        print("Text Generation Examples")
        print("=" * 60)

        seed_text = "the "

        for temp in [0.3, 0.7, 1.0]:
            print(f"\nTemperature = {temp}:")
            print("-" * 50)
            generated = generate_text(
                net, seed_text, char_to_idx, idx_to_char, vocab_size,
                length=150, temperature=temp
            )
            words = generated.split()
            line = ""
            for word in words:
                if len(line) + len(word) > 50:
                    print(f"  {line}")
                    line = word
                else:
                    line = line + " " + word if line else word
            if line:
                print(f"  {line}")

    net.close()

    if verbose:
        print()
        print("Done!")

    return {
        'initial_loss': history['loss'][0],
        'final_loss': history['loss'][-1],
        'val_loss': history['val_loss'][-1] if history.get('val_loss') else None,
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
        max_text_size=args.max_text_size,
        data_path=args.data_path,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
