from typing import Tuple, Union, Sequence, Optional
import numpy


def process_num_neighbors(num_neighbors: Union[int, Sequence]) -> Tuple[numpy.ndarray, bool]:
    if isinstance(num_neighbors, int):
        return numpy.array([num_neighbors], dtype=numpy.uint32), False
    if not isinstance(num_neighbors, numpy.ndarray):
        num_neighbors = numpy.array(num_neighbors, dtype=numpy.uint32)
    return num_neighbors, True


def process_subset(subset: Optional[Sequence]) -> Optional[numpy.ndarray]:
    if subset is None:
        return subset
    if not isinstance(subset, numpy.ndarray):
        subset = numpy.array(subset, dtype=numpy.uint32)
    return subset


def process_threshold(threshold: Union[float, Sequence]) -> numpy.ndarray:
    if isinstance(threshold, float):
        return numpy.array([threshold], dtype=numpy.float64)
    if not isinstance(threshold, numpy.ndarray):
        threshold = numpy.array(threshold, dtype=numpy.float64)
    return threshold
