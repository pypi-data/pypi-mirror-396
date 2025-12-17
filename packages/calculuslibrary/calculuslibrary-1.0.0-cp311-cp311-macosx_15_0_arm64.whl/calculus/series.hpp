#pragma once

#include <functional>
#include <cmath>
#include <vector>
#include <stdexcept>
#include "differentiation.hpp"

namespace calculus {

/**
 * Taylor and Maclaurin series expansion.
 * Computes Taylor series coefficients and evaluates polynomial approximations.
 */
class Series {
public:
    using Function = std::function<double(double)>;

    /**
     * Compute Taylor series coefficients around point a.
     * Returns coefficients c_0, c_1, ..., c_n where:
     * f(x) ≈ Σ c_k * (x-a)^k / k!
     * 
     * Note: The returned coefficients include the 1/k! factor.
     * So taylor_eval uses: Σ c_k * (x-a)^k
     * 
     * @param f The function to expand
     * @param a The center point of the expansion
     * @param n Number of terms (degree of polynomial + 1)
     * @param h Step size for derivative computation
     * @return Vector of Taylor coefficients [c_0, c_1, ..., c_n]
     */
    static std::vector<double> taylor_coefficients(const Function& f, double a, 
                                                    int n = 10, double h = 1e-3) {
        if (n <= 0) {
            throw std::invalid_argument("Number of terms must be positive");
        }
        
        std::vector<double> coefficients(n);
        
        // c_k = f^(k)(a) / k!
        double factorial = 1.0;
        for (int k = 0; k < n; ++k) {
            if (k > 0) factorial *= k;
            
            double derivative = Differentiation::nth_derivative(f, a, k, h);
            coefficients[k] = derivative / factorial;
        }
        
        return coefficients;
    }

    /**
     * Compute Maclaurin series coefficients (Taylor series around x=0).
     * 
     * @param f The function to expand
     * @param n Number of terms
     * @param h Step size for derivative computation
     * @return Vector of Maclaurin coefficients
     */
    static std::vector<double> maclaurin_coefficients(const Function& f, int n = 10, 
                                                       double h = 1e-3) {
        return taylor_coefficients(f, 0.0, n, h);
    }

    /**
     * Evaluate Taylor polynomial approximation at point x.
     * 
     * @param f The original function (used to compute coefficients)
     * @param a The center point of the expansion
     * @param x The point at which to evaluate the approximation
     * @param n Number of terms to use
     * @param h Step size for derivative computation
     * @return Taylor polynomial approximation of f(x)
     */
    static double taylor_eval(const Function& f, double a, double x, 
                              int n = 10, double h = 1e-3) {
        std::vector<double> coeffs = taylor_coefficients(f, a, n, h);
        return evaluate_polynomial(coeffs, x - a);
    }

    /**
     * Evaluate Taylor polynomial using pre-computed coefficients.
     * 
     * @param coefficients Pre-computed Taylor coefficients
     * @param a The center point used when computing coefficients
     * @param x The point at which to evaluate
     * @return Taylor polynomial approximation
     */
    static double taylor_eval_with_coeffs(const std::vector<double>& coefficients,
                                          double a, double x) {
        return evaluate_polynomial(coefficients, x - a);
    }

    /**
     * Estimate the error in Taylor approximation using the Lagrange remainder.
     * Error bound: |R_n(x)| ≤ M * |x-a|^(n+1) / (n+1)!
     * where M is an upper bound on |f^(n+1)(ξ)| for ξ between a and x.
     * 
     * @param f The function
     * @param a Center point
     * @param x Evaluation point
     * @param n Number of terms used
     * @param h Step size for derivative computation
     * @return Estimated error bound
     */
    static double taylor_error_estimate(const Function& f, double a, double x,
                                        int n = 10, double h = 1e-3) {
        // Estimate M by sampling the (n+1)th derivative between a and x
        double M = 0.0;
        int samples = 10;
        double step = (x - a) / samples;
        
        for (int i = 0; i <= samples; ++i) {
            double xi = a + i * step;
            double deriv = std::abs(Differentiation::nth_derivative(f, xi, n + 1, h));
            M = std::max(M, deriv);
        }
        
        // Compute (n+1)!
        double factorial = 1.0;
        for (int k = 2; k <= n + 1; ++k) {
            factorial *= k;
        }
        
        double dx = std::abs(x - a);
        return M * std::pow(dx, n + 1) / factorial;
    }

    /**
     * Find the radius of convergence estimate for a Taylor series.
     * Uses the ratio test on the coefficients.
     * 
     * @param coefficients Taylor coefficients
     * @return Estimated radius of convergence
     */
    static double radius_of_convergence(const std::vector<double>& coefficients) {
        if (coefficients.size() < 2) {
            return std::numeric_limits<double>::infinity();
        }
        
        // Use ratio test: R = lim |c_n / c_{n+1}|
        std::vector<double> ratios;
        for (size_t i = 0; i < coefficients.size() - 1; ++i) {
            if (std::abs(coefficients[i + 1]) > 1e-15) {
                double ratio = std::abs(coefficients[i] / coefficients[i + 1]);
                if (std::isfinite(ratio)) {
                    ratios.push_back(ratio);
                }
            }
        }
        
        if (ratios.empty()) {
            return std::numeric_limits<double>::infinity();
        }
        
        // Take the last few ratios as the best estimate
        double sum = 0.0;
        int count = std::min(static_cast<int>(ratios.size()), 5);
        for (int i = 0; i < count; ++i) {
            sum += ratios[ratios.size() - 1 - i];
        }
        
        return sum / count;
    }

    /**
     * Power series representation: stores coefficients and center.
     */
    struct PowerSeries {
        std::vector<double> coefficients;
        double center;
        
        PowerSeries(std::vector<double> c, double a) 
            : coefficients(std::move(c)), center(a) {}
        
        double operator()(double x) const {
            return evaluate_polynomial(coefficients, x - center);
        }
    };

    /**
     * Create a PowerSeries object for the Taylor expansion of f around a.
     */
    static PowerSeries taylor_series(const Function& f, double a, int n = 10, 
                                     double h = 1e-3) {
        return PowerSeries(taylor_coefficients(f, a, n, h), a);
    }

private:
    /**
     * Evaluate polynomial using Horner's method for numerical stability.
     * Evaluates: c_0 + c_1*x + c_2*x^2 + ... + c_n*x^n
     */
    static double evaluate_polynomial(const std::vector<double>& coeffs, double x) {
        if (coeffs.empty()) return 0.0;
        
        // Horner's method: ((c_n * x + c_{n-1}) * x + c_{n-2}) * x + ...
        double result = coeffs.back();
        for (int i = static_cast<int>(coeffs.size()) - 2; i >= 0; --i) {
            result = result * x + coeffs[i];
        }
        
        return result;
    }
};

} // namespace calculus

