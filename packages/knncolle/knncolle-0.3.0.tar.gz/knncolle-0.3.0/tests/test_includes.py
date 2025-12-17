import knncolle


def test_includes():
    import os
    path = knncolle.includes()
    assert isinstance(path, str)
    assert os.path.exists(os.path.join(path, "knncolle_py.h"))
