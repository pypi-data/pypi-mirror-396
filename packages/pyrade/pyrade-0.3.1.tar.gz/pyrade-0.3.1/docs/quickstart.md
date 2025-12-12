# Quick Start

This guide will get you started with PyRADE in minutes.

## Basic Optimization

The simplest way to use PyRADE:

```python
import numpy as np
from pyrade import DifferentialEvolution

# Define objective function to minimize
def sphere(x):
    """Simple quadratic function"""
    return np.sum(x**2)

# Create optimizer
optimizer = DifferentialEvolution(
    objective_func=sphere,
    bounds=[(-100, 100)] * 10,  # 10D problem
    pop_size=50,
    max_iter=200,
    verbose=True
)

# Run optimization
result = optimizer.optimize()

# View results
print(f"Best solution: {result['best_solution']}")
print(f"Best fitness: {result['best_fitness']:.6e}")
print(f"Time taken: {result['time']:.2f}s")
```

## Using Benchmark Functions

PyRADE includes 12 standard benchmark functions:

```python
from pyrade import DifferentialEvolution
from pyrade.benchmarks import Rastrigin

# Create benchmark function
func = Rastrigin(dim=20)

# Optimize
optimizer = DifferentialEvolution(
    objective_func=func,
    bounds=func.get_bounds_array(),
    pop_size=100,
    max_iter=300
)

result = optimizer.optimize()
error = abs(result['best_fitness'] - func.optimum)
print(f"Error from global optimum: {error:.6e}")
```

## Custom Strategies

Use specific mutation, crossover, and selection strategies:

```python
from pyrade import DifferentialEvolution
from pyrade.operators import DEbest1, ExponentialCrossover, GreedySelection

optimizer = DifferentialEvolution(
    objective_func=my_function,
    bounds=my_bounds,
    mutation=DEbest1(F=0.8),
    crossover=ExponentialCrossover(CR=0.9),
    selection=GreedySelection(),
    pop_size=100,
    max_iter=500
)

result = optimizer.optimize()
```

## Next Steps

- Read the [User Guide](user_guide.md) for detailed information
- Check the [API Reference](api_reference.md) for complete documentation
- Explore [Examples](examples.md) for real-world applications
