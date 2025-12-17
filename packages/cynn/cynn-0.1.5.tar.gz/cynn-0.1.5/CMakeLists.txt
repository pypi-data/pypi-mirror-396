cmake_minimum_required(VERSION 3.15...3.27)

project(cynn_project LANGUAGES C)

find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED
)

add_subdirectory(thirdparty)
add_subdirectory(src)