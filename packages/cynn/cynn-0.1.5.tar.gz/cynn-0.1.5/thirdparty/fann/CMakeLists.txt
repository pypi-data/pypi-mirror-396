cmake_minimum_required (VERSION 3.10)

project (FANN C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED TRUE)

# Configure config.h
set(FANN_VERSION_MAJOR 2)
set(FANN_VERSION_MINOR 2)
set(FANN_VERSION_PATCH 0)
configure_file (cmake/config.h.in ${CMAKE_CURRENT_BINARY_DIR}/src/include/config.h)

# Disable parallel FANN to avoid OpenMP dependency
add_definitions(-DDISABLE_PARALLEL_FANN)
add_definitions(-D_REENTRANT)

# Disable DLL mode on Windows (we're building a static library)
if(WIN32)
    add_definitions(-DFANN_NO_DLL)
endif()

# Build static floatfann library
include_directories(src/include ${CMAKE_CURRENT_BINARY_DIR}/src/include/)

add_library(floatfann STATIC src/floatfann.c)

target_compile_options(floatfann
    PUBLIC
    $<$<C_COMPILER_ID:MSVC>:/W3 /O2>
    $<$<NOT:$<C_COMPILER_ID:MSVC>>:-Wall -Wextra -O3 -fPIC>
)

if (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    target_compile_options(floatfann PUBLIC -Wno-deprecated)
endif()
