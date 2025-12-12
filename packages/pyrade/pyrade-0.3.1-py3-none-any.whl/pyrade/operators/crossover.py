"""
Crossover strategies for Differential Evolution.

This module provides crossover strategies with fully vectorized
implementations for high performance.
"""

from abc import ABC, abstractmethod
import numpy as np


class CrossoverStrategy(ABC):
    """
    Abstract base class for crossover strategies.
    
    All crossover strategies should inherit from this class and implement
    the apply() method.
    """
    
    @abstractmethod
    def apply(self, population, mutants):
        """
        Apply crossover between population and mutants.
        
        Parameters
        ----------
        population : ndarray, shape (pop_size, dim)
            Target vectors
        mutants : ndarray, shape (pop_size, dim)
            Mutant vectors
            
        Returns
        -------
        trials : ndarray, shape (pop_size, dim)
            Trial vectors
        """
        pass


class BinomialCrossover(CrossoverStrategy):
    """
    Binomial crossover: u_ij = v_ij if rand() <= CR or j == j_rand, else x_ij
    
    Most common crossover in DE. Each dimension is independently crossed
    with probability CR.
    
    Parameters
    ----------
    CR : float, default=0.9
        Crossover probability (0 <= CR <= 1)
    
    Notes
    -----
    Higher CR values lead to more exploitation (more from mutant),
    lower CR values lead to more exploration (more from parent).
    At least one dimension is always crossed over to ensure the trial
    differs from the target.
    """
    
    def __init__(self, CR=0.9):
        if not 0 <= CR <= 1:
            raise ValueError("CR must be in [0, 1]")
        self.CR = CR
    
    def apply(self, population, mutants):
        """Apply binomial crossover (fully vectorized)."""
        pop_size, dim = population.shape
        
        # Vectorized: generate crossover mask for entire population
        crossover_mask = np.random.rand(pop_size, dim) <= self.CR
        
        # Ensure at least one dimension crosses over per individual
        j_rand = np.random.randint(0, dim, pop_size)
        crossover_mask[np.arange(pop_size), j_rand] = True
        
        # Vectorized crossover
        trials = np.where(crossover_mask, mutants, population)
        return trials


class ExponentialCrossover(CrossoverStrategy):
    """
    Exponential crossover: copies contiguous segment from mutant.
    
    Alternative to binomial crossover. Copies a contiguous segment
    of dimensions from the mutant vector.
    
    Parameters
    ----------
    CR : float, default=0.9
        Crossover probability (0 <= CR <= 1)
    
    Notes
    -----
    Exponential crossover tends to preserve building blocks better
    than binomial crossover. The length of the copied segment follows
    a geometric distribution with parameter CR.
    """
    
    def __init__(self, CR=0.9):
        if not 0 <= CR <= 1:
            raise ValueError("CR must be in [0, 1]")
        self.CR = CR
    
    def apply(self, population, mutants):
        """Apply exponential crossover (fully vectorized)."""
        pop_size, dim = population.shape
        
        # Start with target vectors
        trials = population.copy()
        
        # For each individual, determine crossover segment
        for i in range(pop_size):
            # Random starting position
            n = np.random.randint(0, dim)
            
            # Copy at least one dimension
            trials[i, n] = mutants[i, n]
            
            # Continue copying with probability CR
            L = 1
            while L < dim and np.random.rand() <= self.CR:
                n = (n + 1) % dim  # Wrap around
                trials[i, n] = mutants[i, n]
                L += 1
        
        return trials


class UniformCrossover(CrossoverStrategy):
    """
    Uniform crossover: each dimension independently with probability 0.5.
    
    A simple crossover strategy where each dimension has equal probability
    of coming from either parent or mutant.
    
    Notes
    -----
    This is a special case of binomial crossover with CR=0.5,
    but ensures at least one dimension crosses over.
    """
    
    def __init__(self):
        pass
    
    def apply(self, population, mutants):
        """Apply uniform crossover (fully vectorized)."""
        pop_size, dim = population.shape
        
        # Vectorized: 50% chance for each dimension
        crossover_mask = np.random.rand(pop_size, dim) <= 0.5
        
        # Ensure at least one dimension crosses over per individual
        j_rand = np.random.randint(0, dim, pop_size)
        crossover_mask[np.arange(pop_size), j_rand] = True
        
        # Vectorized crossover
        trials = np.where(crossover_mask, mutants, population)
        return trials
