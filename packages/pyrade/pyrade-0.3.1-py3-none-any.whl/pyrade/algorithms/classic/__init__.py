"""
Classic Differential Evolution Variants.

This module contains traditional DE algorithm implementations:
- ClassicDE: Base class with configurable operators
- DErand1bin: DE/rand/1/bin (most popular)
- DEbest1bin: DE/best/1/bin (fast convergence)
- DEcurrentToBest1bin: DE/current-to-best/1/bin (balanced)
- DErand2bin: DE/rand/2/bin (high exploration)

All implementations use fully vectorized operations for performance.
"""

import numpy as np
import time
from typing import Callable, Optional, Dict, Any

from pyrade.core.population import Population
from pyrade.operators.mutation import (
    DErand1, DEbest1, DEcurrentToBest1, DErand2, 
    DEbest2, DEcurrentToRand1, DERandToBest1
)
from pyrade.operators.crossover import BinomialCrossover, ExponentialCrossover
from pyrade.operators.selection import GreedySelection


class ClassicDE:
    """
    Classic Differential Evolution with configurable operators.
    
    This is the base implementation that allows full customization of
    mutation, crossover, and selection strategies. Use specific variants
    (DErand1bin, DEbest1bin, etc.) for pre-configured algorithms.
    
    Parameters
    ----------
    objective_func : callable
        Function to minimize: f(x) -> float
    bounds : tuple or array
        (lower_bound, upper_bound) or [(lb1, ub1), (lb2, ub2), ...]
    mutation : MutationStrategy, optional
        Mutation strategy (default: DE/rand/1 with F=0.8)
    crossover : CrossoverStrategy, optional
        Crossover strategy (default: Binomial with CR=0.9)
    selection : SelectionStrategy, optional
        Selection strategy (default: Greedy)
    pop_size : int, default=50
        Population size
    max_iter : int, default=1000
        Maximum iterations
    F : float, default=0.8
        Mutation factor (if mutation not provided)
    CR : float, default=0.9
        Crossover rate (if crossover not provided)
    seed : int, optional
        Random seed for reproducibility
    verbose : bool, default=False
        Print progress
    callback : callable, optional
        Called after each iteration: callback(iteration, best_fitness, best_solution)
    
    Attributes
    ----------
    best_solution_ : ndarray
        Best solution found
    best_fitness_ : float
        Best fitness value
    history_ : dict
        Optimization history (fitness, time, etc.)
    
    Examples
    --------
    >>> from pyrade.algorithms.classic import ClassicDE
    >>> from pyrade.operators import DErand1, BinomialCrossover
    >>> 
    >>> def sphere(x):
    ...     return sum(x**2)
    >>> 
    >>> optimizer = ClassicDE(
    ...     objective_func=sphere,
    ...     bounds=[(-100, 100)] * 10,
    ...     mutation=DErand1(F=0.8),
    ...     crossover=BinomialCrossover(CR=0.9),
    ...     pop_size=50,
    ...     max_iter=1000
    ... )
    >>> result = optimizer.optimize()
    """
    
    def __init__(
        self,
        objective_func: Callable[[np.ndarray], float],
        bounds,
        mutation=None,
        crossover=None,
        selection=None,
        pop_size: int = 50,
        max_iter: int = 1000,
        F: float = 0.8,
        CR: float = 0.9,
        seed: Optional[int] = None,
        verbose: bool = False,
        callback: Optional[Callable] = None
    ):
        """Initialize Classic DE optimizer."""
        # Validate inputs
        if not callable(objective_func):
            raise ValueError("objective_func must be callable")
        if pop_size < 4:
            raise ValueError("pop_size must be at least 4")
        if max_iter < 1:
            raise ValueError("max_iter must be at least 1")
        
        self.objective_func = objective_func
        self.bounds = bounds
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.F = F
        self.CR = CR
        self.seed = seed
        self.verbose = verbose
        self.callback = callback
        
        # Initialize operators with defaults if not provided
        self.mutation = mutation if mutation is not None else DErand1(F=F)
        self.crossover = crossover if crossover is not None else BinomialCrossover(CR=CR)
        self.selection = selection if selection is not None else GreedySelection()
        
        # Infer dimensionality from bounds
        bounds_array = np.array(bounds)
        if bounds_array.ndim == 1:
            raise ValueError(
                "Cannot infer dimensionality from scalar bounds. "
                "Please provide bounds as [(lb1, ub1), (lb2, ub2), ...]"
            )
        self.dim = bounds_array.shape[0]
        
        # Initialize population
        self.population = Population(pop_size, self.dim, bounds, seed)
        
        # Results storage
        self.best_solution_ = None
        self.best_fitness_ = np.inf
        self.history_ = {
            'fitness': [],
            'time': [],
            'iteration': []
        }
    
    def _initialize_population(self):
        """Initialize random population and evaluate fitness."""
        if self.verbose:
            print("Initializing population...")
        
        self.population.initialize_random()
        self.population.evaluate(self.objective_func)
        
        # Store initial best
        self.best_solution_ = self.population.best_vector.copy()
        self.best_fitness_ = self.population.best_fitness
        
        if self.verbose:
            print(f"Initial best fitness: {self.best_fitness_:.6e}")
    
    def _evolve_generation(self):
        """Evolve one generation using vectorized operations."""
        pop_vectors = self.population.vectors
        pop_fitness = self.population.fitness
        best_idx = self.population.best_idx
        target_indices = self.population.get_indices()
        
        # Vectorized mutation
        mutants = self.mutation.apply(
            pop_vectors, pop_fitness, best_idx, target_indices
        )
        
        # Boundary repair
        mutants = self.population.clip_to_bounds(mutants)
        
        # Vectorized crossover
        trials = self.crossover.apply(pop_vectors, mutants)
        
        # Boundary repair
        trials = self.population.clip_to_bounds(trials)
        
        # Evaluate all trials
        trial_fitness = self.population.evaluate_vectors(trials, self.objective_func)
        
        # Vectorized selection
        new_vectors, new_fitness = self.selection.apply(
            pop_vectors, pop_fitness, trials, trial_fitness
        )
        
        # Count improvements
        improved_count = np.sum(new_fitness < pop_fitness)
        
        # Update population
        self.population.update(new_vectors, new_fitness)
        
        # Update global best
        if self.population.best_fitness < self.best_fitness_:
            self.best_solution_ = self.population.best_vector.copy()
            self.best_fitness_ = self.population.best_fitness
        
        return improved_count
    
    def optimize(self) -> Dict[str, Any]:
        """
        Run the optimization.
        
        Returns
        -------
        dict with keys:
            'best_solution': Best solution found
            'best_fitness': Best fitness value
            'n_iterations': Number of iterations run
            'history': Optimization history
            'success': Whether optimization succeeded
            'time': Total optimization time
        """
        if self.verbose:
            print("="*70)
            print(f"Starting {self.__class__.__name__} Optimization")
            print("="*70)
            print(f"Population size: {self.pop_size}")
            print(f"Dimensions: {self.dim}")
            print(f"Max iterations: {self.max_iter}")
            print(f"Mutation: {self.mutation.__class__.__name__}")
            print(f"Crossover: {self.crossover.__class__.__name__}")
            print(f"Selection: {self.selection.__class__.__name__}")
            print("="*70)
        
        start_time = time.time()
        
        # Initialize population
        self._initialize_population()
        
        # Store initial history
        self.history_['fitness'].append(self.best_fitness_)
        self.history_['time'].append(time.time() - start_time)
        self.history_['iteration'].append(0)
        
        # Main optimization loop
        for iteration in range(1, self.max_iter + 1):
            iter_start = time.time()
            
            # Evolve one generation
            improved_count = self._evolve_generation()
            
            # Store history
            iter_time = time.time() - iter_start
            self.history_['fitness'].append(self.best_fitness_)
            self.history_['time'].append(time.time() - start_time)
            self.history_['iteration'].append(iteration)
            
            # Print progress
            if self.verbose and (iteration % 10 == 0 or iteration == 1):
                print(
                    f"Iter {iteration:4d} | "
                    f"Best: {self.best_fitness_:.6e} | "
                    f"Improved: {improved_count:2d}/{self.pop_size} | "
                    f"Time: {iter_time:.3f}s"
                )
            
            # Call callback
            if self.callback is not None:
                self.callback(iteration, self.best_fitness_, self.best_solution_)
        
        total_time = time.time() - start_time
        
        if self.verbose:
            print("="*70)
            print("Optimization Complete")
            print(f"Final best fitness: {self.best_fitness_:.6e}")
            print(f"Total time: {total_time:.3f}s")
            print(f"Average time per iteration: {total_time/self.max_iter:.3f}s")
            print("="*70)
        
        return {
            'best_solution': self.best_solution_,
            'best_fitness': self.best_fitness_,
            'n_iterations': self.max_iter,
            'history': self.history_,
            'success': True,
            'time': total_time
        }


class DErand1bin(ClassicDE):
    """
    DE/rand/1/bin - Most popular DE variant.
    
    Mutation: v = x_r1 + F * (x_r2 - x_r3)
    Crossover: Binomial
    
    Best for general-purpose optimization with balanced
    exploration and exploitation.
    
    Parameters
    ----------
    objective_func : callable
        Function to minimize
    bounds : array-like
        Search space bounds [(lb1, ub1), (lb2, ub2), ...]
    pop_size : int, default=50
        Population size
    max_iter : int, default=1000
        Maximum iterations
    F : float, default=0.8
        Mutation factor
    CR : float, default=0.9
        Crossover rate
    seed : int, optional
        Random seed
    verbose : bool, default=False
        Print progress
        
    Examples
    --------
    >>> from pyrade.algorithms.classic import DErand1bin
    >>> 
    >>> def sphere(x):
    ...     return sum(x**2)
    >>> 
    >>> de = DErand1bin(sphere, bounds=[(-100, 100)] * 10)
    >>> result = de.optimize()
    """
    
    def __init__(self, objective_func, bounds, pop_size=50, max_iter=1000,
                 F=0.8, CR=0.9, seed=None, verbose=False, callback=None):
        super().__init__(
            objective_func=objective_func,
            bounds=bounds,
            mutation=DErand1(F=F),
            crossover=BinomialCrossover(CR=CR),
            selection=GreedySelection(),
            pop_size=pop_size,
            max_iter=max_iter,
            F=F,
            CR=CR,
            seed=seed,
            verbose=verbose,
            callback=callback
        )


class DEbest1bin(ClassicDE):
    """
    DE/best/1/bin - Fast convergence variant.
    
    Mutation: v = x_best + F * (x_r1 - x_r2)
    Crossover: Binomial
    
    Exploitative strategy good for unimodal functions.
    May converge prematurely on multimodal problems.
    
    Parameters
    ----------
    objective_func : callable
        Function to minimize
    bounds : array-like
        Search space bounds
    pop_size : int, default=50
        Population size
    max_iter : int, default=1000
        Maximum iterations
    F : float, default=0.8
        Mutation factor
    CR : float, default=0.9
        Crossover rate
    seed : int, optional
        Random seed
    verbose : bool, default=False
        Print progress
    """
    
    def __init__(self, objective_func, bounds, pop_size=50, max_iter=1000,
                 F=0.8, CR=0.9, seed=None, verbose=False, callback=None):
        super().__init__(
            objective_func=objective_func,
            bounds=bounds,
            mutation=DEbest1(F=F),
            crossover=BinomialCrossover(CR=CR),
            selection=GreedySelection(),
            pop_size=pop_size,
            max_iter=max_iter,
            F=F,
            CR=CR,
            seed=seed,
            verbose=verbose,
            callback=callback
        )


class DEcurrentToBest1bin(ClassicDE):
    """
    DE/current-to-best/1/bin - Balanced variant.
    
    Mutation: v = x_i + F * (x_best - x_i) + F * (x_r1 - x_r2)
    Crossover: Binomial
    
    Good balance between exploration and exploitation.
    Works well on a wide range of problems.
    
    Parameters
    ----------
    objective_func : callable
        Function to minimize
    bounds : array-like
        Search space bounds
    pop_size : int, default=50
        Population size
    max_iter : int, default=1000
        Maximum iterations
    F : float, default=0.8
        Mutation factor
    CR : float, default=0.9
        Crossover rate
    seed : int, optional
        Random seed
    verbose : bool, default=False
        Print progress
    """
    
    def __init__(self, objective_func, bounds, pop_size=50, max_iter=1000,
                 F=0.8, CR=0.9, seed=None, verbose=False, callback=None):
        super().__init__(
            objective_func=objective_func,
            bounds=bounds,
            mutation=DEcurrentToBest1(F=F),
            crossover=BinomialCrossover(CR=CR),
            selection=GreedySelection(),
            pop_size=pop_size,
            max_iter=max_iter,
            F=F,
            CR=CR,
            seed=seed,
            verbose=verbose,
            callback=callback
        )


class DErand2bin(ClassicDE):
    """
    DE/rand/2/bin - High exploration variant.
    
    Mutation: v = x_r1 + F * (x_r2 - x_r3) + F * (x_r4 - x_r5)
    Crossover: Binomial
    
    More exploratory, good for highly multimodal problems.
    Requires larger populations and converges slower.
    
    Parameters
    ----------
    objective_func : callable
        Function to minimize
    bounds : array-like
        Search space bounds
    pop_size : int, default=50
        Population size (recommend larger for this variant)
    max_iter : int, default=1000
        Maximum iterations
    F : float, default=0.8
        Mutation factor
    CR : float, default=0.9
        Crossover rate
    seed : int, optional
        Random seed
    verbose : bool, default=False
        Print progress
    """
    
    def __init__(self, objective_func, bounds, pop_size=50, max_iter=1000,
                 F=0.8, CR=0.9, seed=None, verbose=False, callback=None):
        super().__init__(
            objective_func=objective_func,
            bounds=bounds,
            mutation=DErand2(F=F),
            crossover=BinomialCrossover(CR=CR),
            selection=GreedySelection(),
            pop_size=pop_size,
            max_iter=max_iter,
            F=F,
            CR=CR,
            seed=seed,
            verbose=verbose,
            callback=callback
        )


class DEbest2bin(ClassicDE):
    """
    DE/best/2/bin - Highly exploitative variant.
    
    Mutation: v = x_best + F * (x_r1 - x_r2) + F * (x_r3 - x_r4)
    Crossover: Binomial
    
    Very fast convergence using best individual with two difference vectors.
    Risk of premature convergence on multimodal problems.
    
    Parameters
    ----------
    objective_func : callable
        Function to minimize
    bounds : array-like
        Search space bounds
    pop_size : int, default=50
        Population size
    max_iter : int, default=1000
        Maximum iterations
    F : float, default=0.8
        Mutation factor
    CR : float, default=0.9
        Crossover rate
    seed : int, optional
        Random seed
    verbose : bool, default=False
        Print progress
    """
    
    def __init__(self, objective_func, bounds, pop_size=50, max_iter=1000,
                 F=0.8, CR=0.9, seed=None, verbose=False, callback=None):
        super().__init__(
            objective_func=objective_func,
            bounds=bounds,
            mutation=DEbest2(F=F),
            crossover=BinomialCrossover(CR=CR),
            selection=GreedySelection(),
            pop_size=pop_size,
            max_iter=max_iter,
            F=F,
            CR=CR,
            seed=seed,
            verbose=verbose,
            callback=callback
        )


class DEcurrentToRand1bin(ClassicDE):
    """
    DE/current-to-rand/1/bin - Exploratory variant.
    
    Mutation: v = x_i + K * (x_r1 - x_i) + F * (x_r2 - x_r3)
    Crossover: Binomial
    
    Combines current vector with random direction for diversity.
    Good balance between exploration and maintaining population structure.
    
    Parameters
    ----------
    objective_func : callable
        Function to minimize
    bounds : array-like
        Search space bounds
    pop_size : int, default=50
        Population size
    max_iter : int, default=1000
        Maximum iterations
    F : float, default=0.8
        Mutation factor for difference vector
    K : float, default=0.5
        Weight for current-to-random direction
    CR : float, default=0.9
        Crossover rate
    seed : int, optional
        Random seed
    verbose : bool, default=False
        Print progress
    """
    
    def __init__(self, objective_func, bounds, pop_size=50, max_iter=1000,
                 F=0.8, K=0.5, CR=0.9, seed=None, verbose=False, callback=None):
        super().__init__(
            objective_func=objective_func,
            bounds=bounds,
            mutation=DEcurrentToRand1(F=F, K=K),
            crossover=BinomialCrossover(CR=CR),
            selection=GreedySelection(),
            pop_size=pop_size,
            max_iter=max_iter,
            F=F,
            CR=CR,
            seed=seed,
            verbose=verbose,
            callback=callback
        )


class DERandToBest1bin(ClassicDE):
    """
    DE/rand-to-best/1/bin - Balanced exploitative variant.
    
    Mutation: v = x_r1 + F * (x_best - x_r1) + F * (x_r2 - x_r3)
    Crossover: Binomial
    
    Direction from random vector toward best with additional diversity.
    Less greedy than DE/best/1, good when premature convergence is a concern.
    
    Parameters
    ----------
    objective_func : callable
        Function to minimize
    bounds : array-like
        Search space bounds
    pop_size : int, default=50
        Population size
    max_iter : int, default=1000
        Maximum iterations
    F : float, default=0.8
        Mutation factor
    CR : float, default=0.9
        Crossover rate
    seed : int, optional
        Random seed
    verbose : bool, default=False
        Print progress
    """
    
    def __init__(self, objective_func, bounds, pop_size=50, max_iter=1000,
                 F=0.8, CR=0.9, seed=None, verbose=False, callback=None):
        super().__init__(
            objective_func=objective_func,
            bounds=bounds,
            mutation=DERandToBest1(F=F),
            crossover=BinomialCrossover(CR=CR),
            selection=GreedySelection(),
            pop_size=pop_size,
            max_iter=max_iter,
            F=F,
            CR=CR,
            seed=seed,
            verbose=verbose,
            callback=callback
        )


class DErand1exp(ClassicDE):
    """
    DE/rand/1/exp: Classic DE with exponential crossover.
    
    Uses DE/rand/1 mutation strategy with exponential crossover instead
    of binomial. Exponential crossover tends to preserve building blocks
    better by creating contiguous segments of mutant parameters.
    
    Mutation: v_i = x_r1 + F * (x_r2 - x_r3)
    Crossover: Exponential (contiguous parameter exchange)
    Selection: Greedy (elitist)
    
    Reference:
        Storn, R., & Price, K. (1997). Differential evolution–a simple
        and efficient heuristic for global optimization over continuous
        spaces. Journal of global optimization, 11(4), 341-359.
    
    Parameters
    ----------
    objective_func : callable
        Function to minimize
    bounds : array-like
        Search space bounds
    pop_size : int, default=50
        Population size
    max_iter : int, default=1000
        Maximum iterations
    F : float, default=0.8
        Mutation factor
    CR : float, default=0.9
        Crossover rate (probability of continuing exchange)
    seed : int, optional
        Random seed
    verbose : bool, default=False
        Print progress
    """
    
    def __init__(self, objective_func, bounds, pop_size=50, max_iter=1000,
                 F=0.8, CR=0.9, seed=None, verbose=False, callback=None):
        super().__init__(
            objective_func=objective_func,
            bounds=bounds,
            mutation=DErand1(F=F),
            crossover=ExponentialCrossover(CR=CR),
            selection=GreedySelection(),
            pop_size=pop_size,
            max_iter=max_iter,
            F=F,
            CR=CR,
            seed=seed,
            verbose=verbose,
            callback=callback
        )


class DErand1EitherOrBin(ClassicDE):
    """
    DE/rand/1/either-or: Uses probabilistic choice of F in mutation.
    
    Uses DE/rand/1 mutation with either-or F selection (F or 0.5*F)
    combined with binomial crossover. This adds stochastic variation
    in the mutation step size which can improve exploration.
    
    Mutation: v_i = x_r1 + F_i * (x_r2 - x_r3)
              where F_i = F with probability p_F, else 0.5*F
    Crossover: Binomial
    Selection: Greedy (elitist)
    
    Reference:
        Price, K. V., Storn, R. M., & Lampinen, J. A. (2006).
        Differential Evolution: A Practical Approach to Global Optimization.
    
    Parameters
    ----------
    objective_func : callable
        Function to minimize
    bounds : array-like
        Search space bounds
    pop_size : int, default=50
        Population size
    max_iter : int, default=1000
        Maximum iterations
    F : float, default=0.8
        Mutation factor
    CR : float, default=0.9
        Crossover rate
    p_F : float, default=0.5
        Probability of using full F (vs 0.5*F)
    seed : int, optional
        Random seed
    verbose : bool, default=False
        Print progress
    """
    
    def __init__(self, objective_func, bounds, pop_size=50, max_iter=1000,
                 F=0.8, CR=0.9, p_F=0.5, seed=None, verbose=False, callback=None):
        from pyrade.operators import DErand1EitherOr
        super().__init__(
            objective_func=objective_func,
            bounds=bounds,
            mutation=DErand1EitherOr(F=F, p_F=p_F),
            crossover=BinomialCrossover(CR=CR),
            selection=GreedySelection(),
            pop_size=pop_size,
            max_iter=max_iter,
            F=F,
            CR=CR,
            seed=seed,
            verbose=verbose,
            callback=callback
        )


__all__ = [
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
]
