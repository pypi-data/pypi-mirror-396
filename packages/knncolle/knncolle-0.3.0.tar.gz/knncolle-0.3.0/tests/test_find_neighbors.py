import knncolle
import numpy
import pytest


def ref_find_all(X, threshold, distance="euclidean"):
    collected_index = []
    collected_distance = []

    for i in range(X.shape[0]):
        delta = X - X[i,:]
        if distance == "euclidean":
            all_dist = numpy.sqrt((delta**2).sum(axis=1))
        else:
            all_dist = numpy.abs(delta).sum(axis=1)

        keep = all_dist <= threshold
        keep[i] = False
        keep = numpy.where(keep)[0]

        all_dist = all_dist[keep]
        o = numpy.argsort(all_dist)
        collected_index.append(numpy.array(keep[o], dtype=numpy.uint32))
        collected_distance.append(numpy.array(all_dist[o], dtype=numpy.float64))

    return (collected_index, collected_distance)


def test_find_neighbors_basic(helpers):
    Y = numpy.random.rand(500, 20)

    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    d = numpy.median(knncolle.find_distance(idx, num_neighbors=8))
    out = knncolle.find_neighbors(idx, threshold=d)
    ref_i, ref_d = ref_find_all(Y, d)
    helpers.compare_lists(ref_i, out.index)
    helpers.compare_lists_close(ref_d, out.distance)

    idx = knncolle.build_index(knncolle.VptreeParameters(distance="Manhattan"), Y)
    d = numpy.median(knncolle.find_distance(idx, num_neighbors=8))
    out = knncolle.find_neighbors(idx, threshold=d)
    ref_i, ref_d = ref_find_all(Y, d, distance="manhattan")
    helpers.compare_lists(ref_i, out.index)
    helpers.compare_lists_close(ref_d, out.distance)

    idx = knncolle.build_index(knncolle.VptreeParameters(distance="Cosine"), Y)
    d = numpy.median(knncolle.find_distance(idx, num_neighbors=8))
    out = knncolle.find_neighbors(idx, threshold=d)
    normed = (Y.T / numpy.sqrt((Y**2).sum(axis=1))).T
    ref_i, ref_d = ref_find_all(normed, d)
    helpers.compare_lists(ref_i, out.index)
    helpers.compare_lists_close(ref_d, out.distance)


def test_find_neighbors_parallel(helpers):
    Y = numpy.random.rand(500, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    d = numpy.median(knncolle.find_distance(idx, num_neighbors=8))
    out = knncolle.find_neighbors(idx, threshold=d)
    pout = knncolle.find_neighbors(idx, threshold=d, num_threads=2)
    helpers.compare_lists(out.index, pout.index)
    helpers.compare_lists(out.distance, pout.distance)


def test_find_neighbors_subset(helpers):
    Y = numpy.random.rand(500, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    d = numpy.median(knncolle.find_distance(idx, num_neighbors=3))

    full = knncolle.find_neighbors(idx, threshold=d)
    sout = knncolle.find_neighbors(idx, threshold=d, subset=range(10, 30))
    helpers.compare_lists(full.index[10:30], sout.index)
    helpers.compare_lists(full.distance[10:30], sout.distance)

    with pytest.raises(Exception, match='out-of-range'):
        knncolle.find_neighbors(idx, threshold=d, subset=[1000])

    eidx = knncolle.build_index(knncolle.VptreeParameters(), Y[0:0,:])
    empty = knncolle.find_neighbors(eidx, threshold=d)
    assert len(empty.index) == 0
    assert len(empty.distance) == 0


def test_find_knn_variable_threshold(helpers):
    Y = numpy.random.rand(500, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    d4 = numpy.median(knncolle.find_distance(idx, num_neighbors=4))
    d10 = numpy.median(knncolle.find_distance(idx, num_neighbors=10))

    with pytest.raises(Exception, match='should have length equal'):
        knncolle.find_neighbors(idx, threshold=[1, 1000])

    vard = numpy.tile([d4,d10], 250)
    out = knncolle.find_neighbors(idx, threshold=vard)

    ref = knncolle.find_neighbors(idx, threshold=d4)
    for i in numpy.where(vard == d4)[0]:
        assert (ref.index[i] == out.index[i]).all()
        assert (ref.distance[i] == out.distance[i]).all()

    ref = knncolle.find_neighbors(idx, threshold=d10)
    for i in numpy.where(vard == d10)[0]:
        assert (ref.index[i] == out.index[i]).all()
        assert (ref.distance[i] == out.distance[i]).all()


def test_find_neighbors_variable_output(helpers):
    Y = numpy.random.rand(500, 20)
    idx = knncolle.build_index(knncolle.VptreeParameters(), Y)
    d = numpy.median(knncolle.find_distance(idx, num_neighbors=8))

    out = knncolle.find_neighbors(idx, threshold=d)

    iout = knncolle.find_neighbors(idx, threshold=d, get_distance=False)
    helpers.compare_lists(out.index, iout.index)
    assert iout.distance is None

    dout = knncolle.find_neighbors(idx, threshold=d, get_index=False)
    assert dout.index is None
    helpers.compare_lists(out.distance, dout.distance)
