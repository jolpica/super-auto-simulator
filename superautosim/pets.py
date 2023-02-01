"""Module defining the Pet class"""


class Pet:
    """Pet class"""

    STAT_CAP = 50

    def __init__(self, name="", stats: tuple = None) -> None:
        self.name = name
        self.tier = 1

        self._perm_attack = 1
        self._perm_health = 1
        self._temp_attack = 0
        self._temp_health = 0
        if stats:
            if len(stats) == 2 or len(stats) == 4:
                self._perm_attack, self._perm_health = stats[:2]
            if len(stats) == 4:
                self._temp_attack, self._temp_health = stats[2:]

        self.ability = None
        self.perk = None

        self.experience = 0
        self.level = 1

    @property
    def attack(self):
        return self._perm_attack + self._temp_attack

    @property
    def health(self):
        return self._perm_health + self._temp_health

    @property
    def stats(self):
        return (
            self._perm_attack,
            self._perm_health,
            self._temp_attack,
            self._temp_health,
        )

    def add_stats(self, attack=0, health=0, temp_stats=False):
        """Add temporary or permanent attack / health stats to the pet

        Args:
            attack (int, optional): Attack to add
            health (int, optional): Health to add
            temp_stats (bool, optional): True if stats should be temporary until end of battle
        """
        # Ensure total stats don't go over STAT_CAP or under 1
        attack_added = min(self.STAT_CAP - self.attack, max(1 - self.attack, attack))
        health_added = min(self.STAT_CAP - self.health, max(1 - self.health, health))
        if temp_stats:
            self._temp_attack += attack_added
            self._temp_health += health_added
        else:
            # Logic to convert temp stats into perm stats
            if self.attack + attack >= self.STAT_CAP:
                attack_diff = attack - attack_added
                self._temp_attack -= attack_diff
                attack_added += attack_diff
            if self.health + health >= self.STAT_CAP:
                health_diff = health - health_added
                self._temp_health -= health_diff
                health_added += health_diff

            self._perm_attack += attack_added
            self._perm_health += health_added

    def __repr__(self) -> str:
        return f"{self.name}<{self.attack}-{self.health}>"
