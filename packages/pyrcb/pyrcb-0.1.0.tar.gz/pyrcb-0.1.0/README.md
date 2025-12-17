# concrete-beam

A Python library for concrete beam analysis and design.

## Installation

### From Source (Development)

Clone the repository and install in development mode:

```bash
git clone https://github.com/alexiusacademia/concrete-beam.git
cd concrete-beam
pip install -e ".[dev]"
```

### From PyPI (Once Published)

```bash
pip install pyrcb
```

## Usage

### Basic Example: Calculate Steel Stresses

Calculate stresses in multiple layers of reinforcement steel:

```python
from concrete_beam import calculate_steel_stresses

# Beam parameters
neutral_axis_depth = 100  # mm (depth of neutral axis from compression face)
steel_depths = [50, 100, 150]  # mm (effective depths of each steel layer)
yield_stress = 400  # MPa (steel yield strength)

# Calculate stresses (far end steel at 150mm will yield)
stresses = calculate_steel_stresses(
    neutral_axis_depth=neutral_axis_depth,
    steel_depths=steel_depths,
    yield_stress=yield_stress
)

print(f"Steel stresses: {stresses} MPa")
# Output: Steel stresses: [elastic_stress_1, elastic_stress_2, 400.0] MPa
```

### Example: Calculate Compression Block Height

Determine the compression block height when far end steel yields:

```python
from concrete_beam import calculate_compression_block_height

# Beam parameters
far_end_depth = 500  # mm (effective depth of far end steel)
yield_stress = 400  # MPa

# Calculate compression block height (neutral axis depth)
c = calculate_compression_block_height(
    far_end_depth=far_end_depth,
    yield_stress=yield_stress
)

print(f"Compression block height (C): {c:.2f} mm")
```

### Complete Example: Beam Analysis

Analyze a reinforced concrete beam with multiple steel layers:

```python
from concrete_beam import (
    calculate_compression_block_height,
    calculate_steel_stresses,
)

# Beam geometry
beam_depth = 600  # mm
cover = 40  # mm
steel_layers = 3
layer_spacing = 50  # mm

# Calculate effective depths for each steel layer
steel_depths = [
    cover + i * layer_spacing for i in range(steel_layers)
]
far_end_depth = steel_depths[-1]

# Material properties
yield_stress = 400  # MPa (Grade 60 steel)
elastic_modulus = 200000  # MPa
concrete_strain = 0.003  # Maximum concrete strain

# Step 1: Calculate compression block height assuming far end yields
c = calculate_compression_block_height(
    far_end_depth=far_end_depth,
    yield_stress=yield_stress,
    elastic_modulus=elastic_modulus,
    concrete_strain=concrete_strain,
)

print(f"Neutral axis depth (C): {c:.2f} mm")

# Step 2: Calculate stresses in all steel layers
stresses = calculate_steel_stresses(
    neutral_axis_depth=c,
    steel_depths=steel_depths,
    yield_stress=yield_stress,
    elastic_modulus=elastic_modulus,
    concrete_strain=concrete_strain,
)

# Display results
print("\nSteel Layer Analysis:")
for i, (depth, stress) in enumerate(zip(steel_depths, stresses), 1):
    status = "YIELDED" if stress >= yield_stress else "ELASTIC"
    print(f"  Layer {i} (d={depth}mm): {stress:.2f} MPa - {status}")
```

## Development

### Setup

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## Examples

See the [examples directory](examples/) for complete working examples.

First, make sure you've installed the package in development mode (see Installation above), then run:

```bash
python examples/basic_usage.py
```

The examples demonstrate:
- Calculating steel stresses in multiple layers
- Determining compression block height
- Complete beam analysis workflows

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

MIT License - see LICENSE file for details.

