"""
Tests for context manager support in all network classes.

This module tests that all network types properly implement the context manager
protocol (__enter__/__exit__) and can be used with the 'with' statement.
"""

import pytest
from cynn.tinn import TinnNetwork
from cynn.genann import GenannNetwork
from cynn.fann import FannNetwork
from cynn.cnn import CNNNetwork


class TestTinnContextManager:
    """Test context manager protocol for TinnNetwork."""

    def test_with_statement(self):
        """Test TinnNetwork can be used with 'with' statement."""
        with TinnNetwork(2, 4, 1) as net:
            assert net is not None
            assert net.input_size == 2
            assert net.hidden_size == 4
            assert net.output_size == 1
            output = net.predict([0.5, 0.3])
            assert len(output) == 1

    def test_enter_returns_self(self):
        """Test __enter__ returns the network instance."""
        net = TinnNetwork(2, 4, 1)
        result = net.__enter__()
        assert result is net
        net.__exit__(None, None, None)

    def test_exit_returns_false(self):
        """Test __exit__ returns False to propagate exceptions."""
        net = TinnNetwork(2, 4, 1)
        net.__enter__()
        result = net.__exit__(None, None, None)
        assert result is False

    def test_exception_propagation(self):
        """Test exceptions inside 'with' block are propagated."""
        with pytest.raises(ValueError, match="test error"):
            with TinnNetwork(2, 4, 1) as _net:
                raise ValueError("test error")

    def test_network_usable_after_context(self):
        """Test network remains usable after exiting context."""
        with TinnNetwork(2, 4, 1) as net:
            net.predict([0.5, 0.3])

        # Network should still be usable
        output2 = net.predict([0.5, 0.3])
        assert len(output2) == 1

    def test_training_in_context(self):
        """Test training works inside context manager."""
        with TinnNetwork(2, 4, 1) as net:
            loss = net.train([0.0, 1.0], [1.0], rate=0.5)
            assert isinstance(loss, float)
            assert loss >= 0.0


class TestGenannContextManager:
    """Test context manager protocol for GenannNetwork."""

    def test_with_statement(self):
        """Test GenannNetwork can be used with 'with' statement."""
        with GenannNetwork(2, 1, 4, 1) as net:
            assert net is not None
            assert net.input_size == 2
            assert net.output_size == 1
            output = net.predict([0.5, 0.3])
            assert len(output) == 1

    def test_enter_returns_self(self):
        """Test __enter__ returns the network instance."""
        net = GenannNetwork(2, 1, 4, 1)
        result = net.__enter__()
        assert result is net
        net.__exit__(None, None, None)

    def test_exit_returns_false(self):
        """Test __exit__ returns False to propagate exceptions."""
        net = GenannNetwork(2, 1, 4, 1)
        net.__enter__()
        result = net.__exit__(None, None, None)
        assert result is False

    def test_exception_propagation(self):
        """Test exceptions inside 'with' block are propagated."""
        with pytest.raises(ValueError, match="test error"):
            with GenannNetwork(2, 1, 4, 1) as _net:
                raise ValueError("test error")

    def test_network_usable_after_context(self):
        """Test network remains usable after exiting context."""
        with GenannNetwork(2, 1, 4, 1) as net:
            net.predict([0.5, 0.3])

        # Network should still be usable
        output2 = net.predict([0.5, 0.3])
        assert len(output2) == 1

    def test_training_in_context(self):
        """Test training works inside context manager."""
        with GenannNetwork(2, 1, 4, 1) as net:
            loss = net.train([0.0, 1.0], [1.0], rate=0.5)
            assert isinstance(loss, float)
            assert loss >= 0.0


class TestFannContextManager:
    """Test context manager protocol for FannNetwork."""

    def test_with_statement(self):
        """Test FannNetwork can be used with 'with' statement."""
        with FannNetwork([2, 4, 1]) as net:
            assert net is not None
            assert net.input_size == 2
            assert net.output_size == 1
            output = net.predict([0.5, 0.3])
            assert len(output) == 1

    def test_enter_returns_self(self):
        """Test __enter__ returns the network instance."""
        net = FannNetwork([2, 4, 1])
        result = net.__enter__()
        assert result is net
        net.__exit__(None, None, None)

    def test_exit_returns_false(self):
        """Test __exit__ returns False to propagate exceptions."""
        net = FannNetwork([2, 4, 1])
        net.__enter__()
        result = net.__exit__(None, None, None)
        assert result is False

    def test_exception_propagation(self):
        """Test exceptions inside 'with' block are propagated."""
        with pytest.raises(ValueError, match="test error"):
            with FannNetwork([2, 4, 1]) as _net:
                raise ValueError("test error")

    def test_network_usable_after_context(self):
        """Test network remains usable after exiting context."""
        with FannNetwork([2, 4, 1]) as net:
            net.predict([0.5, 0.3])

        # Network should still be usable
        output2 = net.predict([0.5, 0.3])
        assert len(output2) == 1

    def test_training_in_context(self):
        """Test training works inside context manager."""
        with FannNetwork([2, 4, 1]) as net:
            loss = net.train([0.0, 1.0], [1.0])
            assert isinstance(loss, float)
            assert loss >= 0.0


class TestCNNContextManager:
    """Test context manager protocol for CNNNetwork."""

    def test_with_statement(self):
        """Test CNNNetwork can be used with 'with' statement."""
        with CNNNetwork() as net:
            assert net is not None
            net.create_input_layer(1, 4, 4)
            net.add_full_layer(2)
            output = net.predict([0.5] * 16)
            assert len(output) == 2

    def test_enter_returns_self(self):
        """Test __enter__ returns the network instance."""
        net = CNNNetwork()
        result = net.__enter__()
        assert result is net
        net.__exit__(None, None, None)

    def test_exit_returns_false(self):
        """Test __exit__ returns False to propagate exceptions."""
        net = CNNNetwork()
        net.__enter__()
        result = net.__exit__(None, None, None)
        assert result is False

    def test_exception_propagation(self):
        """Test exceptions inside 'with' block are propagated."""
        with pytest.raises(ValueError, match="test error"):
            with CNNNetwork() as _net:
                raise ValueError("test error")

    def test_network_usable_after_context(self):
        """Test network remains usable after exiting context."""
        with CNNNetwork() as net:
            net.create_input_layer(1, 4, 4)
            net.add_full_layer(2)
            net.predict([0.5] * 16)

        # Network should still be usable
        output2 = net.predict([0.5] * 16)
        assert len(output2) == 2

    def test_training_in_context(self):
        """Test training works inside context manager."""
        with CNNNetwork() as net:
            net.create_input_layer(1, 4, 4)
            net.add_full_layer(2)
            loss = net.train([0.5] * 16, [0.8, 0.2], learning_rate=0.01)
            assert isinstance(loss, float)
            assert loss >= 0.0


class TestMultipleNetworksInContext:
    """Test using multiple networks in nested or sequential contexts."""

    def test_nested_contexts_different_types(self):
        """Test nested context managers with different network types."""
        with TinnNetwork(2, 4, 1) as tinn:
            with GenannNetwork(2, 1, 4, 1) as genann:
                tinn_output = tinn.predict([0.5, 0.3])
                genann_output = genann.predict([0.5, 0.3])
                assert len(tinn_output) == 1
                assert len(genann_output) == 1

    def test_sequential_contexts_same_type(self):
        """Test sequential context managers with same network type."""
        with FannNetwork([2, 4, 1]) as net1:
            output1 = net1.predict([0.5, 0.3])

        with FannNetwork([2, 4, 1]) as net2:
            output2 = net2.predict([0.5, 0.3])

        assert len(output1) == 1
        assert len(output2) == 1

    def test_temporary_network_pattern(self):
        """Test using context manager for temporary network."""
        # Create and use network without storing reference
        with TinnNetwork(2, 4, 1) as net:
            result = net.train([0.5, 0.3], [0.8], rate=0.5)
            assert result >= 0.0
        # Network can be garbage collected after exiting context
