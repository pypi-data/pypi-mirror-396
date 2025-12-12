"""
PyRADE - Minimal Example

The absolute simplest way to run an optimization experiment.
"""

from pyrade import DErand1bin
from pyrade.benchmarks import sphere
from pyrade.runner import run_single

# Run optimization
result = run_single(
    algorithm=DErand1bin,
    benchmark=sphere,
    dimensions=30,
    bounds=(-100, 100),
    pop_size=50,
    max_iter=1000,
    viz_config='all'  # 'all', 'basic', 'research', or 'none'
)

print(f"\nFinal result: {result['best_fitness']:.6e}")
