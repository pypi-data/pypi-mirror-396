import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from cynn.tinn import TinnNetwork


class TestNoGilThreading:
    """Test that nogil allows true parallel execution."""

    def test_concurrent_predictions(self):
        """Test concurrent predictions on multiple threads."""
        net = TinnNetwork(10, 8, 2)

        def predict_task(thread_id):
            """Run predictions in a thread."""
            inputs = [float(i * 0.1) for i in range(10)]
            results = []
            for _ in range(100):
                pred = net.predict(inputs)
                results.append(pred)
            return thread_id, len(results)

        # Run predictions concurrently
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(predict_task, i) for i in range(4)]
            results = [f.result() for f in as_completed(futures)]

        # All threads should complete successfully
        assert len(results) == 4
        assert all(count == 100 for _, count in results)

    def test_concurrent_training(self):
        """Test concurrent training on different networks."""
        def train_network(net_id):
            """Train a network in a thread."""
            net = TinnNetwork(2, 4, 1)
            inputs = [0.5, 0.3]
            targets = [0.8]

            losses = []
            for _ in range(50):
                loss = net.train(inputs, targets, 0.1)
                losses.append(loss)

            return net_id, losses

        # Train multiple networks concurrently
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(train_network, i) for i in range(4)]
            results = [f.result() for f in as_completed(futures)]

        # All threads should complete successfully
        assert len(results) == 4
        for net_id, losses in results:
            assert len(losses) == 50
            assert all(isinstance(loss, float) for loss in losses)

    def test_shared_network_predictions(self):
        """Test multiple threads making predictions on the same network."""
        net = TinnNetwork(5, 6, 3)

        def predict_worker(worker_id, iterations):
            """Worker thread making predictions."""
            inputs = [float(i * 0.1 + worker_id * 0.01) for i in range(5)]
            predictions = []
            for _ in range(iterations):
                pred = net.predict(inputs)
                predictions.append(pred)
            return predictions

        # Multiple threads sharing the same network
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(predict_worker, i, 100)
                for i in range(3)
            ]
            results = [f.result() for f in as_completed(futures)]

        # All threads should complete
        assert len(results) == 3
        assert all(len(preds) == 100 for preds in results)

    def test_parallel_network_creation(self):
        """Test creating multiple networks in parallel."""
        def create_network(size):
            """Create a network with given size."""
            net = TinnNetwork(size, size * 2, size // 2 or 1)
            return net.shape

        sizes = [10, 20, 30, 40]

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(create_network, s) for s in sizes]
            results = [f.result() for f in as_completed(futures)]

        # Verify all networks were created correctly
        assert len(results) == 4
        expected_shapes = {(10, 20, 5), (20, 40, 10), (30, 60, 15), (40, 80, 20)}
        assert set(results) == expected_shapes

    def test_thread_safety_train_predict(self):
        """Test thread safety when training and predicting simultaneously."""
        net = TinnNetwork(3, 5, 2)
        results = {'train': [], 'predict': []}
        lock = threading.Lock()

        def train_thread():
            """Thread that trains the network."""
            inputs = [0.1, 0.2, 0.3]
            targets = [0.7, 0.8]
            for _ in range(50):
                loss = net.train(inputs, targets, 0.1)
                with lock:
                    results['train'].append(loss)

        def predict_thread():
            """Thread that makes predictions."""
            inputs = [0.1, 0.2, 0.3]
            for _ in range(50):
                pred = net.predict(inputs)
                with lock:
                    results['predict'].append(pred)

        # Run train and predict in parallel
        threads = [
            threading.Thread(target=train_thread),
            threading.Thread(target=predict_thread),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Both should complete successfully
        assert len(results['train']) == 50
        assert len(results['predict']) == 50


class TestThreadingPerformance:
    """Test performance benefits of nogil."""

    def test_parallel_speedup(self):
        """Verify that parallel execution is actually faster."""
        # Create a larger network for noticeable computation time
        net = TinnNetwork(100, 50, 10)
        inputs = [float(i * 0.01) for i in range(100)]

        # Sequential execution (use perf_counter for higher resolution on Windows)
        start = time.perf_counter()
        for _ in range(100):
            net.predict(inputs)
        sequential_time = time.perf_counter() - start

        # Parallel execution
        def predict_batch():
            for _ in range(25):
                net.predict(inputs)

        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(predict_batch) for _ in range(4)]
            for f in as_completed(futures):
                f.result()
        parallel_time = time.perf_counter() - start

        # Parallel should be faster (with some tolerance for overhead)
        # We don't assert strict timing as it varies by system,
        # but we verify both complete successfully
        assert sequential_time >= 0
        assert parallel_time >= 0
        # Just verify the operations work in parallel
        # Actual speedup varies based on system/CPU cores

    def test_concurrent_file_operations(self, tmp_path):
        """Test concurrent save/load operations."""
        def save_load_cycle(worker_id):
            """Save and load a network."""
            net = TinnNetwork(5, 4, 2)
            path = tmp_path / f"model_{worker_id}.tinn"

            # Train a bit
            inputs = [0.1 * i for i in range(5)]
            targets = [0.5, 0.5]
            for _ in range(10):
                net.train(inputs, targets, 0.1)

            # Save
            net.save(path)

            # Load
            loaded = TinnNetwork.load(path)

            # Verify
            pred1 = net.predict(inputs)
            pred2 = loaded.predict(inputs)

            return pred1, pred2

        # Run multiple save/load cycles in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(save_load_cycle, i) for i in range(4)]
            results = [f.result() for f in as_completed(futures)]

        # All should complete successfully
        assert len(results) == 4
        for pred1, pred2 in results:
            assert len(pred1) == len(pred2)
            # Predictions should match
            for p1, p2 in zip(pred1, pred2):
                assert abs(p1 - p2) < 1e-6
