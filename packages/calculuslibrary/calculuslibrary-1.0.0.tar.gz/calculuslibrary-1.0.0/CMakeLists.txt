cmake_minimum_required(VERSION 3.15...3.27)
project(calculus VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Fetch pybind11
include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG        v2.11.1
)
FetchContent_MakeAvailable(pybind11)

# Create the Python module
pybind11_add_module(_calculus_core
    src/calculus/bindings.cpp
)

# Include directories for headers
target_include_directories(_calculus_core PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/calculus
)

# Compiler warnings
if(MSVC)
    target_compile_options(_calculus_core PRIVATE /W4)
else()
    target_compile_options(_calculus_core PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Optimization for release builds
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    if(MSVC)
        target_compile_options(_calculus_core PRIVATE /O2)
    else()
        target_compile_options(_calculus_core PRIVATE -O3 -march=native)
    endif()
endif()

# Install the module
install(TARGETS _calculus_core LIBRARY DESTINATION calculus)

