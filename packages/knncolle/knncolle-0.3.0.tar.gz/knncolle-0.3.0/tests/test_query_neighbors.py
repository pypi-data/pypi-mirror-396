import knncolle
import numpy
import pytest


def ref_query_all(X, q, threshold, distance="euclidean"):
    collected_index = []
    collected_distance = []

    for i in range(q.shape[0]):
        delta = X - q[i,:]
        if distance == "euclidean":
            all_dist = numpy.sqrt((delta**2).sum(axis=1))
        else:
            all_dist = numpy.abs(delta).sum(axis=1)

        keep = all_dist <= threshold
        keep = numpy.where(keep)[0]

        all_dist = all_dist[keep]
        o = numpy.argsort(all_dist)
        collected_index.append(numpy.array(keep[o], dtype=numpy.uint32))
        collected_distance.append(numpy.array(all_dist[o], dtype=numpy.float64))

    return (collected_index, collected_distance)


def test_query_neighbors_basic(helpers):
    Y = numpy.random.rand(500, 20)
    q = numpy.random.rand(100, 20)

    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    d = numpy.median(knncolle.query_distance(idx, q, num_neighbors=8))
    out = knncolle.query_neighbors(idx, q, threshold=d)
    ref_i, ref_d = ref_query_all(Y, q, d)
    helpers.compare_lists(ref_i, out.index)
    helpers.compare_lists_close(ref_d, out.distance)

    idx = knncolle.build_index(knncolle.VptreeParameters(distance="Manhattan"), Y)
    d = numpy.median(knncolle.query_distance(idx, q, num_neighbors=8))
    out = knncolle.query_neighbors(idx, q, threshold=d)
    ref_i, ref_d = ref_query_all(Y, q, d, distance="manhattan")
    helpers.compare_lists(ref_i, out.index)
    helpers.compare_lists_close(ref_d, out.distance)

    idx = knncolle.build_index(knncolle.VptreeParameters(distance="Cosine"), Y)
    d = numpy.median(knncolle.query_distance(idx, q, num_neighbors=8))
    out = knncolle.query_neighbors(idx, q, threshold=d)
    normed = (Y.T / numpy.sqrt((Y**2).sum(axis=1))).T
    qnormed = (q.T / numpy.sqrt((q**2).sum(axis=1))).T
    ref_i, ref_d = ref_query_all(normed, qnormed, d)
    helpers.compare_lists(ref_i, out.index)
    helpers.compare_lists_close(ref_d, out.distance)


def test_query_neighbors_parallel(helpers):
    Y = numpy.random.rand(500, 20)
    q = numpy.random.rand(100, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    d = numpy.median(knncolle.query_distance(idx, q, num_neighbors=8))
    out = knncolle.query_neighbors(idx, q, threshold=d)
    pout = knncolle.query_neighbors(idx, q, threshold=d, num_threads=2)
    helpers.compare_lists(out.index, pout.index)
    helpers.compare_lists(out.distance, pout.distance)


def test_find_knn_variable_threshold(helpers):
    Y = numpy.random.rand(500, 20)
    q = numpy.random.rand(100, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    d4 = numpy.median(knncolle.query_distance(idx, q, num_neighbors=4))
    d10 = numpy.median(knncolle.query_distance(idx, q, num_neighbors=10))

    with pytest.raises(Exception, match='should have length equal'):
        knncolle.query_neighbors(idx, q, threshold=[1, 1000])

    vard = numpy.tile([d4,d10], 50)
    out = knncolle.query_neighbors(idx, q, threshold=vard)

    ref = knncolle.query_neighbors(idx, q, threshold=d4)
    for i in numpy.where(vard == d4)[0]:
        assert (ref.index[i] == out.index[i]).all()
        assert (ref.distance[i] == out.distance[i]).all()

    ref = knncolle.query_neighbors(idx, q, threshold=d10)
    for i in numpy.where(vard == d10)[0]:
        assert (ref.index[i] == out.index[i]).all()
        assert (ref.distance[i] == out.distance[i]).all()


def test_query_neighbors_variable_output(helpers):
    Y = numpy.random.rand(500, 20)
    q = numpy.random.rand(100, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    d = numpy.median(knncolle.query_distance(idx, q, num_neighbors=8))

    out = knncolle.query_neighbors(idx, q, threshold=d)

    iout = knncolle.query_neighbors(idx, q, threshold=d, get_distance=False)
    helpers.compare_lists(out.index, iout.index)
    assert iout.distance is None

    dout = knncolle.query_neighbors(idx, q, threshold=d, get_index=False)
    assert dout.index is None
    helpers.compare_lists(out.distance, dout.distance)
