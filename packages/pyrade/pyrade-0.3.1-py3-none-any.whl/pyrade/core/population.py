"""
Population management for Differential Evolution.

This module provides efficient vectorized population operations.
"""

import numpy as np
import logging
from typing import Callable, Tuple, Union, Optional

# Configure module logger
logger = logging.getLogger(__name__)


class Population:
    """
    Manages the population of candidate solutions.
    
    This class handles population initialization, storage, and
    provides vectorized operations for efficient population management.
    
    Parameters
    ----------
    pop_size : int
        Size of the population
    dim : int
        Dimensionality of the search space
    bounds : tuple or array-like
        Search space bounds (lb, ub) or [(lb1, ub1), ...]
    seed : int, optional
        Random seed for reproducibility
    
    Attributes
    ----------
    vectors : ndarray, shape (pop_size, dim)
        Population vectors
    fitness : ndarray, shape (pop_size,)
        Fitness values for each individual
    best_idx : int
        Index of the best individual
    best_vector : ndarray, shape (dim,)
        Best solution vector
    best_fitness : float
        Best fitness value
    """
    
    def __init__(self, pop_size: int, dim: int, bounds: Union[Tuple[float, float], np.ndarray], seed: Optional[int] = None):
        """Initialize population."""
        logger.debug(f"Initializing Population: size={pop_size}, dim={dim}")
        
        if not isinstance(pop_size, int) or pop_size < 1:
            error_msg = f"pop_size must be a positive integer (got: {pop_size})"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not isinstance(dim, int) or dim < 1:
            error_msg = f"dim must be a positive integer (got: {dim})"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.pop_size = pop_size
        self.dim = dim
        self.seed = seed
        
        # Parse bounds
        self.lb, self.ub = self._parse_bounds(bounds, dim)
        
        # Initialize arrays
        self.vectors = np.zeros((pop_size, dim))
        self.fitness = np.full(pop_size, np.inf)
        self.best_idx = 0
        self.best_vector = None
        self.best_fitness = np.inf
        
        # Set random seed
        if seed is not None:
            np.random.seed(seed)
    
    def _parse_bounds(self, bounds: Union[Tuple[float, float], np.ndarray], dim: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Parse bounds into lower and upper bound arrays.
        
        Parameters
        ----------
        bounds : tuple or array-like
            Either (lb, ub) or [(lb1, ub1), (lb2, ub2), ...]
        dim : int
            Dimensionality
        
        Returns
        -------
        lb : ndarray, shape (dim,)
            Lower bounds
        ub : ndarray, shape (dim,)
            Upper bounds
        
        Raises
        ------
        ValueError
            If bounds format is invalid or lower bounds >= upper bounds
        """
        try:
            bounds = np.array(bounds)
        except Exception as e:
            error_msg = f"Failed to convert bounds to array: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
        
        if bounds.ndim == 1 and len(bounds) == 2:
            # Uniform bounds (lb, ub)
            lb = np.full(dim, bounds[0], dtype=np.float64)
            ub = np.full(dim, bounds[1], dtype=np.float64)
            logger.debug(f"Using uniform bounds: [{bounds[0]}, {bounds[1]}]")
        elif bounds.ndim == 2 and bounds.shape[0] == dim and bounds.shape[1] == 2:
            # Per-dimension bounds [(lb1, ub1), ...]
            lb = bounds[:, 0].astype(np.float64)
            ub = bounds[:, 1].astype(np.float64)
            logger.debug(f"Using per-dimension bounds: shape={bounds.shape}")
        else:
            error_msg = (
                f"Invalid bounds shape. Expected (2,) for uniform bounds or "
                f"({dim}, 2) for per-dimension bounds, got {bounds.shape}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if np.any(lb >= ub):
            invalid_dims = np.where(lb >= ub)[0]
            error_msg = (
                f"Lower bounds must be strictly less than upper bounds. "
                f"Violated at dimension(s): {invalid_dims.tolist()}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        return lb, ub
    
    def initialize_random(self):
        """
        Initialize population with random vectors within bounds.
        
        Uses Latin Hypercube Sampling for better space coverage.
        """
        # Latin Hypercube Sampling for better initial distribution
        lhs_samples = np.zeros((self.pop_size, self.dim))
        
        for i in range(self.dim):
            # Divide range into pop_size intervals
            intervals = np.linspace(0, 1, self.pop_size + 1)
            # Sample randomly within each interval
            samples = np.random.uniform(intervals[:-1], intervals[1:])
            # Shuffle to avoid correlation
            np.random.shuffle(samples)
            lhs_samples[:, i] = samples
        
        # Scale to actual bounds
        self.vectors = self.lb + lhs_samples * (self.ub - self.lb)
    
    def evaluate(self, objective_func: Callable[[np.ndarray], float]) -> np.ndarray:
        """
        Evaluate fitness for all individuals in population.
        
        Parameters
        ----------
        objective_func : callable
            Objective function to minimize
        
        Returns
        -------
        fitness : ndarray, shape (pop_size,)
            Fitness values
        """
        # Memory-efficient evaluation with cleanup
        for i in range(self.pop_size):
            try:
                fitness_val = objective_func(self.vectors[i])
                # Handle inf/nan from objective function
                if not np.isfinite(fitness_val):
                    fitness_val = 1e100  # Large penalty for invalid values
                self.fitness[i] = fitness_val
            except Exception:
                # If evaluation fails, assign large penalty
                self.fitness[i] = 1e100
        
        self._update_best()
        return self.fitness
    
    def evaluate_vectors(self, vectors: np.ndarray, objective_func: Callable[[np.ndarray], float]) -> np.ndarray:
        """
        Evaluate fitness for given vectors.
        
        Parameters
        ----------
        vectors : ndarray, shape (pop_size, dim)
            Vectors to evaluate
        objective_func : callable
            Objective function to minimize
        
        Returns
        -------
        fitness : ndarray, shape (pop_size,)
            Fitness values
        """
        # Memory-efficient evaluation with proper cleanup
        fitness = np.zeros(len(vectors), dtype=np.float64)
        for i, vec in enumerate(vectors):
            try:
                fitness_val = objective_func(vec)
                # Handle inf/nan from objective function
                if not np.isfinite(fitness_val):
                    fitness_val = 1e100
                fitness[i] = fitness_val
            except Exception:
                fitness[i] = 1e100
        return fitness
    
    def _update_best(self):
        """Update best solution information."""
        self.best_idx = np.argmin(self.fitness)
        self.best_vector = self.vectors[self.best_idx].copy()
        self.best_fitness = self.fitness[self.best_idx]
    
    def update(self, new_vectors: np.ndarray, new_fitness: np.ndarray) -> None:
        """
        Update population with new vectors and fitness.
        
        Parameters
        ----------
        new_vectors : ndarray, shape (pop_size, dim)
            New population vectors
        new_fitness : ndarray, shape (pop_size,)
            New fitness values
        """
        self.vectors = new_vectors.copy()
        self.fitness = new_fitness.copy()
        self._update_best()
    
    def get_indices(self) -> np.ndarray:
        """Get array of population indices."""
        return np.arange(self.pop_size)
    
    def clip_to_bounds(self, vectors: np.ndarray) -> np.ndarray:
        """
        Clip vectors to bounds.
        
        Parameters
        ----------
        vectors : ndarray, shape (pop_size, dim)
            Vectors to clip
        
        Returns
        -------
        clipped : ndarray, shape (pop_size, dim)
            Clipped vectors
        """
        return np.clip(vectors, self.lb, self.ub)
