from unittest import TestCase
from unittest.mock import Mock
from sapai.effect.events import Event, EventType
from sapai.effect.targets import (
    LeftMostSelector,
    RightMostSelector,
    RandomSelector,
    Selector,
    HealthSelector,
    ValueSelector,
)
from sapai.pets import Pet


class TargetSelectorTestCase(TestCase):
    def setUp(self):
        self.friendly_team = [Mock(Pet) for i in range(5)]
        for i, p in enumerate(self.friendly_team):
            p.health = i + 1
        self.enemy_team = [Mock(Pet) for i in range(5)]

    def test_validate_args(self):
        selector = Mock(Selector)
        with self.assertRaises(ValueError):
            Selector._validate_args(selector, pets=[], n=-1, rand=0)
        with self.assertRaises(ValueError):
            Selector._validate_args(selector, pets=[], n=1, rand=-0.01)
        with self.assertRaises(ValueError):
            Selector._validate_args(selector, pets=[], n=1, rand=1)

    def test_first_target_selector(self):
        """Tests first target selector returns first n pets"""
        selector = LeftMostSelector()
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
        selector = RightMostSelector()
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
        selector = RandomSelector()
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

        self.assertFalse(
            self.friendly_team is selector.select(self.friendly_team, n=99, rand=0)
        )
        self.assertFalse(
            self.friendly_team is selector.select(self.friendly_team, n=5, rand=0)
        )

    def test_random_selector_tiebreak_select(self):
        class TestValueSelector(ValueSelector):
            def select(self):
                pass

        sel_high = TestValueSelector(highest=True)
        sel_low = TestValueSelector(highest=False)

        pet_vals = [(p, 5 - i) for i, p in enumerate(self.friendly_team)]
        # n less <= 0
        self.assertEqual([], sel_low._tiebreak_select([], n=0, rand=0))
        self.assertEqual([], sel_high._tiebreak_select([], n=0, rand=0))
        self.assertEqual([], sel_high._tiebreak_select(pet_vals, n=0, rand=0))
        self.assertEqual([], sel_high._tiebreak_select([], n=-1, rand=0))

        # items <= n
        self.assertEqual(
            self.friendly_team,
            sel_high._tiebreak_select(pet_vals, n=5, rand=0),
        )
        self.assertEqual(
            self.friendly_team,
            sel_high._tiebreak_select(pet_vals, n=6, rand=0),
        )
        self.assertEqual(
            self.friendly_team[::-1],
            sel_low._tiebreak_select(pet_vals, n=5, rand=0),
        )
        self.assertEqual(
            self.friendly_team[::-1],
            sel_low._tiebreak_select(pet_vals, n=6, rand=0),
        )

        # no tiebreak
        self.assertEqual(
            self.friendly_team[:3],
            sel_high._tiebreak_select(pet_vals, n=3, rand=0),
        )
        self.assertEqual(
            self.friendly_team[::-1][:3],
            sel_low._tiebreak_select(pet_vals, n=3, rand=0),
        )

        # tiebreak
        values = [1, 3, 3, 3, 5]
        pet_vals = list(zip(self.friendly_team, values))
        self.assertEqual(
            [self.friendly_team[4], self.friendly_team[1]],
            sel_high._tiebreak_select(pet_vals, n=2, rand=0),
        )
        self.assertEqual(
            [self.friendly_team[4], self.friendly_team[3]],
            sel_high._tiebreak_select(pet_vals, n=2, rand=2 / 3),
        )
        self.assertEqual(
            [self.friendly_team[0], self.friendly_team[1]],
            sel_low._tiebreak_select(pet_vals, n=2, rand=0),
        )
        self.assertEqual(
            [self.friendly_team[0], self.friendly_team[3]],
            sel_low._tiebreak_select(pet_vals, n=2, rand=2 / 3),
        )

    def test_highest_health_target_selector(self):
        selector = HealthSelector()

        # No duplicate health
        self.assertEqual([], selector.select(self.friendly_team, n=0, rand=0))
        expected = self.friendly_team[::-1][:3]
        self.assertEqual(expected, selector.select(self.friendly_team, n=3, rand=0))
        self.assertEqual(
            expected, selector.select(self.friendly_team[::-1], n=3, rand=0)
        )
        # For unique health, input order has no effect on output order
        self.assertEqual(
            selector.select(self.friendly_team, n=5, rand=0),
            selector.select(self.friendly_team[::-1], n=5, rand=0),
        )

        # Duplicate health (pets at index 1,2,3 have 2 health)
        self.friendly_team[2].health = 2
        self.friendly_team[3].health = 2
        duplicates = self.friendly_team[1:4]
        for i in range(3):
            self.assertEqual(
                [self.friendly_team[-1], duplicates[i]],
                selector.select(self.friendly_team, n=2, rand=i / 3),
            )
        self.assertEqual(
            [self.friendly_team[-1], *duplicates[:2]],
            selector.select(self.friendly_team, n=3, rand=0),
        )
        self.assertEqual(
            [self.friendly_team[-1], *duplicates],
            selector.select(self.friendly_team, n=4, rand=0),
        )
