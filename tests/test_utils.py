from itertools import combinations

import pytest

from superautosim.utils import nth_combination


def test_nth_combination():
    items = [(i,) for i in range(10)]
    for r in [2, 5, 9, 10]:
        expected = list(combinations(items, r))
        for i in range(len(expected)):
            assert nth_combination(items, r, i) == expected[i]


def test_nth_combination_index_error():
    items = [(i,) for i in range(10)]
    with pytest.raises(IndexError):
        nth_combination(items, 5, -1)
    for r in [2, 5, 9, 10]:
        expected = list(combinations(items, r))
        with pytest.raises(IndexError):
            nth_combination(items, r, len(expected))
