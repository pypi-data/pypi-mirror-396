import knncolle
import numpy


def test_exhaustive_parameters():
    p = knncolle.ExhaustiveParameters()
    assert p.distance == "Euclidean" 
    p.distance = "Manhattan"
    assert p.distance == "Manhattan" 


def test_exhaustive_basic(helpers):
    x = numpy.random.rand(200, 50)
    idx = knncolle.build_index(knncolle.ExhaustiveParameters(), x) 

    res = knncolle.find_knn(idx, 20)
    helpers.check_index_matrix(res.index, 200, False)
    helpers.check_distance_matrix(res.distance)

    d = res.distance[:,19].mean()
    res = knncolle.find_neighbors(idx, d)
    helpers.check_index_list(res.index, 200, True)
    helpers.check_distance_list(res.distance)


def test_exhaustive_distances(helpers):
    x = numpy.random.rand(200, 50)

    # Checking that the Manhattan distance has some effect.
    idx_m = knncolle.build_index(knncolle.ExhaustiveParameters(distance="Manhattan"), x) 
    res_m = knncolle.find_knn(idx_m, 10)
    helpers.check_index_matrix(res_m.index, 200, False)
    helpers.check_distance_matrix(res_m.distance)

    idx_e = knncolle.build_index(knncolle.ExhaustiveParameters(distance="Euclidean"), x) 
    res_e = knncolle.find_knn(idx_e, 10)
    assert (res_e.distance != res_m.distance).any()

    # Checking that the Cosine distance is correctly configured.
    idx_c = knncolle.build_index(knncolle.ExhaustiveParameters(distance="Cosine"), x) 
    res_c = knncolle.find_knn(idx_c, 10)

    norm = (x.T / numpy.sqrt((x**2).sum(axis=1))).T
    idx_ce = knncolle.build_index(knncolle.ExhaustiveParameters(), norm) 
    res_ce = knncolle.find_knn(idx_ce, 10)
    assert (res_c.index == res_ce.index).all()
    assert numpy.isclose(res_c.distance, res_ce.distance).all()
