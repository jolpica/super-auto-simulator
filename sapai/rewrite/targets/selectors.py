"""Module containing target selector definitions"""
from abc import ABC, abstractmethod
from enum import Enum, auto
import math

from sapai.pets import Pet
from sapai.rewrite.utils import nth_combination


class SelectorType(Enum):
    """Enumeration of types of selector"""

    FIRST = auto()
    LAST = auto()
    RANDOM = auto()
    HEALTH = auto()
    ATTACK = auto()
    STRENGTH = auto()

    @classmethod
    def _get_mapping(cls):
        return {
            cls.FIRST: FirstSelector,
            cls.LAST: LastSelector,
            cls.RANDOM: RandomSelector,
            cls.HEALTH: HealthSelector,
            cls.ATTACK: AttackSelector,
            cls.STRENGTH: StrengthSelector,
        }

    def to_class(self) -> "Selector":
        """Returns the Selector class corresponding to the enum value"""
        mapping = self._get_mapping()
        if self in mapping:
            class_ = mapping[self]
        else:
            raise NotImplementedError(f"{self} does not map to a class")
        return class_

    @classmethod
    def from_class(cls, class_) -> "SelectorType":
        """Returns the Type corresponding to the given class"""
        mapping = cls._get_mapping()
        for type_, map_class in mapping.items():
            if class_ is map_class:
                return type_
        raise NotImplementedError(f"{class_} does not map to a type")


class Selector(ABC):
    """Selects a target(s) from a list of possible targets"""

    def _validate_args(self, pets: list[Pet], num: int, rand: float):
        del pets
        if num < 0:
            raise ValueError("number of selected pets must be > 0")
        if rand < 0 or rand >= 1:
            raise ValueError("rand must be in the range [0,1)")

    @abstractmethod
    def select(self, pets: list[Pet], num: int, rand: float) -> list[Pet]:
        """Select n items from the given list of pets

        Args:
            pets (list[Pet]): List of pets to choose from
            num (int): Number of pets to select
            rand (int): Number to determine random effects.
                Must follow `0 >= rand and rand < 1`.

        Returns:
            list[Pet]: list of pets selected
        """
        raise NotImplementedError()

    def to_dict(self) -> dict:
        """Generates a dictionary representation of the selector

        Returns:
            dict: Selector's dictionary representation, of the form:
                {
                    "selector": The type/name of the filter
                }
        """
        return {"selector": SelectorType.from_class(type(self)).name}

    @staticmethod
    def from_dict(dict_: dict) -> "Selector":
        """Creates a selector from its dictionary representation

        Args:
            selector_dict (dict): dictionary representation to create selector from.

        Raises:
            ValueError: When given an invalid dictionary

        Returns:
            TargetFilter: Selector instance specified by selector_dict
        """
        types = [type_.name for type_ in SelectorType]
        print(types)
        if dict_.get("selector") not in types:
            raise ValueError("Invalid Selector dict representation ('selector' value)")

        class_ = SelectorType[dict_["selector"]].to_class()

        kwargs = {}
        if issubclass(class_, ValueSelector):
            if isinstance(dict_.get("highest"), bool):
                kwargs["highest"] = dict_.get("highest")
            else:
                raise ValueError(
                    "Invalid selector dict representation ('highest' value)"
                )

        return class_(**kwargs)


class FirstSelector(Selector):
    """Selects the left-most (first) n targets"""

    def select(self, pets: list[Pet], num: int, rand: float = None) -> list[Pet]:
        self._validate_args(pets, num, 0)
        return pets[:num]


class LastSelector(FirstSelector):
    """Selects the right-most (last) n targets"""

    def select(self, pets: list[Pet], num: int, rand: float = None) -> list[Pet]:
        return super().select(pets[::-1], num, rand)


class RandomSelector(Selector):
    """Selects n random pets from a list"""

    def _random_select(self, pets: list[Pet], num: int, rand: float) -> list[Pet]:
        if num >= len(pets):
            # return a copy of the input list
            return pets[:]
        comb = math.comb(len(pets), num)
        index = math.floor(rand * comb)
        return list(nth_combination(pets, num, index))

    def select(self, pets: list[Pet], num: int, rand: float) -> list[Pet]:
        """Selects the combination at the index: floor(rand * (len(pets) Choose n))"""
        self._validate_args(pets, num, rand)
        return self._random_select(pets, num, rand)


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
        self, items: list[tuple[Pet, int]], num: int, rand: float
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
        if num <= 0:
            return []
        # No excess pets to filter
        if len(items) <= num:
            return [p for p, _ in sorted_items]

        cutoff_value = sorted_items[num - 1][1]
        # If no tiebreak is needed for the top n items
        if cutoff_value != sorted_items[num][1]:
            return [p for p, _ in sorted_items[:num]]

        # If there is a tie at the cutoff point randomise the pets selected
        tied_pets = [p for p, val in sorted_items if val == cutoff_value]
        above_cutoff = [p for p, val in sorted_items[:num] if val != cutoff_value]
        needed = num - len(above_cutoff)
        chosen = self._random_select(tied_pets, num=needed, rand=rand)
        return [*above_cutoff, *chosen]

    @abstractmethod
    def select(self, pets: list[Pet], num: int, rand: float) -> list[Pet]:
        raise NotImplementedError()

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["highest"] = self._highest
        return result


class HealthSelector(ValueSelector):
    """Selects pets based on health"""

    def select(self, pets: list[Pet], num: int, rand: float) -> list[Pet]:
        self._validate_args(pets, num, rand)
        pet_value = [(p, p.health) for p in pets]
        return self._tiebreak_select(pet_value, num, rand)


class AttackSelector(ValueSelector):
    """Selects pets based on attack"""

    def select(self, pets: list[Pet], num: int, rand: float) -> list[Pet]:
        self._validate_args(pets, num, rand)
        pet_value = [(p, p.attack) for p in pets]
        return self._tiebreak_select(pet_value, num, rand)


class StrengthSelector(ValueSelector):
    """Selects pets based on value of attack + health"""

    def select(self, pets: list[Pet], num: int, rand: float) -> list[Pet]:
        self._validate_args(pets, num, rand)
        pet_value = [(p, p.attack + p.health) for p in pets]
        return self._tiebreak_select(pet_value, num, rand)
