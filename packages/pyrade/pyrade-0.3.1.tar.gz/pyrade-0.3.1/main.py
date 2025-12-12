"""
PyRADE - Simple Experiment Interface

Just set your parameters and run! All the complex code is now in pyrade/runner.py

Quick Start:
    python main.py

Or import and use as functions:
    from main import run_experiment, compare_algorithms
"""

from pyrade import DErand1bin, DEbest1bin, DEcurrentToBest1bin
from pyrade.benchmarks import sphere, rosenbrock, rastrigin, ackley, schwefel
from pyrade.benchmarks import get_benchmark, list_benchmarks
from pyrade.runner import run_experiment, compare_algorithms


# ============================================================================
# EXPERIMENT CONFIGURATION - Just set these parameters!
# ============================================================================

# Select Algorithm (uncomment one or add your own)
ALGORITHM = DErand1bin
# ALGORITHM = DEbest1bin
# ALGORITHM = DEcurrentToBest1bin
# ALGORITHM = DErand2bin
# ALGORITHM = DEbest2bin
# ALGORITHM = DErand1exp
# ALGORITHM = jDE  # Adaptive algorithm

# Select Benchmark Function 
BENCHMARK_FUNC = sphere
# BENCHMARK_FUNC = rosenbrock
# BENCHMARK_FUNC = rastrigin
# BENCHMARK_FUNC = ackley
# BENCHMARK_FUNC = schwefel

# Or use dynamic selection:
# BENCHMARK_FUNC = get_benchmark('rastrigin')

# Or CEC2017 functions:
# from pyrade.benchmarks import CEC2017Function
# BENCHMARK_FUNC = CEC2017Function(func_num=5, dimensions=30)

# Problem Configuration
DIMENSIONS = 30
BOUNDS = (-100, 100)

# Algorithm Parameters
POPULATION_SIZE = 50
MAX_ITERATIONS = 1000
MUTATION_F = 0.8
CROSSOVER_CR = 0.9
RANDOM_SEED = 42

# Experiment Settings
NUM_RUNS = 10  # 1 for single run, >1 for statistics
OUTPUT_DIR = "experimental"

# Visualization
VISUALIZATION_PRESET = 'all'  # Options: 'all', 'basic', 'research', 'none'


# ============================================================================
# RUN EXPERIMENTS
# ============================================================================

if __name__ == "__main__":
    print("\nPyRADE Experiment Runner")
    print("=" * 80)
    print("\nSelect experiment type:")
    print("1. Single run")
    print("2. Multiple runs (with statistics)")
    print("3. Algorithm comparison")
    print("\n" + "=" * 80)
    
    choice = input("\nEnter choice (1/2/3) or press Enter for single run: ").strip()
    
    if choice == "2":
        # Multiple runs
        stats, all_results = run_experiment(
            algorithm=ALGORITHM,
            benchmark=BENCHMARK_FUNC,
            dimensions=DIMENSIONS,
            bounds=BOUNDS,
            num_runs=NUM_RUNS,
            pop_size=POPULATION_SIZE,
            max_iter=MAX_ITERATIONS,
            F=MUTATION_F,
            CR=CROSSOVER_CR,
            seed=RANDOM_SEED,
            output_dir=OUTPUT_DIR,
            viz_preset=VISUALIZATION_PRESET
        )
        
    elif choice == "3":
        # Algorithm comparison
        algorithms_to_compare = [
            DErand1bin,
            DEbest1bin,
            DEcurrentToBest1bin
        ]
        
        results = compare_algorithms(
            algorithms=algorithms_to_compare,
            benchmark=BENCHMARK_FUNC,
            dimensions=DIMENSIONS,
            bounds=BOUNDS,
            num_runs=NUM_RUNS,
            pop_size=POPULATION_SIZE,
            max_iter=MAX_ITERATIONS,
            F=MUTATION_F,
            CR=CROSSOVER_CR,
            seed=RANDOM_SEED,
            output_dir=OUTPUT_DIR,
            viz_preset=VISUALIZATION_PRESET
        )
        
    else:
        # Single run
        result = run_experiment(
            algorithm=ALGORITHM,
            benchmark=BENCHMARK_FUNC,
            dimensions=DIMENSIONS,
            bounds=BOUNDS,
            num_runs=1,
            pop_size=POPULATION_SIZE,
            max_iter=MAX_ITERATIONS,
            F=MUTATION_F,
            CR=CROSSOVER_CR,
            seed=RANDOM_SEED,
            output_dir=OUTPUT_DIR,
            viz_preset=VISUALIZATION_PRESET
        )
