#pragma once

#include <functional>
#include <cmath>
#include <vector>
#include <stdexcept>
#include <limits>
#include <algorithm>

namespace calculus {

/**
 * Numerical integration methods for definite integrals.
 * Provides various algorithms with different accuracy/performance trade-offs.
 */
class Integration {
public:
    using Function = std::function<double(double)>;

    /**
     * Integrate using the trapezoidal rule.
     * Formula: ∫f(x)dx ≈ h/2 * [f(a) + 2*Σf(xi) + f(b)]
     * 
     * @param f The function to integrate
     * @param a Lower bound of integration
     * @param b Upper bound of integration
     * @param n Number of intervals (default: 1000)
     * @return Approximation of the definite integral
     */
    static double trapezoidal(const Function& f, double a, double b, int n = 1000) {
        if (n <= 0) {
            throw std::invalid_argument("Number of intervals must be positive");
        }
        
        double h = (b - a) / n;
        double result = 0.5 * (f(a) + f(b));
        
        for (int i = 1; i < n; ++i) {
            result += f(a + i * h);
        }
        
        return result * h;
    }

    /**
     * Integrate using Simpson's rule.
     * Formula: ∫f(x)dx ≈ h/3 * [f(a) + 4*Σf(x_odd) + 2*Σf(x_even) + f(b)]
     * More accurate than trapezoidal for smooth functions.
     * 
     * @param f The function to integrate
     * @param a Lower bound of integration
     * @param b Upper bound of integration
     * @param n Number of intervals (must be even, default: 1000)
     * @return Approximation of the definite integral
     */
    static double simpson(const Function& f, double a, double b, int n = 1000) {
        if (n <= 0) {
            throw std::invalid_argument("Number of intervals must be positive");
        }
        // Ensure n is even
        if (n % 2 != 0) n++;
        
        double h = (b - a) / n;
        double result = f(a) + f(b);
        
        for (int i = 1; i < n; ++i) {
            double x = a + i * h;
            if (i % 2 == 0) {
                result += 2.0 * f(x);
            } else {
                result += 4.0 * f(x);
            }
        }
        
        return result * h / 3.0;
    }

    /**
     * Integrate using Simpson's 3/8 rule.
     * Uses cubic interpolation for potentially better accuracy.
     * 
     * @param f The function to integrate
     * @param a Lower bound of integration
     * @param b Upper bound of integration
     * @param n Number of intervals (should be divisible by 3)
     * @return Approximation of the definite integral
     */
    static double simpson38(const Function& f, double a, double b, int n = 999) {
        if (n <= 0) {
            throw std::invalid_argument("Number of intervals must be positive");
        }
        // Adjust n to be divisible by 3
        n = (n / 3) * 3;
        if (n == 0) n = 3;
        
        double h = (b - a) / n;
        double result = f(a) + f(b);
        
        for (int i = 1; i < n; ++i) {
            double x = a + i * h;
            if (i % 3 == 0) {
                result += 2.0 * f(x);
            } else {
                result += 3.0 * f(x);
            }
        }
        
        return result * 3.0 * h / 8.0;
    }

    /**
     * Adaptive quadrature using recursive Simpson's rule.
     * Automatically adjusts step size based on local error estimates.
     * 
     * @param f The function to integrate
     * @param a Lower bound of integration
     * @param b Upper bound of integration
     * @param tol Error tolerance (default: 1e-8)
     * @param max_depth Maximum recursion depth (default: 50)
     * @return Approximation of the definite integral
     */
    static double adaptive_quadrature(const Function& f, double a, double b, 
                                      double tol = 1e-8, int max_depth = 50) {
        if (tol <= 0) {
            throw std::invalid_argument("Tolerance must be positive");
        }
        return adaptive_simpson(f, a, b, tol, max_depth, 0);
    }

    /**
     * Gauss-Legendre quadrature (5-point).
     * Very accurate for polynomial-like functions.
     * 
     * @param f The function to integrate
     * @param a Lower bound of integration
     * @param b Upper bound of integration
     * @return Approximation of the definite integral
     */
    static double gauss_legendre_5(const Function& f, double a, double b) {
        // 5-point Gauss-Legendre nodes and weights
        static const double nodes[] = {
            0.0,
            0.5384693101056831,
            -0.5384693101056831,
            0.9061798459386640,
            -0.9061798459386640
        };
        static const double weights[] = {
            0.5688888888888889,
            0.4786286704993665,
            0.4786286704993665,
            0.2369268850561891,
            0.2369268850561891
        };
        
        // Transform from [-1, 1] to [a, b]
        double mid = (a + b) / 2.0;
        double half_length = (b - a) / 2.0;
        
        double result = 0.0;
        for (int i = 0; i < 5; ++i) {
            double x = mid + half_length * nodes[i];
            result += weights[i] * f(x);
        }
        
        return result * half_length;
    }

    /**
     * Composite Gauss-Legendre quadrature.
     * Divides interval into subintervals and applies Gauss-Legendre to each.
     * 
     * @param f The function to integrate
     * @param a Lower bound of integration
     * @param b Upper bound of integration
     * @param n Number of subintervals (default: 100)
     * @return Approximation of the definite integral
     */
    static double gauss_legendre(const Function& f, double a, double b, int n = 100) {
        if (n <= 0) {
            throw std::invalid_argument("Number of intervals must be positive");
        }
        
        double h = (b - a) / n;
        double result = 0.0;
        
        for (int i = 0; i < n; ++i) {
            double sub_a = a + i * h;
            double sub_b = sub_a + h;
            result += gauss_legendre_5(f, sub_a, sub_b);
        }
        
        return result;
    }

    /**
     * Romberg integration.
     * Uses Richardson extrapolation on the trapezoidal rule.
     * Very accurate for smooth functions.
     * 
     * @param f The function to integrate
     * @param a Lower bound of integration
     * @param b Upper bound of integration
     * @param max_iter Maximum iterations (default: 20)
     * @param tol Convergence tolerance (default: 1e-10)
     * @return Approximation of the definite integral
     */
    static double romberg(const Function& f, double a, double b, 
                          int max_iter = 20, double tol = 1e-10) {
        std::vector<std::vector<double>> R(max_iter, std::vector<double>(max_iter, 0.0));
        
        double h = b - a;
        R[0][0] = 0.5 * h * (f(a) + f(b));
        
        for (int i = 1; i < max_iter; ++i) {
            h /= 2.0;
            
            // Compute trapezoidal estimate with new points
            double sum = 0.0;
            int num_new_points = 1 << (i - 1);  // 2^(i-1)
            for (int k = 0; k < num_new_points; ++k) {
                sum += f(a + (2 * k + 1) * h);
            }
            R[i][0] = 0.5 * R[i-1][0] + h * sum;
            
            // Richardson extrapolation
            for (int j = 1; j <= i; ++j) {
                double factor = std::pow(4.0, j);
                R[i][j] = (factor * R[i][j-1] - R[i-1][j-1]) / (factor - 1.0);
            }
            
            // Check convergence
            if (i > 0 && std::abs(R[i][i] - R[i-1][i-1]) < tol) {
                return R[i][i];
            }
        }
        
        return R[max_iter-1][max_iter-1];
    }

private:
    /**
     * Recursive adaptive Simpson's rule helper.
     */
    static double adaptive_simpson(const Function& f, double a, double b,
                                   double tol, int max_depth, int depth) {
        double c = (a + b) / 2.0;
        double h = b - a;
        
        double fa = f(a);
        double fb = f(b);
        double fc = f(c);
        
        double S = (h / 6.0) * (fa + 4.0 * fc + fb);
        
        if (depth >= max_depth) {
            return S;
        }
        
        double d = (a + c) / 2.0;
        double e = (c + b) / 2.0;
        double fd = f(d);
        double fe = f(e);
        
        double S_left = (h / 12.0) * (fa + 4.0 * fd + fc);
        double S_right = (h / 12.0) * (fc + 4.0 * fe + fb);
        double S2 = S_left + S_right;
        
        double error = std::abs(S2 - S) / 15.0;
        
        if (error < tol) {
            return S2 + (S2 - S) / 15.0;  // Richardson extrapolation
        }
        
        return adaptive_simpson(f, a, c, tol / 2.0, max_depth, depth + 1) +
               adaptive_simpson(f, c, b, tol / 2.0, max_depth, depth + 1);
    }
};

} // namespace calculus

