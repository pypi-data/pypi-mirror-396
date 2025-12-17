from functools import singledispatch
from typing import Tuple

from .classes import Parameters


@singledispatch
def define_builder(param: Parameters) -> Tuple:
    """
    Create a builder instance for a given nearest neighbor search algorithm.
    The builder can be used in :py:func:`~knncolle.build_index.build_index` to create a search index from a matrix of observations.

    Args:
        param:
            Parameters for a particular search algorithm.

    Returns:
        Tuple where the first element is a :py:class:`~knncolle.classes.Builder` and the second element is a :py:class:`~knncolle.classes.GenericIndex` type.
    """
    raise NotImplementedError("no available method for '" + str(type(param)) + "'")
