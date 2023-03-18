"""Module defining the Team class"""
from __future__ import annotations

from typing import Sequence

from superautosim.pets import Pet


class Team:
    """Class to represent a team of pets"""

    MAX_TEAM_SIZE = 5

    def __init__(self, pets: Sequence[Pet | None] | None = None) -> None:
        if pets is None:
            pets = []
        if len(pets) > self.MAX_TEAM_SIZE:
            raise ValueError("Team pets must be less than MAX_TEAM_SIZE")

        empty_slots = self.MAX_TEAM_SIZE - len(pets)
        # Slots always has a length of MAX_TEAM_SIZE
        self._slots: list[Pet | None] = list(pets) + [None] * empty_slots

    def summon_pet(self, pet: Pet, index: int) -> bool:
        """Summon a pet as close as possible to the given idx

        Args:
            pet (Pet): Pet to summon
            target_idx (int): Index of slot to attempt the summon.

        Returns:
            bool: True when the pet was successfully summoned.
        """
        self._validate_index(index)
        if None not in self._slots:
            return False

        if None in self._slots[:index]:
            index = max(0, index - 1)

        return self.insert_pet(pet, index)

    def insert_pet(self, pet: Pet, index: int) -> bool:
        """Insert the pet at the given index. Returns False if there is no space.

        If the team is full, return False. If a pet is already at the index, move it
        towards the back of the team to make space, if not possible then move it forwards.

        Args:
            pet (Pet): Pet to insert.
            index (int): Index to insert the pet

        Returns:
            bool: True if pet is successfully inserted. False otherwise.
        """
        self._validate_index(index)
        if len(self.pets) >= self.MAX_TEAM_SIZE:
            return False

        # Get the index of the first None value after the index, otherwise first None infront.
        if None in self._slots[index:]:
            index_to_remove = self._slots.index(None, index)
        else:
            index_to_remove = self.MAX_TEAM_SIZE - self._slots[::-1].index(None) - 1
        self._slots.pop(index_to_remove)

        self._slots.insert(index, pet)
        return True

    @property
    def pets(self) -> list[Pet]:
        return [p for p in self._slots if p]

    def _validate_index(self, index: int):
        if index < 0 or index >= self.MAX_TEAM_SIZE:
            raise IndexError("Invalid Team slot index")

    def __iter__(self):
        return iter(self._slots)

    def __getitem__(self, key):
        return self._slots.__getitem__(key)

    def __repr__(self) -> str:
        return f"Team<{self._slots}>"
