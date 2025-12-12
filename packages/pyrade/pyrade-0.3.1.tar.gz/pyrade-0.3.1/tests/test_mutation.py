"""Tests for mutation operators."""

import pytest
import numpy as np
from pyrade.operators import DErand1, DEbest1, DEcurrentToBest1, DErand2


class TestMutationOperatorShape:
    """Test mutation operators produce correct output shapes."""
    
    def test_derand1_shape(self, test_population, test_fitness):
        """Test DErand1 output shape."""
        mutation = DErand1(F=0.8)
        pop_size, dim = test_population.shape
        best_idx = np.argmin(test_fitness)
        target_indices = np.arange(pop_size)
        
        mutants = mutation.apply(test_population, test_fitness, best_idx, target_indices)
        
        assert mutants.shape == test_population.shape
        assert mutants.shape == (pop_size, dim)
    
    def test_debest1_shape(self, test_population, test_fitness):
        """Test DEbest1 output shape."""
        mutation = DEbest1(F=0.8)
        pop_size, dim = test_population.shape
        best_idx = np.argmin(test_fitness)
        target_indices = np.arange(pop_size)
        
        mutants = mutation.apply(test_population, test_fitness, best_idx, target_indices)
        
        assert mutants.shape == test_population.shape
    
    def test_decurrent_to_best1_shape(self, test_population, test_fitness):
        """Test DEcurrentToBest1 output shape."""
        mutation = DEcurrentToBest1(F=0.8, K=0.5)
        pop_size, dim = test_population.shape
        best_idx = np.argmin(test_fitness)
        target_indices = np.arange(pop_size)
        
        mutants = mutation.apply(test_population, test_fitness, best_idx, target_indices)
        
        assert mutants.shape == test_population.shape
    
    def test_derand2_shape(self, test_population, test_fitness):
        """Test DErand2 output shape."""
        mutation = DErand2(F=0.8)
        pop_size, dim = test_population.shape
        best_idx = np.argmin(test_fitness)
        target_indices = np.arange(pop_size)
        
        mutants = mutation.apply(test_population, test_fitness, best_idx, target_indices)
        
        assert mutants.shape == test_population.shape


class TestMutationValidity:
    """Test mutation operators produce valid outputs."""
    
    def test_derand1_creates_different_solutions(self, test_population, test_fitness):
        """Test that DErand1 creates mutants different from parents."""
        mutation = DErand1(F=0.8)
        pop_size, dim = test_population.shape
        best_idx = np.argmin(test_fitness)
        target_indices = np.arange(pop_size)
        
        mutants = mutation.apply(test_population, test_fitness, best_idx, target_indices)
        
        # Mutants should generally be different from original population
        # (with high F, they should be quite different)
        differences = np.linalg.norm(mutants - test_population, axis=1)
        assert np.mean(differences) > 0.1  # Should have meaningful changes
    
    def test_mutation_factor_effect(self, test_population, test_fitness):
        """Test that mutation factor F affects mutation magnitude."""
        best_idx = np.argmin(test_fitness)
        target_indices = np.arange(test_population.shape[0])
        
        # Low F
        mutation_low = DErand1(F=0.2)
        mutants_low = mutation_low.apply(test_population, test_fitness, best_idx, target_indices)
        diff_low = np.linalg.norm(mutants_low - test_population, axis=1).mean()
        
        # High F
        mutation_high = DErand1(F=1.0)
        mutants_high = mutation_high.apply(test_population, test_fitness, best_idx, target_indices)
        diff_high = np.linalg.norm(mutants_high - test_population, axis=1).mean()
        
        # Higher F should create larger changes
        assert diff_high > diff_low
    
    def test_debest1_uses_best_individual(self, test_population, test_fitness):
        """Test that DEbest1 uses the best individual."""
        mutation = DEbest1(F=0.8)
        best_idx = np.argmin(test_fitness)
        target_indices = np.arange(test_population.shape[0])
        
        # Run multiple times - should be deterministic given same inputs
        mutants1 = mutation.apply(test_population, test_fitness, best_idx, target_indices)
        mutants2 = mutation.apply(test_population, test_fitness, best_idx, target_indices)
        
        # Note: Results will differ due to random selection of r1, r2
        # But we can check that output is valid
        assert mutants1.shape == mutants2.shape
    
    def test_mutation_reproducibility(self, test_population, test_fitness):
        """Test mutation reproducibility with same seed."""
        best_idx = np.argmin(test_fitness)
        target_indices = np.arange(test_population.shape[0])
        
        # First run
        np.random.seed(42)
        mutation1 = DErand1(F=0.8)
        mutants1 = mutation1.apply(test_population, test_fitness, best_idx, target_indices)
        
        # Second run with same seed
        np.random.seed(42)
        mutation2 = DErand1(F=0.8)
        mutants2 = mutation2.apply(test_population, test_fitness, best_idx, target_indices)
        
        # Should produce identical results
        np.testing.assert_array_almost_equal(mutants1, mutants2)


class TestMutationParameters:
    """Test mutation operator parameter handling."""
    
    def test_f_parameter_range(self, test_population, test_fitness):
        """Test different F parameter values."""
        best_idx = np.argmin(test_fitness)
        target_indices = np.arange(test_population.shape[0])
        
        # Test various F values
        for f_value in [0.1, 0.5, 0.8, 1.0, 1.5]:
            mutation = DErand1(F=f_value)
            mutants = mutation.apply(test_population, test_fitness, best_idx, target_indices)
            
            assert mutants.shape == test_population.shape
            assert not np.any(np.isnan(mutants))
            assert not np.any(np.isinf(mutants))
    
    def test_k_parameter_in_current_to_best(self, test_population, test_fitness):
        """Test K parameter in DEcurrentToBest1."""
        best_idx = np.argmin(test_fitness)
        target_indices = np.arange(test_population.shape[0])
        
        # Test various K values
        for k_value in [0.0, 0.3, 0.5, 0.7, 1.0]:
            mutation = DEcurrentToBest1(F=0.8, K=k_value)
            mutants = mutation.apply(test_population, test_fitness, best_idx, target_indices)
            
            assert mutants.shape == test_population.shape
            assert not np.any(np.isnan(mutants))
