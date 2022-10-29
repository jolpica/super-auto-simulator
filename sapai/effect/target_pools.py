from events import Event
from sapai.pets import Pet
from targets import Target


class TargetPool:
    """Generates a list of possible targets"""


class AllTargetPool(TargetPool):
    def get_targets(self, event: Event, owner: Pet) -> Target:
        friendly_team, enemy_team = event.get_named_teams(owner)
        return friendly_team[::-1] + enemy_team


# class FriendlyTargetPool(TargetPool):
#     def get_targets(self, event: Event, owner: Pet) -> Target:
#         friendly_team, _ = event.get_named_teams(owner)
#         return friendly_team


# class EnemyTargetPool(TargetPool):
#     def get_targets(self, event: Event, owner: Pet) -> Target:
#         _, enemy_team = event.get_named_teams(owner)
#         return enemy_team


# class SelfTargetPool(TargetPool):
#     def get_targets(self, event: Event, owner: Pet) -> Target:
#         assert event.pet_in_teams(owner)
#         return [owner]
