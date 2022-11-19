from abc import ABC, abstractmethod
from enum import Enum, auto
from sapai.pets import Pet
from sapai.effect.events import Event


class FilterType(Enum):
    """Enumeration of types of filter"""

    NONE = auto()
    SELF = auto()
    NOT_SELF = auto()
    FRIENDLY = auto()
    ENEMY = auto()
    AHEAD = auto()
    BEHIND = auto()
    ADJACENT = auto()

    def to_filter_class(self):
        """Returns the TargetFilter class corresponding to the enum value"""
        if self is self.SELF:
            filt = SelfFilter
        elif self is self.NOT_SELF:
            filt = NotSelfFilter
        elif self is self.FRIENDLY:
            filt = FriendlyFilter
        elif self is self.ENEMY:
            filt = EnemyFilter
        elif self is self.AHEAD:
            filt = AheadFilter
        elif self is self.BEHIND:
            filt = BehindFilter
        elif self is self.ADJACENT:
            filt = AdjacentFilter
        else:
            raise NotImplementedError()
        return filt


class TargetFilter(ABC):
    """Filters a list of possible targets based on criteria"""

    def __init__(self, owner: Pet):
        self._owner = owner

    @abstractmethod
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        raise NotImplementedError()

    @abstractmethod
    def to_dict(self) -> dict:
        """Generates a dictionary representation of the filter

        Returns:
            dict: Filter represented as a filter or op dictionary:
                {
                    "filter": The type/name of the filter
                }
                or
                {
                    "op": Operation to perform e.g. ALL, ANY
                    "filters": List of nested filter dicts to perform "op" on.
                }
        """
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, filter_dict: dict, owner: Pet) -> "TargetFilter":
        """Creates a filter from its dictionary representation

        Args:
            filter_dict (dict): dictionary representation to create trigger from.

        Raises:
            ValueError: When given an invalid dictionary

        Returns:
            TargetFilter: TargetFilter instance specified by filter_dict
        """
        filter_types = [filt_t.name for filt_t in FilterType]
        if filter_dict.get("filter") in filter_types:
            class_ = FilterType[filter_dict["filter"]].to_filter_class()
            return class_(owner)

        elif filter_dict.get("op") in ("ANY", "ALL") and filter_dict.get("filters"):
            nested_filters = [
                cls.from_dict(filt_d, owner) for filt_d in filter_dict["filters"]
            ]
            if filter_dict["op"] == "ANY":
                return AnyTargetFilter(owner, nested_filters)
            return AllTargetFilter(owner, nested_filters)

        else:
            raise ValueError("Invalid filter_dict representation")


class MultiTargetFilter(TargetFilter):
    """Base class for a filter that applies a list of filters"""

    def __init__(self, owner: Pet, filters: list[TargetFilter]):
        super().__init__(owner)
        for f in filters:
            if not isinstance(f, TargetFilter):
                raise TypeError("filters must all be TargetFilter instances")
        self._filters = filters

    @abstractmethod
    def to_dict(self) -> dict:
        return {
            "filters": [f.to_dict() for f in self._filters],
        }


class AllTargetFilter(MultiTargetFilter):
    """Returns results that are unfiltered by all of the given filters (AND)
    returns all pets if given an empty list of filters"""

    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        for t_filter in self._filters:
            pets = t_filter.filter(pets, event)
        return [p for p in pets]

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["op"] = "ALL"
        return result


class AnyTargetFilter(MultiTargetFilter):
    """Returns results that are unfiltered by any of the given filters (OR)
    returns nothing if given an empty list of filters"""

    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        returned_pets = set()
        for t_filter in self._filters:
            returned_pets.update(t_filter.filter(pets, event))
        # Ensure that pet order is preserved
        return [p for p in pets if p in returned_pets]

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["op"] = "ANY"
        return result


class NoneFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """Does no filtering"""
        return [p for p in pets]

    def to_dict(self) -> dict:
        return {"filter": FilterType.NONE.name}


class SelfFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes only the owner pet"""
        return [p for p in pets if p is self._owner]

    def to_dict(self) -> dict:
        return {"filter": FilterType.SELF.name}


class NotSelfFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes pets that are not the owner in order given in `pets`"""
        return [p for p in pets if p is not self._owner]

    def to_dict(self) -> dict:
        return {"filter": FilterType.NOT_SELF.name}


class FriendlyFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes pets friendly to owner (inclusive) in order given in `pets`"""
        if not event.pet_in_event_teams(self._owner):
            raise ValueError("Owner must be in at least 1 team to use FriendlyFilter")
        friendly_team, _ = event.get_ordered_teams(self._owner)
        return [p for p in pets if p in friendly_team]

    def to_dict(self) -> dict:
        return {"filter": FilterType.FRIENDLY.name}


class EnemyFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes pets in opposition to owner in order given in `pets`"""
        if not event.pet_in_event_teams(self._owner):
            raise ValueError("Owner must be in at least 1 team to use EnemyFilter")
        _, enemy_team = event.get_ordered_teams(self._owner)
        return [p for p in pets if p in enemy_team]

    def to_dict(self) -> dict:
        return {"filter": FilterType.ENEMY.name}


class AheadFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes pets infront of owner in order from closest to furthest"""
        if not event.pet_in_event_teams(self._owner):
            raise ValueError("Owner must be in at least 1 team to use AheadFilter")
        friendly_team, enemy_team = event.get_ordered_teams(self._owner)
        battlefield = [*friendly_team[::-1], *enemy_team]
        idx = battlefield.index(self._owner)
        return [p for p in battlefield[(idx + 1) :] if p in pets]

    def to_dict(self) -> dict:
        return {"filter": FilterType.AHEAD.name}


class BehindFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes pets behind owner in order from closest to furthest"""
        if not event.pet_in_event_teams(self._owner):
            raise ValueError("Owner must be in at least 1 team to use BehindFilter")
        friendly_team, enemy_team = event.get_ordered_teams(self._owner)
        battlefield = [*friendly_team[::-1], *enemy_team]
        idx = battlefield.index(self._owner)
        return [p for p in battlefield[:idx][::-1] if p in pets]

    def to_dict(self) -> dict:
        return {"filter": FilterType.BEHIND.name}


class AdjacentFilter(TargetFilter):
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes pets next to owner in order given by `pets`"""
        if not event.pet_in_event_teams(self._owner):
            raise ValueError("Owner must be in at least 1 team to use AdjacentFilter")
        friendly_team, enemy_team = event.get_ordered_teams(self._owner)
        battlefield = [*friendly_team[::-1], *enemy_team]
        idx = battlefield.index(self._owner)
        result = []
        if (idx - 1) >= 0:
            result.append((battlefield[idx - 1]))
        if (idx + 1) <= len(battlefield) - 1:
            result.append((battlefield[idx + 1]))
        return [p for p in pets if p in result]

    def to_dict(self) -> dict:
        return {"filter": FilterType.ADJACENT.name}
