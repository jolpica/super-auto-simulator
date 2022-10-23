from dataclasses import dataclass, field
from enum import Flag, auto
from sapai.foods import Food
from sapai.pets import Pet
from typing import Tuple
from .events import Event
from .target_pools import TargetPool
from .target_filters import TargetFilter
from .target_selectors import TargetSelector


@dataclass
class Target:
    """Class for providing target data"""

    pets: Tuple[Pet] = field(default_factory=tuple)
    foods: Tuple[Food] = field(default_factory=tuple)
    # shop_generator: ShopGenerator
    # shop_item: ShopItem


class TargetGenerator:
    """Generates a target(s)"""

    def __init__(self) -> None:
        self.possible_targets: TargetPool = None
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
