"""Test configuration and fixtures for PyRADE test suite."""

import pytest
import numpy as np


@pytest.fixture
def random_seed():
    """Fixed random seed for reproducible tests."""
    return 42


@pytest.fixture
def simple_sphere():
    """Simple sphere function for testing."""
    def sphere(x):
        return np.sum(x**2)
    return sphere


@pytest.fixture
def simple_bounds():
    """Simple bounds for testing."""
    return [(-10, 10)] * 5


@pytest.fixture
def test_population():
    """Generate a test population."""
    np.random.seed(42)
    return np.random.uniform(-10, 10, size=(20, 5))


@pytest.fixture
def test_fitness():
    """Generate test fitness values."""
    np.random.seed(42)
    return np.random.uniform(0, 100, size=20)
