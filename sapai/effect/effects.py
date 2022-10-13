from sapai.pets import Pet
from sapai.effect.events import Event, EventType
from enum import Enum, auto


class Effect:
    def run_effect(self, target: "Target"):
        pass


class AddStatsEffect(Effect):
    def __init__(self, attack, health, level_multiply=True):
        self._attack = attack
        self._health = health
        self._level_multiply = level_multiply

    def run_effect(self, target: "Target"):
        pass


class EffectType(Enum):
    ADD_STATS = auto()
    ADD_TEMP_STATS = auto()
    SUMMON = auto()
    DAMAGE = auto()
