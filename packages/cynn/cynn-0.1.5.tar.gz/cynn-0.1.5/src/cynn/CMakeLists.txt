# tinn module
add_custom_command(
    OUTPUT tinn_module.c
    COMMAND Python::Interpreter -m cython
          "${CMAKE_CURRENT_SOURCE_DIR}/tinn.pyx" --output-file tinn_module.c
    DEPENDS tinn.pyx tinn.pxd _common.pxi
)

python_add_library(tinn_py MODULE tinn_module.c WITH_SOABI)

set_target_properties(tinn_py PROPERTIES OUTPUT_NAME "tinn")

target_link_libraries(tinn_py
    PUBLIC
    tinn
)

target_include_directories(tinn_py
    PUBLIC
    ${CMAKE_SOURCE_DIR}/thirdparty/tinn
)

install(TARGETS tinn_py DESTINATION cynn)

# genann module
add_custom_command(
    OUTPUT genann_module.c
    COMMAND Python::Interpreter -m cython
          "${CMAKE_CURRENT_SOURCE_DIR}/genann.pyx" --output-file genann_module.c
    DEPENDS genann.pyx genann.pxd _common.pxi
)

python_add_library(genann_py MODULE genann_module.c WITH_SOABI)

set_target_properties(genann_py PROPERTIES OUTPUT_NAME "genann")

target_link_libraries(genann_py
    PUBLIC
    genann
)

target_include_directories(genann_py
    PUBLIC
    ${CMAKE_SOURCE_DIR}/thirdparty/genann
)

install(TARGETS genann_py DESTINATION cynn)

# fann module (float and double)
add_custom_command(
    OUTPUT fann_module.c
    COMMAND Python::Interpreter -m cython
          "${CMAKE_CURRENT_SOURCE_DIR}/fann.pyx" --output-file fann_module.c
    DEPENDS fann.pyx ffann.pxd _common.pxi
)

python_add_library(fann_py MODULE fann_module.c WITH_SOABI)

set_target_properties(fann_py PROPERTIES OUTPUT_NAME "fann")

target_link_libraries(fann_py
    PUBLIC
    floatfann
)

target_include_directories(fann_py
    PUBLIC
    ${CMAKE_SOURCE_DIR}/thirdparty/fann
    ${CMAKE_SOURCE_DIR}/thirdparty/fann/src/include
    ${CMAKE_BINARY_DIR}/thirdparty/fann/src/include
)

# Disable DLL mode on Windows (static linking)
if(WIN32)
    target_compile_definitions(fann_py PRIVATE FANN_NO_DLL)
endif()

install(TARGETS fann_py DESTINATION cynn)

# cnn module (nn1)
add_custom_command(
    OUTPUT cnn_module.c
    COMMAND Python::Interpreter -m cython
          "${CMAKE_CURRENT_SOURCE_DIR}/cnn.pyx" --output-file cnn_module.c
    DEPENDS cnn.pyx cnn.pxd _common.pxi
)

python_add_library(cnn_py MODULE cnn_module.c WITH_SOABI)

set_target_properties(cnn_py PROPERTIES OUTPUT_NAME "cnn")

target_link_libraries(cnn_py
    PUBLIC
    nn1
)

target_include_directories(cnn_py
    PUBLIC
    ${CMAKE_SOURCE_DIR}/thirdparty/nn1
)

install(TARGETS cnn_py DESTINATION cynn)

# kann module (KANN neural network library)
add_custom_command(
    OUTPUT kann_module.c
    COMMAND Python::Interpreter -m cython
          -I "${CMAKE_CURRENT_SOURCE_DIR}"
          "${CMAKE_CURRENT_SOURCE_DIR}/kann.pyx" --output-file kann_module.c
    DEPENDS kann.pyx kann.pxd _common.pxi
)

python_add_library(kann_py MODULE kann_module.c WITH_SOABI)

set_target_properties(kann_py PROPERTIES OUTPUT_NAME "kann")

target_link_libraries(kann_py
    PUBLIC
    kann_lib
)

target_include_directories(kann_py
    PUBLIC
    ${CMAKE_SOURCE_DIR}/thirdparty/kann
)

install(TARGETS kann_py DESTINATION cynn)
