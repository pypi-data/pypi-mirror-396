# ONNX Export Implementation Plan

## Overview

This document outlines a possible plan to add ONNX export functionality to all six cynn network types: TinnNetwork, GenannNetwork, FannNetwork, FannNetworkDouble, CNNNetwork, and KannNeuralNetwork.

## Current State Analysis

### Available Introspection (as of current codebase)

**TinnNetwork** (`tinn.pxd`):

- Direct C struct access to `w` (all weights), `x` (hidden-to-output), `b` (biases)
- Shape info: `nips`, `nhid`, `nops` (inputs, hidden, outputs)
- Fixed architecture: input → hidden → output (3 layers)
- Activation: Hardcoded (likely sigmoid, needs verification)

**GenannNetwork** (`genann.pxd`):

- Direct access to `weight` array (size: `total_weights`)
- Architecture: `inputs`, `hidden_layers`, `hidden`, `outputs`
- Activation functions: `activation_hidden`, `activation_output` (function pointers)
- **Challenge**: Activation functions are C function pointers, not enums

**FannNetwork/FannNetworkDouble** (`ffann.pxd`, `dfann.pxd`):

- Internal `weights` pointer exists but not exposed
- Layer structure via `fann_get_layer_array()`
- Already exposes: `num_input`, `num_output`, `total_neurons`, `total_connections`
- **Missing**: Activation function query API, per-layer weight extraction

**CNNNetwork** (`cnn.pxd`):

- Rich layer structure via `Layer*` linked list
- Per-layer access to: `weights`, `biases`, `outputs`, `gradients`
- Layer types: `LAYER_INPUT`, `LAYER_FULL`, `LAYER_CONV`
- Conv params: `kernsize`, `padding`, `stride`
- **Challenge**: Activation function appears hardcoded (needs investigation)

**KannNeuralNetwork** (`kann.pxd`):

- Computational graph architecture via `kann_t` struct containing `kad_node_t**` array
- Direct access to collated weights (`kann_t.x`), gradients (`kann_t.g`), and constants (`kann_t.c`)
- Node-level introspection: dimensions (`d[4]`), operator ID (`op`), flags, values (`x`), gradients (`g`)
- Operator names available via `kad_op_name[]` array
- Supports: MLP, LSTM, GRU, RNN, Conv1D, Conv2D, Dropout, LayerNorm
- Cost types: `KANN_C_CEB` (binary cross-entropy), `KANN_C_CEM` (multi-class), `KANN_C_MSE` (MSE)
- Activations: sigmoid (`kad_sigm`), tanh (`kad_tanh`), relu (`kad_relu`), softmax (`kad_softmax`)
- **Challenge**: Graph-based architecture is more complex than layer-sequential models
- **Challenge**: RNN/LSTM/GRU require unrolling for ONNX (stateful ops need special handling)

## Implementation Plan

### Phase 1: Weight Extraction API

Add methods to expose weights and biases as NumPy arrays for each network type.

#### 1.1 TinnNetwork Weight Extraction

Add to `_core.pyx`:

```python
def get_weights(self) -> dict[str, np.ndarray]:
    """Extract all weights and biases as NumPy arrays.

    Returns:
        dict with keys:
        - 'input_to_hidden': shape (nips, nhid)
        - 'hidden_to_output': shape (nhid, nops)
        - 'hidden_bias': shape (nhid,)
        - 'output_bias': shape (nops,)
    """
```

**Implementation**:

- Allocate NumPy arrays and memcpy from `self._net.w`, `self._net.x`, `self._net.b`
- Tinn stores weights in flat arrays; need to determine layout (row-major vs column-major)
- Examine `thirdparty/tinn/Tinn.c` to understand weight indexing

#### 1.2 GenannNetwork Weight Extraction

Add to `_core.pyx`:

```python
def get_weights(self) -> dict[str, np.ndarray]:
    """Extract weights layer by layer.

    Returns:
        dict with keys for each layer:
        - 'layer_0_weights': shape depends on architecture
        - 'layer_0_bias': shape (hidden,)
        - ... (for each hidden layer)
        - 'output_weights': shape (hidden, outputs)
        - 'output_bias': shape (outputs,)
    """
```

**Challenge**: GENANN stores all weights in a single `double* weight` array. Need to:

1. Parse weight array based on architecture (inputs, hidden_layers, hidden, outputs)
2. Calculate offset for each layer's weights and biases
3. Examine `thirdparty/genann/genann.c:genann_init()` to understand layout

#### 1.3 FannNetwork Weight Extraction

**Problem**: FANN's internal `weights` pointer is private. No public API for direct weight access.

**Solution Options**:

1. Add custom C wrapper functions in `thirdparty/fann/` to extract connection weights
2. Parse FANN's text save format (already implemented via `fann_save()`)
3. Use FANN's connection iteration API if available

**Recommended**: Option 2 (parse save format) - least invasive

- Save to temp file, parse to extract weights
- FANN save format is documented and stable

#### 1.4 CNNNetwork Weight Extraction

Add to `_core.pyx`:

```python
def get_weights(self) -> list[dict[str, np.ndarray]]:
    """Extract weights layer by layer.

    Returns:
        List of dicts, one per layer:
        [
            {'type': 'input', 'shape': (d, w, h)},
            {'type': 'conv', 'weights': ndarray, 'biases': ndarray,
             'kernel_size': k, 'stride': s, 'padding': p},
            {'type': 'full', 'weights': ndarray, 'biases': ndarray},
        ]
    """
```

**Implementation**:

- Walk `Layer*` linked list from `_input_layer` to `_output_layer`
- For each layer, copy `weights`, `biases` arrays (sizes: `nweights`, `nbiases`)
- Include metadata: `ltype`, `depth`, `width`, `height`, `conv` params

#### 1.5 KannNeuralNetwork Weight Extraction

Add to `kann.pyx`:

```python
def get_weights(self) -> dict[str, np.ndarray]:
    """Extract weights from the computational graph.

    Returns:
        dict with keys:
        - 'variables': All trainable variables as flat array, shape (n_var,)
        - 'constants': All constants as flat array, shape (n_const,)
        - 'nodes': List of node metadata dicts with:
            - 'op': operator name
            - 'dims': dimension tuple
            - 'flags': node flags
            - 'values': node values if applicable
    """
```

**Implementation**:

- Access `kann_t.x` for collated variable values (size: `n_var`)
- Access `kann_t.c` for collated constant values (size: `n_const`)
- Iterate over `kann_t.v[0..n]` nodes to extract per-node metadata
- Use `kad_op_name[node.op]` to get human-readable operator names
- For each node with `KAD_VAR` flag, extract weights from `node.x`

**Challenge**: KANN stores weights in a flattened format across the graph. Need to:

1. Map node indices to layer semantics (which nodes are dense layers vs activations)
2. Reconstruct weight matrices from flat `x` array using node dimensions
3. Handle different architectures (MLP vs LSTM vs Conv) differently

### Phase 2: Activation Function Introspection

#### 2.1 Investigate Hardcoded Activations

**TinnNetwork**:

- Examine `thirdparty/tinn/Tinn.c` to identify activation (likely tanh or sigmoid)
- Hardcode ONNX mapping in exporter

**GenannNetwork**:

- C struct has `activation_hidden` and `activation_output` function pointers
- Default: `genann_act_sigmoid_cached`
- **Problem**: Cannot introspect function pointer identity from Python
- **Solutions**:
  - Add enum field to genann struct (requires modifying vendored code)
  - Assume default sigmoid (safest for now)
  - Add optional activation parameter to constructor and track in Python wrapper

**CNNNetwork**:

- Examine `thirdparty/nn1/cnn.c` to identify activation
- Likely ReLU for conv layers, softmax for output
- Hardcode ONNX mapping

**FannNetwork**:

- FANN supports multiple activations per layer: LINEAR, SIGMOID, SIGMOID_STEPWISE, SIGMOID_SYMMETRIC, GAUSSIAN, GAUSSIAN_SYMMETRIC, ELLIOT, ELLIOT_SYMMETRIC, LINEAR_PIECE, THRESHOLD, THRESHOLD_SYMMETRIC, SIN_SYMMETRIC, COS_SYMMETRIC
- Missing from `ffann.pxd`: `fann_get_activation_function(fann*, layer, neuron)`
- **Action**: Add activation query functions to `ffann.pxd` and `dfann.pxd`

**KannNeuralNetwork**:

- Activations are explicit nodes in the computational graph with specific operator IDs
- Operator ID maps to `kad_op_name[]`: "sigm", "tanh", "relu", "softmax", etc.
- **Advantage**: Activations are fully introspectable by walking the graph
- Can determine exact activation per layer by examining node connectivity
- RNN gates (LSTM/GRU) use specific internal activations (sigmoid for gates, tanh for state)

#### 2.2 Add FANN Activation Queries

Update `ffann.pxd` and `dfann.pxd`:

```cython
# Add enum
ctypedef enum fann_activationfunc_enum:
    FANN_LINEAR = 0
    FANN_THRESHOLD = 1
    FANN_SIGMOID = 2
    FANN_SIGMOID_STEPWISE = 3
    # ... (complete enum from fann.h)

# Add query functions
cdef fann_activationfunc_enum fann_get_activation_function(
    fann* ann, int layer, int neuron) nogil
```

### Phase 3: ONNX Graph Construction

Create `src/cynn/onnx_export.py` with exporter classes for each network type.

#### 3.1 Architecture

```python
from abc import ABC, abstractmethod
import onnx
from onnx import helper, TensorProto
import numpy as np

class ONNXExporter(ABC):
    """Base class for ONNX export."""

    @abstractmethod
    def build_graph(self, network) -> onnx.ModelProto:
        """Build ONNX graph from network."""
        pass

    def export(self, network, path: str, opset: int = 14):
        """Export network to ONNX file."""
        model = self.build_graph(network)
        onnx.checker.check_model(model)
        onnx.save(model, path)

class TinnONNXExporter(ONNXExporter):
    """Export TinnNetwork to ONNX."""

    def build_graph(self, network: TinnNetwork) -> onnx.ModelProto:
        # 1. Extract weights via network.get_weights()
        # 2. Create input node
        # 3. Create Gemm (MatMul + Add) for input->hidden
        # 4. Create activation (Sigmoid/Tanh)
        # 5. Create Gemm for hidden->output
        # 6. Create output activation
        # 7. Assemble graph with initializers
        pass

class GenannONNXExporter(ONNXExporter):
    """Export GenannNetwork to ONNX."""
    # Similar but iterate over hidden_layers

class FannONNXExporter(ONNXExporter):
    """Export FannNetwork to ONNX."""
    # Parse saved FANN file or use new weight extraction
    # Query activations per layer

class CNNONNXExporter(ONNXExporter):
    """Export CNNNetwork to ONNX."""

    def build_graph(self, network: CNNNetwork) -> onnx.ModelProto:
        # Iterate over network.layers
        # Map LAYER_CONV -> Conv op with extracted weights
        # Map LAYER_FULL -> Gemm op
        # Include kernel_size, stride, padding attributes
        pass

class KannONNXExporter(ONNXExporter):
    """Export KannNeuralNetwork to ONNX."""

    def build_graph(self, network: KannNeuralNetwork) -> onnx.ModelProto:
        # 1. Extract graph structure via network.get_weights()
        # 2. Walk computational graph nodes
        # 3. Map kad operators to ONNX operators:
        #    - kad_matmul -> MatMul
        #    - kad_add -> Add
        #    - kad_sigm -> Sigmoid
        #    - kad_tanh -> Tanh
        #    - kad_relu -> Relu
        #    - kad_softmax -> Softmax
        #    - kad_conv1d/conv2d -> Conv
        #    - kad_dropout -> Dropout (or Identity in inference)
        # 4. Handle RNN/LSTM/GRU specially (see Challenge 6)
        # 5. Create initializers from weight nodes
        pass
```

#### 3.2 ONNX Operator Mapping

| cynn Component | ONNX Operator | Notes |
|----------------|---------------|-------|
| Fully-connected layer | `Gemm` or `MatMul + Add` | Gemm = General Matrix Multiplication |
| Sigmoid activation | `Sigmoid` | Direct mapping |
| Tanh activation | `Tanh` | Direct mapping |
| ReLU activation | `Relu` | Direct mapping |
| Conv layer | `Conv` | Include kernel_size, strides, pads |
| Softmax | `Softmax` | axis=-1 for last dimension |
| LSTM layer | `LSTM` | Requires weight restructuring (see Challenge 6) |
| GRU layer | `GRU` | Requires weight restructuring |
| Simple RNN | `RNN` | Basic recurrent unit |
| Dropout | `Dropout` | Or `Identity` in inference mode |
| LayerNorm | `LayerNormalization` | ONNX opset >= 17 |
| Add (element-wise) | `Add` | Direct mapping |
| Mul (element-wise) | `Mul` | Direct mapping |
| MatMul | `MatMul` | Direct mapping |

#### 3.3 Numerical Precision

**Challenge**: ONNX defaults to float32, but GenannNetwork, FannNetworkDouble, and CNNNetwork use float64.

**Solution**:

- Support both float32 and float64 ONNX models
- Add `dtype` parameter to export: `network.to_onnx(path, dtype='float32')`
- Convert weights during export if needed

### Phase 4: Public API Integration

Add `to_onnx()` method to each network class in `_core.pyx`:

```python
def to_onnx(self, path: str | bytes | os.PathLike,
            opset: int = 14,
            dtype: str = 'float32') -> None:
    """Export network to ONNX format.

    Args:
        path: Output file path
        opset: ONNX opset version (default: 14)
        dtype: 'float32' or 'float64' (auto-detects based on network type)

    Raises:
        ImportError: If onnx package not installed
        ValueError: If network structure cannot be exported
    """
    try:
        from .onnx_export import TinnONNXExporter  # (or appropriate exporter)
    except ImportError:
        raise ImportError(
            "ONNX export requires 'onnx' package. "
            "Install with: pip install cynn[onnx]"
        )

    exporter = TinnONNXExporter()
    exporter.export(self, path, opset=opset)
```

Update `__init__.py` to conditionally import onnx_export (don't fail if onnx not installed).

### Phase 5: Testing & Validation

Create `tests/test_onnx_export.py`:

```python
import pytest
import numpy as np

# Skip all tests if onnx not installed
onnxruntime = pytest.importorskip("onnxruntime")
onnx = pytest.importorskip("onnx")

def test_tinn_onnx_export_numerical_equivalence(tmp_path):
    """Verify TinnNetwork ONNX export matches native inference."""
    from cynn.tinn import TinnNetwork

    # Create and train network
    net = TinnNetwork(2, 4, 1)
    inputs = np.array([[0.5, 0.3]], dtype=np.float32)

    # Get native prediction
    native_output = net.predict(inputs[0])

    # Export to ONNX
    onnx_path = tmp_path / "test.onnx"
    net.to_onnx(onnx_path)

    # Load and run with ONNX Runtime
    sess = onnxruntime.InferenceSession(str(onnx_path))
    onnx_output = sess.run(None, {'input': inputs})[0]

    # Compare outputs
    np.testing.assert_allclose(native_output, onnx_output[0], rtol=1e-5)

# Similar tests for each network type
def test_genann_onnx_export(tmp_path): ...
def test_fann_onnx_export(tmp_path): ...
def test_fann_double_onnx_export(tmp_path): ...
def test_cnn_onnx_export(tmp_path): ...
def test_kann_mlp_onnx_export(tmp_path): ...
def test_kann_lstm_onnx_export(tmp_path): ...

def test_onnx_model_validation(tmp_path):
    """Verify exported ONNX model passes onnx.checker."""
    from cynn.tinn import TinnNetwork
    net = TinnNetwork(2, 4, 1)
    onnx_path = tmp_path / "test.onnx"
    net.to_onnx(onnx_path)

    model = onnx.load(str(onnx_path))
    onnx.checker.check_model(model)  # Should not raise
```

Additional test coverage:

- Different network sizes
- Networks with different activation functions (FANN)
- Multi-layer networks (Genann, FANN)
- CNN with various architectures
- Edge cases (single neuron, very deep networks)

### Phase 6: Dependencies & Packaging

#### 6.1 Update `pyproject.toml`

```toml
[project.optional-dependencies]
onnx = [
    "onnx>=1.15.0",
    "onnxruntime>=1.16.0",
    "numpy>=1.26.0",  # Already in dev dependencies
]

[dependency-groups]
dev = [
    "pytest>=8.4.2",
    "numpy>=1.26.0",
]
```

#### 6.2 Installation

```bash
# Base install (no ONNX)
pip install cynn

# With ONNX support
pip install cynn[onnx]

# Development with ONNX
uv sync --extra onnx
```

#### 6.3 Update Documentation

- Add ONNX export section to README.md
- Document opset compatibility
- Provide examples for each network type
- Document dtype handling and precision considerations

## Implementation Challenges & Solutions

### Challenge 1: Weight Layout Ambiguity

**Problem**: C libraries may use different weight storage layouts (row-major vs column-major, different layer orderings).

**Solution**:

1. Write unit tests that verify weight values by inspecting individual neuron connections
2. Cross-reference with C library source code documentation
3. Create "golden" test cases with known weight values

### Challenge 2: Activation Function Introspection

**Problem**: Some libraries use function pointers (GENANN) or don't expose activation queries (Tinn, CNN).

**Solutions**:

- **Short-term**: Hardcode default activations, document assumptions
- **Medium-term**: Add activation tracking to Python wrappers
- **Long-term**: Modify vendored C code to add activation enums (requires maintaining patches)

### Challenge 3: FANN Weight Extraction

**Problem**: No direct API for weight extraction.

**Solution**: Parse FANN's text save format

```python
def _parse_fann_file(path: str) -> dict:
    """Parse FANN text format to extract weights."""
    # Parse layer structure, connection weights, activations
    # FANN format is documented and stable
```

### Challenge 4: CNNNetwork Activation Functions

**Problem**: CNN library may use different activations for conv layers (ReLU?) vs output (softmax?).

**Solution**:

1. Examine `thirdparty/nn1/cnn.c` to determine exact activations
2. Add layer-specific activation mapping in `CNNONNXExporter`
3. If activations vary by layer, add activation metadata to `CNNLayer` class

### Challenge 5: Sparse Networks (FANN)

**Problem**: FANN supports sparse networks (connection_rate < 1.0), but ONNX's Gemm assumes full connectivity.

**Solution**: Export sparse networks as `MatMul` with explicitly zeroed weights, or use ONNX Sparse Tensor representation (opset >= 11).

### Challenge 6: KANN RNN/LSTM/GRU Export

**Problem**: KANN's RNN implementation uses a computational graph that differs from ONNX's RNN operators.

- KANN stores LSTM weights as separate matrices for each gate (input, forget, cell, output)
- ONNX `LSTM` operator expects concatenated weight matrices in specific order: [Wi, Wo, Wf, Wc]
- KANN uses internal unrolling for training; ONNX handles sequence dimension differently
- Hidden state initialization differs between frameworks

**Solution**:

1. **MLP-only export (simpler)**: Only export feedforward networks initially, skip RNN support
2. **Full RNN export (complex)**:
   - Detect RNN nodes by operator type (lstm, gru, rnn)
   - Extract and restructure weight matrices to ONNX format
   - Map KANN's gate order to ONNX's expected order
   - Handle sequence length and batch dimensions
   - Export unrolled graph for fixed-length sequences, or use ONNX Loop for variable length

**Recommendation**: Start with MLP-only export. RNN export adds significant complexity for limited benefit (users needing RNN deployment should use PyTorch/TensorFlow).

### Challenge 7: KANN Graph Topology

**Problem**: KANN uses a general computational graph, not a sequential layer model.

- Nodes can have arbitrary connectivity (skip connections, residual paths)
- Graph may include nodes not relevant to inference (cost nodes, truth labels)
- Need to identify which nodes are inputs, outputs, and intermediate computations

**Solution**:

1. Filter nodes by `ext_flag`: `KANN_F_IN` for inputs, `KANN_F_OUT` for outputs
2. Perform topological sort to determine evaluation order
3. Only include nodes reachable from inputs that lead to outputs
4. Skip cost nodes (`KANN_F_COST`) and truth nodes (`KANN_F_TRUTH`)

## Phased Rollout

### Milestone 1: TinnNetwork Only (Simplest)

- [ ] Fixed 3-layer architecture
- [ ] Minimal weight extraction
- [ ] Single activation type
- [ ] Float32 only
- **Target**: 2-3 days

### Milestone 2: GenannNetwork (Multi-layer)

- [ ] Variable depth support
- [ ] Multi-layer weight parsing
- [ ] Float64 support
- **Target**: 3-4 days

### Milestone 3: FannNetwork (Complex)

- [ ] FANN file parsing
- [ ] Activation function queries
- [ ] Sparse network handling
- [ ] Both float32 and float64 variants
- **Target**: 5-6 days

### Milestone 4: CNNNetwork

- [ ] Convolutional layer mapping
- [ ] Conv parameter extraction
- [ ] Multi-layer iteration
- [ ] Activation determination
- **Target**: 4-5 days

### Milestone 5: KannNeuralNetwork MLP (Most Complex)

- [ ] Graph traversal and topology sorting
- [ ] Node filtering (inputs, outputs, skip cost/truth nodes)
- [ ] Operator mapping (dense, activations)
- [ ] Weight extraction from collated arrays
- [ ] Float32 only
- **Target**: 5-7 days

### Milestone 6: KannNeuralNetwork RNN (Optional)

- [ ] LSTM weight restructuring
- [ ] GRU weight restructuring
- [ ] Sequence dimension handling
- [ ] Hidden state initialization
- **Target**: 7-10 days (consider skipping - see "Is it worth doing?")

### Milestone 7: Polish & Documentation

- [ ] Comprehensive tests for all types
- [ ] README examples
- [ ] Error handling and validation
- [ ] Performance optimization
- **Target**: 2-3 days

**Total Estimated Effort**: 25-38 days (5-8 weeks) including KANN, or 16-21 days (3-4 weeks) excluding KANN RNN

## Success Criteria

1. All six network types can export to valid ONNX format (KANN RNN optional)
2. ONNX models pass `onnx.checker.check_model()`
3. Numerical outputs match native inference (rtol < 1e-5 for float32, 1e-10 for float64)
4. Round-trip tests pass for all network types
5. Documentation includes working examples for each type
6. Optional dependency doesn't break base installation
7. All tests pass via `make test` (including new ONNX tests when package installed)

## Is it worth doing?

No, it's not worth doing. Here's my analysis:

### Core Problem: Wrong Tool for the Job

If someone needs ONNX export, they should be using PyTorch or TensorFlow
from the start. The README explicitly states:

"For production machine learning, consider TensorFlow, PyTorch, or JAX"

ONNX export is a production deployment feature. It contradicts cynn's
stated purpose: learning fundamentals, embedded systems, and environments
where large frameworks aren't available.

### Effort vs. Value

Estimated effort: 16-21 days (3-4 weeks)

Realistic user base: Maybe 1-2% of users who are simultaneously:

- Using cynn (for its simplicity)
- Training models worth deploying
- Needing ONNX specifically
- Not better served by just using PyTorch

This is feature creep, not user value.

Technical Issues That Undermine the Core Value

1. Activation function opacity: Several networks have hardcoded or
function-pointer-based activations that can't be reliably introspected.
This means you can't guarantee faithful ONNX conversion—which defeats the
entire point of ONNX (portable, exact models).

2. Philosophical contradiction: cynn's value proposition is
"dependency-free" and "minimal." Adding ONNX—even as optional—pulls users
toward the complex ML ecosystem cynn is supposed to be an alternative to.

### What Would Actually Be Valuable

Phase 1 only: Weight extraction API (~2-3 days instead of 21)

```python
# Just expose this:
weights = network.get_weights()
# Returns dict of numpy arrays

# Users can then:
# - Inspect weights manually
# - Build custom exporters if needed
# - Debug their networks
# - Implement their own serialization
```

This gives 80% of the benefit at 10% of the cost. If someone really needs
ONNX, they can build it themselves using the weight extraction API.

Better Priorities from TODO.md

These would help far more users:

1. Batch training (High Priority) - actual performance improvement
2. Standardized training interface (High Priority) - reduces confusion
3. More examples (High Priority) - supports learning use case
4. Higher-level training API (Medium Priority) - improves usability

### Bottom Line

ONNX export is solving a problem that `cynn` users shouldn't have. If they
need ONNX, they need a different library entirely. Implementing this would
be 3-4 weeks chasing ~zero real users.

Recommendation: Implement weight extraction only (Phase 1), document it
clearly, and move on to features that actually serve `cynn`'s target
audience.
