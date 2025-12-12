# PyRADE Documentation

Welcome to **PyRADE** (Python Rapid Algorithm for Differential Evolution) - a high-performance, modular Differential Evolution optimization package.

```{toctree}
:maxdepth: 2
:caption: Contents:

installation
quickstart
user_guide
api_reference
examples
contributing
```

## Overview

PyRADE is a production-ready optimization library implementing **Differential Evolution (DE)**, a powerful evolutionary algorithm for global optimization. Unlike traditional implementations that sacrifice code quality for performance, PyRADE proves you can have **both** through intelligent design.

### Key Features

- **⚡ High Performance**: 3-5x faster than traditional implementations through aggressive NumPy vectorization
- **🏗️ Clean Architecture**: Strategy pattern for all operators - easy to understand and extend
- **🔧 Modular Design**: Plug-and-play mutation, crossover, and selection strategies
- **📦 Production Ready**: Well-documented, tested, professional-quality code
- **🎯 Easy to Use**: Simple, intuitive API similar to scikit-learn optimizers
- **🧪 Comprehensive**: Includes 12 benchmark functions and multiple real-world examples

## Quick Example

```python
import numpy as np
from pyrade import DifferentialEvolution

# Define your objective function
def sphere(x):
    return np.sum(x**2)

# Create optimizer
optimizer = DifferentialEvolution(
    objective_func=sphere,
    bounds=[(-100, 100)] * 10,
    pop_size=50,
    max_iter=200
)

# Run optimization
result = optimizer.optimize()
print(f"Best fitness: {result['best_fitness']:.6e}")
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
