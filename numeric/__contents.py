def is_almost_equal(x: complex, y: complex, eps: float = 1e-9) -> bool:
    """
    x == y +/- eps
    """
    return abs(x - y) <= eps
