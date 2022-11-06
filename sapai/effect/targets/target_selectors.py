from abc import ABC, abstractmethod
import math

from sapai.pets import Pet
from sapai.effect.utils import nth_combination


class TargetSelector(ABC):
    """Selects a target(s) from a list of possible targets"""

    def _validate_args(self, pets, n, rand):
        if n < 0:
            raise ValueError("number of selected pets must be > 0")
        if rand is not None and (rand < 0 or rand >= 1):
            raise ValueError("rand must be in the range [0,1)")

    @abstractmethod
    def select(self, pets: list[Pet], n: int, rand: float) -> list[Pet]:
        """Select n items from the given list of pets

        Args:
            pets (list[Pet]): List of pets to choose from
            n (int): Number of pets to select
            rand (int): Number to determine random effects.
                Must follow `0 >= rand and rand < 1`.

        Returns:
            list[Pet]: _description_
        """
        pass


class FirstTargetSelector(TargetSelector):
    """Selects the first n targets"""

    def select(self, pets: list[Pet], n: int, rand: float = None) -> list[Pet]:
        self._validate_args(pets, n, rand)
        return pets[:n]


class LastTargetSelector(TargetSelector):
    """Selects the last n targets"""

    def select(self, pets: list[Pet], n: int, rand: float = None) -> list[Pet]:
        self._validate_args(pets, n, rand)
        if n == 0:
            return []
        return pets[-n:]


class RandomTargetSelector(TargetSelector):
    """Selects n random pets from a list"""

    def select(self, pets: list[Pet], n: int, rand: float) -> list[Pet]:
        """Selects the combination at the index: floor(rand * (len(pets) Choose n))"""
        self._validate_args(pets, n, rand)
        n = min(n, len(pets))
        comb = math.comb(len(pets), n)
        index = math.floor(rand * comb)
        result = nth_combination(pets, n, index)
        return list(result)
