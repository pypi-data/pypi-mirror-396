# ExperimentManager - High-Level Experiment Interface

The `ExperimentManager` class provides a complete, user-friendly interface for running benchmark experiments with PyRADE. It handles everything from running experiments to generating visualizations and exporting results.

## Quick Start

```python
from pyrade import ExperimentManager

# Create experiment manager
exp = ExperimentManager(
    benchmarks=['Sphere', 'Rastrigin', 'Rosenbrock'],
    dimensions=10,
    n_runs=30,
    population_size=50,
    max_iterations=100
)

# Run complete pipeline: experiments + plots + exports + report
exp.run_complete_pipeline()
```

## Features

### 🎯 Automatic Experiment Management
- Select from 11 built-in benchmark functions
- Support for custom objective functions
- Configurable DE parameters (F, CR, population size, iterations)
- Multiple independent runs for statistical significance
- Reproducible results with seed control

### 📊 Comprehensive Visualization
- Individual convergence plots for each benchmark
- Combined convergence comparison plots
- Fitness distribution boxplots (with automatic scale grouping)
- All plots saved in timestamped folders

### 💾 Multi-Format Data Export
- **CSV**: Summary statistics and detailed run-by-run data
- **NumPy**: Raw arrays for custom analysis
- **JSON**: Structured results for integration
- **Text Reports**: Human-readable summaries

### ⏱️ Timestamped Organization
- Automatic folder creation with date/time stamps
- Complete experiment configuration saved
- All results organized in structured directories

## Installation

```bash
pip install pyrade
```

Or install from source:
```bash
pip install -e .
```

## Available Benchmark Functions

Use `ExperimentManager.list_available_benchmarks()` to see all options:

- **Sphere** - Convex, unimodal, bounds: [-100, 100]
- **Rastrigin** - Highly multimodal, bounds: [-5.12, 5.12]
- **Rosenbrock** - Narrow valley, bounds: [-5, 10]
- **Ackley** - Many local minima, bounds: [-32.768, 32.768]
- **Griewank** - Multimodal, bounds: [-600, 600]
- **Schwefel** - Deceptive, bounds: [-500, 500]
- **Levy** - Multimodal, bounds: [-10, 10]
- **Michalewicz** - Steep ridges, bounds: [0, π]
- **Zakharov** - Unimodal, bounds: [-5, 10]
- **Easom** - Flat with sharp optimum, bounds: [-100, 100]
- **StyblinskiTang** - Multimodal, bounds: [-5, 5]

## Usage Examples

### Example 1: Basic Usage

```python
from pyrade import ExperimentManager

exp = ExperimentManager(
    benchmarks=['Sphere', 'Rastrigin', 'Rosenbrock'],
    dimensions=10,
    n_runs=30,
    population_size=50,
    max_iterations=100
)

# Run everything automatically
exp.run_complete_pipeline()
```

**Output Structure:**
```
experiments/experiment_2025-11-27_12-30-45/
├── config.json
├── convergence_plots/
│   ├── sphere_convergence.png
│   ├── rastrigin_convergence.png
│   └── rosenbrock_convergence.png
├── all_convergence_combined.png
├── fitness_boxplot_all.png
├── fitness_boxplot_group1.png
├── fitness_boxplot_group2.png
├── csv_exports/
│   ├── summary_statistics.csv
│   ├── sphere_detailed.csv
│   ├── rastrigin_detailed.csv
│   ├── rosenbrock_detailed.csv
│   └── convergence/
│       ├── sphere_convergence.csv
│       ├── rastrigin_convergence.csv
│       └── rosenbrock_convergence.csv
├── numpy_data/
│   ├── sphere_convergence.npy
│   ├── sphere_final_fitness.npy
│   ├── sphere_best_solutions.npy
│   └── ... (4 files per benchmark)
├── summary_results.json
└── experiment_report.txt
```

### Example 2: Custom Selection

```python
# Select specific benchmarks and parameters
exp = ExperimentManager(
    benchmarks=['Ackley', 'Griewank', 'Schwefel'],
    dimensions=20,
    n_runs=50,
    population_size=100,
    max_iterations=200,
    F=0.7,              # Mutation factor
    CR=0.8,             # Crossover rate
    experiment_name='custom_experiment',
    base_folder='my_experiments',
    seed=42
)

exp.run_complete_pipeline()
```

### Example 3: Step-by-Step Control

```python
exp = ExperimentManager(
    benchmarks=['Sphere', 'Rastrigin'],
    dimensions=10,
    n_runs=30
)

# Step 1: Run experiments
results = exp.run_experiments(verbose=True)

# Step 2: Generate specific plots
exp.plot_convergence_curves(save=True)
exp.plot_combined_convergence(save=True)
exp.plot_boxplots(save=True, split_scales=True)

# Step 3: Export in specific formats
exp.export_results(formats=['csv', 'numpy'])

# Step 4: Generate report
exp.generate_report()
```

### Example 4: All Benchmarks

```python
# Test all available benchmarks
exp = ExperimentManager(
    benchmarks=None,  # None = all benchmarks
    dimensions=10,
    n_runs=30
)

exp.run_complete_pipeline()
```

### Example 5: Custom Objective Function

```python
import numpy as np

# Define custom function
def my_function(x):
    return np.sum(x**2) + np.sum(10 * np.sin(x))

# Mix with standard benchmarks
exp = ExperimentManager(
    benchmarks=['Sphere', my_function],
    dimensions=10,
    n_runs=20
)

exp.run_complete_pipeline()
```

### Example 6: Accessing Raw Data

```python
exp = ExperimentManager(
    benchmarks=['Sphere', 'Rastrigin'],
    dimensions=10,
    n_runs=30
)

# Run experiments
exp.run_experiments()

# Access results programmatically
for bench_name, data in exp.results.items():
    print(f"{bench_name}:")
    print(f"  Mean: {data['mean_fitness']:.6e}")
    print(f"  Std: {data['std_fitness']:.6e}")
    print(f"  Best: {data['min_fitness']:.6e}")
    
    # Access raw arrays
    convergence = data['convergence_histories']  # List of arrays
    final_fitness = data['final_fitness']        # List of floats
    best_solutions = data['best_solutions']      # List of arrays
    times = data['execution_times']              # List of floats
```

## API Reference

### Constructor Parameters

```python
ExperimentManager(
    benchmarks=None,              # List of benchmark names or functions
    dimensions=10,                # Problem dimensionality
    n_runs=30,                    # Independent runs per benchmark
    population_size=50,           # DE population size
    max_iterations=100,           # Maximum iterations
    F=0.8,                        # Mutation factor
    CR=0.9,                       # Crossover rate
    experiment_name=None,         # Custom name (default: timestamp)
    base_folder='experiments',    # Base directory for experiments
    seed=None                     # Random seed (auto-generated if None)
)
```

### Methods

#### `run_experiments(verbose=True)`
Run all optimization experiments.

**Returns:** Dictionary of results for each benchmark

#### `plot_convergence_curves(save=True)`
Generate individual convergence plots for each benchmark.

**Returns:** Dictionary mapping benchmark names to figure objects

#### `plot_combined_convergence(save=True)`
Plot all convergence curves on one figure for comparison.

**Returns:** Figure object

#### `plot_boxplots(save=True, split_scales=True)`
Generate boxplots comparing fitness distributions.

**Parameters:**
- `split_scales`: Create separate plots for different fitness magnitudes

**Returns:** List of figure objects

#### `plot_all()`
Generate all available visualizations at once.

#### `export_to_csv(detailed=True)`
Export results to CSV files.

**Parameters:**
- `detailed`: Include run-by-run data and convergence histories

#### `export_to_numpy()`
Export raw data to NumPy `.npy` files.

#### `export_results(formats=['csv', 'numpy', 'json'])`
Export in multiple formats.

**Parameters:**
- `formats`: List of export formats

#### `generate_report()`
Generate comprehensive text report with statistics and rankings.

#### `run_complete_pipeline(verbose=True)`
Execute the complete experimental workflow:
1. Run experiments
2. Generate all plots
3. Export all data formats
4. Generate report

### Class Method

#### `ExperimentManager.list_available_benchmarks()`
Print list of available benchmark functions.

## Data Formats

### CSV Exports

#### summary_statistics.csv
```csv
Benchmark,Mean_Fitness,Std_Fitness,Min_Fitness,Max_Fitness,Median_Fitness,Mean_Time_sec,Total_Time_sec
Sphere,1.234e-10,5.678e-11,3.456e-11,2.345e-10,1.123e-10,0.523,15.69
Rastrigin,2.345e+01,3.456e+00,1.234e+01,3.456e+01,2.234e+01,0.634,19.02
```

#### {benchmark}_detailed.csv
```csv
Run,Final_Fitness,Execution_Time_sec,X1,X2,X3,...
1,1.234e-10,0.523,0.0001,-0.0002,0.0003,...
2,5.678e-11,0.512,0.0002,0.0001,-0.0001,...
```

#### convergence/{benchmark}_convergence.csv
```csv
Generation,Run_1,Run_2,Run_3,...
0,1000.234,998.567,1001.123,...
1,856.345,834.678,867.234,...
2,723.456,701.789,734.567,...
```

### NumPy Files

- `{benchmark}_convergence.npy` - Shape: (n_runs, n_generations)
- `{benchmark}_final_fitness.npy` - Shape: (n_runs,)
- `{benchmark}_best_solutions.npy` - Shape: (n_runs, dimensions)
- `{benchmark}_execution_times.npy` - Shape: (n_runs,)

### JSON Format

```json
{
  "Sphere": {
    "mean_fitness": 1.234e-10,
    "std_fitness": 5.678e-11,
    "min_fitness": 3.456e-11,
    "max_fitness": 2.345e-10,
    "median_fitness": 1.123e-10,
    "mean_time": 0.523,
    "total_time": 15.69
  },
  ...
}
```

## Configuration File

Each experiment automatically saves a `config.json`:

```json
{
  "experiment_name": "experiment_2025-11-27_12-30-45",
  "timestamp": "2025-11-27T12:30:45.123456",
  "benchmarks": ["Sphere", "Rastrigin", "Rosenbrock"],
  "dimensions": 10,
  "n_runs": 30,
  "population_size": 50,
  "max_iterations": 100,
  "F": 0.8,
  "CR": 0.9,
  "seed": 42
}
```

## Tips & Best Practices

### Choosing Parameters

**Number of Runs:**
- Quick test: 5-10 runs
- Research: 30-50 runs
- Publication: 50-100 runs

**Population Size:**
- Rule of thumb: 5-10× problem dimensions
- Minimum: 4 (DE requirement)
- Typical: 50-100 for D=10-30

**Max Iterations:**
- Simple problems (Sphere): 50-100
- Complex problems (Rastrigin): 200-500
- High dimensions: 500-1000+

### Performance Optimization

```python
# For large experiments, run in stages
exp = ExperimentManager(benchmarks=['Sphere'], n_runs=100)

# Run experiments (time-consuming part)
exp.run_experiments()

# Generate plots later (fast)
exp.plot_all()

# Export incrementally
exp.export_to_csv()
exp.export_to_numpy()
```

### Memory Management

For very large experiments (many runs × high dimensions):

```python
# Process benchmarks one at a time
for bench in ['Sphere', 'Rastrigin', 'Rosenbrock']:
    exp = ExperimentManager(
        benchmarks=[bench],
        dimensions=100,
        n_runs=100,
        experiment_name=f'large_exp_{bench}'
    )
    exp.run_complete_pipeline()
```

### Reproducibility

```python
# Always set seed for reproducible results
exp = ExperimentManager(
    benchmarks=['Sphere', 'Rastrigin'],
    seed=42  # Fixed seed
)
```

## Integration with Analysis Tools

### Load Data in Python

```python
import numpy as np
import pandas as pd

# Load convergence data
conv = np.load('experiments/my_exp/numpy_data/sphere_convergence.npy')

# Load CSV summary
summary = pd.read_csv('experiments/my_exp/csv_exports/summary_statistics.csv')

# Load detailed results
detailed = pd.read_csv('experiments/my_exp/csv_exports/sphere_detailed.csv')
```

### Use in Jupyter Notebooks

```python
from pyrade import ExperimentManager
import matplotlib.pyplot as plt

exp = ExperimentManager(benchmarks=['Sphere'], n_runs=20)
exp.run_experiments()

# Custom analysis
for bench_name, data in exp.results.items():
    fig, ax = plt.subplots()
    for history in data['convergence_histories']:
        ax.plot(history, alpha=0.3)
    ax.set_yscale('log')
    plt.show()
```

## Troubleshooting

**Issue:** Out of memory errors
**Solution:** Reduce `n_runs`, `dimensions`, or process benchmarks separately

**Issue:** Slow execution
**Solution:** Reduce `max_iterations` or `population_size`, or use fewer benchmarks

**Issue:** Plots not displaying
**Solution:** Set `save=False` in plot methods and add `plt.show()`

**Issue:** Custom function not working
**Solution:** Ensure function accepts NumPy array and returns scalar

## Example Workflow for Research

```python
# 1. Quick exploratory test
exp_test = ExperimentManager(
    benchmarks=['Sphere', 'Rastrigin'],
    dimensions=10,
    n_runs=5,
    max_iterations=50,
    experiment_name='pilot_study'
)
exp_test.run_complete_pipeline()

# 2. Analyze pilot results, then run full experiment
exp_full = ExperimentManager(
    benchmarks=['Sphere', 'Rastrigin', 'Rosenbrock', 'Ackley'],
    dimensions=30,
    n_runs=50,
    population_size=150,
    max_iterations=500,
    experiment_name='full_study',
    seed=42
)
exp_full.run_complete_pipeline()

# 3. Generate publication-ready plots
exp_full.plot_convergence_curves(save=True)
exp_full.plot_boxplots(save=True)

# 4. Export data for statistical analysis in R/MATLAB
exp_full.export_results(formats=['csv'])
```

## Citation

If you use ExperimentManager in your research:

```bibtex
@software{pyrade2025,
  title={PyRADE: Python Rapid Algorithm for Differential Evolution},
  author={PyRADE Contributors},
  year={2025},
  url={https://github.com/arartawil/pyrade}
}
```
