from pathlib import Path
from cynn.fann import FannNetwork


class TestSaveLoad:
    """Test save/load functionality."""

    def test_save_creates_file(self, tmp_path):
        """Test that save creates a file."""
        net = FannNetwork([2, 3, 1])
        path = tmp_path / "test_model.fann"
        net.save(str(path))
        assert path.exists()

    def test_load_restores_network(self, tmp_path):
        """Test that load restores network structure."""
        net = FannNetwork([2, 3, 1])
        path = tmp_path / "test_model.fann"

        # Train the network
        for _ in range(10):
            net.train([0.5, 0.3], [0.8])

        # Save it
        net.save(str(path))

        # Load it
        loaded_net = FannNetwork.load(str(path))
        assert loaded_net.layers == net.layers

        # Predictions should match
        inputs = [0.5, 0.3]
        original_pred = net.predict(inputs)
        loaded_pred = loaded_net.predict(inputs)
        assert original_pred == loaded_pred

    def test_load_preserves_shape(self, tmp_path):
        """Test that loaded network has correct shape."""
        net = FannNetwork([3, 4, 5, 2])
        path = tmp_path / "test_model.fann"

        net.save(str(path))
        loaded_net = FannNetwork.load(str(path))

        assert loaded_net.input_size == 3
        assert loaded_net.output_size == 2
        assert loaded_net.num_layers == 4
        assert loaded_net.layers == [3, 4, 5, 2]

    def test_save_with_string_path(self, tmp_path):
        """Test save with string path."""
        net = FannNetwork([2, 3, 1])
        path = str(tmp_path / "test_model.fann")
        net.save(path)
        assert Path(path).exists()

    def test_save_with_bytes_path(self, tmp_path):
        """Test save with bytes path."""
        net = FannNetwork([2, 3, 1])
        path = bytes(str(tmp_path / "test_model.fann"), 'utf-8')
        net.save(path)
        assert (tmp_path / "test_model.fann").exists()

    def test_save_with_pathlike(self, tmp_path):
        """Test save with PathLike object."""
        net = FannNetwork([2, 3, 1])
        path = tmp_path / "test_model.fann"
        net.save(path)
        assert path.exists()

    def test_load_with_string_path(self, tmp_path):
        """Test load with string path."""
        net = FannNetwork([2, 3, 1])
        path = str(tmp_path / "test_model.fann")
        net.save(path)
        loaded_net = FannNetwork.load(path)
        assert loaded_net.layers == net.layers

    def test_load_with_pathlike(self, tmp_path):
        """Test load with PathLike object."""
        net = FannNetwork([2, 3, 1])
        path = tmp_path / "test_model.fann"
        net.save(path)
        loaded_net = FannNetwork.load(path)
        assert loaded_net.layers == net.layers

    def test_multiple_save_load_cycles(self, tmp_path):
        """Test multiple save/load cycles preserve network."""
        net = FannNetwork([2, 3, 1])
        inputs = [0.5, 0.3]

        # Train original network
        for _ in range(10):
            net.train(inputs, [0.8])

        original_pred = net.predict(inputs)

        # Save/load cycle 1
        path1 = tmp_path / "model1.fann"
        net.save(path1)
        net1 = FannNetwork.load(path1)

        # Save/load cycle 2
        path2 = tmp_path / "model2.fann"
        net1.save(path2)
        net2 = FannNetwork.load(path2)

        # All predictions should match
        assert net1.predict(inputs) == original_pred
        assert net2.predict(inputs) == original_pred

    def test_loaded_network_can_train(self, tmp_path):
        """Test that loaded network can be trained."""
        net = FannNetwork([2, 3, 1])
        path = tmp_path / "test_model.fann"

        # Save initial network
        net.save(path)

        # Load it
        loaded_net = FannNetwork.load(path)

        # Train the loaded network
        inputs = [0.5, 0.3]
        pred_before = loaded_net.predict(inputs)

        for _ in range(20):
            loaded_net.train(inputs, [0.9])

        pred_after = loaded_net.predict(inputs)

        # Training should change predictions
        assert pred_before != pred_after

    def test_save_sparse_network(self, tmp_path):
        """Test saving and loading sparse networks."""
        net = FannNetwork([2, 8, 1], connection_rate=0.5)
        path = tmp_path / "sparse_model.fann"

        # Train the sparse network
        for _ in range(10):
            net.train([0.5, 0.3], [0.8])

        # Save it
        net.save(path)

        # Load it
        loaded_net = FannNetwork.load(path)
        assert loaded_net.layers == net.layers

        # Predictions should match
        inputs = [0.5, 0.3]
        original_pred = net.predict(inputs)
        loaded_pred = loaded_net.predict(inputs)
        assert original_pred == loaded_pred
