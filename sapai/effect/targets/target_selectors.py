from abc import ABC, abstractmethod
import math

from sapai.pets import Pet
from sapai.effect.utils import nth_combination


class Selector(ABC):
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


class LeftMostSelector(Selector):
    """Selects the left-most (first) n targets"""

    def select(self, pets: list[Pet], n: int, rand: float = None) -> list[Pet]:
        self._validate_args(pets, n, rand)
        return pets[:n]


class RightMostSelector(Selector):
    """Selects the right-most (last) n targets"""

    def select(self, pets: list[Pet], n: int, rand: float = None) -> list[Pet]:
        self._validate_args(pets, n, rand)
        if n == 0:
            return []
        return pets[-n:]


class RandomSelector(Selector):
    """Selects n random pets from a list"""

    def _random_select(self, pets: list[Pet], n: int, rand: float) -> list[Pet]:
        if n >= len(pets):
            # return a copy of the input list
            return pets[:]
        comb = math.comb(len(pets), n)
        index = math.floor(rand * comb)
        return list(nth_combination(pets, n, index))

    def select(self, pets: list[Pet], n: int, rand: float) -> list[Pet]:
        """Selects the combination at the index: floor(rand * (len(pets) Choose n))"""
        self._validate_args(pets, n, rand)
        return self._random_select(pets, n, rand)


class ValueSelector(RandomSelector):
    """Base class for selecting based on a given value"""

    def __init__(self, highest: bool = True):
        """Initialises a value selector

        Args:
            highest (bool): Whether highest or lowest values should be selected.
        """
        super().__init__()
        self._highest = highest

    def _tiebreak_select(
        self, items: list[tuple[Pet, int]], n: int, rand: float
    ) -> list[Pet]:
        """Selects the top n items values, using a random select to break any ties

        Args:
            items (list[tuple[Pet, int]]): List of pet, value tuples. With the
                value determining the sort order.
            n (int): Number of pets to select
            rand (float): Number to determine random effects.
                Must follow `0 >= rand and rand < 1`.
            highest (bool, optional): Wheter to return the highest or lowest items.

        Returns:
            list[Pet]: The highest (or lowest) n pets in the list of items.
        """
        sorted_items = sorted(items, key=lambda i: i[1], reverse=self._highest)
        if n <= 0:
            return []
        # No excess pets to filter
        if len(items) <= n:
            return [p for p, _ in sorted_items]

        cutoff_value = sorted_items[n - 1][1]
        # If no tiebreak is needed for the top n items
        if cutoff_value != sorted_items[n][1]:
            return [p for p, _ in sorted_items[:n]]

        # If there is a tie at the cutoff point randomise the pets selected
        tied_pets = [p for p, val in sorted_items if val == cutoff_value]
        above_cutoff = [p for p, val in sorted_items[:n] if val != cutoff_value]
        needed = n - len(above_cutoff)
        chosen = self._random_select(tied_pets, n=needed, rand=rand)
        return [*above_cutoff, *chosen]

    @abstractmethod
    def select(self, pets: list[Pet], n: int, rand: float) -> list[Pet]:
        pass


class HealthSelector(ValueSelector):
    """Selects pets based on health"""

    def select(self, pets: list[Pet], n: int, rand: float = None) -> list[Pet]:
        self._validate_args(pets, n, rand)
        pet_health = [(p, p.health) for p in pets]
        return self._tiebreak_select(pet_health, n, rand)
