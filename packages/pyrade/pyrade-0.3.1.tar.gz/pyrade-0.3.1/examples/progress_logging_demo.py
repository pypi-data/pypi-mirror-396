"""
Demo: Progress Bar and Logging Support in PyRADE v0.3.1

This example demonstrates the new features added in version 0.3.1:
- Progress bar support (tqdm integration)
- Logging support (Python logging module)
- Enhanced error messages and validation
- Type hints throughout codebase
"""

import numpy as np
import logging
from pyrade import DErand1bin
from pyrade.experiments import ExperimentManager

# Configure logging (optional - see different log levels)
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def sphere(x):
    """Simple sphere function for testing."""
    return np.sum(x**2)


def main():
    print("=" * 80)
    print("PyRADE v0.3.1 - Progress Bar and Logging Demo")
    print("=" * 80)
    
    # Example 1: Single optimization with progress bar
    print("\n1. Single Optimization with Progress Bar")
    print("-" * 80)
    
    optimizer = DErand1bin(
        objective_func=sphere,
        bounds=[(-100, 100)] * 10,  # 10-dimensional problem
        pop_size=50,
        max_iter=100,
        verbose=True,           # Print summary
        show_progress=True      # NEW: Show progress bar!
    )
    
    result = optimizer.optimize()
    print(f"\nBest fitness: {result['best_fitness']:.6e}")
    print(f"Time: {result['time']:.2f}s")
    
    # Example 2: ExperimentManager with progress bars
    print("\n\n2. ExperimentManager with Progress Bars")
    print("-" * 80)
    
    exp = ExperimentManager(
        benchmarks=['Sphere', 'Rastrigin'],
        dimensions=10,
        n_runs=5,  # Reduced for demo
        population_size=30,
        max_iterations=50,
        show_progress=True  # NEW: Show progress for both runs and benchmarks!
    )
    
    # Run experiments - you'll see progress bars for each benchmark
    results = exp.run_experiments(verbose=True)
    
    # Example 3: Demonstrating improved error messages
    print("\n\n3. Enhanced Error Messages")
    print("-" * 80)
    print("Trying invalid configurations to show improved error messages:\n")
    
    try:
        # Invalid pop_size
        optimizer = DErand1bin(
            objective_func=sphere,
            bounds=[(-100, 100)] * 10,
            pop_size=2  # Too small!
        )
    except ValueError as e:
        print(f"✓ Caught error with helpful message:\n  {e}\n")
    
    try:
        # Invalid bounds
        optimizer = DErand1bin(
            objective_func=sphere,
            bounds=(100, -100),  # Lower > Upper!
            pop_size=50
        )
    except Exception as e:
        print(f"✓ Caught error with helpful message:\n  {e}\n")
    
    # Example 4: Using logging at different levels
    print("\n4. Logging at Different Levels")
    print("-" * 80)
    print("Set logging level to DEBUG in the code above to see detailed logs!\n")
    
    # Run with DEBUG logging (uncomment the line below)
    # logging.getLogger('pyrade').setLevel(logging.DEBUG)
    
    optimizer = DErand1bin(
        objective_func=sphere,
        bounds=[(-10, 10)] * 5,
        pop_size=20,
        max_iter=20,
        verbose=False,
        show_progress=False
    )
    result = optimizer.optimize()
    
    print(f"Best fitness: {result['best_fitness']:.6e}")
    
    print("\n" + "=" * 80)
    print("Demo Complete!")
    print("=" * 80)
    print("\nNew features in v0.3.1:")
    print("  ✓ Progress bars (show_progress=True)")
    print("  ✓ Logging support (use Python's logging module)")
    print("  ✓ Enhanced error messages")
    print("  ✓ Type hints for better IDE support")
    print("\nTry installing tqdm if you don't see progress bars:")
    print("  pip install tqdm")
    print("=" * 80)


if __name__ == '__main__':
    main()
