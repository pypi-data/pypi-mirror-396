from sdg_core_lib.browser import browse_algorithms, browse_functions


def test_browse_algorithms():
    for desc in browse_algorithms():
        assert desc is not None


def test_browse_functions():
    for desc in browse_functions():
        assert desc is not None
