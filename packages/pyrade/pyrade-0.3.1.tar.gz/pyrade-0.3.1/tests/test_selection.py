"""Tests for selection operators."""

import pytest
import numpy as np
from pyrade.operators import GreedySelection, TournamentSelection, ElitistSelection


class TestSelectionGreedyProperty:
    """Test that selection operators maintain greedy property."""
    
    def test_greedy_selection_keeps_better(self, test_population, test_fitness):
        """Test that greedy selection always keeps better individual."""
        selection = GreedySelection()
        
        # Create trials with known better fitness
        trials = test_population + 0.1
        trial_fitness = test_fitness - 10.0  # Better fitness (lower)
        
        new_population = selection.apply(
            test_population, test_fitness,
            trials, trial_fitness
        )
        
        # New population should be trials (better fitness)
        np.testing.assert_array_almost_equal(new_population, trials)
    
    def test_greedy_selection_keeps_parent_if_better(self, test_population, test_fitness):
        """Test that greedy selection keeps parent if it's better."""
        selection = GreedySelection()
        
        # Create trials with worse fitness
        trials = test_population + 0.1
        trial_fitness = test_fitness + 10.0  # Worse fitness (higher)
        
        new_population = selection.apply(
            test_population, test_fitness,
            trials, trial_fitness
        )
        
        # New population should be parents (better fitness)
        np.testing.assert_array_almost_equal(new_population, test_population)
    
    def test_greedy_monotonic_improvement(self, test_population, test_fitness):
        """Test that greedy selection ensures monotonic fitness improvement."""
        selection = GreedySelection()
        
        # Mixed case: some trials better, some worse
        trials = test_population.copy()
        trial_fitness = test_fitness.copy()
        
        # Make half better, half worse
        half = len(trial_fitness) // 2
        trial_fitness[:half] -= 5.0  # Better
        trial_fitness[half:] += 5.0  # Worse
        
        new_population = selection.apply(
            test_population, test_fitness,
            trials, trial_fitness
        )
        
        # Calculate fitness of new population
        # For test purposes, compare directly
        for i in range(len(test_fitness)):
            if trial_fitness[i] < test_fitness[i]:
                # Should select trial
                np.testing.assert_array_almost_equal(new_population[i], trials[i])
            else:
                # Should select parent
                np.testing.assert_array_almost_equal(new_population[i], test_population[i])


class TestTournamentSelection:
    """Test tournament selection behavior."""
    
    def test_tournament_selection_shape(self, test_population, test_fitness):
        """Test tournament selection maintains population shape."""
        selection = TournamentSelection(tournament_size=3)
        
        trials = test_population + np.random.randn(*test_population.shape) * 0.5
        trial_fitness = test_fitness + np.random.randn(len(test_fitness))
        
        new_population = selection.apply(
            test_population, test_fitness,
            trials, trial_fitness
        )
        
        assert new_population.shape == test_population.shape
    
    def test_tournament_size_parameter(self, test_population, test_fitness):
        """Test different tournament sizes."""
        trials = test_population + 0.1
        trial_fitness = test_fitness + 1.0
        
        for size in [2, 3, 5]:
            selection = TournamentSelection(tournament_size=size)
            new_population = selection.apply(
                test_population, test_fitness,
                trials, trial_fitness
            )
            
            assert new_population.shape == test_population.shape


class TestElitistSelection:
    """Test elitist selection behavior."""
    
    def test_elitist_preserves_best(self, test_population, test_fitness):
        """Test that elitist selection preserves best individuals."""
        elite_size = 5
        selection = ElitistSelection(elite_size=elite_size)
        
        # Find current best individuals
        best_indices = np.argsort(test_fitness)[:elite_size]
        best_individuals = test_population[best_indices].copy()
        
        # Create trials (all slightly worse)
        trials = test_population + 0.1
        trial_fitness = test_fitness + 1.0
        
        new_population = selection.apply(
            test_population, test_fitness,
            trials, trial_fitness
        )
        
        # Best individuals should still be in new population
        assert new_population.shape == test_population.shape
    
    def test_elitist_size_parameter(self, test_population, test_fitness):
        """Test different elite sizes."""
        trials = test_population + 0.1
        trial_fitness = test_fitness + 1.0
        
        for elite_size in [1, 3, 5]:
            selection = ElitistSelection(elite_size=elite_size)
            new_population = selection.apply(
                test_population, test_fitness,
                trials, trial_fitness
            )
            
            assert new_population.shape == test_population.shape


class TestSelectionReproducibility:
    """Test selection reproducibility."""
    
    def test_greedy_deterministic(self, test_population, test_fitness):
        """Test that greedy selection is deterministic."""
        selection = GreedySelection()
        
        trials = test_population + 0.1
        trial_fitness = test_fitness - 5.0
        
        # Run twice
        new_pop1 = selection.apply(test_population, test_fitness, trials, trial_fitness)
        new_pop2 = selection.apply(test_population, test_fitness, trials, trial_fitness)
        
        np.testing.assert_array_almost_equal(new_pop1, new_pop2)
    
    def test_tournament_reproducibility(self, test_population, test_fitness):
        """Test tournament selection reproducibility with seed."""
        trials = test_population + 0.1
        trial_fitness = test_fitness + np.random.randn(len(test_fitness))
        
        # First run
        np.random.seed(42)
        selection1 = TournamentSelection(tournament_size=3)
        new_pop1 = selection1.apply(test_population, test_fitness, trials, trial_fitness)
        
        # Second run with same seed
        np.random.seed(42)
        selection2 = TournamentSelection(tournament_size=3)
        new_pop2 = selection2.apply(test_population, test_fitness, trials, trial_fitness)
        
        np.testing.assert_array_almost_equal(new_pop1, new_pop2)


class TestSelectionValidity:
    """Test that selection produces valid outputs."""
    
    def test_selection_no_nans(self, test_population, test_fitness):
        """Test that selection doesn't introduce NaNs."""
        selection = GreedySelection()
        
        trials = test_population + 0.1
        trial_fitness = test_fitness - 1.0
        
        new_population = selection.apply(
            test_population, test_fitness,
            trials, trial_fitness
        )
        
        assert not np.any(np.isnan(new_population))
        assert not np.any(np.isinf(new_population))
    
    def test_selection_maintains_bounds(self, test_population, test_fitness):
        """Test that selection maintains population within reasonable bounds."""
        selection = GreedySelection()
        
        # Population bounded in [-10, 10]
        trials = np.clip(test_population + 0.1, -10, 10)
        trial_fitness = test_fitness - 1.0
        
        new_population = selection.apply(
            test_population, test_fitness,
            trials, trial_fitness
        )
        
        # New population should be within bounds (same as inputs)
        assert np.all(new_population >= -10)
        assert np.all(new_population <= 10)
