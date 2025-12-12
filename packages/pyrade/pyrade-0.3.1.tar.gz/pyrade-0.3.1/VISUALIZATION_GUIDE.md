# PyRADE Visualization Guide

## Overview
PyRADE v0.3.1+ includes a comprehensive visualization controller that generates publication-quality plots for your optimization experiments. The system automatically adapts to your experiment type and problem characteristics.

## Quick Start

### Configuration in `main.py`

```python
# Option 1: Use a preset (recommended)
VISUALIZATION_CONFIG = 'all'        # Generate all applicable plots
VISUALIZATION_CONFIG = 'basic'      # Only essential plots
VISUALIZATION_CONFIG = 'research'   # Full research suite
VISUALIZATION_CONFIG = 'none'       # Disable all plots

# Option 2: Fine-grained control
VISUALIZATION_CONFIG = {
    'convergence_curve': True,
    'fitness_boxplot': False,
    'parameter_heatmap': True,
    # ... etc
}
```

## Plot Types by Experiment Mode

### 1. Single Run Mode
**Generated plots when using `VISUALIZATION_CONFIG = 'all'`:**

| Plot File | Description | Use Case |
|-----------|-------------|----------|
| `convergence.png` | Standard fitness vs. iterations | Track optimization progress |
| `solution_parameters.png` | Bar chart of solution dimensions | Understand solution structure |
| `convergence_analysis.png` | Log and linear scale side-by-side | Detailed convergence analysis |
| `improvement_rate.png` | Rate of fitness improvement | Identify stagnation periods |
| `fitness_landscape_2d.png` | Contour plot with best solution | **2D problems only** - visualize search space |

**Note:** Multi-objective plots (Pareto, hypervolume, IGD) are skipped as they require MO data.

### 2. Multiple Runs Mode
**Generated plots when using `VISUALIZATION_CONFIG = 'all'`:**

| Plot File | Description | Use Case |
|-----------|-------------|----------|
| `convergence_multiple_runs.png` | All runs with mean overlay | Compare run variability |
| `boxplot_distribution.png` | Distribution of final results | Statistical robustness |
| `violin_plot.png` | Density distribution | Detailed result distribution |
| `statistical_summary.png` | Best/worst/mean/median bar chart | Quick statistical overview |
| `convergence_uncertainty.png` | Mean ± std deviation bands | Quantify uncertainty |

### 3. Algorithm Comparison Mode
**Generated plots when using `VISUALIZATION_CONFIG = 'all'`:**

| Plot File | Description | Use Case |
|-----------|-------------|----------|
| `convergence_comparison.png` | Combined convergence curves | Compare convergence behavior |
| `statistical_comparison.png` | Side-by-side boxplots | Statistical comparison |
| `algorithm_rankings.png` | Ranked performance bars | Identify best algorithm |
| `win_loss_matrix.png` | Head-to-head comparison | Pairwise algorithm analysis |

## Plot Availability Matrix

| Plot Type | Single Run | Multiple Runs | Comparison | Special Requirements |
|-----------|------------|---------------|------------|---------------------|
| Convergence curve | ✅ | ✅ | ✅ | None |
| Solution parameters | ✅ | ✅ | ✅ | None |
| Convergence analysis | ✅ | ✅ | ✅ | None |
| Improvement rate | ✅ | ✅ | ❌ | None |
| Fitness boxplot | ❌ | ✅ | ✅ | Multiple runs needed |
| Violin plot | ❌ | ✅ | ✅ | ≥5 runs recommended |
| Statistical summary | ❌ | ✅ | ✅ | Multiple runs needed |
| Convergence uncertainty | ❌ | ✅ | ✅ | Multiple runs needed |
| Fitness landscape 2D | ✅ | ❌ | ❌ | `DIMENSIONS = 2` |
| Parallel coordinates | 🚧 | 🚧 | 🚧 | Not implemented yet |
| Population diversity | 🚧 | 🚧 | 🚧 | Requires population history |
| Pareto front 2D | 🚧 | 🚧 | 🚧 | Multi-objective only |
| Pareto front 3D | 🚧 | 🚧 | 🚧 | Multi-objective only |
| Hypervolume progress | 🚧 | 🚧 | 🚧 | Multi-objective only |
| IGD progress | 🚧 | 🚧 | 🚧 | Multi-objective only |

**Legend:**
- ✅ Fully implemented
- ❌ Not applicable for this mode
- 🚧 Available in `visualization.py` but not yet integrated into experiments

## Current Status (v0.3.1)

### What Works Now ✅
- **Single run**: 4-5 plots (5 if 2D problem)
- **Multiple runs**: 5 plots showing statistical analysis
- **Algorithm comparison**: Combined convergence curves
- **Automatic CSV export**: All data saved alongside plots
- **Error handling**: Graceful failures with informative messages

### What's Coming Next 🚀
See `ROADMAP_v1.0.0.md` for:
- v0.4.0: Population diversity tracking
- v0.5.0: Multi-objective optimization support
- v0.6.0: Interactive HTML dashboards
- v1.0.0: Complete visualization suite

## Usage Examples

### Example 1: Quick Single Run (Basic Plots)
```python
VISUALIZATION_CONFIG = 'basic'
EXPERIMENT_MODE = 'single'
```
Output: 2 plots (convergence + solution parameters)

### Example 2: Research Paper Quality (All Plots)
```python
VISUALIZATION_CONFIG = 'all'
EXPERIMENT_MODE = 'multiple'
NUM_RUNS = 30
```
Output: 5 plots + statistical CSVs

### Example 3: 2D Landscape Visualization
```python
DIMENSIONS = 2
VISUALIZATION_CONFIG = 'all'
EXPERIMENT_MODE = 'single'
```
Output: 5 plots including fitness landscape

### Example 4: Disable All Plots (Data Only)
```python
VISUALIZATION_CONFIG = 'none'
```
Output: CSV files only, no plots

## Output Structure

```
experimental/
└── YYYYMMDD_HHMMSS/
    ├── *.csv              # Experiment data
    └── *.png              # Visualization plots
```

## Troubleshooting

### "Only getting convergence.png"
**Old behavior (v0.3.1 early)**: Only basic plots implemented
**Fixed in v0.3.1+**: Enhanced visualization system with 4-5 plots per single run

### "Plot X failed with error Y"
The system includes try-except blocks for graceful degradation. Check console output:
- ✓ Success messages show generated plots
- ✗ Error messages explain why a plot couldn't be generated

### "Want more plots"
Contributing new plot types:
1. Add function to `pyrade/visualization.py`
2. Add config flag to `VISUALIZATION_CONFIG` dict
3. Add generation code to appropriate experiment function
4. Submit PR to dev/v0.3.1

## Best Practices

1. **Use presets first**: `'all'`, `'basic'`, `'research'` cover most needs
2. **Multiple runs for statistics**: Use ≥30 runs for robust statistical plots
3. **2D problems for landscapes**: Only works with `DIMENSIONS = 2`
4. **Check console output**: Look for ✓/✗ messages during generation
5. **CSV + plots together**: Always save both for reproducibility

## Next Steps

- See `ROADMAP_v1.0.0.md` for upcoming visualization features
- Check `examples/` folder for complete experiment setups
- Read `pyrade/visualization.py` docstrings for technical details

---
**PyRADE v0.3.1** | Updated: 2025-12-01
