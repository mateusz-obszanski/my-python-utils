from typing import Mapping as _Mapping, Callable as _Callable
import re as _re


def capitalized_first_letter_str(s: str, /) -> str:
    return s[0].upper() + s[1:] if s else ""


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
