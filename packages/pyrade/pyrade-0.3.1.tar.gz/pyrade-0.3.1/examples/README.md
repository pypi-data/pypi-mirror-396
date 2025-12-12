# PyRADE Examples

This directory contains comprehensive examples demonstrating PyRADE's capabilities.

## Files

### `benchmark_experiments.py`
**Main experimental script** - Runs comprehensive benchmark experiments with automatic visualization and data collection.

**Features:**
- Tests multiple benchmark functions (Sphere, Rastrigin, Rosenbrock, Ackley, Griewank, Schwefel, Levy, Zakharov)
- Performs multiple independent runs (default: 30 runs per function)
- Generates convergence plots for each objective function
- Creates boxplots comparing performance across functions
- Saves all results in timestamped experiment folders
- Generates detailed statistics and rankings
- Exports raw data (convergence histories, fitness values, solutions)

**Usage:**
```bash
python benchmark_experiments.py
```

**Output Structure:**
```
experiment_YYYY-MM-DD_HH-MM-SS/
├── convergence_plots/
│   ├── sphere_convergence.png
│   ├── rastrigin_convergence.png
│   ├── rosenbrock_convergence.png
│   └── ... (one per function)
├── all_functions_convergence.png
├── fitness_boxplot.png
├── fitness_boxplot_group1.png
├── fitness_boxplot_group2.png
├── statistics.txt
└── raw_data/
    ├── sphere_convergence.npy
    ├── sphere_final_fitness.npy
    ├── sphere_best_solutions.npy
    └── ... (three files per function)
```

**Customization:**
Edit the `main()` function to adjust parameters:
```python
experiment = BenchmarkExperiment(
    n_runs=30,              # Number of independent runs
    population_size=50,     # DE population size
    max_iterations=100,     # Maximum iterations
    dimensions=10           # Problem dimensionality
)
```

**Quick Test:**
For rapid testing, uncomment the quick test:
```python
if __name__ == "__main__":
    quick_test()  # 5 runs, 3 functions, 5D
```

---

### `visualization_examples.py`
**Visualization gallery** - Demonstrates all available visualization types in PyRADE.

**Includes:**
1. **Convergence Curves** - Fitness improvement over generations
2. **Convergence with Std Dev** - Multiple runs with confidence bands
3. **Fitness Boxplots** - Distribution comparisons
4. **2D Pareto Fronts** - Bi-objective optimization results
5. **3D Pareto Fronts** - Three-objective results with rotation
6. **Parameter Heatmaps** - Population parameter distributions
7. **Parallel Coordinate Plots** - Multi-dimensional parameter exploration
8. **Contour Landscapes** - 2D function landscapes with trajectories
9. **Hypervolume Progress** - Multi-objective quality indicator
10. **IGD Progress** - Inverted Generational Distance tracking
11. **Population Diversity** - Diversity metrics over time

**Usage:**
```bash
python visualization_examples.py
```

**Individual Examples:**
```python
from visualization_examples import example_convergence_curves
example_convergence_curves()
```

---

## Quick Start

### Run Full Experiment Suite
```bash
cd examples
python benchmark_experiments.py
```

Expected runtime: ~5-10 minutes (30 runs × 8 functions)

### View Visualization Gallery
```bash
python visualization_examples.py
```

Expected output: 11 PNG files demonstrating all visualization types

---

## Visualization API

### Basic Usage

```python
from pyrade import OptimizationVisualizer

# Initialize visualizer
viz = OptimizationVisualizer(figsize=(10, 6))

# Plot convergence
fig = viz.plot_convergence_curve(
    history=fitness_history,
    title="My Optimization",
    log_scale=True,
    save_path="convergence.png"
)
```

### Available Plot Types

#### Convergence Curves
```python
viz.plot_convergence_curve(history, labels, log_scale, show_std)
```

#### Fitness Boxplots
```python
viz.plot_fitness_boxplot(fitness_data, title)
```

#### Pareto Fronts
```python
viz.plot_2d_pareto_front(objectives, pareto_front)
viz.plot_3d_pareto_front(objectives, pareto_front)
```

#### Parameter Analysis
```python
viz.plot_parameter_heatmap(parameters, fitness, param_names)
viz.plot_parallel_coordinates(parameters, fitness, normalize=True)
```

#### Landscape Visualization
```python
viz.plot_contour_landscape(benchmark_func, bounds, trajectory)
```

#### Multi-objective Metrics
```python
viz.plot_hypervolume_progress(hypervolume_history)
viz.plot_igd_progress(igd_history)
```

---

## Helper Functions

### Hypervolume Calculation
```python
from pyrade import calculate_hypervolume_2d

hv = calculate_hypervolume_2d(objectives, reference_point)
```

### IGD Calculation
```python
from pyrade import calculate_igd

igd = calculate_igd(obtained_front, true_front)
```

### Pareto Efficiency
```python
from pyrade import is_pareto_efficient

pareto_mask = is_pareto_efficient(objectives)
pareto_solutions = solutions[pareto_mask]
```

---

## Experiment Analysis Workflow

1. **Run Experiments**
   ```bash
   python benchmark_experiments.py
   ```

2. **Review Statistics**
   ```
   Open experiment_YYYY-MM-DD_HH-MM-SS/statistics.txt
   ```

3. **Analyze Convergence**
   - Check individual convergence plots in `convergence_plots/`
   - Compare all functions in `all_functions_convergence.png`

4. **Compare Performance**
   - View boxplots for distribution analysis
   - Check rankings in statistics.txt

5. **Load Raw Data** (for custom analysis)
   ```python
   import numpy as np
   
   convergence = np.load('raw_data/sphere_convergence.npy')
   fitness = np.load('raw_data/sphere_final_fitness.npy')
   solutions = np.load('raw_data/sphere_best_solutions.npy')
   ```

---

## Tips

### Performance Tuning
- Adjust `n_runs` for statistical significance (20-50 recommended)
- Increase `max_iterations` for harder problems
- Scale `population_size` with problem dimensions (5-10x recommended)

### Visualization Quality
- Use `dpi=300` for publication-quality figures
- Set `figsize=(12, 8)` for presentations
- Enable `log_scale=True` for wide fitness ranges

### Custom Benchmarks
Add your own functions to `benchmark_experiments.py`:
```python
def my_function(x):
    return np.sum(x**4)

experiment.benchmarks['MyFunc'] = (my_function, [(-10, 10)] * dimensions)
```

---

## Requirements

All examples require:
- `numpy`
- `matplotlib`
- `pyrade` (installed package)

Install dependencies:
```bash
pip install numpy matplotlib
pip install -e ..  # Install PyRADE in development mode
```

---

## Troubleshooting

**Issue:** `ModuleNotFoundError: No module named 'pyrade'`
**Solution:** Install PyRADE: `pip install -e ..` from examples directory

**Issue:** Plots not displaying
**Solution:** Add `plt.show()` or run in interactive environment

**Issue:** Memory errors with large experiments
**Solution:** Reduce `n_runs` or `dimensions` parameters

**Issue:** Slow execution
**Solution:** Run `quick_test()` for debugging, then scale up

---

## Citation

If you use these examples in your research, please cite:
```
@software{pyrade2025,
  title={PyRADE: Python Rapid Algorithm for Differential Evolution},
  author={PyRADE Contributors},
  year={2025},
  url={https://github.com/arartawil/pyrade}
}
```
