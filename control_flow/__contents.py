from abc import ABC
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    NoReturn,
    Optional,
    TypeVar,
    Union,
    overload,
)
from ..types.predicates import is_callable, is_iterable, is_mapping


_In = TypeVar("_In")
_Out = TypeVar("_Out")
_PredIn = TypeVar("_PredIn")

Pred = Union[bool, Callable[[_Out, _PredIn], bool]]


class KWArgsError(ABC, ValueError):
    pass


class NotMappingError(KWArgsError):
    """
    KWArgs are not a `Mapping`.
    """


class KeysNotStrError(KWArgsError):
    """
    Not all kwargs' keys are strings.
    """


class PredicateError(ABC, ValueError):
    pass


class PredicateTypeError(PredicateError):
    """
    Wrong type of the predicate - accepted: `bool`, `Callable`.
    """


class PredicateNotMappingError(PredicateError, KWArgsError):
    pass


class PredicateKeysNotStrError(PredicateError, KeysNotStrError):
    pass


__expected_mapping_error_msg_fmt = "`{kwargs_name}` must be a `Mapping`, got `{type}`"
__keys_not_str_error_msg_fmt = "all `{kwargs_name}` keys must be `str`, got `{type}`"


def run_forever(f: Callable[..., Any], *args, **kwargs) -> NoReturn:
    """
    Protip
    ------
    `f` can be a callable object with stete set to previous output (`None` initially)
    in order to compute values based on previous output.
    """
    while True:
        f(*args, **kwargs)


def __check_args_kwargs_and_run(
    f: Callable[[_In], _Out],
    args_name: str = "args",
    kwargs_name: str = "kwargs",
    *args: _In,
    **kwargs: _In,
) -> _Out:
    """
    `args_name` and `kwargs_name` are keys to look for in `**kwargs` containing `f`'s args and
    kwargs.

    Raises
    ------
    - `NotMappingError`(`KWArgsError` (`ValueError`)) - `f`'s kwargs are not a `Mapping`,
    - `KeysNotStrError`(`KWArgsError` (`ValueError`)) - not all `f`'s kwargs' keys are `str`
    """
    f_args = kwargs.get(args_name, args)
    if not is_iterable(f_args):
        f_args = (f_args,)

    f_kwargs = kwargs.get(kwargs_name, {})
    if not is_mapping(f_kwargs):
        raise NotMappingError(
            __expected_mapping_error_msg_fmt.format(
                kwargs_name=kwargs_name, type=str(type(f_kwargs))
            )
        )

    non_str_key = next((key for key in f_kwargs.keys() if not isinstance(key, str)), None)  # type: ignore
    if not non_str_key:
        raise KeysNotStrError(
            __keys_not_str_error_msg_fmt.format(
                kwargs_name=kwargs_name, type=str(type(f_kwargs))
            )
        )
    return f(*f_args, **f_kwargs)  # type: ignore


@overload
def run_if(
    f: Callable[[_In], _Out], pred: Pred, *args: _In, **kwargs: _In
) -> Union[_Out, None]:
    ...


@overload
def run_if(
    f: Callable[[_In], _Out],
    pred: Pred,
    args: Optional[Iterable[_In]] = None,
    kwargs: Optional[Mapping[str, _In]] = None,
    pred_args: Optional[Iterable[_PredIn]] = None,
    pred_kwargs: Optional[Mapping[str, _PredIn]] = None,
) -> Union[_Out, None]:
    ...


def run_if(f: Callable[..., _Out], pred, *args, **kwargs) -> Union[_Out, None]:
    """
    Parameters
    ----------
    - `f: Callable`,
    - `pred: bool | Callable` - if `Callable`, `pred_args` or `pred_kwargs` can be used,
    - `pred_args`,
    - `pred_kwargs`,
    - `f`'s args can be provided as `*args` or by keyword: `args=...`,
    - `f`s kwargs can be provided as `**kwargs` or by keyword: `kwargs=...`

    Raises
    ------
    - `NotMappingError`(`KWArgsError`(`ValueError`)) - `f`'s kwargs are not a `Mapping`,
    - `KeysNotStrError`(`KWArgsError`(`ValueError`)) - not all `f`'s kwargs' keys are `str`,
    - `PredicateTypeError`(`PredicateError`(`ValueError`)) - `pred` is neither `bool` nor `Callable`,
    - `PredicateNotMappingError`(`PredicateError`(`ValueError`), `KWArgsError`) - `pred_kwargs` is not a `Mapping`,
    - `PredicateKeysNotStrError`(`PredicateError`(`ValueError`), KeysNotSetError) - not all `pred_kwargs`' keys are `str`
    """
    if isinstance(pred, bool):
        if pred:
            return __check_args_kwargs_and_run(f, *args, **kwargs)
    if is_callable(pred):
        try:
            pred_val = __check_args_kwargs_and_run(
                pred, *args, args_name="pred_args", kwargs_name="pred_kwargs", **kwargs  # type: ignore
            )

        except KWArgsError as e:
            raise PredicateNotMappingError(*e.args) from e

        except KeysNotStrError as e:
            raise PredicateKeysNotStrError(*e.args) from e

        if pred_val:
            return __check_args_kwargs_and_run(f, *args, **kwargs)

        return

    raise PredicateTypeError(f"`pred` must be `bool` or `Callable`, got `{type(pred)}`")


def loop_if():
    pass
