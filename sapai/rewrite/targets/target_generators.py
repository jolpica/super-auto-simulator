"""Module containing target generator definitions"""
from abc import ABC, abstractmethod
from enum import Enum, auto
from sapai.pets import Pet
from sapai.rewrite.events import Event

from .filters import Filter, NoneFilter
from .selectors import Selector


class TargetGeneratorType(Enum):
    """Enumeration of types of selector"""

    BATTLEFIELD = auto()

    @classmethod
    def _get_mapping(cls):
        return {
            cls.BATTLEFIELD: BattlefieldTargetGenerator,
        }

    def to_class(self) -> "TargetGenerator":
        """Returns the TargetFilter class corresponding to the enum value"""
        mapping = self._get_mapping()
        if self in mapping:
            class_ = mapping[self]
        else:
            raise NotImplementedError(f"{self} does not map to a class")
        return class_

    @classmethod
    def from_class(cls, class_) -> "TargetGeneratorType":
        """Returns the Type corresponding to the given class"""
        mapping = cls._get_mapping()
        for type_, map_class in mapping.items():
            if class_ is map_class:
                return type_
        raise NotImplementedError(f"{class_} does not map to a type")


class TargetGenerator(ABC):
    """Generates a target(s)"""

    def __init__(self, selector: Selector, filter_: Filter = None):
        self._selector = selector
        self._filter = filter_ if filter_ else NoneFilter(None)

    def _filter_select(self, pets: list[Pet], event: Event, num: int, rand: float):
        filtered = self._filter.filter(pets, event) if self._filter else pets
        return self._selector.select(filtered, num, rand)

    @abstractmethod
    def get(self, event: Event, num: int, rand: float):
        pass

    def to_dict(self):
        return {
            "target_generator": TargetGeneratorType.from_class(type(self)).name,
            "filter": self._filter.to_dict(),
            "selector": self._selector.to_dict(),
        }

    @staticmethod
    def from_dict(dict_: dict, owner: Pet) -> "TargetGenerator":
        """Creates a target generator from its dictionary representation

        Args:
            dict_ (dict): dictionary representation to create from.

        Raises:
            ValueError: When given an invalid dictionary

        Returns:
            TargetFilter: TargetGenerator instance specified by dict
        """
        selector = Selector.from_dict(dict_.get("selector"))
        filter_ = Filter.from_dict(dict_.get("filter"), owner)
        types = [type_.name for type_ in TargetGeneratorType]
        if dict_.get("target_generator") in types:
            class_ = TargetGeneratorType[dict_["target_generator"]].to_class()
        else:
            raise ValueError("Invalid TargetGenerator dict representation")

        return class_(owner, selector, filter_)


class BattlefieldTargetGenerator(TargetGenerator):
    """Generates target(s) from current battlefield teams"""

    def __init__(self, owner: Pet, selector: Selector, filter_: Filter = None):
        super().__init__(selector, filter_)
        self._owner = owner

    def get(self, event: Event, num: int, rand: float):
        friendly_team, enemy_team = event.get_ordered_teams(self._owner)
        pets = [*friendly_team[::-1], *enemy_team]
        return self._filter_select(pets, event, num, rand)
