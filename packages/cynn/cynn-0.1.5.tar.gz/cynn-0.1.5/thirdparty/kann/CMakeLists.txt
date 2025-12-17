# KANN - Klib Artificial Neural Network
# https://github.com/attractivechaos/kann

add_library(kann_lib STATIC
    kann.c
    kautodiff.c
    kann_extra/kann_data.c
)

target_include_directories(kann_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

target_compile_options(kann_lib
    PUBLIC
    $<$<C_COMPILER_ID:MSVC>:/O2>
    $<$<NOT:$<C_COMPILER_ID:MSVC>>:-O3 -fPIC>
)
