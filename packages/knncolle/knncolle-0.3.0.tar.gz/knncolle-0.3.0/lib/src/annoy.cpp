#include "knncolle_py.h"
#include "pybind11/pybind11.h"

#include <memory>
#include <stdexcept>
#include <cstdint>
#include <string>

#include "knncolle_annoy/knncolle_annoy.hpp"

std::uintptr_t create_annoy_builder(int num_trees, double search_mult, std::string distance) {
    knncolle_annoy::AnnoyOptions opt;
    opt.num_trees = num_trees;
    opt.search_mult = search_mult;
    auto tmp = std::make_unique<knncolle_py::WrappedBuilder>();

    if (distance == "Manhattan") {
        tmp->ptr.reset(new knncolle_annoy::AnnoyBuilder<knncolle_py::Index, knncolle_py::MatrixValue, knncolle_py::Distance, Annoy::Manhattan>(opt));

    } else if (distance == "Euclidean") {
        tmp->ptr.reset(new knncolle_annoy::AnnoyBuilder<knncolle_py::Index, knncolle_py::MatrixValue, knncolle_py::Distance, Annoy::Euclidean>(opt));

    } else if (distance == "Cosine") {
        tmp->ptr.reset(
            new knncolle::L2NormalizedBuilder<knncolle_py::Index, knncolle_py::MatrixValue, knncolle_py::Distance, knncolle_py::MatrixValue>(
                std::make_shared<knncolle_annoy::AnnoyBuilder<knncolle_py::Index, knncolle_py::MatrixValue, knncolle_py::Distance, Annoy::Euclidean> >(opt)
            )
        );

    } else {
        throw std::runtime_error("unknown distance type '" + distance + "'");
    }

    return reinterpret_cast<std::uintptr_t>(static_cast<void*>(tmp.release()));
}

void init_annoy(pybind11::module& m) {
    m.def("create_annoy_builder", &create_annoy_builder);
}
