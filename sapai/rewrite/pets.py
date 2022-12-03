"""Module defining the Pet class"""


class Pet:
    """Pet class"""

    def __init__(self) -> None:
        self.name = ""
        self.tier = 1
        self._perm_attack = 1
        self._perm_health = 1

        self.ability = None
        self.perk = None

        self._temp_attack = 0
        self._temp_health = 0
        self.experience = 0
        self.level = 1

    @property
    def attack(self):
        return self._perm_attack + self._temp_attack

    @property
    def health(self):
        return self._perm_health + self._temp_health

    def add_stats(self, attack=0, health=0, temp_stats=False):
        """Add temporary or permanent attack / health stats to the pet

        Args:
            attack (int, optional): Attack to add
            health (int, optional): Health to add
            temp_stats (bool, optional): True if stats should be temporary until end of battle
        """
        if temp_stats:
            self._temp_attack += attack
            self._temp_health += health
        else:
            self._perm_attack += attack
            self._perm_health += health
