"""
Custom strategy example for PyRADE.

This example demonstrates how to create and use custom
mutation, crossover, and selection strategies.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from pyrade import DifferentialEvolution
from pyrade.operators import (
    MutationStrategy,
    CrossoverStrategy,
    SelectionStrategy,
    DErand1,
    DEbest1,
    BinomialCrossover,
    GreedySelection,
)
from pyrade.benchmarks import Rastrigin, Ackley


class AdaptiveMutation(MutationStrategy):
    """
    Custom adaptive mutation strategy.
    
    Adjusts mutation factor F based on iteration progress.
    F decreases linearly from F_max to F_min.
    """
    
    def __init__(self, F_max=0.9, F_min=0.4):
        self.F_max = F_max
        self.F_min = F_min
        self.F = F_max
        self.iteration = 0
        self.max_iterations = 1000
    
    def set_iteration(self, iteration, max_iterations):
        """Update current iteration for adaptive behavior."""
        self.iteration = iteration
        self.max_iterations = max_iterations
        # Linear decay
        progress = iteration / max_iterations
        self.F = self.F_max - progress * (self.F_max - self.F_min)
    
    def apply(self, population, fitness, best_idx, target_indices):
        """Apply DE/rand/1 with adaptive F."""
        pop_size = len(population)
        
        # Select random indices (same as DErand1)
        r1 = np.random.randint(0, pop_size, pop_size)
        r2 = np.random.randint(0, pop_size, pop_size)
        r3 = np.random.randint(0, pop_size, pop_size)
        
        # Ensure distinct indices
        mask = (r1 == target_indices) | (r2 == target_indices) | (r3 == target_indices)
        mask |= (r1 == r2) | (r1 == r3) | (r2 == r3)
        
        attempt = 0
        while np.any(mask) and attempt < 100:
            r1[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r2[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r3[mask] = np.random.randint(0, pop_size, np.sum(mask))
            mask = (r1 == target_indices) | (r2 == target_indices) | (r3 == target_indices)
            mask |= (r1 == r2) | (r1 == r3) | (r2 == r3)
            attempt += 1
        
        # Vectorized mutation with current F
        mutants = population[r1] + self.F * (population[r2] - population[r3])
        return mutants


class HybridMutation(MutationStrategy):
    """
    Hybrid mutation combining DE/rand/1 and DE/best/1.
    
    Uses DE/rand/1 with probability p, otherwise DE/best/1.
    """
    
    def __init__(self, F=0.8, p_rand=0.5):
        self.F = F
        self.p_rand = p_rand
        self.rand_strategy = DErand1(F=F)
        self.best_strategy = DEbest1(F=F)
    
    def apply(self, population, fitness, best_idx, target_indices):
        """Apply hybrid mutation."""
        pop_size = len(population)
        
        # Generate mutants from both strategies
        mutants_rand = self.rand_strategy.apply(
            population, fitness, best_idx, target_indices
        )
        mutants_best = self.best_strategy.apply(
            population, fitness, best_idx, target_indices
        )
        
        # Randomly choose which to use for each individual
        use_rand = np.random.rand(pop_size) < self.p_rand
        mutants = np.where(use_rand[:, np.newaxis], mutants_rand, mutants_best)
        
        return mutants


class DitherCrossover(CrossoverStrategy):
    """
    Crossover with dithered CR (randomized per individual).
    
    Instead of using fixed CR, randomly samples CR from a range
    for each individual.
    """
    
    def __init__(self, CR_mean=0.9, CR_std=0.1):
        self.CR_mean = CR_mean
        self.CR_std = CR_std
    
    def apply(self, population, mutants):
        """Apply binomial crossover with dithered CR."""
        pop_size, dim = population.shape
        
        # Generate random CR for each individual
        CR_values = np.random.normal(self.CR_mean, self.CR_std, pop_size)
        CR_values = np.clip(CR_values, 0, 1)
        
        # Apply crossover with individual CR values
        trials = population.copy()
        for i in range(pop_size):
            crossover_mask = np.random.rand(dim) <= CR_values[i]
            j_rand = np.random.randint(0, dim)
            crossover_mask[j_rand] = True
            trials[i] = np.where(crossover_mask, mutants[i], population[i])
        
        return trials


def example_adaptive_mutation():
    """Example using adaptive mutation strategy."""
    print("="*70)
    print("Example 1: Adaptive Mutation Strategy")
    print("="*70)
    
    func = Rastrigin(dim=20)
    
    # Note: The adaptive mutation would need integration with the main algorithm
    # to update iteration count. For now, we use it with fixed F.
    mutation = AdaptiveMutation(F_max=0.9, F_min=0.4)
    
    optimizer = DifferentialEvolution(
        objective_func=func,
        bounds=func.get_bounds_array(),
        mutation=mutation,
        pop_size=100,
        max_iter=300,
        verbose=True,
        seed=42
    )
    
    result = optimizer.optimize()
    
    print(f"\nFinal fitness: {result['best_fitness']:.6e}")
    print(f"Error from optimum: {abs(result['best_fitness'] - func.optimum):.6e}")
    print()


def example_hybrid_mutation():
    """Example using hybrid mutation strategy."""
    print("="*70)
    print("Example 2: Hybrid Mutation Strategy")
    print("="*70)
    
    func = Ackley(dim=20)
    
    # Combine exploratory (rand/1) and exploitative (best/1) strategies
    mutation = HybridMutation(F=0.8, p_rand=0.7)
    
    optimizer = DifferentialEvolution(
        objective_func=func,
        bounds=func.get_bounds_array(),
        mutation=mutation,
        pop_size=100,
        max_iter=300,
        verbose=True,
        seed=42
    )
    
    result = optimizer.optimize()
    
    print(f"\nFinal fitness: {result['best_fitness']:.6e}")
    print(f"Error from optimum: {abs(result['best_fitness'] - func.optimum):.6e}")
    print()


def example_dither_crossover():
    """Example using dithered crossover strategy."""
    print("="*70)
    print("Example 3: Dithered Crossover Strategy")
    print("="*70)
    
    func = Rastrigin(dim=20)
    
    # Use randomized CR for diversity
    crossover = DitherCrossover(CR_mean=0.9, CR_std=0.1)
    
    optimizer = DifferentialEvolution(
        objective_func=func,
        bounds=func.get_bounds_array(),
        mutation=DErand1(F=0.8),
        crossover=crossover,
        pop_size=100,
        max_iter=300,
        verbose=True,
        seed=42
    )
    
    result = optimizer.optimize()
    
    print(f"\nFinal fitness: {result['best_fitness']:.6e}")
    print(f"Error from optimum: {abs(result['best_fitness'] - func.optimum):.6e}")
    print()


def example_strategy_comparison():
    """Compare different mutation strategies."""
    print("="*70)
    print("Example 4: Strategy Comparison")
    print("="*70)
    
    func = Rastrigin(dim=15)
    
    strategies = [
        ("DE/rand/1", DErand1(F=0.8)),
        ("DE/best/1", DEbest1(F=0.8)),
        ("Hybrid", HybridMutation(F=0.8, p_rand=0.5)),
    ]
    
    print(f"\nComparing strategies on {func.__class__.__name__} (dim={func.dim}):")
    print(f"{'Strategy':<20} {'Final Fitness':<20} {'Time (s)':<10}")
    print("-" * 52)
    
    for name, mutation in strategies:
        optimizer = DifferentialEvolution(
            objective_func=func,
            bounds=func.get_bounds_array(),
            mutation=mutation,
            crossover=BinomialCrossover(CR=0.9),
            selection=GreedySelection(),
            pop_size=80,
            max_iter=200,
            verbose=False,
            seed=42
        )
        
        result = optimizer.optimize()
        
        print(f"{name:<20} {result['best_fitness']:<20.6e} {result['time']:<10.3f}")
    
    print()


def example_custom_selection():
    """Example with custom selection strategy."""
    print("="*70)
    print("Example 5: Custom Selection Strategy")
    print("="*70)
    
    class ElitistGreedySelection(SelectionStrategy):
        """Greedy selection with guaranteed elite preservation."""
        
        def __init__(self, elite_count=2):
            self.elite_count = elite_count
        
        def apply(self, population, fitness, trials, trial_fitness):
            # Standard greedy selection
            improved = trial_fitness < fitness
            new_population = population.copy()
            new_population[improved] = trials[improved]
            new_fitness = fitness.copy()
            new_fitness[improved] = trial_fitness[improved]
            
            # Force preserve top elites
            elite_indices = np.argsort(fitness)[:self.elite_count]
            for idx in elite_indices:
                if new_fitness[idx] > fitness[idx]:
                    new_population[idx] = population[idx]
                    new_fitness[idx] = fitness[idx]
            
            return new_population, new_fitness
    
    func = Ackley(dim=20)
    selection = ElitistGreedySelection(elite_count=3)
    
    optimizer = DifferentialEvolution(
        objective_func=func,
        bounds=func.get_bounds_array(),
        selection=selection,
        pop_size=100,
        max_iter=300,
        verbose=True,
        seed=42
    )
    
    result = optimizer.optimize()
    
    print(f"\nFinal fitness: {result['best_fitness']:.6e}")
    print()


if __name__ == "__main__":
    # Run all examples
    example_adaptive_mutation()
    example_hybrid_mutation()
    example_dither_crossover()
    example_strategy_comparison()
    example_custom_selection()
    
    print("="*70)
    print("All custom strategy examples completed!")
    print("="*70)
