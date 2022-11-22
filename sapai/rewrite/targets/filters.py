"""Module containing target filter definitions"""
from abc import ABC, abstractmethod
from enum import Enum, auto
from sapai.pets import Pet
from sapai.rewrite.events import Event


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

    @classmethod
    def _get_mapping(cls):
        return {
            cls.NONE: NoneFilter,
            cls.SELF: SelfFilter,
            cls.NOT_SELF: NotSelfFilter,
            cls.FRIENDLY: FriendlyFilter,
            cls.ENEMY: EnemyFilter,
            cls.AHEAD: AheadFilter,
            cls.BEHIND: BehindFilter,
            cls.ADJACENT: AdjacentFilter,
        }

    def to_class(self) -> "Filter":
        """Returns the TargetFilter class corresponding to the enum value"""
        mapping = self._get_mapping()
        if self in mapping:
            class_ = mapping[self]
        else:
            raise NotImplementedError(f"{self} does not map to a class")
        return class_

    @classmethod
    def from_class(cls, class_) -> "FilterType":
        """Returns the Type corresponding to the given class"""
        mapping = cls._get_mapping()
        for type_, map_class in mapping.items():
            if class_ is map_class:
                return type_
        raise NotImplementedError(f"{class_} does not map to a type")


class Filter(ABC):
    """Filters a list of possible targets based on criteria"""

    def __init__(self, owner: Pet):
        self._owner = owner

    @abstractmethod
    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        raise NotImplementedError()

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
        return {"filter": FilterType.from_class(type(self)).name}

    @classmethod
    def from_dict(cls, filter_dict: dict, owner: Pet) -> "Filter":
        """Creates a filter from its dictionary representation

        Args:
            filter_dict (dict): dictionary representation to create from.

        Raises:
            ValueError: When given an invalid dictionary

        Returns:
            TargetFilter: TargetFilter instance specified by filter_dict
        """
        types = [type_.name for type_ in FilterType]
        if filter_dict.get("filter") in types:
            class_ = FilterType[filter_dict["filter"]].to_class()
            return class_(owner)

        elif filter_dict.get("op") in ("ANY", "ALL") and filter_dict.get("filters"):
            nested_filters = [
                cls.from_dict(filt_d, owner) for filt_d in filter_dict["filters"]
            ]
            if filter_dict["op"] == "ANY":
                return AnyFilter(owner, nested_filters)
            return AllFilter(owner, nested_filters)

        else:
            raise ValueError("Invalid TargetFilter dict representation")


class MultiFilter(Filter):
    """Base class for a filter that applies a list of filters"""

    def __init__(self, owner: Pet, filters: list[Filter]):
        super().__init__(owner)
        for filt in filters:
            if not isinstance(filt, Filter):
                raise TypeError("filters must all be TargetFilter instances")
        self._filters = filters

    @abstractmethod
    def to_dict(self) -> dict:
        return {
            "filters": [f.to_dict() for f in self._filters],
        }


class AllFilter(MultiFilter):
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


class AnyFilter(MultiFilter):
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


class NoneFilter(Filter):
    """No Filtering"""

    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """Does no filtering"""
        return [p for p in pets]


class SelfFilter(Filter):
    """Filters to only the owner pet"""

    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes only the owner pet"""
        return [p for p in pets if p is self._owner]


class NotSelfFilter(Filter):
    """Filters to pets that are not the owner"""

    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes pets that are not the owner in order given in `pets`"""
        return [p for p in pets if p is not self._owner]


class FriendlyFilter(Filter):
    """Filters to pets in friendly to owner"""

    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes pets friendly to owner (inclusive) in order given in `pets`"""
        if not event.pet_in_event_teams(self._owner):
            raise ValueError("Owner must be in at least 1 team to use FriendlyFilter")
        friendly_team, _ = event.get_ordered_teams(self._owner)
        return [p for p in pets if p in friendly_team]


class EnemyFilter(Filter):
    """Filters to pets in opposition to owner"""

    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes pets in opposition to owner in order given in `pets`"""
        if not event.pet_in_event_teams(self._owner):
            raise ValueError("Owner must be in at least 1 team to use EnemyFilter")
        _, enemy_team = event.get_ordered_teams(self._owner)
        return [p for p in pets if p in enemy_team]


class AheadFilter(Filter):
    """Filters to pets ahead of owner"""

    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes pets infront of owner in order from closest to furthest"""
        if not event.pet_in_event_teams(self._owner):
            raise ValueError("Owner must be in at least 1 team to use AheadFilter")
        friendly_team, enemy_team = event.get_ordered_teams(self._owner)
        battlefield = [*friendly_team[::-1], *enemy_team]
        idx = battlefield.index(self._owner)
        return [p for p in battlefield[(idx + 1) :] if p in pets]


class BehindFilter(Filter):
    """Filters to pets behind owner"""

    def filter(self, pets: list[Pet], event: Event) -> list[Pet]:
        """includes pets behind owner in order from closest to furthest"""
        if not event.pet_in_event_teams(self._owner):
            raise ValueError("Owner must be in at least 1 team to use BehindFilter")
        friendly_team, enemy_team = event.get_ordered_teams(self._owner)
        battlefield = [*friendly_team[::-1], *enemy_team]
        idx = battlefield.index(self._owner)
        return [p for p in battlefield[:idx][::-1] if p in pets]


class AdjacentFilter(Filter):
    """Filters to pets adjacent to owner"""

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
