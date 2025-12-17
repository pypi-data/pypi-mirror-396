import pytest
import os
from cynn.tinn import TinnNetwork


class TestSaveLoad:
    """Test save and load functionality like test.c."""

    def test_save_creates_file(self, simple_network, temp_model_path):
        """Test that save creates a file."""
        simple_network.save(temp_model_path)
        assert temp_model_path.exists()
        assert temp_model_path.stat().st_size > 0

    def test_load_restores_network(self, simple_network, temp_model_path):
        """Test that load restores network state."""
        # Train the network a bit
        inputs = [0.5, 0.3]
        targets = [0.8]
        for _ in range(10):
            simple_network.train(inputs, targets, 0.5)

        # Get prediction before save
        pred_before = simple_network.predict(inputs)

        # Save the network
        simple_network.save(temp_model_path)

        # Load into new network
        loaded_network = TinnNetwork.load(temp_model_path)

        # Prediction should be identical
        pred_after = loaded_network.predict(inputs)

        assert len(pred_before) == len(pred_after)
        assert pred_before[0] == pytest.approx(pred_after[0], abs=1e-6)

    def test_load_preserves_shape(self, simple_network, temp_model_path):
        """Test that loaded network has same shape."""
        original_shape = simple_network.shape

        simple_network.save(temp_model_path)
        loaded_network = TinnNetwork.load(temp_model_path)

        assert loaded_network.shape == original_shape
        assert loaded_network.input_size == simple_network.input_size
        assert loaded_network.hidden_size == simple_network.hidden_size
        assert loaded_network.output_size == simple_network.output_size

    def test_save_load_cycle_like_test_c(self, xor_network, xor_data, temp_model_path):
        """Test save/load cycle similar to test.c workflow."""
        # Train the network (like test.c does)
        rate = 1.0
        anneal = 0.99
        iterations = 50

        for _ in range(iterations):
            for inputs, targets in xor_data:
                xor_network.train(inputs, targets, rate)
            rate *= anneal

        # Save (like test.c: xtsave(tinn, "saved.tinn"))
        xor_network.save(temp_model_path)

        # Load from disk (like test.c: xtload("saved.tinn"))
        loaded = TinnNetwork.load(temp_model_path)

        # Make predictions with loaded network (like test.c does)
        test_inputs = xor_data[0][0]

        pred_original = xor_network.predict(test_inputs)
        pred_loaded = loaded.predict(test_inputs)

        # Predictions should be identical
        assert pred_original[0] == pytest.approx(pred_loaded[0], abs=1e-6)

    def test_save_with_string_path(self, simple_network, tmp_path):
        """Test save with string path."""
        path_str = str(tmp_path / "model_str.tinn")
        simple_network.save(path_str)
        assert os.path.exists(path_str)

    def test_save_with_bytes_path(self, simple_network, tmp_path):
        """Test save with bytes path."""
        path_bytes = bytes(tmp_path / "model_bytes.tinn")
        simple_network.save(path_bytes)
        assert os.path.exists(path_bytes)

    def test_save_with_pathlike(self, simple_network, tmp_path):
        """Test save with Path object."""
        path_obj = tmp_path / "model_path.tinn"
        simple_network.save(path_obj)
        assert path_obj.exists()

    def test_load_with_string_path(self, simple_network, tmp_path):
        """Test load with string path."""
        path_str = str(tmp_path / "model_str.tinn")
        simple_network.save(path_str)
        loaded = TinnNetwork.load(path_str)
        assert loaded.shape == simple_network.shape

    def test_load_with_pathlike(self, simple_network, tmp_path):
        """Test load with Path object."""
        path_obj = tmp_path / "model_path.tinn"
        simple_network.save(path_obj)
        loaded = TinnNetwork.load(path_obj)
        assert loaded.shape == simple_network.shape

    def test_save_invalid_path_type(self, simple_network):
        """Test that invalid path types raise TypeError."""
        with pytest.raises(TypeError, match="path must be"):
            simple_network.save(123)
        with pytest.raises(TypeError, match="path must be"):
            simple_network.save(["/tmp/model.tinn"])

    def test_multiple_save_load_cycles(self, simple_network, tmp_path):
        """Test multiple save/load cycles preserve state."""
        inputs = [0.5, 0.3]

        # Original prediction
        pred1 = simple_network.predict(inputs)

        # First save/load cycle
        path1 = tmp_path / "model1.tinn"
        simple_network.save(path1)
        net1 = TinnNetwork.load(path1)
        pred2 = net1.predict(inputs)

        # Second save/load cycle
        path2 = tmp_path / "model2.tinn"
        net1.save(path2)
        net2 = TinnNetwork.load(path2)
        pred3 = net2.predict(inputs)

        # All predictions should be identical
        assert pred1[0] == pytest.approx(pred2[0], abs=1e-6)
        assert pred2[0] == pytest.approx(pred3[0], abs=1e-6)

    def test_loaded_network_can_train(self, simple_network, temp_model_path):
        """Test that loaded network can continue training."""
        inputs = [0.5, 0.3]
        targets = [0.8]

        # Save initial network
        simple_network.save(temp_model_path)

        # Load and train
        loaded = TinnNetwork.load(temp_model_path)
        pred_before = loaded.predict(inputs)

        for _ in range(20):
            loaded.train(inputs, targets, 0.5)

        pred_after = loaded.predict(inputs)

        # Training should change predictions
        assert pred_before[0] != pred_after[0]
