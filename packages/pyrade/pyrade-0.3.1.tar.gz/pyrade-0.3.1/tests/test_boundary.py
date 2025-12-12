"""Tests for boundary handlers."""

import pytest
import numpy as np
from pyrade.utils import (
    ClipBoundary, ReflectBoundary, RandomBoundary,
    WrapBoundary, MidpointBoundary
)


class TestBoundaryHandlerCorrectness:
    """Test that boundary handlers correctly enforce bounds."""
    
    def test_clip_boundary(self):
        """Test clip boundary handler."""
        handler = ClipBoundary()
        bounds = [(-5, 5)] * 3
        
        # Test values outside bounds
        population = np.array([
            [10, 0, -10],    # Outside on both sides
            [3, -3, 0],      # Within bounds
            [6, -6, 0]       # Outside on both sides
        ])
        
        corrected = handler.apply(population, bounds)
        
        # Should be clipped to bounds
        assert np.all(corrected >= -5)
        assert np.all(corrected <= 5)
        np.testing.assert_array_equal(corrected[0], [5, 0, -5])
        np.testing.assert_array_equal(corrected[1], [3, -3, 0])
        np.testing.assert_array_equal(corrected[2], [5, -5, 0])
    
    def test_reflect_boundary(self):
        """Test reflect boundary handler."""
        handler = ReflectBoundary()
        bounds = [(-5, 5)] * 2
        
        # Test reflection
        population = np.array([
            [6, -6],   # Outside by 1 on each side
            [0, 0]     # Within bounds
        ])
        
        corrected = handler.apply(population, bounds)
        
        # Should be reflected
        assert np.all(corrected >= -5)
        assert np.all(corrected <= 5)
        # 6 reflects to 4, -6 reflects to -4
        np.testing.assert_array_almost_equal(corrected[0], [4, -4])
        np.testing.assert_array_equal(corrected[1], [0, 0])
    
    def test_random_boundary(self):
        """Test random boundary handler."""
        np.random.seed(42)
        handler = RandomBoundary()
        bounds = [(-5, 5)] * 3
        
        population = np.array([
            [10, 0, -10],
            [3, -3, 0]
        ])
        
        corrected = handler.apply(population, bounds)
        
        # Should be within bounds
        assert np.all(corrected >= -5)
        assert np.all(corrected <= 5)
        # Out-of-bounds values should be replaced with random values
        assert corrected[0, 0] != 10  # Was out of bounds
        assert corrected[0, 2] != -10  # Was out of bounds
        assert corrected[1, 0] == 3  # Was in bounds
    
    def test_wrap_boundary(self):
        """Test wrap boundary handler (toroidal)."""
        handler = WrapBoundary()
        bounds = [(-5, 5)] * 2
        
        population = np.array([
            [6, -6],   # Outside by 1
            [15, -15]  # Outside by 10
        ])
        
        corrected = handler.apply(population, bounds)
        
        # Should wrap around
        assert np.all(corrected >= -5)
        assert np.all(corrected <= 5)
    
    def test_midpoint_boundary(self):
        """Test midpoint boundary handler."""
        handler = MidpointBoundary()
        bounds = [(-10, 10)] * 2
        
        # Create parent population (needed for midpoint calculation)
        parents = np.array([
            [0, 0],
            [5, 5]
        ])
        
        # Offspring outside bounds
        population = np.array([
            [15, -15],
            [12, -12]
        ])
        
        corrected = handler.apply(population, bounds, parents)
        
        # Should be within bounds
        assert np.all(corrected >= -10)
        assert np.all(corrected <= 10)


class TestBoundaryHandlerEdgeCases:
    """Test boundary handler edge cases."""
    
    def test_all_within_bounds(self):
        """Test when all individuals are within bounds."""
        handler = ClipBoundary()
        bounds = [(-10, 10)] * 3
        
        population = np.array([
            [0, 0, 0],
            [5, -5, 3],
            [-3, 2, -1]
        ])
        
        corrected = handler.apply(population, bounds)
        
        # Should be unchanged
        np.testing.assert_array_equal(corrected, population)
    
    def test_asymmetric_bounds(self):
        """Test with asymmetric bounds."""
        handler = ClipBoundary()
        bounds = [(-5, 10), (-20, 5), (0, 100)]
        
        population = np.array([
            [15, -25, 150],
            [-10, 10, -5]
        ])
        
        corrected = handler.apply(population, bounds)
        
        # Check each dimension separately
        assert np.all(corrected[:, 0] >= -5) and np.all(corrected[:, 0] <= 10)
        assert np.all(corrected[:, 1] >= -20) and np.all(corrected[:, 1] <= 5)
        assert np.all(corrected[:, 2] >= 0) and np.all(corrected[:, 2] <= 100)
    
    def test_single_dimension(self):
        """Test with 1D problem."""
        handler = ClipBoundary()
        bounds = [(-5, 5)]
        
        population = np.array([[10], [-10], [0]])
        
        corrected = handler.apply(population, bounds)
        
        assert corrected.shape == (3, 1)
        np.testing.assert_array_equal(corrected, [[5], [-5], [0]])
    
    def test_large_population(self):
        """Test with large population."""
        handler = ClipBoundary()
        bounds = [(-10, 10)] * 5
        
        np.random.seed(42)
        population = np.random.uniform(-20, 20, size=(1000, 5))
        
        corrected = handler.apply(population, bounds)
        
        assert corrected.shape == (1000, 5)
        assert np.all(corrected >= -10)
        assert np.all(corrected <= 10)


class TestBoundaryHandlerReproducibility:
    """Test boundary handler reproducibility."""
    
    def test_clip_deterministic(self):
        """Test that clip is deterministic."""
        handler = ClipBoundary()
        bounds = [(-5, 5)] * 3
        
        population = np.random.uniform(-10, 10, size=(20, 3))
        
        corrected1 = handler.apply(population, bounds)
        corrected2 = handler.apply(population, bounds)
        
        np.testing.assert_array_equal(corrected1, corrected2)
    
    def test_random_with_seed(self):
        """Test random boundary with seed reproducibility."""
        bounds = [(-5, 5)] * 3
        population = np.array([[10, 0, -10], [3, -3, 0]])
        
        np.random.seed(42)
        handler1 = RandomBoundary()
        corrected1 = handler1.apply(population, bounds)
        
        np.random.seed(42)
        handler2 = RandomBoundary()
        corrected2 = handler2.apply(population, bounds)
        
        np.testing.assert_array_almost_equal(corrected1, corrected2)


class TestBoundaryHandlerValidity:
    """Test that boundary handlers produce valid outputs."""
    
    def test_no_nans(self):
        """Test that boundary handlers don't introduce NaNs."""
        handler = ClipBoundary()
        bounds = [(-10, 10)] * 5
        
        population = np.random.uniform(-20, 20, size=(50, 5))
        corrected = handler.apply(population, bounds)
        
        assert not np.any(np.isnan(corrected))
        assert not np.any(np.isinf(corrected))
    
    def test_shape_preservation(self):
        """Test that boundary handlers preserve shape."""
        handlers = [
            ClipBoundary(),
            ReflectBoundary(),
            RandomBoundary(),
            WrapBoundary()
        ]
        
        bounds = [(-10, 10)] * 5
        population = np.random.uniform(-20, 20, size=(30, 5))
        
        for handler in handlers:
            corrected = handler.apply(population, bounds)
            assert corrected.shape == population.shape
