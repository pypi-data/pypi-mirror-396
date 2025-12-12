# Changelog

All notable changes to PyRADE will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2025-12-09

### Added
- **Progress Bar Support**: Integrated tqdm for visual progress tracking during optimization
- **Logging Support**: Comprehensive logging using Python's logging module throughout the codebase
- **Type Hints**: Added type hints to all major classes and methods for better IDE support and type checking
- **Enhanced Validation**: Improved input validation with detailed error messages

### Fixed
- **Boundary Handling**: Enhanced edge case handling for extreme bounds with proper inf/nan validation and overflow prevention
- **High-Dimensional Convergence**: Resolved convergence issues in problems with >100 dimensions through improved numerical stability and NaN/Inf handling
- **Memory Leaks**: Fixed memory accumulation in long-running optimizations with proper type conversions and array cleanup
- **Statistical Reporting**: Corrected ExperimentManager statistics with robust calculations, quartiles, and additional metrics
- Package build and distribution improvements
- Version consistency across configuration files

### Changed
- Updated package metadata for better PyPI compatibility
- Improved numerical stability in mutation and crossover operations
- Enhanced error handling in objective function evaluation
- Better error messages with contextual information

## [0.3.0] - 2025-11-30

### Added

#### Classic DE Variants (10 total)
- **DErand1bin**: DE/rand/1/bin - Classic random base with binomial crossover
- **DErand2bin**: DE/rand/2/bin - Two difference vectors for increased exploration
- **DEbest1bin**: DE/best/1/bin - Best individual as base vector
- **DEbest2bin**: DE/best/2/bin - Best individual with two difference vectors
- **DEcurrentToBest1bin**: DE/current-to-best/1/bin - Greedier search toward best
- **DEcurrentToRand1bin**: DE/current-to-rand/1/bin - Increased diversity maintenance
- **DERandToBest1bin**: DE/rand-to-best/1/bin - Balance between exploration and exploitation
- **DErand1exp**: DE/rand/1/exp - Exponential crossover for building block preservation
- **DErand1EitherOrBin**: DE/rand/1/either-or - Probabilistic F selection (F or 0.5*F)
- **ClassicDE**: Flexible base class for custom classic DE configurations

#### Mutation Strategies
- **DEbest2**: Best individual with two difference vectors
- **DEcurrentToRand1**: Current-to-random mutation with configurable K parameter
- **DERandToBest1**: Random-to-best mutation for balanced search
- **DErand1EitherOr**: Probabilistic F selection for adaptive step sizes

#### Adaptive DE Variants
- **jDE**: Self-adaptive F and CR parameters with tau-based adaptation
- **SaDE**: Self-adaptive Differential Evolution (placeholder)
- **JADE**: Adaptive DE with optional external archive (placeholder)
- **CoDE**: Composite DE with multiple strategies (placeholder)

#### Algorithm Organization
- Created `pyrade/algorithms/` module with categorical structure:
  - `classic/`: Traditional DE variants
  - `adaptive/`: Self-adaptive parameter control variants
  - `multi_population/`: Multi-population and ensemble methods (placeholder)
  - `hybrid/`: Hybrid and enhanced variants (placeholder)

#### Examples & Experiments
- **algorithm_categories_demo.py**: Demonstrates all 8 classic variants
- **full_classic_experiments.py**: Comprehensive benchmarking framework with:
  - 5 test functions (Sphere, Rosenbrock, Rastrigin, Ackley, Schwefel)
  - 30 independent runs per algorithm
  - Convergence plots, boxplots, performance profiles
  - Statistical heatmaps and speed analysis
  - Publication-ready visualizations

#### Documentation
- **pyrade/algorithms/README.md**: Complete guide to algorithm categories and usage
- Comprehensive docstrings for all new classes and methods
- Algorithm comparison guidelines and parameter tuning recommendations

### Changed
- Reorganized package structure for better scalability
- Updated `pyrade/__init__.py` to export all new variants
- Enhanced operator exports in `pyrade/operators/__init__.py`
- Improved test coverage with `test_new_variants.py`

### Fixed
- Maintained backward compatibility with legacy `DifferentialEvolution` class
- Ensured all operators work with vectorized NumPy operations
- Verified distinct index selection in all mutation strategies

### Performance
- All mutation strategies fully vectorized with NumPy (3-5x speedup)
- Efficient memory usage with in-place operations where possible
- Optimized random number generation for large populations

## [0.2.0] - 2024

### Initial Release
- Core `DifferentialEvolution` algorithm implementation
- Basic mutation strategies: DErand1, DEbest1, DEcurrentToBest1, DErand2
- Crossover operators: BinomialCrossover, ExponentialCrossover, UniformCrossover
- Selection strategies: GreedySelection
- Population management with bounds handling
- Visualization tools and experiment management
- Performance optimizations with NumPy vectorization

---

## Release Notes

### v0.3.0 Highlights

**Complete Classic DE Variant Collection**: All 10 standard DE variants from the literature are now implemented and tested, providing comprehensive coverage for different optimization scenarios.

**Organized Architecture**: New categorical structure makes it easy to find and use the right algorithm for your problem:
- Classic variants for standard optimization
- Adaptive variants for parameter-free optimization (jDE fully implemented)
- Placeholders for multi-population and hybrid methods (coming soon)

**Production-Ready Examples**: New comprehensive experiment framework with statistical analysis and publication-quality visualizations.

**Backward Compatible**: All existing code continues to work - new variants are additions, not replacements.

### Migration Guide (0.2.0 → 0.3.0)

No breaking changes! Your existing code works as-is. To use new variants:

```python
# Old way (still works)
from pyrade import DifferentialEvolution

# New way (recommended for specific variants)
from pyrade import DErand1bin, DEbest1bin, jDE

# Or import from category modules
from pyrade.algorithms.classic import ClassicDE
from pyrade.algorithms.adaptive import jDE
```

### What's Next (v0.4.0 Roadmap)

- Complete implementations of SaDE, JADE, and CoDE adaptive algorithms
- Multi-population variants (Island Model, Cooperative Coevolution)
- Hybrid variants (DE-PSO, DE-GA, Memetic DE)
- Constraint handling techniques
- Multi-objective DE (MODE, NSDE)
- Enhanced CEC benchmark integration
- Performance profiling and optimization guide

---

[0.3.0]: https://github.com/arartawil/pyrade/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/arartawil/pyrade/releases/tag/v0.2.0
