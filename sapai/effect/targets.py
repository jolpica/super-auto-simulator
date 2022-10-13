from dataclasses import dataclass, field
from enum import Flag, auto()
from sapai.foods import Food
from sapai.pets import Pet
from typing import Tuple
from .events import Event


@dataclass
class Target:
    """Class for providing target data"""

    pets: Tuple[Pet] = field(default_factory=tuple)
    foods: Tuple[Food] = field(default_factory=tuple)
    # shop_generator: ShopGenerator
    # shop_item: ShopItem


class TargetGenerator:
    def get_targets(self, event: Event, amount: int = 1) -> Target:
        return Target(
            pets=self.get_possible_pets(),
            foods=self.get_possible_foods(),
        )

    def get_possible_pets(self, event: Event, owner: Pet) -> list:
        return []

    def get_possible_foods(self, event: Event, owner: Pet) -> list:
        return []


class RandomTargetGenerator(TargetGenerator):
    pass
class LeftTargetGenerator(TargetGenerator):
    pass
class HighestHealthTargetGenerator(TargetGenerator):
    pass
class HighestAttackTargetGenerator(TargetGenerator):
    pass
class HighestStatsTargetGenerator(TargetGenerator):
    pass

class TargetType(Flag):
    SELF = auto()
    FRIENDLY = auto()
    ENEMY = auto()
    AHEAD =auto()
    BEHIND = auto()
    CURRENT_SHOP_PETS = auto()
    ALL_SHOP_PETS = auto()

class TargetModifier(Flag):
    HIGHEST_HEALTH = auto()



class FriendlyTargetGenerator(TargetGenerator):
    def get_targets(self, event: Event, amount: int = 1) -> Target:
        return super().get_targets(event, amount)

    def get_possible_targets(self, event: Event, owner: Pet) -> Target:
        friendly_team, _ = event.get_named_teams(owner)
        return [p for p in friendly_team if p is not owner]
