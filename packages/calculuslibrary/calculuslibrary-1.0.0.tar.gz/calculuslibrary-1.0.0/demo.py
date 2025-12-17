#!/usr/bin/env python3
"""
Calculus Library Demo
=====================
A comprehensive demonstration of the calculus library's capabilities.
"""

import math
import calculus

def print_header(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_subheader(title):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")

# ============================================================================
#  DIFFERENTIATION
# ============================================================================
print_header("DIFFERENTIATION")

print_subheader("First Derivatives")

# Polynomial: f(x) = x³ → f'(x) = 3x²
f = lambda x: x**3
x = 2.0
result = calculus.derivative(f, x)
print(f"f(x) = x³")
print(f"f'({x}) = {result:.6f}  (exact: {3*x**2})")

# Trigonometric: f(x) = sin(x) → f'(x) = cos(x)
f = math.sin
x = math.pi / 4
result = calculus.derivative(f, x)
print(f"\nf(x) = sin(x)")
print(f"f'(π/4) = {result:.6f}  (exact: {math.cos(x):.6f})")

# Exponential: f(x) = e^x → f'(x) = e^x
f = math.exp
x = 1.0
result = calculus.derivative(f, x)
print(f"\nf(x) = eˣ")
print(f"f'(1) = {result:.6f}  (exact: {math.e:.6f})")

print_subheader("Higher Order Derivatives")

# f(x) = x⁴ → f''(x) = 12x²
f = lambda x: x**4
x = 2.0
d1 = calculus.derivative(f, x, n=1)
d2 = calculus.derivative(f, x, n=2)
d3 = calculus.derivative(f, x, n=3)
d4 = calculus.derivative(f, x, n=4)
print(f"f(x) = x⁴ at x = {x}")
print(f"  f'(x)   = {d1:.4f}  (exact: {4*x**3})")
print(f"  f''(x)  = {d2:.4f}  (exact: {12*x**2})")
print(f"  f'''(x) = {d3:.4f}  (exact: {24*x})")
print(f"  f''''(x)= {d4:.4f}  (exact: 24)")

print_subheader("Richardson Extrapolation (Higher Accuracy)")

f = lambda x: math.log(x)  # f'(x) = 1/x
x = 2.0
standard = calculus.derivative(f, x)
richardson = calculus.derivative_richardson(f, x)
exact = 1/x
print(f"f(x) = ln(x), f'({x})")
print(f"  Standard:   {standard:.10f}")
print(f"  Richardson: {richardson:.10f}")
print(f"  Exact:      {exact:.10f}")
print(f"  Error (standard):   {abs(standard - exact):.2e}")
print(f"  Error (Richardson): {abs(richardson - exact):.2e}")

# ============================================================================
#  INTEGRATION
# ============================================================================
print_header("INTEGRATION")

print_subheader("Basic Integration")

# ∫x² dx from 0 to 3 = x³/3 |₀³ = 9
f = lambda x: x**2
a, b = 0.0, 3.0
result = calculus.integrate(f, a, b)
exact = 9.0
print(f"∫x² dx from {a} to {b}")
print(f"  Result: {result:.10f}")
print(f"  Exact:  {exact}")

# ∫sin(x) dx from 0 to π = 2
f = math.sin
a, b = 0.0, math.pi
result = calculus.integrate(f, a, b)
exact = 2.0
print(f"\n∫sin(x) dx from 0 to π")
print(f"  Result: {result:.10f}")
print(f"  Exact:  {exact}")

print_subheader("Comparing Integration Methods")

f = lambda x: math.exp(-x**2)  # Gaussian - no closed form
a, b = 0.0, 1.0
print(f"∫e^(-x²) dx from {a} to {b}  (Gaussian integral)")

methods = ['trapezoidal', 'simpson', 'gauss', 'romberg']
for method in methods:
    result = calculus.integrate(f, a, b, method=method)
    print(f"  {method:12s}: {result:.10f}")

# Adaptive quadrature
result = calculus.quad(f, a, b, tol=1e-12)
print(f"  {'adaptive':12s}: {result:.10f}")

print_subheader("High-Precision with Romberg")

# ∫1/(1+x²) dx from 0 to 1 = arctan(1) = π/4
f = lambda x: 1 / (1 + x**2)
a, b = 0.0, 1.0
result = calculus.romberg(f, a, b, max_iter=20, tol=1e-14)
exact = math.pi / 4
print(f"∫1/(1+x²) dx from 0 to 1 = arctan(1) = π/4")
print(f"  Result: {result:.15f}")
print(f"  Exact:  {exact:.15f}")
print(f"  Error:  {abs(result - exact):.2e}")

# ============================================================================
#  LIMITS
# ============================================================================
print_header("LIMITS")

print_subheader("Finite Limits")

# lim(x→0) sin(x)/x = 1
f = lambda x: math.sin(x) / x
result = calculus.limit(f, 0.0)
print(f"lim(x→0) sin(x)/x")
print(f"  Value: {result.value:.10f}")
print(f"  Exists: {result.exists}, Finite: {result.is_finite}")

# lim(x→1) (x²-1)/(x-1) = 2  (removable discontinuity)
f = lambda x: (x**2 - 1) / (x - 1)
result = calculus.limit(f, 1.0)
print(f"\nlim(x→1) (x²-1)/(x-1)  [= x+1 for x≠1]")
print(f"  Value: {result.value:.10f}")

# lim(x→0) (e^x - 1)/x = 1
f = lambda x: (math.exp(x) - 1) / x
result = calculus.limit(f, 0.0)
print(f"\nlim(x→0) (eˣ-1)/x")
print(f"  Value: {result.value:.10f}")

print_subheader("One-Sided Limits")

# |x|/x has different left and right limits at x=0
f = lambda x: abs(x) / x
left = calculus.limit(f, 0.0, direction='left')
right = calculus.limit(f, 0.0, direction='right')
print(f"lim(x→0) |x|/x")
print(f"  Left limit (x→0⁻):  {left.value:.1f}")
print(f"  Right limit (x→0⁺): {right.value:.1f}")

print_subheader("Limits at Infinity")

# lim(x→∞) 1/x = 0
f = lambda x: 1/x
result = calculus.limit_inf(f, direction='positive')
print(f"lim(x→+∞) 1/x = {result.value:.10f}")

# lim(x→∞) (2x+1)/(x+3) = 2
f = lambda x: (2*x + 1) / (x + 3)
result = calculus.limit_inf(f)
print(f"lim(x→+∞) (2x+1)/(x+3) = {result.value:.10f}")

# lim(x→-∞) e^x = 0
f = math.exp
result = calculus.limit_inf(f, direction='negative')
print(f"lim(x→-∞) eˣ = {result.value:.10f}")

# ============================================================================
#  TAYLOR SERIES
# ============================================================================
print_header("TAYLOR SERIES")

print_subheader("Taylor Coefficients")

# e^x Maclaurin series: 1 + x + x²/2! + x³/3! + ...
coeffs = calculus.maclaurin(math.exp, n=6)
print("Maclaurin series for eˣ:")
print(f"  Coefficients: {[f'{c:.4f}' for c in coeffs]}")
print(f"  Expected:     [1, 1, 1/2, 1/6, 1/24, 1/120]")
print(f"                [{1:.4f}, {1:.4f}, {1/2:.4f}, {1/6:.4f}, {1/24:.4f}, {1/120:.4f}]")

# sin(x) Maclaurin: x - x³/3! + x⁵/5! - ...
coeffs = calculus.maclaurin(math.sin, n=7)
print(f"\nMaclaurin series for sin(x):")
print(f"  Coefficients: {[f'{c:.5f}' for c in coeffs]}")
print(f"  Expected:     [0, 1, 0, -1/6, 0, 1/120, 0]")

print_subheader("Taylor Polynomial Approximation")

# Approximate sin(0.5) using Taylor polynomial
f = math.sin
a = 0.0  # Expand around x=0
x = 0.5  # Evaluate at x=0.5

print(f"Approximating sin({x}) using Taylor polynomials centered at {a}:")
for n in [3, 5, 7, 9]:
    approx = calculus.taylor_eval(f, a, x, n=n)
    error = abs(approx - math.sin(x))
    print(f"  n={n}: {approx:.10f}  (error: {error:.2e})")
print(f"  Exact: {math.sin(x):.10f}")

print_subheader("Power Series Object")

# Create a reusable power series for cos(x)
series = calculus.taylor_series(math.cos, 0.0, n=12)
print(f"Power series for cos(x): {series}")
print(f"\nEvaluating at various points:")
for x in [0, 0.5, 1.0, math.pi/4]:
    approx = series(x)
    exact = math.cos(x)
    print(f"  cos({x:.4f}) ≈ {approx:.8f}  (exact: {exact:.8f})")

# ============================================================================
#  MULTIVARIABLE CALCULUS
# ============================================================================
print_header("MULTIVARIABLE CALCULUS")

print_subheader("Gradient")

# f(x,y) = x² + y² → ∇f = [2x, 2y]
f = lambda p: p[0]**2 + p[1]**2
point = [3.0, 4.0]
grad = calculus.gradient(f, point)
print(f"f(x,y) = x² + y²")
print(f"∇f({point[0]}, {point[1]}) = {[f'{g:.4f}' for g in grad]}")
print(f"Expected: [2*{point[0]}, 2*{point[1]}] = [{2*point[0]}, {2*point[1]}]")

# f(x,y,z) = x*y*z → ∇f = [yz, xz, xy]
f = lambda p: p[0] * p[1] * p[2]
point = [1.0, 2.0, 3.0]
grad = calculus.gradient(f, point)
print(f"\nf(x,y,z) = xyz")
print(f"∇f({point}) = {[f'{g:.4f}' for g in grad]}")
print(f"Expected: [yz, xz, xy] = [{point[1]*point[2]}, {point[0]*point[2]}, {point[0]*point[1]}]")

print_subheader("Jacobian Matrix")

# F(x,y) = [x*y, x+y] → J = [[y, x], [1, 1]]
f = lambda p: [p[0] * p[1], p[0] + p[1]]
point = [2.0, 3.0]
J = calculus.jacobian(f, point)
print(f"F(x,y) = [xy, x+y]")
print(f"Jacobian at ({point[0]}, {point[1]}):")
for row in J:
    print(f"  [{row[0]:.4f}, {row[1]:.4f}]")
print(f"Expected: [[y, x], [1, 1]] = [[{point[1]}, {point[0]}], [1, 1]]")

print_subheader("Hessian Matrix")

# f(x,y) = x³ + y³ + x*y → H = [[6x, 1], [1, 6y]]
f = lambda p: p[0]**3 + p[1]**3 + p[0]*p[1]
point = [1.0, 2.0]
H = calculus.hessian(f, point)
print(f"f(x,y) = x³ + y³ + xy")
print(f"Hessian at ({point[0]}, {point[1]}):")
for row in H:
    print(f"  [{row[0]:.4f}, {row[1]:.4f}]")
print(f"Expected: [[6x, 1], [1, 6y]] = [[{6*point[0]}, 1], [1, {6*point[1]}]]")

# ============================================================================
#  PRACTICAL EXAMPLE: Finding Critical Points
# ============================================================================
print_header("PRACTICAL EXAMPLE: Critical Point Analysis")

# f(x) = x³ - 3x + 1
f = lambda x: x**3 - 3*x + 1
print("f(x) = x³ - 3x + 1")
print("\nFinding where f'(x) = 0:")

# The derivative is f'(x) = 3x² - 3 = 0 → x = ±1
for x in [-1.0, 1.0]:
    f_val = f(x)
    f_prime = calculus.derivative(f, x)
    f_double_prime = calculus.derivative(f, x, n=2)
    
    if f_double_prime > 0:
        nature = "local minimum"
    elif f_double_prime < 0:
        nature = "local maximum"
    else:
        nature = "inflection point"
    
    print(f"\nAt x = {x}:")
    print(f"  f(x)   = {f_val:.4f}")
    print(f"  f'(x)  = {f_prime:.6f} (≈ 0, critical point)")
    print(f"  f''(x) = {f_double_prime:.4f}")
    print(f"  Nature: {nature}")

# ============================================================================
#  PRACTICAL EXAMPLE: Arc Length Calculation  
# ============================================================================
print_header("PRACTICAL EXAMPLE: Arc Length")

# Arc length of y = sin(x) from 0 to π
# L = ∫√(1 + (dy/dx)²) dx
print("Computing arc length of y = sin(x) from 0 to π")
print("Formula: L = ∫√(1 + cos²(x)) dx")

def arc_length_integrand(x):
    dydx = math.cos(x)  # derivative of sin(x)
    return math.sqrt(1 + dydx**2)

length = calculus.integrate(arc_length_integrand, 0, math.pi, method='romberg')
print(f"\nArc length: {length:.10f}")

# Compare with more points for accuracy
length_adaptive = calculus.quad(arc_length_integrand, 0, math.pi, tol=1e-10)
print(f"Arc length (adaptive): {length_adaptive:.10f}")

# ============================================================================
print_header("DEMO COMPLETE")
print("\nThe calculus library provides high-performance numerical methods")
print("for differentiation, integration, limits, and series expansion.")
print("All core algorithms are implemented in C++ for speed.")

