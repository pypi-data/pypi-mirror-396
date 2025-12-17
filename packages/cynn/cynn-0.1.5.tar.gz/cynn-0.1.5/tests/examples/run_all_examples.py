#!/usr/bin/env python3
"""
Run All Examples - cynn Neural Network Library
===============================================

This script runs all cynn examples, collects results, and provides a summary
with performance ratings.

Usage:
    python tests/examples/run_all_examples.py
    python tests/examples/run_all_examples.py --ratio 0.5   # Half epochs
    python tests/examples/run_all_examples.py --verbose     # Show full output
"""

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# Add examples directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class ExampleResult:
    """Result from running an example."""
    name: str
    success: bool
    duration: float
    metrics: dict
    error: str = ""


# ==============================================================================
# Performance Rating
# ==============================================================================

def rate_performance(example_num: int, metrics: dict) -> tuple[str, str]:
    """
    Rate the performance of an example based on its metrics.

    Returns: (rating, explanation)
    """
    if not metrics:
        return "N/A", "No metrics available"

    # Rating thresholds for each example type
    if example_num == 1:  # XOR
        acc = metrics.get('accuracy', 0)
        if acc >= 1.0:
            return "Excellent", "100% accuracy on XOR"
        elif acc >= 0.75:
            return "Good", f"{acc*100:.0f}% accuracy"
        else:
            return "Poor", f"Only {acc*100:.0f}% accuracy"

    elif example_num == 2:  # Iris
        acc = metrics.get('accuracy', 0)
        if acc >= 0.95:
            return "Excellent", f"{acc*100:.0f}% test accuracy"
        elif acc >= 0.85:
            return "Good", f"{acc*100:.0f}% test accuracy"
        else:
            return "Fair", f"{acc*100:.0f}% test accuracy"

    elif example_num == 3:  # Sine regression
        mse = metrics.get('mse', 1)
        if mse <= 0.005:
            return "Excellent", f"MSE={mse:.4f}"
        elif mse <= 0.02:
            return "Good", f"MSE={mse:.4f}"
        else:
            return "Fair", f"MSE={mse:.4f}"

    elif example_num == 4:  # MNIST CNN
        acc = metrics.get('accuracy', 0)
        if acc >= 0.90:
            return "Excellent", f"{acc*100:.0f}% test accuracy"
        elif acc >= 0.80:
            return "Good", f"{acc*100:.0f}% test accuracy"
        else:
            return "Fair", f"{acc*100:.0f}% test accuracy"

    elif example_num == 5:  # KANN MLP Iris
        acc = metrics.get('accuracy', 0)
        if acc >= 0.95:
            return "Excellent", f"{acc*100:.0f}% test accuracy"
        elif acc >= 0.85:
            return "Good", f"{acc*100:.0f}% test accuracy"
        else:
            return "Fair", f"{acc*100:.0f}% test accuracy"

    elif example_num == 6:  # LSTM sequence
        acc = metrics.get('accuracy', 0)
        if acc >= 0.90:
            return "Excellent", f"{acc*100:.0f}% prediction accuracy"
        elif acc >= 0.70:
            return "Good", f"{acc*100:.0f}% prediction accuracy"
        else:
            return "Fair", f"{acc*100:.0f}% prediction accuracy"

    elif example_num == 7:  # GRU text
        final_loss = metrics.get('final_loss', 10)
        initial_loss = metrics.get('initial_loss', 10)
        improvement = (initial_loss - final_loss) / initial_loss if initial_loss > 0 else 0
        if improvement >= 0.5:
            return "Excellent", f"Loss {initial_loss:.2f}->{final_loss:.2f}"
        elif improvement >= 0.2:
            return "Good", f"Loss {initial_loss:.2f}->{final_loss:.2f}"
        else:
            return "Fair", f"Loss {initial_loss:.2f}->{final_loss:.2f}"

    elif example_num == 8:  # Time series
        rmse = metrics.get('rmse', 1)
        if rmse <= 0.02:
            return "Excellent", f"RMSE={rmse:.4f}"
        elif rmse <= 0.05:
            return "Good", f"RMSE={rmse:.4f}"
        else:
            return "Fair", f"RMSE={rmse:.4f}"

    elif example_num == 9:  # Text generation
        final_loss = metrics.get('final_loss', 10)
        initial_loss = metrics.get('initial_loss', 10)
        improvement = (initial_loss - final_loss) / initial_loss if initial_loss > 0 else 0
        if improvement >= 0.4:
            return "Excellent", f"Loss {initial_loss:.2f}->{final_loss:.2f}"
        elif improvement >= 0.2:
            return "Good", f"Loss {initial_loss:.2f}->{final_loss:.2f}"
        else:
            return "Fair", f"Loss {initial_loss:.2f}->{final_loss:.2f}"

    return "N/A", "Unknown example"


# ==============================================================================
# Example Runners
# ==============================================================================

def run_example_01(quick=False):
    """Run XOR example."""
    from examples import ex01_tinn_xor as ex01
    epochs = 1000 if quick else 2000
    return ex01.run(epochs=epochs, verbose=False)


def run_example_02(quick=False):
    """Run Iris classification example."""
    from examples import ex02_genann_iris as ex02
    epochs = 150 if quick else 300
    return ex02.run(epochs=epochs, verbose=False)


def run_example_03(quick=False):
    """Run sine regression example."""
    from examples import ex03_fann_regression as ex03
    epochs = 500 if quick else 1000
    return ex03.run(epochs=epochs, verbose=False)


def run_example_04(quick=False):
    """Run MNIST CNN example."""
    from examples import ex05_cnn_mnist as ex04
    epochs = 25 if quick else 50
    return ex04.run(epochs=epochs, verbose=False)


def run_example_05(quick=False):
    """Run KANN MLP Iris example."""
    from examples import ex06_kann_mlp_iris as ex05
    epochs = 100 if quick else 200
    return ex05.run(epochs=epochs, verbose=False)


def run_example_06(quick=False):
    """Run LSTM sequence example."""
    from examples import ex07_kann_lstm_sequence as ex06
    epochs = 25 if quick else 50
    return ex06.run(epochs=epochs, verbose=False)


def run_example_07(quick=False):
    """Run GRU text example."""
    from examples import ex08_kann_gru_text as ex07
    epochs = 15 if quick else 30
    return ex07.run(epochs=epochs, verbose=False)


def run_example_08(quick=False):
    """Run time series example."""
    from examples import ex09_kann_rnn_timeseries as ex08
    epochs = 50 if quick else 100
    return ex08.run(epochs=epochs, verbose=False)


def run_example_09(quick=False):
    """Run text generation example."""
    from examples import ex10_kann_text_generation as ex09
    epochs = 10 if quick else 20
    return ex09.run(epochs=epochs, verbose=False)


# Example info
EXAMPLES = [
    (1, "TinnNetwork XOR", "tinn_xor", run_example_01),
    (2, "GenannNetwork Iris", "genann_iris", run_example_02),
    (3, "FannNetwork Regression", "fann_regression", run_example_03),
    (4, "CNNNetwork MNIST", "cnn_mnist", run_example_04),
    (5, "KANN MLP Iris", "kann_mlp_iris", run_example_05),
    (6, "KANN LSTM Sequence", "kann_lstm_sequence", run_example_06),
    (7, "KANN GRU Text", "kann_gru_text", run_example_07),
    (8, "KANN MLP Timeseries", "kann_rnn_timeseries", run_example_08),
    (9, "KANN LSTM TextGen", "kann_text_generation", run_example_09),
]


# ==============================================================================
# Main
# ==============================================================================

def import_examples():
    """Import all example modules with renamed imports."""
    import importlib.util
    examples_dir = Path(__file__).parent

    modules = {}
    for num, name, filename, _ in EXAMPLES:
        module_name = f"ex{num:02d}_{filename.split('_', 1)[1]}"
        filepath = examples_dir / f"{filename}.py"

        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"examples.{module_name}"] = module
        spec.loader.exec_module(module)
        modules[num] = module

    return modules


def run_all_examples(ratio=1.0, verbose=False, data_dir=None):
    """Run all examples and collect results."""
    print("=" * 70)
    print("Running All cynn Examples")
    print("=" * 70)
    print()

    # Data file mapping for examples that need external data
    DATA_FILES = {
        2: "iris.csv",
        3: "sine_wave.csv",
        4: "mnist_subset.csv",
        5: "iris.csv",
        6: "sequences.csv",
        7: "shakespeare_tiny.txt",
        8: "sine_wave.csv",
        9: "shakespeare_tiny.txt",
    }

    # Base epochs for each example (at ratio=1.0)
    BASE_EPOCHS = {
        1: 2000, 2: 300, 3: 1000, 4: 50, 5: 200,
        6: 50, 7: 30, 8: 100, 9: 20
    }

    print(f"Training ratio: {ratio:.0%}")
    print()

    # Import all modules
    print("Importing example modules...")
    modules = import_examples()
    print("  Done!")
    print()

    results = []
    total_start = time.time()

    for num, name, filename, _ in EXAMPLES:
        print(f"Running Example {num:02d}: {name}...")

        module = modules[num]
        start_time = time.time()

        try:
            # Calculate epochs based on ratio
            epochs = max(1, int(BASE_EPOCHS[num] * ratio))

            kwargs = {'epochs': epochs, 'verbose': verbose}

            # Add data_path if this example uses external data
            if data_dir and num in DATA_FILES:
                kwargs['data_path'] = str(Path(data_dir) / DATA_FILES[num])

            metrics = module.run(**kwargs)

            duration = time.time() - start_time
            result = ExampleResult(
                name=name,
                success=True,
                duration=duration,
                metrics=metrics
            )
            rating, explanation = rate_performance(num, metrics)
            print(f"  Completed in {duration:.1f}s - {rating}: {explanation}")

        except Exception as e:
            duration = time.time() - start_time
            result = ExampleResult(
                name=name,
                success=False,
                duration=duration,
                metrics={},
                error=str(e)
            )
            print(f"  FAILED after {duration:.1f}s: {e}")

        results.append((num, result))
        print()

    total_duration = time.time() - total_start

    # Print summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()

    # Results table
    print(f"{'#':<3} {'Example':<28} {'Status':<8} {'Time':>8} {'Rating':<10} {'Details'}")
    print("-" * 90)

    passed = 0
    for num, result in results:
        status = "OK" if result.success else "FAILED"
        if result.success:
            passed += 1
            rating, explanation = rate_performance(num, result.metrics)
        else:
            rating = "N/A"
            explanation = result.error[:30] + "..." if len(result.error) > 30 else result.error

        print(f"{num:<3} {result.name:<28} {status:<8} {result.duration:>6.1f}s  {rating:<10} {explanation}")

    print("-" * 90)
    print()

    # Overall statistics
    print(f"Total examples: {len(results)}")
    print(f"Passed: {passed}/{len(results)}")
    print(f"Total time: {total_duration:.1f}s")

    # Count ratings
    ratings = {}
    for num, result in results:
        if result.success:
            rating, _ = rate_performance(num, result.metrics)
            ratings[rating] = ratings.get(rating, 0) + 1

    print()
    print("Performance distribution:")
    for rating in ["Excellent", "Good", "Fair", "Poor"]:
        count = ratings.get(rating, 0)
        if count > 0:
            bar = "#" * count
            print(f"  {rating:<10}: {count} {bar}")

    print()
    return passed == len(results)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Run all cynn examples and summarize results',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--ratio', type=float, default=1.0,
                        help='Training ratio (0.5 = half epochs, 1.0 = full, 2.0 = double)')
    parser.add_argument('--verbose', action='store_true',
                        help='Show full output from each example')
    parser.add_argument('--data-dir', type=str, default=None,
                        help='Directory containing test data files (iris.csv, sine_wave.csv, etc.)')
    return parser.parse_args()


def main():
    args = parse_args()
    success = run_all_examples(ratio=args.ratio, verbose=args.verbose, data_dir=args.data_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
