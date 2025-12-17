from functools import singledispatch
import numpy

from .classes import Parameters, Index
from .define_builder import define_builder
from . import lib_knncolle as lib


@singledispatch
def build_index(param: Parameters, x: numpy.ndarray, **kwargs) -> Index:
    """
    Build a search index for a given nearest neighbor search algorithm.
    The default method calls :py:func:`~knncolle.define_builder.define_builder` to obtain an algorithm-specific factory that builds the index from ``x``. 

    Args:
        param:
            Parameters for a particular search algorithm.

        x:
            Matrix of coordinates for the observations to be searched.
            This should be a double-precision row-major NumPy matrix where the rows are observations and columns are dimensions.

        kwargs:
            Additional arguments to be passed to individual methods.

    Returns:
        Instance of a :py:class:`~knncolle.classes.Index` subclass.
    """
    builder, cls = define_builder(param)
    prebuilt = lib.generic_build(builder.ptr, x)
    return cls(prebuilt)
