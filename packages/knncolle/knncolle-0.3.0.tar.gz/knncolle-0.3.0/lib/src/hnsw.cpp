#include "knncolle_py.h"
#include "pybind11/pybind11.h"

#include <string>
#include <cstdint>
#include <memory>

#include "knncolle_hnsw/knncolle_hnsw.hpp"

std::uintptr_t create_hnsw_builder(int nlinks, int ef_construct, int ef_search, std::string distance) {
    knncolle_hnsw::HnswOptions opt;
    opt.num_links = nlinks;
    opt.ef_construction = ef_construct;
    opt.ef_search = ef_search;
    auto tmp = std::make_unique<knncolle_py::WrappedBuilder>();

    if (distance == "Manhattan") {
        tmp->ptr.reset(
            new knncolle_hnsw::HnswBuilder<knncolle_py::Index, knncolle_py::MatrixValue, knncolle_py::Distance>(
                knncolle_hnsw::makeManhattanDistanceConfig(),
                opt
            )
        );

    } else if (distance == "Euclidean") {
        tmp->ptr.reset(
            new knncolle_hnsw::HnswBuilder<knncolle_py::Index, knncolle_py::MatrixValue, knncolle_py::Distance>(
                knncolle_hnsw::makeEuclideanDistanceConfig(),
                opt
            )
        );

    } else if (distance == "Cosine") {
        tmp->ptr.reset(
            new knncolle::L2NormalizedBuilder<knncolle_py::Index, knncolle_py::MatrixValue, knncolle_py::Distance, knncolle_py::MatrixValue>(
                std::make_shared<knncolle_hnsw::HnswBuilder<knncolle_py::Index, knncolle_py::MatrixValue, knncolle_py::Distance> >(
                    knncolle_hnsw::makeEuclideanDistanceConfig(),
                    opt
                )
            )
        );

    } else {
        throw std::runtime_error("unknown distance type '" + distance + "'");
    }

    return reinterpret_cast<uintptr_t>(static_cast<void*>(tmp.release()));
}

void init_hnsw(pybind11::module& m) {
    m.def("create_hnsw_builder", &create_hnsw_builder);
}
