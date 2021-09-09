from operator import itemgetter as _itemgetter
from ._utils import Trie as _Trie, suffix_array as _suffix_array
from typing import (
    Generator as _Generator,
    Union as _Union,
    Optional as _Optional,
    Literal as _Literal,
    Callable as _Callable,
    overload as _overload,
)
import re as _re
from itertools import takewhile as _takewhile


def reverse_text(text: str, /) -> str:
    return "".join(reversed(text))


def split_camel_case(text: str, /) -> str:
    camelcase_group_pattern = _re.compile(r"(^[^A-Z]+|[A-Z_]+(?![^A-Z])|[A-Z][^A-Z_]+)")
    cc_groups = (m.group(0) for m in camelcase_group_pattern.finditer(text))
    return "".join(cc_groups)


Prefix = str
Prefixes = list[Prefix]
Occurences = int
PrefixWithOccurences = tuple[Prefix, Occurences]
PrefixesWithOccurences = list[tuple[Prefix, Occurences]]


@_overload
def prefixes_by_occurences(
    *strings: str, min_len: int = 1, ascending_order: bool = False
) -> Prefixes:
    ...


@_overload
def prefixes_by_occurences(
    *strings: str,
    with_occurences: _Literal[False],
    min_len: int = 1,
    ascending_order: bool = False,
) -> Prefixes:
    ...


@_overload
def prefixes_by_occurences(
    *strings: str, with_occurences: _Literal[True], min_len: int = 1, ascending_order: bool = False
) -> PrefixesWithOccurences:
    ...


def prefixes_by_occurences(
    *strings: str, with_occurences: bool = False, min_len: int = 1, ascending_order: bool = False
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
    return (
        reverse_text(lcs)
        if (lcs := longest_common_prefix(*map(reverse_text, strings))) is not None
        else None
    )


def shortest_common_suffix(*strings: str, min_len: int = 1) -> _Optional[str]:
    return (
        reverse_text(scs)
        if (scs := shortest_common_prefix(*map(reverse_text, strings), min_len=min_len))
        is not None
        else None
    )


def longest_common_prefixes(*strings: str, min_len: int = 1, min_occurences: int = 0) -> list[str]:
    prefixes_with_occurences = prefixes_by_occurences(
        *strings, min_len=min_len, with_occurences=True
    )

    if not prefixes_with_occurences:
        return []

    prefix_with_occurences = prefixes_with_occurences[0]
    prev_prefix, prev_occurences = first_prefix, _ = prefix_with_occurences

    more_than_min_occurences: _Callable[[PrefixWithOccurences], bool] = (
        lambda pwo: pwo[1] > min_occurences
    )

    return [first_prefix] + [
        prefix
        for prefix, occurences in _takewhile(
            more_than_min_occurences, prefixes_with_occurences[1:]
        )
        if (
            prev_occurences == (prev_occurences := occurences)
            and not prev_prefix.startswith(prefix)
        )
        or not prev_prefix.startswith(prev_prefix := prefix)
    ]


def longest_common_suffixes(*strings: str, min_len: int = 1) -> list[str]:
    return list(
        map(reverse_text, longest_common_prefixes(*map(reverse_text, strings), min_len=min_len))
    )


PrefixGroup = _Union[Prefix, list["PrefixGroup"]]


# TODO test
def groups_by_prefixes(*strings, min_len: int = 1) -> list[PrefixGroup]:
    strings = sorted(strings)
    prev_prefix_lengths = len(strings) * [0]
    max_str_len = max(len(s) for s in strings)

    def _groups_by_prefixes(
        *strings: str, prev_prefix_lengths: list[int], max_str_len: int
    ) -> _Generator[PrefixGroup, None, None]:
        while True:
            new_prev_prefix_lengths = len(strings) * [0]
            for ppl_ix, (prefix, prev_prefix_len) in enumerate(
                zip(
                    sorted(longest_common_prefixes(*strings, min_len=min_len), key=_itemgetter(0)),
                    prev_prefix_lengths,
                )
            ):
                starts_with_prefix: _Callable[[str], bool] = lambda s: s.startswith(
                    prefix, prev_prefix_len
                )
                strings_starting_with_prefix = list(_takewhile(starts_with_prefix, strings))

                if not strings_starting_with_prefix:
                    yield prefix

                else:
                    yield list(
                        reversed(
                            [
                                *_groups_by_prefixes(
                                    *strings,
                                    prev_prefix_lengths=prev_prefix_lengths,
                                    max_str_len=max_str_len,
                                )
                            ]
                        )
                    )

                new_prev_prefix_lengths[ppl_ix] = len(prefix)

            if all(nppl > max_str_len for nppl in new_prev_prefix_lengths):
                return

            prev_prefix_lengths = new_prev_prefix_lengths

    return [
        pg
        for pg in _groups_by_prefixes(
            *strings, prev_prefix_lengths=prev_prefix_lengths, max_str_len=max_str_len
        )
    ]


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
    suffix_array, _, longest_common_prefixes = _suffix_array(text)
    max_len = max(longest_common_prefixes)  # type: ignore
    result = {}
    for i in range(1, len(text)):
        if longest_common_prefixes[i] == max_len:
            j1, j2, h = suffix_array[i - 1], suffix_array[i], longest_common_prefixes[i]
            assert text[j1 : j1 + h] == text[j2 : j2 + h]  # type: ignore
            substring = text[j1 : j1 + h]  # type: ignore
            if substring not in result:
                result[substring] = [j1]
            result[substring].append(j2)
    return dict((k, sorted(v)) for k, v in result.items())
