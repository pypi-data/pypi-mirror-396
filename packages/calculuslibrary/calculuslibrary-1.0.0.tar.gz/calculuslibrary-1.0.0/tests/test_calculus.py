"""
Comprehensive test suite for the Calculus Library.

Run with: pytest tests/test_calculus.py -v
"""

import math
import pytest


class TestDifferentiation:
    """Tests for differentiation functions."""

    def test_first_derivative_polynomial(self):
        """Test derivative of x² at various points."""
        import calculus
        
        f = lambda x: x**2
        
        # d/dx(x²) = 2x
        assert abs(calculus.derivative(f, 0.0) - 0.0) < 1e-6
        assert abs(calculus.derivative(f, 1.0) - 2.0) < 1e-6
        assert abs(calculus.derivative(f, 2.0) - 4.0) < 1e-6
        assert abs(calculus.derivative(f, -3.0) - (-6.0)) < 1e-6

    def test_first_derivative_trig(self):
        """Test derivative of sin(x)."""
        import calculus
        
        f = math.sin
        
        # d/dx(sin(x)) = cos(x)
        for x in [0.0, 0.5, 1.0, math.pi/4, math.pi/2]:
            expected = math.cos(x)
            result = calculus.derivative(f, x)
            assert abs(result - expected) < 1e-5, f"At x={x}: {result} != {expected}"

    def test_second_derivative(self):
        """Test second derivative computation."""
        import calculus
        
        f = lambda x: x**3  # d²/dx²(x³) = 6x
        
        assert abs(calculus.derivative(f, 1.0, n=2) - 6.0) < 1e-3
        assert abs(calculus.derivative(f, 2.0, n=2) - 12.0) < 1e-2  # Slightly relaxed for numerical stability

    def test_nth_derivative(self):
        """Test higher order derivatives."""
        import calculus
        
        f = math.exp  # All derivatives of e^x are e^x
        
        for n in range(1, 5):
            for x in [0.0, 0.5, 1.0]:
                expected = math.exp(x)
                result = calculus.derivative(f, x, n=n, h=1e-2)
                # Tolerance increases with n
                assert abs(result - expected) < 0.1 * n, f"n={n}, x={x}"

    def test_forward_backward_difference(self):
        """Test forward and backward difference methods."""
        import calculus
        
        f = lambda x: x**2
        x = 2.0
        expected = 4.0
        
        # These are less accurate but should still be close
        assert abs(calculus.forward_difference(f, x) - expected) < 1e-5
        assert abs(calculus.backward_difference(f, x) - expected) < 1e-5

    def test_richardson_extrapolation(self):
        """Test Richardson extrapolation for improved accuracy."""
        import calculus
        
        f = lambda x: math.sin(x)
        x = 1.0
        expected = math.cos(x)
        
        result = calculus.derivative_richardson(f, x)
        assert abs(result - expected) < 1e-8


class TestIntegration:
    """Tests for integration functions."""

    def test_integrate_polynomial(self):
        """Test integration of x² from 0 to 1."""
        import calculus
        
        f = lambda x: x**2
        expected = 1.0 / 3.0  # ∫₀¹ x² dx = 1/3
        
        result = calculus.integrate(f, 0.0, 1.0)
        assert abs(result - expected) < 1e-6

    def test_integrate_methods(self):
        """Test different integration methods give similar results."""
        import calculus
        
        f = lambda x: math.exp(-x**2)  # Gaussian
        a, b = 0.0, 1.0
        
        methods = ['simpson', 'trapezoidal', 'gauss', 'romberg']
        results = [calculus.integrate(f, a, b, method=m) for m in methods]
        
        # All methods should give similar results
        for i, r1 in enumerate(results):
            for j, r2 in enumerate(results):
                if i != j:
                    assert abs(r1 - r2) < 1e-4, f"{methods[i]} vs {methods[j]}"

    def test_quad_adaptive(self):
        """Test adaptive quadrature."""
        import calculus
        
        f = lambda x: x**2
        expected = 1.0 / 3.0
        
        result = calculus.quad(f, 0.0, 1.0)
        assert abs(result - expected) < 1e-8

    def test_integrate_trig(self):
        """Test integration of sin(x) from 0 to π."""
        import calculus
        
        f = math.sin
        expected = 2.0  # ∫₀^π sin(x) dx = 2
        
        result = calculus.integrate(f, 0.0, math.pi)
        assert abs(result - expected) < 1e-6

    def test_romberg_high_accuracy(self):
        """Test Romberg integration for high accuracy."""
        import calculus
        
        f = lambda x: 4.0 / (1.0 + x**2)  # ∫₀¹ = π
        expected = math.pi
        
        result = calculus.romberg(f, 0.0, 1.0)
        assert abs(result - expected) < 1e-9

    def test_gauss_legendre(self):
        """Test Gauss-Legendre quadrature."""
        import calculus
        
        f = lambda x: x**5 - 3*x**3 + 2*x
        # ∫₋₁¹ (x⁵ - 3x³ + 2x) dx = 0 (odd function)
        
        result = calculus.gauss_legendre(f, -1.0, 1.0)
        assert abs(result) < 1e-10


class TestLimits:
    """Tests for limit computation."""

    def test_limit_polynomial(self):
        """Test limit of polynomial function."""
        import calculus
        
        f = lambda x: x**2 + 2*x + 1
        
        result = calculus.limit(f, 2.0)
        expected = 9.0  # f(2) = 4 + 4 + 1 = 9
        
        assert result.exists
        assert abs(result.value - expected) < 1e-6

    def test_limit_removable_discontinuity(self):
        """Test limit at removable discontinuity."""
        import calculus
        
        # f(x) = (x² - 1)/(x - 1) = x + 1 for x ≠ 1
        f = lambda x: (x**2 - 1) / (x - 1)
        
        result = calculus.limit(f, 1.0)
        expected = 2.0
        
        assert result.exists
        assert abs(result.value - expected) < 1e-4

    def test_one_sided_limits(self):
        """Test one-sided limits."""
        import calculus
        
        f = lambda x: x**2
        
        left = calculus.limit(f, 2.0, direction='left')
        right = calculus.limit(f, 2.0, direction='right')
        
        assert left.exists and right.exists
        assert abs(left.value - 4.0) < 1e-6
        assert abs(right.value - 4.0) < 1e-6

    def test_limit_at_infinity(self):
        """Test limit as x → ∞."""
        import calculus
        
        f = lambda x: 1.0 / x
        
        result = calculus.limit_inf(f)
        
        assert result.exists
        assert result.is_finite
        assert abs(result.value) < 1e-6

    def test_limit_negative_infinity(self):
        """Test limit as x → -∞."""
        import calculus
        
        f = lambda x: 1.0 / x
        
        result = calculus.limit_inf(f, direction='negative')
        
        assert result.exists
        assert abs(result.value) < 1e-6

    def test_limit_value_function(self):
        """Test simplified limit_value function."""
        import calculus
        
        f = lambda x: x**2
        
        result = calculus.limit_value(f, 3.0)
        assert abs(result - 9.0) < 1e-6


class TestSeries:
    """Tests for Taylor series functions."""

    def test_taylor_exponential(self):
        """Test Taylor series of e^x around x=0."""
        import calculus
        
        f = math.exp
        coeffs = calculus.taylor(f, 0.0, n=6)
        
        # e^x = 1 + x + x²/2! + x³/3! + ...
        expected = [1.0, 1.0, 0.5, 1/6, 1/24, 1/120]
        
        for i, (c, e) in enumerate(zip(coeffs, expected)):
            assert abs(c - e) < 0.01, f"Coefficient {i}: {c} != {e}"

    def test_maclaurin_sin(self):
        """Test Maclaurin series of sin(x)."""
        import calculus
        
        f = math.sin
        coeffs = calculus.maclaurin(f, n=7)
        
        # sin(x) = x - x³/3! + x⁵/5! - ...
        # coeffs = [0, 1, 0, -1/6, 0, 1/120, 0]
        assert abs(coeffs[0]) < 1e-3  # sin(0) = 0
        assert abs(coeffs[1] - 1.0) < 0.01  # cos(0) = 1
        assert abs(coeffs[2]) < 0.01  # -sin(0) = 0

    def test_taylor_eval(self):
        """Test Taylor polynomial evaluation."""
        import calculus
        
        f = math.exp
        x = 0.5
        
        approx = calculus.taylor_eval(f, 0.0, x, n=10)
        actual = math.exp(x)
        
        assert abs(approx - actual) < 1e-5

    def test_taylor_eval_with_coeffs(self):
        """Test evaluation with pre-computed coefficients."""
        import calculus
        
        f = lambda x: x**3 + 2*x**2 - x + 5
        coeffs = calculus.taylor(f, 0.0, n=5)
        
        for x in [0.0, 0.5, 1.0, -0.5]:
            approx = calculus.taylor_eval_with_coeffs(coeffs, 0.0, x)
            actual = f(x)
            assert abs(approx - actual) < 1e-3

    def test_taylor_series_object(self):
        """Test PowerSeries object."""
        import calculus
        
        f = math.cos
        series = calculus.taylor_series(f, 0.0, n=10)
        
        assert series.center == 0.0
        assert len(series.coefficients) == 10
        
        # Test calling the series
        for x in [0.0, 0.1, 0.2]:
            approx = series(x)
            actual = math.cos(x)
            assert abs(approx - actual) < 1e-4


class TestMultivariable:
    """Tests for multivariable calculus functions (Python-level)."""

    def test_gradient(self):
        """Test gradient computation."""
        import calculus
        
        # f(x, y) = x² + y²
        f = lambda p: p[0]**2 + p[1]**2
        
        grad = calculus.gradient(f, [1.0, 2.0])
        # ∇f = [2x, 2y] = [2, 4]
        
        assert abs(grad[0] - 2.0) < 1e-5
        assert abs(grad[1] - 4.0) < 1e-5

    def test_gradient_3d(self):
        """Test gradient in 3D."""
        import calculus
        
        # f(x, y, z) = x*y + y*z + x*z
        f = lambda p: p[0]*p[1] + p[1]*p[2] + p[0]*p[2]
        
        grad = calculus.gradient(f, [1.0, 2.0, 3.0])
        # ∇f = [y+z, x+z, y+x] = [5, 4, 3]
        
        assert abs(grad[0] - 5.0) < 1e-5
        assert abs(grad[1] - 4.0) < 1e-5
        assert abs(grad[2] - 3.0) < 1e-5

    def test_hessian(self):
        """Test Hessian matrix computation."""
        import calculus
        
        # f(x, y) = x²y + y³
        f = lambda p: p[0]**2 * p[1] + p[1]**3
        
        H = calculus.hessian(f, [1.0, 1.0])
        
        # H = [[2y, 2x], [2x, 6y]] at (1,1) = [[2, 2], [2, 6]]
        assert abs(H[0][0] - 2.0) < 0.1
        assert abs(H[0][1] - 2.0) < 0.1
        assert abs(H[1][0] - 2.0) < 0.1
        assert abs(H[1][1] - 6.0) < 0.1

    def test_jacobian(self):
        """Test Jacobian matrix computation."""
        import calculus
        
        # f(x, y) = [x*y, x+y]
        f = lambda p: [p[0]*p[1], p[0]+p[1]]
        
        J = calculus.jacobian(f, [2.0, 3.0])
        
        # J = [[y, x], [1, 1]] at (2,3) = [[3, 2], [1, 1]]
        assert abs(J[0][0] - 3.0) < 1e-5
        assert abs(J[0][1] - 2.0) < 1e-5
        assert abs(J[1][0] - 1.0) < 1e-5
        assert abs(J[1][1] - 1.0) < 1e-5


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_derivative_step_size(self):
        """Test that step size affects accuracy."""
        import calculus
        
        f = lambda x: x**3
        x = 2.0
        expected = 12.0  # 3x² = 12
        
        # Smaller step size should be more accurate (up to a point)
        result_large = calculus.derivative(f, x, h=0.1)
        result_small = calculus.derivative(f, x, h=1e-6)
        
        assert abs(result_small - expected) < abs(result_large - expected)

    def test_integrate_negative_interval(self):
        """Test integration with a > b."""
        import calculus
        
        f = lambda x: x
        
        # ∫₁⁰ x dx = -∫₀¹ x dx = -0.5
        result = calculus.integrate(f, 1.0, 0.0)
        assert abs(result - (-0.5)) < 1e-6

    def test_constant_function(self):
        """Test with constant functions."""
        import calculus
        
        f = lambda x: 5.0
        
        # Derivative of constant is 0
        assert abs(calculus.derivative(f, 1.0)) < 1e-6
        
        # Integral of 5 from 0 to 2 is 10
        assert abs(calculus.integrate(f, 0.0, 2.0) - 10.0) < 1e-6

    def test_zero_function(self):
        """Test with zero function."""
        import calculus
        
        f = lambda x: 0.0
        
        assert abs(calculus.derivative(f, 1.0)) < 1e-10
        assert abs(calculus.integrate(f, 0.0, 10.0)) < 1e-10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

