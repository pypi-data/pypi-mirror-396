<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/knncolle.svg?branch=main)](https://cirrus-ci.com/github/<USER>/knncolle)
[![ReadTheDocs](https://readthedocs.org/projects/knncolle/badge/?version=latest)](https://knncolle.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/knncolle/main.svg)](https://coveralls.io/r/<USER>/knncolle)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/knncolle.svg)](https://anaconda.org/conda-forge/knncolle)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/knncolle)
-->

[![PyPI-Server](https://img.shields.io/pypi/v/knncolle.svg)](https://pypi.org/project/knncolle/)
[![Monthly Downloads](https://static.pepy.tech/badge/knncolle/month)](https://pepy.tech/project/knncolle)
![Unit tests](https://github.com/knncolle/knncolle-py/actions/workflows/pypi-test.yml/badge.svg)

# Python bindings to knncolle

## Overview

The **knncolle** Python package implements Python bindings to the [C++ library of the same name](https://github.com/knncolle) for nearest neighbor (NN) searches.
Downstream packages can re-use the NN search algorithms in **knncolle**, either via Python or by directly calling C++ through shared pointers.
This is inspired by the [**BiocNeighbors** Bioconductor package](https://bioconductor/packages/BiocNeighbors), which does the same thing for R packages.

## Quick start

Install it:

```shell
pip install knncolle
```

And run the desired search:

```python
# Mocking up data with 20 dimensions, 1000 observations
import numpy
y = numpy.random.rand(1000, 20) 

# Building a search index with vantage point trees:
import knncolle
params = knncolle.VptreeParameters()
idx = knncolle.build_index(params, y)

# Performing the search:
res = knncolle.find_knn(idx, num_neighbors=10)

res.index # each row is an observation, each column is a neighbor
## array([[881,  74, 959, ..., 917, 385, 522],
##        [586,   8, 874, ..., 895,  52, 591],
##        [290, 215, 298, ..., 148, 627, 443],
##        ...,
##        [773,  44, 669, ..., 775, 287, 819],
##        [658, 847, 691, ..., 630, 861, 434],
##        [796, 158,  11, ..., 606, 815, 882]],
##       shape=(1000, 10), dtype=uint32)

res.distance # distances to the neighbors in 'index'
## array([[1.12512471, 1.12792771, 1.15229055, ..., 1.21499808, 1.2176659 ,
##         1.23952456],
##        [0.9988856 , 1.03782045, 1.08870223, ..., 1.16899062, 1.17007634,
##         1.17147675],
##        [1.2471501 , 1.26328659, 1.2643019 , ..., 1.32229768, 1.32679721,
##         1.33451926],
##        ...,
##        [1.05765983, 1.08981287, 1.11295647, ..., 1.18395012, 1.1976068 ,
##         1.21577234],
##        [0.96758957, 1.02363497, 1.05326212, ..., 1.21518925, 1.22847612,
##         1.24106054],
##        [1.17846147, 1.22299985, 1.2248128 , ..., 1.35088373, 1.39274142,
##         1.40207528]], shape=(1000, 10))
```

Check out the [reference documentation](https://knncolle.github.io/knncolle-py) for details.

## Switching algorithms

We can easily switch to a different NN search algorithm by supplying a different `params` object.
For example, we could use the [Approximate Nearest Neighbors Oh Yeah](https://github.com/spotify/annoy) (Annoy) algorithm:

```python
an_params = knncolle.AnnoyParameters()
an_idx = knncolle.build_index(an_params, y)
```

We can also tweak the search parameters in our `Parameters` object during or after its construction.
For example, with the [hierarchical navigable small worlds](https://github.com/nmslib/hnswlib) (HNSW) algorithm:

```python
h_params = knncolle.HnswParameters(num_links=20, distance="Manhattan")
h_params.ef_construction = 150
h_idx = knncolle.build_index(h_params, y)
```

Currently, we support Annoy, HNSW, vantage point trees, k-means k-nearest neighbors, and an exhaustive brute-force search.
More algorithms can be added by extending **knncolle** as described [below](#extending-to-more-algorithms) without any change to end-user code.

## Other searches 

Given a separate query dataset of the same dimensionality, we can find the nearest neighbors in the prebuilt NN search index:

```python
q = numpy.random.rand(50, 20)
qres = knncolle.query_knn(idx, q, num_neighbors=10)

qres.index.shape # each row is an observation in 'q'
## (50, 10)
qres.distance.shape
## (50, 10)

qres.index[0,:]
## array([712, 947, 924, 506, 640, 228, 424, 662, 299, 473], dtype=uint32)

qres.distance[0,:]
## array([0.9846863 , 0.99493741, 1.01642662, 1.02303339, 1.02915264,
##        1.05241022, 1.0690309 , 1.09889404, 1.1327715 , 1.14832321])
```

We can ask `find_knn()` to report variable numbers of neighbors for each observation:

```python
variable_k = (numpy.random.rand(y.shape[0]) * 10).astype(numpy.uint32)
var_res = knncolle.find_knn(idx, num_neighbors=variable_k)

len(var_res.index)
## 1000

len(var_res.distance)
## 1000

variable_k[0]
## np.uint32(7)

var_res.index[0]
## array([881,  74, 959, 135, 148, 946, 276], dtype=uint32)

var_res.distance[0]
## array([1.12512471, 1.12792771, 1.15229055, 1.16210922, 1.19067866,
##        1.19773984, 1.21375003])
```

We can find all observations within a distance threshold of each observation via `find_neighbors()`.
The related `query_neighbors()` function handles querying of observations in a separate dataset.
Both functions also accept a variable threshold for each observation.

```python
range_res = knncolle.find_neighbors(idx, threshold=1.2)

len(range_res.index)
## 1000

len(range_res.distance)
## 1000

range_res.index[0]
## array([881,  74, 959, 135, 148, 946], dtype=uint32)

range_res.distance[0]
## array([1.12512471, 1.12792771, 1.15229055, 1.16210922, 1.19067866,
##        1.19773984])
```

## Use with C++

The raison d'être of the **knncolle** Python package is to facilitate the re-use of the neighbor search algorithms by C++ code in other Python packages.
The idea is that downstream packages will link against the **knncolle** C++ interface so that they can re-use the search indices created by the **knncolle** Python package.
This allows developers to (i) save time by avoiding the need to re-compile all desired algorithms and (ii) support more algorithms in extensions to the **knncolle** framework.
To do so:

1. Add `knncolle.includes()` and `assorthead.includes()` to the compiler's include path for the package.
This can be done through `include_dirs=` of the `Extension()` definition in `setup.py`
or by adding a `target_include_directories()` in CMake, depending on the build system.
2. Call `knncolle.build_index()` to construct a `GenericIndex` instance.
This exposes a shared pointer to the C++-allocated index via its `ptr` property.
3. Pass `ptr` to C++ code as a `uintptr_t` referencing a `knncolle::Prebuilt`.
which can be interrogated as described in the [**knncolle** documentation](https://github.com/knncolle/knncolle).

So, for example, the C++ code in our downstream package might look like this:

```cpp
#include "knncolle_py.h"

int do_something(uintptr_t ptr) {
    const auto& prebuilt = knncolle_py::cast_prebuilt(ptr)->ptr;
    // Do something with the search index interface.
    return 1;
}

PYBIND11_MODULE(lib_downstream, m) {
    m.def("do_something", &do_something);
}
```

Which can then be called from Python:

```python
from . import lib_downstream as lib
from knncolle import GenericIndex

def do_something(idx: GenericIndex):
    return lib.do_something(idx.ptr)
```

In some scenarios, it may be more convenient to construct the search index inside C++,
e.g., if the dataset to be searched is not available before the call to the C++ function.
This can be accommodated by accepting a `uintptr_t` to a `knncolle::Builder` in the C++ code:

```cpp
#include "knncolle_py.h"

int do_something_mk2(uintptr_t ptr) {
    const auto& builder = knncolle_py::cast_builder(ptr)->ptr;
    // The builder is a algorithm-specific factory that accepts a matrix and
    // returns a search index for that algorithm. Presumably we construct a
    // new search index inside this function and use it.
    return 1;
}

PYBIND11_MODULE(lib_downstream, m) {
    m.def("do_something_mk2", &do_something_mk2);
}
```

A pointer to the `knncolle::Builder` can be created by the `define_builder()` function in Python, and then passed to the C++ code:

```python
from . import lib_downstream as lib
from knncolle import define_builder, Parameters

def do_something(param: Parameters):
    builder, cls = define_builder(param)
    return lib.do_something_mk2(builder.ptr)
```

Check out [the included header](src/knncolle/include/knncolle_py.h) for more definitions.

## Extending to more algorithms

### Via `define_builder()`

The best way to extend **knncolle** is to do so in C++.
This involves writing subclasses of the interfaces in the [**knncolle**](https://github.com/knncolle/knncolle) library.
Once this is done, it is a simple matter of writing the following Python bindings:

- Implement a `SomeNewParameters` class that inherits from `Parameters`.
- Implement a `SomeNewIndex` class that inherits from `GenericIndex`.
  This should accept a single `ptr` in its constructor and have a `ptr` property that returns the same value.
- Register a `define_builder()` method that dispatches on `SomeNewParameters`.
  This should call into C++ and return a tuple containing a `Builder` object and the `SomeNewIndex` constructor.

No new methods are required for `find_knn()`, `build_index()`, etc. as the default method will work automatically if a `define_builder()` method is available.
This approach also allows the new method to be used in C++ code of downstream packages. 

### Without `define_builder()`

If it is not possible to implement the search algorithm in C++, we can still extend **knncolle** in Python.
Each extension package should:

- Implement a `SomeNewParameters` class that inherits from `Parameters`.
- Implement a `SomeNewIndex` class that inherits from `Index`.
  This can have an arbitrary structure, i.e., it does not need to have a `ptr` property.
- Register a `build_index()` method that dispatches on `SomeNewParameters`.
  This should return an instance of `SomeNewIndex`.
- Register a method for any number of these generics: `find_knn()`, `find_distance()`, `find_neighbors()`, `query_knn()`, `query_distance()`, `query_neighbors()`.
  These methods should dispatch on `SomeNewParameters` and return the appropriate result object.

This approach will not support re-use by C++ code in other Python packages.
