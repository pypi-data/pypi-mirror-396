# Differential Evolution Algorithm Variants

This directory organizes DE algorithms into categories based on their characteristics and mechanisms.

## Directory Structure

```
algorithms/
├── classic/          # Traditional DE variants
├── adaptive/         # Self-adaptive parameter control
├── multi_population/ # Multi-population & ensemble methods
└── hybrid/           # Hybrid & enhanced variants
```

## Categories

### 1. Classic DE Variants (`classic/`)

Traditional differential evolution algorithms with fixed parameters:

- **`ClassicDE`** - Base class with configurable mutation/crossover/selection
- **`DErand1bin`** - DE/rand/1/bin (most popular, balanced)
- **`DEbest1bin`** - DE/best/1/bin (fast convergence, exploitative)
- **`DEcurrentToBest1bin`** - DE/current-to-best/1/bin (balanced)
- **`DErand2bin`** - DE/rand/2/bin (high exploration)

**Usage:**
```python
from pyrade.algorithms.classic import DErand1bin

de = DErand1bin(objective_func, bounds=[(-100, 100)] * 10)
result = de.optimize()
```

### 2. Adaptive DE Variants (`adaptive/`)

Algorithms with self-adaptive parameter control (coming soon):

- **JADE** - Adaptive DE with Optional External Archive
- **SHADE** - Success-History based Adaptive DE
- **jDE** - Self-Adaptive DE
- **SaDE** - Self-adaptive DE with Neighborhood Search
- **EPSDE** - Ensemble of Parameters and Strategies DE

These automatically tune F, CR, and other parameters during optimization.

### 3. Multi-Population Variants (`multi_population/`)

Algorithms using multiple populations or ensembles (coming soon):

- **Island Model DE** - Multiple populations with migration
- **Cooperative Coevolution DE** - Decomposition-based approach
- **Ensemble DE** - Multiple strategies in parallel
- **Distributed DE** - Parallel population processing

Designed for large-scale and complex problems.

### 4. Hybrid & Enhanced Variants (`hybrid/`)

Algorithms combining DE with other techniques (coming soon):

- **Hybrid PSO-DE** - Combines Particle Swarm with DE
- **Memetic DE** - DE with local search
- **Opposition-based DE** - Uses opposition-based learning
- **Chaotic DE** - DE with chaotic maps
- **Levy Flight DE** - DE with Levy flight operators
- **Quantum DE** - Quantum-inspired mechanisms

Enhanced for specific problem classes.

## Quick Reference

| Algorithm | Type | Best For | Convergence | Exploration |
|-----------|------|----------|-------------|-------------|
| DErand1bin | Classic | General purpose | Medium | Medium |
| DEbest1bin | Classic | Unimodal functions | Fast | Low |
| DEcurrentToBest1bin | Classic | Wide range | Medium | Medium |
| DErand2bin | Classic | Multimodal | Slow | High |
| JADE | Adaptive | Auto-tuning needed | Fast | Adaptive |
| SHADE | Adaptive | State-of-the-art | Very Fast | Adaptive |

## Adding New Variants

To add a new variant:

1. Determine the category (classic/adaptive/multi_population/hybrid)
2. Implement the algorithm class inheriting from appropriate base
3. Add to category's `__init__.py`
4. Update main `algorithms/__init__.py`
5. Add tests and documentation

See existing implementations for examples.
