# Contributing to PyRADE

We welcome contributions! This guide will help you get started.

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/yourusername/pyrade.git
cd pyrade
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

## Code Style

We use:
- **black** for code formatting
- **flake8** for linting
- **mypy** for type checking

Format your code:
```bash
black pyrade/
flake8 pyrade/
mypy pyrade/
```

## Testing

Run tests:
```bash
pytest tests/
pytest tests/ --cov=pyrade  # With coverage
```

## Adding New Features

### Adding a Mutation Strategy

1. Create your strategy in `pyrade/operators/mutation.py`:

```python
class MyMutation(MutationStrategy):
    def __init__(self, F=0.8):
        self.F = F
    
    def apply(self, population, fitness, best_idx, target_indices):
        # Your implementation
        # Must return mutants array
        pass
```

2. Add tests in `tests/test_mutation.py`
3. Update documentation in `docs/api_reference.md`
4. Add example usage

### Adding a Benchmark Function

1. Add to `pyrade/benchmarks/functions.py`:

```python
class MyFunction(BenchmarkFunction):
    def __init__(self, dim=30):
        super().__init__(dim)
        self.bounds = (-10, 10)
        self.optimum = 0.0
        self.optimum_location = np.zeros(dim)
    
    def __call__(self, x):
        # Your implementation
        pass
```

2. Add tests and documentation

## Pull Request Process

1. Create a feature branch:
```bash
git checkout -b feature/my-feature
```

2. Make your changes and commit:
```bash
git add .
git commit -m "feat: Add my feature"
```

3. Push and create PR:
```bash
git push origin feature/my-feature
```

4. Ensure:
   - All tests pass
   - Code is formatted
   - Documentation is updated
   - PR description is clear

## Commit Message Format

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding tests
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

## Questions?

- Open an issue on GitHub
- Email: arartawil@gmail.com

See also: [Code of Conduct](../CODE_OF_CONDUCT.md)
