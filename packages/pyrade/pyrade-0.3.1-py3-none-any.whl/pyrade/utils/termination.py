"""
Termination criteria for Differential Evolution.

This module provides various criteria for determining when to
stop the optimization process.
"""

from abc import ABC, abstractmethod
import numpy as np


class TerminationCriterion(ABC):
    """
    Abstract base class for termination criteria.
    
    All termination criteria should inherit from this class and
    implement the should_terminate() method.
    """
    
    @abstractmethod
    def should_terminate(self, iteration, fitness_history):
        """
        Check if optimization should terminate.
        
        Parameters
        ----------
        iteration : int
            Current iteration number
        fitness_history : list of float
            History of best fitness values
        
        Returns
        -------
        bool
            True if optimization should terminate
        """
        pass


class MaxIterations(TerminationCriterion):
    """
    Terminate after maximum iterations.
    
    Most basic termination criterion. Stops optimization after
    a fixed number of iterations.
    
    Parameters
    ----------
    max_iter : int
        Maximum number of iterations
    """
    
    def __init__(self, max_iter):
        if max_iter < 1:
            raise ValueError("max_iter must be at least 1")
        self.max_iter = max_iter
    
    def should_terminate(self, iteration, fitness_history):
        """Check if max iterations reached."""
        return iteration >= self.max_iter


class FitnessThreshold(TerminationCriterion):
    """
    Terminate when fitness reaches threshold.
    
    Stops optimization when the best fitness value reaches or
    falls below a specified threshold.
    
    Parameters
    ----------
    threshold : float
        Target fitness threshold
    """
    
    def __init__(self, threshold):
        self.threshold = threshold
    
    def should_terminate(self, iteration, fitness_history):
        """Check if fitness threshold reached."""
        if len(fitness_history) == 0:
            return False
        return fitness_history[-1] <= self.threshold


class NoImprovement(TerminationCriterion):
    """
    Terminate if no improvement for n iterations.
    
    Stops optimization if the best fitness has not improved
    significantly for a specified number of iterations.
    
    Parameters
    ----------
    patience : int, default=50
        Number of iterations to wait for improvement
    min_delta : float, default=1e-6
        Minimum change in fitness to be considered improvement
    
    Notes
    -----
    This criterion helps detect convergence and avoid wasting
    computational resources on stagnated optimization.
    """
    
    def __init__(self, patience=50, min_delta=1e-6):
        if patience < 1:
            raise ValueError("patience must be at least 1")
        if min_delta < 0:
            raise ValueError("min_delta must be non-negative")
        self.patience = patience
        self.min_delta = min_delta
    
    def should_terminate(self, iteration, fitness_history):
        """Check if no improvement for patience iterations."""
        if len(fitness_history) < self.patience:
            return False
        
        recent = fitness_history[-self.patience:]
        improvement = recent[0] - recent[-1]
        return improvement < self.min_delta


class MaxTime(TerminationCriterion):
    """
    Terminate after maximum time.
    
    Stops optimization after a specified amount of time has elapsed.
    
    Parameters
    ----------
    max_time : float
        Maximum time in seconds
    start_time : float, optional
        Start time (from time.time())
    
    Notes
    -----
    Requires start_time to be set before use.
    """
    
    def __init__(self, max_time):
        if max_time <= 0:
            raise ValueError("max_time must be positive")
        self.max_time = max_time
        self.start_time = None
    
    def set_start_time(self, start_time):
        """Set the optimization start time."""
        self.start_time = start_time
    
    def should_terminate(self, iteration, fitness_history, current_time):
        """Check if max time exceeded."""
        if self.start_time is None:
            return False
        elapsed = current_time - self.start_time
        return elapsed >= self.max_time


class FitnessVariance(TerminationCriterion):
    """
    Terminate when population fitness variance is low.
    
    Stops optimization when the variance in fitness values
    across the population falls below a threshold, indicating
    convergence.
    
    Parameters
    ----------
    threshold : float, default=1e-6
        Variance threshold
    
    Notes
    -----
    Requires access to population fitness values, not just
    best fitness history.
    """
    
    def __init__(self, threshold=1e-6):
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        self.threshold = threshold
    
    def should_terminate_with_population(self, iteration, fitness_array):
        """
        Check if fitness variance below threshold.
        
        Parameters
        ----------
        iteration : int
            Current iteration
        fitness_array : ndarray
            Current population fitness values
        
        Returns
        -------
        bool
            True if should terminate
        """
        variance = np.var(fitness_array)
        return variance < self.threshold


class CombinedCriterion(TerminationCriterion):
    """
    Combine multiple termination criteria.
    
    Terminates when any of the specified criteria are met.
    
    Parameters
    ----------
    criteria : list of TerminationCriterion
        List of criteria to combine
    mode : str, default='any'
        'any': terminate when any criterion is met
        'all': terminate only when all criteria are met
    """
    
    def __init__(self, criteria, mode='any'):
        if not criteria:
            raise ValueError("criteria list cannot be empty")
        if mode not in ['any', 'all']:
            raise ValueError("mode must be 'any' or 'all'")
        self.criteria = criteria
        self.mode = mode
    
    def should_terminate(self, iteration, fitness_history):
        """Check combined criteria."""
        results = [
            criterion.should_terminate(iteration, fitness_history)
            for criterion in self.criteria
        ]
        
        if self.mode == 'any':
            return any(results)
        else:  # mode == 'all'
            return all(results)
