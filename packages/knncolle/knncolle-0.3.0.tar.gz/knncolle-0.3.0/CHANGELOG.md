# Changelog

## 0.3.0

- Updated C++ bindings to use the latest **knncolle** interfaces from the **assorthead** package.
- Enabled manual vectorization in Annoy and HNSW to favor speed over inter-machine reproducibility.

## 0.2.0

- Switch to accepting row-major matrices where the observations are in the rows.
  This is for greater consistency with our own output format, NumPy's defaults, and the R package.

## 0.1.2

- Exported the various `*Results` classes.
- Fixed error message in the default `define_builder()` method.

## 0.1.1

- Cast pointers to/from `uintptr_t` so that downstream packages aren't forced to rely on **pybind10** converters.
- Added a `knncolle_py.h` header to ensure developers use the correct types during casting.

## 0.1.0

Bindings to the algorithms in the **knncolle** package.
