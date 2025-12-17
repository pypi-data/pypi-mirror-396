from .classes import Parameters, GenericIndex
from typing import Literal, Tuple

from . import lib_knncolle as lib
from .classes import Parameters, GenericIndex, Builder
from .define_builder import define_builder


class KmknnParameters(Parameters):
    """Parameters for the k-means k-nearest neighbors (KMKNN) algorithm."""

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


class KmknnIndex(GenericIndex):
    """A prebuilt index for the k-means k-nearest neighbors algorithm,
    created by :py:func:`~knncolle.define_builder.define_builder` with a :py:class:`~knncolle.kmknn.KmknnParameters` instance.
    """

    def __init__(self, ptr):
        """
        Args:
            ptr:
                Address of a ``knncolle_py::WrappedPrebuilt`` containing a KMKNN search index, allocated in C++.
        """
        super().__init__(ptr)


@define_builder.register
def _define_builder_kmknn(x: KmknnParameters) -> Tuple:
    return (Builder(lib.create_kmknn_builder(x.distance)), KmknnIndex)
