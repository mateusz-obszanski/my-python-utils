from typing import (
    Any as __Any,
    Union as __Union,
    Callable as __Callable,
    Mapping as __Mapping,
    overload as __overload,
)
import re as __re
from common.exceptions.messages import value_error_positional_msg as __value_error_positional_msg
from common.format import _pluralize


pluralize = _pluralize


@__overload
def stringify_kwargs(kwargs: __Mapping[str, __Any]) -> str:
    ...


@__overload
def stringify_kwargs(**kwargs) -> str:
    ...


def stringify_kwargs(*args: __Mapping[str, __Any], **kwargs) -> str:
    if args and kwargs:
        raise ValueError(
            __value_error_positional_msg(f_name=stringify_kwargs.__name__, expected_n=0, args=args)
        )
    try:
        return ", ".join(f"{key}={val}" for key, val in kwargs.items())
    except AttributeError:
        # generic Mapping might not implement items method
        return ", ".join(f"{key}={kwargs[key]}" for key in kwargs.keys())


def replace_many(string: str, mapping: __Mapping[str, str], ignore_case: bool = False) -> str:
    """
    Given a string and a replacement map, it returns the replaced string.

    Parameters
    ----------
    - `string: str` - string to execute replacements on,
    - `mapping` - replacement dictionary {value to find: value to replace},
    - `ignore_case: bool = False` - whether the match should be case insensitive

    Returns
    -------
    `str` - `string` after substitution

    Source of the original code: https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729
    """
    if not mapping:
        # Edge case that'd produce a funny regex and cause a KeyError
        return string

    # If case insensitive, we need to normalize the old string so that later a replacement
    # can be found. For instance with {"HEY": "lol"} we should match and find a replacement for
    # "hey", HEY", "hEy", etc.
    if ignore_case:
        normalize: __Callable[[str], str] = lambda s: s.lower()
        re_mode = __re.IGNORECASE

    else:
        normalize: __Callable[[str], str] = lambda s: s
        re_mode = 0

    mapping = {normalize(key): val for key, val in mapping.items()}

    # Place longer ones first to keep shorter substrings from matching where the longer ones should
    # take place. For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string
    # 'hey abc', it should produce 'hey ABC' and not 'hey ABc'
    rep_sorted = sorted(mapping, key=len, reverse=True)
    rep_escaped = map(__re.escape, rep_sorted)

    # Create a big OR regex that matches any of the substrings to replace
    pattern = __re.compile("|".join(rep_escaped), re_mode)  # type: ignore

    # For each match, look up the new string in the replacements, being the key the normalized old
    # string
    return pattern.sub(lambda match: mapping[normalize(match.group(0))], string)


def __format_partial_handle_value_error(
    match: __Union[__re.Match, None], fmt: str, val: str, e: ValueError
):
    keyword = (match.groupdict().get("keyword", None) or "") if match is not None else ""
    specifier = "{" f"{keyword}:{fmt}" "}"
    raise FormatError(f"Invalid format specifier: `{specifier}` for value `{val}`") from e


def format_partial_kwargs(
    string: str, kwargs: __Mapping[str, __Any], raise_nonexistent_keywords: bool = False
) -> str:
    group_fmt = r"(?P<fmt>[^}]*)"
    group_fmt_optional = f"(:{group_fmt})?"

    re_compile = __re.compile

    for keyword, value in kwargs.items():
        keyword_pattern = re_compile(f"{{{keyword}{group_fmt_optional}}}")

        if raise_nonexistent_keywords:
            matches = list(keyword_pattern.finditer(string))
            if not matches:
                raise KeyError(keyword)

        else:
            matches = keyword_pattern.finditer(string)

        for match in matches:
            fmt = match.groupdict()["fmt"]
            if fmt is None:
                optional_fmt_with_suffix = ""
                repl = str(value)
            else:
                optional_fmt_with_suffix = f":{fmt}" if fmt else ""
                try:
                    repl = f"{{:{fmt}}}".format(value)
                except ValueError as e:
                    __format_partial_handle_value_error(match, fmt, value, e)

            string = string.replace(f"{{{keyword}{optional_fmt_with_suffix}}}", repl, 1)

    return string


def format_partial(
    string: str,
    args: tuple = (),
    kwargs: __Mapping[str, __Any] = {},
    ordered_ph_no_overflow: bool = True,
    raise_nonexistent_keywords: bool = False,
) -> str:
    """
    Partial string substitution. supported placeholders: {}, {<number>} and {<keyword>}.

    ordered_ph_no_overflow - if False and str has numerical placeholder, i.e. {4} >= len(args), raises
    IndexError, else decrements all not replaced numerical placeholders

    raise_nonexistent_keywords - if True and nonexistent keyword in kwargs, raises KeyError
    """
    # TODO no trailing : with empty fmt
    # TODO debug - format_partial("{3}-{1:.2f}", args=[1, 3.145, 7]) == '3.15-{1:.2f}'
    if not string:
        if not ordered_ph_no_overflow or ordered_ph_no_overflow and not args and not kwargs:
            msg = __value_error_positional_msg(
                format_partial.__name__, expected_n="at least one", args=args
            )
            raise ValueError(f"empty string - {msg}")

        return ""

    if not args and not kwargs:
        raise ValueError(
            __value_error_positional_msg(
                format_partial.__name__, expected_n="at least one", args=args
            )
        )

    re_compile = __re.compile

    # i.e. "...{1}...{0}..."
    #           ^     ^
    keyword_numeric = r"\d+"

    group_keyword_numeric = rf"(?P<keyword>{keyword_numeric})"
    # i.e. "...{:<.2f}..."
    #            ^^^^
    group_fmt = r"(?P<fmt>[^}]*)"

    # i.e. "...{:<.2f}..."
    #           ^^^^^
    group_fmt_optional = f"(:{group_fmt})?"

    # placeholder patterns
    _ph_pattern_template = r"{" "%s" f"{group_fmt_optional}" r"}"

    ph_pattern_empty = re_compile(_ph_pattern_template % "")
    ph_pattern_keyword_numeric = re_compile(_ph_pattern_template % group_keyword_numeric)

    # order of substitution matters
    # {foo:...} -> {4:...} -> {:...}

    # replace keyword placeholders
    string = format_partial_kwargs(
        string, kwargs, raise_nonexistent_keywords=raise_nonexistent_keywords
    )

    args_used_indices: set[int] = set()
    ns_to_decrement: set[int] = set()

    # replace ordered
    for arg_match_numeric in ph_pattern_keyword_numeric.finditer(string):
        groupdict = arg_match_numeric.groupdict()
        arg_index = int(groupdict["keyword"])
        fmt = groupdict["fmt"] or ""

        try:
            arg = args[arg_index]
        except IndexError as e:
            if not ordered_ph_no_overflow:
                raise IndexError(
                    f"Replacement index {arg_index} out of range for positional args tuple"
                ) from e

            ns_to_decrement.add(arg_index)
            continue

        try:
            string = ph_pattern_keyword_numeric.sub(f"{{:{fmt}}}".format(arg), string, count=1)
        except ValueError as e:
            __format_partial_handle_value_error(arg_match_numeric, fmt, arg, e)

        args_used_indices.add(arg_index)

    # decrement leftover numeric placeholders
    if ordered_ph_no_overflow and ns_to_decrement:
        args_len = len(args)
        for n in sorted(ns_to_decrement):
            n_pattern = re_compile(f"{{{n}{group_fmt_optional}}}")
            # replace all (fmts differ)
            for match in n_pattern.finditer(string):
                match = next(n_pattern.finditer(string))
                groupdict = match.groupdict()
                fmt = groupdict["fmt"] or ""

                string = ph_pattern_keyword_numeric.sub(
                    f"{{{n - args_len}:{fmt}}}", string, count=1
                )

    # replace any empty placeholder
    index_not_used: __Callable[[int], bool] = lambda i: i not in args_used_indices

    for arg_index, arg_match in zip(
        filter(index_not_used, range(len(args))),
        ph_pattern_empty.finditer(string),
    ):
        arg = args[arg_index]
        fmt = arg_match.groupdict()["fmt"] or ""
        try:
            string = ph_pattern_empty.sub(f"{{:{fmt}}}".format(arg), string, count=1)

        except ValueError as e:
            __format_partial_handle_value_error(arg_match, fmt, arg, e)

        args_used_indices.add(arg_index)

    return string


class FormatError(ValueError):
    pass
