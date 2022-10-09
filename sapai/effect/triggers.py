from collections import namedtuple
from typing import List, NamedTuple, Union
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

    def to_dict(self):
        """Generates a dictionary representation of the trigger

        Returns:
            dict: Trigger represented with the following keys
                (all optional but must have an op or event)
                "event": The EventType of the trigger
                "op": Operation to perform e.g. ALL, ANY, True, False
                "triggers": List of nested triggers to perform "op" on.
                "modifiers": List of dictionaries representing modifiers
                    with a "type" key and possible other keys.
        """
        return {"op": False}

    @classmethod
    def from_dict(cls, trigger_dict: dict):
        trigger = None

        # Create base trigger based on "op" or "event" key
        if trigger_dict.get("event") in [et.name for et in EventType]:
            trigger = TypeTrigger(EventType[trigger_dict["event"]])
        elif trigger_dict.get("op") in ("ANY", "ALL") and "triggers" in trigger_dict:
            nested_triggers = [cls.from_dict(t) for t in trigger_dict["triggers"]]
            if trigger_dict["op"] == "ANY":
                trigger = AnyTrigger(nested_triggers)
            elif trigger_dict["op"] == "ALL":
                trigger = AllTrigger(nested_triggers)
        elif trigger_dict.get("op") in (True, False):
            if trigger_dict["op"] is False:
                trigger = Trigger()
            elif trigger_dict["op"] is True:
                trigger = AlwaysTrigger()
        else:
            raise ValueError("Unsupported or missing op or event value")

        # Add modifiers to trigger
        if trigger_dict.get("modifiers"):
            # Sort so generated trigger does not rely on order
            modifiers = sorted(
                trigger_dict["modifiers"], key=lambda d: tuple(d.items())
            )
            for modifier_dict in modifiers:
                trigger = cls.add_modifier_from_dict(trigger, modifier_dict)

        return trigger

    @classmethod
    def add_modifier_from_dict(cls, trigger: "Trigger", modifier_dict: dict):
        if not modifier_dict.get("type"):
            raise ValueError(f"Missing modifier type")

        if modifier_dict["type"] == "self":
            return SelfTrigger(trigger)
        elif modifier_dict["type"] == "friendly":
            return FriendlyTrigger(trigger)
        elif modifier_dict["type"] == "enemy":
            return EnemyTrigger(trigger)
        elif modifier_dict["type"] == "ahead":
            return AheadTrigger(trigger)
        elif (
            modifier_dict["type"] in ("limit", "count")
            and modifier_dict.get("n")
            and modifier_dict.get("reset_event")
        ):
            if modifier_dict["type"] == "limit":
                modifier_trigger = LimitTrigger
            elif modifier_dict["type"] == "count":
                modifier_trigger = CountTrigger
            return modifier_trigger(
                trigger,
                n=modifier_dict["n"],
                reset_event=EventType[modifier_dict["reset_event"]],
            )
        else:
            raise ValueError(
                f"Unsupported or badly formatted modifier: {modifier_dict}"
            )

    def __lt__(self, other):
        return repr(self.to_dict()) < repr(other.to_dict())

    def __repr__(self):
        return f"Trigger<{self.to_dict()}>"


class AlwaysTrigger(Trigger):
    """Always triggers, regardless of event or owner"""

    def is_triggered(self, event: Event, owner: Pet = None):
        return True

    def to_dict(self):
        return {"op": True}


class MultiTrigger(Trigger):
    """Base class for a trigger that takes a list of triggers"""

    def __init__(self, triggers: List[Trigger]):
        for t in triggers:
            if not isinstance(t, Trigger):
                raise TypeError("triggers must all be Trigger instances")
        # Sort so order is irrelevant
        self._triggers = sorted(triggers)

    def to_dict(self):
        return {
            "triggers": [t.to_dict() for t in self._triggers],
        }


class AnyTrigger(MultiTrigger):
    """Triggers if any of the given triggers are triggered"""

    def is_triggered(self, event: Event, owner: Pet = None):
        for trigger in self._triggers:
            if trigger.is_triggered(event, owner):
                return True
        return False

    def to_dict(self):
        result = super().to_dict()
        result["op"] = "ANY"
        return result


class AllTrigger(MultiTrigger):
    """Triggers if all of the given triggers are triggered"""

    def is_triggered(self, event: Event, owner: Pet = None):
        for trigger in self._triggers:
            if not trigger.is_triggered(event, owner):
                return False
        return len(self._triggers) > 0

    def to_dict(self):
        result = super().to_dict()
        result["op"] = "ALL"
        return result


class TypeTrigger(Trigger):
    """Trigger based on a given trigger event type"""

    def __init__(self, event_type: EventType):
        self._event_type = event_type

    def is_triggered(self, event: Event, owner: Pet = None):
        return event and event.type is self._event_type

    def to_dict(self):
        return {"event": self._event_type.name}


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

    def to_dict(self):
        result = self._trigger.to_dict()
        if "modifiers" not in result:
            result["modifiers"] = []
        return result


class LimitTrigger(ModifierTrigger):
    """Only triggers a maximum number of times between events"""

    def __init__(
        self,
        trigger: Trigger,
        n=3,
        reset_event: EventType = EventType.START_OF_TURN,
    ):
        if not isinstance(reset_event, EventType):
            raise TypeError(f"reset_event must be of type EventType")
        super().__init__(trigger)
        self._reset_event = reset_event
        self.n = n
        self.remaining_limit = self.n

    def reset_limit(self):
        self.remaining_limit = self.n

    def is_triggered(self, event: Event, owner: Pet = None):
        if event.type is self._reset_event:
            self.reset_limit()

        if self.remaining_limit <= 0:
            return False

        is_triggered = super().is_triggered(event, owner)
        if is_triggered:
            self.remaining_limit -= 1
        return is_triggered

    def to_dict(self):
        result = super().to_dict()
        modifier = {
            "type": "limit",
            "n": self.n,
            "reset_event": self._reset_event.name,
        }
        result["modifiers"].append(modifier)
        return result


class CountTrigger(ModifierTrigger):
    """Only triggers once every N activations of the given trigger"""

    def __init__(
        self,
        trigger: Trigger,
        n: int = 2,
        reset_event: EventType = EventType.START_OF_TURN,
    ):
        if not isinstance(reset_event, EventType):
            raise TypeError(f"reset_event must be of type EventType")
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

    def to_dict(self, starting_dict=None):
        result = super().to_dict()
        modifier = {
            "type": "count",
            "n": self.n,
            "reset_event": self._reset_event.name,
        }
        result["modifiers"].append(modifier)
        return result


class SelfTrigger(ModifierTrigger):
    """Trigger on type IF event pet is owner pet"""

    def is_triggered(self, event: Event, owner: Pet = None):
        if not super().is_triggered(event, owner):
            return False
        return None not in (owner, event.pet) and owner is event.pet

    def to_dict(self):
        result = super().to_dict()
        modifier = {"type": "self"}
        result["modifiers"].append(modifier)
        return result


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

    def to_dict(self):
        result = super().to_dict()
        modifier = {"type": "friendly"}
        result["modifiers"].append(modifier)
        return result


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

    def to_dict(self):
        result = super().to_dict()
        modifier = {"type": "enemy"}
        result["modifiers"].append(modifier)
        return result


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

    def to_dict(self):
        result = super().to_dict()
        modifier = {"type": "ahead"}
        result["modifiers"].append(modifier)
        return result
