"""Tests for DifferentialEvolution algorithm."""

import pytest
import numpy as np
from pyrade import DifferentialEvolution


class TestAlgorithmConvergence:
    """Test algorithm convergence on simple problems."""
    
    def test_sphere_convergence(self, simple_sphere, simple_bounds):
        """Test convergence on simple sphere function."""
        optimizer = DifferentialEvolution(
            objective_func=simple_sphere,
            bounds=simple_bounds,
            pop_size=30,
            max_iter=200,
            seed=42
        )
        
        result = optimizer.optimize()
        
        # Should converge close to optimum (0)
        assert result['best_fitness'] < 1e-3, "Failed to converge to optimum"
        # Solution should be close to origin
        assert np.linalg.norm(result['best_solution']) < 1.0


class TestReproducibility:
    """Test that same seed produces same results."""
    
    def test_same_seed_same_results(self, simple_sphere, simple_bounds):
        """Test reproducibility with same seed."""
        # First run
        optimizer1 = DifferentialEvolution(
            objective_func=simple_sphere,
            bounds=simple_bounds,
            pop_size=30,
            max_iter=100,
            seed=42
        )
        result1 = optimizer1.optimize()
        
        # Second run with same seed
        optimizer2 = DifferentialEvolution(
            objective_func=simple_sphere,
            bounds=simple_bounds,
            pop_size=30,
            max_iter=100,
            seed=42
        )
        result2 = optimizer2.optimize()
        
        # Results should be identical
        np.testing.assert_array_almost_equal(
            result1['best_solution'], 
            result2['best_solution'],
            decimal=10
        )
        assert abs(result1['best_fitness'] - result2['best_fitness']) < 1e-10
    
    def test_different_seed_different_results(self, simple_sphere, simple_bounds):
        """Test that different seeds produce different results."""
        # First run
        optimizer1 = DifferentialEvolution(
            objective_func=simple_sphere,
            bounds=simple_bounds,
            pop_size=30,
            max_iter=50,
            seed=42
        )
        result1 = optimizer1.optimize()
        
        # Second run with different seed
        optimizer2 = DifferentialEvolution(
            objective_func=simple_sphere,
            bounds=simple_bounds,
            pop_size=30,
            max_iter=50,
            seed=123
        )
        result2 = optimizer2.optimize()
        
        # Results should be different (with high probability)
        assert not np.allclose(result1['best_solution'], result2['best_solution'])


class TestAlgorithmBehavior:
    """Test general algorithm behavior."""
    
    def test_returns_best_fitness(self, simple_sphere, simple_bounds):
        """Test that algorithm returns valid result dictionary."""
        optimizer = DifferentialEvolution(
            objective_func=simple_sphere,
            bounds=simple_bounds,
            pop_size=20,
            max_iter=50,
            seed=42
        )
        
        result = optimizer.optimize()
        
        # Check result structure
        assert 'best_solution' in result
        assert 'best_fitness' in result
        assert 'iterations' in result
        assert 'time' in result
        
        # Check types
        assert isinstance(result['best_solution'], np.ndarray)
        assert isinstance(result['best_fitness'], (int, float))
        assert isinstance(result['iterations'], int)
        assert isinstance(result['time'], float)
    
    def test_respects_max_iterations(self, simple_sphere, simple_bounds):
        """Test that algorithm respects max_iter parameter."""
        max_iter = 100
        optimizer = DifferentialEvolution(
            objective_func=simple_sphere,
            bounds=simple_bounds,
            pop_size=20,
            max_iter=max_iter,
            seed=42
        )
        
        result = optimizer.optimize()
        
        assert result['iterations'] <= max_iter
    
    def test_callback_execution(self, simple_sphere, simple_bounds):
        """Test that callback is executed during optimization."""
        callback_data = []
        
        def callback(iteration, best_fitness, best_solution):
            callback_data.append({
                'iteration': iteration,
                'fitness': best_fitness,
                'solution': best_solution.copy()
            })
        
        optimizer = DifferentialEvolution(
            objective_func=simple_sphere,
            bounds=simple_bounds,
            pop_size=20,
            max_iter=50,
            callback=callback,
            seed=42
        )
        
        optimizer.optimize()
        
        # Callback should have been called
        assert len(callback_data) > 0
        # Should have been called multiple times
        assert len(callback_data) >= 10
    
    def test_fitness_improvement(self, simple_sphere, simple_bounds):
        """Test that fitness improves over iterations."""
        history = []
        
        def callback(iteration, best_fitness, best_solution):
            history.append(best_fitness)
        
        optimizer = DifferentialEvolution(
            objective_func=simple_sphere,
            bounds=simple_bounds,
            pop_size=30,
            max_iter=100,
            callback=callback,
            seed=42
        )
        
        optimizer.optimize()
        
        # First fitness should be worse than last fitness
        assert history[0] > history[-1]
        # Fitness should be non-increasing (monotonic improvement)
        for i in range(1, len(history)):
            assert history[i] <= history[i-1]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_single_dimension(self):
        """Test optimization in 1D."""
        def f(x):
            return x[0]**2
        
        optimizer = DifferentialEvolution(
            objective_func=f,
            bounds=[(-5, 5)],
            pop_size=20,
            max_iter=100,
            seed=42
        )
        
        result = optimizer.optimize()
        assert abs(result['best_solution'][0]) < 0.1
        assert result['best_fitness'] < 0.01
    
    def test_high_dimension(self):
        """Test optimization in higher dimensions."""
        def sphere(x):
            return np.sum(x**2)
        
        dim = 50
        optimizer = DifferentialEvolution(
            objective_func=sphere,
            bounds=[(-10, 10)] * dim,
            pop_size=100,
            max_iter=300,
            seed=42
        )
        
        result = optimizer.optimize()
        assert result['best_solution'].shape[0] == dim
        assert result['best_fitness'] < 10.0  # Should improve significantly
    
    def test_asymmetric_bounds(self):
        """Test with asymmetric bounds."""
        def f(x):
            return np.sum((x - 5)**2)
        
        optimizer = DifferentialEvolution(
            objective_func=f,
            bounds=[(-10, 20)] * 5,  # Asymmetric around optimum at 5
            pop_size=30,
            max_iter=200,
            seed=42
        )
        
        result = optimizer.optimize()
        # Should converge near 5
        assert np.allclose(result['best_solution'], 5, atol=0.5)
