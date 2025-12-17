# CMFO: Fractal Universal Computation Engine

[![PyPI version](https://badge.fury.io/py/cmfo.svg)](https://badge.fury.io/py/cmfo)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**CMFO** is a deterministic geometric computing platform that replaces probabilistic approximation with **geometric inversion** on a 7-dimensional φ-manifold.

## Installation

```bash
pip install cmfo
```

### Optional Dependencies

```bash
# For CUDA acceleration
pip install cmfo[cuda]

# For development
pip install cmfo[dev]

# For documentation building
pip install cmfo[docs]

# Install all extras
pip install cmfo[cuda,dev,docs]
```

## Quick Start

```python
import cmfo

# Display CMFO information
cmfo.info()

# Create a T7 Tensor
from cmfo import T7Tensor
tensor = cmfo.tensor([1, 1, 1, 1, 1, 1, 1])

# Use gamma-phi operations
from cmfo import gamma_step
result = gamma_step(0.5)

# Phi-based logic operations
from cmfo import phi_and, phi_or, phi_xor, phi_not
a = phi_and(1.0, 0.0)
b = phi_or(1.0, 0.0)
c = phi_xor(1.0, 1.0)
```

## Features

- **T7 Tensor Operations**: 7-dimensional tensor computations on φ-manifold
- **Gamma-Phi Functions**: Fractal geometric operations
- **Phi Logic**: Deterministic, reversible logic gates (AND, OR, XOR, NOT, NAND)
- **Native Performance**: C/C++ core with Python bindings
- **CUDA Support**: Optional GPU acceleration
- **CLI Tools**: Command-line interface for common operations

## Core Components

### T7 Tensor
7-dimensional tensors for fractal computations:
```python
from cmfo import T7Tensor

# Create tensor
t = T7Tensor([1.618, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

# Operations available
# (see full API documentation)
```

### Phi Logic
Reversible geometric logic operations:
```python
from cmfo import phi_and, phi_or, phi_xor

# Deterministic logic
result = phi_and(1.0, 1.0)  # Returns phi-scaled result
```

### Gamma Step
Fractal iteration function:
```python
from cmfo import gamma_step

# Compute gamma step
value = gamma_step(0.5)
```

## Architecture

CMFO operates on a unified mathematical structure where Physics, Logic, and Language are isomorphic operations:

- **L1: Theory** - Unified Field mathematical axioms
- **L2: Engine** - C++/CUDA high-performance core
- **L3: Logic** - Matrix compiler for text-to-matrix translation
- **L4: User** - Python API and CLI

## Documentation

- [Full Documentation](https://1jonmonterv.github.io/CMFO-COMPUTACION-FRACTAL-/)
- [GitHub Repository](https://github.com/1JONMONTERV/CMFO-COMPUTACION-FRACTAL-)
- [Theory Papers](https://github.com/1JONMONTERV/CMFO-COMPUTACION-FRACTAL-/tree/main/docs/theory)

## Verified Claims

This package contains **executable proofs** for:

1. **Physics**: α⁵ correction for particle mass derivation (Error < 10⁻⁹)
2. **Logic**: Reversible Boolean operations via unitary rotations
3. **Mining**: O(1) geometric inversion of cryptographic hashes

See the [main repository](https://github.com/1JONMONTERV/CMFO-COMPUTACION-FRACTAL-) for verification scripts.

## Requirements

- Python 3.9 or higher
- NumPy >= 1.20
- Optional: CUDA-capable GPU for acceleration

## License

MIT License with commercial restrictions for enterprise modules.

## Author

**Jonnathan Montero Viques**  
Email: jmvlavacar@hotmail.com  
Location: San José, Costa Rica

## Citation

If you use CMFO in your research, please cite:

```bibtex
@software{cmfo2024,
  title = {CMFO: Fractal Universal Computation Engine},
  author = {Montero Viques, Jonnathan},
  year = {2024},
  url = {https://github.com/1JONMONTERV/CMFO-COMPUTACION-FRACTAL-}
}
```

## Contributing

See [CONTRIBUTING.md](https://github.com/1JONMONTERV/CMFO-COMPUTACION-FRACTAL-/blob/main/CONTRIBUTING.md) in the main repository.

## Support

For issues, questions, or commercial licensing:
- GitHub Issues: https://github.com/1JONMONTERV/CMFO-COMPUTACION-FRACTAL-/issues
- Email: jmvlavacar@hotmail.com
