"""
Main Differential Evolution algorithm implementation.

This module provides the core DifferentialEvolution class with
fully vectorized operations for high performance.
"""

import numpy as np
import time
import logging
from typing import Callable, Optional, Dict, Any, Union, Tuple

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    tqdm = None

from pyrade.core.population import Population
from pyrade.operators.mutation import DErand1
from pyrade.operators.crossover import BinomialCrossover
from pyrade.operators.selection import GreedySelection


# Configure module logger
logger = logging.getLogger(__name__)


class DifferentialEvolution:
    """
    Main Differential Evolution optimizer with vectorized operations.
    
    This implementation uses aggressive vectorization to process entire
    populations at once, achieving significant performance improvements
    over monolithic implementations.
    
    Features:
    - Fully vectorized (processes entire population at once)
    - Strategy pattern for operators (easy to extend)
    - Professional API (fit/predict style)
    - Progress tracking and callbacks
    - Progress bar support (tqdm integration)
    - Comprehensive logging support
    
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
        Population size (must be >= 4)
    max_iter : int, default=1000
        Maximum iterations (must be >= 1)
    seed : int, optional
        Random seed for reproducibility
    verbose : bool, default=False
        Print progress information
    show_progress : bool, default=False
        Show progress bar (requires tqdm)
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
    
    Methods
    -------
    optimize() : dict
        Run optimization and return results
    
    Examples
    --------
    >>> def sphere(x):
    ...     return sum(x**2)
    >>> 
    >>> optimizer = DifferentialEvolution(
    ...     objective_func=sphere,
    ...     bounds=(-100, 100),
    ...     pop_size=50,
    ...     max_iter=1000
    ... )
    >>> result = optimizer.optimize()
    >>> print(f"Best fitness: {result['best_fitness']}")
    """
    
    def __init__(
        self,
        objective_func: Callable[[np.ndarray], float],
        bounds: Union[Tuple[float, float], np.ndarray],
        mutation: Optional[Any] = None,
        crossover: Optional[Any] = None,
        selection: Optional[Any] = None,
        pop_size: int = 50,
        max_iter: int = 1000,
        seed: Optional[int] = None,
        verbose: bool = False,
        show_progress: bool = False,
        callback: Optional[Callable] = None
    ):
        """Initialize Differential Evolution optimizer."""
        logger.info("Initializing DifferentialEvolution optimizer")
        
        # Validate inputs with detailed error messages
        if not callable(objective_func):
            error_msg = "objective_func must be callable. Received: {}".format(type(objective_func).__name__)
            logger.error(error_msg)
            raise TypeError(error_msg)
        
        if not isinstance(pop_size, int) or pop_size < 4:
            error_msg = "pop_size must be an integer >= 4 (got: {}). DE requires at least 4 individuals for mutation.".format(pop_size)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not isinstance(max_iter, int) or max_iter < 1:
            error_msg = "max_iter must be an integer >= 1 (got: {})".format(max_iter)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.objective_func = objective_func
        self.bounds = bounds
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.seed = seed
        self.verbose = verbose
        self.show_progress = show_progress and TQDM_AVAILABLE
        self.callback = callback
        
        # Log warning if progress bar requested but tqdm not available
        if show_progress and not TQDM_AVAILABLE:
            warning_msg = "Progress bar requested but tqdm is not installed. Install with: pip install tqdm"
            logger.warning(warning_msg)
            if verbose:
                print(f"Warning: {warning_msg}")
        
        # Initialize operators with defaults if not provided
        self.mutation = mutation if mutation is not None else DErand1(F=0.8)
        self.crossover = crossover if crossover is not None else BinomialCrossover(CR=0.9)
        self.selection = selection if selection is not None else GreedySelection()
        
        logger.debug(f"Operators initialized: Mutation={self.mutation.__class__.__name__}, "
                    f"Crossover={self.crossover.__class__.__name__}, "
                    f"Selection={self.selection.__class__.__name__}")
        
        # Infer dimensionality from bounds with enhanced validation
        try:
            bounds_array = np.array(bounds)
        except Exception as e:
            error_msg = f"Failed to convert bounds to numpy array: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if bounds_array.ndim == 1:
            error_msg = (
                "Cannot infer dimensionality from scalar bounds. "
                "Please provide bounds as [(lb1, ub1), (lb2, ub2), ...] or "
                "as a 2D array with shape (n_dimensions, 2). "
                f"Received bounds shape: {bounds_array.shape}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.dim = bounds_array.shape[0]
        logger.info(f"Problem dimensionality: {self.dim}D")
        
        # Initialize population
        try:
            self.population = Population(pop_size, self.dim, bounds, seed)
            logger.info(f"Population initialized: size={pop_size}, dimensions={self.dim}")
        except Exception as e:
            error_msg = f"Failed to initialize population: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        
        # Results storage
        self.best_solution_ = None
        self.best_fitness_ = np.inf
        self.history_ = {
            'fitness': [],
            'time': [],
            'iteration': []
        }
        
        logger.debug("Initialization complete")
    
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
        """
        Evolve one generation using vectorized operations.
        
        Steps:
        1. Vectorized mutation (all individuals at once)
        2. Boundary repair (vectorized clip)
        3. Vectorized crossover (all at once)
        4. Boundary repair (vectorized clip)
        5. Evaluate all trials
        6. Vectorized selection (all at once)
        7. Update best solution
        
        Returns
        -------
        improved_count : int
            Number of individuals that improved
        """
        pop_vectors = self.population.vectors
        pop_fitness = self.population.fitness
        best_idx = self.population.best_idx
        target_indices = self.population.get_indices()
        
        # Step 1: Vectorized mutation
        mutants = self.mutation.apply(
            pop_vectors, pop_fitness, best_idx, target_indices
        )
        
        # Step 2: Boundary repair (mutation)
        mutants = self.population.clip_to_bounds(mutants)
        
        # Fix: Ensure mutants are valid and not NaN/Inf (high-dimensional stability)
        mutants = np.where(np.isfinite(mutants), mutants, 
                          self.population.lb + np.random.rand(*mutants.shape) * 
                          (self.population.ub - self.population.lb))
        
        # Step 3: Vectorized crossover
        trials = self.crossover.apply(pop_vectors, mutants)
        
        # Step 4: Boundary repair (crossover)
        trials = self.population.clip_to_bounds(trials)
        
        # Fix: Ensure trials are valid (high-dimensional stability)
        trials = np.where(np.isfinite(trials), trials, pop_vectors)
        
        # Step 5: Evaluate all trials
        trial_fitness = self.population.evaluate_vectors(trials, self.objective_func)
        
        # Step 6: Vectorized selection
        new_vectors, new_fitness = self.selection.apply(
            pop_vectors, pop_fitness, trials, trial_fitness
        )
        
        # Count improvements
        improved_count = np.sum(new_fitness < pop_fitness)
        
        # Step 7: Update population (memory efficient - no unnecessary copies)
        self.population.vectors[:] = new_vectors
        self.population.fitness[:] = new_fitness
        self.population._update_best()
        
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
            print("Starting Differential Evolution Optimization")
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
        self.history_['fitness'].append(float(self.best_fitness_))
        self.history_['time'].append(time.time() - start_time)
        self.history_['iteration'].append(0)
        
        # Main optimization loop with optional progress bar
        iterator = range(1, self.max_iter + 1)
        if self.show_progress:
            iterator = tqdm(iterator, desc="Optimizing", unit="iter",
                          bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
        
        for iteration in iterator:
            iter_start = time.time()
            
            # Evolve one generation
            improved_count = self._evolve_generation()
            
            # Store history (convert to float to prevent memory accumulation)
            iter_time = time.time() - iter_start
            self.history_['fitness'].append(float(self.best_fitness_))
            self.history_['time'].append(float(time.time() - start_time))
            self.history_['iteration'].append(int(iteration))
            
            # Update progress bar postfix if available
            if self.show_progress:
                iterator.set_postfix({
                    'best': f'{self.best_fitness_:.6e}',
                    'improved': f'{improved_count}/{self.pop_size}'
                })
            
            # Print progress (only if not using progress bar)
            if self.verbose and not self.show_progress and (iteration % 10 == 0 or iteration == 1):
                print(
                    f"Iter {iteration:4d} | "
                    f"Best: {self.best_fitness_:.6e} | "
                    f"Improved: {improved_count:2d}/{self.pop_size} | "
                    f"Time: {iter_time:.3f}s"
                )
            
            # Log detailed progress
            if iteration % 100 == 0 or iteration == 1:
                logger.debug(f"Iteration {iteration}/{self.max_iter}: "
                           f"best_fitness={self.best_fitness_:.6e}, "
                           f"improved={improved_count}/{self.pop_size}")
            
            # Call callback
            if self.callback is not None:
                try:
                    self.callback(iteration, self.best_fitness_, self.best_solution_)
                except Exception as e:
                    logger.warning(f"Callback error at iteration {iteration}: {e}")
        
        total_time = time.time() - start_time
        
        logger.info(f"Optimization complete: best_fitness={self.best_fitness_:.6e}, "
                   f"total_time={total_time:.3f}s, iterations={self.max_iter}")
        
        if self.verbose:
            print("="*70)
            print("Optimization Complete")
            print(f"Final best fitness: {self.best_fitness_:.6e}")
            print(f"Total time: {total_time:.3f}s")
            print(f"Average time per iteration: {total_time/self.max_iter:.3f}s")
            print("="*70)
        
        # Return with explicit copies to prevent memory leaks
        return {
            'best_solution': self.best_solution_.copy(),
            'best_fitness': float(self.best_fitness_),
            'n_iterations': int(self.max_iter),
            'history': {
                'fitness': list(self.history_['fitness']),
                'time': list(self.history_['time']),
                'iteration': list(self.history_['iteration'])
            },
            'success': True,
            'time': float(total_time)
        }
