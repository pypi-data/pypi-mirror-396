# PyRADE Simplified Interface

## Overview

PyRADE v0.3.1+ includes a **simplified high-level interface** for running experiments with minimal boilerplate code. All experiment logic has been moved to `pyrade/runner.py`, leaving clean, easy-to-read configuration files.

## Quick Start

### Minimal Example (3 lines!)

```python
from pyrade import DErand1bin, run_single
from pyrade.benchmarks import sphere

result = run_single(DErand1bin, sphere, dimensions=30)
```

### Standard Example (~15 lines vs ~850 lines before)

**`main_simple.py`:**
```python
from pyrade import DErand1bin
from pyrade.benchmarks import sphere
from pyrade.runner import run_single

result = run_single(
    algorithm=DErand1bin,
    benchmark=sphere,
    dimensions=30,
    bounds=(-100, 100),
    pop_size=50,
    max_iter=1000,
    F=0.8,
    CR=0.9,
    seed=42,
    viz_config='all'  # Generate all visualizations
)
```

## API Reference

### `run_single()` - Single Experiment

```python
result = run_single(
    algorithm,          # DE algorithm class (e.g., DErand1bin)
    benchmark,          # Function to optimize
    dimensions=30,      # Problem dimensionality
    bounds=(-100, 100), # Search space bounds
    pop_size=50,        # Population size
    max_iter=1000,      # Maximum iterations
    F=0.8,             # Mutation factor
    CR=0.9,            # Crossover rate
    seed=42,           # Random seed
    verbose=True,      # Print progress
    save_results=True, # Save to CSV
    save_plots=True,   # Generate plots
    output_dir="experimental",
    viz_config='all'   # 'all', 'basic', 'research', 'none'
)
```

**Returns:** Dictionary with `best_fitness`, `best_solution`, `time`, `history`, etc.

**Generated files:**
- `experimental/YYYYMMDD_HHMMSS/single_run_results.csv`
- `experimental/YYYYMMDD_HHMMSS/convergence_history.csv`
- `experimental/YYYYMMDD_HHMMSS/*.png` (4-5 plots with `viz_config='all'`)

---

### `run_multiple()` - Statistical Analysis

```python
fitness, histories = run_multiple(
    algorithm,
    benchmark,
    dimensions=30,
    bounds=(-100, 100),
    pop_size=50,
    max_iter=1000,
    F=0.8,
    CR=0.9,
    seed=42,
    num_runs=10,        # Number of independent runs
    save_results=True,
    save_plots=True,
    output_dir="experimental",
    viz_config='all'
)
```

**Returns:** Tuple of `(fitness_array, histories_list)`

**Generated files:**
- `experimental/YYYYMMDD_HHMMSS/multiple_runs_statistics.csv`
- `experimental/YYYYMMDD_HHMMSS/all_runs_results.csv`
- `experimental/YYYYMMDD_HHMMSS/*.png` (5 plots with `viz_config='all'`)

**Example usage:**
```python
fitness, histories = run_multiple(DErand1bin, sphere, num_runs=30)
print(f"Mean ± Std: {fitness.mean():.6e} ± {fitness.std():.6e}")
```

---

### `compare_algorithms()` - Algorithm Comparison

```python
results = compare_algorithms(
    algorithms,         # List of algorithm classes
    benchmark,
    dimensions=30,
    bounds=(-100, 100),
    pop_size=50,
    max_iter=1000,
    F=0.8,
    CR=0.9,
    seed=42,
    num_runs=10,        # Runs per algorithm
    save_results=True,
    save_plots=True,
    output_dir="experimental",
    viz_config='all'
)
```

**Returns:** Dictionary `{algorithm_name: fitness_array}`

**Generated files:**
- `experimental/YYYYMMDD_HHMMSS/algorithm_comparison_summary.csv`
- `experimental/YYYYMMDD_HHMMSS/algorithm_comparison_detailed.csv`
- `experimental/YYYYMMDD_HHMMSS/*.png` (2+ plots)

**Example usage:**
```python
from pyrade import DErand1bin, DEbest1bin, DEcurrentToBest1bin

results = compare_algorithms(
    algorithms=[DErand1bin, DEbest1bin, DEcurrentToBest1bin],
    benchmark=rastrigin,
    num_runs=30
)

# Find best algorithm
best = min(results.items(), key=lambda x: x[1].mean())
print(f"Winner: {best[0]}")
```

## Visualization Configuration

The `viz_config` parameter controls which plots are generated:

### Quick Presets

```python
viz_config='all'       # Generate all available plots (4-5 for single, 5 for multiple)
viz_config='basic'     # Only essential plots (convergence + boxplot)
viz_config='research'  # Full research suite (all statistical plots)
viz_config='none'      # No plots, CSV only
```

### Fine-Grained Control

```python
viz_config={
    'convergence_curve': True,
    'fitness_boxplot': True,
    'parameter_heatmap': True,
    'parallel_coordinates': False,
    'population_diversity': True,
    'contour_landscape': True,  # 2D problems only
    'pareto_front_2d': False,   # Multi-objective only
    'pareto_front_3d': False,
    'hypervolume_progress': False,
    'igd_progress': False
}
```

## Complete Examples

### Example 1: Minimal (3 lines)
```python
from pyrade import DErand1bin, run_single
from pyrade.benchmarks import sphere

result = run_single(DErand1bin, sphere, dimensions=30)
```

### Example 2: Multiple Runs with Statistics
```python
from pyrade import DErand1bin, run_multiple
from pyrade.benchmarks import rastrigin

fitness, histories = run_multiple(
    algorithm=DErand1bin,
    benchmark=rastrigin,
    dimensions=30,
    bounds=(-5.12, 5.12),
    num_runs=30,
    viz_config='research'
)

print(f"Best: {fitness.min():.6e}")
print(f"Mean ± Std: {fitness.mean():.6e} ± {fitness.std():.6e}")
```

### Example 3: Algorithm Comparison
```python
from pyrade import DErand1bin, DEbest1bin, DEcurrentToBest1bin, compare_algorithms
from pyrade.benchmarks import ackley

results = compare_algorithms(
    algorithms=[DErand1bin, DEbest1bin, DEcurrentToBest1bin],
    benchmark=ackley,
    dimensions=30,
    bounds=(-32.768, 32.768),
    num_runs=30,
    viz_config='all'
)

# Analyze results
for name, fitness in results.items():
    print(f"{name}: {fitness.mean():.6e} ± {fitness.std():.6e}")
```

### Example 4: CEC2017 Benchmark
```python
from pyrade import DErand1bin, run_single
from pyrade.benchmarks import CEC2017Function

# Use CEC2017 F5 (Rastrigin)
benchmark = CEC2017Function(func_num=5, dimensions=30)

result = run_single(
    algorithm=DErand1bin,
    benchmark=benchmark,
    dimensions=30,  # Must match CEC2017 dimensions
    bounds=benchmark.get_bounds_array(),  # Use CEC2017 bounds
    max_iter=1000,
    viz_config='all'
)
```

### Example 5: 2D Landscape Visualization
```python
from pyrade import DErand1bin, run_single
from pyrade.benchmarks import rosenbrock

# 2D problems generate fitness landscape plots
result = run_single(
    algorithm=DErand1bin,
    benchmark=rosenbrock,
    dimensions=2,  # Must be 2 for landscape plot
    bounds=(-5, 10),
    pop_size=30,
    max_iter=500,
    viz_config='all'  # Includes fitness_landscape_2d.png
)
```

## Migration Guide

### Old Way (main.py ~850 lines)
```python
# Configure 80 lines of parameters
ALGORITHM = DErand1bin
BENCHMARK_FUNC = sphere
DIMENSIONS = 30
# ... 70 more lines ...

# Run with 3 experiment functions (300+ lines each)
if choice == "1":
    run_single_experiment()  # 300 lines of code
elif choice == "2":
    run_multiple_experiments()  # 300 lines of code
elif choice == "3":
    run_algorithm_comparison()  # 300 lines of code
```

### New Way (main_simple.py ~120 lines)
```python
# Configure in 10 lines
ALGORITHM = DErand1bin
BENCHMARK_FUNC = sphere
DIMENSIONS = 30
POPULATION_SIZE = 50
MAX_ITERATIONS = 1000
# ... 5 more parameters ...

# Run with clean function calls
if choice == "1":
    run_single(ALGORITHM, BENCHMARK_FUNC, DIMENSIONS, ...)
elif choice == "2":
    run_multiple(ALGORITHM, BENCHMARK_FUNC, DIMENSIONS, num_runs=10, ...)
elif choice == "3":
    compare_algorithms([Algo1, Algo2, Algo3], BENCHMARK_FUNC, ...)
```

**Reduction:** 850 lines → 120 lines (86% smaller!)

## File Structure

```
PyRADE/
├── pyrade/
│   ├── runner.py              # NEW: High-level experiment runners
│   ├── algorithms/
│   ├── benchmarks/
│   └── visualization.py
├── main.py                     # OLD: 850 lines (kept for compatibility)
├── main_simple.py              # NEW: 120 lines (recommended)
├── examples/
│   ├── minimal_example.py      # NEW: 10 lines
│   ├── multiple_runs_example.py
│   └── algorithm_comparison_example.py
├── SIMPLIFIED_INTERFACE.md     # This file
└── VISUALIZATION_GUIDE.md
```

## Benefits

✅ **86% less boilerplate** (850 → 120 lines)  
✅ **Cleaner configuration** - just set parameters  
✅ **Same features** - all functionality preserved  
✅ **Better modularity** - experiment logic in `runner.py`  
✅ **Easier maintenance** - changes in one place  
✅ **More readable** - focus on what, not how  
✅ **Backward compatible** - old `main.py` still works  

## Next Steps

1. **Try the examples:** `python examples/minimal_example.py`
2. **Use `main_simple.py`:** Cleaner than old `main.py`
3. **Read `VISUALIZATION_GUIDE.md`:** Understand plot types
4. **Check `ROADMAP_v1.0.0.md`:** See what's coming

---

**PyRADE v0.3.1+** | Updated: 2025-12-01
