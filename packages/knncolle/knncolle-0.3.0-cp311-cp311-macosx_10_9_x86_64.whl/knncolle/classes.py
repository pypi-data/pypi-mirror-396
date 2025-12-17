from abc import ABC
from . import lib_knncolle as lib


class Parameters(ABC):
    """Abstract base class for the parameters of a nearest neighbor search.
    Each search algorithm should implement a subclass that contains the relevant parameters for controlling index construction or search."""
    pass


class Builder:
    """Pointer to a search index builder, i.e., ``knncolle_py::WrappedBuilder``, for use in C++ to build new neighbor search indices.
    The associated memory is automatically freed upon garbage collection."""

    def __init__(self, ptr: int):
        """
        Args:
            ptr:
                Address of a ``knncolle_py::WrappedBuilder``.
        """
        self._ptr = ptr

    def __del__(self):
        """Frees the builder in C++."""
        lib.free_builder(self._ptr)

    @property
    def ptr(self):
        """Address of a ``knncolle_py::WrappedBuilder``, to be passed into C++ as a ``uintptr_t``; see ``knncolle_py.h`` for details."""
        return self._ptr


class Index(ABC):
    """Abstract base class for a prebuilt nearest neighbor-search index.
    Each search algorithm should implement their own subclasses, but are free to use any data structure to represent their search indices."""
    pass


class GenericIndex(Index):
    """Abstract base class for a prebuilt nearest neighbor-search index that holds an address to a ``knncolle_py::WrappedPrebuilt`` instance in C++.
    The associated memory is automatically freed upon garbage collection."""

    def __init__(self, ptr: int):
        """
        Args:
            ptr:
                Address of a ``knncolle_py::WrappedPrebuilt``.
        """
        self._ptr = ptr

    @property
    def ptr(self) -> int:
        """Address of a ``knncolle_py::WrappedPrebuilt``, to be passed into C++ as a ``uintptr_t``; see ``knncolle_py.h`` for details."""
        return self._ptr

    def __del__(self):
        """Frees the index in C++."""
        lib.free_prebuilt(self._ptr)

    def num_observations(self) -> int:
        """
        Returns:
            Number of observations in this index.
        """
        return lib.generic_num_obs(self._ptr)

    def num_dimensions(self) -> int:
        """
        Returns:
            Number of dimensions in this index.
        """
        return lib.generic_num_dims(self._ptr)
