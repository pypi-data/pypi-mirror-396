import knncolle
import numpy
import pytest


def ref_find_knn(X, k, distance="euclidean"):
    collected_index = []
    collected_distance = []

    for i in range(X.shape[0]):
        delta = X - X[i,:]
        if distance == "euclidean":
            all_dist = numpy.sqrt((delta**2).sum(axis=1))
        else:
            all_dist = numpy.abs(delta).sum(axis=1)

        o = numpy.argsort(all_dist)
        o = o[o != i]
        keep = o if k >= len(o) else o[:k]
        collected_index.append(numpy.array(keep, dtype=numpy.uint32))
        collected_distance.append(numpy.array(all_dist[keep], dtype=numpy.float64))

    return (
        numpy.vstack(collected_index),
        numpy.vstack(collected_distance)
    )


def test_find_knn_basic():
    Y = numpy.random.rand(500, 20)

    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    out = knncolle.find_knn(idx, num_neighbors=8)
    ref_i, ref_d = ref_find_knn(Y, k=8)
    assert (ref_i == out.index).all()
    assert numpy.isclose(ref_d, out.distance).all()

    idx = knncolle.build_index(knncolle.VptreeParameters(distance="Manhattan"), Y)
    out = knncolle.find_knn(idx, num_neighbors=8)
    ref_i, ref_d = ref_find_knn(Y, k=8, distance="manhattan")
    assert (ref_i == out.index).all()
    assert numpy.isclose(ref_d, out.distance).all()

    idx = knncolle.build_index(knncolle.VptreeParameters(distance="Cosine"), Y)
    out = knncolle.find_knn(idx, num_neighbors=8)
    normed = (Y.T / numpy.sqrt((Y**2).sum(axis=1))).T
    ref_i, ref_d = ref_find_knn(normed, k=8)
    assert (ref_i == out.index).all()
    assert numpy.isclose(ref_d, out.distance).all()


def test_find_knn_parallel():
    Y = numpy.random.rand(500, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    out = knncolle.find_knn(idx, num_neighbors=8)
    pout = knncolle.find_knn(idx, num_neighbors=8, num_threads=2)
    assert (out.index == pout.index).all()
    assert (out.distance == pout.distance).all()


def test_find_knn_subset():
    Y = numpy.random.rand(500, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    full = knncolle.find_knn(idx, num_neighbors=8)

    sout = knncolle.find_knn(idx, num_neighbors=8, subset=range(0, 10))
    assert (full.index[0:10,:] == sout.index).all()
    assert (full.distance[0:10,:] == sout.distance).all()

    with pytest.raises(Exception, match='out-of-range'):
        knncolle.find_distance(idx, num_neighbors=8, subset=[1000])

    eidx = knncolle.build_index(knncolle.VptreeParameters(), Y[0:0,:])
    empty = knncolle.find_knn(eidx, num_neighbors=8)
    assert empty.index.shape[0] == 0
    assert empty.distance.shape[0] == 0


def test_find_knn_variable_k():
    Y = numpy.random.rand(500, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)

    with pytest.raises(Exception, match='must be equal'):
        knncolle.find_knn(idx, num_neighbors=[1, 1000])

    k = numpy.tile([4,10], 250)
    out = knncolle.find_knn(idx, num_neighbors=k)

    ref = knncolle.find_knn(idx, num_neighbors=4)
    for i in numpy.where(k == 4)[0]:
        assert (ref.index[i,:] == out.index[i]).all()
        assert (ref.distance[i,:] == out.distance[i]).all()

    ref = knncolle.find_knn(idx, num_neighbors=10)
    for i in numpy.where(k == 10)[0]:
        assert (ref.index[i,:] == out.index[i]).all()
        assert (ref.distance[i,:] == out.distance[i]).all()


def test_find_knn_variable_output():
    Y = numpy.random.rand(500, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    out = knncolle.find_knn(idx, num_neighbors=8)

    iout = knncolle.find_knn(idx, num_neighbors=8, get_distance=False)
    assert (iout.index == out.index).all()
    assert iout.distance is None

    dout = knncolle.find_knn(idx, num_neighbors=8, get_index=False)
    assert dout.index is None
    assert (dout.distance == out.distance).all()
