from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    NoReturn,
    Optional,
    Sequence,
    TypeVar,
    Union,
)
from itertools import repeat, zip_longest
from time import sleep

_In = TypeVar("_In")
_Out = TypeVar("_Out")
_PredIn = TypeVar("_PredIn")

Pred = Union[bool, Callable[..., bool]]

_Args = Sequence
_KWArgs = Mapping[str, Any]


class ArgumentTypeError(ValueError):
    """
    Wrong type of the predicate - accepted: `bool`, `Callable`
    """


class InvalidValueError(ValueError):
    """
    Argument set to value that is not considered valid
    """


class UnsizableSequenceError(ValueError):
    """
    Possibly infinite sequence
    """


def run_forever(
    f: Callable, args: Optional[Sequence] = None, kwargs: Optional[Mapping[str, Any]] = None
) -> NoReturn:
    """
    Protip
    ------
    `f` can be a callable object with stete set to previous output (`None` initially)
    in order to compute values based on previous output
    """
    if args is None:
        if kwargs is None:
            while True:
                f()

        while True:
            f(**kwargs)

    if kwargs is None:
        while True:
            f(*args)

    while True:
        f(*args, **kwargs)


def run_for_args_and_kwargs_sequence(
    f: Callable[..., _Out],
    args_gen: Iterable,
    kwargs_gen: Optional[Iterable[Mapping[str, Any]]] = None,
    until_longer: bool = False,
    fill_value: Optional[Any] = None,
    return_option: str = "all",
) -> Union[_Out, list[_Out], None, NoReturn]:
    """
    Runs until the shorter of `args_gen` and `kwargs_gen`
    iterators is exhausted.
    Returns the last `f`'s output

    Parameters
    ----------
    - `f: Callable`,
    - `args_gen: Iterable` - `f`'s args generator for every iteration,
    - `kwargs_gen: Iterable[Mapping[str, Any]] | None` - optional `f`'s
        kwargs generator for every iteration.
    - `until_longer: bool = False` - if `True`, runs until the longer iterator is exhausted
    - `fill_value: Any | None = None` - ignored if `until_longer == False`. Fill value for the shorter iterator
    - `return_option: str = "all"` - `"discard" | "last" | "all"`

    Raises
    ------
    `InvalidValueError`(`ValueError`) if `return_option`'s value is not valid

    Protip
    ------
    `itertools.repeat` can be used as `args_gen` and `kwargs_gen` for infinite loop
    """

    if kwargs_gen is None:
        kwargs_gen = repeat({})

    args_and_kwargs_gen = (
        zip_longest(args_gen, kwargs_gen, fillvalue=fill_value)
        if until_longer
        else zip(args_gen, kwargs_gen)
    )

    if return_option == "all":
        return [f(*args, **kwargs) for args, kwargs in args_and_kwargs_gen]

    if return_option == "discard":
        for args, kwargs in args_and_kwargs_gen:
            f(*args, **kwargs)

        return

    if return_option == "last":
        result = None
        for args, kwargs in args_and_kwargs_gen:
            result = f(*args, **kwargs)

        return result

    raise InvalidValueError(
        f"""`return_option`'s valid values are: "discard" | "last" | "all", got "{return_option}\""""
    )


def run_if(
    f: Callable[..., _Out],
    pred: Pred,
    args: Iterable[_In] = (),
    kwargs: Optional[Mapping[str, _In]] = None,
    pred_args: Iterable[_PredIn] = (),
    pred_kwargs: Mapping[str, _PredIn] = {},
) -> Union[_Out, None]:
    """
    Parameters
    ----------
    - `f: Callable`,
    - `pred: bool | Callable` - predicate. If `Callable`, `pred_args` or `pred_kwargs` can be used,
    - `args: Iterable | None` - `f`'s args,
    - `kwargs: Mapping[str, Any] | None` - `f`'s kwargs,
    - `pred_args: Iterable | None` - `pred`'s args,
    - `pred_kwargs: Mapping[str, Any] | None` - `pred`'s kwargs

    Returns
    -------
    `f`s output

    Raises
    ------
    `ArgumentTypeError`(`ValueError`) if `pred` is neither `bool` nor `Callable`
    """
    if kwargs is None:
        kwargs = {}

    if isinstance(pred, bool):
        if pred:
            return f(*args, **kwargs)

        return

    if callable(pred):
        pred_val: bool = pred(*pred_args, **pred_kwargs)
        if pred_val:
            return f(*args, **kwargs)

        return

    raise ArgumentTypeError(
        f"`pred` must be instance of either`bool` or `Callable`, got `{type(pred)}`"
    )


def loop_if(
    f: Callable[[_Args, _KWArgs], _Out],
    pred: Callable[[_Out], tuple[bool, _Args, _KWArgs]],
    interval: float = 1.0,
) -> NoReturn:
    """
    Executes `f` every time when `pred` returns `True` every `interval` seconds.

    Parameters
    ----------
    - `f: Callable[[_Args, _KWArgs], _Out]`,
    - `pred: Callable[[_Out], tuple[bool, _Args, _KWArgs]]` - predicate, takes `f`'s output as argument
        (`None` for the first time) must return `tuple[bool, _Args, _KWArgs]` - `bool` determines whether
        `f` will be called with `_Args` arguments and `_KWArgs` keyword arguments,
    - `interval: float = 1.0` - time interval of loop repetition [s]
    """
    prev_out = None
    while True:
        call, args, kwargs = pred(prev_out)
        if call:
            prev_out = f(*args, **kwargs)

        sleep(interval)
