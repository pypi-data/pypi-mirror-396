"""
Selection strategies for Differential Evolution.

This module provides selection strategies with fully vectorized
implementations for high performance.
"""

from abc import ABC, abstractmethod
import numpy as np


class SelectionStrategy(ABC):
    """
    Abstract base class for selection strategies.
    
    All selection strategies should inherit from this class and implement
    the apply() method.
    """
    
    @abstractmethod
    def apply(self, population, fitness, trials, trial_fitness):
        """
        Select survivors for next generation.
        
        Parameters
        ----------
        population : ndarray, shape (pop_size, dim)
            Current population
        fitness : ndarray, shape (pop_size,)
            Current fitness
        trials : ndarray, shape (pop_size, dim)
            Trial vectors
        trial_fitness : ndarray, shape (pop_size,)
            Trial fitness
            
        Returns
        -------
        new_population : ndarray, shape (pop_size, dim)
            Selected population
        new_fitness : ndarray, shape (pop_size,)
            Selected fitness
        """
        pass


class GreedySelection(SelectionStrategy):
    """
    Greedy selection: keep trial if better, else keep target.
    
    Standard DE selection. For minimization problems, selects the
    individual with lower fitness value.
    
    Notes
    -----
    This is the most common selection strategy in DE, ensuring
    the population never degrades (monotonic improvement).
    """
    
    def apply(self, population, fitness, trials, trial_fitness):
        """Apply greedy selection (fully vectorized)."""
        # Vectorized selection: keep trial if better
        improved = trial_fitness < fitness
        
        # Create new population
        new_population = population.copy()
        new_population[improved] = trials[improved]
        
        # Create new fitness array
        new_fitness = fitness.copy()
        new_fitness[improved] = trial_fitness[improved]
        
        return new_population, new_fitness


class TournamentSelection(SelectionStrategy):
    """
    Tournament selection: select winner from random tournament.
    
    Selects the best individual from a random subset of the population.
    Can add diversity compared to greedy selection.
    
    Parameters
    ----------
    tournament_size : int, default=2
        Number of individuals in each tournament
    
    Notes
    -----
    Larger tournament sizes increase selection pressure.
    Tournament size of 2 is most common.
    """
    
    def __init__(self, tournament_size=2):
        if tournament_size < 2:
            raise ValueError("tournament_size must be at least 2")
        self.tournament_size = tournament_size
    
    def apply(self, population, fitness, trials, trial_fitness):
        """Apply tournament selection."""
        pop_size = len(population)
        
        # Combine current population and trials
        combined_pop = np.vstack([population, trials])
        combined_fitness = np.concatenate([fitness, trial_fitness])
        
        new_population = np.zeros_like(population)
        new_fitness = np.zeros_like(fitness)
        
        # Select winners via tournament
        for i in range(pop_size):
            # Random tournament
            tournament_indices = np.random.choice(
                2 * pop_size, self.tournament_size, replace=False
            )
            tournament_fitness = combined_fitness[tournament_indices]
            
            # Winner has best fitness
            winner_idx = tournament_indices[np.argmin(tournament_fitness)]
            new_population[i] = combined_pop[winner_idx]
            new_fitness[i] = combined_fitness[winner_idx]
        
        return new_population, new_fitness


class ElitistSelection(SelectionStrategy):
    """
    Elitist selection: always preserve best individuals.
    
    Combines greedy selection with elitism to ensure the absolute
    best individuals are never lost.
    
    Parameters
    ----------
    elite_size : int, default=1
        Number of elite individuals to preserve
    
    Notes
    -----
    Elite individuals are guaranteed to survive to the next generation,
    regardless of their trial performance.
    """
    
    def __init__(self, elite_size=1):
        if elite_size < 0:
            raise ValueError("elite_size must be non-negative")
        self.elite_size = elite_size
    
    def apply(self, population, fitness, trials, trial_fitness):
        """Apply elitist selection."""
        # Start with greedy selection
        improved = trial_fitness < fitness
        new_population = population.copy()
        new_population[improved] = trials[improved]
        new_fitness = fitness.copy()
        new_fitness[improved] = trial_fitness[improved]
        
        # Preserve elites
        if self.elite_size > 0:
            # Find elite individuals from original population
            elite_indices = np.argsort(fitness)[:self.elite_size]
            
            # Find worst individuals in new population
            worst_indices = np.argsort(new_fitness)[-self.elite_size:]
            
            # Replace worst with elites if necessary
            for elite_idx, worst_idx in zip(elite_indices, worst_indices):
                if fitness[elite_idx] < new_fitness[worst_idx]:
                    new_population[worst_idx] = population[elite_idx]
                    new_fitness[worst_idx] = fitness[elite_idx]
        
        return new_population, new_fitness
