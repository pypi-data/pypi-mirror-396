"""
Calculus Library
================

A high-performance calculus library for Python with a C++ backend.

Features:
- Numerical differentiation (central differences, Richardson extrapolation)
- Numerical integration (trapezoidal, Simpson's, adaptive quadrature, Romberg)
- Limit computation (one-sided, two-sided, limits at infinity)
- Taylor series expansion and evaluation

Basic Usage
-----------
>>> import calculus
>>> 
>>> # Define a function
>>> f = lambda x: x**2
>>> 
>>> # Compute derivative at x=2: d/dx(x²) = 2x = 4
>>> calculus.derivative(f, 2.0)
4.0
>>> 
>>> # Integrate from 0 to 1: ∫x² dx = 1/3
>>> calculus.integrate(f, 0.0, 1.0)
0.3333333333333333
>>> 
>>> # Compute limit as x → 1 of (x²-1)/(x-1) = 2
>>> g = lambda x: (x**2 - 1) / (x - 1)
>>> calculus.limit(g, 1.0).value
2.0

Modules
-------
All functions are available directly from the calculus namespace.

Differentiation:
    derivative, first_derivative, second_derivative, nth_derivative,
    forward_difference, backward_difference, derivative_richardson

Integration:
    integrate, quad, trapezoidal, simpson, romberg, gauss_legendre

Limits:
    limit, limit_inf, limit_value, Direction, LimitResult

Series:
    taylor, maclaurin, taylor_eval, taylor_eval_with_coeffs,
    taylor_error, taylor_series, radius_of_convergence, PowerSeries
"""

__version__ = "1.0.0"
__author__ = "Aditya Palit"

# Import all functions from the C++ extension module
from ._calculus_core import (
    # Differentiation
    derivative,
    first_derivative,
    second_derivative,
    nth_derivative,
    forward_difference,
    backward_difference,
    derivative_richardson,
    
    # Integration
    integrate,
    quad,
    trapezoidal,
    simpson,
    romberg,
    gauss_legendre,
    
    # Limits
    limit,
    limit_inf,
    limit_value,
    Direction,
    LimitResult,
    
    # Series
    taylor,
    maclaurin,
    taylor_eval,
    taylor_eval_with_coeffs,
    taylor_error,
    taylor_series,
    radius_of_convergence,
    PowerSeries,
)

# Define what's exported with "from calculus import *"
__all__ = [
    # Version
    "__version__",
    
    # Differentiation
    "derivative",
    "first_derivative",
    "second_derivative",
    "nth_derivative",
    "forward_difference",
    "backward_difference",
    "derivative_richardson",
    
    # Integration
    "integrate",
    "quad",
    "trapezoidal",
    "simpson",
    "romberg",
    "gauss_legendre",
    
    # Limits
    "limit",
    "limit_inf",
    "limit_value",
    "Direction",
    "LimitResult",
    
    # Series
    "taylor",
    "maclaurin",
    "taylor_eval",
    "taylor_eval_with_coeffs",
    "taylor_error",
    "taylor_series",
    "radius_of_convergence",
    "PowerSeries",
]


def gradient(f, point, h=1e-6):
    """
    Compute the gradient of a multivariable function at a point.
    
    Parameters
    ----------
    f : callable
        Function taking a list/tuple of coordinates and returning a scalar.
    point : list or tuple
        The point at which to compute the gradient.
    h : float, optional
        Step size for finite differences (default: 1e-6).
    
    Returns
    -------
    list
        The gradient vector [∂f/∂x₁, ∂f/∂x₂, ...].
    
    Examples
    --------
    >>> import calculus
    >>> f = lambda p: p[0]**2 + p[1]**2  # f(x,y) = x² + y²
    >>> calculus.gradient(f, [1.0, 2.0])  # [2x, 2y] = [2, 4]
    [2.0, 4.0]
    """
    point = list(point)
    n = len(point)
    grad = []
    
    for i in range(n):
        # Compute partial derivative with respect to x_i
        def partial_func(xi, idx=i):
            p = point.copy()
            p[idx] = xi
            return f(p)
        
        grad.append(derivative(partial_func, point[i], n=1, h=h))
    
    return grad


def jacobian(f, point, h=1e-6):
    """
    Compute the Jacobian matrix of a vector-valued function.
    
    Parameters
    ----------
    f : callable
        Function taking a list of n coordinates and returning a list of m values.
    point : list or tuple
        The point at which to compute the Jacobian.
    h : float, optional
        Step size for finite differences (default: 1e-6).
    
    Returns
    -------
    list of lists
        The m×n Jacobian matrix where J[i][j] = ∂fᵢ/∂xⱼ.
    """
    point = list(point)
    n = len(point)
    f0 = f(point)
    m = len(f0)
    
    jacobian_matrix = [[0.0] * n for _ in range(m)]
    
    for j in range(n):
        # Compute partial derivatives with respect to x_j
        point_plus = point.copy()
        point_minus = point.copy()
        point_plus[j] += h
        point_minus[j] -= h
        
        f_plus = f(point_plus)
        f_minus = f(point_minus)
        
        for i in range(m):
            jacobian_matrix[i][j] = (f_plus[i] - f_minus[i]) / (2 * h)
    
    return jacobian_matrix


def hessian(f, point, h=1e-4):
    """
    Compute the Hessian matrix of a scalar function.
    
    Parameters
    ----------
    f : callable
        Function taking a list of n coordinates and returning a scalar.
    point : list or tuple
        The point at which to compute the Hessian.
    h : float, optional
        Step size for finite differences (default: 1e-4).
    
    Returns
    -------
    list of lists
        The n×n Hessian matrix where H[i][j] = ∂²f/(∂xᵢ∂xⱼ).
    """
    point = list(point)
    n = len(point)
    
    hessian_matrix = [[0.0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if i == j:
                # Diagonal: ∂²f/∂xᵢ²
                p_plus = point.copy()
                p_minus = point.copy()
                p_plus[i] += h
                p_minus[i] -= h
                
                hessian_matrix[i][j] = (f(p_plus) - 2*f(point) + f(p_minus)) / (h * h)
            else:
                # Off-diagonal: ∂²f/(∂xᵢ∂xⱼ)
                p_pp = point.copy()
                p_pm = point.copy()
                p_mp = point.copy()
                p_mm = point.copy()
                
                p_pp[i] += h; p_pp[j] += h
                p_pm[i] += h; p_pm[j] -= h
                p_mp[i] -= h; p_mp[j] += h
                p_mm[i] -= h; p_mm[j] -= h
                
                hessian_matrix[i][j] = (f(p_pp) - f(p_pm) - f(p_mp) + f(p_mm)) / (4 * h * h)
    
    return hessian_matrix


# Add to __all__
__all__.extend(["gradient", "jacobian", "hessian"])

