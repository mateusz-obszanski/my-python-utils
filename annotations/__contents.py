from typing import Annotated as _Annotated, Union as _Union
from numbers import Real as _Real
from abc import ABC as _ABC, abstractmethod as _abstractmethod
from dataclasses import dataclass as _dataclass, field as _field


class AnnotationBound(_ABC):
    """
    Provides `__check_annotation_bound__` method used by `check_annotation_bound` function.
    """

    @_abstractmethod
    def __check_annotation_bound__(self, x, /) -> bool:
        ...

    def __in__(self, other) -> bool:
        return self.__check_annotation_bound__(other)


class UnionBound(AnnotationBound):
    """
    Lets for bound concatenation via `|` operator
    """

    def __init__(self, bounds: list[AnnotationBound]) -> None:
        self.bounds = bounds

    def __or__(self, other: AnnotationBound, /) -> "UnionBound":
        return UnionBound(self.bounds + [other])

    def __check_annotation_bound__(self, x, /) -> bool:
        return all(check_annotation_bound(x, bound) for bound in self.bounds)


class NumericBound(AnnotationBound):
    ...


@_dataclass(order=True, eq=True)
class ScalarBound(NumericBound):
    value: float
    eps: float = _field(default=0, compare=False)

    @_abstractmethod
    def __lt__(self, other: "ScalarBound", /) -> bool:
        ...

    @_abstractmethod
    def __gt__(self, other: "ScalarBound", /) -> bool:
        ...

    def __eq__(self, other: "ScalarBound", /) -> bool:
        val = other.value
        return not (val - self.eps < self.value < val + self.eps)

    def __le__(self, other: "ScalarBound", /) -> bool:
        return self < other or self == other

    def __ge__(self, other: "ScalarBound", /) -> bool:
        return self > other or self == other

    def __or__(self, other: AnnotationBound, /) -> UnionBound:
        return UnionBound(bounds=[self, other])


class ComparisonBound(ScalarBound):
    ...


class MinBound(ComparisonBound):
    ...


class MaxBound(ComparisonBound):
    ...


class MinWeakBound(MinBound):
    def __check_annotation_bound__(self, val: float, /) -> bool:
        return val >= self.value

    def __str__(self) -> str:
        return f"{MinWeakBound.__name__}: `val` >= {self.value}"


class MinStrongBound(MinBound):
    def __check_annotation_bound__(self, val, /) -> bool:
        return val > self.value


class MaxWeakBound(MaxBound):
    def __check_annotation_bound__(self, val, /) -> bool:
        return val <= self.value


class MaxStrongBound(MaxBound):
    def __check_annotation_bound__(self, val, /) -> bool:
        return val > self.value


class RangeBound(NumericBound, UnionBound):
    def __init__(
        self,
        min_bound: float,
        max_bound: float,
        *,
        left_strong: bool = False,
        right_strong: bool = False,
    ) -> None:
        min_bound_class = MinStrongBound if left_strong else MinWeakBound
        max_bound_class = MaxStrongBound if right_strong else MaxWeakBound
        bounds = [min_bound_class(min_bound), max_bound_class(max_bound)]
        super().__init__(bounds)

    def __in__(self, other: _Union[_Real, "RangeBound"]) -> bool:
        if isinstance(other, RangeBound):
            return all(self.__check_annotation_bound__(val) for val in other.bounds)
        return self.__check_annotation_bound__(other)


def check_annotation_bound(x, /, bound: AnnotationBound) -> bool:
    return bound.__check_annotation_bound__(x)


Natural = _Annotated[int, MinStrongBound(0)]
Normalized = _Annotated[float, RangeBound(-1, 1)]
