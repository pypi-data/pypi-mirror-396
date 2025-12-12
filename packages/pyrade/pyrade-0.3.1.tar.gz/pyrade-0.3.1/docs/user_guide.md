# User Guide

Comprehensive guide to using PyRADE effectively.

## Understanding Differential Evolution

Differential Evolution (DE) is a population-based optimization algorithm that:

1. Maintains a population of candidate solutions
2. Creates new candidates through mutation and crossover
3. Selects better solutions through competition
4. Iterates until convergence or termination

## Architecture Overview

PyRADE uses the Strategy pattern for maximum flexibility:

```
DifferentialEvolution
├── Population (manages candidate solutions)
├── MutationStrategy (how to create mutants)
├── CrossoverStrategy (how to mix parent and mutant)
├── SelectionStrategy (how to choose survivors)
├── BoundaryHandler (handles constraint violations)
└── TerminationCriterion (when to stop)
```

## Available Strategies

### Mutation Strategies

**DE/rand/1** (Default)
- Creates mutants from random individuals
- Good exploration, general-purpose
- Best for: Multimodal problems

```python
from pyrade.operators import DErand1
mutation = DErand1(F=0.8)
```

**DE/best/1**
- Uses best individual in population
- Fast convergence, exploitative
- Best for: Unimodal problems

```python
from pyrade.operators import DEbest1
mutation = DEbest1(F=0.8)
```

**DE/current-to-best/1**
- Balanced exploration/exploitation
- Adapts based on current individual
- Best for: Mixed landscapes

```python
from pyrade.operators import DEcurrentToBest1
mutation = DEcurrentToBest1(F=0.8, K=0.5)
```

**DE/rand/2**
- Uses two difference vectors
- More exploratory
- Best for: Highly multimodal problems

```python
from pyrade.operators import DErand2
mutation = DErand2(F=0.8)
```

### Crossover Strategies

**Binomial Crossover** (Default)
- Independent dimension-wise crossover
- Standard choice for most problems

```python
from pyrade.operators import BinomialCrossover
crossover = BinomialCrossover(CR=0.9)
```

**Exponential Crossover**
- Contiguous segment crossover
- Good for separable problems

```python
from pyrade.operators import ExponentialCrossover
crossover = ExponentialCrossover(CR=0.9)
```

**Uniform Crossover**
- Equal probability for all dimensions
- Maximum mixing

```python
from pyrade.operators import UniformCrossover
crossover = UniformCrossover(CR=0.5)
```

### Selection Strategies

**Greedy Selection** (Default)
- Keep better individual always
- Standard DE selection

```python
from pyrade.operators import GreedySelection
selection = GreedySelection()
```

**Tournament Selection**
- Tournament-based selection
- Maintains diversity

```python
from pyrade.operators import TournamentSelection
selection = TournamentSelection(tournament_size=3)
```

**Elitist Selection**
- Preserves top individuals
- Ensures best solutions survive

```python
from pyrade.operators import ElitistSelection
selection = ElitistSelection(elite_size=5)
```

## Parameter Tuning

### Population Size (`pop_size`)
- Rule of thumb: 5-10 × problem dimension
- Larger: better exploration, slower
- Smaller: faster, may miss optima

### Mutation Factor (`F`)
- Range: [0.4, 1.0]
- Default: 0.8
- Higher: more exploration
- Lower: more exploitation

### Crossover Rate (`CR`)
- Range: [0.0, 1.0]
- Default: 0.9
- Higher: more mixing
- Lower: more parent preservation

### Maximum Iterations (`max_iter`)
- Depends on problem complexity
- Start with: 100-500 for testing
- Production: 1000-10000

## Handling Constraints

Use penalty methods:

```python
def constrained_objective(x):
    # Original objective
    obj = my_function(x)
    
    # Add penalties for constraint violations
    penalty = 0
    if x[0] < 0:  # Constraint: x[0] >= 0
        penalty += 1000 * abs(x[0])
    
    return obj + penalty
```

## Progress Monitoring

Use callbacks to track optimization:

```python
history = []

def callback(iteration, best_fitness, best_solution):
    history.append(best_fitness)
    if iteration % 50 == 0:
        print(f"Iter {iteration}: {best_fitness:.6e}")

optimizer = DifferentialEvolution(
    objective_func=my_func,
    bounds=my_bounds,
    callback=callback
)
```

## Performance Tips

1. **Vectorize your objective function** if possible
2. **Use appropriate mutation strategy** for your problem type
3. **Tune F and CR** - defaults work well but tuning helps
4. **Start with smaller population** for quick testing
5. **Use multiprocessing** for expensive objective functions

## Common Patterns

### Optimization with Timeout

```python
from pyrade.utils import MaxTime

optimizer = DifferentialEvolution(
    objective_func=my_func,
    bounds=my_bounds,
    termination=MaxTime(max_seconds=60)
)
```

### Multiple Runs for Robustness

```python
best_results = []
for seed in range(10):
    optimizer = DifferentialEvolution(
        objective_func=my_func,
        bounds=my_bounds,
        seed=seed
    )
    result = optimizer.optimize()
    best_results.append(result['best_fitness'])

print(f"Mean: {np.mean(best_results):.6e}")
print(f"Std: {np.std(best_results):.6e}")
```

### Adaptive Strategy Selection

```python
# Start explorative, become exploitative
if iteration < max_iter // 2:
    mutation = DErand1(F=0.9)  # Explore
else:
    mutation = DEbest1(F=0.7)  # Exploit
```
