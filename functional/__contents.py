from sys import _getframe


def name_of_caller(nest_lvl: int = 0) -> str:
    """
    Returns caller's name
    """
    return _getframe(nest_lvl + 1).f_code.co_name
