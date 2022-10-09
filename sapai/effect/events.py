from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Tuple
from sapai.pets import Pet
from sapai.foods import Food
from sapai.teams import Team


class EventType(Enum):
    NONE = auto()
    START_OF_BATTLE = auto()
    BEFORE_ATTACK = auto()
    ATTACK = auto()
    HURT = auto()
    BEFORE_FAINT = auto()
    FAINT = auto()
    KNOCKOUT = auto()
    SUMMONED = auto()
    PUSHED = auto()
    START_OF_TURN = auto()
    UPGRADE_SHOP_TIER = auto()
    BUY_PET = auto()  # Condition of tier 1
    BUY_FOOD = auto()
    EAT_SHOP_FOOD = auto()  # condition of apple
    SELL = auto()
    ROLL = auto()
    LEVEL_UP = auto()
    END_OF_TURN = auto()
    END_TURN = END_OF_TURN  # Is there a difference?


@dataclass
class Event:
    """Class for providing event data"""

    type: EventType
    pet: Pet = None
    food: Food = None
    in_battle: bool = False
    teams: Tuple[Team] = field(default_factory=tuple)

    def __post_init__(self):
        if len(self.teams) > 2:
            raise ValueError("Can only have a maximum of 2 teams")
