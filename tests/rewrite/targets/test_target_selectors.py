from unittest import TestCase
from unittest.mock import Mock

from sapai.rewrite.events import Event, EventType
from sapai.rewrite.targets import (
    AttackSelector,
    FirstSelector,
    HealthSelector,
    LastSelector,
    RandomSelector,
    Selector,
    StrengthSelector,
    ValueSelector,
    SelectorType,
)
from sapai.pets import Pet


class SelectorTypeTestCase(TestCase):
    def test_to_from_class(self):
        """Tests all types map to a class and back"""
        for type_ in SelectorType:
            class_ = type_.to_class()
            self.assertTrue(issubclass(class_, Selector))
            self.assertEqual(SelectorType.from_class(class_), type_)


class TargetSelectorTestCase(TestCase):
    def setUp(self):
        self.friendly_team = [Mock(Pet) for i in range(5)]
        for i, p in enumerate(self.friendly_team):
            p.health = i + 1
        self.enemy_team = [Mock(Pet) for i in range(5)]

    def test_validate_args(self):
        selector = Mock(Selector)
        with self.assertRaises(ValueError):
            Selector._validate_args(selector, pets=[], num=-1, rand=0)
        with self.assertRaises(ValueError):
            Selector._validate_args(selector, pets=[], num=1, rand=-0.01)
        with self.assertRaises(ValueError):
            Selector._validate_args(selector, pets=[], num=1, rand=1)

    def test_first_target_selector(self):
        """Tests first target selector returns first n pets"""
        selector = FirstSelector()
        self.assertEqual([], selector.select(self.friendly_team, num=0))
        self.assertEqual(
            [self.friendly_team[0]], selector.select(self.friendly_team, num=1)
        )
        self.assertEqual(
            [self.friendly_team[0], self.friendly_team[1]],
            selector.select(self.friendly_team, num=2),
        )
        self.assertEqual(self.friendly_team, selector.select(self.friendly_team, num=5))
        self.assertEqual(
            self.friendly_team, selector.select(self.friendly_team, num=10)
        )

    def test_last_target_selector(self):
        """Tests last target selector returns last n pets"""
        selector = LastSelector()
        self.assertEqual([], selector.select(self.friendly_team, num=0))
        self.assertEqual(
            [self.friendly_team[-1]], selector.select(self.friendly_team, num=1)
        )
        self.assertEqual(
            [self.friendly_team[-1], self.friendly_team[-2]],
            selector.select(self.friendly_team, num=2),
        )
        self.assertEqual(
            self.friendly_team[::-1], selector.select(self.friendly_team, num=5)
        )
        self.assertEqual(
            self.friendly_team[::-1], selector.select(self.friendly_team, num=10)
        )

    def test_random_target_selector(self):
        selector = RandomSelector()
        self.assertEqual([], selector.select(self.friendly_team, num=0, rand=0))
        # Since we use the seed for the index of the nth combination,
        # the random pet chosen is consistent with its index in the list
        n = len(self.friendly_team)
        for i, p in enumerate(self.friendly_team):
            self.assertEqual(
                [p], selector.select(self.friendly_team, num=1, rand=i / n)
            )

        self.assertEqual(
            self.friendly_team[:2],
            selector.select(self.friendly_team, num=2, rand=0),
        )

        self.assertFalse(
            self.friendly_team is selector.select(self.friendly_team, num=99, rand=0)
        )
        self.assertFalse(
            self.friendly_team is selector.select(self.friendly_team, num=5, rand=0)
        )

    def test_random_selector_tiebreak_select(self):
        class TestValueSelector(ValueSelector):
            def select(self):
                pass

            def get_type(self):
                pass

        sel_high = TestValueSelector(highest=True)
        sel_low = TestValueSelector(highest=False)

        pet_vals = [(p, 5 - i) for i, p in enumerate(self.friendly_team)]
        # n less <= 0
        self.assertEqual([], sel_low._tiebreak_select([], num=0, rand=0))
        self.assertEqual([], sel_high._tiebreak_select([], num=0, rand=0))
        self.assertEqual([], sel_high._tiebreak_select(pet_vals, num=0, rand=0))
        self.assertEqual([], sel_high._tiebreak_select([], num=-1, rand=0))

        # items <= n
        self.assertEqual(
            self.friendly_team,
            sel_high._tiebreak_select(pet_vals, num=5, rand=0),
        )
        self.assertEqual(
            self.friendly_team,
            sel_high._tiebreak_select(pet_vals, num=6, rand=0),
        )
        self.assertEqual(
            self.friendly_team[::-1],
            sel_low._tiebreak_select(pet_vals, num=5, rand=0),
        )
        self.assertEqual(
            self.friendly_team[::-1],
            sel_low._tiebreak_select(pet_vals, num=6, rand=0),
        )

        # no tiebreak
        self.assertEqual(
            self.friendly_team[:3],
            sel_high._tiebreak_select(pet_vals, num=3, rand=0),
        )
        self.assertEqual(
            self.friendly_team[::-1][:3],
            sel_low._tiebreak_select(pet_vals, num=3, rand=0),
        )

        # tiebreak
        values = [1, 3, 3, 3, 5]
        pet_vals = list(zip(self.friendly_team, values))
        self.assertEqual(
            [self.friendly_team[4], self.friendly_team[1]],
            sel_high._tiebreak_select(pet_vals, num=2, rand=0),
        )
        self.assertEqual(
            [self.friendly_team[4], self.friendly_team[3]],
            sel_high._tiebreak_select(pet_vals, num=2, rand=2 / 3),
        )
        self.assertEqual(
            [self.friendly_team[0], self.friendly_team[1]],
            sel_low._tiebreak_select(pet_vals, num=2, rand=0),
        )
        self.assertEqual(
            [self.friendly_team[0], self.friendly_team[3]],
            sel_low._tiebreak_select(pet_vals, num=2, rand=2 / 3),
        )

    def test_highest_health_target_selector(self):
        selector = HealthSelector()

        # No duplicate health
        self.assertEqual([], selector.select(self.friendly_team, num=0, rand=0))
        expected = self.friendly_team[::-1][:3]
        self.assertEqual(expected, selector.select(self.friendly_team, num=3, rand=0))
        self.assertEqual(
            expected, selector.select(self.friendly_team[::-1], num=3, rand=0)
        )
        # For unique health, input order has no effect on output order
        self.assertEqual(
            selector.select(self.friendly_team, num=5, rand=0),
            selector.select(self.friendly_team[::-1], num=5, rand=0),
        )

        # Duplicate health (pets at index 1,2,3 have 2 health)
        self.friendly_team[2].health = 2
        self.friendly_team[3].health = 2
        duplicates = self.friendly_team[1:4]
        for i in range(3):
            self.assertEqual(
                [self.friendly_team[-1], duplicates[i]],
                selector.select(self.friendly_team, num=2, rand=i / 3),
            )
        self.assertEqual(
            [self.friendly_team[-1], *duplicates[:2]],
            selector.select(self.friendly_team, num=3, rand=0),
        )
        self.assertEqual(
            [self.friendly_team[-1], *duplicates],
            selector.select(self.friendly_team, num=4, rand=0),
        )

    def test_strength_selector(self):
        selector = StrengthSelector()
        selector_low = StrengthSelector(highest=False)
        for i, p in enumerate(self.friendly_team):
            p.attack = i

        self.assertEqual([], selector.select(self.friendly_team, num=0, rand=0))
        self.assertEqual(
            self.friendly_team[::-1], selector.select(self.friendly_team, num=5, rand=0)
        )
        self.assertEqual(
            self.friendly_team, selector_low.select(self.friendly_team, num=5, rand=0)
        )
        self.assertEqual(
            [self.friendly_team[4]], selector.select(self.friendly_team, num=1, rand=0)
        )
        self.assertEqual(
            [self.friendly_team[0]],
            selector_low.select(self.friendly_team, num=1, rand=0),
        )

        # Check randomness when attack + health is all equal
        for i, p in enumerate(self.friendly_team):
            p.health = 4 - i
        self.assertEqual(
            [self.friendly_team[0]],
            selector_low.select(self.friendly_team, num=1, rand=0),
        )
        self.assertEqual(
            [self.friendly_team[1]],
            selector_low.select(self.friendly_team, num=1, rand=1 / 5),
        )

    def test_attack_selector(self):
        selector = AttackSelector()
        selector_low = AttackSelector(highest=False)
        for i, p in enumerate(self.friendly_team):
            p.attack = i

        self.assertEqual([], selector.select(self.friendly_team, num=0, rand=0))
        self.assertEqual(
            self.friendly_team[::-1], selector.select(self.friendly_team, num=5, rand=0)
        )
        self.assertEqual(
            self.friendly_team, selector_low.select(self.friendly_team, num=5, rand=0)
        )
        self.assertEqual(
            [self.friendly_team[4]], selector.select(self.friendly_team, num=1, rand=0)
        )
        self.assertEqual(
            [self.friendly_team[0]],
            selector_low.select(self.friendly_team, num=1, rand=0),
        )


class SelectorToDictTestCase(TestCase):
    def test_simple_selector_to_dict(self):
        test_dict = {
            FirstSelector: {"selector": "FIRST"},
            LastSelector: {"selector": "LAST"},
            RandomSelector: {"selector": "RANDOM"},
        }
        for sel, result in test_dict.items():
            self.assertEqual(result, sel().to_dict())

    def test_value_selector_to_dict(self):
        test_dict = {
            AttackSelector: {"selector": "ATTACK"},
            HealthSelector: {"selector": "HEALTH"},
            StrengthSelector: {"selector": "STRENGTH"},
        }
        for sel, result in test_dict.items():
            result["highest"] = True
            self.assertEqual(result, sel(highest=True).to_dict())
            result["highest"] = False
            self.assertEqual(result, sel(highest=False).to_dict())


class SelectorFromDictTestCase(TestCase):
    def test_simple_selector_from_dict(self):
        test_dict = {
            FirstSelector: {"selector": "FIRST"},
            LastSelector: {"selector": "LAST"},
            RandomSelector: {"selector": "RANDOM"},
        }
        for sel, dict_ in test_dict.items():
            self.assertIsInstance(Selector.from_dict(dict_), sel)

        with self.assertRaises(ValueError):
            Selector.from_dict({"selector": "invalid value"})
        with self.assertRaises(ValueError):
            Selector.from_dict({"selector": "invalid value"})

    def test_value_selector_from_dict(self):
        test_dict = {
            AttackSelector: {"selector": "ATTACK"},
            HealthSelector: {"selector": "HEALTH"},
            StrengthSelector: {"selector": "STRENGTH"},
        }
        for sel, dict_ in test_dict.items():
            dict_["highest"] = True
            self.assertIsInstance(Selector.from_dict(dict_), sel)
            dict_["highest"] = False
            self.assertIsInstance(Selector.from_dict(dict_), sel)

        with self.assertRaises(ValueError):
            Selector.from_dict({"selector": "ATTACK"})
        with self.assertRaises(ValueError):
            Selector.from_dict({"selector": "ATTACK", "highest": "true"})
