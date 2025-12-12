"""
Basic usage example for PyRADE.

This example demonstrates the simplest way to use the
DifferentialEvolution optimizer.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from pyrade import DifferentialEvolution
from pyrade.benchmarks import Sphere, Rastrigin, Rosenbrock, Ackley


def example_simple():
    """Simple example with default settings."""
    print("="*70)
    print("Example 1: Simple Sphere Function Optimization")
    print("="*70)
    
    # Define objective function
    def sphere(x):
        return np.sum(x**2)
    
    # Create optimizer with default settings
    optimizer = DifferentialEvolution(
        objective_func=sphere,
        bounds=[(-100, 100)] * 10,  # 10-dimensional problem
        pop_size=50,
        max_iter=200,
        verbose=True,
        seed=42
    )
    
    # Run optimization
    result = optimizer.optimize()
    
    # Display results
    print(f"\nBest solution: {result['best_solution']}")
    print(f"Best fitness: {result['best_fitness']:.6e}")
    print(f"Total time: {result['time']:.3f}s")
    print()


def example_benchmark_functions():
    """Example using benchmark functions."""
    print("="*70)
    print("Example 2: Benchmark Function Optimization")
    print("="*70)
    
    # Test on multiple benchmark functions
    benchmarks = [
        Sphere(dim=10),
        Rastrigin(dim=10),
        Rosenbrock(dim=10),
        Ackley(dim=10),
    ]
    
    for benchmark in benchmarks:
        print(f"\n{benchmark.__class__.__name__} Function:")
        print(f"  Global optimum: {benchmark.optimum}")
        
        optimizer = DifferentialEvolution(
            objective_func=benchmark,
            bounds=benchmark.get_bounds_array(),
            pop_size=50,
            max_iter=200,
            verbose=False,
            seed=42
        )
        
        result = optimizer.optimize()
        
        error = abs(result['best_fitness'] - benchmark.optimum)
        print(f"  Final fitness: {result['best_fitness']:.6e}")
        print(f"  Error from optimum: {error:.6e}")
        print(f"  Time: {result['time']:.3f}s")


def example_with_callback():
    """Example with custom callback function."""
    print("="*70)
    print("Example 3: Optimization with Callback")
    print("="*70)
    
    # Define callback to track progress
    improvements = []
    
    def progress_callback(iteration, best_fitness, best_solution):
        if iteration % 50 == 0:
            improvements.append((iteration, best_fitness))
            print(f"  Iteration {iteration}: fitness = {best_fitness:.6e}")
    
    # Optimize Rastrigin function
    func = Rastrigin(dim=20)
    
    optimizer = DifferentialEvolution(
        objective_func=func,
        bounds=func.get_bounds_array(),
        pop_size=100,
        max_iter=300,
        verbose=False,
        callback=progress_callback,
        seed=42
    )
    
    result = optimizer.optimize()
    
    print(f"\nFinal best fitness: {result['best_fitness']:.6e}")
    print(f"Number of callback invocations: {len(improvements)}")
    print()


def example_different_dimensions():
    """Example showing scalability across dimensions."""
    print("="*70)
    print("Example 4: Scalability Test")
    print("="*70)
    
    func_class = Sphere
    dimensions = [5, 10, 20, 30]
    
    print("\nTesting Sphere function across different dimensions:")
    print(f"{'Dim':<6} {'Fitness':<15} {'Time (s)':<10}")
    print("-" * 35)
    
    for dim in dimensions:
        func = func_class(dim=dim)
        
        optimizer = DifferentialEvolution(
            objective_func=func,
            bounds=func.get_bounds_array(),
            pop_size=50,
            max_iter=100,
            verbose=False,
            seed=42
        )
        
        result = optimizer.optimize()
        
        print(f"{dim:<6} {result['best_fitness']:<15.6e} {result['time']:<10.3f}")
    
    print()


def example_with_constraints():
    """Example with a constrained optimization problem."""
    print("="*70)
    print("Example 5: Constrained Optimization")
    print("="*70)
    
    # Define a simple constrained problem
    # Minimize: x^2 + y^2
    # Subject to: x + y >= 1
    
    def constrained_objective(x):
        # Penalty method for constraints
        penalty = 0
        
        # Constraint: x + y >= 1
        constraint_violation = max(0, 1 - (x[0] + x[1]))
        penalty = 1000 * constraint_violation**2
        
        # Objective
        objective = x[0]**2 + x[1]**2
        
        return objective + penalty
    
    optimizer = DifferentialEvolution(
        objective_func=constrained_objective,
        bounds=[(-5, 5), (-5, 5)],
        pop_size=50,
        max_iter=200,
        verbose=True,
        seed=42
    )
    
    result = optimizer.optimize()
    
    print(f"\nBest solution: x={result['best_solution'][0]:.4f}, y={result['best_solution'][1]:.4f}")
    print(f"Sum (should be ≥ 1): {np.sum(result['best_solution']):.4f}")
    print(f"Objective value: {result['best_fitness']:.6e}")
    print()


if __name__ == "__main__":
    # Run all examples
    example_simple()
    example_benchmark_functions()
    example_with_callback()
    example_different_dimensions()
    example_with_constraints()
    
    print("="*70)
    print("All examples completed successfully!")
    print("="*70)
