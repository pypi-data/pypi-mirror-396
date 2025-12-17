"""Dummy conftest.py for knncolle.

If you don't know what this is for, just leave it empty.
Read more about conftest.py under:
- https://docs.pytest.org/en/stable/fixture.html
- https://docs.pytest.org/en/stable/writing_plugins.html
"""

import pytest

class Helpers:
    @staticmethod
    def check_index_matrix(index, num_obs, include_self):
        for r in range(index.shape[0]):
            currow = index[r,:]
            assert (currow >= 0).all()
            assert (currow < num_obs).all()
            if not include_self:
                assert (currow != r).all()
            assert len(set(currow)) == len(currow)

    @staticmethod
    def check_distance_matrix(distance):
        for r in range(distance.shape[0]):
            currow = distance[r,:]
            assert (currow >= 0).all()
            for i in range(len(currow) - 1):
                assert currow[i] <= currow[i+1]

    @staticmethod
    def check_index_list(index, num_obs, include_self):
        for entry in index:
            assert (entry >= 0).all()
            assert (entry < num_obs).all()
            if not include_self:
                assert (entry != r).all()
            assert len(set(entry)) == len(entry)

    @staticmethod
    def check_distance_list(distance):
        for entry in distance:
            assert (entry >= 0).all()
            for i in range(len(entry) - 1):
                assert entry[i] <= entry[i+1]

    @staticmethod
    def compare_lists(x, y):
        assert len(x) == len(y)
        for i, val in enumerate(x):
            assert (val == y[i]).all()

    @staticmethod
    def compare_lists_close(x, y):
        import numpy
        assert len(x) == len(y)
        for i, val in enumerate(x):
            assert numpy.isclose(val, y[i]).all()



@pytest.fixture
def helpers():
    return Helpers
