import knncolle
import numpy
import pytest


def test_query_distance_basic():
    Y = numpy.random.rand(500, 20)
    q = numpy.random.rand(100, 20)

    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    dist = knncolle.query_distance(idx, q, num_neighbors=8)
    ref = knncolle.query_knn(idx, q, num_neighbors=8)
    assert (dist == ref.distance[:,7]).all()

    # Respects alternative methods.
    idx2 = knncolle.build_index(knncolle.AnnoyParameters(), Y)
    dist2 = knncolle.query_distance(idx2, q, num_neighbors=8)
    assert (dist != dist2).any()

    with pytest.raises(Exception, match='dimensionality'):
        knncolle.query_distance(idx, q[:,1:10], num_neighbors=8)


def test_query_distance_parallel():
    Y = numpy.random.rand(500, 20)
    q = numpy.random.rand(100, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    dist = knncolle.query_distance(idx, q, num_neighbors=8)
    pdist = knncolle.query_distance(idx, q, num_neighbors=8, num_threads=2)
    assert (dist == pdist).all()


def test_query_distance_variable_k():
    Y = numpy.random.rand(500, 20)
    q = numpy.random.rand(100, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)

    with pytest.raises(Exception, match='must be equal'):
        knncolle.query_distance(idx, q, num_neighbors=[1, 1000])

    k = numpy.tile([4,10], 50)
    out = knncolle.query_distance(idx, q, num_neighbors=k)

    keep = numpy.where(k == 4)[0]
    ref = knncolle.query_distance(idx, q, num_neighbors=4)
    assert (ref[keep] == out[keep]).all()

    keep = numpy.where(k == 10)[0]
    ref = knncolle.query_distance(idx, q, num_neighbors=10)
    assert (ref[keep] == out[keep]).all()
