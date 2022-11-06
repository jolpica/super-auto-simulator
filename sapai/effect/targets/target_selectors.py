from abc import ABC, abstractmethod

from sapai.pets import Pet


class TargetSelector(ABC):
    """Selects a target(s) from a list of possible targets"""

    @abstractmethod
    def select(self, pets: list[Pet], n: int, seed: int = None) -> list[Pet]:
        pass


class FirstTargetSelector(TargetSelector):
    """Selects the first n targets"""

    def select(self, pets: list[Pet], n: int, seed: int = None) -> list[Pet]:
        if n <= 0:
            return []
        return pets[:n]


class LastTargetSelector(TargetSelector):
    """Selects the last n targets"""

    def select(self, pets: list[Pet], n: int, seed: int = None) -> list[Pet]:
        if n <= 0:
            return []
        return pets[-n:]


class RandomTargetSelector(TargetSelector):
    """Selects n random pets from a list"""

    def select(self, pets: list[Pet], n: int, seed: int = None) -> list[Pet]:
        pass
