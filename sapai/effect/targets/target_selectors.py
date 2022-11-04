from abc import ABC, abstractmethod

from sapai.pets import Pet


class TargetSelector(ABC):
    """Selects a target(s) from a list of possible targets"""

    @abstractmethod
    def select(pets: list[Pet], n: int) -> list[Pet]:
        pass


# class RandomTargetSelector(TargetSelector):
