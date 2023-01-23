"""Module defining the Team class"""
from __future__ import annotations

from typing import Sequence

from sapai.rewrite.pets import Pet


class Team:
    """Class to represent a team of pets"""

    MAX_TEAM_SIZE = 5

    def __init__(self, pets: Sequence[Pet | None] = None) -> None:
        if pets is None:
            pets = []
        if len(pets) > self.MAX_TEAM_SIZE:
            raise ValueError("Team pets must be less than MAX_TEAM_SIZE")

        empty_slots = self.MAX_TEAM_SIZE - len(pets)
        self._slots: list[Pet | None] = list(pets) + [None] * empty_slots

    def __iter__(self):
        return iter(self._slots)
