#ifndef KNNCOLLE_PY_H
#define KNNCOLLE_PY_H

#include <cstdint>
#include <memory>
#include "knncolle/knncolle.hpp"

namespace knncolle_py {

/**
 * Type of the indices.
 */
typedef std::uint32_t Index;

/**
 * Type of the distances.
 */
typedef double Distance;

/**
 * Type of the input matrix data.
 */
typedef double MatrixValue;

/**
 * Type for the matrix inputs into the **knncolle** interface.
 * Indices are unsigned 32-bit points while values are double-precision.
 */
typedef knncolle::Matrix<Index, MatrixValue> Matrix;

/**
 * @brief Wrapper for the builder factory.
 */
struct WrappedBuilder {
    /**
     * Pointer to an algorithm-specific `knncolle::Builder`.
     */
    std::shared_ptr<knncolle::Builder<Index, MatrixValue, Distance> > ptr;
};

/**
 * @param ptr Stored pointer to a `WrappedBuilder`.
 * @return Pointer to a `WrappedBuilder`.
 */
inline const WrappedBuilder* cast_builder(uintptr_t ptr) {
    return static_cast<const WrappedBuilder*>(reinterpret_cast<void*>(ptr));
}

/**
 * @brief Wrapper for a prebuilt search index.
 */
struct WrappedPrebuilt {
    /**
     * Pointer to a `knncolle::Prebuilt` containing a prebuilt search index.
     */
    std::shared_ptr<knncolle::Prebuilt<Index, MatrixValue, Distance> > ptr;
};

/**
 * @param ptr Stored pointer to a `WrappedPrebuilt`.
 * @return Pointer to a `WrappedPrebuilt`.
 */
inline const WrappedPrebuilt* cast_prebuilt(uintptr_t ptr) {
    return static_cast<const WrappedPrebuilt*>(reinterpret_cast<void*>(ptr));
}

}

#endif
