"""
Benchmark functions for testing optimization algorithms.

This module provides standard test functions commonly used to
evaluate and compare optimization algorithms.
"""

import numpy as np


class BenchmarkFunction:
    """
    Base class for benchmark functions.
    
    Attributes
    ----------
    dim : int
        Dimensionality of the function
    bounds : tuple
        Search space bounds (lb, ub)
    optimum : float
        Known global optimum value
    optimum_location : ndarray, optional
        Location of global optimum
    """
    
    def __init__(self, dim):
        self.dim = dim
        self.bounds = None
        self.optimum = None
        self.optimum_location = None
    
    def __call__(self, x):
        """Evaluate function at x."""
        raise NotImplementedError
    
    def get_bounds_array(self):
        """Get bounds as array for each dimension."""
        if isinstance(self.bounds, tuple):
            lb, ub = self.bounds
            return [(lb, ub) for _ in range(self.dim)]
        return self.bounds


class Sphere(BenchmarkFunction):
    """
    Sphere function: the simplest continuous optimization benchmark.
    
    A smooth, convex, unimodal function that represents the sum of squares.
    This is the most basic benchmark function and serves as a baseline for
    algorithm performance. It has no local minima except the global minimum.
    
    Mathematical form:
    f(x) = sum(x^2)
    
    Parameters
    ----------
    dim : int, default=30
        Dimensionality of the problem
    
    Properties
    ----------
    Domain: [-100, 100]^d
    Global minimum: f(0, ..., 0) = 0
    Characteristics: Unimodal, separable, convex, smooth
    """
    
    def __init__(self, dim=30):
        super().__init__(dim)
        self.bounds = (-100, 100)
        self.optimum = 0.0
        self.optimum_location = np.zeros(dim)
    
    def __call__(self, x):
        """Evaluate sphere function."""
        return np.sum(x**2)


class Rastrigin(BenchmarkFunction):
    """
    Rastrigin function: highly multimodal with regular structure.
    
    A highly multimodal function with a large number of regularly distributed
    local minima. Based on the Sphere function with added cosine modulation.
    This function is a common benchmark for testing an algorithm's ability to
    escape local optima and find the global minimum.
    
    Mathematical form:
    f(x) = 10*d + sum(x^2 - 10*cos(2*pi*x))
    
    Parameters
    ----------
    dim : int, default=30
        Dimensionality of the problem
    
    Properties
    ----------
    Domain: [-5.12, 5.12]^d
    Global minimum: f(0, ..., 0) = 0
    Characteristics: Multimodal, separable, regularly structured
    """
    
    def __init__(self, dim=30):
        super().__init__(dim)
        self.bounds = (-5.12, 5.12)
        self.optimum = 0.0
        self.optimum_location = np.zeros(dim)
    
    def __call__(self, x):
        """Evaluate Rastrigin function."""
        return 10*self.dim + np.sum(x**2 - 10*np.cos(2*np.pi*x))


class Rosenbrock(BenchmarkFunction):
    """
    Rosenbrock function: narrow valley leading to the optimum.
    
    Also known as Rosenbrock's banana function due to its curved valley shape.
    The global minimum lies inside a long, narrow, parabolic-shaped flat valley.
    Finding the valley is easy, but converging to the global minimum is difficult.
    This function tests an algorithm's ability to navigate narrow valleys.
    
    Mathematical form:
    f(x) = sum(100*(x[i+1] - x[i]^2)^2 + (1 - x[i])^2)
    
    Parameters
    ----------
    dim : int, default=30
        Dimensionality of the problem
    
    Properties
    ----------
    Domain: [-5, 10]^d
    Global minimum: f(1, ..., 1) = 0
    Characteristics: Unimodal, non-separable, valley-shaped
    """
    
    def __init__(self, dim=30):
        super().__init__(dim)
        self.bounds = (-5, 10)
        self.optimum = 0.0
        self.optimum_location = np.ones(dim)
    
    def __call__(self, x):
        """Evaluate Rosenbrock function."""
        return np.sum(100*(x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)


class Ackley(BenchmarkFunction):
    """
    Ackley function: multimodal with nearly flat outer region.
    
    A widely used multimodal function characterized by an almost flat outer
    region and a large hole at the center. The function has many local minima
    with a single global minimum. The search space is highly multimodal with
    exponential terms that create the characteristic shape.
    
    Mathematical form:
    f(x) = -20*exp(-0.2*sqrt(sum(x^2)/d)) - exp(sum(cos(2*pi*x))/d) + 20 + e
    
    Parameters
    ----------
    dim : int, default=30
        Dimensionality of the problem
    
    Properties
    ----------
    Domain: [-32, 32]^d
    Global minimum: f(0, ..., 0) = 0
    Characteristics: Multimodal, separable, exponential decay
    """
    
    def __init__(self, dim=30):
        super().__init__(dim)
        self.bounds = (-32, 32)
        self.optimum = 0.0
        self.optimum_location = np.zeros(dim)
    
    def __call__(self, x):
        """Evaluate Ackley function."""
        n = len(x)
        sum1 = np.sum(x**2)
        sum2 = np.sum(np.cos(2*np.pi*x))
        return -20*np.exp(-0.2*np.sqrt(sum1/n)) - np.exp(sum2/n) + 20 + np.e


class Griewank(BenchmarkFunction):
    """
    Griewank function: multimodal with product-based interaction.
    
    A multimodal function with many widespread local minima that are regularly
    distributed. The function combines a quadratic term with a product of cosines,
    creating interdependencies between variables. As the search space dimension
    increases, the function becomes more difficult to optimize.
    
    Mathematical form:
    f(x) = sum(x^2)/4000 - prod(cos(x[i]/sqrt(i+1))) + 1
    
    Parameters
    ----------
    dim : int, default=30
        Dimensionality of the problem
    
    Properties
    ----------
    Domain: [-600, 600]^d
    Global minimum: f(0, ..., 0) = 0
    Characteristics: Multimodal, non-separable, product interactions
    """
    
    def __init__(self, dim=30):
        super().__init__(dim)
        self.bounds = (-600, 600)
        self.optimum = 0.0
        self.optimum_location = np.zeros(dim)
    
    def __call__(self, x):
        """Evaluate Griewank function."""
        sum_part = np.sum(x**2) / 4000
        i = np.arange(1, len(x) + 1)
        prod_part = np.prod(np.cos(x / np.sqrt(i)))
        return sum_part - prod_part + 1


class Schwefel(BenchmarkFunction):
    """
    Schwefel function: highly deceptive multimodal function.
    
    A complex multimodal function where the global minimum is geometrically
    distant from the next best local minima. This makes the function highly
    deceptive for search algorithms. The second-best minimum is far from the
    global optimum, and there is a large number of local minima.
    
    Mathematical form:
    f(x) = 418.9829*d - sum(x * sin(sqrt(abs(x))))
    
    Parameters
    ----------
    dim : int, default=30
        Dimensionality of the problem
    
    Properties
    ----------
    Domain: [-500, 500]^d
    Global minimum: f(420.9687, ..., 420.9687) ≈ 0
    Characteristics: Multimodal, separable, highly deceptive
    """
    
    def __init__(self, dim=30):
        super().__init__(dim)
        self.bounds = (-500, 500)
        self.optimum = 0.0
        self.optimum_location = np.full(dim, 420.9687)
    
    def __call__(self, x):
        """Evaluate Schwefel function."""
        return 418.9829*self.dim - np.sum(x * np.sin(np.sqrt(np.abs(x))))


class Levy(BenchmarkFunction):
    """
    Levy function: multimodal with complex landscape.
    
    Named after Levy distribution, this function has a complex multimodal
    landscape with many local minima. It combines multiple sine and squared
    terms creating a challenging optimization problem. The function tests
    an algorithm's ability to handle non-linear interdependencies.
    
    Mathematical form:
    f(x) = sin²(πw₁) + Σ(wᵢ-1)²[1+10sin²(πwᵢ+1)] + (wₐ-1)²[1+sin²(2πwₐ)]
    where w = 1 + (x-1)/4
    
    Parameters
    ----------
    dim : int, default=30
        Dimensionality of the problem
    
    Properties
    ----------
    Domain: [-10, 10]^d
    Global minimum: f(1, ..., 1) = 0
    Characteristics: Multimodal, non-separable, complex landscape
    """
    
    def __init__(self, dim=30):
        super().__init__(dim)
        self.bounds = (-10, 10)
        self.optimum = 0.0
        self.optimum_location = np.ones(dim)
    
    def __call__(self, x):
        """Evaluate Levy function."""
        w = 1 + (x - 1) / 4
        
        term1 = np.sin(np.pi * w[0])**2
        term2 = np.sum((w[:-1] - 1)**2 * (1 + 10*np.sin(np.pi*w[:-1] + 1)**2))
        term3 = (w[-1] - 1)**2 * (1 + np.sin(2*np.pi*w[-1])**2)
        
        return term1 + term2 + term3


class Michalewicz(BenchmarkFunction):
    """
    Michalewicz function: multimodal with steep ridges and valleys.
    
    A multimodal function with d! local minima, characterized by steep
    ridges and valleys. The steepness parameter m controls the "sharpness"
    of the valleys. Larger m values result in more difficult optimization
    with very narrow valleys. This function is particularly challenging
    for gradient-based methods.
    
    Mathematical form:
    f(x) = -sum(sin(x[i]) * sin((i+1)*x[i]^2/pi)^(2*m))
    
    Parameters
    ----------
    dim : int, default=30
        Dimensionality of the problem
    m : int, default=10
        Steepness parameter (higher = steeper valleys)
    
    Properties
    ----------
    Domain: [0, pi]^d
    Global minimum: depends on dimension (approximately -1.8*d for d≤10)
    Characteristics: Multimodal, non-separable, steep valleys
    """
    
    def __init__(self, dim=30, m=10):
        super().__init__(dim)
        self.bounds = (0, np.pi)
        self.m = m
        self.optimum = None  # Depends on dimension
        self.optimum_location = None
    
    def __call__(self, x):
        """Evaluate Michalewicz function."""
        i = np.arange(1, len(x) + 1)
        return -np.sum(np.sin(x) * np.sin(i * x**2 / np.pi)**(2*self.m))


class Zakharov(BenchmarkFunction):
    """
    Zakharov function: unimodal function with plate-shaped surface.
    
    A smooth, unimodal function that combines quadratic and quartic terms.
    The function has a single global minimum at the origin and becomes
    increasingly difficult to optimize as dimensionality increases.
    
    Mathematical form:
    f(x) = sum(x^2) + (sum(0.5*i*x))^2 + (sum(0.5*i*x))^4
    
    Parameters
    ----------
    dim : int, default=30
        Dimensionality of the problem
    
    Properties
    ----------
    Domain: [-5, 10]^d
    Global minimum: f(0, ..., 0) = 0
    Characteristics: Unimodal, smooth, plate-shaped
    """
    
    def __init__(self, dim=30):
        super().__init__(dim)
        self.bounds = (-5, 10)
        self.optimum = 0.0
        self.optimum_location = np.zeros(dim)
    
    def __call__(self, x):
        """Evaluate Zakharov function."""
        i = np.arange(1, len(x) + 1)
        sum1 = np.sum(x**2)
        sum2 = np.sum(0.5 * i * x)
        return sum1 + sum2**2 + sum2**4


class Easom(BenchmarkFunction):
    """
    Easom function: unimodal function with large flat region.
    
    A deceptive function with a single sharp global minimum surrounded by
    a vast flat plateau. This function tests an algorithm's ability to
    navigate flat landscapes and exploit small promising regions.
    
    Mathematical form:
    f(x) = -cos(x1)*cos(x2)*exp(-((x1-pi)^2 + (x2-pi)^2))
    
    Parameters
    ----------
    dim : int, default=2
        Dimensionality (typically 2D)
    
    Properties
    ----------
    Domain: [-100, 100]^d
    Global minimum: f(pi, pi, ..., pi) = -1
    Characteristics: Unimodal, deceptive, large flat region
    """
    
    def __init__(self, dim=2):
        super().__init__(dim)
        self.bounds = (-100, 100)
        self.optimum = -1.0
        self.optimum_location = np.full(dim, np.pi)
    
    def __call__(self, x):
        """Evaluate Easom function."""
        # For 2D: standard Easom
        if len(x) == 2:
            return -np.cos(x[0]) * np.cos(x[1]) * np.exp(-((x[0]-np.pi)**2 + (x[1]-np.pi)**2))
        # For higher dimensions: generalized Easom
        cos_prod = np.prod(np.cos(x))
        exp_term = np.exp(-np.sum((x - np.pi)**2))
        return -cos_prod * exp_term


class StyblinskiTang(BenchmarkFunction):
    """
    Styblinski-Tang function: multimodal with single global minimum.
    
    A relatively simple multimodal function where each variable contributes
    independently to the objective value. Despite having multiple local minima,
    it has a single global minimum that is relatively easy to find.
    
    Mathematical form:
    f(x) = sum(x^4 - 16*x^2 + 5*x) / 2
    
    Parameters
    ----------
    dim : int, default=30
        Dimensionality of the problem
    
    Properties
    ----------
    Domain: [-5, 5]^d
    Global minimum: f(-2.903534, ..., -2.903534) ≈ -39.16599*d
    Characteristics: Multimodal, separable, symmetric
    """
    
    def __init__(self, dim=30):
        super().__init__(dim)
        self.bounds = (-5, 5)
        self.optimum = -39.16599 * dim
        self.optimum_location = np.full(dim, -2.903534)
    
    def __call__(self, x):
        """Evaluate Styblinski-Tang function."""
        return np.sum(x**4 - 16*x**2 + 5*x) / 2


# ============================================================================
# Simple Function Wrappers (for direct usage without classes)
# ============================================================================

def sphere(x):
    """Sphere function: f(x) = sum(x^2). Global minimum: 0 at origin."""
    return np.sum(x**2)


def rastrigin(x):
    """Rastrigin function: highly multimodal. Global minimum: 0 at origin."""
    d = len(x)
    return 10*d + np.sum(x**2 - 10*np.cos(2*np.pi*x))


def rosenbrock(x):
    """Rosenbrock function: valley-shaped. Global minimum: 0 at [1,1,...,1]."""
    return np.sum(100*(x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)


def ackley(x):
    """Ackley function: many local minima. Global minimum: 0 at origin."""
    d = len(x)
    sum1 = np.sum(x**2)
    sum2 = np.sum(np.cos(2*np.pi*x))
    return -20*np.exp(-0.2*np.sqrt(sum1/d)) - np.exp(sum2/d) + 20 + np.e


def griewank(x):
    """Griewank function: multimodal. Global minimum: 0 at origin."""
    sum_part = np.sum(x**2) / 4000
    prod_part = np.prod(np.cos(x / np.sqrt(np.arange(1, len(x)+1))))
    return sum_part - prod_part + 1


def schwefel(x):
    """Schwefel function: deceptive. Global minimum: 0 at x=420.9687."""
    d = len(x)
    return 418.9829*d - np.sum(x * np.sin(np.sqrt(np.abs(x))))


def levy(x):
    """Levy function: multimodal. Global minimum: 0 at [1,1,...,1]."""
    d = len(x)
    w = 1 + (x - 1) / 4
    term1 = np.sin(np.pi*w[0])**2
    term2 = np.sum((w[:-1]-1)**2 * (1 + 10*np.sin(np.pi*w[:-1]+1)**2))
    term3 = (w[-1]-1)**2 * (1 + np.sin(2*np.pi*w[-1])**2)
    return term1 + term2 + term3


def michalewicz(x):
    """Michalewicz function: steep valleys. Global minimum depends on dimension."""
    m = 10
    d = len(x)
    i = np.arange(1, d+1)
    return -np.sum(np.sin(x) * np.sin(i*x**2/np.pi)**(2*m))


def zakharov(x):
    """Zakharov function: unimodal. Global minimum: 0 at origin."""
    d = len(x)
    i = np.arange(1, d+1)
    sum1 = np.sum(x**2)
    sum2 = np.sum(0.5*i*x)
    return sum1 + sum2**2 + sum2**4


def easom(x):
    """Easom function: sharp peak, flat elsewhere. Global minimum: -1 at [pi,pi]."""
    return -np.cos(x[0])*np.cos(x[1])*np.exp(-((x[0]-np.pi)**2 + (x[1]-np.pi)**2))


def styblinskitang(x):
    """Styblinski-Tang function. Global minimum: -39.16599*d at [-2.903534, ...]."""
    return np.sum(x**4 - 16*x**2 + 5*x) / 2


# ============================================================================
# Benchmark Registry (for dynamic access by name)
# ============================================================================

BENCHMARK_REGISTRY = {
    # Class-based (with bounds and metadata)
    'Sphere': Sphere,
    'Rastrigin': Rastrigin,
    'Rosenbrock': Rosenbrock,
    'Ackley': Ackley,
    'Griewank': Griewank,
    'Schwefel': Schwefel,
    'Levy': Levy,
    'Michalewicz': Michalewicz,
    'Zakharov': Zakharov,
    'Easom': Easom,
    'StyblinskiTang': StyblinskiTang,
    
    # Function-based (simple callables)
    'sphere': sphere,
    'rastrigin': rastrigin,
    'rosenbrock': rosenbrock,
    'ackley': ackley,
    'griewank': griewank,
    'schwefel': schwefel,
    'levy': levy,
    'michalewicz': michalewicz,
    'zakharov': zakharov,
    'easom': easom,
    'styblinskitang': styblinskitang,
}


def get_benchmark(name, dim=30):
    """
    Get a benchmark function by name (case-insensitive).
    
    Parameters
    ----------
    name : str
        Name of benchmark function (e.g., 'sphere', 'Rastrigin')
    dim : int, default=30
        Dimension for class-based benchmarks
        
    Returns
    -------
    callable
        Benchmark function (either class instance or simple function)
        
    Examples
    --------
    >>> func = get_benchmark('sphere')
    >>> func = get_benchmark('Rastrigin', dim=20)
    """
    # Try exact match first
    if name in BENCHMARK_REGISTRY:
        item = BENCHMARK_REGISTRY[name]
        if isinstance(item, type):  # It's a class
            return item(dim=dim)
        return item  # It's a function
    
    # Try case-insensitive match
    name_lower = name.lower()
    for key, item in BENCHMARK_REGISTRY.items():
        if key.lower() == name_lower:
            if isinstance(item, type):
                return item(dim=dim)
            return item
    
    raise ValueError(f"Unknown benchmark: {name}. Available: {list(BENCHMARK_REGISTRY.keys())}")


def list_benchmarks():
    """List all available benchmark functions."""
    classes = [k for k, v in BENCHMARK_REGISTRY.items() if isinstance(v, type)]
    functions = [k for k, v in BENCHMARK_REGISTRY.items() if not isinstance(v, type)]
    return {
        'classes': sorted(classes),
        'functions': sorted(functions)
    }
