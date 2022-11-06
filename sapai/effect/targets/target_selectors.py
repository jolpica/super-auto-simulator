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


class LeftMostTargetSelector(TargetSelector):
    """Selects the left-most (first) n targets"""

    def select(self, pets: list[Pet], n: int, rand: float = None) -> list[Pet]:
        self._validate_args(pets, n, rand)
        return pets[:n]


class RightMostTargetSelector(TargetSelector):
    """Selects the right-most (last) n targets"""

    def select(self, pets: list[Pet], n: int, rand: float = None) -> list[Pet]:
        self._validate_args(pets, n, rand)
        if n == 0:
            return []
        return pets[-n:]


class RandomTargetSelector(TargetSelector):
    """Selects n random pets from a list"""

    def random_selection(self, pets: list[Pet], n: int, rand: float) -> list[Pet]:
        if n >= len(pets):
            # return a copy of the input list
            return pets[:]
        comb = math.comb(len(pets), n)
        index = math.floor(rand * comb)
        return list(nth_combination(pets, n, index))

    def tiebreak_selection(
        self, items: tuple[Pet, int], n: int, rand: float
    ) -> list[Pet]:
        pass

    def select(self, pets: list[Pet], n: int, rand: float) -> list[Pet]:
        """Selects the combination at the index: floor(rand * (len(pets) Choose n))"""
        self._validate_args(pets, n, rand)
        return self.random_selection(pets, n, rand)


class HighestHealthTargetSelector(RandomTargetSelector):
    """Selects n pets with the highest health"""

    def __init__(self, highest_health=True) -> None:
        super().__init__()
        self.highest_health = highest_health

    def select(self, pets: list[Pet], n: int, rand: float = None) -> list[Pet]:
        self._validate_args(pets, n, rand)
        if n >= len(pets):
            return pets[:]
        pets_health = sorted(pets, key=lambda p: p.health, reverse=self.highest_health)
        # If there is a health draw at the cutoff point randomise the pets selected
        cutoff_health = pets_health[n - 1].health
        if cutoff_health == pets_health[n].health:
            tied_pets = [p for p in pets_health if p.health == cutoff_health]
            above_cutoff = [p for p in pets_health[:n] if p.health != cutoff_health]
            needed = n - len(above_cutoff)
            chosen = self.random_selection(tied_pets, needed, rand)
            return [*above_cutoff, *chosen]
        return pets_health[:n]
