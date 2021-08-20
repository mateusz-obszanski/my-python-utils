from types import FunctionType, BuiltinFunctionType
from typing import Iterable, Union


def hasattr_all(x, attrs: Union[str, Iterable[str]]) -> bool:
    if isinstance(x, str):
        x = (x,)

    return all(hasattr(x, attr) for attr in attrs)


def is_function(x) -> bool:
    return isinstance(x, (FunctionType, BuiltinFunctionType))


def is_callable(x) -> bool:
    return hasattr(x, "__call__")


def is_iterable(x) -> bool:
    """
    Iterable is an object capable of returning iterator.
    """
    return hasattr(x, "__iter__")


def is_iterator(x) -> bool:
    return hasattr(x, "__next__")


def is_sizable(x) -> bool:
    return hasattr(x, "__len__")


def is_mapping(x) -> bool:
    return hasattr_all(x, ("__getitem__", "keys"))
