from functools import singledispatch
from typing import Sequence, Optional, Union
from dataclasses import dataclass
import numpy

from .classes import Index, GenericIndex
from . import lib_knncolle as lib
from ._utils import process_num_neighbors, process_subset


@dataclass
class FindKnnResults:
    """Results of :py:func:`~knncolle.find_knn.find_knn`.

    If ``num_neighbors`` is an integer, ``index`` and ``distance`` are both matrices.
    Each row corresponds to an observation in ``X`` and each column corresponds to one of its neighbors.
    ``index`` contains the indices of the nearest neighbors while ``distance`` contains the distance to those neighbors.
    In each row, neighbors are guaranteed to be sorted in order of increasing distance.
    Each row of ``index`` is guaranteed to not contain the index of the corresponding observation.

    If ``num_neighbors`` is a sequence, ``index`` and ``distance`` are instead lists.
    Each list element corresponds to an observation in ``X`` and is a NumPy array containing the indices (for ``index``) or distances (for ``distance``) to the requested number of neighbors for that observation.
    For each observation, the neighbors are guaranteed to be sorted in order of increasing distance.
    Each element of ``index`` is guaranteed to not contain the index of the corresponding observation.

    If ``get_index = False``, ``index`` is set to None.

    If ``get_distance = False``, ``distance`` is set to None.

    If ``subset`` is provided, the number of rows in ``index`` and ``distance`` (if ``num_neighbors`` is an integer) or their length (otherwise) is instead equal to the length of the subset.
    Each row or list entry corresponds to one of the observations in the subset.
    """
    index: Optional[numpy.ndarray]
    distance: Optional[numpy.ndarray]


@singledispatch
def find_knn(
    X: Index,
    num_neighbors: Union[int, Sequence],
    num_threads: int = 1,
    subset: Optional[Sequence] = None, 
    get_index: bool = True,
    get_distance: bool = True,
    **kwargs
) -> FindKnnResults:
    """Find the k-nearest neighbors for each observation.

    Args:
        X:
            A prebuilt search index.

        num_neighbors:
            Number of nearest neighbors to identify for each observation in ``X``.
            This is automatically capped at the number of observations minus 1.

            Alternatively, this may be a sequence of non-negative integers of length equal to the number of observations in ``X``.
            Each element specifies the number of neighbors to find for each observation.

            If ``subset`` is supplied and ``num_neighbors`` is a sequence, it should have length equal to ``subset`` instead.
            Each element should specify the number of neighbors for each observation in the subset.

        num_threads:
            Number of threads to use for the search.

        subset:
            Sequence of integers containing the indices of the observations for which to identify neighbors.
            All indices should be non-negative and less than the total number of observations.

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


@find_knn.register
def _find_knn_generic(
    X: GenericIndex,
    num_neighbors: Union[int, Sequence],
    num_threads: int = 1,
    subset: Optional[Sequence] = None,
    get_index: bool = True,
    get_distance: bool = True,
    **kwargs
) -> FindKnnResults:
    num_neighbors, force_variable = process_num_neighbors(num_neighbors)
    idx, dist = lib.generic_find_knn(
        X.ptr, 
        num_neighbors,
        force_variable,
        process_subset(subset), 
        num_threads, 
        False,
        get_index,
        get_distance
    )
    return FindKnnResults(index = idx, distance = dist)
