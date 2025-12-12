"""
PyRADE - Python Rapid Algorithm for Differential Evolution

A high-performance, modular Differential Evolution optimization package
with clean OOP architecture and aggressive vectorization.

Example usage:
-------------
>>> from pyrade import DifferentialEvolution
>>> from pyrade.operators import DErand1, BinomialCrossover
>>> 
>>> def sphere(x):
...     return sum(x**2)
>>> 
>>> optimizer = DifferentialEvolution(
...     objective_func=sphere,
...     bounds=(-100, 100),
...     mutation=DErand1(F=0.8),
...     crossover=BinomialCrossover(CR=0.9),
...     pop_size=50,
...     max_iter=1000
... )
>>> 
>>> result = optimizer.optimize()
>>> print(f"Best solution: {result['best_solution']}")
>>> print(f"Best fitness: {result['best_fitness']}")
"""

from pyrade.__version__ import __version__

__author__ = "PyRADE Contributors"

# Core components
from pyrade.core.algorithm import DifferentialEvolution
from pyrade.core.population import Population

# Visualization and experiments
from pyrade.visualization import (
    OptimizationVisualizer,
    calculate_hypervolume_2d,
    calculate_igd,
    is_pareto_efficient
)
from pyrade.experiments import ExperimentManager

# Algorithm variants - organized by category
from pyrade.algorithms.classic import (
    ClassicDE,
    DErand1bin,
    DEbest1bin,
    DEcurrentToBest1bin,
    DErand2bin,
    DEbest2bin,
    DEcurrentToRand1bin,
    DERandToBest1bin,
    DErand1exp,
    DErand1EitherOrBin,
)

# High-level experiment runners
from pyrade.runner import run_experiment, compare_algorithms

__all__ = [
    # Legacy/core (for backward compatibility)
    "DifferentialEvolution",
    "Population",
    
    # Visualization
    "OptimizationVisualizer",
    "ExperimentManager",
    "calculate_hypervolume_2d",
    "calculate_igd",
    "is_pareto_efficient",
    
    # Classic DE variants
    "ClassicDE",
    "DErand1bin",
    "DEbest1bin",
    "DEcurrentToBest1bin",
    "DErand2bin",
    "DEbest2bin",
    "DEcurrentToRand1bin",
    "DERandToBest1bin",
    "DErand1exp",
    "DErand1EitherOrBin",
    
    # High-level runners
    "run_single",
    "run_multiple",
    "compare_algorithms",
]
