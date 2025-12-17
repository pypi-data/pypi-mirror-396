#pragma once

#include <functional>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <string>
#include <optional>

namespace calculus {

/**
 * Numerical limit computation using sequence approximation.
 * Computes limits by evaluating the function at points approaching the limit point.
 */
class Limits {
public:
    using Function = std::function<double(double)>;

    /**
     * Direction of limit approach.
     */
    enum class Direction {
        Both,   // Two-sided limit
        Left,   // Left-hand limit (x -> a-)
        Right   // Right-hand limit (x -> a+)
    };

    /**
     * Result of a limit computation.
     */
    struct LimitResult {
        double value;           // The computed limit value
        bool exists;            // Whether the limit appears to exist
        bool is_finite;         // Whether the limit is finite
        double confidence;      // Confidence estimate (0-1)
        
        LimitResult(double v = 0.0, bool e = true, bool f = true, double c = 1.0)
            : value(v), exists(e), is_finite(f), confidence(c) {}
    };

    /**
     * Compute the limit of f(x) as x approaches a.
     * Uses Richardson extrapolation for improved accuracy.
     * 
     * @param f The function
     * @param a The point to approach
     * @param direction Direction of approach (Both, Left, or Right)
     * @param tol Tolerance for convergence detection
     * @return LimitResult containing the limit value and metadata
     */
    static LimitResult limit(const Function& f, double a, 
                             Direction direction = Direction::Both,
                             double tol = 1e-10) {
        if (direction == Direction::Both) {
            // Check both sides and verify they match
            LimitResult left = compute_one_sided_limit(f, a, -1, tol);
            LimitResult right = compute_one_sided_limit(f, a, 1, tol);
            
            if (!left.exists || !right.exists) {
                return LimitResult(std::numeric_limits<double>::quiet_NaN(), false, false, 0.0);
            }
            
            // Check if left and right limits match
            double diff = std::abs(left.value - right.value);
            double scale = std::max(std::abs(left.value), std::abs(right.value));
            if (scale < 1.0) scale = 1.0;
            
            if (diff / scale > tol * 1000) {
                // Limits don't match - limit doesn't exist
                return LimitResult(std::numeric_limits<double>::quiet_NaN(), false, false, 0.0);
            }
            
            // Average the two limits
            double avg = (left.value + right.value) / 2.0;
            double confidence = std::min(left.confidence, right.confidence);
            bool is_finite = left.is_finite && right.is_finite;
            
            return LimitResult(avg, true, is_finite, confidence);
        }
        
        int sign = (direction == Direction::Right) ? 1 : -1;
        return compute_one_sided_limit(f, a, sign, tol);
    }

    /**
     * Compute the limit as x approaches positive or negative infinity.
     * 
     * @param f The function
     * @param positive If true, compute lim(x->+∞), else lim(x->-∞)
     * @param tol Tolerance for convergence
     * @return LimitResult containing the limit value and metadata
     */
    static LimitResult limit_at_infinity(const Function& f, bool positive = true,
                                         double tol = 1e-8) {
        // Use substitution t = 1/x to transform limit at infinity to limit at 0
        // lim(x->∞) f(x) = lim(t->0+) f(1/t)
        
        std::vector<double> values;
        std::vector<double> x_values;
        
        double base = positive ? 1.0 : -1.0;
        
        // Evaluate at increasingly large x values
        for (int i = 1; i <= 20; ++i) {
            double x = base * std::pow(10.0, i);
            double val = f(x);
            
            if (std::isnan(val)) continue;
            
            values.push_back(val);
            x_values.push_back(x);
        }
        
        if (values.size() < 5) {
            return LimitResult(std::numeric_limits<double>::quiet_NaN(), false, false, 0.0);
        }
        
        // Check for convergence
        double last = values.back();
        bool is_finite = std::isfinite(last);
        
        if (!is_finite) {
            // Check if diverging to infinity
            bool all_increasing = true;
            bool all_decreasing = true;
            for (size_t i = 1; i < values.size(); ++i) {
                if (values[i] <= values[i-1]) all_increasing = false;
                if (values[i] >= values[i-1]) all_decreasing = false;
            }
            
            if (all_increasing) {
                return LimitResult(std::numeric_limits<double>::infinity(), true, false, 0.9);
            }
            if (all_decreasing) {
                return LimitResult(-std::numeric_limits<double>::infinity(), true, false, 0.9);
            }
            
            return LimitResult(std::numeric_limits<double>::quiet_NaN(), false, false, 0.0);
        }
        
        // Check convergence by looking at differences
        double confidence = 1.0;
        for (size_t i = values.size() - 3; i < values.size() - 1; ++i) {
            double diff = std::abs(values[i+1] - values[i]);
            double scale = std::max(std::abs(values[i]), 1.0);
            if (diff / scale > tol) {
                confidence *= 0.8;
            }
        }
        
        // Use Richardson extrapolation on the last few values
        double extrapolated = richardson_extrapolate(values);
        
        return LimitResult(extrapolated, true, true, confidence);
    }

    /**
     * Simplified limit function returning just the value.
     * Throws an exception if the limit doesn't exist.
     */
    static double limit_value(const Function& f, double a,
                              Direction direction = Direction::Both,
                              double tol = 1e-10) {
        LimitResult result = limit(f, a, direction, tol);
        if (!result.exists) {
            throw std::runtime_error("Limit does not exist");
        }
        return result.value;
    }

    /**
     * Simplified limit at infinity function returning just the value.
     */
    static double limit_inf_value(const Function& f, bool positive = true,
                                  double tol = 1e-8) {
        LimitResult result = limit_at_infinity(f, positive, tol);
        if (!result.exists) {
            throw std::runtime_error("Limit at infinity does not exist");
        }
        return result.value;
    }

private:
    /**
     * Compute one-sided limit using Romberg-like extrapolation.
     * 
     * @param f The function
     * @param a The limit point
     * @param sign Direction: +1 for right, -1 for left
     * @param tol Tolerance
     */
    static LimitResult compute_one_sided_limit(const Function& f, double a, 
                                                int sign, double tol) {
        const int max_iterations = 30;
        std::vector<double> values;
        
        // Generate sequence approaching 'a' from the given direction
        // Use h = 1, 0.5, 0.25, 0.125, ... scaled appropriately
        double base_h = 0.1;
        
        for (int i = 0; i < max_iterations; ++i) {
            double h = base_h * std::pow(0.5, i);
            double x = a + sign * h;
            double val = f(x);
            
            if (std::isnan(val)) {
                // Function undefined at this point, try to continue
                if (values.empty()) {
                    continue;  // Haven't found any valid point yet
                }
                break;  // Stop if we hit NaN after having valid values
            }
            
            if (std::isinf(val)) {
                // Limit might be infinite
                if (values.size() >= 3) {
                    // Check if approaching infinity
                    bool diverging = true;
                    for (size_t j = 1; j < values.size(); ++j) {
                        if (std::abs(values[j]) <= std::abs(values[j-1]) * 1.1) {
                            diverging = false;
                            break;
                        }
                    }
                    if (diverging) {
                        return LimitResult(val, true, false, 0.8);
                    }
                }
            }
            
            values.push_back(val);
            
            // Check for convergence
            if (values.size() >= 5) {
                double diff1 = std::abs(values.back() - values[values.size()-2]);
                double diff2 = std::abs(values[values.size()-2] - values[values.size()-3]);
                double scale = std::max(std::abs(values.back()), 1.0);
                
                // If differences are decreasing and small, we've converged
                if (diff1 < tol * scale && diff1 < diff2) {
                    double extrapolated = richardson_extrapolate(values);
                    return LimitResult(extrapolated, true, true, 1.0);
                }
            }
        }
        
        if (values.size() < 3) {
            return LimitResult(std::numeric_limits<double>::quiet_NaN(), false, false, 0.0);
        }
        
        // Use Richardson extrapolation
        double extrapolated = richardson_extrapolate(values);
        
        // Estimate confidence based on convergence rate
        double diff = std::abs(values.back() - values[values.size()-2]);
        double scale = std::max(std::abs(extrapolated), 1.0);
        double confidence = std::min(1.0, tol / (diff / scale + tol));
        
        return LimitResult(extrapolated, true, std::isfinite(extrapolated), confidence);
    }

    /**
     * Apply Richardson extrapolation to a sequence of values.
     * Assumes the sequence is from evaluations with halving step sizes.
     */
    static double richardson_extrapolate(const std::vector<double>& values) {
        if (values.empty()) return std::numeric_limits<double>::quiet_NaN();
        if (values.size() == 1) return values[0];
        if (values.size() == 2) {
            // Simple linear extrapolation
            return 2.0 * values[1] - values[0];
        }
        
        // Aitken's delta-squared method for acceleration
        size_t n = values.size();
        double s0 = values[n-3];
        double s1 = values[n-2];
        double s2 = values[n-1];
        
        double denom = s2 - 2*s1 + s0;
        if (std::abs(denom) < 1e-15) {
            return s2;  // Already converged
        }
        
        double accelerated = s2 - (s2 - s1) * (s2 - s1) / denom;
        return accelerated;
    }
};

} // namespace calculus

