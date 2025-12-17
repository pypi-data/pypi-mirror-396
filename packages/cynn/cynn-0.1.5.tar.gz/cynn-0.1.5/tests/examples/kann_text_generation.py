#!/usr/bin/env python3
"""
Example 10: Complete Text Generation Pipeline with KANN LSTM
=============================================================

This example demonstrates a complete text generation pipeline using KANN's LSTM
network. It covers the full workflow from loading a text corpus to generating
new text, including model saving and loading.

Network: KannNeuralNetwork.lstm() factory method
Task: Character-level text generation
Dataset: tests/data/shakespeare_tiny.txt

Key Concepts:
- Complete text generation workflow
- Building character vocabulary
- Training LSTM with train_rnn()
- Continuous text generation with rnn_start/rnn_end
- Temperature-controlled sampling
- Model persistence (save/load)

Usage:
    python tests/examples/kann_text_generation.py
    python tests/examples/kann_text_generation.py --epochs 30 --hidden-size 512
"""

import argparse
import array as arr
import random
import tempfile
from pathlib import Path

from cynn.kann import (
    KannNeuralNetwork,
    COST_MULTI_CROSS_ENTROPY,
    set_seed as kann_set_seed,
    softmax_sample,
)


def one_hot_encode(value, num_classes):
    """Create one-hot encoded vector for a single value."""
    vec = arr.array('f', [0.0] * num_classes)
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


class TextProcessor:
    """Handles text tokenization and vocabulary management."""

    def __init__(self):
        self.char_to_idx = {}
        self.idx_to_char = {}
        self.vocab_size = 0

    def build_vocabulary(self, text):
        """Build character vocabulary from text."""
        chars = sorted(set(text))
        self.char_to_idx = {c: i for i, c in enumerate(chars)}
        self.idx_to_char = {i: c for i, c in enumerate(chars)}
        self.vocab_size = len(chars)
        return self.vocab_size

    def encode(self, text):
        """Convert text to list of token indices."""
        return [self.char_to_idx.get(c, 0) for c in text]

    def decode(self, indices):
        """Convert list of token indices back to text."""
        return ''.join(self.idx_to_char.get(i, '?') for i in indices)

    def text_to_sequences(self, text, seq_length):
        """Convert text to training sequences."""
        encoded = self.encode(text)
        sequences = []
        actual_len = seq_length + 1
        for i in range(0, len(encoded) - actual_len, seq_length // 2):
            seq = encoded[i:i + actual_len]
            if len(seq) == actual_len:
                sequences.append(seq)
        return sequences


# ==============================================================================
# Text Generator
# ==============================================================================

class TextGenerator:
    """High-level text generation interface."""

    def __init__(self, net, processor):
        self.net = net
        self.processor = processor

    def generate(self, seed_text, length=200, temperature=0.7):
        """Generate text starting from seed."""
        generated = list(seed_text)
        vocab_size = self.processor.vocab_size

        self.net.rnn_start()

        output = None
        for char in seed_text:
            idx = self.processor.char_to_idx.get(char, 0)
            inp = one_hot_encode(idx, vocab_size)
            output = self.net.apply(inp)

        for _ in range(length):
            if output is None:
                break

            if temperature > 0:
                next_idx = softmax_sample(output, temperature)
            else:
                next_idx = list(output).index(max(output))

            next_char = self.processor.idx_to_char.get(next_idx, '?')
            generated.append(next_char)

            inp = one_hot_encode(next_idx, vocab_size)
            output = self.net.apply(inp)

        self.net.rnn_end()

        return ''.join(generated)


# ==============================================================================
# Training
# ==============================================================================

def train_model(text, processor, seq_length, hidden_size, epochs,
                learning_rate, batch_size, verbose=True):
    """Train LSTM model on text data."""
    vocab_size = processor.build_vocabulary(text)

    if verbose:
        print(f"  Vocabulary size: {vocab_size} characters")

    sequences = processor.text_to_sequences(text, seq_length)

    if verbose:
        print(f"  Training sequences: {len(sequences)}")
        print()
        print("Creating LSTM network...")
        print(f"  Hidden size: {hidden_size}")

    net = KannNeuralNetwork.lstm(
        input_size=vocab_size,
        hidden_size=hidden_size,
        output_size=vocab_size,
        cost_type=COST_MULTI_CROSS_ENTROPY
    )

    if verbose:
        print(f"  Trainable parameters: {net.n_var}")
        print()
        print(f"Training for {epochs} epochs...")

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

    return net, history


# ==============================================================================
# Main
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Complete Text Generation Pipeline with KANN LSTM',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    parser.add_argument('--epochs', type=int, default=20,
                        help='Number of training epochs')
    parser.add_argument('--learning-rate', type=float, default=0.01,
                        help='Learning rate')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Mini-batch size')
    parser.add_argument('--hidden-size', type=int, default=256,
                        help='LSTM hidden state size')
    parser.add_argument('--seq-length', type=int, default=50,
                        help='Sequence length for training')
    parser.add_argument('--max-text-size', type=int, default=15000,
                        help='Maximum text size to load')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress progress output')
    parser.add_argument('--data-path', type=str, default=None,
                        help='Path to shakespeare_tiny.txt data file')
    return parser.parse_args()


def run(seed=42, epochs=20, learning_rate=0.01, batch_size=32,
        hidden_size=256, seq_length=50, max_text_size=15000, data_path=None, verbose=True):
    """
    Run the text generation example.

    Returns:
        dict with keys: initial_loss, final_loss
    """
    kann_set_seed(seed)
    random.seed(seed)

    if verbose:
        print("=" * 60)
        print("Example 10: Complete Text Generation Pipeline")
        print("=" * 60)
        print()
        print("Loading Shakespeare text...")

    data_file = get_data_path("shakespeare_tiny.txt", data_path)
    with open(data_file, 'r') as f:
        text = f.read()
    if len(text) > max_text_size:
        text = text[:max_text_size]

    if verbose:
        print(f"  Loaded {len(text)} characters from {data_file}")
        print(f"  Sample: {repr(text[:100])}...")
        print()

    processor = TextProcessor()

    if verbose:
        print("=" * 60)
        print("Training")
        print("=" * 60)

    net, history = train_model(
        text, processor, seq_length, hidden_size,
        epochs, learning_rate, batch_size, verbose
    )

    if verbose:
        print()
        print("Training complete!")
        print(f"  Initial loss: {history['loss'][0]:.4f}")
        print(f"  Final loss: {history['loss'][-1]:.4f}")

    generator = TextGenerator(net, processor)

    if verbose:
        print()
        print("=" * 60)
        print("Text Generation Examples")
        print("=" * 60)

        seeds = ["the ", "love ", "what "]

        for seed_text in seeds:
            print(f"\nSeed: '{seed_text}'")
            print("-" * 50)

            for temp in [0.3, 0.7, 1.0]:
                print(f"\nTemperature {temp}:")
                generated = generator.generate(seed_text, length=100, temperature=temp)

                words = generated.split()
                line = "  "
                for word in words:
                    if len(line) + len(word) > 55:
                        print(line)
                        line = "  " + word
                    else:
                        line = line + " " + word if line.strip() else "  " + word
                if line.strip():
                    print(line)

        print()
        print("=" * 60)
        print("Model Persistence Demo")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "shakespeare_lstm.kann"

            print(f"\nSaving model to {model_path}...")
            net.save(str(model_path))
            print(f"  File size: {model_path.stat().st_size} bytes")

            print("\nLoading model...")
            loaded_net = KannNeuralNetwork.load(str(model_path))
            print("  Loaded successfully!")

            loaded_gen = TextGenerator(loaded_net, processor)
            print("\nGenerating with loaded model:")
            result = loaded_gen.generate("the ", length=80, temperature=0.7)
            print(f"  {result}")

            loaded_net.close()

    net.close()

    if verbose:
        print()
        print("Done!")

    return {
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
        max_text_size=args.max_text_size,
        data_path=args.data_path,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
