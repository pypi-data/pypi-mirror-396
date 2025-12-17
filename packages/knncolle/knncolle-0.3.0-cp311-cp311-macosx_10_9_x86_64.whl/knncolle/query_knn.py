from functools import singledispatch
from typing import Sequence, Optional, Union
from dataclasses import dataclass
import numpy

from .classes import Index, GenericIndex
from . import lib_knncolle as lib
from ._utils import process_num_neighbors, process_subset


@dataclass
class QueryKnnResults:
    """Results of :py:func:`~knncolle.query_knn.query_knn`.

    If ``num_neighbors`` is an integer, ``index`` and ``distance`` are both matrices.
    Each row corresponds to an observation in ``query`` and each column corresponds to one of its neighbors in ``X``.
    ``index`` contains the indices of the nearest neighbors while ``distance`` contains the distance to those neighbors.
    In each row, neighbors are guaranteed to be sorted in order of increasing distance.

    If ``num_neighbors`` is a sequence, ``index`` and ``distance`` are lists instead.
    Each list element corresponds to an observation in ``X`` and is a NumPy array containing the indices (for ``index``) or distances (for ``distance``) to the requested number of neighbors for that observation.
    For each observation, the neighbors are guaranteed to be sorted in order of increasing distance. 

    If ``get_index = False``, ``index`` is set to None.

    If ``get_distance = False``, ``distance`` is set to None.
    """
    index: Optional[numpy.ndarray]
    distance: Optional[numpy.ndarray]


@singledispatch
def query_knn(
    X: Index,
    query: numpy.ndarray,
    num_neighbors: Union[int, Sequence],
    num_threads: int = 1,
    get_index: bool = True,
    get_distance: bool = True,
    **kwargs
) -> QueryKnnResults:
    """Find the k-nearest neighbors in the search index for each observation in the query matrix.

    Args:
        X:
            A prebuilt search index.

        query:
            Matrix of coordinates for the query observations.
            This should be a double-precision row-major NumPy matrix where the rows are dimensions and columns are observations.
            The number of dimensions should be consistent with that in ``X``.

        num_neighbors:
            Number of nearest neighbors in ``X`` to identify for each observation in ``query``, i.e., k.
            This is automatically capped at the total number of observations in ``X``. 

            Alternatively, this may be a sequence of non-negative integers of length equal to the number of observations in ``query``.
            This should specify the number of neighbors to find for each observation.

        num_threads:
            Number of threads to use for the search.

        get_index:
            Whether to report the indices of each nearest neighbor.

        get_distance:
            Whether to report the distances to each nearest neighbor.

        kwargs:
            Additional arguments to pass to specific methods.

    Returns:
        Results of the nearest-neighbor search.
    """
    raise NotImplementedError("no available method for '" + str(type(X)) + "'")


@query_knn.register
def _query_knn_generic(
    X: GenericIndex,
    query: numpy.ndarray,
    num_neighbors: Union[int, Sequence],
    num_threads: int = 1,
    get_index: bool = True,
    get_distance: bool = True,
    **kwargs
) -> QueryKnnResults:
    num_neighbors, force_variable = process_num_neighbors(num_neighbors)
    idx, dist = lib.generic_query_knn(
        X.ptr, 
        query,
        num_neighbors,
        force_variable,
        num_threads, 
        False,
        get_index,
        get_distance
    )
    return QueryKnnResults(index = idx, distance = dist)
