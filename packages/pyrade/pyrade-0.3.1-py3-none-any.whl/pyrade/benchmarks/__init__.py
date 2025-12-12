"""
Benchmark functions module for testing optimization algorithms.

This module provides two ways to use benchmark functions:

1. Class-based (with metadata): Sphere(dim=30)
2. Function-based (simple):     sphere(x)
3. Dynamic access:               get_benchmark('sphere')

Examples
--------
# Class-based (recommended for full features)
>>> from pyrade.benchmarks import Sphere
>>> func = Sphere(dim=20)
>>> print(func.bounds, func.optimum)
>>> result = func(x)

# Function-based (quick and simple)
>>> from pyrade.benchmarks import sphere
>>> result = sphere(x)

# Dynamic access by name
>>> from pyrade.benchmarks import get_benchmark
>>> func = get_benchmark('rastrigin', dim=30)
>>> result = func(x)
"""

from pyrade.benchmarks.functions import (
    # Base class
    BenchmarkFunction,
    
    # Class-based benchmarks (with bounds and metadata)
    Sphere,
    Rastrigin,
    Rosenbrock,
    Ackley,
    Griewank,
    Schwefel,
    Levy,
    Michalewicz,
    Zakharov,
    Easom,
    StyblinskiTang,
    
    # Simple function wrappers
    sphere,
    rastrigin,
    rosenbrock,
    ackley,
    griewank,
    schwefel,
    levy,
    michalewicz,
    zakharov,
    easom,
    styblinskitang,
    
    # Utilities
    get_benchmark,
    list_benchmarks,
    BENCHMARK_REGISTRY,
)

# CEC2017 Competition Functions
from pyrade.benchmarks.cec2017 import CEC2017Function

__all__ = [
    # Base
    "BenchmarkFunction",
    
    # Classes
    "Sphere",
    "Rastrigin",
    "Rosenbrock",
    "Ackley",
    "Griewank",
    "Schwefel",
    "Levy",
    "Michalewicz",
    "Zakharov",
    "Easom",
    "StyblinskiTang",
    
    # Functions
    "sphere",
    "rastrigin",
    "rosenbrock",
    "ackley",
    "griewank",
    "schwefel",
    "levy",
    "michalewicz",
    "zakharov",
    "easom",
    "styblinskitang",
    
    # CEC2017
    "CEC2017Function",
    
    # Utilities
    "get_benchmark",
    "list_benchmarks",
    "BENCHMARK_REGISTRY",
]
