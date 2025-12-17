#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"
#include "pybind11/stl.h"

void init_annoy(pybind11::module&);
void init_exhaustive(pybind11::module&);
void init_generics(pybind11::module&);
void init_hnsw(pybind11::module&);
void init_kmknn(pybind11::module&);
void init_vptree(pybind11::module&);

PYBIND11_MODULE(lib_knncolle, m) {
    init_annoy(m);
    init_exhaustive(m);
    init_generics(m);
    init_hnsw(m);
    init_kmknn(m);
    init_vptree(m);
}
