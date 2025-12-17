import knncolle
import numpy
import pytest


def test_find_distance_basic():
    Y = numpy.random.rand(500, 20)

    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    dist = knncolle.find_distance(idx, num_neighbors=8)
    ref = knncolle.find_knn(idx, num_neighbors=8)
    assert (dist == ref.distance[:,7]).all()

    # Respects alternative methods.
    idx2 = knncolle.build_index(knncolle.AnnoyParameters(), Y)
    dist2 = knncolle.find_distance(idx2, num_neighbors=8)
    assert (dist != dist2).any()


def test_find_distance_parallel():
    Y = numpy.random.rand(500, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    dist = knncolle.find_distance(idx, num_neighbors=8)
    pdist = knncolle.find_distance(idx, num_neighbors=8, num_threads=2)
    assert (dist == pdist).all()


def test_find_distance_subset():
    Y = numpy.random.rand(500, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    full = knncolle.find_distance(idx, num_neighbors=8)
    sub = knncolle.find_distance(idx, num_neighbors=8, subset=range(5, 20))
    assert (full[5:20] == sub).all()

    with pytest.raises(Exception, match='out-of-range'):
        knncolle.find_distance(idx, num_neighbors=8, subset=[1000])

    eidx = knncolle.build_index(knncolle.VptreeParameters(), Y[0:0,:])
    empty = knncolle.find_distance(eidx, num_neighbors=10)
    assert len(empty) == 0


def test_find_distance_variable_k():
    Y = numpy.random.rand(500, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)

    with pytest.raises(Exception, match='must be equal'):
        knncolle.find_distance(idx, num_neighbors=[1, 1000])

    k = numpy.tile([4,10], 250)
    out = knncolle.find_distance(idx, num_neighbors=k)

    keep = numpy.where(k == 4)[0]
    ref = knncolle.find_distance(idx, num_neighbors=4)
    assert (ref[keep] == out[keep]).all()

    keep = numpy.where(k == 10)[0]
    ref = knncolle.find_distance(idx, num_neighbors=10)
    assert (ref[keep] == out[keep]).all()
