#include "knncolle_py.h"

#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"
#include "pybind11/stl.h"

#include "sanisizer/sanisizer.hpp"

#include <algorithm>
#include <cstdint>
#include <optional>
#include <memory>
#include <stdexcept>
#include <vector>

typedef pybind11::array_t<knncolle_py::MatrixValue, pybind11::array::c_style | pybind11::array::forcecast> DataMatrix;

void free_builder(std::uintptr_t builder_ptr) {
    delete knncolle_py::cast_builder(builder_ptr);
}

std::uintptr_t generic_build(std::uintptr_t builder_ptr, const DataMatrix& data) {
    auto buffer = data.request();

    // All input NumPy matrices are row-major layouts with observations in rows,
    // which is trivially transposed to give us the expected column-major layout with observations in columns.
    const auto nobs = sanisizer::cast<knncolle_py::Index>(buffer.shape[0]);
    const auto ndim = sanisizer::cast<knncolle_py::Index>(buffer.shape[1]);

    auto builder = knncolle_py::cast_builder(builder_ptr);
    auto tmp = std::make_unique<knncolle_py::WrappedPrebuilt>();
    tmp->ptr.reset(builder->ptr->build_raw(knncolle::SimpleMatrix(ndim, nobs, static_cast<const knncolle_py::MatrixValue*>(buffer.ptr))));

    return reinterpret_cast<std::uintptr_t>(static_cast<void*>(tmp.release()));
}

void free_prebuilt(std::uintptr_t prebuilt_ptr) {
    delete knncolle_py::cast_prebuilt(prebuilt_ptr);
}

knncolle_py::Index generic_num_obs(std::uintptr_t prebuilt_ptr) {
    const auto& prebuilt = knncolle_py::cast_prebuilt(prebuilt_ptr)->ptr;
    return prebuilt->num_observations();
}

knncolle_py::Index generic_num_dims(std::uintptr_t prebuilt_ptr) {
    const auto& prebuilt = knncolle_py::cast_prebuilt(prebuilt_ptr)->ptr;
    return prebuilt->num_dimensions();
}

/*********************************
 ********* KNN functions *********
 *********************************/

template<typename Value_>
using OutputMatrix = pybind11::array_t<Value_, pybind11::array::c_style>;

template<typename Input_>
using I = std::remove_reference_t<std::remove_cv_t<Input_> >;

template<typename Value_>
Value_* prepare_output(OutputMatrix<Value_>& mat, const bool report, knncolle_py::Index k, knncolle_py::Index nobs) {
    if (report) {
        mat = OutputMatrix<Value_>({ nobs, k });
        return static_cast<Value_*>(mat.request().ptr);
    } else {
        return NULL;
    }
}

template<typename Value_>
pybind11::list format_range_output(const std::vector<std::vector<Value_> >& results) {
    const auto num = results.size();
    auto output = sanisizer::create<pybind11::list>(num);
    for (I<decltype(num)> r = 0; r < num; ++r) {
        output[r] = pybind11::array_t<Value_>(results[r].size(), results[r].data());
    }
    return output;
}

typedef pybind11::array_t<knncolle_py::Index, pybind11::array::f_style | pybind11::array::forcecast> NeighborVector;

typedef pybind11::array_t<knncolle_py::Index, pybind11::array::f_style | pybind11::array::forcecast> ChosenVector;

pybind11::object generic_find_knn(
    std::uintptr_t prebuilt_ptr,
    const NeighborVector& num_neighbors,
    const bool force_variable_neighbors,
    std::optional<ChosenVector> chosen,
    const int num_threads,
    const bool last_distance_only,
    bool report_index,
    bool report_distance
) {
    const auto& prebuilt = knncolle_py::cast_prebuilt(prebuilt_ptr)->ptr;
    const auto nobs = prebuilt->num_observations();

    // Checking if we have to handle subsets.
    auto num_output = nobs;
    const knncolle_py::Index* subset_ptr = NULL;
    if (chosen.has_value()) {
        const auto& subset = *chosen;
        num_output = subset.size();

        for (I<decltype(num_output)> i = 0; i < num_output; ++i) {
            const auto s = subset.at(i);
            if (s >= nobs) { // no need to check for negatives, as the index is unsigned. 
                throw std::runtime_error("'subset' contains out-of-range indices");
            } 
        }
        subset_ptr = static_cast<const knncolle_py::Index*>(subset.request().ptr);
    }

    // Checking that the 'k' is valid.
    auto sanitize_k = [&](knncolle_py::Index k) -> knncolle_py::Index {
        if (k < nobs) {
            return k;
        }
        //Rcpp::warning("'k' capped at the number of observations minus 1");
        if (nobs >= 1) {
            return nobs - 1;
        } else {
            return 0;
        }
    };

    bool is_k_variable = false;
    knncolle_py::Index const_k = 0;
    std::vector<knncolle_py::Index> variable_k;

    if (num_neighbors.size() != 1 || force_variable_neighbors) {
        is_k_variable = true;
        if (!sanisizer::is_equal(num_neighbors.size(), num_output)) {
            throw std::runtime_error("length of 'k' must be equal to the number of points in the index or 'subset'");
        }

        sanisizer::resize(variable_k, num_output);
        for (I<decltype(num_output)> o = 0; o < num_output; ++o) {
            variable_k[o] = sanitize_k(num_neighbors.at(o));
        }
    } else {
        const_k = sanitize_k(num_neighbors.at(0));
    }

    // Formatting all the possible output containers.
    OutputMatrix<knncolle_py::Index> const_i;
    OutputMatrix<knncolle_py::MatrixValue> const_d;
    pybind11::array_t<knncolle_py::MatrixValue> last_d;
    knncolle_py::Index* out_i_ptr = NULL; 
    knncolle_py::MatrixValue* out_d_ptr = NULL; 
    std::vector<std::vector<knncolle_py::Index> > var_i;
    std::vector<std::vector<knncolle_py::MatrixValue> > var_d;

    if (last_distance_only) {
        last_d = pybind11::array_t<knncolle_py::MatrixValue>(num_output);
        out_d_ptr = static_cast<knncolle_py::MatrixValue*>(last_d.request().ptr);
        report_index = false;
        report_distance = true;

    } else if (is_k_variable) {
        if (report_index) {
            sanisizer::resize(var_i, num_output);
        }
        if (report_distance) {
            sanisizer::resize(var_d, num_output);
        }

    } else {
        out_i_ptr = prepare_output(const_i, report_index, const_k, num_output);
        out_d_ptr = prepare_output(const_d, report_distance, const_k, num_output);
    }

    knncolle::parallelize(num_threads, num_output, [&](int, knncolle_py::Index start, knncolle_py::Index length) {
        auto searcher = prebuilt->initialize();
        std::vector<knncolle_py::Index> tmp_i;
        std::vector<knncolle_py::MatrixValue> tmp_d;

        for (knncolle_py::Index o = start, end = start + length; o < end; ++o) {
            searcher->search(
                (subset_ptr != NULL ? subset_ptr[o] : o),
                (is_k_variable ? variable_k[o] : const_k),
                (report_index ? &tmp_i : NULL),
                (report_distance ? &tmp_d : NULL)
            );

            if (report_index) {
                if (is_k_variable) {
                    var_i[o].swap(tmp_i);
                } else {
                    auto out_offset = sanisizer::product_unsafe<std::size_t>(o, const_k);
                    std::copy_n(tmp_i.begin(), const_k, out_i_ptr + out_offset); 
                }
            }

            if (report_distance) {
                if (last_distance_only) {
                    out_d_ptr[o] = (tmp_d.empty() ? 0 : tmp_d.back());
                } else if (is_k_variable) {
                    var_d[o].swap(tmp_d);
                } else {
                    auto out_offset = sanisizer::product_unsafe<std::size_t>(o, const_k);
                    std::copy_n(tmp_d.begin(), const_k, out_d_ptr + out_offset); 
                }
            }
        }
    });

    if (last_distance_only) {
        return last_d;

    } else if (is_k_variable) {
        pybind11::tuple output(2);
        if (report_index) {
            output[0] = format_range_output(var_i);
        } else {
            output[0] = pybind11::none();
        }
        if (report_distance) {
            output[1] = format_range_output(var_d);
        } else {
            output[1] = pybind11::none();
        }
        return output;

    } else {
        pybind11::tuple output(2);
        if (report_index) {
            output[0] = const_i;
        } else {
            output[0] = pybind11::none();
        }
        if (report_distance) {
            output[1] = const_d;
        } else {
            output[1] = pybind11::none();
        }
        return output;
    }
} 

pybind11::object generic_query_knn(
    std::uintptr_t prebuilt_ptr,
    const DataMatrix& query,
    const NeighborVector& num_neighbors,
    const bool force_variable_neighbors,
    const int num_threads,
    const bool last_distance_only,
    bool report_index,
    bool report_distance
) {
    const auto& prebuilt = knncolle_py::cast_prebuilt(prebuilt_ptr)->ptr;
    const auto nobs = prebuilt->num_observations();
    const auto ndim = prebuilt->num_dimensions();

    // Remember, all input NumPy matrices are row-major layouts with observations in rows.
    auto buf_info = query.request();
    const auto nquery = buf_info.shape[0];
    const auto query_ptr = static_cast<const knncolle_py::MatrixValue*>(buf_info.ptr);
    if (!sanisizer::is_equal(buf_info.shape[1], ndim)) {
        throw std::runtime_error("mismatch in dimensionality between index and 'query'");
    }

    // Checking that 'k' is valid.
    auto sanitize_k = [&](knncolle_py::Index k) -> knncolle_py::Index {
        if (k <= nobs) {
            return k;
        }
        //Rcpp::warning("'k' capped at the number of observations");
        return nobs;
    };

    bool is_k_variable = false;
    knncolle_py::Index const_k = 0;
    std::vector<knncolle_py::Index> variable_k;
    if (num_neighbors.size() != 1 || force_variable_neighbors) {
        is_k_variable = true;
        if (!sanisizer::is_equal(num_neighbors.size(), nquery)) {
            throw std::runtime_error("length of 'k' must be equal to the number of points in the index or 'subset'");
        }

        sanisizer::resize(variable_k, nquery);
        for (I<decltype(nquery)> o = 0; o < nquery; ++o) {
            variable_k[o] = sanitize_k(num_neighbors.at(o));
        }
    } else {
        const_k = sanitize_k(num_neighbors.at(0));
    }

    // Formatting all the possible output containers.
    OutputMatrix<knncolle_py::Index> const_i;
    OutputMatrix<knncolle_py::MatrixValue> const_d;
    pybind11::array_t<knncolle_py::MatrixValue> last_d;
    knncolle_py::Index* out_i_ptr = NULL; 
    knncolle_py::MatrixValue* out_d_ptr = NULL; 
    std::vector<std::vector<knncolle_py::Index> > var_i;
    std::vector<std::vector<knncolle_py::MatrixValue> > var_d;

    if (last_distance_only) {
        last_d = pybind11::array_t<knncolle_py::MatrixValue>(nquery);
        out_d_ptr = static_cast<knncolle_py::MatrixValue*>(last_d.request().ptr);
        report_index = false;
        report_distance = true;

    } else if (is_k_variable) {
        if (report_index) {
            sanisizer::resize(var_i, nquery);
        }
        if (report_distance) {
            sanisizer::resize(var_d, nquery);
        }

    } else {
        out_i_ptr = prepare_output(const_i, report_index, const_k, nquery);
        out_d_ptr = prepare_output(const_d, report_distance, const_k, nquery);
    }

    knncolle::parallelize(num_threads, nquery, [&](int, knncolle_py::Index start, knncolle_py::Index length) {
        auto searcher = prebuilt->initialize();
        std::vector<knncolle_py::Index> tmp_i;
        std::vector<knncolle_py::MatrixValue> tmp_d;

        for (knncolle_py::Index o = start, end = start + length; o < end; ++o) {
            const auto query_offset = sanisizer::product_unsafe<std::size_t>(o, ndim);
            searcher->search(
                query_ptr + query_offset,
                (is_k_variable ? variable_k[o] : const_k),
                (report_index ? &tmp_i : NULL),
                (report_distance ? &tmp_d : NULL)
            );

            if (report_index) {
                if (is_k_variable) {
                    var_i[o].swap(tmp_i);
                } else {
                    const auto out_offset = sanisizer::product_unsafe<std::size_t>(o, const_k);
                    std::copy_n(tmp_i.begin(), const_k, out_i_ptr + out_offset); 
                }
            }

            if (report_distance) {
                if (last_distance_only) {
                    out_d_ptr[o] = (tmp_d.empty() ? 0 : tmp_d.back());
                } else if (is_k_variable) {
                    var_d[o].swap(tmp_d);
                } else {
                    const auto out_offset = sanisizer::product_unsafe<std::size_t>(o, const_k);
                    std::copy_n(tmp_d.begin(), const_k, out_d_ptr + out_offset); 
                }
            }
        }
    });

    if (last_distance_only) {
        return last_d;

    } else if (is_k_variable) {
        pybind11::tuple output(2);
        if (report_index) {
            output[0] = format_range_output(var_i);
        } else {
            output[0] = pybind11::none();
        }
        if (report_distance) {
            output[1] = format_range_output(var_d);
        } else {
            output[1] = pybind11::none();
        }
        return output;

    } else {
        pybind11::tuple output(2);
        if (report_index) {
            output[0] = const_i;
        } else {
            output[0] = pybind11::none();
        }
        if (report_distance) {
            output[1] = const_d;
        } else {
            output[1] = pybind11::none();
        }
        return output;
    }
}

/***********************************
 ********* Range functions *********
 ***********************************/

typedef pybind11::array_t<knncolle_py::MatrixValue, pybind11::array::f_style | pybind11::array::forcecast> ThresholdVector;

pybind11::object generic_find_all(
    std::uintptr_t prebuilt_ptr, 
    std::optional<ChosenVector> chosen,
    const ThresholdVector& thresholds,
    const int num_threads,
    const bool report_index,
    const bool report_distance
) {
    const auto& prebuilt = knncolle_py::cast_prebuilt(prebuilt_ptr)->ptr;
    const auto nobs = prebuilt->num_observations();

    auto num_output = nobs;
    const knncolle_py::Index* subset_ptr = NULL;
    if (chosen.has_value()) {
        const auto& subset = *chosen;
        num_output = subset.size();

        for (I<decltype(num_output)> i = 0; i < num_output; ++i) {
            auto s = subset.at(i);
            if (s >= nobs) { // no need to check for negatives, index is unsigned.
                throw std::runtime_error("'subset' contains out-of-range indices");
            } 
        }

        subset_ptr = static_cast<const knncolle_py::Index*>(subset.request().ptr);
    }

    std::vector<std::vector<knncolle_py::MatrixValue> > out_d(report_distance ? num_output : 0);
    std::vector<std::vector<knncolle_py::Index> > out_i(report_index ? num_output : 0);

    const bool store_count = !report_distance && !report_index;
    pybind11::array_t<knncolle_py::Index> counts(store_count ? num_output : 0);
    const auto counts_ptr = static_cast<knncolle_py::Index*>(counts.request().ptr);

    const auto nthresholds = thresholds.size();
    const bool multiple_thresholds = (nthresholds != 1);
    if (multiple_thresholds && !sanisizer::is_equal(nthresholds, num_output)) {
        throw std::runtime_error("'threshold' should have length equal to the number of observations or 'subset'");
    }
    const auto threshold_ptr = static_cast<const knncolle_py::MatrixValue*>(thresholds.request().ptr);

    bool no_support = false;
    knncolle::parallelize(num_threads, num_output, [&](int tid, knncolle_py::Index start, knncolle_py::Index length) {
        auto searcher = prebuilt->initialize();

        if (!searcher->can_search_all()) {
            if (tid == 0) {
                no_support = true;
            }
            return;
        }

        for (knncolle_py::Index o = start, end = start + length; o < end; ++o) {
            auto count = searcher->search_all(
                (subset_ptr != NULL ? subset_ptr[o] : o),
                threshold_ptr[multiple_thresholds ? o : 0],
                (report_index ? &out_i[o] : NULL),
                (report_distance ? &out_d[o] : NULL)
            ); 
            if (store_count) {
                counts_ptr[o] = count;
            }
        }
    });

    if (no_support) {
        throw std::runtime_error("algorithm does not support search by distance");
    }

    if (store_count) {
        return counts;
    } else {
        pybind11::tuple output(2);
        if (report_index) {
            output[0] = format_range_output(out_i);
        } else {
            output[0] = pybind11::none();
        }
        if (report_distance) {
            output[1] = format_range_output(out_d);
        } else {
            output[1] = pybind11::none();
        }
        return output;
    }
} 

pybind11::object generic_query_all(
    std::uintptr_t prebuilt_ptr, 
    const DataMatrix& query,
    const ThresholdVector& thresholds,
    const int num_threads,
    const bool report_index,
    const bool report_distance
) {
    const auto& prebuilt = knncolle_py::cast_prebuilt(prebuilt_ptr)->ptr;
    const auto ndim = prebuilt->num_dimensions();

    // Remember, all input NumPy matrices are row-major layouts with observations in rows.
    auto buf_info = query.request();
    const auto nquery = sanisizer::cast<knncolle_py::Index>(buf_info.shape[0]);
    const auto query_ptr = static_cast<const knncolle_py::MatrixValue*>(buf_info.ptr);
    if (!sanisizer::is_equal(buf_info.shape[1], ndim)) {
        throw std::runtime_error("mismatch in dimensionality between index and 'query'");
    }

    std::vector<std::vector<knncolle_py::MatrixValue> > out_d(report_distance ? nquery : 0);
    std::vector<std::vector<knncolle_py::Index> > out_i(report_index ? nquery : 0);

    const bool store_count = !report_distance && !report_index;
    pybind11::array_t<knncolle_py::Index> counts(store_count ? nquery : 0);
    const auto counts_ptr = static_cast<knncolle_py::Index*>(counts.request().ptr);

    const auto nthresholds = thresholds.size();
    bool multiple_thresholds = (nthresholds != 1);
    if (multiple_thresholds && nthresholds != nquery) {
        throw std::runtime_error("'threshold' should have length equal to 'subset'");
    }
    const auto threshold_ptr = static_cast<const knncolle_py::MatrixValue*>(thresholds.request().ptr);

    bool no_support = false;
    knncolle::parallelize(num_threads, nquery, [&](int tid, knncolle_py::Index start, knncolle_py::Index length) {
        auto searcher = prebuilt->initialize();

        if (!searcher->can_search_all()) {
            if (tid == 0) {
                no_support = true;
            }
            return;
        }

        for (knncolle_py::Index o = start, end = start + length; o < end; ++o) {
            const auto current_ptr = query_ptr + sanisizer::product_unsafe<std::size_t>(o, ndim);
            auto count = searcher->search_all(
                current_ptr,
                threshold_ptr[multiple_thresholds ? o : 0],
                (report_index ? &out_i[o] : NULL),
                (report_distance ? &out_d[o] : NULL)
            ); 
            if (store_count) {
                counts_ptr[o] = count;
            }
        }
    });

    if (no_support) {
        throw std::runtime_error("algorithm does not support search by distance");
    }

    if (store_count) {
        return counts;
    } else {
        pybind11::tuple output(2);
        if (report_index) {
            output[0] = format_range_output(out_i);
        } else {
            output[0] = pybind11::none();
        }
        if (report_distance) {
            output[1] = format_range_output(out_d);
        } else {
            output[1] = pybind11::none();
        }
        return output;
    }
} 

/*********************************
 ********* Init function *********
 *********************************/

void init_generics(pybind11::module& m) {
    m.def("free_builder", &free_builder);
    m.def("generic_build", &generic_build);
    m.def("free_prebuilt", &free_prebuilt);
    m.def("generic_num_obs", &generic_num_obs);
    m.def("generic_num_dims", &generic_num_dims);
    m.def("generic_find_knn", &generic_find_knn);
    m.def("generic_query_knn", &generic_query_knn);
    m.def("generic_find_all", &generic_find_all);
    m.def("generic_query_all", &generic_query_all);
}
