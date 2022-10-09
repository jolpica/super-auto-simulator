from enum import Enum, auto
from typing import List
from sapai.pets import Pet
from sapai.effect.events import Event, EventType


class Trigger:
    """Base class to determine if an ability's effect should be triggered"""

    def is_triggered(self, event: Event, owner: Pet = None):
        """Determines if the given conditions should trigger an effect

        Args:
            event (Event): Information about the triggered event such
                as the type of event, the source pet, which food was used,
                whether a battle is in progress and the teams involved.
            owner (Pet, optional): The pet who owns the trigger.

        Returns:
            bool: Whether the event is triggered.
        """
        return False


class AnyTrigger(Trigger):
    """Triggers if any of the given triggers are triggered"""

    def __init__(self, triggers: List[Trigger]):
        self._triggers = triggers

    def is_triggered(self, event: Event, owner: Pet = None):
        for trigger in self._triggers:
            if trigger.is_triggered(event, owner):
                return True
        return False


class AllTrigger(Trigger):
    """Triggers if all of the given triggers are triggered"""

    def __init__(self, triggers: List[Trigger]):
        self._triggers = triggers

    def is_triggered(self, event: Event, owner: Pet = None):
        for trigger in self._triggers:
            if not trigger.is_triggered(event, owner):
                return False
        return True


class LimitedTrigger(Trigger):
    """Only triggers a maximum number of time between events"""

    def __init__(
        self,
        trigger: Trigger,
        limit=3,
        reset_event: EventType = EventType.START_OF_TURN,
    ):
        self._trigger = trigger
        self._reset_event = reset_event
        self.limit = limit
        self.remaining_limit = self.limit

    def reset_limit(self):
        self.remaining_limit = self.limit

    def is_triggered(self, event: Event, owner: Pet = None):
        if event.type is self._reset_event:
            self.reset_limit()

        return self._trigger.is_triggered(event, owner)


class CountNTrigger(Trigger):
    """Only triggers once every N activations of the given trigger"""

    def __init__(
        self, trigger: Trigger, n=3, reset_event: EventType = EventType.START_OF_TURN
    ):
        self._trigger = trigger
        self._reset_event = reset_event
        self.n = n
        self.count = 0

    def reset_count(self):
        self.count = self.n

    def is_triggered(self, event: Event, owner: Pet = None):
        if event.type is self._reset_event:
            self.reset_count()

        if self._trigger.is_triggered(event, owner):
            self.count += 1

            if self.count >= self.n:
                self.reset_count()
                return True
        return False


class TypeTrigger(Trigger):
    """Trigger based on a given trigger event type"""

    def __init__(self, event_type: EventType):
        self._event_type = event_type

    def is_triggered(self, event: Event, owner: Pet = None):
        return event.type is self._event_type


class SelfTrigger(TypeTrigger):
    """Trigger on type IF current pet is triggering pet"""

    def is_triggered(self, event: Event, owner: Pet = None):
        if not super().is_triggered(event, owner):
            return False
        return None not in (owner, event.pet) and owner is event.pet


class FriendlyTrigger(TypeTrigger):
    """Trigger on type IF triggering pet is a non-owner friendly pet"""

    def is_triggered(self, event: Event, owner: Pet = None):
        if not super().is_triggered(event, owner):
            return False

        friendly_team = None
        for team in event.teams:
            if owner in team:
                friendly_team = team
                break

        return (
            None not in (friendly_team, owner, event.pet)
            and owner is not event.pet
            and event.pet in friendly_team
        )


class EnemyTrigger(TypeTrigger):
    """Trigger on type IF triggering pet is an enemy pet"""

    def is_triggered(self, event: Event, owner: Pet = None):
        if not super().is_triggered(event, owner):
            return False

        enemy_team = None
        for team in event.teams:
            if owner not in team:
                enemy_team = team
                break

        return None not in (enemy_team, owner, event.pet) and event.pet in enemy_team


class AheadTrigger(TypeTrigger):
    """Trigger on type IF triggering pet is ahead"""

    def is_triggered(self, event: Event, owner: Pet = None):
        if not super().is_triggered(event, owner):
            return False

        if len(event.teams) == 0:
            return False
        elif len(event.teams) == 1:
            friendly_team = event.teams[0]
        else:  # 2 teams
            if owner in event.teams[0]:
                friendly_team, enemy_team = event.teams
            elif owner in event.teams[1]:
                enemy_team, friendly_team = event.teams
            else:
                raise ValueError("Trigger owner must be in at least 1 event team")

        pet_order = friendly_team[::-1] + enemy_team[::1]
        for pet, pet_ahead in zip(pet_order, pet_order[1:]):
            if pet is owner:
                return pet_ahead is event.pet

        return False


class TriggerCondition(Enum):
    NONE = auto()
    SELF = auto()
    FRIEND = auto()
    ENEMY = auto()
