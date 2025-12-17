#include "knncolle_py.h"
#include "pybind11/pybind11.h"

#include <memory>
#include <stdexcept>
#include <string>
#include <cstdint>

std::uintptr_t create_vptree_builder(std::string distance) {
    auto tmp = std::make_unique<knncolle_py::WrappedBuilder>();

    if (distance == "Manhattan") {
        tmp->ptr.reset(
            new knncolle::VptreeBuilder<knncolle_py::Index, knncolle_py::MatrixValue, knncolle_py::Distance>(
                std::make_shared<knncolle::ManhattanDistance<knncolle_py::MatrixValue, knncolle_py::Distance> >()
            )
        );

    } else if (distance == "Euclidean") {
        tmp->ptr.reset(
            new knncolle::VptreeBuilder<knncolle_py::Index, knncolle_py::MatrixValue, knncolle_py::Distance>(
                std::make_shared<knncolle::EuclideanDistance<knncolle_py::MatrixValue, knncolle_py::Distance> >()
            )
        );

    } else if (distance == "Cosine") {
        tmp->ptr.reset(
            new knncolle::L2NormalizedBuilder<knncolle_py::Index, knncolle_py::MatrixValue, knncolle_py::Distance, knncolle_py::MatrixValue>(
                std::make_shared<knncolle::VptreeBuilder<knncolle_py::Index, knncolle_py::MatrixValue, knncolle_py::Distance> >(
                    std::make_shared<knncolle::EuclideanDistance<knncolle_py::MatrixValue, knncolle_py::Distance> >()
                )
            )
        );

    } else {
        throw std::runtime_error("unknown distance type '" + distance + "'");
    }

    return reinterpret_cast<std::uintptr_t>(static_cast<void*>(tmp.release()));
}

void init_vptree(pybind11::module& m) {
    m.def("create_vptree_builder", &create_vptree_builder);
}
