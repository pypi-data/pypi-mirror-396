"""
PyRADE - Algorithm Comparison Example

Compare multiple DE variants on the same problem.
"""

from pyrade import DErand1bin, DEbest1bin, DEcurrentToBest1bin, DErand2bin
from pyrade.benchmarks import ackley
from pyrade.runner import compare_algorithms

# Compare 4 DE variants
results = compare_algorithms(
    algorithms=[DErand1bin, DEbest1bin, DEcurrentToBest1bin, DErand2bin],
    benchmark=ackley,
    dimensions=30,
    bounds=(-32.768, 32.768),
    pop_size=50,
    max_iter=1000,
    num_runs=30,
    viz_config='all'
)

# Find best algorithm
best_algo = min(results.items(), key=lambda x: x[1].mean())
print(f"\nBest algorithm: {best_algo[0]}")
print(f"Mean fitness: {best_algo[1].mean():.6e}")
