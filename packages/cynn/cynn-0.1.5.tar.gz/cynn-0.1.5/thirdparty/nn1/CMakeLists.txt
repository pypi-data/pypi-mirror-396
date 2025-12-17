project(nn1_project C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED TRUE)

add_library(nn1
	STATIC
	cnn.c
)

target_compile_options(nn1
	PUBLIC
	$<$<C_COMPILER_ID:MSVC>:/W4 /O2 /fp:fast>
	$<$<NOT:$<C_COMPILER_ID:MSVC>>:-Wall -Wextra -pedantic -O3 -ffast-math -flto -fPIC>
)

# Add math library for exp, tanh, etc. (not needed on Windows)
if(NOT WIN32)
	target_link_libraries(nn1 PUBLIC m)
endif()
