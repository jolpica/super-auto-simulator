from unittest import TestCase
from unittest.mock import Mock
from sapai.effect.events import Event, EventType
from sapai.effect.targets import (
    LeftMostTargetSelector,
    RightMostTargetSelector,
    RandomTargetSelector,
    TargetSelector,
)
from sapai.pets import Pet


class TargetSelectorTestCase(TestCase):
    def setUp(self):
        self.friendly_team = [Mock(Pet) for i in range(5)]
        self.enemy_team = [Mock(Pet) for i in range(5)]

    def test_validate_args(self):
        selector = Mock(TargetSelector)
        with self.assertRaises(ValueError):
            TargetSelector._validate_args(selector, pets=[], n=-1, rand=0)
        with self.assertRaises(ValueError):
            TargetSelector._validate_args(selector, pets=[], n=1, rand=-0.01)
        with self.assertRaises(ValueError):
            TargetSelector._validate_args(selector, pets=[], n=1, rand=1)

    def test_first_target_selector(self):
        """Tests first target selector returns first n pets"""
        selector = LeftMostTargetSelector()
        self.assertEqual([], selector.select(self.friendly_team, n=0))
        self.assertEqual(
            [self.friendly_team[0]], selector.select(self.friendly_team, n=1)
        )
        self.assertEqual(
            [self.friendly_team[0], self.friendly_team[1]],
            selector.select(self.friendly_team, n=2),
        )
        self.assertEqual(self.friendly_team, selector.select(self.friendly_team, n=5))
        self.assertEqual(self.friendly_team, selector.select(self.friendly_team, n=10))

    def test_last_target_selector(self):
        """Tests last target selector returns last n pets"""
        selector = RightMostTargetSelector()
        self.assertEqual([], selector.select(self.friendly_team, n=0))
        self.assertEqual(
            [self.friendly_team[-1]], selector.select(self.friendly_team, n=1)
        )
        self.assertEqual(
            [self.friendly_team[-2], self.friendly_team[-1]],
            selector.select(self.friendly_team, n=2),
        )
        self.assertEqual(self.friendly_team, selector.select(self.friendly_team, n=5))
        self.assertEqual(self.friendly_team, selector.select(self.friendly_team, n=10))

    def test_random_target_selector(self):
        selector = RandomTargetSelector()
        self.assertEqual([], selector.select(self.friendly_team, n=0, rand=0))
        # Since we use the seed for the index of the nth combination,
        # the random pet chosen is consistent with its index in the list
        n = len(self.friendly_team)
        for i, p in enumerate(self.friendly_team):
            self.assertEqual([p], selector.select(self.friendly_team, n=1, rand=i / n))

        self.assertEqual(
            self.friendly_team[:2],
            selector.select(self.friendly_team, n=2, rand=0),
        )
