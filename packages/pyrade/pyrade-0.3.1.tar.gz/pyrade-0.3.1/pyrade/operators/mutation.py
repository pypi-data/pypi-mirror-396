"""
Mutation strategies for Differential Evolution.

This module provides various mutation strategies with fully vectorized
implementations for high performance.
"""

from abc import ABC, abstractmethod
import numpy as np


class MutationStrategy(ABC):
    """
    Abstract base class for mutation strategies.
    
    All mutation strategies should inherit from this class and implement
    the apply() method.
    """
    
    @abstractmethod
    def apply(self, population, fitness, best_idx, target_indices):
        """
        Apply mutation to generate mutant vectors.
        
        Parameters
        ----------
        population : ndarray, shape (pop_size, dim)
            Current population
        fitness : ndarray, shape (pop_size,)
            Fitness values
        best_idx : int
            Index of best individual
        target_indices : ndarray, shape (pop_size,)
            Indices being mutated
            
        Returns
        -------
        mutants : ndarray, shape (pop_size, dim)
            Mutant vectors
        """
        pass


class DErand1(MutationStrategy):
    """
    DE/rand/1: v = x_r1 + F * (x_r2 - x_r3)
    
    Most common DE mutation strategy. Selects three random distinct
    individuals and creates mutant from their differences.
    
    Parameters
    ----------
    F : float, default=0.8
        Mutation factor (differential weight)
    
    Notes
    -----
    This is the most widely used mutation strategy, providing a good
    balance between exploration and exploitation.
    """
    
    def __init__(self, F=0.8):
        if not 0 <= F <= 2:
            raise ValueError("F must be in [0, 2]")
        self.F = F
    
    def apply(self, population, fitness, best_idx, target_indices):
        """Apply DE/rand/1 mutation (fully vectorized)."""
        pop_size = len(population)
        
        # Vectorized: select random indices for entire population
        r1 = np.random.randint(0, pop_size, pop_size)
        r2 = np.random.randint(0, pop_size, pop_size)
        r3 = np.random.randint(0, pop_size, pop_size)
        
        # Ensure all indices are distinct
        mask = (r1 == target_indices) | (r2 == target_indices) | (r3 == target_indices)
        mask |= (r1 == r2) | (r1 == r3) | (r2 == r3)
        
        max_attempts = 100
        attempt = 0
        while np.any(mask) and attempt < max_attempts:
            r1[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r2[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r3[mask] = np.random.randint(0, pop_size, np.sum(mask))
            mask = (r1 == target_indices) | (r2 == target_indices) | (r3 == target_indices)
            mask |= (r1 == r2) | (r1 == r3) | (r2 == r3)
            attempt += 1
        
        # Vectorized mutation
        mutants = population[r1] + self.F * (population[r2] - population[r3])
        return mutants


class DEbest1(MutationStrategy):
    """
    DE/best/1: v = x_best + F * (x_r1 - x_r2)
    
    Exploitative strategy using best individual as base vector.
    Converges faster but may get stuck in local optima.
    
    Parameters
    ----------
    F : float, default=0.8
        Mutation factor (differential weight)
    
    Notes
    -----
    More exploitative than DE/rand/1. Good for unimodal functions
    but may converge prematurely on multimodal problems.
    """
    
    def __init__(self, F=0.8):
        if not 0 <= F <= 2:
            raise ValueError("F must be in [0, 2]")
        self.F = F
    
    def apply(self, population, fitness, best_idx, target_indices):
        """Apply DE/best/1 mutation (fully vectorized)."""
        pop_size = len(population)
        
        # Select two random distinct individuals
        r1 = np.random.randint(0, pop_size, pop_size)
        r2 = np.random.randint(0, pop_size, pop_size)
        
        # Ensure distinct from each other and from target
        mask = (r1 == target_indices) | (r2 == target_indices) | (r1 == r2)
        
        max_attempts = 100
        attempt = 0
        while np.any(mask) and attempt < max_attempts:
            r1[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r2[mask] = np.random.randint(0, pop_size, np.sum(mask))
            mask = (r1 == target_indices) | (r2 == target_indices) | (r1 == r2)
            attempt += 1
        
        # Vectorized mutation using best individual
        best_vector = population[best_idx]
        mutants = best_vector + self.F * (population[r1] - population[r2])
        return mutants


class DEcurrentToBest1(MutationStrategy):
    """
    DE/current-to-best/1: v = x_i + F * (x_best - x_i) + F * (x_r1 - x_r2)
    
    Balances exploration and exploitation by combining current individual
    with best and random difference vectors.
    
    Parameters
    ----------
    F : float, default=0.8
        Mutation factor (differential weight)
    
    Notes
    -----
    This strategy provides a good balance between DE/rand/1 and DE/best/1,
    often performing well on a wide range of problems.
    """
    
    def __init__(self, F=0.8):
        if not 0 <= F <= 2:
            raise ValueError("F must be in [0, 2]")
        self.F = F
    
    def apply(self, population, fitness, best_idx, target_indices):
        """Apply DE/current-to-best/1 mutation (fully vectorized)."""
        pop_size = len(population)
        
        # Select two random distinct individuals
        r1 = np.random.randint(0, pop_size, pop_size)
        r2 = np.random.randint(0, pop_size, pop_size)
        
        # Ensure distinct
        mask = (r1 == target_indices) | (r2 == target_indices) | (r1 == r2)
        
        max_attempts = 100
        attempt = 0
        while np.any(mask) and attempt < max_attempts:
            r1[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r2[mask] = np.random.randint(0, pop_size, np.sum(mask))
            mask = (r1 == target_indices) | (r2 == target_indices) | (r1 == r2)
            attempt += 1
        
        # Vectorized mutation
        best_vector = population[best_idx]
        current_vectors = population[target_indices]
        mutants = (
            current_vectors +
            self.F * (best_vector - current_vectors) +
            self.F * (population[r1] - population[r2])
        )
        return mutants


class DErand2(MutationStrategy):
    """
    DE/rand/2: v = x_r1 + F * (x_r2 - x_r3) + F * (x_r4 - x_r5)
    
    More exploratory strategy using two difference vectors.
    Provides greater diversity but may converge slower.
    
    Parameters
    ----------
    F : float, default=0.8
        Mutation factor (differential weight)
    
    Notes
    -----
    Uses more difference vectors for increased exploration.
    Good for highly multimodal problems but requires larger populations.
    """
    
    def __init__(self, F=0.8):
        if not 0 <= F <= 2:
            raise ValueError("F must be in [0, 2]")
        self.F = F
    
    def apply(self, population, fitness, best_idx, target_indices):
        """Apply DE/rand/2 mutation (fully vectorized)."""
        pop_size = len(population)
        
        # Select five random distinct individuals
        r1 = np.random.randint(0, pop_size, pop_size)
        r2 = np.random.randint(0, pop_size, pop_size)
        r3 = np.random.randint(0, pop_size, pop_size)
        r4 = np.random.randint(0, pop_size, pop_size)
        r5 = np.random.randint(0, pop_size, pop_size)
        
        # Ensure all indices are distinct
        mask = (r1 == target_indices) | (r2 == target_indices) | (r3 == target_indices)
        mask |= (r4 == target_indices) | (r5 == target_indices)
        mask |= (r1 == r2) | (r1 == r3) | (r1 == r4) | (r1 == r5)
        mask |= (r2 == r3) | (r2 == r4) | (r2 == r5)
        mask |= (r3 == r4) | (r3 == r5)
        mask |= (r4 == r5)
        
        max_attempts = 100
        attempt = 0
        while np.any(mask) and attempt < max_attempts:
            r1[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r2[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r3[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r4[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r5[mask] = np.random.randint(0, pop_size, np.sum(mask))
            
            mask = (r1 == target_indices) | (r2 == target_indices) | (r3 == target_indices)
            mask |= (r4 == target_indices) | (r5 == target_indices)
            mask |= (r1 == r2) | (r1 == r3) | (r1 == r4) | (r1 == r5)
            mask |= (r2 == r3) | (r2 == r4) | (r2 == r5)
            mask |= (r3 == r4) | (r3 == r5)
            mask |= (r4 == r5)
            attempt += 1
        
        # Vectorized mutation with two difference vectors
        mutants = (
            population[r1] +
            self.F * (population[r2] - population[r3]) +
            self.F * (population[r4] - population[r5])
        )
        return mutants


class DEbest2(MutationStrategy):
    """
    DE/best/2: v = x_best + F * (x_r1 - x_r2) + F * (x_r3 - x_r4)
    
    Highly exploitative strategy using best individual as base with
    two difference vectors. Fast convergence but risk of premature convergence.
    
    Parameters
    ----------
    F : float, default=0.8
        Mutation factor (differential weight)
    
    Notes
    -----
    More aggressive than DE/best/1. Good for unimodal functions
    but requires careful parameter tuning for multimodal problems.
    """
    
    def __init__(self, F=0.8):
        if not 0 <= F <= 2:
            raise ValueError("F must be in [0, 2]")
        self.F = F
    
    def apply(self, population, fitness, best_idx, target_indices):
        """Apply DE/best/2 mutation (fully vectorized)."""
        pop_size = len(population)
        
        # Select four random distinct individuals
        r1 = np.random.randint(0, pop_size, pop_size)
        r2 = np.random.randint(0, pop_size, pop_size)
        r3 = np.random.randint(0, pop_size, pop_size)
        r4 = np.random.randint(0, pop_size, pop_size)
        
        # Ensure all indices are distinct
        mask = (r1 == target_indices) | (r2 == target_indices) 
        mask |= (r3 == target_indices) | (r4 == target_indices)
        mask |= (r1 == r2) | (r1 == r3) | (r1 == r4)
        mask |= (r2 == r3) | (r2 == r4)
        mask |= (r3 == r4)
        
        max_attempts = 100
        attempt = 0
        while np.any(mask) and attempt < max_attempts:
            r1[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r2[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r3[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r4[mask] = np.random.randint(0, pop_size, np.sum(mask))
            
            mask = (r1 == target_indices) | (r2 == target_indices)
            mask |= (r3 == target_indices) | (r4 == target_indices)
            mask |= (r1 == r2) | (r1 == r3) | (r1 == r4)
            mask |= (r2 == r3) | (r2 == r4)
            mask |= (r3 == r4)
            attempt += 1
        
        # Vectorized mutation using best individual with two difference vectors
        best_vector = population[best_idx]
        mutants = (
            best_vector +
            self.F * (population[r1] - population[r2]) +
            self.F * (population[r3] - population[r4])
        )
        return mutants


class DEcurrentToRand1(MutationStrategy):
    """
    DE/current-to-rand/1: v = x_i + K * (x_r1 - x_i) + F * (x_r2 - x_r3)
    
    Combines current vector with random vector plus difference vector.
    More exploratory than current-to-best.
    
    Parameters
    ----------
    F : float, default=0.8
        Mutation factor for difference vector
    K : float, default=0.5
        Weight for current-to-random direction
    
    Notes
    -----
    Provides diversity through random direction. Good balance between
    exploration and maintaining population structure.
    """
    
    def __init__(self, F=0.8, K=0.5):
        if not 0 <= F <= 2:
            raise ValueError("F must be in [0, 2]")
        if not 0 <= K <= 2:
            raise ValueError("K must be in [0, 2]")
        self.F = F
        self.K = K
    
    def apply(self, population, fitness, best_idx, target_indices):
        """Apply DE/current-to-rand/1 mutation (fully vectorized)."""
        pop_size = len(population)
        
        # Select three random distinct individuals
        r1 = np.random.randint(0, pop_size, pop_size)
        r2 = np.random.randint(0, pop_size, pop_size)
        r3 = np.random.randint(0, pop_size, pop_size)
        
        # Ensure all indices are distinct
        mask = (r1 == target_indices) | (r2 == target_indices) | (r3 == target_indices)
        mask |= (r1 == r2) | (r1 == r3) | (r2 == r3)
        
        max_attempts = 100
        attempt = 0
        while np.any(mask) and attempt < max_attempts:
            r1[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r2[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r3[mask] = np.random.randint(0, pop_size, np.sum(mask))
            mask = (r1 == target_indices) | (r2 == target_indices) | (r3 == target_indices)
            mask |= (r1 == r2) | (r1 == r3) | (r2 == r3)
            attempt += 1
        
        # Vectorized mutation
        current_vectors = population[target_indices]
        mutants = (
            current_vectors +
            self.K * (population[r1] - current_vectors) +
            self.F * (population[r2] - population[r3])
        )
        return mutants


class DERandToBest1(MutationStrategy):
    """
    DE/rand-to-best/1: v = x_r1 + F * (x_best - x_r1) + F * (x_r2 - x_r3)
    
    Direction from random vector toward best, plus random difference.
    Balances exploration from random base with exploitation toward best.
    
    Parameters
    ----------
    F : float, default=0.8
        Mutation factor (differential weight)
    
    Notes
    -----
    Less greedy than DE/best/1 but still directed toward best solution.
    Good for problems where premature convergence is a concern.
    """
    
    def __init__(self, F=0.8):
        if not 0 <= F <= 2:
            raise ValueError("F must be in [0, 2]")
        self.F = F
    
    def apply(self, population, fitness, best_idx, target_indices):
        """Apply DE/rand-to-best/1 mutation (fully vectorized)."""
        pop_size = len(population)
        
        # Select three random distinct individuals
        r1 = np.random.randint(0, pop_size, pop_size)
        r2 = np.random.randint(0, pop_size, pop_size)
        r3 = np.random.randint(0, pop_size, pop_size)
        
        # Ensure all indices are distinct
        mask = (r1 == target_indices) | (r2 == target_indices) | (r3 == target_indices)
        mask |= (r1 == r2) | (r1 == r3) | (r2 == r3)
        
        max_attempts = 100
        attempt = 0
        while np.any(mask) and attempt < max_attempts:
            r1[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r2[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r3[mask] = np.random.randint(0, pop_size, np.sum(mask))
            mask = (r1 == target_indices) | (r2 == target_indices) | (r3 == target_indices)
            mask |= (r1 == r2) | (r1 == r3) | (r2 == r3)
            attempt += 1
        
        # Vectorized mutation: direction from random to best plus difference
        best_vector = population[best_idx]
        mutants = (
            population[r1] +
            self.F * (best_vector - population[r1]) +
            self.F * (population[r2] - population[r3])
        )
        return mutants


class DErand1EitherOr(MutationStrategy):
    """
    DE/rand/1/either-or: v = x_r1 + F_i * (x_r2 - x_r3)
    
    Uses probabilistic choice of scaling factor F_i which is either
    F or 0.5*F based on probability p_F (typically 0.5).
    
    Reference:
        Price, K. V., Storn, R. M., & Lampinen, J. A. (2006).
        Differential Evolution: A Practical Approach to Global Optimization.
        Springer Science & Business Media.
    
    Parameters
    ----------
    F : float, default=0.8
        Mutation factor (differential weight)
    p_F : float, default=0.5
        Probability of using full F (vs 0.5*F)
    
    Notes
    -----
    This strategy adds randomness in the scaling factor which can
    help maintain diversity. Each difference vector independently
    chooses between F and 0.5*F.
    """
    
    def __init__(self, F=0.8, p_F=0.5):
        if not 0 <= F <= 2:
            raise ValueError("F must be in [0, 2]")
        if not 0 <= p_F <= 1:
            raise ValueError("p_F must be in [0, 1]")
        self.F = F
        self.p_F = p_F
    
    def apply(self, population, fitness, best_idx, target_indices):
        """Apply DE/rand/1/either-or mutation (fully vectorized)."""
        pop_size = len(population)
        
        # Vectorized: select random indices for entire population
        r1 = np.random.randint(0, pop_size, pop_size)
        r2 = np.random.randint(0, pop_size, pop_size)
        r3 = np.random.randint(0, pop_size, pop_size)
        
        # Ensure all indices are distinct
        mask = (r1 == target_indices) | (r2 == target_indices) | (r3 == target_indices)
        mask |= (r1 == r2) | (r1 == r3) | (r2 == r3)
        
        max_attempts = 100
        attempt = 0
        while np.any(mask) and attempt < max_attempts:
            r1[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r2[mask] = np.random.randint(0, pop_size, np.sum(mask))
            r3[mask] = np.random.randint(0, pop_size, np.sum(mask))
            mask = (r1 == target_indices) | (r2 == target_indices) | (r3 == target_indices)
            mask |= (r1 == r2) | (r1 == r3) | (r2 == r3)
            attempt += 1
        
        # Probabilistic choice of F: either F or 0.5*F
        F_i = np.where(np.random.rand(pop_size) < self.p_F, self.F, 0.5 * self.F)
        
        # Vectorized mutation with either-or F
        mutants = population[r1] + F_i[:, np.newaxis] * (population[r2] - population[r3])
        return mutants
