from abc import ABC, abstractmethod

from sapai.pets import Pet


class TargetSelector(ABC):
    """Selects a target(s) from a list of possible targets"""

    @abstractmethod
    def select(self, pets: list[Pet], n: int, seed: int = None) -> list[Pet]:
        pass


class FirstTargetSelector(TargetSelector):
    """Selects the first n targets"""

    def select(self, pets: list[Pet], n: int, seed: int = None) -> list[Pet]:
        if n <= 0:
            return []
        return pets[:n]


class LastTargetSelector(TargetSelector):
    """Selects the last n targets"""

    def select(self, pets: list[Pet], n: int, seed: int = None) -> list[Pet]:
        if n <= 0:
            return []
        return pets[-n:]


class RandomTargetSelector(TargetSelector):
    """Selects n random pets from a list"""

    def select(self, pets: list[Pet], n: int, seed: int = None) -> list[Pet]:
        pass


def nth_permutation(items: list, n: int, size: int):
    """Returns the nth permutation of the given size from the list of items.

    For example in the list [1,2,3], the first permutation of size 2 would be
    [1,2], the second would be [2,1]

    Args:
        items (list): _description_
        n (int): _description_
        size (int): _description_

    Returns:
        _type_: _description_
    """
    result = []
    for _ in range(size):
        item = n % len(items)
        n = n // len(items)
        result.append(items.pop(item))

    return result
