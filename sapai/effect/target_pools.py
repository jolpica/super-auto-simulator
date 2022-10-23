class TargetPool:
    """Generates a list of possible targets"""


class FriendlyTargetPool(TargetPool):
    def get_targets(self, event: "Event", owner: "Pet") -> "Target":
        friendly_team, _ = event.get_named_teams(owner)
        return [p for p in friendly_team if p is not owner]
