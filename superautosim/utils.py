import math
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T", bound=Enum)
Y = TypeVar("Y")


class ClassMapMixin(Generic[Y]):
    """Helper class for Enums mapping to classes"""

    def to_class(self) -> type[Y]:
        """Returns the Selector class corresponding to the enum value"""
        return self.value

    @classmethod
    def from_class(cls: type[T], class_: type[Y]) -> T:
        """Returns the Type corresponding to the given class"""
        for type_ in cls:
            if type_.value is class_:
                return type_
        raise NotImplementedError(f"{class_} does not map to a type")


def nth_combination(iterable, r, index):
    """Returns the nth permutation of the given size from the list of items.

    Equivalent to list(combinations(iterable, r))[index].
    For example in the list [1,2,3], the first combination of size 2 would be
    [1,2], the second would be [1,3]

    Obtained from the itertools recipes found here:
    https://docs.python.org/3/library/itertools.html#itertools-recipes

    Args:
        iterable (Iterable): iterable of objects to get a combination of
        r (int): The size of the combination
        index (int): The index of the combination in the range of combinations
            Must be between 0 and `nCr - 1` - the total possible combinations (nCr).

    Raises:
        IndexError: When the index is out of bounds of list(combinations(iterable, r))

    returns:
        tuple: the nth combination of the iterable as determined by the index.
    """
    pool = tuple(iterable)
    n = len(pool)
    c = math.comb(n, r)
    if index < 0 or index >= c:
        raise IndexError
    result = []
    while r:
        c, n, r = c * r // n, n - 1, r - 1
        while index >= c:
            index -= c
            c, n = c * (n - r) // n, n - 1
        result.append(pool[-1 - n])
    return tuple(result)
