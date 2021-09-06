from .__utils import Trie as _Trie, suffix_array as _suffix_array
from typing import (
    Union as _Union,
    Optional as _Optional,
    Literal as _Literal,
    overload as _overload,
)
import re as _re


def reverse_text(text: str, /) -> str:
    return "".join(reversed(text))


def split_camel_case(text: str, /) -> str:
    camelcase_group_pattern = _re.compile(r"(^[^A-Z]+|[A-Z_]+(?![^A-Z])|[A-Z][^A-Z_]+)")
    cc_groups = (m.group(0) for m in camelcase_group_pattern.finditer(text))
    return "".join(cc_groups)


Prefixes = list[str]
PrefixesWithOccurences = list[tuple[str, int]]


@_overload
def prefixes_by_occurences(
    *strings: str, min_len: int = 0, ascending_order: bool = False
) -> Prefixes:
    ...


@_overload
def prefixes_by_occurences(
    *strings: str,
    with_occurences: _Literal[False],
    min_len: int = 0,
    ascending_order: bool = False,
) -> Prefixes:
    ...


@_overload
def prefixes_by_occurences(
    *strings: str, with_occurences: _Literal[True], min_len: int = 0, ascending_order: bool = False
) -> PrefixesWithOccurences:
    ...


def prefixes_by_occurences(
    *strings: str, with_occurences: bool = False, min_len: int = 0, ascending_order: bool = False
) -> _Union[Prefixes, PrefixesWithOccurences]:
    trie = _Trie()
    trie.insert(*strings)
    prefixes_with_occurences = trie.getPrefixesByOccurences(
        min_len=min_len, ascending_order=ascending_order
    )
    if with_occurences:
        return prefixes_with_occurences

    return [prefix for prefix, _ in prefixes_with_occurences]


def longest_common_prefix(*strings: str) -> _Optional[str]:
    (most_common_prefix, occurences), *_ = prefixes_by_occurences(*strings, with_occurences=True)
    return most_common_prefix if occurences == len(strings) else None


def shortest_common_prefix(*strings: str, min_len: int = 1) -> _Optional[str]:
    (most_common_prefix, occurences), *_ = prefixes_by_occurences(
        *strings, with_occurences=True, min_len=min_len, ascending_order=True
    )
    return most_common_prefix if occurences == len(strings) else None


def longest_common_suffix(*strings: str) -> _Optional[str]:
    return longest_common_prefix(*map(reverse_text, strings))


def shortest_common_suffix(*strings: str, min_len: int = 1) -> _Optional[str]:
    return shortest_common_prefix(*map(reverse_text, strings), min_len=min_len)


def longest_common_substring(text: str) -> dict[str, list[int]]:
    """Get the longest common substrings and their positions.
    >>> longest_common_substring('banana')
    {'ana': [1, 3]}
    >>> text = "not so Agamemnon, who spoke fiercely to "
    >>> sorted(longest_common_substring(text).items())
    [(' s', [3, 21]), ('no', [0, 13]), ('o ', [5, 20, 38])]
    This function can be easy modified for any criteria, e.g. for searching ten
    longest non overlapping repeated substrings.
    """
    sa, _, lcp = _suffix_array(text)
    maxlen = max(lcp)  # type: ignore
    result = {}
    for i in range(1, len(text)):
        if lcp[i] == maxlen:
            j1, j2, h = sa[i - 1], sa[i], lcp[i]
            assert text[j1 : j1 + h] == text[j2 : j2 + h]  # type: ignore
            substring = text[j1 : j1 + h]  # type: ignore
            if substring not in result:
                result[substring] = [j1]
            result[substring].append(j2)
    return dict((k, sorted(v)) for k, v in result.items())
