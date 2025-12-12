# Examples

Real-world examples and use cases.

## Engineering Design Optimization

### Pressure Vessel Design

Minimize the cost of a pressure vessel while satisfying constraints:

```python
import numpy as np
from pyrade import DifferentialEvolution

def pressure_vessel_cost(x):
    """
    Minimize cost of pressure vessel design.
    x[0]: shell thickness
    x[1]: head thickness
    x[2]: inner radius
    x[3]: length
    """
    # Material and welding costs
    cost = (
        0.6224 * x[0] * x[2] * x[3] +
        1.7781 * x[1] * x[2]**2 +
        3.1661 * x[0]**2 * x[3] +
        19.84 * x[0]**2 * x[2]
    )
    
    # Constraint penalties
    penalty = 0
    
    # Minimum thickness constraints
    if x[0] < 0.0625:
        penalty += 1000 * (0.0625 - x[0])**2
    if x[1] < 0.0625:
        penalty += 1000 * (0.0625 - x[1])**2
    
    # Volume constraint
    volume = np.pi * x[2]**2 * x[3] + 4/3 * np.pi * x[2]**3
    if volume < 1296000:
        penalty += 10 * (1296000 - volume)**2
    
    return cost + penalty

# Define bounds
bounds = [
    (0.0625, 99),   # shell thickness
    (0.0625, 99),   # head thickness
    (10, 200),      # inner radius
    (10, 200)       # length
]

# Optimize
optimizer = DifferentialEvolution(
    objective_func=pressure_vessel_cost,
    bounds=bounds,
    pop_size=40,
    max_iter=500
)

result = optimizer.optimize()
print(f"Optimal cost: ${result['best_fitness']:.2f}")
print(f"Design: {result['best_solution']}")
```

## Machine Learning Hyperparameter Tuning

Optimize neural network hyperparameters:

```python
from pyrade import DifferentialEvolution
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score

def optimize_nn(x):
    """Optimize neural network hyperparameters"""
    hidden_layer_sizes = int(x[0])
    learning_rate = 10 ** x[1]
    alpha = 10 ** x[2]
    
    model = MLPClassifier(
        hidden_layer_sizes=(hidden_layer_sizes,),
        learning_rate_init=learning_rate,
        alpha=alpha,
        max_iter=1000,
        random_state=42
    )
    
    # Return negative accuracy (we minimize)
    score = cross_val_score(model, X_train, y_train, cv=5)
    return -np.mean(score)

bounds = [
    (10, 200),      # hidden layer size
    (-5, -1),       # log10(learning_rate)
    (-5, -1)        # log10(alpha)
]

optimizer = DifferentialEvolution(
    objective_func=optimize_nn,
    bounds=bounds,
    pop_size=20,
    max_iter=50
)

result = optimizer.optimize()
print(f"Best accuracy: {-result['best_fitness']:.4f}")
```

## Portfolio Optimization

Optimize asset allocation:

```python
import numpy as np
from pyrade import DifferentialEvolution

def portfolio_risk(weights, returns, cov_matrix):
    """
    Minimize portfolio risk while targeting return.
    weights: asset allocation (must sum to 1)
    """
    # Normalize weights to sum to 1
    weights = weights / np.sum(weights)
    
    # Portfolio return
    portfolio_return = np.dot(weights, returns)
    
    # Portfolio variance (risk)
    portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
    
    # Minimize variance with return penalty
    target_return = 0.10
    return_penalty = 1000 * max(0, target_return - portfolio_return)**2
    
    return portfolio_variance + return_penalty

# Example data
n_assets = 5
returns = np.random.rand(n_assets) * 0.15
cov_matrix = np.random.rand(n_assets, n_assets)
cov_matrix = (cov_matrix + cov_matrix.T) / 2

bounds = [(0, 1)] * n_assets

optimizer = DifferentialEvolution(
    objective_func=lambda w: portfolio_risk(w, returns, cov_matrix),
    bounds=bounds,
    pop_size=50,
    max_iter=300
)

result = optimizer.optimize()
optimal_weights = result['best_solution'] / np.sum(result['best_solution'])
print(f"Optimal allocation: {optimal_weights}")
```

## Function Approximation

Find parameters for a model to fit data:

```python
import numpy as np
from pyrade import DifferentialEvolution

def model(x, params):
    """Model: y = a*sin(b*x + c) + d"""
    a, b, c, d = params
    return a * np.sin(b * x + c) + d

def fit_error(params):
    """MSE between model and data"""
    predictions = model(x_data, params)
    return np.mean((y_data - predictions)**2)

# Generate noisy data
x_data = np.linspace(0, 10, 100)
true_params = [2, 0.5, 1, 0.5]
y_data = model(x_data, true_params) + np.random.normal(0, 0.1, 100)

# Optimize
bounds = [
    (-5, 5),    # amplitude
    (0, 2),     # frequency
    (0, 2*np.pi),  # phase
    (-2, 2)     # offset
]

optimizer = DifferentialEvolution(
    objective_func=fit_error,
    bounds=bounds,
    pop_size=50,
    max_iter=200
)

result = optimizer.optimize()
print(f"True params: {true_params}")
print(f"Found params: {result['best_solution']}")
print(f"MSE: {result['best_fitness']:.6f}")
```

## Custom Strategy Example

Create and use a custom adaptive mutation strategy:

```python
from pyrade.operators import MutationStrategy
import numpy as np

class AdaptiveMutation(MutationStrategy):
    """Adapts F based on fitness improvement"""
    
    def __init__(self, F_min=0.4, F_max=1.0):
        self.F_min = F_min
        self.F_max = F_max
        self.F = F_max
        self.prev_best = float('inf')
    
    def apply(self, population, fitness, best_idx, target_indices):
        pop_size, dim = population.shape
        
        # Adapt F based on improvement
        current_best = fitness[best_idx]
        if current_best < self.prev_best:
            # Improving: increase exploration
            self.F = min(self.F * 1.1, self.F_max)
        else:
            # Stagnating: increase exploitation
            self.F = max(self.F * 0.9, self.F_min)
        self.prev_best = current_best
        
        # Standard DE/rand/1 with adaptive F
        indices = np.arange(pop_size)
        r1 = np.random.choice(indices, size=pop_size)
        r2 = np.random.choice(indices, size=pop_size)
        r3 = np.random.choice(indices, size=pop_size)
        
        mutants = population[r1] + self.F * (population[r2] - population[r3])
        return mutants

# Use custom strategy
from pyrade import DifferentialEvolution
from pyrade.benchmarks import Rastrigin

func = Rastrigin(dim=20)
optimizer = DifferentialEvolution(
    objective_func=func,
    bounds=func.get_bounds_array(),
    mutation=AdaptiveMutation(),
    pop_size=100,
    max_iter=500
)

result = optimizer.optimize()
print(f"Result: {result['best_fitness']:.6e}")
```

## Parallel Evaluation

For expensive objective functions, use multiprocessing:

```python
from multiprocessing import Pool
import numpy as np
from pyrade import DifferentialEvolution

def expensive_function(x):
    """Simulated expensive computation"""
    import time
    time.sleep(0.01)  # Simulate delay
    return np.sum(x**2)

def parallel_objective(population):
    """Evaluate population in parallel"""
    with Pool() as pool:
        results = pool.map(expensive_function, population)
    return np.array(results)

# Note: You'd need to modify DE to accept batch evaluation
# This is conceptual - shows the pattern
```
