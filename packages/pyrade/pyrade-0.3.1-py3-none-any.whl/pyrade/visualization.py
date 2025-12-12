"""
Visualization utilities for PyRADE optimization results.

This module provides comprehensive visualization capabilities for analyzing
Differential Evolution optimization runs including convergence curves, fitness
distributions, parameter space exploration, and multi-objective results.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Dict, Optional, Tuple, Callable, Union
import warnings


class OptimizationVisualizer:
    """
    Comprehensive visualization toolkit for optimization results.
    
    Provides methods for creating various types of plots to analyze
    optimization performance, convergence, parameter distributions,
    and multi-objective results.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (10, 6), style: str = 'seaborn-v0_8-darkgrid'):
        """
        Initialize the visualizer.
        
        Parameters
        ----------
        figsize : tuple, optional
            Default figure size (width, height) in inches
        style : str, optional
            Matplotlib style to use for plots
        """
        self.figsize = figsize
        try:
            plt.style.use(style)
        except:
            warnings.warn(f"Style '{style}' not available, using default")
    
    def plot_convergence_curve(self, 
                               history: Union[List[float], Dict[str, List[float]]],
                               labels: Optional[List[str]] = None,
                               title: str = "Convergence Curve",
                               xlabel: str = "Generation",
                               ylabel: str = "Best Fitness",
                               log_scale: bool = False,
                               show_std: bool = False,
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot convergence curve(s) showing fitness improvement over generations.
        
        Parameters
        ----------
        history : list or dict
            Single list of fitness values or dict mapping labels to fitness lists
        labels : list of str, optional
            Labels for multiple convergence curves
        title : str, optional
            Plot title
        xlabel : str, optional
            X-axis label
        ylabel : str, optional
            Y-axis label
        log_scale : bool, optional
            Use logarithmic scale for y-axis
        show_std : bool, optional
            Show standard deviation bands (requires 2D array input)
        save_path : str, optional
            Path to save the figure
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure   
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Handle single or multiple convergence curves
        if isinstance(history, dict):
            for label, values in history.items():
                generations = range(len(values))
                ax.plot(generations, values, marker='o', markersize=3, 
                       label=label, linewidth=2)
        elif isinstance(history, list):
            if isinstance(history[0], (list, np.ndarray)) and show_std:
                # Multiple runs - show mean and std
                history_array = np.array(history)
                mean_fitness = np.mean(history_array, axis=0)
                std_fitness = np.std(history_array, axis=0)
                generations = range(len(mean_fitness))
                
                ax.plot(generations, mean_fitness, marker='o', markersize=3,
                       label='Mean', linewidth=2)
                ax.fill_between(generations, 
                               mean_fitness - std_fitness,
                               mean_fitness + std_fitness,
                               alpha=0.3, label='±1 Std Dev')
            else:
                # Single run
                generations = range(len(history))
                ax.plot(generations, history, marker='o', markersize=3,
                       linewidth=2, label=labels[0] if labels else 'Best Fitness')
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        if log_scale:
            ax.set_yscale('log')
        
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_fitness_boxplot(self,
                            fitness_data: Dict[str, List[float]],
                            title: str = "Fitness Distribution Comparison",
                            ylabel: str = "Fitness Value",
                            save_path: Optional[str] = None) -> plt.Figure:
        """
        Create boxplot comparing fitness distributions across algorithms/runs.
        
        Parameters
        ----------
        fitness_data : dict
            Dictionary mapping algorithm/strategy names to lists of fitness values
        title : str, optional
            Plot title
        ylabel : str, optional
            Y-axis label
        save_path : str, optional
            Path to save the figure
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        labels = list(fitness_data.keys())
        data = [fitness_data[label] for label in labels]
        
        bp = ax.boxplot(data, labels=labels, patch_artist=True,
                       showmeans=True, meanline=True)
        
        # Color the boxes
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        # Customize appearance
        for element in ['whiskers', 'fliers', 'means', 'medians', 'caps']:
            plt.setp(bp[element], linewidth=1.5)
        
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3)
        
        # Rotate x-axis labels if many algorithms
        if len(labels) > 5:
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_2d_pareto_front(self,
                            objectives: np.ndarray,
                            pareto_front: Optional[np.ndarray] = None,
                            title: str = "2D Pareto Front",
                            xlabel: str = "Objective 1",
                            ylabel: str = "Objective 2",
                            save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot 2D Pareto front scatter plot.
        
        Parameters
        ----------
        objectives : ndarray of shape (n_solutions, 2)
            Two-objective values for each solution
        pareto_front : ndarray, optional
            Indices or boolean mask of Pareto-optimal solutions
        title : str, optional
            Plot title
        xlabel : str, optional
            X-axis label (objective 1)
        ylabel : str, optional
            Y-axis label (objective 2)
        save_path : str, optional
            Path to save the figure
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot all solutions
        ax.scatter(objectives[:, 0], objectives[:, 1], 
                  c='lightblue', s=50, alpha=0.6, 
                  edgecolors='black', linewidth=0.5,
                  label='All Solutions')
        
        # Highlight Pareto front if provided
        if pareto_front is not None:
            if pareto_front.dtype == bool:
                pareto_obj = objectives[pareto_front]
            else:
                pareto_obj = objectives[pareto_front]
            
            # Sort for line connection
            sorted_idx = np.argsort(pareto_obj[:, 0])
            pareto_obj = pareto_obj[sorted_idx]
            
            ax.scatter(pareto_obj[:, 0], pareto_obj[:, 1],
                      c='red', s=100, alpha=0.8,
                      edgecolors='darkred', linewidth=1.5,
                      label='Pareto Front', zorder=5)
            ax.plot(pareto_obj[:, 0], pareto_obj[:, 1],
                   'r--', linewidth=2, alpha=0.5, zorder=4)
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_3d_pareto_front(self,
                            objectives: np.ndarray,
                            pareto_front: Optional[np.ndarray] = None,
                            title: str = "3D Pareto Front",
                            labels: Tuple[str, str, str] = ("Obj 1", "Obj 2", "Obj 3"),
                            save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot 3D Pareto front scatter plot.
        
        Parameters
        ----------
        objectives : ndarray of shape (n_solutions, 3)
            Three-objective values for each solution
        pareto_front : ndarray, optional
            Indices or boolean mask of Pareto-optimal solutions
        title : str, optional
            Plot title
        labels : tuple of str, optional
            Labels for the three axes
        save_path : str, optional
            Path to save the figure
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure
        """
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot all solutions
        ax.scatter(objectives[:, 0], objectives[:, 1], objectives[:, 2],
                  c='lightblue', s=30, alpha=0.4,
                  edgecolors='black', linewidth=0.3,
                  label='All Solutions')
        
        # Highlight Pareto front if provided
        if pareto_front is not None:
            if pareto_front.dtype == bool:
                pareto_obj = objectives[pareto_front]
            else:
                pareto_obj = objectives[pareto_front]
            
            ax.scatter(pareto_obj[:, 0], pareto_obj[:, 1], pareto_obj[:, 2],
                      c='red', s=80, alpha=0.9,
                      edgecolors='darkred', linewidth=1,
                      label='Pareto Front', zorder=5)
        
        ax.set_xlabel(labels[0], fontsize=11)
        ax.set_ylabel(labels[1], fontsize=11)
        ax.set_zlabel(labels[2], fontsize=11)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_parameter_heatmap(self,
                              parameters: np.ndarray,
                              fitness: np.ndarray,
                              param_names: Optional[List[str]] = None,
                              title: str = "Parameter Value Heatmap",
                              cmap: str = 'viridis',
                              save_path: Optional[str] = None) -> plt.Figure:
        """
        Create heatmap showing parameter values across population.
        
        Parameters
        ----------
        parameters : ndarray of shape (n_individuals, n_parameters)
            Parameter values for each individual
        fitness : ndarray of shape (n_individuals,)
            Fitness value for each individual
        param_names : list of str, optional
            Names of parameters
        title : str, optional
            Plot title
        cmap : str, optional
            Colormap name
        save_path : str, optional
            Path to save the figure
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure
        """
        # Sort individuals by fitness
        sorted_idx = np.argsort(fitness)
        sorted_params = parameters[sorted_idx]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        im = ax.imshow(sorted_params.T, aspect='auto', cmap=cmap,
                      interpolation='nearest')
        
        # Set labels
        ax.set_xlabel('Individual (sorted by fitness)', fontsize=12)
        ax.set_ylabel('Parameter', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Set y-axis ticks
        if param_names:
            ax.set_yticks(range(len(param_names)))
            ax.set_yticklabels(param_names)
        else:
            ax.set_yticks(range(parameters.shape[1]))
            ax.set_yticklabels([f'P{i}' for i in range(parameters.shape[1])])
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Parameter Value', fontsize=11)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_parallel_coordinates(self,
                                 parameters: np.ndarray,
                                 fitness: np.ndarray,
                                 param_names: Optional[List[str]] = None,
                                 normalize: bool = True,
                                 title: str = "Parallel Coordinate Plot",
                                 cmap: str = 'RdYlGn_r',
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        Create parallel coordinate plot for parameter space exploration.
        
        Parameters
        ----------
        parameters : ndarray of shape (n_individuals, n_parameters)
            Parameter values for each individual
        fitness : ndarray of shape (n_individuals,)
            Fitness value for each individual
        param_names : list of str, optional
            Names of parameters
        normalize : bool, optional
            Normalize each parameter to [0, 1]
        title : str, optional
            Plot title
        cmap : str, optional
            Colormap for fitness coloring
        save_path : str, optional
            Path to save the figure
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure
        """
        n_individuals, n_params = parameters.shape
        
        # Normalize parameters if requested
        if normalize:
            params_normalized = (parameters - parameters.min(axis=0)) / \
                              (parameters.max(axis=0) - parameters.min(axis=0) + 1e-10)
        else:
            params_normalized = parameters.copy()
        
        # Normalize fitness for coloring
        fitness_norm = (fitness - fitness.min()) / (fitness.max() - fitness.min() + 1e-10)
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # Create colormap
        colormap = cm.get_cmap(cmap)
        
        # Plot each individual
        x = range(n_params)
        for i in range(n_individuals):
            color = colormap(fitness_norm[i])
            ax.plot(x, params_normalized[i], c=color, alpha=0.3, linewidth=1)
        
        # Set axis labels
        ax.set_xticks(x)
        if param_names:
            ax.set_xticklabels(param_names, rotation=45, ha='right')
        else:
            ax.set_xticklabels([f'P{i}' for i in range(n_params)])
        
        ax.set_ylabel('Normalized Value' if normalize else 'Value', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3)
        
        # Add colorbar
        sm = cm.ScalarMappable(cmap=colormap, 
                              norm=plt.Normalize(vmin=fitness.min(), 
                                               vmax=fitness.max()))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label('Fitness', fontsize=11)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_contour_landscape(self,
                              benchmark_func: Callable,
                              bounds: np.ndarray,
                              optimal_point: Optional[np.ndarray] = None,
                              trajectory: Optional[np.ndarray] = None,
                              resolution: int = 100,
                              title: str = "Optimization Landscape",
                              cmap: str = 'terrain',
                              save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot contour map of 2D benchmark function landscape.
        
        Parameters
        ----------
        benchmark_func : callable
            Function that takes (x, y) and returns fitness value
        bounds : ndarray of shape (2, 2)
            [[x_min, x_max], [y_min, y_max]]
        optimal_point : ndarray, optional
            Location of global optimum [x, y]
        trajectory : ndarray, optional
            Shape (n_iterations, 2) - optimization trajectory to overlay
        resolution : int, optional
            Grid resolution for contour plot
        title : str, optional
            Plot title
        cmap : str, optional
            Colormap name
        save_path : str, optional
            Path to save the figure
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create mesh grid
        x = np.linspace(bounds[0, 0], bounds[0, 1], resolution)
        y = np.linspace(bounds[1, 0], bounds[1, 1], resolution)
        X, Y = np.meshgrid(x, y)
        
        # Evaluate function
        Z = np.zeros_like(X)
        for i in range(resolution):
            for j in range(resolution):
                point = np.array([X[i, j], Y[i, j]])
                Z[i, j] = benchmark_func(point)
        
        # Create contour plot
        contour = ax.contourf(X, Y, Z, levels=50, cmap=cmap, alpha=0.8)
        contour_lines = ax.contour(X, Y, Z, levels=20, colors='black', 
                                   alpha=0.3, linewidths=0.5)
        
        # Add colorbar
        cbar = plt.colorbar(contour, ax=ax)
        cbar.set_label('Fitness Value', fontsize=11)
        
        # Mark optimal point
        if optimal_point is not None:
            ax.plot(optimal_point[0], optimal_point[1], 'r*', 
                   markersize=20, label='Global Optimum',
                   markeredgecolor='white', markeredgewidth=1.5)
        
        # Overlay trajectory
        if trajectory is not None:
            ax.plot(trajectory[:, 0], trajectory[:, 1], 
                   'wo-', linewidth=2, markersize=6,
                   markeredgecolor='black', markeredgewidth=1,
                   label='Optimization Path', alpha=0.8)
            ax.plot(trajectory[0, 0], trajectory[0, 1],
                   'go', markersize=10, label='Start',
                   markeredgecolor='white', markeredgewidth=1.5)
            ax.plot(trajectory[-1, 0], trajectory[-1, 1],
                   'rs', markersize=10, label='End',
                   markeredgecolor='white', markeredgewidth=1.5)
        
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        if optimal_point is not None or trajectory is not None:
            ax.legend(fontsize=10, loc='best')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_hypervolume_progress(self,
                                 hypervolume_history: List[float],
                                 title: str = "Hypervolume Indicator Progress",
                                 xlabel: str = "Generation",
                                 ylabel: str = "Hypervolume",
                                 reference_hv: Optional[float] = None,
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot hypervolume indicator over iterations.
        
        Parameters
        ----------
        hypervolume_history : list of float
            Hypervolume values at each generation
        title : str, optional
            Plot title
        xlabel : str, optional
            X-axis label
        ylabel : str, optional
            Y-axis label
        reference_hv : float, optional
            Reference hypervolume (e.g., true Pareto front) to plot as baseline
        save_path : str, optional
            Path to save the figure
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        generations = range(len(hypervolume_history))
        ax.plot(generations, hypervolume_history, 
               marker='o', markersize=4, linewidth=2,
               color='blue', label='Hypervolume')
        
        # Add reference line if provided
        if reference_hv is not None:
            ax.axhline(y=reference_hv, color='red', linestyle='--',
                      linewidth=2, label='Reference HV', alpha=0.7)
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_igd_progress(self,
                         igd_history: List[float],
                         title: str = "IGD Metric Progress",
                         xlabel: str = "Generation",
                         ylabel: str = "IGD (lower is better)",
                         log_scale: bool = False,
                         save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot Inverted Generational Distance (IGD) over iterations.
        
        Parameters
        ----------
        igd_history : list of float
            IGD values at each generation
        title : str, optional
            Plot title
        xlabel : str, optional
            X-axis label
        ylabel : str, optional
            Y-axis label
        log_scale : bool, optional
            Use logarithmic scale for y-axis
        save_path : str, optional
            Path to save the figure
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        generations = range(len(igd_history))
        ax.plot(generations, igd_history,
               marker='s', markersize=4, linewidth=2,
               color='green', label='IGD')
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        if log_scale:
            ax.set_yscale('log')
        
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_population_diversity(self,
                                 diversity_history: Union[List[float], Dict[str, List[float]]],
                                 title: str = "Population Diversity Over Time",
                                 xlabel: str = "Generation",
                                 ylabel: str = "Diversity Metric",
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot population diversity metrics over iterations.
        
        Parameters
        ----------
        diversity_history : list or dict
            Single list or dict mapping metric names to diversity values
        title : str, optional
            Plot title
        xlabel : str, optional
            X-axis label
        ylabel : str, optional
            Y-axis label
        save_path : str, optional
            Path to save the figure
            
        Returns
        -------
        fig : matplotlib.figure.Figure
            The created figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if isinstance(diversity_history, dict):
            for metric_name, values in diversity_history.items():
                generations = range(len(values))
                ax.plot(generations, values, marker='o', markersize=3,
                       linewidth=2, label=metric_name)
        else:
            generations = range(len(diversity_history))
            ax.plot(generations, diversity_history, marker='o', markersize=3,
                   linewidth=2, label='Diversity')
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig


def calculate_hypervolume_2d(objectives: np.ndarray, reference_point: np.ndarray) -> float:
    """
    Calculate hypervolume indicator for 2D objectives (minimization).
    
    Parameters
    ----------
    objectives : ndarray of shape (n_points, 2)
        Objective values
    reference_point : ndarray of shape (2,)
        Reference point (should dominate all solutions)
        
    Returns
    -------
    float
        Hypervolume value
    """
    # Sort by first objective
    sorted_idx = np.argsort(objectives[:, 0])
    sorted_obj = objectives[sorted_idx]
    
    hypervolume = 0.0
    prev_x = reference_point[0]
    
    for i in range(len(sorted_obj)):
        width = prev_x - sorted_obj[i, 0]
        height = reference_point[1] - sorted_obj[i, 1]
        hypervolume += width * height
        prev_x = sorted_obj[i, 0]
    
    return hypervolume


def calculate_igd(obtained_front: np.ndarray, true_front: np.ndarray) -> float:
    """
    Calculate Inverted Generational Distance (IGD).
    
    Parameters
    ----------
    obtained_front : ndarray of shape (n_obtained, n_objectives)
        Obtained Pareto front approximation
    true_front : ndarray of shape (n_true, n_objectives)
        True Pareto front
        
    Returns
    -------
    float
        IGD value (lower is better)
    """
    distances = []
    for true_point in true_front:
        min_dist = np.min(np.linalg.norm(obtained_front - true_point, axis=1))
        distances.append(min_dist)
    
    return np.mean(distances)


def is_pareto_efficient(costs: np.ndarray) -> np.ndarray:
    """
    Find Pareto efficient solutions (minimization).
    
    Parameters
    ----------
    costs : ndarray of shape (n_points, n_objectives)
        Objective values for each solution
        
    Returns
    -------
    ndarray of shape (n_points,)
        Boolean array indicating Pareto-efficient solutions
    """
    is_efficient = np.ones(costs.shape[0], dtype=bool)
    
    for i, cost in enumerate(costs):
        if is_efficient[i]:
            # Check if any other solution dominates this one
            is_efficient[is_efficient] = np.any(
                costs[is_efficient] < cost, axis=1
            ) | np.all(
                costs[is_efficient] <= cost, axis=1
            ) == False
            is_efficient[i] = True
    
    return is_efficient
