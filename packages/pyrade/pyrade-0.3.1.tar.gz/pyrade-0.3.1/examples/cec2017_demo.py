"""
CEC2017 Benchmark Functions Usage Demo

CEC2017 provides 30 competition-grade benchmark functions:
- F1-F3:   Unimodal (3 functions)
- F4-F10:  Simple Multimodal (7 functions) - IMPLEMENTED
- F11-F20: Hybrid (10 functions) - Coming soon
- F21-F30: Composition (10 functions) - Coming soon

Supported dimensions: 10, 30, 50, 100
"""

import numpy as np
from pyrade import DErand1bin
from pyrade.benchmarks import CEC2017Function

print("=" * 80)
print("CEC2017 Benchmark Functions Demo")
print("=" * 80)

# Example 1: Create and evaluate a CEC2017 function
print("\n### Example 1: Basic Usage ###")
func = CEC2017Function(func_num=5, dimensions=10)  # F5: Rastrigin
print(f"Function: {func.name}")
print(f"Dimensions: {func.dimensions}")
print(f"Bounds: {func.bounds}")
print(f"Optimal value: {func.optimum}")

x = np.random.uniform(-100, 100, 10)
result = func(x)
print(f"f(random x) = {result:.6f}")

# Example 2: Optimize a CEC2017 function
print("\n### Example 2: Optimization ###")
print("Optimizing CEC2017 F1 (Bent Cigar) with DErand1bin...")

func1 = CEC2017Function(func_num=1, dimensions=10)
optimizer = DErand1bin(
    objective_func=func1,
    bounds=func1.get_bounds_array(),
    pop_size=50,
    max_iter=100,
    verbose=False,
    seed=42
)

result = optimizer.optimize()
print(f"Best fitness: {result['best_fitness']:.6e}")
print(f"Target (optimum): {func1.optimum:.6e}")
print(f"Error: {abs(result['best_fitness'] - func1.optimum):.6e}")

# Example 3: Compare multiple CEC2017 functions
print("\n### Example 3: Multiple Functions ###")
print(f"{'Function':<20} {'Dimension':<12} {'Random Point':<20} {'Optimum'}")
print("-" * 80)

for func_num in [1, 2, 3, 4, 5]:
    f = CEC2017Function(func_num=func_num, dimensions=10)
    x = np.random.uniform(-100, 100, 10)
    val = f(x)
    print(f"{f.name:<20} {f.dimensions:<12} {val:<20.6e} {f.optimum:.1f}")

# Example 4: Different dimensions
print("\n### Example 4: Different Dimensions ###")
print("CEC2017 F5 (Rastrigin) across dimensions:")
print(f"{'Dim':<8} {'Random Eval':<20} {'Optimum'}")
print("-" * 50)

for dim in [10, 30, 50]:
    f = CEC2017Function(func_num=5, dimensions=dim)
    x = np.random.uniform(-100, 100, dim)
    val = f(x)
    print(f"{dim:<8} {val:<20.6e} {f.optimum:.1f}")

print("\n" + "=" * 80)
print("CEC2017 Functions Status:")
print("=" * 80)
print("✓ F1-F3:   Unimodal (3 implemented)")
print("✓ F4-F10:  Simple Multimodal (7 implemented)")
print("⏳ F11-F20: Hybrid (coming in v0.4.0)")
print("⏳ F21-F30: Composition (coming in v0.4.0)")
print("=" * 80)

# Example 5: Integration with main.py
print("\n### Usage in main.py ###")
print("""
# In main.py, add:
from pyrade.benchmarks import CEC2017Function

# Then use like any benchmark:
BENCHMARK_FUNC = CEC2017Function(func_num=5, dimensions=30)
BOUNDS = BENCHMARK_FUNC.get_bounds_array()
""")

print("\n✓ CEC2017 integration complete!")
