from functools import singledispatch
from typing import Sequence, Optional, Union
from dataclasses import dataclass
import numpy

from .classes import Index, GenericIndex
from . import lib_knncolle as lib
from ._utils import process_threshold, process_subset


@dataclass
class QueryNeighborsResults:
    """Results of :py:func:`~knncolle.query_neighbors.query_neighbors`.

    ``index`` and ``distance`` are lists where each element is a NumPy array that corresponds to an observation in ``query``.
    Each array contains the indices of (for ``index``) or distances to (for ``distance``) the observations of ``X`` that neighbor the corresponding observation within the specified threshold distance.
    For each query observation, neighbors are guaranteed to be sorted in order of increasing distance. 

    If ``get_index = False``, ``index`` is set to None.

    If ``get_distance = False``, ``distance`` is set to None.
    """
    index: Optional[list]
    distance: Optional[list]


@singledispatch
def query_neighbors(
    X: Index,
    threshold: Union[float, Sequence],
    num_threads: int = 1,
    subset: Optional[Sequence] = None, 
    get_index: bool = True,
    get_distance: bool = True,
    **kwargs
) -> QueryNeighborsResults:
    """Find all observations in the search index that lie within a threshold distance of each observation in the query dataset.

    Args:
        X:
            A prebuilt search index.

        query:
            Matrix of coordinates for the query observations.
            This should be a double-precision row-major NumPy matrix where the rows are dimensions and columns are observations.
            The number of dimensions should be consistent with that in ``X``.

        threshold:
            Distance threshold at which to identify neighbors for each observation in ``X``. 

            Alternatively, this may be a sequence of non-negative floats of length equal to the number of observations in ``X``, specifying the distance threshold to search for each observation.

        num_threads:
            Number of threads to use for the search.

        get_index:
            Whether to report the indices of each nearest neighbor.

        get_distance:
            Whether to report the distances to each nearest neighbor.

        kwargs:
            Additional arguments to pass to specific methods.

    Returns:
        Results of the neighbor search.
    """
    raise NotImplementedError("no available method for '" + str(type(X)) + "'")


@query_neighbors.register
def _query_neighbors_generic(
    X: GenericIndex,
    query: numpy.ndarray,
    threshold: Union[float, Sequence],
    num_threads: int = 1,
    get_index: bool = True,
    get_distance: bool = True,
    **kwargs
) -> QueryNeighborsResults:
    idx, dist = lib.generic_query_all(
        X.ptr, 
        query,
        process_threshold(threshold),
        num_threads, 
        get_index,
        get_distance
    )
    return QueryNeighborsResults(index = idx, distance = dist)
