/**
 * Calculus Library Core Implementation
 * 
 * This file combines all the calculus modules and provides the main
 * implementation that gets compiled into the shared library.
 * 
 * Modules included:
 * - Differentiation: Numerical differentiation using finite differences
 * - Integration: Numerical integration (trapezoidal, Simpson's, adaptive)
 * - Limits: Numerical limit computation
 * - Series: Taylor and Maclaurin series expansion
 */

#include "differentiation.hpp"
#include "integration.hpp"
#include "limits.hpp"
#include "series.hpp"

// This file serves as the compilation unit that includes all headers
// and ensures the template instantiations are available.

namespace calculus {

// Version information
constexpr const char* VERSION = "1.0.0";
constexpr int VERSION_MAJOR = 1;
constexpr int VERSION_MINOR = 0;
constexpr int VERSION_PATCH = 0;

/**
 * Get the library version string.
 */
inline const char* get_version() {
    return VERSION;
}

/**
 * Convenience namespace alias for commonly used types.
 */
using Func = std::function<double(double)>;

} // namespace calculus

