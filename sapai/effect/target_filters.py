from sapai.pets import Pet
from events import Event


class TargetFilter:
    """Filters a list of possible targets based on criteria"""

    def __init__(self, owner: Pet):
        self._owner = owner

    def filter(self, pets: list[Pet], event: Event):
        return [p for p in pets]


class SelfFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event):
        return [p for p in pets if p is self._owner]


class FriendlyFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event):
        friendly_team, _ = event.get_ordered_teams(self._owner)
        return [p for p in pets if p in friendly_team]


class EnemyFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event):
        _, enemy_team = event.get_ordered_teams(self._owner)
        return [p for p in pets if p in enemy_team]
