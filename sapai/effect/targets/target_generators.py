from abc import ABC, abstractmethod
from sapai.pets import Pet
from sapai.effect.events import Event

from .target_filters import TargetFilter
from .target_selectors import Selector


class TargetGenerator(ABC):
    """Generates a target(s)"""

    def __init__(self, filter_: TargetFilter, selector: Selector):
        self._filter = filter_
        self._selector = selector

    def _filter_select(self, pets: list[Pet], event: Event, n: int, rand: float):
        filtered = self._filter.filter(pets, event)
        return self._selector.select(filtered, n, rand)

    @abstractmethod
    def get(self, event: Event, n: int, rand: float):
        pass


class BattlefieldTargetGenerator(TargetGenerator):
    """Generates target(s) from current battlefield teams"""

    def __init__(self, filter_: TargetFilter, selector: Selector, owner: Pet):
        super().__init__(filter_, selector)
        self._owner = owner

    def get(self, event: Event, n: int, rand: float):
        friendly_team, enemy_team = event.get_ordered_teams(self._owner)
        pets = [*friendly_team[::-1], *enemy_team]
        return self._filter_select(pets, event, n, rand)


target = {
    "possible_targets": [
        "self",
        "friendly",
        "enemy",
        "current_shop",
        "ahead",
        "behind",
    ],
    "filters": ["level", "ability_type"],
    "selectors": ["first", "last", "random", "HIGHEST_HEALTH"],
}
