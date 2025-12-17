import knncolle
import numpy


def test_annoy_parameters():
    p = knncolle.AnnoyParameters()
    assert p.num_trees == 50
    assert p.search_mult == 50.0
    assert p.distance == "Euclidean" 

    p = knncolle.AnnoyParameters(distance="Manhattan")
    assert p.distance == "Manhattan" 

    p.num_trees = 20
    assert p.num_trees == 20
    p.search_mult = None
    assert p.num_trees == 20.0


def test_annoy_basic(helpers):
    x = numpy.random.rand(200, 50)
    idx = knncolle.build_index(knncolle.AnnoyParameters(), x) 

    res = knncolle.find_knn(idx, 20)
    helpers.check_index_matrix(res.index, 200, False)
    helpers.check_distance_matrix(res.distance)

    q = numpy.random.rand(100, 50)
    res = knncolle.query_knn(idx, q, 10)
    helpers.check_index_matrix(res.index, 200, True)
    helpers.check_distance_matrix(res.distance)


def test_annoy_distances(helpers):
    x = numpy.random.rand(200, 50)

    # Checking that the Manhattan distance has some effect.
    idx_m = knncolle.build_index(knncolle.AnnoyParameters(distance="Manhattan"), x) 
    res_m = knncolle.find_knn(idx_m, 10)
    helpers.check_index_matrix(res_m.index, 200, False)
    helpers.check_distance_matrix(res_m.distance)

    idx_e = knncolle.build_index(knncolle.AnnoyParameters(distance="Euclidean"), x) 
    res_e = knncolle.find_knn(idx_e, 10)
    assert (res_e.distance != res_m.distance).any()

    # Checking that the Cosine distance is correctly configured.
    idx_c = knncolle.build_index(knncolle.AnnoyParameters(distance="Cosine"), x) 
    res_c = knncolle.find_knn(idx_c, 10)
    norm = (x.T / numpy.sqrt((x**2).sum(axis=1))).T
    idx_ce = knncolle.build_index(knncolle.AnnoyParameters(), norm) 
    res_ce = knncolle.find_knn(idx_ce, 10)
    assert (res_c.index == res_ce.index).all()
    assert numpy.isclose(res_c.distance, res_ce.distance).all()
