# Installation

## Using pip (Recommended)

Install PyRADE from PyPI:

```bash
pip install pyrade
```

## From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/arartawil/pyrade.git
cd pyrade
pip install -e .
```

## Requirements

- Python >= 3.7
- NumPy >= 1.20.0

## Verification

Verify the installation:

```python
import pyrade
from pyrade import DifferentialEvolution

print(f"PyRADE version: {pyrade.__version__}")
```

## Development Installation

For development with additional tools:

```bash
git clone https://github.com/arartawil/pyrade.git
cd pyrade
pip install -e ".[dev]"
```

This includes:
- pytest (testing)
- pytest-cov (coverage)
- black (formatting)
- flake8 (linting)
- mypy (type checking)
