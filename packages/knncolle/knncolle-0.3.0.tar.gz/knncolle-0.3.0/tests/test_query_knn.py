import knncolle
import numpy
import pytest


def ref_query_knn(X, q, k, distance="euclidean"):
    collected_index = []
    collected_distance = []

    for i in range(q.shape[0]):
        delta = X - q[i,:]
        if distance == "euclidean":
            all_dist = numpy.sqrt((delta**2).sum(axis=1))
        else:
            all_dist = numpy.abs(delta).sum(axis=1)

        o = numpy.argsort(all_dist)
        keep = o if k >= len(o) else o[:k]
        collected_index.append(numpy.array(keep, dtype=numpy.uint32))
        collected_distance.append(numpy.array(all_dist[keep], dtype=numpy.float64))

    return (
        numpy.vstack(collected_index),
        numpy.vstack(collected_distance)
    )


def test_query_knn_basic():
    Y = numpy.random.rand(500, 20)
    q = numpy.random.rand(100, 20)

    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    out = knncolle.query_knn(idx, q, num_neighbors=8)
    ref_i, ref_d = ref_query_knn(Y, q, k=8)
    assert (ref_i == out.index).all()
    assert numpy.isclose(ref_d, out.distance).all()

    idx = knncolle.build_index(knncolle.VptreeParameters(distance="Manhattan"), Y)
    out = knncolle.query_knn(idx, q, num_neighbors=8)
    ref_i, ref_d = ref_query_knn(Y, q, k=8, distance="manhattan")
    assert (ref_i == out.index).all()
    assert numpy.isclose(ref_d, out.distance).all()

    idx = knncolle.build_index(knncolle.VptreeParameters(distance="Cosine"), Y)
    out = knncolle.query_knn(idx, q, num_neighbors=8)
    normed = (Y.T / numpy.sqrt((Y**2).sum(axis=1))).T
    qnormed = (q.T / numpy.sqrt((q**2).sum(axis=1))).T
    ref_i, ref_d = ref_query_knn(normed, qnormed, k=8)
    assert (ref_i == out.index).all()
    assert numpy.isclose(ref_d, out.distance).all()


def test_query_knn_parallel():
    Y = numpy.random.rand(500, 20)
    q = numpy.random.rand(100, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    out = knncolle.query_knn(idx, q, num_neighbors=8)
    pout = knncolle.query_knn(idx, q, num_neighbors=8, num_threads=2)
    assert (out.index == pout.index).all()
    assert (out.distance == pout.distance).all()


def test_query_knn_variable_k():
    Y = numpy.random.rand(500, 20)
    q = numpy.random.rand(100, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)

    with pytest.raises(Exception, match='must be equal'):
        knncolle.query_knn(idx, q, num_neighbors=[1, 1000])

    k = numpy.tile([4,10], 50)
    out = knncolle.query_knn(idx, q, num_neighbors=k)

    ref = knncolle.query_knn(idx, q, num_neighbors=4)
    for i in numpy.where(k == 4)[0]:
        assert (ref.index[i,:] == out.index[i]).all()
        assert (ref.distance[i,:] == out.distance[i]).all()

    ref = knncolle.query_knn(idx, q, num_neighbors=10)
    for i in numpy.where(k == 10)[0]:
        assert (ref.index[i,:] == out.index[i]).all()
        assert (ref.distance[i,:] == out.distance[i]).all()


def test_query_knn_variable_output():
    Y = numpy.random.rand(500, 20)
    q = numpy.random.rand(100, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    out = knncolle.query_knn(idx, q, num_neighbors=8)

    iout = knncolle.query_knn(idx, q, num_neighbors=8, get_distance=False)
    assert (iout.index == out.index).all()
    assert iout.distance is None

    dout = knncolle.query_knn(idx, q, num_neighbors=8, get_index=False)
    assert dout.index is None
    assert (dout.distance == out.distance).all()
