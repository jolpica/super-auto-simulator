import typing
from unittest import TestCase
from unittest.mock import Mock, patch

import pytest

from superautosim.events import Event, EventType
from superautosim.pets import Pet
from superautosim.targets import (
    BattlefieldTargetGenerator,
    FirstSelector,
    FriendlyFilter,
    RandomSelector,
    TargetGenerator,
    TargetGeneratorType,
    TargetGeneratorTypeValue,
)


def test_target_generator_dict():
    literals = set(typing.get_args(TargetGeneratorTypeValue))
    enums = set(type.name for type in TargetGeneratorType)
    assert literals == enums


def test_type_to_from_class():
    """Tests all types map to a class and back (all new types are added)"""
    for type_ in TargetGeneratorType:
        class_ = type_.to_class()
        assert issubclass(class_, TargetGenerator), "not a subclass"
        assert TargetGeneratorType.from_class(class_) == type_


def test_type_from_class_not_implemented():
    """abstacts not implemented"""
    with pytest.raises(NotImplementedError):
        TargetGeneratorType.from_class(TargetGenerator)


def test_get_not_implemented():
    """abstacts not implemented"""
    with patch.object(TargetGenerator, "__abstractmethods__", set()):
        targen = TargetGenerator(None, None)
        with pytest.raises(NotImplementedError):
            targen.get(None, None, None)


def test_from_dict(friendly_team):
    test = {
        "target_generator": "BATTLEFIELD",
        "filter": {"op": "SINGLE", "filter": "FRIENDLY"},
        "selector": {"selector": "RANDOM"},
    }
    target = TargetGenerator.from_dict(test, friendly_team[0])

    assert isinstance(target, BattlefieldTargetGenerator)
    assert isinstance(target._filter, FriendlyFilter)
    assert isinstance(target._selector, RandomSelector)


def test_from_dict_invalid(friendly_team):
    test = {
        "target_generator": "invalid",
        "filter": {"op": "SINGLE", "filter": "FRIENDLY"},
        "selector": {"selector": "RANDOM"},
    }
    with pytest.raises(ValueError):
        TargetGenerator.from_dict(test, friendly_team[0])


class BattlefieldTargetGeneratorTestCase(TestCase):
    def setUp(self) -> None:
        self.friendly_team = [Mock(Pet) for i in range(5)]
        self.enemy_team = [Mock(Pet) for i in range(5)]
        self.battlefield = self.friendly_team[::-1] + self.enemy_team
        self.event = Event(
            EventType.NONE,
            self.friendly_team[0],
            teams=[self.friendly_team, self.enemy_team],
        )
        self.event_r = Event(
            EventType.NONE,
            self.friendly_team[0],
            teams=[self.friendly_team, self.enemy_team],
        )

    def test_selector(self):
        target = BattlefieldTargetGenerator(
            owner=self.friendly_team[0], selector=FirstSelector()
        )
        self.assertEqual(self.battlefield, target.get(self.event, 10, 0))
        self.assertEqual(self.battlefield, target.get(self.event, 99, 0))

        self.assertEqual(self.battlefield, target.get(self.event_r, 10, 0))
        self.assertEqual(self.battlefield[:5], target.get(self.event_r, 5, 0))
        self.assertEqual([], target.get(self.event_r, 0, 0))

    def test_filter(self):
        target = BattlefieldTargetGenerator(
            owner=self.friendly_team[0],
            selector=FirstSelector(),
            filter_=FriendlyFilter(self.friendly_team[0]),
        )

        self.assertEqual(self.friendly_team[::-1], target.get(self.event, 10, 0))

    def test_random_filter_select(self):
        target = BattlefieldTargetGenerator(
            owner=self.friendly_team[0],
            selector=RandomSelector(),
            filter_=FriendlyFilter(self.friendly_team[0]),
        )

        self.assertEqual(self.friendly_team[::-1], target.get(self.event, 10, 0))
        self.assertEqual(self.friendly_team[::-1], target.get(self.event, 10, 0.99))

        self.assertEqual(self.friendly_team[::-1][:2], target.get(self.event, 2, 0))
        self.assertEqual(self.friendly_team[::-1][-2:], target.get(self.event, 2, 0.99))

    def test_to_dict(self):
        """Test generation of dictionary representation"""
        target = BattlefieldTargetGenerator(
            self.friendly_team[0],
            selector=RandomSelector(),
            filter_=FriendlyFilter(self.friendly_team[0]),
        )
        test = {
            "target_generator": "BATTLEFIELD",
            "filter": {"op": "SINGLE", "filter": "FRIENDLY"},
            "selector": {"selector": "RANDOM"},
        }
        self.assertEqual(test, target.to_dict())
        target = BattlefieldTargetGenerator(
            self.friendly_team[0],
            selector=RandomSelector(),
        )
        test = {
            "target_generator": "BATTLEFIELD",
            "filter": {"op": "SINGLE", "filter": "NONE"},
            "selector": {"selector": "RANDOM"},
        }
        self.assertEqual(test, target.to_dict())
