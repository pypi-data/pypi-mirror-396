# Calculus Library

A high-performance calculus library for Python with a C++ backend. Provides numerical methods for differentiation, integration, limits, and Taylor series expansion.

## Features

- **Differentiation**: Central differences, forward/backward differences, Richardson extrapolation
- **Integration**: Trapezoidal rule, Simpson's rule, adaptive quadrature, Romberg, Gauss-Legendre
- **Limits**: One-sided limits, two-sided limits, limits at infinity
- **Series**: Taylor/Maclaurin series expansion and evaluation
- **Multivariable**: Gradient, Jacobian, Hessian (Python-level)

## Installation

### From source

```bash
# Clone the repository
git clone https://github.com/username/calculus.git
cd calculus

# Install with pip
pip install .
```

### Development installation

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
import calculus
import math

# Define a function
f = lambda x: x**2

# Compute the derivative at x=2: d/dx(x²) = 2x = 4
print(calculus.derivative(f, 2.0))  # Output: 4.0

# Compute the integral from 0 to 1: ∫x² dx = 1/3
print(calculus.integrate(f, 0.0, 1.0))  # Output: 0.333...

# Compute a limit
g = lambda x: (x**2 - 1) / (x - 1)  # = x + 1 for x ≠ 1
result = calculus.limit(g, 1.0)
print(result.value)  # Output: 2.0

# Taylor series of sin(x) around 0
coeffs = calculus.taylor(math.sin, 0.0, n=5)
print(coeffs)  # [0, 1, 0, -0.166..., 0]
```

## API Reference

### Differentiation

```python
# First derivative (central difference)
calculus.derivative(f, x, n=1, h=1e-6)

# Specific methods
calculus.first_derivative(f, x, h=1e-6)
calculus.second_derivative(f, x, h=1e-4)
calculus.nth_derivative(f, x, n, h=1e-3)
calculus.forward_difference(f, x, h=1e-6)
calculus.backward_difference(f, x, h=1e-6)
calculus.derivative_richardson(f, x, h=1e-4)  # Higher accuracy
```

### Integration

```python
# General integration (supports multiple methods)
calculus.integrate(f, a, b, method='simpson', n=1000)
# Methods: 'simpson', 'trapezoidal', 'simpson38', 'gauss', 'romberg'

# Adaptive quadrature (automatic error control)
calculus.quad(f, a, b, tol=1e-8, max_depth=50)

# Specific methods
calculus.trapezoidal(f, a, b, n=1000)
calculus.simpson(f, a, b, n=1000)
calculus.romberg(f, a, b, max_iter=20, tol=1e-10)
calculus.gauss_legendre(f, a, b, n=100)
```

### Limits

```python
# Compute limit (returns LimitResult object)
result = calculus.limit(f, x, direction='both', tol=1e-10)
# direction: 'both', 'left'/'-', 'right'/'+'

# Access result
result.value       # The limit value
result.exists      # Whether limit exists
result.is_finite   # Whether limit is finite
result.confidence  # Confidence estimate (0-1)

# Limit at infinity
result = calculus.limit_inf(f, direction='positive', tol=1e-8)
# direction: 'positive'/'+', 'negative'/'-'

# Get just the value (raises exception if limit doesn't exist)
value = calculus.limit_value(f, x)
```

### Series

```python
# Taylor coefficients
coeffs = calculus.taylor(f, a, n=10, h=1e-3)

# Maclaurin coefficients (Taylor at x=0)
coeffs = calculus.maclaurin(f, n=10, h=1e-3)

# Evaluate Taylor approximation
approx = calculus.taylor_eval(f, a, x, n=10, h=1e-3)

# With pre-computed coefficients
approx = calculus.taylor_eval_with_coeffs(coeffs, a, x)

# Error estimate
error = calculus.taylor_error(f, a, x, n=10, h=1e-3)

# Create callable PowerSeries object
series = calculus.taylor_series(f, a, n=10)
value = series(x)  # Evaluate at x

# Estimate radius of convergence
r = calculus.radius_of_convergence(coeffs)
```

### Multivariable Calculus

```python
# Gradient
f = lambda p: p[0]**2 + p[1]**2
grad = calculus.gradient(f, [1.0, 2.0])  # [2.0, 4.0]

# Jacobian matrix
f = lambda p: [p[0]*p[1], p[0]+p[1]]
J = calculus.jacobian(f, [2.0, 3.0])

# Hessian matrix
f = lambda p: p[0]**2 * p[1] + p[1]**3
H = calculus.hessian(f, [1.0, 1.0])
```

## Examples

### Finding Critical Points

```python
import calculus

# f(x) = x³ - 3x
f = lambda x: x**3 - 3*x
df = lambda x: calculus.derivative(f, x)

# Critical points where f'(x) = 0
# f'(x) = 3x² - 3 = 0 → x = ±1

# Second derivative test
print(calculus.derivative(f, 1.0, n=2))   # -6 < 0: local max
print(calculus.derivative(f, -1.0, n=2))  # 6 > 0: local min
```

### Computing Arc Length

```python
import calculus
import math

# Arc length of y = sin(x) from 0 to π
# L = ∫√(1 + (dy/dx)²) dx

def arc_length_integrand(x):
    dydx = calculus.derivative(math.sin, x)
    return math.sqrt(1 + dydx**2)

length = calculus.integrate(arc_length_integrand, 0.0, math.pi)
print(f"Arc length: {length}")
```

### Numerical Solution of ODEs (Euler Method)

```python
import calculus

def euler_solve(f, y0, t0, t1, n=1000):
    """Solve dy/dt = f(t, y) with y(t0) = y0"""
    h = (t1 - t0) / n
    t, y = t0, y0
    for _ in range(n):
        y += h * f(t, y)
        t += h
    return y

# Solve dy/dt = y, y(0) = 1 → y = e^t
f = lambda t, y: y
result = euler_solve(f, 1.0, 0.0, 1.0)
print(f"y(1) ≈ {result}, e¹ = {math.e}")
```

## Testing

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests
pytest tests/ -v
```

## Building from Source

Requirements:
- C++17 compatible compiler
- CMake 3.15+
- Python 3.8+

```bash
# Build and install
pip install .

# Or build in place for development
pip install -e .
```

## Performance

The library uses C++ for core numerical computations, providing significant speedups over pure Python implementations. Benchmarks show 10-100x improvements for integration and differentiation operations.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

