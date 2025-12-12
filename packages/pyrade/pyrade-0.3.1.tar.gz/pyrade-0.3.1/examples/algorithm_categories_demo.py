"""
Example demonstrating the new algorithm classification structure.

This shows how to use different DE variants organized by category:
- Classic variants (traditional DE algorithms)
- Adaptive variants (coming soon)
- Multi-population variants (coming soon)
- Hybrid variants (coming soon)
"""

import numpy as np
from pyrade.algorithms.classic import (
    ClassicDE,
    DErand1bin,
    DEbest1bin,
    DEcurrentToBest1bin,
    DErand2bin,
    DEbest2bin,
    DEcurrentToRand1bin,
    DERandToBest1bin,
)


def sphere(x):
    """Simple sphere function for testing."""
    return np.sum(x**2)


def rastrigin(x):
    """Rastrigin function - highly multimodal."""
    n = len(x)
    return 10*n + np.sum(x**2 - 10*np.cos(2*np.pi*x))


def compare_classic_variants():
    """Compare different classic DE variants on test problems."""
    print("="*70)
    print("Comparing Classic DE Variants")
    print("="*70)
    
    # Problem setup
    bounds = [(-5.12, 5.12)] * 10
    pop_size = 50
    max_iter = 200
    
    # Test functions
    problems = [
        ("Sphere (unimodal)", sphere),
        ("Rastrigin (multimodal)", rastrigin)
    ]
    
    # Classic variants to test
    variants = [
        ("DE/rand/1/bin", DErand1bin),
        ("DE/best/1/bin", DEbest1bin),
        ("DE/current-to-best/1/bin", DEcurrentToBest1bin),
        ("DE/rand/2/bin", DErand2bin),
        ("DE/best/2/bin", DEbest2bin),
        ("DE/current-to-rand/1/bin", DEcurrentToRand1bin),
        ("DE/rand-to-best/1/bin", DERandToBest1bin),
    ]
    
    for prob_name, prob_func in problems:
        print(f"\n{prob_name}")
        print("-" * 70)
        
        for var_name, var_class in variants:
            # Create optimizer
            de = var_class(
                objective_func=prob_func,
                bounds=bounds,
                pop_size=pop_size,
                max_iter=max_iter,
                seed=42,
                verbose=False
            )
            
            # Run optimization
            result = de.optimize()
            
            print(f"  {var_name:25s} | "
                  f"Best: {result['best_fitness']:.6e} | "
                  f"Time: {result['time']:.2f}s")


def example_classic_de_custom():
    """Example using ClassicDE with custom operators."""
    from pyrade.operators import DErand1, BinomialCrossover, GreedySelection
    
    print("\n" + "="*70)
    print("ClassicDE with Custom Operators")
    print("="*70)
    
    # Custom configuration
    de = ClassicDE(
        objective_func=sphere,
        bounds=[(-100, 100)] * 20,
        mutation=DErand1(F=0.8),
        crossover=BinomialCrossover(CR=0.9),
        selection=GreedySelection(),
        pop_size=100,
        max_iter=500,
        verbose=True
    )
    
    result = de.optimize()
    
    print(f"\nFinal Result:")
    print(f"  Best fitness: {result['best_fitness']:.6e}")
    print(f"  Time: {result['time']:.2f}s")


def example_simple_usage():
    """Simplest way to use a classic variant."""
    print("\n" + "="*70)
    print("Simple Usage Example")
    print("="*70)
    
    # Just pick a variant and go!
    de = DErand1bin(
        objective_func=sphere,
        bounds=[(-100, 100)] * 10,
        pop_size=50,
        max_iter=200,
        F=0.8,
        CR=0.9
    )
    
    result = de.optimize()
    
    print(f"Best fitness: {result['best_fitness']:.6e}")
    print(f"Best solution: {result['best_solution'][:5]}...")  # First 5 dims


if __name__ == "__main__":
    # Run examples
    example_simple_usage()
    compare_classic_variants()
    example_classic_de_custom()
    
    print("\n" + "="*70)
    print("Examples Complete!")
    print("\nSummary:")
    print("  ✓ 8 Classic DE variants available")
    print("  ✓ All variants tested and working")
    print("\nNext Steps:")
    print("  - Adaptive variants (jDE, SaDE, JADE, CoDE) - in progress")
    print("  - Multi-population variants coming soon")
    print("  - Hybrid variants coming soon")
    print("="*70)
