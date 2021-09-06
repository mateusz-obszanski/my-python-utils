# -*- coding: utf-8 -*-

from typing import (
    Any as _Any,
    Callable as _Callable,
    Mapping as _Mapping,
    Literal as _Literal,
    Union as _Union,
    Iterable as _Iterable,
    TypedDict as _TypedDict,
    Optional as _Optional,
    overload as _overload,
)
import re as _re
from itertools import chain as _chain


def textified_kwargs(kwargs: _Mapping[str, _Any], /) -> str:
    try:
        return ", ".join(f"{key}={val}" for key, val in kwargs.items())
    except AttributeError:
        # generic Mapping might not implement items method
        return ", ".join(f"{key}={kwargs[key]}" for key in kwargs.keys())


def replace_many(text: str, /, mapping: _Mapping[str, str], *, ignore_case: bool = False) -> str:
    """
    Given a text and a replacement map, it returns the replaced text.

    Parameters
    ----------
    - `text: str` - text to execute replacements on,
    - `mapping` - replacement dictionary {value to find: value to replace},
    - `ignore_case: bool = False` - whether the match should be case insensitive

    Returns
    -------
    `str` - `text` after substitution

    Source of the original code: https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729
    """
    if not mapping:
        return text

    if ignore_case:
        normalize: _Callable[[str], str] = lambda s: s.lower()
        re_mode = _re.IGNORECASE

        mapping = {normalize(key): val for key, val in mapping.items()}

    else:
        normalize: _Callable[[str], str] = lambda s: s
        re_mode = 0

    # Place longer ones first to keep shorter subtexts from matching where the longer ones should
    # take place. For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the text
    # 'hey abc', it should produce 'hey ABC' and not 'hey ABc'
    rep_sorted = sorted(mapping, key=len, reverse=True)
    rep_escaped = map(_re.escape, rep_sorted)

    # Create a big OR regex that matches any of the subtexts to replace
    pattern = _re.compile("|".join(rep_escaped), re_mode)  # type: ignore

    return pattern.sub(lambda match: mapping[normalize(match.group(0))], text)


def capitalized_first_letter_str(s: str, /) -> str:
    return s[0].upper() + s[1:] if s else ""


Case = _Literal["camel", "snake", "kebab"]
Sep = _Union[str, None]


class _SepMapping(_TypedDict):
    camel: None
    snake: str
    kebab: str


_SEP_MAPPING: _SepMapping = {
    "camel": None,
    "snake": "_",
    "kebab": "-",
}


@_overload
def converted_case(
    text: str,
    /,
    old_case: Case,
    new_case: Case,
    *,
    capitalize_first_letter: bool = False,
) -> str:
    ...


@_overload
def converted_case(
    text: str,
    /,
    old_sep: Sep,
    new_sep: Sep,
    *,
    capitalize_first_letter: bool = False,
) -> str:
    ...


@_overload
def converted_case(
    text: str,
    old_case_or_sep: _Union[Case, Sep],
    new_case_or_sep: _Union[Case, Sep],
    /,
    *,
    capitalize_first_letter: bool = False,
) -> str:
    ...


def converted_case(
    text: str,
    /,
    *args: _Union[Case, Sep],
    capitalize_first_letter: bool = False,
    **kwargs: _Union[Case, Sep],
) -> str:
    if not text:
        return ""

    if len(args) + len(kwargs) > 2:
        raise ValueError(f"expected 2 arguments, got: {len(args) + len(kwargs)}")

    wrong_kw = next(
        (kw for kw in kwargs if kw not in {"old_case", "new_case", "old_sep", "new_sep"}), None
    )
    if wrong_kw is not None:
        raise ValueError(f"Unexpected keyword: {wrong_kw}")

    if "old_case" in kwargs:
        old_case = kwargs["old_case"]
        old_sep = _SEP_MAPPING[old_case] if old_case is not None else None
    elif "old_sep" in kwargs:
        old_sep = kwargs["old_sep"]
    elif args:
        old_case_or_sep = args[0]
        if old_case_or_sep is None:
            old_sep = None
        else:
            old_sep = (
                _SEP_MAPPING[old_case_or_sep]
                if old_case_or_sep in _SEP_MAPPING
                else old_case_or_sep
            )
    else:
        raise ValueError(f"expected `old_sep` or 'old_case' argument")

    if "new_case" in kwargs:
        new_case = kwargs["new_case"]
        new_sep = _SEP_MAPPING[new_case] if new_case is not None else None
    elif "new_sep" in kwargs:
        new_sep = kwargs["new_sep"]
    elif len(args) == 2:
        new_case_or_sep = args[1]
        if new_case_or_sep is None:
            new_sep = None
        else:
            new_sep = _SEP_MAPPING.get(new_case_or_sep, new_case_or_sep)
    else:
        raise ValueError(f"expected `new_sep` or `new_case` argument")

    subgroups: _Iterable[str]

    # from camelCase
    if old_sep is None:
        # to camelCase
        if new_sep is None:
            return text

        camelcase_group_pattern = _re.compile(r"(^[^A-Z]+|[A-Z_]+(?![^A-Z])|[A-Z][^A-Z_]+)")
        subgroups = (m.group(0).lower() for m in camelcase_group_pattern.finditer(text))

    else:
        subgroups = (sg for sg in text.split(old_sep))

    # to camelCase
    if new_sep is None:
        if capitalize_first_letter:
            return "".join(sg[0].upper() + sg[1:] if sg else "" for sg in subgroups)

        first_subgroup = next(subgroups)
        return "".join(
            _chain([first_subgroup], (sg[0].upper() + sg[1:] if sg else "" for sg in subgroups))
        )

    return new_sep.join(subgroups)


def __case_dispatch_old_sep(
    args: tuple[_Union[Case, Sep], ...], kwargs: dict[str, _Union[Case, Sep]]
) -> _Union[str, None]:
    if len(args) + len(kwargs) != 1:
        raise ValueError(f"expected 1 argument, got {len(args) + len(kwargs)}")

    if "old_sep" in kwargs:
        old_sep = kwargs["old_sep"]

    elif "old_case" in kwargs:
        old_case: _Optional[_Union[Case, str]] = kwargs["old_case"]
        if not isinstance(old_case, str):
            raise ValueError(f"expected `str`, got `{type(old_case)}`")

        if old_case not in _SEP_MAPPING:
            raise ValueError(
                f"expected `old_case` to be in {list(_SEP_MAPPING.keys())}, " f"got `{old_case}`"
            )

        old_sep = _SEP_MAPPING[old_case]

    else:
        old_arg_or_sep = args[0]
        if old_arg_or_sep is None:
            old_sep = None
        else:
            old_sep = _SEP_MAPPING.get(old_arg_or_sep, old_arg_or_sep)

    return old_sep


@_overload
def snake_case(text: str, /, new_case: Case, *, capitalize_first_letter: bool = False) -> str:
    ...


@_overload
def snake_case(text: str, /, new_sep: Sep, *, capitalize_first_letter: bool = False) -> str:
    ...


def snake_case(
    text: str,
    /,
    *args: _Union[Case, Sep],
    capitalize_first_letter: bool = False,
    **kwargs: _Union[Case, Sep],
) -> str:
    old_sep = __case_dispatch_old_sep(args, kwargs)
    return converted_case(
        text, old_sep=old_sep, new_sep="_", capitalize_first_letter=capitalize_first_letter
    )


@_overload
def camel_case(text: str, /, new_case: Case, *, capitalize_first_letter: bool = False) -> str:
    ...


@_overload
def camel_case(text: str, /, new_sep: Sep, *, capitalize_first_letter: bool = False) -> str:
    ...


def camel_case(
    text: str,
    /,
    *args: _Union[Case, Sep],
    capitalize_first_letter: bool = False,
    **kwargs: _Union[Case, Sep],
) -> str:
    old_sep = __case_dispatch_old_sep(args, kwargs)
    return converted_case(
        text, old_sep=old_sep, new_sep=None, capitalize_first_letter=capitalize_first_letter
    )


@_overload
def kebab_case(text: str, /, new_case: Case, *, capitalize_first_letter: bool = False) -> str:
    ...


@_overload
def kebab_case(text: str, /, new_sep: Sep, *, capitalize_first_letter: bool = False) -> str:
    ...


def kebab_case(
    text: str,
    /,
    *args: _Union[Case, Sep],
    capitalize_first_letter: bool = False,
    **kwargs: _Union[Case, Sep],
) -> str:
    old_sep = __case_dispatch_old_sep(args, kwargs)
    return converted_case(
        text, old_sep=old_sep, new_sep="-", capitalize_first_letter=capitalize_first_letter
    )
