import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .classes import Parameters, Index, GenericIndex
from .annoy import AnnoyParameters, AnnoyIndex
from .build_index import build_index
from .define_builder import define_builder
from .exhaustive import ExhaustiveParameters, ExhaustiveIndex
from .find_distance import find_distance
from .find_knn import find_knn, FindKnnResults
from .find_neighbors import find_neighbors, FindNeighborsResults
from .hnsw import HnswParameters, HnswIndex
from .kmknn import KmknnParameters, KmknnIndex
from .query_distance import query_distance
from .query_knn import query_knn, QueryKnnResults
from .query_neighbors import query_neighbors, QueryNeighborsResults
from .vptree import VptreeParameters, VptreeIndex


def includes() -> str:
    """Provides access to ``knncolle_py.h`` C++ header.

    Returns:
        Path to a directory containing the header.
    """
    import os
    import inspect
    dirname = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return os.path.join(dirname, "include")
