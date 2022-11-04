from sapai.pets import Pet
from sapai.effect.events import Event

from .target_filters import TargetFilter
from .target_selectors import TargetSelector
from .targets import Target


class TargetGenerator:
    """Generates a target(s)"""

    def __init__(self):
        self.target_filter: TargetFilter = None
        self.target_selector: TargetSelector = None

    def get_targets(self, event: Event, amount: int = 1) -> Target:
        return Target(
            pets=self.get_possible_pets(),
            foods=self.get_possible_foods(),
        )

    def get_possible_pets(self, event: Event, owner: Pet) -> list:
        return []

    def get_possible_foods(self, event: Event, owner: Pet) -> list:
        return []


class BattlefieldTargetGenerator(TargetGenerator):
    """Generates target(s) from current battlefield teams"""

    def __init__(self, target_filter: TargetFilter):
        self.target_filter = target_filter


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
