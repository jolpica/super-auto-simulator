from unittest import TestCase
from unittest.mock import Mock
from sapai.effect.events import Event, EventType
from sapai.effect.targets import (
    FirstTargetSelector,
    LastTargetSelector,
    nth_permutation,
)
from sapai.pets import Pet


class TargetSelectorTestCase(TestCase):
    def setUp(self):
        self.friendly_team = [Mock(Pet) for i in range(5)]
        self.enemy_team = [Mock(Pet) for i in range(5)]

    def test_first_target_selector(self):
        """Tests first target selector returns first n pets"""
        selector = FirstTargetSelector()
        self.assertEqual([], selector.select(self.friendly_team, n=-1))
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
        selector = LastTargetSelector()
        self.assertEqual([], selector.select(self.friendly_team, n=-1))
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

    def test_nth_permutation(self):
        print()
        for i in range(6):
            print(nth_permutation(list("abcd"), i, 2))
