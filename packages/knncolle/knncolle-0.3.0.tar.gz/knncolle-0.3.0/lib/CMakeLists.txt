cmake_minimum_required(VERSION 3.24)

project(knncolle_py
    VERSION 1.0.0
    DESCRIPTION "Building the knncolle_py shared library"
    LANGUAGES CXX)

# Defining the targets.
find_package(pybind11 CONFIG)

# pybind11 method:
pybind11_add_module(knncolle_py
    src/annoy.cpp
    src/exhaustive.cpp
    src/generics.cpp
    src/hnsw.cpp
    src/init.cpp
    src/kmknn.cpp
    src/vptree.cpp
)

target_include_directories(knncolle_py PRIVATE "${ASSORTHEAD_INCLUDE_DIR}")
target_include_directories(knncolle_py PRIVATE "../src/knncolle/include")

set_property(TARGET knncolle_py PROPERTY CXX_STANDARD 17)

target_link_libraries(knncolle_py PRIVATE pybind11::pybind11)

set_target_properties(knncolle_py PROPERTIES
    OUTPUT_NAME lib_knncolle
    PREFIX ""
)
