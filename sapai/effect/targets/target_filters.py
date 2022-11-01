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


class AllTargetFilter(TargetFilter):
    pass


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
