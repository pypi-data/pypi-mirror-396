"""
PyRADE - Multiple Runs Example

Run 30 independent experiments and get statistical analysis.
"""

from pyrade import DErand1bin
from pyrade.benchmarks import rastrigin
from pyrade.runner import run_multiple

# Run 30 independent experiments
fitness, histories = run_multiple(
    algorithm=DErand1bin,
    benchmark=rastrigin,
    dimensions=30,
    bounds=(-5.12, 5.12),
    pop_size=50,
    max_iter=1000,
    num_runs=30,
    viz_config='research'  # Generate research-quality plots
)

print(f"\nBest across all runs: {fitness.min():.6e}")
print(f"Mean ± Std: {fitness.mean():.6e} ± {fitness.std():.6e}")
