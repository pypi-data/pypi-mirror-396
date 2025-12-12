"""
Experiment Manager for PyRADE.

This module provides a high-level interface for running, managing, and visualizing
benchmark experiments with automatic result storage and export capabilities.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable, Union, Tuple, Any
import json
import warnings
import logging

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    tqdm = None

from pyrade.core.algorithm import DifferentialEvolution
from pyrade.operators import DErand1, BinomialCrossover
from pyrade.visualization import OptimizationVisualizer
from pyrade import benchmarks

# Configure module logger
logger = logging.getLogger(__name__)


class ExperimentManager:
    """
    High-level experiment manager for benchmark testing and analysis.
    
    This class provides a complete pipeline for running optimization experiments,
    generating visualizations, and exporting results. It handles:
    - Multiple benchmark function selection
    - Configurable optimization parameters
    - Automated visualization generation
    - Result export to CSV, JSON, and NumPy formats
    - Timestamped experiment folders
    
    Parameters
    ----------
    benchmarks : list of str or callable
        Benchmark function names (e.g., 'Sphere', 'Rastrigin') or custom functions
    dimensions : int, default=10
        Problem dimensionality
    n_runs : int, default=30
        Number of independent runs per benchmark
    population_size : int, default=50
        DE population size
    max_iterations : int, default=100
        Maximum iterations per run
    F : float, default=0.8
        Mutation factor
    CR : float, default=0.9
        Crossover rate
    mutation : str, callable, or instance, optional
        Mutation strategy to use. Can be the name of a strategy from
        `pyrade.operators` (e.g., 'DErand1'), a callable/class that
        can be instantiated with `F=...`, or an already-created
        mutation instance. If `None`, defaults to `DErand1(F=0.8)`.
    experiment_name : str, optional
        Custom experiment name (default: auto-generated timestamp)
    base_folder : str, default='experiments'
        Base folder for storing experiments
    seed : int, optional
        Random seed for first run (incremented for subsequent runs)
        
    Attributes
    ----------
    results : dict
        Dictionary containing all experimental results
    experiment_folder : Path
        Path to the current experiment folder
    viz : OptimizationVisualizer
        Visualizer instance for plotting
        
    Examples
    --------
    >>> from pyrade.experiments import ExperimentManager
    >>> 
    >>> # Create experiment manager
    >>> exp = ExperimentManager(
    ...     benchmarks=['Sphere', 'Rastrigin', 'Rosenbrock'],
    ...     dimensions=10,
    ...     n_runs=30,
    ...     population_size=50,
    ...     max_iterations=100
    ... )
    >>> 
    >>> # Run experiments
    >>> exp.run_experiments()
    >>> 
    >>> # Generate all plots
    >>> exp.plot_all()
    >>> 
    >>> # Export results
    >>> exp.export_results()
    """
    
    # Available benchmark functions
    AVAILABLE_BENCHMARKS = {
        'Sphere': (benchmarks.Sphere, [(-100, 100)]),
        'Rastrigin': (benchmarks.Rastrigin, [(-5.12, 5.12)]),
        'Rosenbrock': (benchmarks.Rosenbrock, [(-5, 10)]),
        'Ackley': (benchmarks.Ackley, [(-32.768, 32.768)]),
        'Griewank': (benchmarks.Griewank, [(-600, 600)]),
        'Schwefel': (benchmarks.Schwefel, [(-500, 500)]),
        'Levy': (benchmarks.Levy, [(-10, 10)]),
        'Michalewicz': (benchmarks.Michalewicz, [(0, np.pi)]),
        'Zakharov': (benchmarks.Zakharov, [(-5, 10)]),
        'Easom': (benchmarks.Easom, [(-100, 100)]),
        'StyblinskiTang': (benchmarks.StyblinskiTang, [(-5, 5)]),
    }
    
    def __init__(
        self,
        benchmarks: Union[List[str], List[Callable], str, Callable, None] = None,
        dimensions: int = 10,
        n_runs: int = 30,
        population_size: int = 50,
        max_iterations: int = 100,
        F: float = 0.8,
        CR: float = 0.9,
        mutation: Optional[Union[str, Callable, object]] = None,
        experiment_name: Optional[str] = None,
        base_folder: str = 'experiments',
        seed: Optional[int] = None,
        show_progress: bool = True
    ):
        """Initialize the experiment manager."""
        logger.info("Initializing ExperimentManager")
        # Validate inputs
        if not isinstance(dimensions, int) or dimensions < 1:
            error_msg = f"dimensions must be a positive integer (got: {dimensions})"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not isinstance(n_runs, int) or n_runs < 1:
            error_msg = f"n_runs must be a positive integer (got: {n_runs})"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Configuration
        self.dimensions = dimensions
        self.n_runs = n_runs
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.F = F
        self.CR = CR
        # Mutation strategy: can be a string (name from pyrade.operators),
        # a callable/class that returns an instance, or an instance itself.
        # If None, default to DErand1 during runs.
        self.mutation = mutation
        self.seed = seed if seed is not None else np.random.randint(0, 10000)
        self.show_progress = show_progress and TQDM_AVAILABLE
        
        # Log warning if progress bar requested but tqdm not available
        if show_progress and not TQDM_AVAILABLE:
            logger.warning("Progress bar requested but tqdm is not installed. Install with: pip install tqdm")
        
        logger.debug(f"Configuration: D={dimensions}, runs={n_runs}, pop={population_size}, iter={max_iterations}")
        
        # Setup benchmark functions
        self.benchmark_configs = {}
        if benchmarks is None:
            # Use all available benchmarks
            benchmarks = list(self.AVAILABLE_BENCHMARKS.keys())

        # Allow single callable or single string to be provided
        if not isinstance(benchmarks, (list, tuple)):
            benchmarks = [benchmarks]

        for bench in benchmarks:
            if isinstance(bench, str):
                if bench not in self.AVAILABLE_BENCHMARKS:
                    warnings.warn(f"Unknown benchmark '{bench}', skipping")
                    continue
                func_class, bounds_template = self.AVAILABLE_BENCHMARKS[bench]
                self.benchmark_configs[bench] = {
                    'function': func_class(),
                    'bounds': bounds_template * dimensions
                }
            elif callable(bench):
                # Custom function
                func_name = bench.__name__ if hasattr(bench, '__name__') else 'CustomFunc'
                self.benchmark_configs[func_name] = {
                    'function': bench,
                    'bounds': [(-100, 100)] * dimensions  # Default bounds
                }
        
        # Create experiment folder
        if experiment_name is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            experiment_name = f"experiment_{timestamp}"
        
        self.experiment_folder = Path(base_folder) / experiment_name
        self.experiment_folder.mkdir(parents=True, exist_ok=True)
        
        # Initialize visualizer
        self.viz = OptimizationVisualizer(figsize=(10, 6))
        
        # Storage for results
        self.results = {}
        self.is_run_complete = False
        
        # Configuration file
        self._save_config()
        
        print(f"Experiment initialized: {self.experiment_folder}")
        print(f"Benchmarks: {list(self.benchmark_configs.keys())}")
        print(f"Configuration: D={dimensions}, Runs={n_runs}, Pop={population_size}, Iter={max_iterations}")
    
    def _save_config(self):
        """Save experiment configuration to JSON file."""
        config = {
            'experiment_name': self.experiment_folder.name,
            'timestamp': datetime.now().isoformat(),
            'benchmarks': list(self.benchmark_configs.keys()),
            'dimensions': self.dimensions,
            'n_runs': self.n_runs,
            'population_size': self.population_size,
            'max_iterations': self.max_iterations,
            'F': self.F,
            'CR': self.CR,
            'seed': self.seed,
            'mutation': str(self.mutation) if self.mutation is not None else None
        }
        
        config_file = self.experiment_folder / 'config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def _build_mutation_instance(self):
        """Return a mutation strategy instance based on `self.mutation`.

        Supports:
        - None: returns default `DErand1(F=self.F)`
        - string: resolved from `pyrade.operators` by name
        - callable/class: attempted to instantiate with `F=self.F`, or called without args
        - instance: returned as-is
        """
        # Default
        if self.mutation is None:
            return DErand1(F=self.F)

        # If string, resolve from module
        if isinstance(self.mutation, str):
            try:
                import pyrade.operators as ops
                if hasattr(ops, self.mutation):
                    cls = getattr(ops, self.mutation)
                    try:
                        return cls(F=self.F)
                    except Exception:
                        try:
                            return cls()
                        except Exception:
                            warnings.warn(f"Could not instantiate mutation '{self.mutation}', using default")
                            return DErand1(F=self.F)
                else:
                    warnings.warn(f"Mutation strategy '{self.mutation}' not found in pyrade.operators; using default")
                    return DErand1(F=self.F)
            except Exception:
                warnings.warn(f"Error loading pyrade.operators; using default mutation")
                return DErand1(F=self.F)

        # If callable/class, try to instantiate
        if callable(self.mutation):
            try:
                return self.mutation(F=self.F)
            except TypeError:
                try:
                    return self.mutation()
                except Exception:
                    # If it's already an instance disguised as callable, fallback
                    return self.mutation

        # Otherwise, assume instance
        return self.mutation
    
    def run_experiments(self, verbose: bool = True, apply_visualizations: bool = False):
        """
        Run all experiments.
        
        Parameters
        ----------
        verbose : bool, default=True
            Print progress information
            
        Returns
        -------
        dict
            Results dictionary with statistics for each benchmark
        """
        if verbose:
            print("\n" + "=" * 80)
            print(f"STARTING EXPERIMENTS: {self.n_runs} runs × {len(self.benchmark_configs)} benchmarks")
            print("=" * 80 + "\n")
        
        start_time = datetime.now()
        
        for bench_name, bench_config in self.benchmark_configs.items():
            if verbose:
                print(f"Running {bench_name}...")
            
            bench_results = self._run_benchmark(
                bench_name,
                bench_config['function'],
                bench_config['bounds'],
                verbose=verbose
            )
            
            self.results[bench_name] = bench_results
            
            if verbose:
                print(f"  ✓ {bench_name} completed: Mean={bench_results['mean_fitness']:.6e}, "
                      f"Std={bench_results['std_fitness']:.6e}\n")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        self.is_run_complete = True
        
        if verbose:
            print("=" * 80)
            print(f"ALL EXPERIMENTS COMPLETED in {duration}")
            print("=" * 80 + "\n")
        
        # Optionally generate all visualizations immediately after running
        if apply_visualizations:
            try:
                self.plot_all()
            except Exception as e:
                warnings.warn(f"plot_all() failed after experiments: {e}")

        return self.results
    
    def _run_benchmark(self, bench_name: str, func: Callable, bounds: list, verbose: bool = False) -> Dict[str, Any]:
        """Run multiple optimization runs for a single benchmark."""
        logger.info(f"Starting benchmark: {bench_name} ({self.n_runs} runs)")
        
        convergence_histories = []
        final_fitness_values = []
        best_solutions = []
        execution_times = []
        
        # Create progress bar for runs if enabled
        run_iterator = range(self.n_runs)
        if self.show_progress:
            run_iterator = tqdm(run_iterator, desc=f"{bench_name}", unit="run", leave=False)
        
        for run in run_iterator:
            # Build mutation instance (respecting user config)
            mutation_instance = self._build_mutation_instance()

            # Run single optimization
            try:
                de = DifferentialEvolution(
                    objective_func=func,
                    bounds=np.array(bounds),
                    mutation=mutation_instance,
                    crossover=BinomialCrossover(CR=self.CR),
                    pop_size=self.population_size,
                    max_iter=self.max_iterations,
                    seed=self.seed + run,
                    verbose=False,
                    show_progress=False  # Don't show inner progress bar
                )
                
                result = de.optimize()
            except Exception as e:
                error_msg = f"Error in run {run+1}/{self.n_runs} for {bench_name}: {e}"
                logger.error(error_msg)
                if verbose:
                    print(f"  Warning: {error_msg}")
                continue
            
            # Store results
            final_fitness_values.append(result['best_fitness'])
            best_solutions.append(result['best_solution'])
            execution_times.append(result['time'])
            
            if 'history' in result and 'fitness' in result['history']:
                convergence_histories.append(result['history']['fitness'])
            else:
                convergence_histories.append([result['best_fitness']] * (self.max_iterations + 1))
            
            if verbose and not self.show_progress and (run + 1) % 10 == 0:
                print(f"    Completed {run + 1}/{self.n_runs} runs")
            
            logger.debug(f"Run {run+1}/{self.n_runs} complete: fitness={result['best_fitness']:.6e}")
        
        # Compute statistics with proper numerical handling
        final_fitness_array = np.array(final_fitness_values, dtype=np.float64)
        execution_times_array = np.array(execution_times, dtype=np.float64)
        
        # Filter out any inf/nan values for robust statistics
        valid_fitness = final_fitness_array[np.isfinite(final_fitness_array)]
        if len(valid_fitness) == 0:
            logger.warning(f"{bench_name}: No valid fitness values found (all inf/nan)")
            valid_fitness = final_fitness_array  # Use all if none are finite
        elif len(valid_fitness) < len(final_fitness_array):
            logger.warning(f"{bench_name}: {len(final_fitness_array) - len(valid_fitness)} runs had inf/nan fitness")
        
        # Compute robust statistics
        return {
            'convergence_histories': convergence_histories,
            'final_fitness': final_fitness_values,
            'best_solutions': best_solutions,
            'execution_times': execution_times,
            'mean_fitness': float(np.mean(valid_fitness)),
            'std_fitness': float(np.std(valid_fitness, ddof=1) if len(valid_fitness) > 1 else 0.0),
            'min_fitness': float(np.min(valid_fitness)),
            'max_fitness': float(np.max(valid_fitness)),
            'median_fitness': float(np.median(valid_fitness)),
            'q25_fitness': float(np.percentile(valid_fitness, 25)),
            'q75_fitness': float(np.percentile(valid_fitness, 75)),
            'mean_time': float(np.mean(execution_times_array)),
            'std_time': float(np.std(execution_times_array, ddof=1) if len(execution_times_array) > 1 else 0.0),
            'total_time': float(np.sum(execution_times_array)),
            'n_valid_runs': int(len(valid_fitness)),
            'n_total_runs': int(len(final_fitness_values))
        }
    
    def plot_convergence_curves(self, save: bool = True) -> Dict[str, plt.Figure]:
        """
        Generate convergence plots for each benchmark.
        
        Parameters
        ----------
        save : bool, default=True
            Save plots to experiment folder
            
        Returns
        -------
        dict
            Dictionary mapping benchmark names to figure objects
        """
        if not self.is_run_complete:
            raise RuntimeError("Run experiments first using run_experiments()")
        
        print("Generating convergence plots...")
        
        conv_folder = self.experiment_folder / "convergence_plots"
        conv_folder.mkdir(exist_ok=True)
        
        figures = {}
        
        for bench_name, data in self.results.items():
            fig = self.viz.plot_convergence_curve(
                history=data['convergence_histories'],
                title=f"{bench_name} Convergence (D={self.dimensions})",
                xlabel="Generation",
                ylabel="Best Fitness",
                log_scale=True,
                show_std=True,
                save_path=conv_folder / f"{bench_name.lower()}_convergence.png" if save else None
            )
            figures[bench_name] = fig
            if not save:
                plt.show()
            else:
                plt.close(fig)
        
        print(f"  ✓ Saved {len(figures)} convergence plots")
        return figures
    
    def plot_combined_convergence(self, save: bool = True) -> plt.Figure:
        """
        Plot all convergence curves on one figure.
        
        Parameters
        ----------
        save : bool, default=True
            Save plot to experiment folder
            
        Returns
        -------
        matplotlib.figure.Figure
            The created figure
        """
        if not self.is_run_complete:
            raise RuntimeError("Run experiments first using run_experiments()")
        
        print("Generating combined convergence plot...")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for bench_name, data in self.results.items():
            histories = np.array(data['convergence_histories'])
            mean_history = np.mean(histories, axis=0)
            generations = range(len(mean_history))
            
            ax.plot(generations, mean_history, marker='o', markersize=2,
                   linewidth=2, label=bench_name, alpha=0.8)
        
        ax.set_xlabel("Generation", fontsize=12)
        ax.set_ylabel("Mean Best Fitness", fontsize=12)
        ax.set_title(f"Convergence Comparison (D={self.dimensions}, {self.n_runs} runs)",
                    fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10, loc='best')
        plt.tight_layout()
        
        if save:
            save_path = self.experiment_folder / "all_convergence_combined.png"
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"  ✓ Saved combined convergence plot")
        else:
            plt.show()
        
        return fig
    
    def plot_boxplots(self, save: bool = True, split_scales: bool = True) -> List[plt.Figure]:
        """
        Generate boxplots comparing final fitness distributions.
        
        Parameters
        ----------
        save : bool, default=True
            Save plots to experiment folder
        split_scales : bool, default=True
            Create separate plots for different fitness scales
            
        Returns
        -------
        list of matplotlib.figure.Figure
            List of created figures
        """
        if not self.is_run_complete:
            raise RuntimeError("Run experiments first using run_experiments()")
        
        print("Generating boxplots...")
        
        figures = []
        
        # Main boxplot with all benchmarks
        fitness_data = {
            name: data['final_fitness']
            for name, data in self.results.items()
        }
        
        fig1 = self.viz.plot_fitness_boxplot(
            fitness_data=fitness_data,
            title=f"Final Fitness Distribution\n(D={self.dimensions}, Runs={self.n_runs})",
            ylabel="Final Best Fitness",
            save_path=self.experiment_folder / "fitness_boxplot_all.png" if save else None
        )
        figures.append(fig1)
        
        if not save:
            plt.show()
        else:
            plt.close(fig1)
        
        # Split by scale if requested
        if split_scales and len(self.results) > 3:
            # Group by fitness magnitude
            fitness_magnitudes = {
                name: np.log10(np.abs(data['mean_fitness']) + 1e-100)
                for name, data in self.results.items()
            }
            sorted_funcs = sorted(fitness_magnitudes.items(), key=lambda x: x[1])
            mid = len(sorted_funcs) // 2
            
            group1_data = {name: self.results[name]['final_fitness'] 
                          for name, _ in sorted_funcs[:mid]}
            group2_data = {name: self.results[name]['final_fitness'] 
                          for name, _ in sorted_funcs[mid:]}
            
            if group1_data:
                fig2 = self.viz.plot_fitness_boxplot(
                    fitness_data=group1_data,
                    title=f"Final Fitness - Lower Scale (Runs={self.n_runs})",
                    ylabel="Final Best Fitness",
                    save_path=self.experiment_folder / "fitness_boxplot_group1.png" if save else None
                )
                figures.append(fig2)
                if not save:
                    plt.show()
                else:
                    plt.close(fig2)
            
            if group2_data:
                fig3 = self.viz.plot_fitness_boxplot(
                    fitness_data=group2_data,
                    title=f"Final Fitness - Higher Scale (Runs={self.n_runs})",
                    ylabel="Final Best Fitness",
                    save_path=self.experiment_folder / "fitness_boxplot_group2.png" if save else None
                )
                figures.append(fig3)
                if not save:
                    plt.show()
                else:
                    plt.close(fig3)
        
        print(f"  ✓ Saved {len(figures)} boxplot(s)")
        return figures
    
    def plot_all(self):
        """Generate all available plots."""
        print("\n" + "=" * 80)
        print("GENERATING ALL VISUALIZATIONS")
        print("=" * 80 + "\n")
        # Core plots
        self.plot_convergence_curves(save=True)
        self.plot_combined_convergence(save=True)
        self.plot_boxplots(save=True, split_scales=True)

        # Additional parameter-space visualizations when data is available
        print("Generating parameter-space visualizations where applicable...")
        param_folder = self.experiment_folder / "parameter_visualizations"
        param_folder.mkdir(exist_ok=True)

        for bench_name, data in self.results.items():
            try:
                params = np.array(data.get('best_solutions'))  # shape: (n_runs, dim)
                fitness = np.array(data.get('final_fitness'))
                if params is None or fitness is None:
                    continue

                # Parameter heatmap
                try:
                    heatmap_path = param_folder / f"{bench_name.lower()}_parameter_heatmap.png"
                    self.viz.plot_parameter_heatmap(
                        parameters=params,
                        fitness=fitness,
                        param_names=[f'X{i+1}' for i in range(params.shape[1])],
                        title=f"{bench_name} Parameter Heatmap",
                        save_path=heatmap_path
                    )
                except Exception as e:
                    warnings.warn(f"Failed to create parameter heatmap for {bench_name}: {e}")

                # Parallel coordinates
                try:
                    pcp_path = param_folder / f"{bench_name.lower()}_parallel_coordinates.png"
                    self.viz.plot_parallel_coordinates(
                        parameters=params,
                        fitness=fitness,
                        param_names=[f'X{i+1}' for i in range(params.shape[1])],
                        normalize=True,
                        title=f"{bench_name} Parallel Coordinates",
                        save_path=pcp_path
                    )
                except Exception as e:
                    warnings.warn(f"Failed to create parallel coordinates for {bench_name}: {e}")

                # Contour landscape (only for 2D problems)
                try:
                    if self.dimensions == 2 and 'bounds' in self.benchmark_configs.get(bench_name, {}):
                        bounds_list = self.benchmark_configs[bench_name]['bounds']
                        # bounds_list is a list of tuples, convert to numpy array [[x_min,x_max],[y_min,y_max]]
                        b = np.array([bounds_list[0], bounds_list[1]])
                        contour_path = param_folder / f"{bench_name.lower()}_contour.png"
                        self.viz.plot_contour_landscape(
                            benchmark_func=self.benchmark_configs[bench_name]['function'],
                            bounds=b,
                            title=f"{bench_name} Contour Landscape",
                            save_path=contour_path
                        )
                except Exception as e:
                    warnings.warn(f"Failed to create contour landscape for {bench_name}: {e}")

            except Exception:
                # Skip if data is missing or malformed
                continue

        print("\n✓ All visualizations generated")
    
    def export_to_csv(self, detailed: bool = True):
        """
        Export results to CSV files.
        
        Parameters
        ----------
        detailed : bool, default=True
            Export detailed run-by-run data in addition to summary statistics
        """
        if not self.is_run_complete:
            raise RuntimeError("Run experiments first using run_experiments()")
        
        print("Exporting to CSV...")
        
        csv_folder = self.experiment_folder / "csv_exports"
        csv_folder.mkdir(exist_ok=True)
        
        # Summary statistics
        summary_data = []
        for bench_name, data in self.results.items():
            summary_data.append({
                'Benchmark': bench_name,
                'Mean_Fitness': data['mean_fitness'],
                'Std_Fitness': data['std_fitness'],
                'Min_Fitness': data['min_fitness'],
                'Max_Fitness': data['max_fitness'],
                'Median_Fitness': data['median_fitness'],
                'Mean_Time_sec': data['mean_time'],
                'Total_Time_sec': data['total_time']
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(csv_folder / "summary_statistics.csv", index=False)
        print(f"  ✓ Saved summary_statistics.csv")
        
        if detailed:
            # Detailed results for each benchmark
            for bench_name, data in self.results.items():
                detailed_data = {
                    'Run': list(range(1, self.n_runs + 1)),
                    'Final_Fitness': data['final_fitness'],
                    'Execution_Time_sec': data['execution_times']
                }
                
                # Add best solution components
                best_solutions = np.array(data['best_solutions'])
                for dim in range(self.dimensions):
                    detailed_data[f'X{dim+1}'] = best_solutions[:, dim]
                
                detailed_df = pd.DataFrame(detailed_data)
                filename = f"{bench_name.lower()}_detailed.csv"
                detailed_df.to_csv(csv_folder / filename, index=False)
            
            print(f"  ✓ Saved {len(self.results)} detailed CSV files")
            
            # Convergence data
            conv_folder = csv_folder / "convergence"
            conv_folder.mkdir(exist_ok=True)
            
            for bench_name, data in self.results.items():
                conv_array = np.array(data['convergence_histories'])
                conv_df = pd.DataFrame(
                    conv_array.T,
                    columns=[f'Run_{i+1}' for i in range(self.n_runs)]
                )
                conv_df.insert(0, 'Generation', range(len(conv_df)))
                filename = f"{bench_name.lower()}_convergence.csv"
                conv_df.to_csv(conv_folder / filename, index=False)
            
            print(f"  ✓ Saved {len(self.results)} convergence CSV files")
    
    def export_to_numpy(self):
        """Export raw data to NumPy .npy files."""
        if not self.is_run_complete:
            raise RuntimeError("Run experiments first using run_experiments()")
        
        print("Exporting to NumPy format...")
        
        numpy_folder = self.experiment_folder / "numpy_data"
        numpy_folder.mkdir(exist_ok=True)
        
        for bench_name, data in self.results.items():
            prefix = bench_name.lower()
            
            # Save convergence histories
            np.save(numpy_folder / f"{prefix}_convergence.npy",
                   np.array(data['convergence_histories']))
            
            # Save final fitness
            np.save(numpy_folder / f"{prefix}_final_fitness.npy",
                   np.array(data['final_fitness']))
            
            # Save best solutions
            np.save(numpy_folder / f"{prefix}_best_solutions.npy",
                   np.array(data['best_solutions']))
            
            # Save execution times
            np.save(numpy_folder / f"{prefix}_execution_times.npy",
                   np.array(data['execution_times']))
        
        print(f"  ✓ Saved {len(self.results) * 4} NumPy files")
    
    def export_results(self, formats: List[str] = None):
        """
        Export results in multiple formats.
        
        Parameters
        ----------
        formats : list of str, optional
            Export formats: 'csv', 'numpy', 'json'. Default: all formats
        """
        if formats is None:
            formats = ['csv', 'numpy', 'json']
        
        print("\n" + "=" * 80)
        print("EXPORTING RESULTS")
        print("=" * 80 + "\n")
        
        if 'csv' in formats:
            self.export_to_csv(detailed=True)
        
        if 'numpy' in formats:
            self.export_to_numpy()
        
        if 'json' in formats:
            self._export_to_json()
        
        print("\n✓ All exports completed")
    
    def _export_to_json(self):
        """Export summary statistics to JSON."""
        print("Exporting to JSON...")
        
        summary = {}
        for bench_name, data in self.results.items():
            summary[bench_name] = {
                'mean_fitness': float(data['mean_fitness']),
                'std_fitness': float(data['std_fitness']),
                'min_fitness': float(data['min_fitness']),
                'max_fitness': float(data['max_fitness']),
                'median_fitness': float(data['median_fitness']),
                'mean_time': float(data['mean_time']),
                'total_time': float(data['total_time'])
            }
        
        json_file = self.experiment_folder / "summary_results.json"
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"  ✓ Saved summary_results.json")
    
    def generate_report(self):
        """Generate a comprehensive text report."""
        if not self.is_run_complete:
            raise RuntimeError("Run experiments first using run_experiments()")
        
        print("Generating report...")
        
        report_file = self.experiment_folder / "experiment_report.txt"
        
        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("EXPERIMENT REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # Configuration
            f.write("Configuration:\n")
            f.write(f"  Experiment: {self.experiment_folder.name}\n")
            f.write(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  Dimensions: {self.dimensions}\n")
            f.write(f"  Population Size: {self.population_size}\n")
            f.write(f"  Max Iterations: {self.max_iterations}\n")
            f.write(f"  Number of Runs: {self.n_runs}\n")
            f.write(f"  F (Mutation): {self.F}\n")
            f.write(f"  CR (Crossover): {self.CR}\n")
            f.write(f"  Seed: {self.seed}\n\n")
            
            # Results table
            f.write("-" * 80 + "\n")
            f.write(f"{'Benchmark':<20} {'Mean':<15} {'Std':<15} {'Min':<15} {'Median':<15}\n")
            f.write("-" * 80 + "\n")
            
            for bench_name, data in sorted(self.results.items()):
                f.write(f"{bench_name:<20} "
                       f"{data['mean_fitness']:<15.6e} "
                       f"{data['std_fitness']:<15.6e} "
                       f"{data['min_fitness']:<15.6e} "
                       f"{data['median_fitness']:<15.6e}\n")
            
            f.write("-" * 80 + "\n\n")
            
            # Ranking
            f.write("Ranking by Mean Fitness:\n")
            ranked = sorted(self.results.items(), key=lambda x: x[1]['mean_fitness'])
            for rank, (bench_name, data) in enumerate(ranked, 1):
                f.write(f"  {rank:2d}. {bench_name:<20} {data['mean_fitness']:.6e}\n")
            
            f.write("\n" + "=" * 80 + "\n")
        
        print(f"  ✓ Saved experiment_report.txt")
        
        # Also print to console
        with open(report_file, 'r') as f:
            print("\n" + f.read())
    
    def run_complete_pipeline(self, verbose: bool = True):
        """
        Run the complete experimental pipeline: experiments → plots → exports → report.
        
        Parameters
        ----------
        verbose : bool, default=True
            Print progress information
        """
        start_time = datetime.now()
        
        print("\n" + "=" * 80)
        print("COMPLETE EXPERIMENTAL PIPELINE")
        print("=" * 80)
        print(f"Experiment: {self.experiment_folder.name}")
        print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")
        
        # Run experiments
        self.run_experiments(verbose=verbose)
        
        # Generate visualizations
        self.plot_all()
        
        # Export results
        self.export_results()
        
        # Generate report
        self.generate_report()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 80)
        print("PIPELINE COMPLETED!")
        print("=" * 80)
        print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Duration: {duration}")
        print(f"\nAll results saved to: {self.experiment_folder.absolute()}")
        print("=" * 80 + "\n")
    
    @staticmethod
    def list_available_benchmarks():
        """Print list of available benchmark functions."""
        print("\nAvailable Benchmark Functions:")
        print("-" * 40)
        for name in ExperimentManager.AVAILABLE_BENCHMARKS.keys():
            print(f"  - {name}")
        print("-" * 40)
