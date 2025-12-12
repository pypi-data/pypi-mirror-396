"""Tests for benchmark functions."""

import pytest
import numpy as np
from pyrade.benchmarks import (
    Sphere, Rastrigin, Rosenbrock, Ackley, Griewank,
    Schwefel, Levy, Michalewicz, Zakharov, Easom, StyblinskiTang
)


class TestBenchmarkOptimumLocations:
    """Test that benchmark functions have correct optimum locations."""
    
    def test_sphere_optimum(self):
        """Test Sphere function optimum."""
        func = Sphere(dim=10)
        
        # Optimum at origin
        optimum_value = func(func.optimum_location)
        
        assert np.isclose(optimum_value, func.optimum, atol=1e-10)
        assert np.isclose(optimum_value, 0.0, atol=1e-10)
        np.testing.assert_array_almost_equal(func.optimum_location, np.zeros(10))
    
    def test_rastrigin_optimum(self):
        """Test Rastrigin function optimum."""
        func = Rastrigin(dim=10)
        
        optimum_value = func(func.optimum_location)
        
        assert np.isclose(optimum_value, func.optimum, atol=1e-10)
        assert np.isclose(optimum_value, 0.0, atol=1e-10)
        np.testing.assert_array_almost_equal(func.optimum_location, np.zeros(10))
    
    def test_rosenbrock_optimum(self):
        """Test Rosenbrock function optimum."""
        func = Rosenbrock(dim=10)
        
        optimum_value = func(func.optimum_location)
        
        assert np.isclose(optimum_value, func.optimum, atol=1e-10)
        assert np.isclose(optimum_value, 0.0, atol=1e-10)
        np.testing.assert_array_almost_equal(func.optimum_location, np.ones(10))
    
    def test_ackley_optimum(self):
        """Test Ackley function optimum."""
        func = Ackley(dim=10)
        
        optimum_value = func(func.optimum_location)
        
        assert np.isclose(optimum_value, func.optimum, atol=1e-10)
        assert np.isclose(optimum_value, 0.0, atol=1e-10)
        np.testing.assert_array_almost_equal(func.optimum_location, np.zeros(10))
    
    def test_griewank_optimum(self):
        """Test Griewank function optimum."""
        func = Griewank(dim=10)
        
        optimum_value = func(func.optimum_location)
        
        assert np.isclose(optimum_value, func.optimum, atol=1e-10)
        assert np.isclose(optimum_value, 0.0, atol=1e-10)
        np.testing.assert_array_almost_equal(func.optimum_location, np.zeros(10))
    
    def test_schwefel_optimum(self):
        """Test Schwefel function optimum."""
        func = Schwefel(dim=10)
        
        optimum_value = func(func.optimum_location)
        
        # Schwefel optimum is approximately 0
        assert np.isclose(optimum_value, func.optimum, atol=1e-4)
        assert np.isclose(optimum_value, 0.0, atol=1e-4)
        # Optimum at 420.9687 for each dimension
        assert np.allclose(func.optimum_location, 420.9687, atol=0.01)
    
    def test_levy_optimum(self):
        """Test Levy function optimum."""
        func = Levy(dim=10)
        
        optimum_value = func(func.optimum_location)
        
        assert np.isclose(optimum_value, func.optimum, atol=1e-10)
        assert np.isclose(optimum_value, 0.0, atol=1e-10)
        np.testing.assert_array_almost_equal(func.optimum_location, np.ones(10))
    
    def test_zakharov_optimum(self):
        """Test Zakharov function optimum."""
        func = Zakharov(dim=10)
        
        optimum_value = func(func.optimum_location)
        
        assert np.isclose(optimum_value, func.optimum, atol=1e-10)
        assert np.isclose(optimum_value, 0.0, atol=1e-10)
        np.testing.assert_array_almost_equal(func.optimum_location, np.zeros(10))
    
    def test_easom_optimum(self):
        """Test Easom function optimum."""
        func = Easom(dim=2)
        
        optimum_value = func(func.optimum_location)
        
        assert np.isclose(optimum_value, func.optimum, atol=1e-10)
        assert np.isclose(optimum_value, -1.0, atol=1e-10)
        np.testing.assert_array_almost_equal(func.optimum_location, [np.pi, np.pi])
    
    def test_styblinski_tang_optimum(self):
        """Test StyblinskiTang function optimum."""
        func = StyblinskiTang(dim=10)
        
        optimum_value = func(func.optimum_location)
        
        expected_optimum = -39.16599 * 10
        assert np.isclose(optimum_value, func.optimum, atol=1e-4)
        assert np.isclose(optimum_value, expected_optimum, atol=1e-4)
        assert np.allclose(func.optimum_location, -2.903534, atol=0.01)


class TestBenchmarkFunctionBehavior:
    """Test benchmark function behavior."""
    
    def test_sphere_is_unimodal(self):
        """Test that Sphere function increases away from optimum."""
        func = Sphere(dim=5)
        
        # Value at optimum
        val_opt = func(np.zeros(5))
        
        # Values away from optimum should be larger
        val_1 = func(np.ones(5))
        val_2 = func(np.ones(5) * 2)
        
        assert val_1 > val_opt
        assert val_2 > val_1
    
    def test_rastrigin_is_multimodal(self):
        """Test Rastrigin has local minima."""
        func = Rastrigin(dim=2)
        
        # Optimum at origin
        val_opt = func(np.zeros(2))
        
        # Should have higher values around it
        val_near = func(np.array([0.5, 0.5]))
        
        assert val_near > val_opt
    
    def test_rosenbrock_valley(self):
        """Test Rosenbrock valley property."""
        func = Rosenbrock(dim=5)
        
        # Optimum at ones
        val_opt = func(np.ones(5))
        
        # Values away from optimum
        val_1 = func(np.zeros(5))
        val_2 = func(np.ones(5) * 2)
        
        assert val_1 > val_opt
        assert val_2 > val_opt


class TestBenchmarkFunctionDimensions:
    """Test benchmark functions with different dimensions."""
    
    def test_various_dimensions(self):
        """Test functions work with various dimensions."""
        dimensions = [1, 5, 10, 30, 50]
        
        for dim in dimensions:
            # Test a few functions
            sphere = Sphere(dim=dim)
            rastrigin = Rastrigin(dim=dim)
            rosenbrock = Rosenbrock(dim=dim)
            
            # Create random test point
            x = np.random.randn(dim)
            
            # Should return scalar value
            val_sphere = sphere(x)
            val_rastrigin = rastrigin(x)
            val_rosenbrock = rosenbrock(x)
            
            assert isinstance(val_sphere, (int, float, np.number))
            assert isinstance(val_rastrigin, (int, float, np.number))
            assert isinstance(val_rosenbrock, (int, float, np.number))
    
    def test_single_dimension(self):
        """Test functions work in 1D."""
        sphere = Sphere(dim=1)
        rastrigin = Rastrigin(dim=1)
        
        x = np.array([2.0])
        
        val_sphere = sphere(x)
        val_rastrigin = rastrigin(x)
        
        assert val_sphere == 4.0
        assert val_rastrigin > 0


class TestBenchmarkBounds:
    """Test benchmark function bounds."""
    
    def test_sphere_bounds(self):
        """Test Sphere function bounds."""
        func = Sphere(dim=10)
        
        assert func.bounds == (-100, 100)
        bounds_array = func.get_bounds_array()
        assert len(bounds_array) == 10
        assert all(b == (-100, 100) for b in bounds_array)
    
    def test_rastrigin_bounds(self):
        """Test Rastrigin function bounds."""
        func = Rastrigin(dim=10)
        
        assert func.bounds == (-5.12, 5.12)
    
    def test_rosenbrock_bounds(self):
        """Test Rosenbrock function bounds."""
        func = Rosenbrock(dim=10)
        
        assert func.bounds == (-5, 10)
    
    def test_ackley_bounds(self):
        """Test Ackley function bounds."""
        func = Ackley(dim=10)
        
        assert func.bounds == (-32, 32)


class TestBenchmarkValidity:
    """Test that benchmark functions produce valid outputs."""
    
    def test_no_nans(self):
        """Test that functions don't produce NaNs for valid inputs."""
        functions = [
            Sphere(dim=5),
            Rastrigin(dim=5),
            Rosenbrock(dim=5),
            Ackley(dim=5),
            Griewank(dim=5),
            Levy(dim=5),
            Zakharov(dim=5)
        ]
        
        # Test with random valid inputs
        np.random.seed(42)
        for func in functions:
            for _ in range(10):
                x = np.random.uniform(-10, 10, size=5)
                val = func(x)
                
                assert not np.isnan(val)
                assert not np.isinf(val)
    
    def test_output_is_scalar(self):
        """Test that functions return scalar values."""
        func = Sphere(dim=10)
        
        x = np.random.randn(10)
        val = func(x)
        
        # Should be scalar
        assert isinstance(val, (int, float, np.number))
        assert np.isscalar(val)
    
    def test_michalewicz_with_parameter(self):
        """Test Michalewicz function with different m parameter."""
        for m in [5, 10, 20]:
            func = Michalewicz(dim=5, m=m)
            x = np.random.uniform(0, np.pi, size=5)
            val = func(x)
            
            assert isinstance(val, (int, float, np.number))
            assert not np.isnan(val)


class TestBenchmarkConsistency:
    """Test consistency of benchmark function implementations."""
    
    def test_repeated_evaluation(self):
        """Test that repeated evaluations give same result."""
        func = Sphere(dim=10)
        x = np.random.randn(10)
        
        val1 = func(x)
        val2 = func(x)
        val3 = func(x)
        
        assert val1 == val2 == val3
    
    def test_function_is_deterministic(self):
        """Test that functions are deterministic."""
        functions = [
            Sphere(dim=5),
            Rastrigin(dim=5),
            Rosenbrock(dim=5)
        ]
        
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        for func in functions:
            val1 = func(x)
            val2 = func(x)
            
            assert val1 == val2
