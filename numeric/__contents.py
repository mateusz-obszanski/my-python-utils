from typing import Union


Number = Union[int, float, complex]


def is_almost_equal(x: Number, y: Number, eps: Union[int, float] = 1e-9) -> bool:
    """
    x == y +/- eps
    """
    return abs(x - y) <= eps
