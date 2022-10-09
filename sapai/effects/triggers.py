from enum import Enum, auto
from typing import List


class Trigger:
    """Base class to determine if an ability's effect should be triggered"""

    def is_triggered(
        self,
        trigger_type,
        *,
        current_pet=None,
        triggering_pet=None,
        triggering_food=None,
        friendly_team=None,
        enemy_team=None,
    ):
        return False


class AnyTrigger(Trigger):
    """Triggers if any of the given triggers are triggered"""

    def __init__(self, triggers: List[Trigger]):
        self._triggers = triggers

    def is_triggered(self, *args, **kwargs):
        for trigger in self._triggers:
            if trigger.is_triggered(*args, **kwargs):
                return True
        return False


class AllTrigger(Trigger):
    """Triggers if all of the given triggers are triggered"""

    def __init__(self, triggers: List[Trigger]):
        self._triggers = triggers

    def is_triggered(self, *args, **kwargs):
        for trigger in self._triggers:
            if not trigger.is_triggered(*args, **kwargs):
                return False
        return True


class TypeTrigger(Trigger):
    """Trigger based on a given trigger type"""

    def __init__(self, trigger_type: "TriggerType"):
        self._trigger_type = trigger_type

    def is_triggered(self, trigger_type, **kwargs):
        if trigger_type is self._trigger_type:
            return True
        return False


class SelfTrigger(TypeTrigger):
    """Trigger on type IF current pet is triggering pet"""

    def is_triggered(
        self,
        trigger_type,
        current_pet=None,
        triggering_pet=None,
        **kwargs,
    ):
        return (
            current_pet is not None
            and triggering_pet is not None
            and current_pet is triggering_pet
            and super().is_triggered(
                trigger_type, current_pet, triggering_pet, **kwargs
            )
        )


class TriggerCondition(Enum):
    NONE = auto()
    SELF = auto()
    FRIEND = auto()
    ENEMY = auto()


class TriggerType(Enum):
    NONE = auto()
    START_OF_BATTLE = auto()
    BEFORE_FRIEND_ATTACKS = auto()
    BEFORE_ATTACK = auto()
    FRIEND_AHEAD_ATTACKS = auto()
    HURT = auto()
    ENEMY_HURT = auto()
    FRIEND_HURT = auto()
    BEFORE_FAINT = auto()  # Before faint triggers like bee
    FAINT = auto()
    FRIEND_FAINTS = auto()  # counter for vulture
    KNOCKOUT = auto()
    SUMMONED = auto()
    FRIEND_SUMMONED = auto()
    ENEMY_SUMMONED = auto()
    ENEMY_PUSHED = auto()
    START_OF_TURN = auto()
    BUY = auto()  # Condition of tier 1
    EAT_SHOP_FOOD = auto()  # condition of apple
    FOOD_BOUGHT = auto()
    FRIEND_BOUGHT = auto()
    FRIEND_SOLD = auto()
    SELL = auto()
    ROLL = auto()
    UPGRADE_SHOP_TIER = auto()
    LEVEL_UP = auto()
    FRIEND_LEVEL_UP = auto()
    ENEMY_LEVEL_UP = auto()  # part 2 of jellyfish
    END_OF_TURN = auto()
    END_TURN = END_OF_TURN  # Is there a difference?

    FOOD_USED = auto()  # Cat ability
    FRIEND_AHEAD_USES_ABILITY = auto()  # Tiger ability
