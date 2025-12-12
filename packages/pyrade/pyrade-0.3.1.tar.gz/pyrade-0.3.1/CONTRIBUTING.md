# Contributing to PyRADE

First off, thank you for considering contributing to PyRADE! It's people like you that make PyRADE such a great tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
  - [Git Commit Messages](#git-commit-messages)
  - [Python Style Guide](#python-style-guide)
  - [Documentation Style Guide](#documentation-style-guide)
- [Additional Notes](#additional-notes)

## Code of Conduct

This project and everyone participating in it is governed by the [PyRADE Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

* **Use a clear and descriptive title** for the issue
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples** to demonstrate the steps
* **Describe the behavior you observed** and what you expected
* **Include screenshots or code snippets** if relevant
* **Specify your environment** (OS, Python version, NumPy version)

**Example Bug Report:**
```markdown
## Bug Description
DifferentialEvolution fails with ValueError when bounds are not properly formatted

## Steps to Reproduce
1. Create optimizer with single-value bounds
2. Run optimization
3. See error

## Expected Behavior
Should handle bounds gracefully or provide clear error message

## Actual Behavior
ValueError: Invalid bounds shape

## Environment
- OS: Windows 11
- Python: 3.10.2
- NumPy: 1.23.0
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Explain why this enhancement would be useful**
* **List any alternative solutions or features you've considered**
* **Include code examples** if applicable

**Enhancement Ideas:**
- New mutation strategies (e.g., DE/rand-to-best/2)
- Additional benchmark functions
- Performance optimizations
- New boundary handling methods
- Enhanced termination criteria
- Better visualization tools

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the style guidelines
3. **Add tests** if you've added code that should be tested
4. **Update documentation** for any changed functionality
5. **Ensure the test suite passes**
6. **Issue the pull request**

**Pull Request Template:**
```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Performance improvement
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Tested on multiple Python versions

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented if necessary)
```

## Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/arartawil/pyrade.git
cd pyrade
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install -e .  # Install in editable mode
```

### 4. Install Development Dependencies
```bash
pip install pytest pytest-cov black flake8 mypy
```

### 5. Run Tests
```bash
python test_installation.py
python -m pytest  # If you add unit tests
```

## Style Guidelines

### Git Commit Messages

Use conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(operators): add DE/best/2 mutation strategy
fix(core): handle edge case in population initialization
docs(readme): update installation instructions
perf(mutation): optimize vectorized operations in DErand1
```

### Python Style Guide

- Follow **PEP 8** style guidelines
- Use **type hints** for function arguments and returns
- Maximum line length: **100 characters**
- Use **docstrings** for all public modules, classes, and functions

**Docstring Format (NumPy Style):**
```python
def example_function(x, y, z=None):
    """
    Brief description of function.
    
    Longer description if needed, explaining what the
    function does in more detail.
    
    Parameters
    ----------
    x : ndarray
        Description of x
    y : float
        Description of y
    z : int, optional
        Description of z, by default None
    
    Returns
    -------
    result : float
        Description of return value
    
    Examples
    --------
    >>> example_function([1, 2, 3], 0.5)
    2.5
    """
    pass
```

**Code Formatting:**
```python
# Use black for automatic formatting
black pyrade/

# Check with flake8
flake8 pyrade/

# Type checking with mypy
mypy pyrade/
```

### Documentation Style Guide

- Use **Markdown** for documentation files
- Include **code examples** for all public APIs
- Keep examples **simple and practical**
- Update **API_DOCUMENTATION.md** for API changes
- Add **inline comments** for complex algorithms

## Additional Notes

### Project Structure

```
pyrade/
├── core/           # Core algorithm and population management
├── operators/      # Mutation, crossover, selection strategies
├── utils/          # Utility functions (boundaries, termination)
└── benchmarks/     # Test functions

examples/           # Usage examples
```

### Adding New Mutation Strategies

1. Inherit from `MutationStrategy` base class
2. Implement the `apply()` method with vectorized operations
3. Add docstring with algorithm description
4. Update `operators/__init__.py` to export the new strategy
5. Add example usage in `examples/custom_strategy.py`
6. Update documentation

**Template:**
```python
class MyMutation(MutationStrategy):
    """
    Brief description of the mutation strategy.
    
    Mathematical formula: v = ...
    
    Parameters
    ----------
    F : float
        Mutation factor
    """
    
    def __init__(self, F=0.8):
        self.F = F
    
    def apply(self, population, fitness, best_idx, target_indices):
        """Apply mutation (fully vectorized)."""
        # Vectorized implementation here
        mutants = ...
        return mutants
```

### Performance Guidelines

- **Always use vectorized NumPy operations**
- **Avoid Python loops** over populations
- **Profile code** before and after optimizations
- **Benchmark** against baseline implementations
- Target: maintain **3-5x speedup** over monolithic implementations

### Testing Guidelines

- Write tests for new features
- Test edge cases and boundary conditions
- Ensure backward compatibility
- Run performance benchmarks

## Questions?

Feel free to open an issue for questions or join discussions!

## Attribution

Thank you to all contributors who help improve PyRADE! 🎉

---

**Happy Coding!** 🚀
