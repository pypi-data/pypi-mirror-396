"""
Comprehensive Experiments with All Classic DE Variants.

This script runs full experiments comparing all 8 classic DE variants
with complete visualizations, statistics, and analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import pandas as pd

from pyrade.algorithms.classic import (
    DErand1bin,
    DEbest1bin,
    DEcurrentToBest1bin,
    DErand2bin,
    DEbest2bin,
    DEcurrentToRand1bin,
    DERandToBest1bin,
)


# Test functions
def sphere(x):
    """Unimodal - smooth, single optimum."""
    return np.sum(x**2)


def rosenbrock(x):
    """Unimodal - narrow valley, challenging."""
    return np.sum(100.0 * (x[1:] - x[:-1]**2)**2 + (x[:-1] - 1)**2)


def rastrigin(x):
    """Highly multimodal - many local optima."""
    n = len(x)
    return 10*n + np.sum(x**2 - 10*np.cos(2*np.pi*x))


def ackley(x):
    """Multimodal - flat regions with sharp optimum."""
    n = len(x)
    sum1 = np.sum(x**2)
    sum2 = np.sum(np.cos(2*np.pi*x))
    return -20*np.exp(-0.2*np.sqrt(sum1/n)) - np.exp(sum2/n) + 20 + np.e


def schwefel(x):
    """Multimodal - deceptive, optimum far from origin."""
    n = len(x)
    return 418.9829*n - np.sum(x * np.sin(np.sqrt(np.abs(x))))


def main():
    """Run comprehensive experiments."""
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"experiments_classic_de_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    
    print("="*80)
    print("COMPREHENSIVE CLASSIC DE VARIANTS EXPERIMENTS")
    print("="*80)
    print(f"Output directory: {output_dir}")
    print()
    
    # Experiment configuration
    n_runs = 30
    dimensions = 10
    pop_size = 50
    max_iter = 300
    
    # Define test problems
    problems = [
        ("Sphere", sphere, [(-100, 100)]),
        ("Rosenbrock", rosenbrock, [(-5, 10)]),
        ("Rastrigin", rastrigin, [(-5.12, 5.12)]),
        ("Ackley", ackley, [(-32.768, 32.768)]),
        ("Schwefel", schwefel, [(-500, 500)]),
    ]
    
    # Define algorithms
    algorithms = [
        ("DE/rand/1/bin", DErand1bin),
        ("DE/best/1/bin", DEbest1bin),
        ("DE/current-to-best/1/bin", DEcurrentToBest1bin),
        ("DE/rand/2/bin", DErand2bin),
        ("DE/best/2/bin", DEbest2bin),
        ("DE/current-to-rand/1/bin", DEcurrentToRand1bin),
        ("DE/rand-to-best/1/bin", DERandToBest1bin),
    ]
    
    # Storage for results
    all_results = {}
    
    # Run experiments
    for prob_name, prob_func, bounds_template in problems:
        print(f"\n{'='*80}")
        print(f"Problem: {prob_name}")
        print(f"{'='*80}")
        
        bounds = bounds_template * dimensions
        all_results[prob_name] = {}
        
        for alg_name, alg_class in algorithms:
            print(f"\n  Testing {alg_name}...")
            
            fitness_values = []
            convergence_curves = []
            times = []
            
            for run in range(n_runs):
                # Run optimization
                de = alg_class(
                    objective_func=prob_func,
                    bounds=bounds,
                    pop_size=pop_size,
                    max_iter=max_iter,
                    seed=42 + run,
                    verbose=False
                )
                
                result = de.optimize()
                
                fitness_values.append(result['best_fitness'])
                convergence_curves.append(result['history']['fitness'])
                times.append(result['time'])
                
                if (run + 1) % 10 == 0:
                    print(f"    Run {run+1}/{n_runs} complete")
            
            # Store results
            all_results[prob_name][alg_name] = {
                'fitness': fitness_values,
                'convergence': convergence_curves,
                'times': times,
                'mean': np.mean(fitness_values),
                'std': np.std(fitness_values),
                'median': np.median(fitness_values),
                'best': np.min(fitness_values),
                'worst': np.max(fitness_values),
                'mean_time': np.mean(times),
            }
            
            print(f"    Mean: {np.mean(fitness_values):.6e} ± {np.std(fitness_values):.6e}")
            print(f"    Best: {np.min(fitness_values):.6e}")
    
    # Generate visualizations
    print(f"\n{'='*80}")
    print("Generating Visualizations...")
    print(f"{'='*80}\n")
    
    # 1. Convergence curves for each problem
    generate_convergence_plots(all_results, output_dir)
    
    # 2. Box plots comparing algorithms
    generate_boxplots(all_results, output_dir)
    
    # 3. Performance profiles
    generate_performance_profiles(all_results, output_dir)
    
    # 4. Statistical summary tables
    generate_summary_tables(all_results, output_dir)
    
    # 5. Heatmap of algorithm performance
    generate_performance_heatmap(all_results, output_dir)
    
    # 6. Convergence speed comparison
    generate_convergence_speed_analysis(all_results, output_dir)
    
    print(f"\n{'='*80}")
    print("EXPERIMENTS COMPLETE!")
    print(f"{'='*80}")
    print(f"\nAll results saved to: {output_dir}")
    print("\nGenerated files:")
    print("  - convergence_*.png - Convergence curves for each problem")
    print("  - boxplot_*.png - Box plots comparing algorithms")
    print("  - performance_profile.png - Performance profile across problems")
    print("  - performance_heatmap.png - Algorithm performance heatmap")
    print("  - convergence_speed.png - Convergence speed analysis")
    print("  - summary_statistics.csv - Detailed statistics table")
    print("  - results_summary.txt - Text summary of all results")


def generate_convergence_plots(all_results, output_dir):
    """Generate convergence curve plots."""
    print("  Generating convergence plots...")
    
    for prob_name, prob_results in all_results.items():
        fig, ax = plt.subplots(figsize=(12, 7))
        
        for alg_name, data in prob_results.items():
            # Calculate mean convergence curve
            curves = np.array(data['convergence'])
            mean_curve = np.mean(curves, axis=0)
            std_curve = np.std(curves, axis=0)
            
            generations = range(len(mean_curve))
            
            # Plot mean with confidence interval
            ax.plot(generations, mean_curve, label=alg_name, linewidth=2)
            ax.fill_between(
                generations,
                mean_curve - std_curve,
                mean_curve + std_curve,
                alpha=0.2
            )
        
        ax.set_xlabel('Generation', fontsize=12)
        ax.set_ylabel('Best Fitness', fontsize=12)
        ax.set_title(f'Convergence Curves - {prob_name}', fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / f'convergence_{prob_name.lower()}.png', dpi=300)
        plt.close()


def generate_boxplots(all_results, output_dir):
    """Generate box plots comparing algorithms."""
    print("  Generating box plots...")
    
    for prob_name, prob_results in all_results.items():
        fig, ax = plt.subplots(figsize=(14, 7))
        
        data = [prob_results[alg]['fitness'] for alg in prob_results.keys()]
        labels = list(prob_results.keys())
        
        bp = ax.boxplot(data, labels=labels, patch_artist=True)
        
        # Color boxes
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax.set_xlabel('Algorithm', fontsize=12)
        ax.set_ylabel('Final Best Fitness', fontsize=12)
        ax.set_title(f'Algorithm Comparison - {prob_name}', fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        plt.xticks(rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_dir / f'boxplot_{prob_name.lower()}.png', dpi=300)
        plt.close()


def generate_performance_profiles(all_results, output_dir):
    """Generate performance profile plot."""
    print("  Generating performance profile...")
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Get all algorithms
    alg_names = list(next(iter(all_results.values())).keys())
    
    # Calculate performance ratios
    tau_values = np.logspace(-2, 2, 100)
    
    for alg_name in alg_names:
        probabilities = []
        
        for tau in tau_values:
            solved_count = 0
            total_problems = 0
            
            for prob_name, prob_results in all_results.items():
                # Get best result for this problem across all algorithms
                best_result = min(
                    np.min(prob_results[alg]['fitness'])
                    for alg in alg_names
                )
                
                # Check if this algorithm solved within tau * best
                alg_result = np.min(prob_results[alg_name]['fitness'])
                if alg_result <= tau * best_result:
                    solved_count += 1
                
                total_problems += 1
            
            probabilities.append(solved_count / total_problems)
        
        ax.plot(tau_values, probabilities, label=alg_name, linewidth=2, marker='o', markersize=4)
    
    ax.set_xlabel('Performance Ratio (τ)', fontsize=12)
    ax.set_ylabel('Probability of Solving', fontsize=12)
    ax.set_title('Performance Profile - All Problems', fontsize=14, fontweight='bold')
    ax.set_xscale('log')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([tau_values[0], tau_values[-1]])
    ax.set_ylim([0, 1.05])
    
    plt.tight_layout()
    plt.savefig(output_dir / 'performance_profile.png', dpi=300)
    plt.close()


def generate_summary_tables(all_results, output_dir):
    """Generate summary statistics tables."""
    print("  Generating summary tables...")
    
    # Create DataFrame
    rows = []
    for prob_name, prob_results in all_results.items():
        for alg_name, data in prob_results.items():
            rows.append({
                'Problem': prob_name,
                'Algorithm': alg_name,
                'Mean': data['mean'],
                'Std': data['std'],
                'Median': data['median'],
                'Best': data['best'],
                'Worst': data['worst'],
                'Mean Time (s)': data['mean_time'],
            })
    
    df = pd.DataFrame(rows)
    
    # Save to CSV
    df.to_csv(output_dir / 'summary_statistics.csv', index=False)
    
    # Create text summary
    with open(output_dir / 'results_summary.txt', 'w') as f:
        f.write("="*80 + "\n")
        f.write("CLASSIC DE VARIANTS - EXPERIMENTAL RESULTS SUMMARY\n")
        f.write("="*80 + "\n\n")
        
        for prob_name in all_results.keys():
            f.write(f"\n{prob_name}\n")
            f.write("-" * 80 + "\n")
            
            prob_df = df[df['Problem'] == prob_name].sort_values('Mean')
            f.write(prob_df.to_string(index=False))
            f.write("\n\n")
            
            # Rank algorithms
            f.write("  Rankings (by mean fitness):\n")
            for i, row in enumerate(prob_df.itertuples(), 1):
                f.write(f"    {i}. {row.Algorithm}: {row.Mean:.6e}\n")
            f.write("\n")


def generate_performance_heatmap(all_results, output_dir):
    """Generate heatmap of algorithm performance."""
    print("  Generating performance heatmap...")
    
    # Prepare data matrix
    problems = list(all_results.keys())
    algorithms = list(next(iter(all_results.values())).keys())
    
    matrix = np.zeros((len(problems), len(algorithms)))
    
    for i, prob_name in enumerate(problems):
        for j, alg_name in enumerate(algorithms):
            matrix[i, j] = np.log10(all_results[prob_name][alg_name]['mean'])
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    
    im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto')
    
    # Set ticks
    ax.set_xticks(range(len(algorithms)))
    ax.set_yticks(range(len(problems)))
    ax.set_xticklabels(algorithms, rotation=45, ha='right')
    ax.set_yticklabels(problems)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('log₁₀(Mean Fitness)', fontsize=12)
    
    # Add values
    for i in range(len(problems)):
        for j in range(len(algorithms)):
            text = ax.text(j, i, f'{matrix[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=8)
    
    ax.set_title('Algorithm Performance Heatmap', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'performance_heatmap.png', dpi=300)
    plt.close()


def generate_convergence_speed_analysis(all_results, output_dir):
    """Analyze convergence speed of algorithms."""
    print("  Generating convergence speed analysis...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    
    for idx, (prob_name, prob_results) in enumerate(all_results.items()):
        ax = axes[idx]
        
        for alg_name, data in prob_results.items():
            curves = np.array(data['convergence'])
            mean_curve = np.mean(curves, axis=0)
            
            # Calculate how fast it reaches certain thresholds
            target = mean_curve[0] * 0.01  # 1% of initial fitness
            
            generations = range(len(mean_curve))
            ax.plot(generations, mean_curve, label=alg_name, linewidth=2)
        
        ax.set_xlabel('Generation', fontsize=10)
        ax.set_ylabel('Best Fitness', fontsize=10)
        ax.set_title(prob_name, fontsize=12, fontweight='bold')
        ax.set_yscale('log')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    # Hide extra subplot
    if len(all_results) < len(axes):
        axes[-1].axis('off')
    
    plt.suptitle('Convergence Speed Comparison', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'convergence_speed.png', dpi=300)
    plt.close()


if __name__ == "__main__":
    main()
