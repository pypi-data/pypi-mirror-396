from functools import singledispatch
from typing import Sequence, Optional, Union
import numpy

from .classes import Index, GenericIndex
from . import lib_knncolle as lib
from ._utils import process_num_neighbors, process_subset


@singledispatch
def find_distance(
    X: Index,
    num_neighbors: Union[int, Sequence],
    num_threads: int = 1,
    subset: Optional[Sequence] = None, 
    **kwargs
) -> numpy.ndarray:
    """Find the distance to the k-th closest point for each observation.

    Args:
        X:
            A prebuilt search index.

        num_neighbors:
            Number of nearest neighbors at which to compute the distance from each observation in ``X``, i.e., k.
            This is automatically capped at the number of observations minus 1.

            Alternatively, this may be a sequence of non-negative integers of length equal to the number of observations in ``X``.
            Each element should specify the neighbor at which to compute the distance for each observation.

            If ``subset`` is supplied and ``num_neighbors`` is a sequence, it should have length equal to ``subset`` instead.
            Each element should specify the neighbor at which to compute the distance for each observation in the subset.

        num_threads:
            Number of threads to use for the search.

        subset:
            Sequence of integers containing the indices of the observations for which to compute the distances.
            All indices should be non-negative and less than the total number of observations.

        kwargs:
            Additional arguments to pass to specific methods.

    Returns:
        A NumPy array of length equal to the number of observations in ``X`` (or ``subset``, if provided).
        Each element contains the distance to the ``num_neighbors``-th point for each observation.
    """
    raise NotImplementedError("no available method for '" + str(type(X)) + "'")


@find_distance.register
def _find_distance_generic(
    X: GenericIndex,
    num_neighbors: Union[int, Sequence],
    num_threads: int = 1,
    subset: Optional[Sequence] = None,
    **kwargs
) -> numpy.ndarray:
    num_neighbors, force_variable = process_num_neighbors(num_neighbors)
    return lib.generic_find_knn(
        X.ptr, 
        num_neighbors,
        force_variable,
        process_subset(subset), 
        num_threads, 
        True,
        False,
        False
    )
