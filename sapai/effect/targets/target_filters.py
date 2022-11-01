from abc import ABC, abstractmethod
from sapai.pets import Pet
from sapai.effect.events import Event


class TargetFilter(ABC):
    """Filters a list of possible targets based on criteria"""

    def __init__(self, owner: Pet):
        self._owner = owner

    @abstractmethod
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        pass


class MultiTargetFilter(TargetFilter):
    """Base class for a filter that applies a list of filters"""

    def __init__(self, owner: Pet, filters: list[TargetFilter]):
        super().__init__(owner)
        for f in filters:
            if not isinstance(f, TargetFilter):
                raise TypeError("filters must all be TargetFilter instances")
        # TODO: sort as order is irrelevant (implement __lt__ on TargetFilter)
        self._filters = filters


class AllTargetFilter(MultiTargetFilter):
    """Returns results that are unfiltered by all of the given filters (AND)
    returns all pets if given an empty list of filters"""

    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        for t_filter in self._filters:
            pets = t_filter.filter(pets, event)
        return [p for p in pets]


class AnyTargetFilter(MultiTargetFilter):
    """Returns results that are unfiltered by any of the given filters (OR)
    returns nothing if given an empty list of filters"""

    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        returned_pets = set()
        for t_filter in self._filters:
            returned_pets.update(t_filter.filter(pets, event))
        # Ensure that pet order is preserved
        return [p for p in pets if p in returned_pets]


class SelfFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        return [p for p in pets if p is self._owner]


class NotSelfFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        return [p for p in pets if p is not self._owner]


class FriendlyFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        if not event.pet_in_event_teams(self._owner):
            raise ValueError("Owner must be in at least 1 team to use FriendlyFilter")
        friendly_team, _ = event.get_ordered_teams(self._owner)
        return [p for p in pets if p in friendly_team]


class EnemyFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        if not event.pet_in_event_teams(self._owner):
            raise ValueError("Owner must be in at least 1 team to use EnemyFilter")
        _, enemy_team = event.get_ordered_teams(self._owner)
        return [p for p in pets if p in enemy_team]
