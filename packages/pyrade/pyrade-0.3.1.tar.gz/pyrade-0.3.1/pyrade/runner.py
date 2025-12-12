"""
PyRADE Experiment Runner

All experiment execution logic - keeps main.py simple!
"""

import numpy as np
from datetime import datetime
import os
import csv
import matplotlib.pyplot as plt
from pyrade.visualization import OptimizationVisualizer


def run_experiment(algorithm, benchmark, dimensions=30, bounds=(-100, 100), num_runs=1,
                   pop_size=50, max_iter=1000, F=0.8, CR=0.9, seed=42,
                   output_dir="experimental", viz_preset='all', verbose=True):
    """
    Run optimization experiment with automatic visualization and CSV export.
    
    Returns: result dict (single run) or (stats dict, all results) (multiple runs)
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_folder = os.path.join(output_dir, timestamp)
    os.makedirs(exp_folder, exist_ok=True)
    
    func_name = getattr(benchmark, 'name', None) or getattr(benchmark, '__name__', None) or str(benchmark.__class__.__name__)
    
    if hasattr(benchmark, 'get_bounds_array'):
        bounds_array = benchmark.get_bounds_array()
    elif isinstance(bounds, tuple):
        bounds_array = [bounds] * dimensions
    else:
        bounds_array = bounds
    
    viz_config = _get_viz_config(viz_preset)
    visualizer = OptimizationVisualizer()
    
    if verbose:
        print("=" * 80)
        print(f"PyRADE Experiment - {timestamp}")
        print("=" * 80)
        print(f"Algorithm:   {algorithm.__name__}")
        print(f"Function:    {func_name}")
        print(f"Dimensions:  {dimensions}")
        print(f"Runs:        {num_runs}")
        print(f"Output:      {exp_folder}")
        print("=" * 80)
    
    if num_runs == 1:
        return _run_single(algorithm, benchmark, bounds_array, pop_size, max_iter, F, CR, seed,
                          exp_folder, func_name, dimensions, viz_config, visualizer, verbose)
    else:
        return _run_multiple(algorithm, benchmark, bounds_array, pop_size, max_iter, F, CR, seed,
                            num_runs, exp_folder, func_name, dimensions, viz_config, visualizer, verbose)


def compare_algorithms(algorithms, benchmark, dimensions=30, bounds=(-100, 100), num_runs=10,
                      pop_size=50, max_iter=1000, F=0.8, CR=0.9, seed=42,
                      output_dir="experimental", viz_preset='all', verbose=True):
    """Compare multiple algorithms on the same benchmark."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_folder = os.path.join(output_dir, timestamp)
    os.makedirs(exp_folder, exist_ok=True)
    
    func_name = getattr(benchmark, 'name', None) or getattr(benchmark, '__name__', None) or str(benchmark.__class__.__name__)
    
    if hasattr(benchmark, 'get_bounds_array'):
        bounds_array = benchmark.get_bounds_array()
    elif isinstance(bounds, tuple):
        bounds_array = [bounds] * dimensions
    else:
        bounds_array = bounds
    
    if verbose:
        print("=" * 80)
        print(f"Algorithm Comparison - {timestamp}")
        print("=" * 80)
        print(f"Function:    {func_name}")
        print(f"Algorithms:  {len(algorithms)}")
        print(f"Runs/algo:   {num_runs}")
        print("=" * 80)
    
    results = {}
    histories = {}
    
    for algo in algorithms:
        if verbose: print(f"\nTesting {algo.__name__}...")
        
        algo_results = []
        algo_histories = []
        
        for run in range(num_runs):
            optimizer = algo(
                objective_func=benchmark, bounds=bounds_array, pop_size=pop_size,
                max_iter=max_iter, F=F, CR=CR, seed=seed + run if seed else None, verbose=False
            )
            
            result = optimizer.optimize()
            algo_results.append(result['best_fitness'])
            if 'history' in result and isinstance(result['history'], dict):
                algo_histories.append(result['history']['fitness'])
        
        results[algo.__name__] = np.array(algo_results)
        if algo_histories:
            histories[algo.__name__] = np.array(algo_histories)
        
        if verbose:
            print(f"  Mean: {np.mean(algo_results):.6e}, Best: {np.min(algo_results):.6e}")
    
    _save_comparison_results(results, exp_folder, func_name, dimensions, num_runs, pop_size, max_iter)
    
    viz_config = _get_viz_config(viz_preset)
    _plot_comparison(results, histories, exp_folder, func_name, num_runs, viz_config, verbose)
    
    if verbose:
        print("\n" + "=" * 80)
        print(f"Results in: {exp_folder}")
        print("=" * 80)
    
    return results


def _get_viz_config(preset):
    """Parse visualization preset."""
    presets = {
        'all': {k: True for k in ['convergence_curve', 'fitness_boxplot', 'parameter_heatmap', 'parallel_coordinates', 'population_diversity', 'contour_landscape', 'pareto_front_2d', 'pareto_front_3d', 'hypervolume_progress', 'igd_progress']},
        'basic': {'convergence_curve': True, 'fitness_boxplot': True, 'parameter_heatmap': False, 'parallel_coordinates': False, 'population_diversity': False, 'contour_landscape': False, 'pareto_front_2d': False, 'pareto_front_3d': False, 'hypervolume_progress': False, 'igd_progress': False},
        'research': {'convergence_curve': True, 'fitness_boxplot': True, 'parameter_heatmap': True, 'parallel_coordinates': True, 'population_diversity': True, 'contour_landscape': False, 'pareto_front_2d': False, 'pareto_front_3d': False, 'hypervolume_progress': False, 'igd_progress': False},
        'none': {k: False for k in ['convergence_curve', 'fitness_boxplot', 'parameter_heatmap', 'parallel_coordinates', 'population_diversity', 'contour_landscape', 'pareto_front_2d', 'pareto_front_3d', 'hypervolume_progress', 'igd_progress']}
    }
    return presets.get(preset.lower(), presets['basic'])


def _run_single(algorithm, benchmark, bounds, pop_size, max_iter, F, CR, seed, exp_folder, func_name, dimensions, viz_config, visualizer, verbose):
    """Single run."""
    optimizer = algorithm(objective_func=benchmark, bounds=bounds, pop_size=pop_size, max_iter=max_iter, F=F, CR=CR, seed=seed, verbose=verbose)
    result = optimizer.optimize()
    
    if verbose:
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"Best Fitness:  {result['best_fitness']:.6e}")
        print(f"Time:          {result['time']:.3f}s")
        print("=" * 80)
    
    _save_single_results(result, exp_folder, algorithm.__name__, func_name, dimensions, pop_size, max_iter, F, CR)
    
    if verbose:
        print("\n" + "=" * 80)
        print("GENERATING VISUALIZATIONS")
        print("=" * 80)
    
    plots = 0
    
    # Convergence
    if viz_config.get('convergence_curve') and 'history' in result:
        try:
            fig = visualizer.plot_convergence_curve(result['history'])
            plt.title(f"{algorithm.__name__} on {func_name}")
            plt.savefig(f"{exp_folder}/convergence.png", dpi=150, bbox_inches='tight')
            plt.close()
            if verbose: print("✓ convergence.png")
            plots += 1
        except: pass
    
    # Solution parameters
    if viz_config.get('parameter_heatmap') and len(result['best_solution']) <= 50:
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.bar(range(len(result['best_solution'])), result['best_solution'], alpha=0.7, edgecolor='black')
            ax.set_xlabel('Dimension')
            ax.set_ylabel('Value')
            ax.set_title(f'Solution Parameters - {func_name}')
            ax.grid(True, alpha=0.3)
            plt.savefig(f"{exp_folder}/solution_parameters.png", dpi=150, bbox_inches='tight')
            plt.close()
            if verbose: print("✓ solution_parameters.png")
            plots += 1
        except: pass
    
    # Convergence analysis (log + linear)
    if viz_config.get('convergence_curve') and 'history' in result:
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            fitness = result['history']['fitness']
            iterations = range(len(fitness))
            
            ax1.semilogy(iterations, fitness, 'b-', linewidth=2)
            ax1.set_xlabel('Iteration')
            ax1.set_ylabel('Best Fitness (log)')
            ax1.set_title(f'Convergence (Log) - {func_name}')
            ax1.grid(True, alpha=0.3)
            
            ax2.plot(iterations, fitness, 'g-', linewidth=2)
            ax2.set_xlabel('Iteration')
            ax2.set_ylabel('Best Fitness')
            ax2.set_title(f'Convergence (Linear) - {func_name}')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f"{exp_folder}/convergence_analysis.png", dpi=150, bbox_inches='tight')
            plt.close()
            if verbose: print("✓ convergence_analysis.png")
            plots += 1
        except: pass
    
    # Improvement rate
    if viz_config.get('population_diversity') and 'history' in result:
        try:
            fitness = np.array(result['history']['fitness'])
            improvements = np.diff(fitness)
            rate = np.abs(improvements) / (fitness[:-1] + 1e-10)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(rate, 'r-', linewidth=2)
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Improvement Rate')
            ax.set_title(f'Improvement Rate - {func_name}')
            ax.set_yscale('log')
            ax.grid(True, alpha=0.3)
            plt.savefig(f"{exp_folder}/improvement_rate.png", dpi=150, bbox_inches='tight')
            plt.close()
            if verbose: print("✓ improvement_rate.png")
            plots += 1
        except: pass
    
    if verbose:
        print(f"\nTotal plots: {plots}")
        print("=" * 80)
    
    return result


def _run_multiple(algorithm, benchmark, bounds, pop_size, max_iter, F, CR, seed, num_runs, exp_folder, func_name, dimensions, viz_config, visualizer, verbose):
    """Multiple runs with statistics."""
    all_fitness = []
    all_histories = []
    
    for run in range(num_runs):
        if verbose: print(f"\nRun {run + 1}/{num_runs}...", end=" ")
        
        optimizer = algorithm(objective_func=benchmark, bounds=bounds, pop_size=pop_size, max_iter=max_iter, F=F, CR=CR, seed=seed + run if seed else None, verbose=False)
        result = optimizer.optimize()
        all_fitness.append(result['best_fitness'])
        if 'history' in result:
            all_histories.append(result['history'])
        
        if verbose: print(f"Best: {result['best_fitness']:.6e}")
    
    fitness = np.array(all_fitness)
    
    if verbose:
        print("\n" + "=" * 80)
        print("STATISTICAL RESULTS")
        print("=" * 80)
        print(f"Best:    {np.min(fitness):.6e}")
        print(f"Mean:    {np.mean(fitness):.6e}")
        print(f"Median:  {np.median(fitness):.6e}")
        print(f"Worst:   {np.max(fitness):.6e}")
        print(f"Std Dev: {np.std(fitness):.6e}")
        print("=" * 80)
    
    _save_multiple_results(fitness, exp_folder, algorithm.__name__, func_name, dimensions, num_runs, pop_size, max_iter, F, CR)
    
    if verbose:
        print("\n" + "=" * 80)
        print("GENERATING VISUALIZATIONS")
        print("=" * 80)
    
    plots = _plot_multiple_runs(all_histories, fitness, exp_folder, func_name, algorithm.__name__, num_runs, viz_config, verbose)
    
    if verbose:
        print(f"\nTotal plots: {plots}")
        print("=" * 80)
    
    return ({'best': np.min(fitness), 'mean': np.mean(fitness), 'std': np.std(fitness), 'median': np.median(fitness), 'worst': np.max(fitness)}, all_fitness)


def _save_single_results(result, folder, algo_name, func_name, dims, pop, iters, F, CR):
    """Save single run CSV."""
    with open(f"{folder}/single_run_results.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Algorithm', algo_name])
        writer.writerow(['Function', func_name])
        writer.writerow(['Dimensions', dims])
        writer.writerow(['Population', pop])
        writer.writerow(['Iterations', iters])
        writer.writerow(['F', F])
        writer.writerow(['CR', CR])
        writer.writerow(['Best Fitness', result['best_fitness']])
        writer.writerow(['Time (s)', result['time']])
    
    if 'history' in result:
        with open(f"{folder}/convergence_history.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Iteration', 'Fitness', 'Time'])
            for i, (fit, t) in enumerate(zip(result['history']['fitness'], result['history']['time'])):
                writer.writerow([i, fit, t])


def _save_multiple_results(fitness, folder, algo_name, func_name, dims, runs, pop, iters, F, CR):
    """Save multiple runs CSV."""
    with open(f"{folder}/statistics.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Algorithm', algo_name])
        writer.writerow(['Function', func_name])
        writer.writerow(['Dimensions', dims])
        writer.writerow(['Runs', runs])
        writer.writerow(['Population', pop])
        writer.writerow(['Iterations', iters])
        writer.writerow(['F', F])
        writer.writerow(['CR', CR])
        writer.writerow([''])
        writer.writerow(['Best', np.min(fitness)])
        writer.writerow(['Mean', np.mean(fitness)])
        writer.writerow(['Median', np.median(fitness)])
        writer.writerow(['Worst', np.max(fitness)])
        writer.writerow(['Std Dev', np.std(fitness)])
    
    with open(f"{folder}/all_runs.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Run', 'Fitness'])
        for i, fit in enumerate(fitness, 1):
            writer.writerow([i, fit])


def _save_comparison_results(results, folder, func_name, dims, runs, pop, iters):
    """Save comparison CSV."""
    with open(f"{folder}/comparison_summary.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Function', func_name])
        writer.writerow(['Dimensions', dims])
        writer.writerow(['Runs', runs])
        writer.writerow(['Population', pop])
        writer.writerow(['Iterations', iters])
        writer.writerow([''])
        writer.writerow(['Algorithm', 'Best', 'Mean', 'Median', 'Worst', 'Std Dev'])
        for name, fitness in results.items():
            writer.writerow([name, np.min(fitness), np.mean(fitness), np.median(fitness), np.max(fitness), np.std(fitness)])
    
    with open(f"{folder}/comparison_detailed.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        header = ['Run'] + list(results.keys())
        writer.writerow(header)
        for i in range(len(next(iter(results.values())))):
            row = [i + 1] + [results[name][i] for name in results.keys()]
            writer.writerow(row)


def _plot_multiple_runs(histories, fitness, folder, func_name, algo_name, num_runs, viz_config, verbose):
    """Plot multiple runs."""
    plots = 0
    
    # Convergence curves
    if viz_config.get('convergence_curve') and histories:
        try:
            plt.figure(figsize=(10, 6))
            fitness_histories = []
            for h in histories:
                if isinstance(h, dict) and 'fitness' in h:
                    fitness_histories.append(h['fitness'])
                    plt.semilogy(h['fitness'], alpha=0.3, color='blue')
            
            if fitness_histories:
                mean_hist = np.mean(fitness_histories, axis=0)
                plt.semilogy(mean_hist, 'r-', linewidth=2, label='Mean')
            
            plt.xlabel('Iteration')
            plt.ylabel('Best Fitness (log)')
            plt.title(f'{algo_name} on {func_name} ({num_runs} runs)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(f"{folder}/convergence_multiple_runs.png", dpi=150, bbox_inches='tight')
            plt.close()
            if verbose: print("✓ convergence_multiple_runs.png")
            plots += 1
        except: pass
    
    # Boxplot
    if viz_config.get('fitness_boxplot'):
        try:
            plt.figure(figsize=(8, 6))
            plt.boxplot(fitness, vert=True)
            plt.ylabel('Best Fitness')
            plt.title(f'Distribution - {algo_name} on {func_name}')
            plt.grid(True, alpha=0.3)
            plt.savefig(f"{folder}/boxplot.png", dpi=150, bbox_inches='tight')
            plt.close()
            if verbose: print("✓ boxplot.png")
            plots += 1
        except: pass
    
    # Violin plot
    if viz_config.get('fitness_boxplot') and len(fitness) >= 5:
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.violinplot([fitness], vert=True, showmeans=True, showmedians=True)
            ax.set_ylabel('Best Fitness')
            ax.set_title(f'Violin Plot - {algo_name} on {func_name}')
            ax.grid(True, alpha=0.3, axis='y')
            plt.savefig(f"{folder}/violin.png", dpi=150, bbox_inches='tight')
            plt.close()
            if verbose: print("✓ violin.png")
            plots += 1
        except: pass
    
    # Statistical summary
    if viz_config.get('fitness_boxplot'):
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            stats = {'Best': np.min(fitness), 'Q1': np.percentile(fitness, 25), 'Median': np.median(fitness), 'Mean': np.mean(fitness), 'Q3': np.percentile(fitness, 75), 'Worst': np.max(fitness)}
            ax.barh(list(stats.keys()), list(stats.values()), alpha=0.7, edgecolor='black')
            ax.set_xlabel('Fitness')
            ax.set_title(f'Statistics - {algo_name} on {func_name}')
            ax.grid(True, alpha=0.3, axis='x')
            plt.savefig(f"{folder}/statistics.png", dpi=150, bbox_inches='tight')
            plt.close()
            if verbose: print("✓ statistics.png")
            plots += 1
        except: pass
    
    # Convergence uncertainty
    if viz_config.get('convergence_curve') and histories:
        try:
            fitness_histories = []
            for h in histories:
                if isinstance(h, dict) and 'fitness' in h:
                    fitness_histories.append(h['fitness'])
            
            if fitness_histories:
                mean_hist = np.mean(fitness_histories, axis=0)
                std_hist = np.std(fitness_histories, axis=0)
                iterations = range(len(mean_hist))
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(iterations, mean_hist, 'b-', linewidth=2, label='Mean')
                ax.fill_between(iterations, mean_hist - std_hist, mean_hist + std_hist, alpha=0.3, color='blue', label='±1 Std')
                ax.set_xlabel('Iteration')
                ax.set_ylabel('Best Fitness')
                ax.set_title(f'Convergence with Uncertainty - {func_name}')
                ax.set_yscale('log')
                ax.legend()
                ax.grid(True, alpha=0.3)
                plt.savefig(f"{folder}/convergence_uncertainty.png", dpi=150, bbox_inches='tight')
                plt.close()
                if verbose: print("✓ convergence_uncertainty.png")
                plots += 1
        except: pass
    
    return plots


def _plot_comparison(results, histories, folder, func_name, num_runs, viz_config, verbose):
    """Plot algorithm comparison."""
    
    # Convergence comparison
    if viz_config.get('convergence_curve') and histories:
        try:
            plt.figure(figsize=(12, 6))
            colors = plt.cm.tab10(np.linspace(0, 1, len(histories)))
            
            for (name, hist), color in zip(histories.items(), colors):
                mean_hist = np.mean(hist, axis=0)
                std_hist = np.std(hist, axis=0)
                iterations = np.arange(len(mean_hist))
                
                plt.semilogy(iterations, mean_hist, label=name, color=color, linewidth=2)
                plt.fill_between(iterations, mean_hist - std_hist, mean_hist + std_hist, alpha=0.2, color=color)
            
            plt.xlabel('Iteration')
            plt.ylabel('Best Fitness (log)')
            plt.title(f'Convergence Comparison - {func_name}')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(f"{folder}/convergence_comparison.png", dpi=150, bbox_inches='tight')
            plt.close()
            if verbose: print("✓ convergence_comparison.png")
        except: pass
    
    # Statistical comparison
    if viz_config.get('fitness_boxplot'):
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Boxplot
            ax1.boxplot(results.values(), tick_labels=results.keys())
            ax1.set_ylabel('Best Fitness')
            ax1.set_title('Distribution Comparison')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3)
            
            # Bar plot
            means = [np.mean(v) for v in results.values()]
            stds = [np.std(v) for v in results.values()]
            x_pos = np.arange(len(results))
            ax2.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, edgecolor='black')
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(results.keys(), rotation=45, ha='right')
            ax2.set_ylabel('Mean Best Fitness')
            ax2.set_title('Mean ± Std Comparison')
            ax2.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            plt.savefig(f"{folder}/statistical_comparison.png", dpi=150, bbox_inches='tight')
            plt.close()
            if verbose: print("✓ statistical_comparison.png")
        except: pass
