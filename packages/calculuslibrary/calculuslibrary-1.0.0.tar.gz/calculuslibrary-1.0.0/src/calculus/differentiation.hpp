#pragma once

#include <functional>
#include <cmath>
#include <vector>
#include <stdexcept>

namespace calculus {

/**
 * Numerical differentiation using finite difference methods.
 * Provides accurate approximations for derivatives of arbitrary functions.
 */
class Differentiation {
public:
    using Function = std::function<double(double)>;

    /**
     * Compute the first derivative using central difference method.
     * Formula: f'(x) ≈ (f(x+h) - f(x-h)) / (2h)
     * 
     * @param f The function to differentiate
     * @param x The point at which to evaluate the derivative
     * @param h Step size (default: 1e-6)
     * @return Approximation of f'(x)
     */
    static double first_derivative(const Function& f, double x, double h = 1e-6) {
        if (h <= 0) {
            throw std::invalid_argument("Step size h must be positive");
        }
        return (f(x + h) - f(x - h)) / (2.0 * h);
    }

    /**
     * Compute the second derivative using central difference method.
     * Formula: f''(x) ≈ (f(x+h) - 2f(x) + f(x-h)) / h²
     * 
     * @param f The function to differentiate
     * @param x The point at which to evaluate the derivative
     * @param h Step size (default: 1e-4, larger for stability)
     * @return Approximation of f''(x)
     */
    static double second_derivative(const Function& f, double x, double h = 1e-4) {
        if (h <= 0) {
            throw std::invalid_argument("Step size h must be positive");
        }
        return (f(x + h) - 2.0 * f(x) + f(x - h)) / (h * h);
    }

    /**
     * Compute the nth derivative using recursive central differences.
     * Uses the formula for higher-order finite differences.
     * 
     * @param f The function to differentiate
     * @param x The point at which to evaluate the derivative
     * @param n Order of the derivative (n >= 1)
     * @param h Step size (automatically adjusted for higher orders)
     * @return Approximation of f^(n)(x)
     */
    static double nth_derivative(const Function& f, double x, int n, double h = 1e-3) {
        if (n < 0) {
            throw std::invalid_argument("Derivative order must be non-negative");
        }
        if (n == 0) {
            return f(x);
        }
        if (h <= 0) {
            throw std::invalid_argument("Step size h must be positive");
        }

        // Adjust step size for higher order derivatives
        double adjusted_h = h * std::pow(2.0, (n - 1) / 2.0);
        
        // Use central difference formula with binomial coefficients
        // f^(n)(x) ≈ (1/h^n) * Σ_{k=0}^{n} (-1)^k * C(n,k) * f(x + (n/2 - k)*h)
        double result = 0.0;
        double h_n = std::pow(adjusted_h, n);
        
        for (int k = 0; k <= n; ++k) {
            double coef = binomial_coefficient(n, k);
            if (k % 2 == 1) coef = -coef;
            double point = x + (n / 2.0 - k) * adjusted_h;
            result += coef * f(point);
        }
        
        return result / h_n;
    }

    /**
     * Compute the forward difference approximation.
     * Formula: f'(x) ≈ (f(x+h) - f(x)) / h
     * Less accurate but useful when f(x-h) is undefined.
     */
    static double forward_difference(const Function& f, double x, double h = 1e-6) {
        if (h <= 0) {
            throw std::invalid_argument("Step size h must be positive");
        }
        return (f(x + h) - f(x)) / h;
    }

    /**
     * Compute the backward difference approximation.
     * Formula: f'(x) ≈ (f(x) - f(x-h)) / h
     * Less accurate but useful when f(x+h) is undefined.
     */
    static double backward_difference(const Function& f, double x, double h = 1e-6) {
        if (h <= 0) {
            throw std::invalid_argument("Step size h must be positive");
        }
        return (f(x) - f(x - h)) / h;
    }

    /**
     * Compute a more accurate first derivative using Richardson extrapolation.
     * Combines central differences with different step sizes for higher accuracy.
     */
    static double derivative_richardson(const Function& f, double x, double h = 1e-4) {
        if (h <= 0) {
            throw std::invalid_argument("Step size h must be positive");
        }
        
        // Richardson extrapolation: D1 with h and h/2
        double d1 = first_derivative(f, x, h);
        double d2 = first_derivative(f, x, h / 2.0);
        
        // Richardson formula for central difference (order 2 method)
        return (4.0 * d2 - d1) / 3.0;
    }

private:
    /**
     * Compute binomial coefficient C(n, k) = n! / (k! * (n-k)!)
     */
    static double binomial_coefficient(int n, int k) {
        if (k < 0 || k > n) return 0;
        if (k == 0 || k == n) return 1;
        
        // Use multiplicative formula to avoid overflow
        double result = 1.0;
        for (int i = 0; i < k; ++i) {
            result *= (n - i);
            result /= (i + 1);
        }
        return result;
    }
};

} // namespace calculus

