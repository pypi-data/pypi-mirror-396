#!/usr/bin/env python3
"""
Download public datasets for cynn examples.

This script downloads datasets from public sources and prepares them
for use with the examples in the examples/ directory.

Datasets:
- Iris: UCI Machine Learning Repository
- MNIST: Yann LeCun's website (subset)
- Shakespeare: Project Gutenberg

Usage:
    python scripts/download_datasets.py

The datasets will be saved to tests/data/
"""

import gzip
import os
import struct
import urllib.request
from pathlib import Path

# Output directory
DATA_DIR = Path(__file__).parent.parent / "tests" / "data"


def download_file(url, dest_path, description=""):
    """Download a file from URL to destination path."""
    print(f"Downloading {description or url}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"  Saved to {dest_path}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def download_iris():
    """Download Iris dataset from UCI ML Repository."""
    print("\n=== Iris Dataset ===")
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"

    # Download raw data
    print("Downloading from UCI ML Repository...")
    try:
        response = urllib.request.urlopen(url)
        raw_data = response.read().decode('utf-8')
    except Exception as e:
        print(f"  Error downloading: {e}")
        return False

    # Parse and normalize
    lines = [line.strip() for line in raw_data.strip().split('\n') if line.strip()]

    # Map class names to integers
    class_map = {'Iris-setosa': 0, 'Iris-versicolor': 1, 'Iris-virginica': 2}

    data = []
    for line in lines:
        parts = line.split(',')
        if len(parts) == 5:
            features = [float(x) for x in parts[:4]]
            label = class_map.get(parts[4], -1)
            if label >= 0:
                data.append(features + [label])

    if not data:
        print("  Error: No valid data parsed")
        return False

    # Calculate min/max for normalization
    mins = [min(row[i] for row in data) for i in range(4)]
    maxs = [max(row[i] for row in data) for i in range(4)]

    # Write normalized CSV
    output_path = DATA_DIR / "iris.csv"
    with open(output_path, 'w') as f:
        f.write('sepal_length,sepal_width,petal_length,petal_width,class\n')
        for row in data:
            normalized = [(row[i] - mins[i]) / (maxs[i] - mins[i]) for i in range(4)]
            f.write(f'{normalized[0]:.6f},{normalized[1]:.6f},{normalized[2]:.6f},{normalized[3]:.6f},{int(row[4])}\n')

    print(f"  Created {output_path} with {len(data)} samples (normalized to [0,1])")
    return True


def download_mnist():
    """Download MNIST dataset and create a subset."""
    print("\n=== MNIST Dataset ===")

    # MNIST URLs (from Yann LeCun's website mirror)
    base_url = "https://storage.googleapis.com/cvdf-datasets/mnist/"
    files = {
        'train_images': 'train-images-idx3-ubyte.gz',
        'train_labels': 'train-labels-idx1-ubyte.gz',
    }

    temp_dir = DATA_DIR / "temp_mnist"
    temp_dir.mkdir(exist_ok=True)

    try:
        # Download files
        for name, filename in files.items():
            url = base_url + filename
            dest = temp_dir / filename
            if not download_file(url, dest, f"MNIST {name}"):
                return False

        # Read images
        print("Processing MNIST data...")
        with gzip.open(temp_dir / files['train_images'], 'rb') as f:
            magic, num_images, rows, cols = struct.unpack('>IIII', f.read(16))
            images = []
            for _ in range(num_images):
                image = struct.unpack(f'>{rows*cols}B', f.read(rows * cols))
                images.append(image)

        # Read labels
        with gzip.open(temp_dir / files['train_labels'], 'rb') as f:
            magic, num_labels = struct.unpack('>II', f.read(8))
            labels = struct.unpack(f'>{num_labels}B', f.read(num_labels))

        # Create balanced subset (50 samples per digit = 500 total)
        samples_per_digit = 50
        subset = {i: [] for i in range(10)}

        for img, label in zip(images, labels):
            if len(subset[label]) < samples_per_digit:
                subset[label].append(img)
            if all(len(v) >= samples_per_digit for v in subset.values()):
                break

        # Write CSV
        output_path = DATA_DIR / "mnist_subset.csv"
        with open(output_path, 'w') as f:
            header = 'label,' + ','.join(f'pixel_{i}' for i in range(784))
            f.write(header + '\n')

            count = 0
            for digit in range(10):
                for img in subset[digit]:
                    # Normalize pixel values to [0, 1]
                    normalized = [p / 255.0 for p in img]
                    row = f'{digit},' + ','.join(f'{p:.4f}' for p in normalized)
                    f.write(row + '\n')
                    count += 1

        print(f"  Created {output_path} with {count} samples")

        # Cleanup temp files
        for filename in files.values():
            (temp_dir / filename).unlink(missing_ok=True)
        temp_dir.rmdir()

        return True

    except Exception as e:
        print(f"  Error: {e}")
        # Cleanup on error
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False


def generate_sine_wave():
    """Generate sine wave dataset (mathematical, no download needed)."""
    print("\n=== Sine Wave Dataset ===")
    import math

    samples = 1000
    x_max = 4 * math.pi  # 2 full cycles

    output_path = DATA_DIR / "sine_wave.csv"
    with open(output_path, 'w') as f:
        f.write('x,y\n')
        for i in range(samples):
            x = (i / (samples - 1)) * x_max
            y = math.sin(x)
            f.write(f'{x:.6f},{y:.6f}\n')

    print(f"  Created {output_path} with {samples} samples")
    return True


def download_shakespeare():
    """Download Shakespeare text from Project Gutenberg."""
    print("\n=== Shakespeare Text ===")

    # The Complete Works of Shakespeare from Project Gutenberg
    url = "https://www.gutenberg.org/cache/epub/100/pg100.txt"

    print("Downloading from Project Gutenberg...")
    try:
        response = urllib.request.urlopen(url)
        text = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"  Error downloading: {e}")
        return False

    # Extract a portion and clean it
    # Skip the header/license (find first play)
    start_marker = "THE SONNETS"
    end_marker = "End of the Project Gutenberg"

    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker)

    if start_idx == -1:
        start_idx = 0
    if end_idx == -1:
        end_idx = len(text)

    # Extract ~50KB of text
    target_size = 50000
    extracted = text[start_idx:start_idx + target_size]

    # Clean: lowercase, ASCII only, normalize whitespace
    cleaned = []
    for char in extracted.lower():
        if char.isascii() and (char.isalnum() or char in ' \n.,;:!?\'"()-'):
            cleaned.append(char)

    cleaned_text = ''.join(cleaned)

    # Normalize multiple newlines/spaces
    import re
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)

    output_path = DATA_DIR / "shakespeare_tiny.txt"
    with open(output_path, 'w') as f:
        f.write(cleaned_text)

    print(f"  Created {output_path} ({len(cleaned_text)} characters)")
    return True


def main():
    """Download all datasets."""
    print("=" * 60)
    print("Downloading datasets for cynn examples")
    print("=" * 60)

    # Ensure output directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    results = {
        'Iris': download_iris(),
        'MNIST': download_mnist(),
        'Sine Wave': generate_sine_wave(),
        'Shakespeare': download_shakespeare(),
    }

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    for name, success in results.items():
        status = "OK" if success else "FAILED"
        print(f"  {name}: {status}")

    if all(results.values()):
        print("\nAll datasets downloaded successfully!")
        return 0
    else:
        print("\nSome downloads failed. Check errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
