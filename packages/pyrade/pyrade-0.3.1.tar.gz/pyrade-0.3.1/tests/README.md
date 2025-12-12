# PyRADE Test Suite

Comprehensive test suite for PyRADE package.

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with coverage
```bash
pytest tests/ --cov=pyrade --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_algorithm.py
pytest tests/test_mutation.py
```

### Run specific test
```bash
pytest tests/test_algorithm.py::TestAlgorithmConvergence::test_sphere_convergence
```

### Verbose output
```bash
pytest tests/ -v
```

## Test Coverage

The test suite covers:

### Algorithm Tests (`test_algorithm.py`)
- ✅ Convergence on simple problems
- ✅ Reproducibility (same seed = same results)
- ✅ Different seeds produce different results
- ✅ Result structure validation
- ✅ Max iterations respected
- ✅ Callback execution
- ✅ Fitness improvement over iterations
- ✅ Edge cases (1D, high-D, asymmetric bounds)

### Mutation Tests (`test_mutation.py`)
- ✅ Output shape validation for all strategies
- ✅ Mutants differ from parents
- ✅ Mutation factor (F) effect
- ✅ Reproducibility with same seed
- ✅ Parameter range validation
- ✅ No NaN/Inf values

### Crossover Tests (`test_crossover.py`)
- ✅ Output shape validation for all strategies
- ✅ Diversity maintenance
- ✅ Crossover rate (CR) effect
- ✅ Parent and mutant mixing
- ✅ Reproducibility
- ✅ Edge cases (CR=0, CR=1, 1D)

### Selection Tests (`test_selection.py`)
- ✅ Greedy property (keeps better individual)
- ✅ Monotonic fitness improvement
- ✅ Tournament selection behavior
- ✅ Elitist selection preservation
- ✅ Reproducibility
- ✅ No NaN/Inf values
- ✅ Bounds maintenance

### Boundary Handler Tests (`test_boundary.py`)
- ✅ Correctness of all boundary strategies
- ✅ Clip, Reflect, Random, Wrap, Midpoint
- ✅ Asymmetric bounds handling
- ✅ Edge cases (all within bounds, 1D, large population)
- ✅ Reproducibility
- ✅ Shape preservation
- ✅ No NaN/Inf values

### Benchmark Function Tests (`test_benchmarks.py`)
- ✅ Optimum locations for all functions
- ✅ Optimum values verification
- ✅ Function behavior (unimodal, multimodal)
- ✅ Various dimensions (1D to 50D)
- ✅ Bounds validation
- ✅ No NaN/Inf for valid inputs
- ✅ Scalar output
- ✅ Deterministic evaluation
- ✅ Consistency across repeated evaluations

## Test Statistics

- **Total Tests**: 100+
- **Functions Tested**: 12 benchmark functions
- **Operators Tested**: 4 mutation, 3 crossover, 3 selection
- **Boundary Handlers**: 5 strategies
- **Code Coverage Target**: >90%

## Continuous Integration

Tests are automatically run on:
- Push to main branch
- Pull requests
- GitHub Actions workflow

## Contributing Tests

When adding new features, please include:
1. Unit tests for the new functionality
2. Integration tests if applicable
3. Edge case tests
4. Documentation of test purpose

### Test Template

```python
def test_feature_name():
    """Test description: what is being tested and why."""
    # Arrange
    setup_code()
    
    # Act
    result = function_to_test()
    
    # Assert
    assert expected_condition(result)
```
