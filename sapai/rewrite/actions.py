from abc import ABC, abstractmethod
from enum import Enum, auto

from sapai.rewrite.events import Event
from .targets.target_generators import TargetGenerator


class ActionType(Enum):
    ADD_STATS = auto()
    ADD_TEMP_STATS = auto()
    SUMMON = auto()
    DAMAGE = auto()


class Action(ABC):
    @abstractmethod
    def run_effect(self, level: int, event: Event, rand: float):
        raise NotImplementedError()


class TargetedAction(Action):
    def __init__(self, target_generator: TargetGenerator, max_targets: int):
        self._target_generator = target_generator
        self._max_targets = max_targets


class AddStatsAction(TargetedAction):
    def __init__(
        self,
        target_generator: TargetGenerator,
        max_targets: int = 1,
        attack: int = 0,
        health: int = 0,
        level_multiply=True,
        temp_stats=False,
    ):
        super().__init__(target_generator, max_targets)
        self._attack = attack
        self._health = health
        self._level_multiply = level_multiply
        self._temp_stats = temp_stats

    def run_effect(self, level: int, event: Event, rand: float):
        targets = self._target_generator.get(event, self._max_targets, rand)
        health_buff = self._health * (level * self._level_multiply)
        attack_buff = self._attack * (level * self._level_multiply)
        for pet in targets:
            pet.add_stats(attack_buff, health_buff, self._temp_stats)
