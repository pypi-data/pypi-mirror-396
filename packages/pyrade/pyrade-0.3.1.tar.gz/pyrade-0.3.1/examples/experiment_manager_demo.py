"""
Example usage of the ExperimentManager class.

This script demonstrates how to use PyRADE's high-level ExperimentManager
for running, visualizing, and exporting benchmark experiments.
"""

from pyrade import ExperimentManager
from pyrade.operators import DEbest1, DErand1


def example_basic_usage():
    """Basic usage with default settings."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 80 + "\n")
    
    # Create experiment manager with 3 benchmarks
    exp = ExperimentManager(
        benchmarks=['Sphere', 'Rastrigin', 'Rosenbrock'],
        dimensions=10,
        n_runs=5,  # Quick test with 5 runs
        population_size=30,
        max_iterations=50
    )
    
    # Run complete pipeline
    exp.run_complete_pipeline()


def example_custom_selection():
    """Select specific benchmarks and customize parameters."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Custom Benchmark Selection")
    print("=" * 80 + "\n")
    
    # List available benchmarks
    ExperimentManager.list_available_benchmarks()
    
    # Create experiment with custom selection
    exp = ExperimentManager(
        benchmarks=['Ackley', 'Griewank', 'Schwefel', 'Levy'],
        dimensions=20,
        n_runs=10,
        population_size=100,
        max_iterations=200,
        F=0.7,
        CR=0.8,
        experiment_name='custom_experiment',
        seed=42
    )
    
    # Run experiments and automatically generate visualizations
    exp.run_experiments(verbose=True, apply_visualizations=True)

    # Export in specific formats (visualizations already saved)
    exp.export_results(formats=['csv', 'json'])


def example_step_by_step():
    """Step-by-step execution with more control."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Step-by-Step Execution")
    print("=" * 80 + "\n")
    
    # Initialize
    exp = ExperimentManager(
        benchmarks=['Sphere', 'Rastrigin'],
        dimensions=5,
        n_runs=10,
        population_size=30,
        max_iterations=50,
        experiment_name='step_by_step_demo'
    )
    
    # Step 1: Run experiments
    print("Step 1: Running experiments...")
    results = exp.run_experiments(verbose=False)
    
    # Access results programmatically
    for bench_name, data in results.items():
        print(f"\n{bench_name} Results:")
        print(f"  Mean Fitness: {data['mean_fitness']:.6e}")
        print(f"  Std Fitness: {data['std_fitness']:.6e}")
        print(f"  Best Run: {data['min_fitness']:.6e}")
        print(f"  Worst Run: {data['max_fitness']:.6e}")
    
    # Step 2: Generate plots individually
    print("\nStep 2: Generating plots...")
    exp.plot_convergence_curves(save=True)
    exp.plot_combined_convergence(save=True)
    exp.plot_boxplots(save=True, split_scales=False)
    
    # Step 3: Export data
    print("\nStep 3: Exporting data...")
    exp.export_to_csv(detailed=True)
    exp.export_to_numpy()
    
    # Step 4: Generate report
    print("\nStep 4: Generating report...")
    exp.generate_report()
    
    print("\n✓ All steps completed!")


def example_all_benchmarks():
    """Run experiments on all available benchmarks."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: All Benchmarks")
    print("=" * 80 + "\n")
    
    # Use all available benchmarks (benchmarks=None)
    exp = ExperimentManager(
        benchmarks=None,  # This will use all available benchmarks
        dimensions=10,
        n_runs=20,
        population_size=50,
        max_iterations=100,
        experiment_name='full_benchmark_suite'
    )
    
    # Run complete pipeline
    exp.run_complete_pipeline(verbose=True)


def example_high_dimensional():
    """Test on high-dimensional problems."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: High-Dimensional Problems")
    print("=" * 80 + "\n")
    
    exp = ExperimentManager(
        benchmarks=['Sphere', 'Rastrigin', 'Ackley'],
        dimensions=50,  # 50-dimensional
        n_runs=15,
        population_size=200,  # Larger population for higher dimensions
        max_iterations=500,
        experiment_name='high_dim_experiment'
    )
    
    exp.run_complete_pipeline()


def example_custom_function():
    """Use custom objective function."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Custom Objective Function")
    print("=" * 80 + "\n")
    
    # Define custom function
    def my_custom_function(x):
        """Custom quadratic + sine function."""
        return sum(x**2) + sum(10 * np.sin(x))
    
    # Include custom function with standard benchmarks
    exp = ExperimentManager(
        benchmarks=['Sphere', my_custom_function],  # Mix standard and custom
        dimensions=10,
        n_runs=10,
        population_size=40,
        max_iterations=100,
        experiment_name='custom_function_test'
    )
    
    exp.run_complete_pipeline()


def example_custom_mutation():
    """Demonstrate passing different mutation strategies to ExperimentManager."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6b: Custom Mutation Strategies")
    print("=" * 80 + "\n")

    # Use built-in strategy by name
    exp1 = ExperimentManager(
        benchmarks=['Sphere'],
        dimensions=10,
        n_runs=5,
        population_size=40,
        max_iterations=80,
        mutation='DEbest1',  # resolved from pyrade.operators
        experiment_name='mutation_by_name'
    )
    exp1.run_complete_pipeline()

    # Use an instance of a mutation strategy
    exp2 = ExperimentManager(
        benchmarks=['Rastrigin'],
        dimensions=10,
        n_runs=5,
        population_size=40,
        max_iterations=80,
        mutation=DErand1(F=0.6),  # pass an instance
        experiment_name='mutation_by_instance'
    )
    exp2.run_complete_pipeline()


def example_custom_pop_itr_objf():
    """Demonstrate a custom objective function with custom population and iterations."""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Custom Population, Iterations, and Objective Function")
    print("=" * 80 + "\n")

    # Define a custom objective (shifted quartic + sinusoid)
    def custom_obj(x):
        # x will be a numpy array provided by DifferentialEvolution
        return np.sum((x - 1.5) ** 4) + np.sum(5.0 * np.sin(2.0 * x))

    # Use the custom objective with an explicit population and iteration count
    exp = ExperimentManager(
        benchmarks=[custom_obj],
        dimensions=8,
        n_runs=6,
        population_size=120,   # larger population
        max_iterations=250,    # more iterations
        experiment_name='custom_pop_itr_objf'
    )

    exp.run_complete_pipeline()


def example_quick_comparison():
    """Quick comparison with minimal runs for testing."""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Quick Comparison (Testing Mode)")
    print("=" * 80 + "\n")
    
    exp = ExperimentManager(
        benchmarks=['Sphere', 'Rastrigin', 'Rosenbrock', 'Ackley'],
        dimensions=5,
        n_runs=3,  # Just 3 runs for quick testing
        population_size=20,
        max_iterations=30,
        experiment_name='quick_test'
    )
    
    exp.run_complete_pipeline(verbose=True)


def example_accessing_raw_data():
    """Example of accessing and analyzing raw data."""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Accessing Raw Data")
    print("=" * 80 + "\n")
    
    import numpy as np
    
    exp = ExperimentManager(
        benchmarks=['Sphere', 'Rastrigin'],
        dimensions=10,
        n_runs=10,
        population_size=50,
        max_iterations=100
    )
    
    # Run experiments
    exp.run_experiments(verbose=False)
    
    # Access raw data
    print("\nAnalyzing raw data:")
    for bench_name, data in exp.results.items():
        print(f"\n{bench_name}:")
        
        # Convergence analysis
        conv_histories = np.array(data['convergence_histories'])
        print(f"  Convergence shape: {conv_histories.shape}")
        print(f"  Initial avg fitness: {np.mean(conv_histories[:, 0]):.6e}")
        print(f"  Final avg fitness: {np.mean(conv_histories[:, -1]):.6e}")
        
        # Solution analysis
        best_solutions = np.array(data['best_solutions'])
        print(f"  Solution shape: {best_solutions.shape}")
        print(f"  Solution mean: {np.mean(best_solutions):.6e}")
        print(f"  Solution std: {np.std(best_solutions):.6e}")
        
        # Performance analysis
        print(f"  Success rate (< 1e-5): {np.sum(np.array(data['final_fitness']) < 1e-5) / len(data['final_fitness']) * 100:.1f}%")
    
    # Export for further analysis
    exp.export_results()


if __name__ == "__main__":
    import numpy as np
    
    # Run examples (uncomment the ones you want to try)
    
    # Quick tests
    #example_basic_usage()
    # example_quick_comparison()
    
    # Detailed examples
    # example_custom_selection()
    # example_step_by_step()
    # example_accessing_raw_data()
    
    # Full benchmarks
    example_all_benchmarks()
    
    # Advanced
    # example_high_dimensional()
    # example_custom_function()
