from text import longest_common_substring
from text._utils import suffix_array
import itertools


class HelperTestMixin:
    """
    author: Anonta (https://stackoverflow.com/users/5798361/anonta)
    source: https://stackoverflow.com/questions/51456472/python-fastest-algorithm-to-get-the-most-common-prefix-out-of-a-list-of-strings/51457611
    """

    def suffix_verify(self, text, step=16):
        tx = text
        sa, _, lcp = suffix_array(text=tx, _step=step)
        assert set(sa) == set(range(len(tx)))
        ok = True
        for i0, i1, h in zip(sa[:-1], sa[1:], lcp[1:]):
            assert tx[i1 : i1 + h] == tx[i0 : i0 + h]  # type: ignore
            assert tx[i1 + h : i1 + h + 1] > tx[i0 + h : i0 + h + 1]  # type: ignore

            assert max(i0, i1) <= len(tx) - h  # type: ignore

        assert ok == True


class TestSuffixArray(HelperTestMixin):
    """
    author: Anonta (https://stackoverflow.com/users/5798361/anonta)
    source: https://stackoverflow.com/questions/51456472/python-fastest-algorithm-to-get-the-most-common-prefix-out-of-a-list-of-strings/51457611
    """

    def test_16(self):
        # 'a' < 'ana' < 'anana' < 'banana' < 'na' < 'nana'
        expect = ([5, 3, 1, 0, 4, 2], [3, 2, 5, 1, 4, 0], [0, 1, 3, 0, 0, 2])
        assert suffix_array(text="banana", _step=16) == expect

    def test_1(self):
        expect = ([5, 3, 1, 0, 4, 2], [3, 2, 5, 1, 4, 0], [0, 1, 3, 0, 0, 2])
        assert suffix_array(text="banana", _step=1) == expect

    def test_mini(self):
        assert suffix_array(text="", _step=1) == ([], [], [])
        assert suffix_array(text="a", _step=1) == ([0], [0], [0])
        assert suffix_array(text="aa", _step=1) == ([1, 0], [1, 0], [0, 1])
        assert suffix_array(text="aaa", _step=1) == ([2, 1, 0], [2, 1, 0], [0, 1, 2])

    def test_example(self):
        self.suffix_verify("abracadabra")

    def test_cartesian(self):
        """Test all combinations of alphabet "ABC" up to length 4 characters"""
        for size in range(7):
            for cartesian in itertools.product(*(size * ["ABC"])):
                text = "".join(cartesian)
                self.suffix_verify(text, 1)

    def test_lcp(self):
        expect = {"ana": [1, 3]}
        assert longest_common_substring("banana") == expect
        expect = {" s": [3, 21], "no": [0, 13], "o ": [5, 20, 38]}
        assert longest_common_substring("not so Agamemnon, who spoke fiercely to ") == expect
