from .classes import Parameters, GenericIndex
from typing import Literal, Tuple

from . import lib_knncolle as lib
from .classes import Parameters, GenericIndex, Builder
from .define_builder import define_builder


class ExhaustiveParameters(Parameters):
    """Parameters for an exhaustive search. """

    def __init__(
        self,
        distance: Literal["Euclidean", "Manhattan", "Cosine"] = "Euclidean",
    ):
        """
        Args:
            distance:
                Distance metric for index construction and search.
        """
        self.distance = distance

    @property
    def distance(self) -> str:
        """Distance metric, see :meth:`~__init__()`."""
        return self._distance

    @distance.setter
    def distance(self, distance: str):
        """
        Args:
            distance:
                Distance metric, see :meth:`~__init__()`.
        """
        if distance not in ["Euclidean", "Manhattan", "Cosine"]:
            raise ValueError("unsupported 'distance'")
        self._distance = distance


class ExhaustiveIndex(GenericIndex):
    """A prebuilt index for an exhaustive search, created by :py:func:`~knncolle.define_builder.define_builder` with a :py:class:`~knncolle.exhaustive.ExhaustiveParameters` instance."""

    def __init__(self, ptr):
        """
        Args:
            ptr:
                Address of a ``knncolle_py::WrappedPrebuilt`` containing an exhaustive search index, allocated in C++.
        """
        super().__init__(ptr)


@define_builder.register
def _define_builder_exhaustive(x: ExhaustiveParameters) -> Tuple:
    return (Builder(lib.create_exhaustive_builder(x.distance)), ExhaustiveIndex)
