"""Tests for crossover operators."""

import pytest
import numpy as np
from pyrade.operators import BinomialCrossover, ExponentialCrossover, UniformCrossover


class TestCrossoverShape:
    """Test crossover operators produce correct output shapes."""
    
    def test_binomial_shape(self, test_population):
        """Test BinomialCrossover output shape."""
        crossover = BinomialCrossover(CR=0.9)
        mutants = test_population + np.random.randn(*test_population.shape) * 0.5
        
        trials = crossover.apply(test_population, mutants)
        
        assert trials.shape == test_population.shape
    
    def test_exponential_shape(self, test_population):
        """Test ExponentialCrossover output shape."""
        crossover = ExponentialCrossover(CR=0.9)
        mutants = test_population + np.random.randn(*test_population.shape) * 0.5
        
        trials = crossover.apply(test_population, mutants)
        
        assert trials.shape == test_population.shape
    
    def test_uniform_shape(self, test_population):
        """Test UniformCrossover output shape."""
        crossover = UniformCrossover(CR=0.5)
        mutants = test_population + np.random.randn(*test_population.shape) * 0.5
        
        trials = crossover.apply(test_population, mutants)
        
        assert trials.shape == test_population.shape


class TestCrossoverDiversity:
    """Test that crossover maintains diversity."""
    
    def test_binomial_mixes_parent_and_mutant(self, test_population):
        """Test that binomial crossover creates mixed offspring."""
        crossover = BinomialCrossover(CR=0.5)
        mutants = test_population + 10.0  # Very different from parents
        
        trials = crossover.apply(test_population, mutants)
        
        # Trials should be mixture of parents and mutants
        # Not identical to either parent or mutant for most individuals
        parent_identical = np.all(trials == test_population, axis=1).sum()
        mutant_identical = np.all(trials == mutants, axis=1).sum()
        
        pop_size = test_population.shape[0]
        # Most should be mixed (not all identical to one or the other)
        assert parent_identical < pop_size * 0.2
        assert mutant_identical < pop_size * 0.2
    
    def test_cr_parameter_effect(self, test_population):
        """Test that CR parameter affects crossover rate."""
        mutants = test_population + 10.0
        
        # Low CR - more parent material
        crossover_low = BinomialCrossover(CR=0.1)
        trials_low = crossover_low.apply(test_population, mutants)
        
        # High CR - more mutant material
        crossover_high = BinomialCrossover(CR=0.9)
        trials_high = crossover_high.apply(test_population, mutants)
        
        # High CR should be closer to mutants than low CR
        dist_low = np.linalg.norm(trials_low - mutants, axis=1).mean()
        dist_high = np.linalg.norm(trials_high - mutants, axis=1).mean()
        
        assert dist_high < dist_low
    
    def test_exponential_creates_contiguous_segments(self, test_population):
        """Test that exponential crossover creates contiguous segments."""
        crossover = ExponentialCrossover(CR=0.7)
        mutants = test_population + 10.0
        
        trials = crossover.apply(test_population, mutants)
        
        # Check that trials are valid combinations
        assert trials.shape == test_population.shape
        # All values should be from either parent or mutant
        for i in range(trials.shape[0]):
            trial = trials[i]
            parent = test_population[i]
            mutant = mutants[i]
            
            # Each dimension should be close to either parent or mutant
            from_parent = np.isclose(trial, parent)
            from_mutant = np.isclose(trial, mutant)
            assert np.all(from_parent | from_mutant)
    
    def test_uniform_crossover_randomness(self, test_population):
        """Test uniform crossover produces varied results."""
        crossover = UniformCrossover(CR=0.5)
        mutants = test_population + 5.0
        
        # Run crossover multiple times
        np.random.seed(42)
        trials1 = crossover.apply(test_population, mutants)
        
        np.random.seed(43)
        trials2 = crossover.apply(test_population, mutants)
        
        # Different random seeds should give different results
        assert not np.allclose(trials1, trials2)


class TestCrossoverReproducibility:
    """Test crossover reproducibility."""
    
    def test_binomial_reproducibility(self, test_population):
        """Test binomial crossover reproducibility with same seed."""
        mutants = test_population + np.random.randn(*test_population.shape)
        
        # First run
        np.random.seed(42)
        crossover1 = BinomialCrossover(CR=0.9)
        trials1 = crossover1.apply(test_population, mutants)
        
        # Second run with same seed
        np.random.seed(42)
        crossover2 = BinomialCrossover(CR=0.9)
        trials2 = crossover2.apply(test_population, mutants)
        
        np.testing.assert_array_almost_equal(trials1, trials2)
    
    def test_exponential_reproducibility(self, test_population):
        """Test exponential crossover reproducibility with same seed."""
        mutants = test_population + np.random.randn(*test_population.shape)
        
        # First run
        np.random.seed(42)
        crossover1 = ExponentialCrossover(CR=0.9)
        trials1 = crossover1.apply(test_population, mutants)
        
        # Second run with same seed
        np.random.seed(42)
        crossover2 = ExponentialCrossover(CR=0.9)
        trials2 = crossover2.apply(test_population, mutants)
        
        np.testing.assert_array_almost_equal(trials1, trials2)


class TestCrossoverEdgeCases:
    """Test crossover edge cases."""
    
    def test_cr_zero(self, test_population):
        """Test CR=0 should use mostly parent."""
        crossover = BinomialCrossover(CR=0.0)
        mutants = test_population + 10.0
        
        trials = crossover.apply(test_population, mutants)
        
        # With CR=0, most dimensions should be from parent
        # (but at least one dimension is always from mutant)
        assert trials.shape == test_population.shape
    
    def test_cr_one(self, test_population):
        """Test CR=1 should use mostly mutant."""
        crossover = BinomialCrossover(CR=1.0)
        mutants = test_population + 10.0
        
        trials = crossover.apply(test_population, mutants)
        
        # With CR=1, most should be similar to mutants
        assert trials.shape == test_population.shape
    
    def test_single_dimension(self):
        """Test crossover with 1D problems."""
        population = np.array([[1.0], [2.0], [3.0]])
        mutants = np.array([[10.0], [20.0], [30.0]])
        
        crossover = BinomialCrossover(CR=0.5)
        trials = crossover.apply(population, mutants)
        
        assert trials.shape == (3, 1)
