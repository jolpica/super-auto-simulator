from unittest import TestCase
from unittest.mock import Mock
from sapai.effect.events import Event, EventType
from sapai.effect.targets import (
    SelfFilter,
    NotSelfFilter,
    FriendlyFilter,
    EnemyFilter,
    MultiTargetFilter,
    AllTargetFilter,
    AnyTargetFilter,
)
from sapai.pets import Pet


class TargetFilterTestCase(TestCase):
    def setUp(self):
        self.friendly_team = [Mock(Pet) for i in range(5)]
        self.enemy_team = [Mock(Pet) for i in range(5)]
        self.combined_team = []
        for fe in zip(self.friendly_team, self.enemy_team):
            self.combined_team += fe
        # Event with 0 teams given
        self.event0 = Event(
            EventType.NONE,
            pet=self.friendly_team[0],
            in_battle=True,
            teams=tuple(),
        )
        # Event with 1 team given
        self.event1 = Event(
            EventType.NONE,
            pet=self.friendly_team[0],
            in_battle=True,
            teams=(self.friendly_team,),
        )
        # Event with 2 teams given
        self.event2 = Event(
            EventType.NONE,
            pet=self.friendly_team[0],
            in_battle=True,
            teams=(self.friendly_team, self.enemy_team),
        )

    def test_multi_filter(self):
        # Multi filter is abstract so instances can't be made
        multi = Mock(MultiTargetFilter)
        owner = self.friendly_team[0]
        try:
            MultiTargetFilter.__init__(multi, owner, [])
            MultiTargetFilter.__init__(multi, owner, [SelfFilter(owner)])
            MultiTargetFilter.__init__(
                multi, owner, (FriendlyFilter(owner), SelfFilter(owner))
            )
        except Exception as e:
            raise e
            self.fail("MultiTargetFilter should accept iterables of filters")
        # Check with None
        with self.assertRaises(TypeError) as terr:
            MultiTargetFilter.__init__(multi, owner, None)
        if "abstract" in terr.exception.args[0]:
            self.fail()
        with self.assertRaises(TypeError) as terr:
            MultiTargetFilter.__init__(multi, owner, [None])
        if "abstract" in terr.exception.args[0]:
            self.fail()

    def test_all_filter(self):
        """Test AnyTrigger will do boolean OR on given triggers"""
        owner = self.friendly_team[0]
        filter_s = SelfFilter(owner)
        filter_f = FriendlyFilter(owner)
        filter_e = EnemyFilter(owner)
        # Empty list returns original list
        filt = AllTargetFilter(owner, [])
        self.assertEqual(
            self.combined_team, filt.filter(self.combined_team, self.event2)
        )
        # multiple of same filter has same result
        expected = filter_s.filter(self.combined_team, self.event2)
        filt = AllTargetFilter(owner, [filter_s])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        filt = AllTargetFilter(owner, [filter_s, filter_s])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        # self + friendly combined
        expected = []
        filt = AllTargetFilter(owner, [filter_s, filter_e])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        filt = AllTargetFilter(owner, [filter_e, filter_s])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        # return nothing
        filt = AllTargetFilter(owner, [filter_s, filter_e])
        self.assertEqual([], filt.filter(self.enemy_team, self.event2))

    def test_any_filter(self):
        """Test AnyTrigger will do boolean OR on given triggers"""
        owner = self.friendly_team[0]
        filter_s = SelfFilter(owner)
        filter_f = FriendlyFilter(owner)
        filter_e = EnemyFilter(owner)
        # Empty list
        filt = AnyTargetFilter(owner, [])
        self.assertEqual([], filt.filter(self.combined_team, self.event2))
        # multiple of same filter has same result
        expected = filter_s.filter(self.combined_team, self.event2)
        filt = AnyTargetFilter(owner, [filter_s])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        filt = AnyTargetFilter(owner, [filter_s, filter_s])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        # self + enemy combined
        expected = filter_s.filter(self.combined_team, self.event2) + filter_e.filter(
            self.combined_team, self.event2
        )
        filt = AnyTargetFilter(owner, [filter_s, filter_e])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        filt = AnyTargetFilter(owner, [filter_e, filter_s])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        # return nothing
        filt = AnyTargetFilter(owner, [filter_s, filter_f])
        self.assertEqual([], filt.filter(self.enemy_team, self.event2))

    def test_self_filter(self):
        filt = SelfFilter(self.friendly_team[0])
        self.assertEqual(1, len(filt.filter(self.friendly_team, self.event0)))
        self.assertEqual(1, len(filt.filter(self.friendly_team, self.event1)))
        self.assertEqual(1, len(filt.filter(self.friendly_team, self.event2)))
        self.assertIn(
            self.friendly_team[0], filt.filter(self.friendly_team, self.event2)
        )

        self.assertEqual(0, len(filt.filter(self.enemy_team, self.event0)))
        self.assertEqual(0, len(filt.filter(self.enemy_team, self.event1)))
        self.assertEqual(0, len(filt.filter(self.enemy_team, self.event2)))

    def test_not_self_filter(self):
        filt = NotSelfFilter(self.friendly_team[0])
        self.assertEqual(4, len(filt.filter(self.friendly_team, self.event0)))
        self.assertEqual(4, len(filt.filter(self.friendly_team, self.event1)))
        self.assertEqual(4, len(filt.filter(self.friendly_team, self.event2)))
        self.assertEqual(
            self.friendly_team[1:], filt.filter(self.friendly_team, self.event2)
        )

        self.assertEqual(5, len(filt.filter(self.enemy_team, self.event0)))
        self.assertEqual(5, len(filt.filter(self.enemy_team, self.event1)))
        self.assertEqual(5, len(filt.filter(self.enemy_team, self.event2)))

    def test_friendly_filter(self):
        filt = FriendlyFilter(self.friendly_team[0])
        # Error if owner isn't in either team
        with self.assertRaises(ValueError):
            filt.filter(self.friendly_team, self.event0)
        # remove or keep whole list
        self.assertEqual(
            self.friendly_team, filt.filter(self.friendly_team, self.event2)
        )
        self.assertEqual([], filt.filter(self.enemy_team, self.event2))
        # Partial filtering of list of pets
        self.assertEqual(
            self.friendly_team,
            filt.filter(self.friendly_team + self.enemy_team, self.event2),
        )
        self.assertEqual(
            self.friendly_team,
            filt.filter(self.enemy_team + self.friendly_team, self.event2),
        )
        # Mixed filtering of mixed teams
        self.assertEqual(
            [self.friendly_team[0]],
            filt.filter([*self.enemy_team, self.friendly_team[0]], self.event2),
        )
        self.assertEqual(
            [self.friendly_team[1], self.friendly_team[0]],
            filt.filter(
                [self.friendly_team[1], *self.enemy_team, self.friendly_team[0]],
                self.event2,
            ),
        )

    def test_enemy_filter(self):
        filt = EnemyFilter(self.friendly_team[0])
        # Error if owner isn't in either team
        with self.assertRaises(ValueError):
            filt.filter(self.friendly_team, self.event0)
        # remove or keep whole list
        self.assertEqual([], filt.filter(self.friendly_team, self.event2))
        self.assertEqual(self.enemy_team, filt.filter(self.enemy_team, self.event2))
        # Partial filtering of list of pets
        self.assertEqual(
            self.enemy_team,
            filt.filter(self.friendly_team + self.enemy_team, self.event2),
        )
        self.assertEqual(
            self.enemy_team,
            filt.filter(self.enemy_team + self.friendly_team, self.event2),
        )
        # Mixed filtering of mixed teams
        self.assertEqual(
            [self.enemy_team[0]],
            filt.filter([*self.friendly_team, self.enemy_team[0]], self.event2),
        )
        self.assertEqual(
            [self.enemy_team[1], self.enemy_team[0]],
            filt.filter(
                [self.enemy_team[1], *self.friendly_team, self.enemy_team[0]],
                self.event2,
            ),
        )
