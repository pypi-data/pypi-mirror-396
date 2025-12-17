/**
 * pybind11 bindings for the Calculus Library
 * 
 * This file creates Python bindings for all C++ calculus functions,
 * allowing seamless use from Python with automatic type conversion.
 */

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>
#include <sstream>

#include "differentiation.hpp"
#include "integration.hpp"
#include "limits.hpp"
#include "series.hpp"

namespace py = pybind11;
using namespace calculus;

// Type alias for Python callable
using PyFunction = std::function<double(double)>;

PYBIND11_MODULE(_calculus_core, m) {
    m.doc() = R"pbdoc(
        Calculus Library - High-Performance Numerical Calculus for Python
        ==================================================================

        A comprehensive calculus library with C++ backend providing:
        - Numerical differentiation (central differences, Richardson extrapolation)
        - Numerical integration (trapezoidal, Simpson's, adaptive quadrature)
        - Limit computation (one-sided, two-sided, limits at infinity)
        - Taylor series expansion and evaluation

        Example usage:
            import calculus
            
            # Define a function
            f = lambda x: x**2
            
            # Compute derivative at x=2
            df = calculus.derivative(f, 2.0)  # Returns 4.0
            
            # Integrate from 0 to 1
            integral = calculus.integrate(f, 0.0, 1.0)  # Returns ~0.333
    )pbdoc";

    // ========================================================================
    // Version info
    // ========================================================================
    m.attr("__version__") = "1.0.0";

    // ========================================================================
    // Differentiation functions
    // ========================================================================
    
    m.def("derivative", [](const PyFunction& f, double x, int n, double h) {
        if (n == 1) {
            return Differentiation::first_derivative(f, x, h);
        } else if (n == 2) {
            return Differentiation::second_derivative(f, x, h);
        } else {
            return Differentiation::nth_derivative(f, x, n, h);
        }
    }, py::arg("f"), py::arg("x"), py::arg("n") = 1, py::arg("h") = 1e-6,
    R"pbdoc(
        Compute the nth derivative of f at point x.

        Parameters
        ----------
        f : callable
            The function to differentiate. Must accept a single float argument.
        x : float
            The point at which to evaluate the derivative.
        n : int, optional
            Order of the derivative (default: 1).
        h : float, optional
            Step size for finite differences (default: 1e-6).

        Returns
        -------
        float
            Approximation of f^(n)(x).

        Examples
        --------
        >>> import calculus
        >>> f = lambda x: x**3
        >>> calculus.derivative(f, 2.0)  # First derivative: 3x^2 = 12
        12.0
        >>> calculus.derivative(f, 2.0, n=2)  # Second derivative: 6x = 12
        12.0
    )pbdoc");

    m.def("first_derivative", &Differentiation::first_derivative,
        py::arg("f"), py::arg("x"), py::arg("h") = 1e-6,
        "Compute first derivative using central difference method.");

    m.def("second_derivative", &Differentiation::second_derivative,
        py::arg("f"), py::arg("x"), py::arg("h") = 1e-4,
        "Compute second derivative using central difference method.");

    m.def("nth_derivative", &Differentiation::nth_derivative,
        py::arg("f"), py::arg("x"), py::arg("n"), py::arg("h") = 1e-3,
        "Compute nth derivative using recursive central differences.");

    m.def("forward_difference", &Differentiation::forward_difference,
        py::arg("f"), py::arg("x"), py::arg("h") = 1e-6,
        "Compute derivative using forward difference (less accurate).");

    m.def("backward_difference", &Differentiation::backward_difference,
        py::arg("f"), py::arg("x"), py::arg("h") = 1e-6,
        "Compute derivative using backward difference (less accurate).");

    m.def("derivative_richardson", &Differentiation::derivative_richardson,
        py::arg("f"), py::arg("x"), py::arg("h") = 1e-4,
        "Compute derivative using Richardson extrapolation (higher accuracy).");

    // ========================================================================
    // Integration functions
    // ========================================================================

    m.def("integrate", [](const PyFunction& f, double a, double b, 
                          const std::string& method, int n) {
        if (method == "trapezoidal" || method == "trapz") {
            return Integration::trapezoidal(f, a, b, n);
        } else if (method == "simpson" || method == "simps") {
            return Integration::simpson(f, a, b, n);
        } else if (method == "simpson38") {
            return Integration::simpson38(f, a, b, n);
        } else if (method == "gauss" || method == "gauss_legendre") {
            return Integration::gauss_legendre(f, a, b, n);
        } else if (method == "romberg") {
            return Integration::romberg(f, a, b, n);
        } else {
            throw std::invalid_argument("Unknown integration method: " + method);
        }
    }, py::arg("f"), py::arg("a"), py::arg("b"), 
       py::arg("method") = "simpson", py::arg("n") = 1000,
    R"pbdoc(
        Integrate f(x) from a to b using the specified method.

        Parameters
        ----------
        f : callable
            The function to integrate.
        a : float
            Lower bound of integration.
        b : float
            Upper bound of integration.
        method : str, optional
            Integration method: 'simpson', 'trapezoidal', 'simpson38', 
            'gauss', 'romberg' (default: 'simpson').
        n : int, optional
            Number of intervals or iterations (default: 1000).

        Returns
        -------
        float
            Approximation of the definite integral.

        Examples
        --------
        >>> import calculus
        >>> f = lambda x: x**2
        >>> calculus.integrate(f, 0.0, 1.0)  # ∫x² dx from 0 to 1 = 1/3
        0.3333333333333333
    )pbdoc");

    m.def("quad", &Integration::adaptive_quadrature,
        py::arg("f"), py::arg("a"), py::arg("b"), 
        py::arg("tol") = 1e-8, py::arg("max_depth") = 50,
    R"pbdoc(
        Adaptive quadrature integration with automatic error control.

        Uses recursive Simpson's rule with adaptive step size selection.

        Parameters
        ----------
        f : callable
            The function to integrate.
        a : float
            Lower bound of integration.
        b : float
            Upper bound of integration.
        tol : float, optional
            Error tolerance (default: 1e-8).
        max_depth : int, optional
            Maximum recursion depth (default: 50).

        Returns
        -------
        float
            Approximation of the definite integral.
    )pbdoc");

    m.def("trapezoidal", &Integration::trapezoidal,
        py::arg("f"), py::arg("a"), py::arg("b"), py::arg("n") = 1000,
        "Integrate using the trapezoidal rule.");

    m.def("simpson", &Integration::simpson,
        py::arg("f"), py::arg("a"), py::arg("b"), py::arg("n") = 1000,
        "Integrate using Simpson's rule.");

    m.def("romberg", &Integration::romberg,
        py::arg("f"), py::arg("a"), py::arg("b"), 
        py::arg("max_iter") = 20, py::arg("tol") = 1e-10,
        "Integrate using Romberg's method (Richardson extrapolation).");

    m.def("gauss_legendre", &Integration::gauss_legendre,
        py::arg("f"), py::arg("a"), py::arg("b"), py::arg("n") = 100,
        "Integrate using Gauss-Legendre quadrature.");

    // ========================================================================
    // Limit functions
    // ========================================================================

    // Direction enum
    py::enum_<Limits::Direction>(m, "Direction", "Direction of limit approach")
        .value("Both", Limits::Direction::Both, "Two-sided limit")
        .value("Left", Limits::Direction::Left, "Left-hand limit (x -> a-)")
        .value("Right", Limits::Direction::Right, "Right-hand limit (x -> a+)")
        .export_values();

    // LimitResult class
    py::class_<Limits::LimitResult>(m, "LimitResult", "Result of a limit computation")
        .def_readonly("value", &Limits::LimitResult::value, "The computed limit value")
        .def_readonly("exists", &Limits::LimitResult::exists, "Whether the limit exists")
        .def_readonly("is_finite", &Limits::LimitResult::is_finite, "Whether the limit is finite")
        .def_readonly("confidence", &Limits::LimitResult::confidence, "Confidence estimate (0-1)")
        .def("__repr__", [](const Limits::LimitResult& r) {
            std::ostringstream oss;
            oss << "LimitResult(value=" << r.value 
                << ", exists=" << (r.exists ? "True" : "False")
                << ", is_finite=" << (r.is_finite ? "True" : "False")
                << ", confidence=" << r.confidence << ")";
            return oss.str();
        });

    m.def("limit", [](const PyFunction& f, double a, const std::string& direction, double tol) {
        Limits::Direction dir = Limits::Direction::Both;
        if (direction == "left" || direction == "Left" || direction == "-") {
            dir = Limits::Direction::Left;
        } else if (direction == "right" || direction == "Right" || direction == "+") {
            dir = Limits::Direction::Right;
        }
        return Limits::limit(f, a, dir, tol);
    }, py::arg("f"), py::arg("x"), py::arg("direction") = "both", py::arg("tol") = 1e-10,
    R"pbdoc(
        Compute the limit of f(x) as x approaches a given value.

        Parameters
        ----------
        f : callable
            The function.
        x : float
            The point to approach.
        direction : str, optional
            Direction of approach: 'both', 'left'/'-', 'right'/'+' (default: 'both').
        tol : float, optional
            Tolerance for convergence detection (default: 1e-10).

        Returns
        -------
        LimitResult
            Object containing the limit value and metadata.

        Examples
        --------
        >>> import calculus
        >>> f = lambda x: (x**2 - 1) / (x - 1)  # = x + 1 for x ≠ 1
        >>> result = calculus.limit(f, 1.0)
        >>> result.value  # Limit is 2
        2.0
    )pbdoc");

    m.def("limit_inf", [](const PyFunction& f, const std::string& direction, double tol) {
        bool positive = true;
        if (direction == "negative" || direction == "-" || direction == "-inf") {
            positive = false;
        }
        return Limits::limit_at_infinity(f, positive, tol);
    }, py::arg("f"), py::arg("direction") = "positive", py::arg("tol") = 1e-8,
    R"pbdoc(
        Compute the limit of f(x) as x approaches infinity.

        Parameters
        ----------
        f : callable
            The function.
        direction : str, optional
            'positive'/'+' for +∞, 'negative'/'-' for -∞ (default: 'positive').
        tol : float, optional
            Tolerance for convergence (default: 1e-8).

        Returns
        -------
        LimitResult
            Object containing the limit value and metadata.

        Examples
        --------
        >>> import calculus
        >>> f = lambda x: 1/x
        >>> result = calculus.limit_inf(f)
        >>> result.value  # Limit is 0
        0.0
    )pbdoc");

    m.def("limit_value", [](const PyFunction& f, double a, const std::string& direction, double tol) {
        Limits::Direction dir = Limits::Direction::Both;
        if (direction == "left" || direction == "Left" || direction == "-") {
            dir = Limits::Direction::Left;
        } else if (direction == "right" || direction == "Right" || direction == "+") {
            dir = Limits::Direction::Right;
        }
        return Limits::limit_value(f, a, dir, tol);
    }, py::arg("f"), py::arg("x"), py::arg("direction") = "both", py::arg("tol") = 1e-10,
    "Compute limit and return just the value (raises exception if limit doesn't exist).");

    // ========================================================================
    // Series functions
    // ========================================================================

    m.def("taylor", &Series::taylor_coefficients,
        py::arg("f"), py::arg("a"), py::arg("n") = 10, py::arg("h") = 1e-3,
    R"pbdoc(
        Compute Taylor series coefficients around point a.

        Returns coefficients c_0, c_1, ..., c_{n-1} where:
        f(x) ≈ c_0 + c_1*(x-a) + c_2*(x-a)² + ... + c_{n-1}*(x-a)^{n-1}

        Parameters
        ----------
        f : callable
            The function to expand.
        a : float
            Center point of the expansion.
        n : int, optional
            Number of terms (default: 10).
        h : float, optional
            Step size for derivative computation (default: 1e-3).

        Returns
        -------
        list of float
            Taylor coefficients [c_0, c_1, ..., c_{n-1}].

        Examples
        --------
        >>> import calculus
        >>> import math
        >>> f = math.exp  # e^x
        >>> coeffs = calculus.taylor(f, 0.0, 5)  # Maclaurin series
        >>> coeffs  # Should be [1, 1, 0.5, 0.166..., 0.041...]
    )pbdoc");

    m.def("maclaurin", &Series::maclaurin_coefficients,
        py::arg("f"), py::arg("n") = 10, py::arg("h") = 1e-3,
        "Compute Maclaurin series coefficients (Taylor series around x=0).");

    m.def("taylor_eval", &Series::taylor_eval,
        py::arg("f"), py::arg("a"), py::arg("x"), py::arg("n") = 10, py::arg("h") = 1e-3,
    R"pbdoc(
        Evaluate Taylor polynomial approximation at point x.

        Parameters
        ----------
        f : callable
            The function to approximate.
        a : float
            Center point of the Taylor expansion.
        x : float
            Point at which to evaluate the approximation.
        n : int, optional
            Number of terms (default: 10).
        h : float, optional
            Step size for derivative computation (default: 1e-3).

        Returns
        -------
        float
            Taylor polynomial approximation of f(x).

        Examples
        --------
        >>> import calculus
        >>> import math
        >>> f = math.sin
        >>> approx = calculus.taylor_eval(f, 0.0, 0.5, n=5)
        >>> actual = math.sin(0.5)
        >>> abs(approx - actual) < 0.001
        True
    )pbdoc");

    m.def("taylor_eval_with_coeffs", &Series::taylor_eval_with_coeffs,
        py::arg("coefficients"), py::arg("a"), py::arg("x"),
        "Evaluate Taylor polynomial using pre-computed coefficients.");

    m.def("taylor_error", &Series::taylor_error_estimate,
        py::arg("f"), py::arg("a"), py::arg("x"), py::arg("n") = 10, py::arg("h") = 1e-3,
        "Estimate the error in Taylor approximation using Lagrange remainder.");

    m.def("radius_of_convergence", &Series::radius_of_convergence,
        py::arg("coefficients"),
        "Estimate the radius of convergence for a Taylor series from its coefficients.");

    // PowerSeries class
    py::class_<Series::PowerSeries>(m, "PowerSeries", "A power series representation")
        .def(py::init<std::vector<double>, double>())
        .def_readonly("coefficients", &Series::PowerSeries::coefficients)
        .def_readonly("center", &Series::PowerSeries::center)
        .def("__call__", &Series::PowerSeries::operator())
        .def("__repr__", [](const Series::PowerSeries& s) {
            std::ostringstream oss;
            oss << "PowerSeries(center=" << s.center 
                << ", terms=" << s.coefficients.size() << ")";
            return oss.str();
        });

    m.def("taylor_series", &Series::taylor_series,
        py::arg("f"), py::arg("a"), py::arg("n") = 10, py::arg("h") = 1e-3,
    R"pbdoc(
        Create a PowerSeries object representing the Taylor expansion of f around a.

        The returned object is callable and can be used to evaluate the series.

        Parameters
        ----------
        f : callable
            The function to expand.
        a : float
            Center point.
        n : int, optional
            Number of terms (default: 10).
        h : float, optional
            Step size for derivatives (default: 1e-3).

        Returns
        -------
        PowerSeries
            A callable power series object.

        Examples
        --------
        >>> import calculus
        >>> import math
        >>> series = calculus.taylor_series(math.sin, 0.0, n=10)
        >>> series(0.5)  # Evaluate at x=0.5
    )pbdoc");
}

