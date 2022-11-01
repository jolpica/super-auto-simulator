from dataclasses import dataclass, field
from sapai.foods import Food
from sapai.pets import Pet
from typing import Tuple


@dataclass
class Target:
    """Class for providing target data"""

    pets: Tuple[Pet] = field(default_factory=tuple)
    foods: Tuple[Food] = field(default_factory=tuple)

    # shop_generator: ShopGenerator
    # shop_item: ShopItem
