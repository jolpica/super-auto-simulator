from enum import Enum, auto
from dataclasses import dataclass, field
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
    teams: tuple[Team] = field(default_factory=tuple)

    def __post_init__(self):
        if len(self.teams) > 2:
            raise ValueError("teams must be a tuple of at most 2 teams of pets")

    def pet_in_event_teams(self, pet: Pet) -> bool:
        for team in self.teams:
            if pet in team:
                return True
        return False

    def get_ordered_teams(self, pet: Pet) -> tuple[list[Pet], list[Pet]]:
        """Return 2-tuple of friendly and enemy team determined by given pet

        Args:
            pet (Pet): The pet the team order should be relative to.
                The given pet will always be found in the first team in the
                given tuple (the friendly team).

        Raises:
            ValueError: given pet is not in either Team

        Returns:
            Tuple[List[Pet], List[Pet]]: Tuple of friendly team and enemy team
                with enemy team an empty list if not provided.
        """
        if len(self.teams) > 0 and pet in self.teams[0]:
            friendly_team = self.teams[0]
            enemy_team = [] if len(self.teams) == 1 else self.teams[1]
        elif len(self.teams) > 1 and pet in self.teams[1]:
            enemy_team, friendly_team = self.teams
        else:
            raise ValueError("pet must be in at least 1 event team")
        return (friendly_team, enemy_team)
