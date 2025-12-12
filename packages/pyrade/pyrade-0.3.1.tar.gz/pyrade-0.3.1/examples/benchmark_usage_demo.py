"""
Demo: Three ways to use PyRADE benchmark functions

This shows the flexibility of the benchmark system.
"""

import numpy as np
from pyrade.benchmarks import (
    # Method 1: Direct function import
    sphere, rastrigin,
    
    # Method 2: Class-based with metadata
    Sphere, Rastrigin,
    
    # Method 3: Dynamic access
    get_benchmark, list_benchmarks
)

print("=" * 80)
print("PyRADE Benchmark Functions - Usage Examples")
print("=" * 80)

# Test point
x = np.array([1.0, 2.0, 3.0])

print("\n### Method 1: Direct Function Import (Simplest) ###")
print("Best for: Quick experiments, when you know the function name")
print()
result = sphere(x)
print(f"sphere({x}) = {result}")
result = rastrigin(x)
print(f"rastrigin({x}) = {result:.6f}")

print("\n### Method 2: Class-Based with Metadata (Recommended) ###")
print("Best for: When you need bounds, optimum location, problem info")
print()
func = Sphere(dim=3)
print(f"Function: {func.__class__.__name__}")
print(f"Bounds: {func.bounds}")
print(f"Optimum: {func.optimum}")
print(f"Optimum location: {func.optimum_location}")
result = func(x)
print(f"f({x}) = {result}")

print()
func2 = Rastrigin(dim=3)
print(f"Function: {func2.__class__.__name__}")
print(f"Bounds: {func2.bounds}")
print(f"Optimum: {func2.optimum}")
result2 = func2(x)
print(f"f({x}) = {result2:.6f}")

print("\n### Method 3: Dynamic Access by Name (Most Flexible) ###")
print("Best for: User input, configuration files, batch experiments")
print()

# Get function by name (case-insensitive)
func3 = get_benchmark('ackley', dim=5)
x2 = np.random.randn(5)
result3 = func3(x2)
print(f"ackley (via get_benchmark) = {result3:.6f}")

# Get simple function version
func4 = get_benchmark('schwefel')  # lowercase gets simple function
x3 = np.random.uniform(-500, 500, 10)
result4 = func4(x3)
print(f"schwefel (simple function) = {result4:.6f}")

print("\n### List All Available Benchmarks ###")
benchmarks = list_benchmarks()
print(f"\nClass-based ({len(benchmarks['classes'])}): {benchmarks['classes']}")
print(f"\nFunction-based ({len(benchmarks['functions'])}): {benchmarks['functions']}")

print("\n" + "=" * 80)
print("Summary of Three Methods:")
print("=" * 80)
print("1. Direct import:    from pyrade.benchmarks import sphere")
print("                     result = sphere(x)")
print()
print("2. Class-based:      from pyrade.benchmarks import Sphere")
print("                     func = Sphere(dim=30)")
print("                     result = func(x)")
print()
print("3. Dynamic access:   from pyrade.benchmarks import get_benchmark")
print("                     func = get_benchmark('sphere', dim=30)")
print("                     result = func(x)")
print("=" * 80)
