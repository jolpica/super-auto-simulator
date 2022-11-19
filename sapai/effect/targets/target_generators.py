from abc import ABC, abstractmethod
from enum import Enum, auto
from sapai.pets import Pet
from sapai.effect.events import Event

from .target_filters import TargetFilter, NoneFilter
from .target_selectors import Selector


class TargetGeneratorType(Enum):
    """Enumeration of types of selector"""

    BATTLEFIELD = auto()

    def to_class(self) -> "TargetGenerator":
        """Returns the Selector class corresponding to the enum value"""
        if self is self.BATTLEFIELD:
            class_ = BattlefieldTargetGenerator
        else:
            raise NotImplementedError(f"{self} does not map to a class")
        return class_


class TargetGenerator(ABC):
    """Generates a target(s)"""

    def __init__(self, selector: Selector, filter_: TargetFilter = None):
        self._selector = selector
        self._filter = filter_ if filter_ else NoneFilter(None)

    def _filter_select(self, pets: list[Pet], event: Event, n: int, rand: float):
        filtered = self._filter.filter(pets, event) if self._filter else pets
        return self._selector.select(filtered, n, rand)

    @abstractmethod
    def get(self, event: Event, n: int, rand: float):
        pass

    def to_dict(self):
        return {
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
        filter_ = TargetFilter.from_dict(dict_.get("filter"), owner)
        types = [type_.name for type_ in TargetGeneratorType]
        if dict_.get("target_generator") in types:
            class_ = TargetGeneratorType[dict_["target_generator"]].to()
        else:
            raise ValueError("Invalid TargetGenerator dict representation")

        return class_(owner, selector, filter_)


class BattlefieldTargetGenerator(TargetGenerator):
    """Generates target(s) from current battlefield teams"""

    def __init__(self, owner: Pet, selector: Selector, filter_: TargetFilter = None):
        super().__init__(selector, filter_)
        self._owner = owner

    def get(self, event: Event, n: int, rand: float):
        friendly_team, enemy_team = event.get_ordered_teams(self._owner)
        pets = [*friendly_team[::-1], *enemy_team]
        return self._filter_select(pets, event, n, rand)

    def to_dict(self):
        result = super().to_dict()
        result["target_generator"] = "BATTLEFIELD"
        return result
