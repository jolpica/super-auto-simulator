from enum import Enum, auto
from typing import List, Union
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


class AlwaysTrigger(Trigger):
    """Always triggers, regardless of event or owner"""

    def is_triggered(self, event: Event, owner: Pet = None):
        return True


class MultiTrigger(Trigger):
    """Base class for a trigger that takes a list of triggers"""

    def __init__(self, triggers: List[Trigger]):
        for t in triggers:
            if not isinstance(t, Trigger):
                raise TypeError("triggers must all be Trigger instances")
        self._triggers = triggers


class AnyTrigger(MultiTrigger):
    """Triggers if any of the given triggers are triggered"""

    def is_triggered(self, event: Event, owner: Pet = None):
        for trigger in self._triggers:
            if trigger.is_triggered(event, owner):
                return True
        return False


class AllTrigger(MultiTrigger):
    """Triggers if all of the given triggers are triggered"""

    def is_triggered(self, event: Event, owner: Pet = None):
        for trigger in self._triggers:
            if not trigger.is_triggered(event, owner):
                return False
        return len(self._triggers) > 0


class TypeTrigger(Trigger):
    """Trigger based on a given trigger event type"""

    def __init__(self, event_type: EventType):
        self._event_type = event_type

    def is_triggered(self, event: Event, owner: Pet = None):
        return event and event.type is self._event_type


class ModifierTrigger(Trigger):
    """Base class for a trigger that modifies another trigger"""

    def __init__(self, trigger: Union[Trigger, EventType]):
        if isinstance(trigger, EventType):
            # Create a type trigger
            self._trigger = TypeTrigger(trigger)
        elif isinstance(trigger, Trigger):
            self._trigger = trigger
        else:
            raise ValueError("trigger must be of type Trigger or EventType")

    def is_triggered(self, event: Event, owner: Pet = None):
        return self._trigger.is_triggered(event, owner)


class LimitedTrigger(ModifierTrigger):
    """Only triggers a maximum number of times between events"""

    def __init__(
        self,
        trigger: Trigger,
        limit=3,
        reset_event: EventType = EventType.START_OF_TURN,
    ):
        super().__init__(trigger)
        self._reset_event = reset_event
        self.limit = limit
        self.remaining_limit = self.limit

    def reset_limit(self):
        self.remaining_limit = self.limit

    def is_triggered(self, event: Event, owner: Pet = None):
        if event.type is self._reset_event:
            self.reset_limit()

        if self.remaining_limit <= 0:
            return False

        is_triggered = super().is_triggered(event, owner)
        if is_triggered:
            self.remaining_limit -= 1
        return is_triggered


class CountNTrigger(ModifierTrigger):
    """Only triggers once every N activations of the given trigger"""

    def __init__(
        self,
        trigger: Trigger,
        n: int = 3,
        reset_event: EventType = EventType.START_OF_TURN,
    ):
        super().__init__(trigger)
        self._reset_event = reset_event
        self.n = n
        self.count = 0

    def reset_count(self):
        self.count = 0

    def is_triggered(self, event: Event, owner: Pet = None):
        if event.type is self._reset_event:
            self.reset_count()

        if super().is_triggered(event, owner):
            self.count += 1

            if self.count >= self.n:
                self.reset_count()
                return True
        return False


class SelfTrigger(ModifierTrigger):
    """Trigger on type IF event pet is owner pet"""

    def is_triggered(self, event: Event, owner: Pet = None):
        if not super().is_triggered(event, owner):
            return False
        return None not in (owner, event.pet) and owner is event.pet


class FriendlyTrigger(ModifierTrigger):
    """Trigger on type IF event pet is a *non-owner* friendly pet"""

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


class EnemyTrigger(ModifierTrigger):
    """Trigger on type IF event pet is an enemy pet"""

    def is_triggered(self, event: Event, owner: Pet = None):
        if not super().is_triggered(event, owner):
            return False

        if len(event.teams) < 2:
            return False
        else:  # 2 teams
            if owner in event.teams[0]:
                _, enemy_team = event.teams
            elif owner in event.teams[1]:
                enemy_team, _ = event.teams
            else:
                raise ValueError("Trigger owner must be in at least 1 event team")

        return None not in (enemy_team, owner, event.pet) and event.pet in enemy_team


class AheadTrigger(ModifierTrigger):
    """Trigger on type IF event pet is ahead"""

    def is_triggered(self, event: Event, owner: Pet = None):
        if not super().is_triggered(event, owner):
            return False

        if len(event.teams) == 0:
            return False
        elif len(event.teams) == 1:
            friendly_team = event.teams[0]
            enemy_team = []
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
