project(genann_project C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED TRUE)

add_library(genann
	STATIC
	genann.c
)

target_compile_options(genann
	PUBLIC
	$<$<C_COMPILER_ID:MSVC>:/W4 /O2 /fp:fast>
	$<$<NOT:$<C_COMPILER_ID:MSVC>>:-Wall -Wextra -pedantic -O3 -ffast-math -flto -fPIC>
)
