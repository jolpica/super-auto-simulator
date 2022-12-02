from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional

from sapai.rewrite.events import Event
from .targets.target_generators import TargetGenerator


class Effect(ABC):
    @abstractmethod
    def run_effect(self, level: int, event: Event, rand: float):
        raise NotImplementedError()

class TargetedEffect(Effect):
    def __init__(self, target_generator: TargetGenerator, max_targets: int):
        self._target_generator = target_generator
        self._max_targets = max_targets


class AddStatsEffect(TargetedEffect):
    def __init__(self, target_generator: TargetGenerator, max_targets: int = 1, attack: int = 0, health: int = 0, level_multiply=True):
        super().__init__(target_generator, max_targets)
        self._attack = attack
        self._health = health
        self._level_multiply = level_multiply

    def run_effect(self, level: int, event: Event, rand: float):
        targets = self._target_generator.get(event, self._max_targets, rand)
        for pet in targets:
            pet.health += self._health * (level * self._level_multiply)
            pet.attack += self._attack * (level * self._level_multiply)


class EffectType(Enum):
    ADD_STATS = auto()
    ADD_TEMP_STATS = auto()
    SUMMON = auto()
    DAMAGE = auto()
