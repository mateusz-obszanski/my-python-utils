from typing import Union as _Union, ClassVar as _ClassVar


class EmptyInitializationError(Exception):
    ...


# * null types
class EmptyType:
    __instance: _ClassVar[_Union["EmptyType", None]] = None

    __slots__ = ("__name",)

    def __init__(self, *, name: str = "empty") -> None:
        self.__name = name

    def __new__(cls, *args, **kwargs) -> "EmptyType":
        if cls.__instance is None:
            cls.__instance = object.__new__(EmptyType, *args, **kwargs)
        return cls.__instance

    def __str__(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return f"EmptyType(name={self.__name})"
