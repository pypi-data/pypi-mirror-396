# Test Datasets

This directory contains datasets used by the examples in `examples/`.

To download/regenerate datasets, run:
```bash
python scripts/download_datasets.py
```

## Files

### iris.csv
The classic Iris flower dataset for classification tasks.
- **Source**: [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/iris)
- **Samples**: 150
- **Features**: 4 (sepal_length, sepal_width, petal_length, petal_width)
- **Classes**: 3 (0=setosa, 1=versicolor, 2=virginica)
- **Format**: CSV with header
- **Values**: Normalized to [0, 1] range

### sine_wave.csv
Generated sine wave data for regression tasks.
- **Source**: Mathematically generated (y = sin(x))
- **Samples**: 1000
- **Columns**: x, y where y = sin(x)
- **Range**: x in [0, 4*pi] (2 full cycles)
- **Format**: CSV with header

### mnist_subset.csv
A small subset of the MNIST handwritten digit dataset.
- **Source**: [MNIST Database](http://yann.lecun.com/exdb/mnist/) via Google Cloud mirror
- **Samples**: 500 (50 per digit, balanced)
- **Features**: 784 (28x28 pixel values)
- **Classes**: 10 (digits 0-9)
- **Format**: CSV with header (label, pixel_0, ..., pixel_783)
- **Values**: Normalized to [0, 1] range

### shakespeare_tiny.txt
A small excerpt of Shakespeare text for character-level language modeling.
- **Source**: [Project Gutenberg](https://www.gutenberg.org/ebooks/100) (Complete Works of Shakespeare)
- **Size**: ~47KB
- **Format**: Plain ASCII text, lowercase
- **Content**: Sonnets and early plays

### sequences.csv
Integer sequences for LSTM sequence prediction training.
- **Source**: Mathematically generated patterns
- **Samples**: 15 sequences
- **Length**: 17 elements each (for seq_length=16 training)
- **Values**: Integers 0-9 (various mathematical sequences)
- **Format**: CSV with header (name, s0, s1, ..., s16)
- **Patterns include**: Forward/reverse counting, Fibonacci mod 8, pi digits, triangular numbers, prime numbers mod 8, Collatz sequence, popcount
