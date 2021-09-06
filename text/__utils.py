from typing import (
    Annotated as _Annotated,
    Callable as _Callable,
    Optional as _Optional,
    Union as _Union,
)
from itertools import groupby
from operator import itemgetter


_Char = _Annotated[str, "length == 1"]
_Natural = _Annotated[int, ">= 0"]


class Trie:
    """
    Helper class for string suffixes trie.

    Examples
    --------
    >>> strings = ['file_1', 'file_2', 'file_3', 'not_a_file_1', 'not_a_file_2']
    >>> min_length_of_prefix = 6
    >>> trie = Trie()
    >>> for s in strings:
    >>> trie.insert(s)
    >>> prefixes = trie.getPrefixes(min_length_of_prefix)
    >>> print(prefixes)
    [('not_a_file_', 2), ('not_a_file', 2), ('not_a_fil', 2), ('not_a_fi', 2), ('not_a_f', 2), ('not_a_', 2), ('not_a_file_2', 1), ('not_a_file_1', 1), ('file_3', 1), ('file_2', 1), ('file_1', 1)]


    author: Anonta (https://stackoverflow.com/users/5798361/anonta)
    source: https://stackoverflow.com/questions/51456472/python-fastest-algorithm-to-get-the-most-common-prefix-out-of-a-list-of-strings/51457611
    """

    class _TrieNode:
        """
        Helper class for string suffixes trie.

        author: Anonta (https://stackoverflow.com/users/5798361/anonta)
        source: https://stackoverflow.com/questions/51456472/python-fastest-algorithm-to-get-the-most-common-prefix-out-of-a-list-of-strings/51457611
        """

        def __init__(self, character: _Char) -> None:
            self.count = 1
            self.character = character
            self.children: dict[_Char, Trie._TrieNode] = {}

        def insert(self, string: str, idx: _Natural) -> None:
            if idx >= len(string):
                return

            child = string[idx]
            if child in self.children:
                self.children[child].count += 1
            else:
                self.children[child] = Trie._TrieNode(string[idx])

            self.children[child].insert(string, idx + 1)

    def __init__(self) -> None:
        self.__root = Trie._TrieNode("")
        self._prefixes: _Optional[dict[str, int]] = None

    def insert(self, /, *strings: str) -> None:
        for string in strings:
            self.__root.insert(string, 0)

    # just a wrapper function
    def getPrefixesByOccurences(
        self, min_len: _Natural, ascending_order=False
    ) -> list[tuple[str, _Natural]]:
        # pair of prefix, and frequency
        # prefixes shorter than min_length are not stored
        self._prefixes_with_occurences = {}

        self.__discoverPrefixes(self.__root, [], min_len, 0)

        # return the prefixes in sorted order
        reversed_items: _Callable[[tuple[str, _Natural]], tuple[_Natural, str]] = lambda x: (
            x[1],
            x[0],
        )

        return sorted(
            self._prefixes_with_occurences.items(),
            key=reversed_items,
            reverse=not ascending_order,
        )

    # do a dfa search on the trie
    # discovers the prefixes in the trie and stores them in the self.prefixes dictionary
    def __discoverPrefixes(
        self,
        node: _TrieNode,
        prefix_characters: list[str],
        min_length: _Natural,
        actual_len: _Natural,
    ) -> None:
        if actual_len >= min_length:
            self._prefixes_with_occurences[
                "".join(prefix_characters) + node.character
            ] = node.count

        for char_node in node.children.values():
            prefix_characters.append(node.character)
            self.__discoverPrefixes(char_node, prefix_characters, min_length, actual_len + 1)
            prefix_characters.pop()


def suffix_array(text: str, _step: int = 16):
    """
    Find the longest repeated substring.
    "Efficient way to find longest duplicate string for Python (From Programming Pearls)"
    http://stackoverflow.com/questions/13560037/
    The algorithm is based on "Prefix doubling".
    The worst time complexity is O(n (log n)^2). Memory requirements are linear.

    Analyze all common strings in the text.
    Short substrings of the length _step a are first pre-sorted. The are the
    results repeatedly merged so that the garanteed number of compared
    characters bytes is doubled in every iteration until all substrings are
    sorted exactly.
    Arguments:
        text:  The text to be analyzed.
        _step: Is only for optimization and testing. It is the optimal length
               of substrings used for initial pre-sorting. The bigger value is
               faster if there is enough memory. Memory requirements are
               approximately (estimate for 32 bit Python 3.3):
                   len(text) * (29 + (_size + 20 if _size > 2 else 0)) + 1MB
    Return value:      (tuple)
      (sa, rsa, lcp)
        sa:  Suffix array                  for i in range(1, size):
               assert text[sa[i-1]:] < text[sa[i]:]
        rsa: Reverse suffix array          for i in range(size):
               assert rsa[sa[i]] == i
        lcp: Longest common prefix         for i in range(1, size):
               assert text[sa[i-1]:sa[i-1]+lcp[i]] == text[sa[i]:sa[i]+lcp[i]]
               if sa[i-1] + lcp[i] < len(text):
                   assert text[sa[i-1] + lcp[i]] < text[sa[i] + lcp[i]]
    >>> suffix_array(text='banana')
    ([5, 3, 1, 0, 4, 2], [3, 2, 5, 1, 4, 0], [0, 1, 3, 0, 0, 2])
    Explanation: 'a' < 'ana' < 'anana' < 'banana' < 'na' < 'nana'
    The Longest Common String is 'ana': lcp[2] == 3 == len('ana')
    It is between  tx[sa[1]:] == 'ana' < 'anana' == tx[sa[2]:]

    author: https://gist.github.com/hynekcer
    source: https://gist.github.com/hynekcer/fa340f3b63826168ffc0c4b33310ae9c
    """
    tx = text
    size = len(tx)
    step = min(max(_step, 1), len(tx))
    sa = list(range(len(tx)))
    sa.sort(key=lambda i: tx[i : i + step])
    grpstart = size * [False] + [True]  # a boolean map for iteration speedup.
    # It helps to skip yet resolved values. The last value True is a sentinel.
    rsa: list[_Union[int, None]] = size * [None]  # type: ignore
    stgrp, igrp = "", 0
    for i, pos in enumerate(sa):
        st = tx[pos : pos + step]
        if st != stgrp:
            grpstart[igrp] = igrp < i - 1
            stgrp = st
            igrp = i
        rsa[pos] = igrp
        sa[i] = pos
    grpstart[igrp] = igrp < size - 1 or size == 0
    while grpstart.index(True) < size:
        # assert step <= size
        nmerge = 0
        nextgr = grpstart.index(True)
        while nextgr < size:
            igrp = nextgr
            nextgr = grpstart.index(True, igrp + 1)
            glist = []
            for ig in range(igrp, nextgr):
                pos = sa[ig]
                if rsa[pos] != igrp:
                    break
                newgr = rsa[pos + step] if pos + step < size else -1
                glist.append((newgr, pos))
            glist.sort()
            for ig, g in groupby(glist, key=itemgetter(0)):
                g = [x[1] for x in g]
                sa[igrp : igrp + len(g)] = g
                grpstart[igrp] = len(g) > 1
                for pos in g:
                    rsa[pos] = igrp
                igrp += len(g)
            nmerge += len(glist)
        step *= 2
    del grpstart
    # create LCP array
    lcp = size * [None]
    h = 0
    for i in range(size):
        if rsa[i] > 0:  # type: ignore
            j = sa[rsa[i] - 1]  # type: ignore
            while i != size - h and j != size - h and tx[i + h] == tx[j + h]:
                h += 1
            lcp[rsa[i]] = h  # type: ignore
            if h > 0:
                h -= 1
    if size > 0:
        lcp[0] = 0  # type: ignore
    return sa, rsa, lcp
