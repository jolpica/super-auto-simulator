from unittest import TestCase
from unittest.mock import Mock

from sapai.rewrite.events import Event, EventType
from sapai.rewrite.targets import (
    AdjacentFilter,
    AheadFilter,
    AllFilter,
    AnyFilter,
    BehindFilter,
    EnemyFilter,
    FilterType,
    FriendlyFilter,
    MultiFilter,
    NoneFilter,
    NotSelfFilter,
    SelfFilter,
    Filter,
    FilterType,
)
from sapai.pets import Pet


class FilterTypeTestCase(TestCase):
    def test_to_from_class(self):
        """Tests all types map to a class and back"""
        for type_ in FilterType:
            class_ = type_.to_class()
            self.assertTrue(issubclass(class_, Filter))
            self.assertEqual(FilterType.from_class(class_), type_)


class TargetFilterTestCase(TestCase):
    def setUp(self):
        self.friendly_team = [Mock(Pet) for i in range(5)]
        for i, p in enumerate(self.friendly_team):
            p.index = i
            p.__repr__ = lambda s: str(s.index)
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
        multi = Mock(MultiFilter)
        owner = self.friendly_team[0]
        try:
            MultiFilter.__init__(multi, owner, [])
            MultiFilter.__init__(multi, owner, [SelfFilter(owner)])
            MultiFilter.__init__(
                multi, owner, (FriendlyFilter(owner), SelfFilter(owner))
            )
        except Exception as e:
            self.fail("MultiTargetFilter should accept iterables of filters")
        # Check with None
        with self.assertRaises(TypeError) as terr:
            MultiFilter.__init__(multi, owner, None)
        if "abstract" in terr.exception.args[0]:
            self.fail()
        with self.assertRaises(TypeError) as terr:
            MultiFilter.__init__(multi, owner, [None])
        if "abstract" in terr.exception.args[0]:
            self.fail()

    def test_all_filter(self):
        """Test AnyTrigger will do boolean OR on given triggers"""
        owner = self.friendly_team[0]
        filter_s = SelfFilter(owner)
        filter_f = FriendlyFilter(owner)
        filter_e = EnemyFilter(owner)
        # Empty list returns original list
        filt = AllFilter(owner, [])
        self.assertEqual(
            self.combined_team, filt.filter(self.combined_team, self.event2)
        )
        # multiple of same filter has same result
        expected = filter_s.filter(self.combined_team, self.event2)
        filt = AllFilter(owner, [filter_s])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        filt = AllFilter(owner, [filter_s, filter_s])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        # self + friendly combined
        expected = []
        filt = AllFilter(owner, [filter_s, filter_e])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        filt = AllFilter(owner, [filter_e, filter_s])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        # return nothing
        filt = AllFilter(owner, [filter_s, filter_e])
        self.assertEqual([], filt.filter(self.enemy_team, self.event2))

    def test_any_filter(self):
        """Test AnyTrigger will do boolean OR on given triggers"""
        owner = self.friendly_team[0]
        filter_s = SelfFilter(owner)
        filter_f = FriendlyFilter(owner)
        filter_e = EnemyFilter(owner)
        # Empty list
        filt = AnyFilter(owner, [])
        self.assertEqual([], filt.filter(self.combined_team, self.event2))
        # multiple of same filter has same result
        expected = filter_s.filter(self.combined_team, self.event2)
        filt = AnyFilter(owner, [filter_s])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        filt = AnyFilter(owner, [filter_s, filter_s])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        # self + enemy combined
        expected = filter_s.filter(self.combined_team, self.event2) + filter_e.filter(
            self.combined_team, self.event2
        )
        filt = AnyFilter(owner, [filter_s, filter_e])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        filt = AnyFilter(owner, [filter_e, filter_s])
        self.assertEqual(expected, filt.filter(self.combined_team, self.event2))
        # return nothing
        filt = AnyFilter(owner, [filter_s, filter_f])
        self.assertEqual([], filt.filter(self.enemy_team, self.event2))

    def test_none_filter(self):
        filt = NoneFilter(self.friendly_team[0])
        self.assertEqual(
            self.friendly_team,
            filt.filter(self.friendly_team, self.event0),
        )
        self.assertEqual(
            self.friendly_team,
            filt.filter(self.friendly_team, self.event1),
        )
        self.assertEqual(
            self.friendly_team,
            filt.filter(self.friendly_team, self.event2),
        )
        self.assertEqual(
            self.combined_team,
            filt.filter(self.combined_team, self.event2),
        )

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

    def test_ahead_filter(self):
        # Error if owner isn't in either team
        filt = AheadFilter(Mock(Pet))
        with self.assertRaises(ValueError):
            filt.filter(self.friendly_team, self.event2)
        # no pets ahead
        filt = AheadFilter(self.friendly_team[0])
        self.assertEqual([], filt.filter(self.combined_team, self.event1))
        self.assertEqual([], filt.filter(self.friendly_team, self.event2))
        # pets ahead
        filt = AheadFilter(self.friendly_team[4])
        self.assertEqual(
            self.friendly_team[3::-1],
            filt.filter(self.friendly_team, self.event2),
        )
        self.assertEqual(
            self.friendly_team[3::-1] + self.enemy_team,
            filt.filter(self.combined_team, self.event2),
        )

    def test_behind_filter(self):
        # Error if owner isn't in either team
        filt = BehindFilter(Mock(Pet))
        with self.assertRaises(ValueError):
            filt.filter(self.friendly_team, self.event2)
        # no pets behind
        filt = BehindFilter(self.friendly_team[4])
        self.assertEqual([], filt.filter(self.combined_team, self.event1))
        self.assertEqual([], filt.filter(self.combined_team, self.event2))
        # pets ahead
        filt = BehindFilter(self.friendly_team[0])
        self.assertEqual(
            self.friendly_team[1:],
            filt.filter(self.friendly_team, self.event2),
        )
        self.assertEqual(
            self.friendly_team[1:],
            filt.filter(self.combined_team, self.event2),
        )

    def test_adjacent_filter(self):
        # Error if owner isn't in either team
        filt = AdjacentFilter(Mock(Pet))
        with self.assertRaises(ValueError):
            filt.filter(self.friendly_team, self.event2)
        # Pet is at back of team
        filt = AdjacentFilter(self.friendly_team[4])
        self.assertEqual(
            [self.friendly_team[3]],
            filt.filter(self.friendly_team, self.event1),
        )
        self.assertEqual(
            [self.friendly_team[3]],
            filt.filter(self.friendly_team, self.event2),
        )
        # Pet is in middle of team
        filt = AdjacentFilter(self.friendly_team[2])
        self.assertEqual(
            [self.friendly_team[1], self.friendly_team[3]],
            filt.filter(self.friendly_team, self.event1),
        )
        self.assertEqual(
            [self.friendly_team[1], self.friendly_team[3]],
            filt.filter(self.friendly_team, self.event2),
        )
        # Pet at front of team (no enemy)
        filt = AdjacentFilter(self.friendly_team[0])
        self.assertEqual(
            [self.friendly_team[1]],
            filt.filter(self.friendly_team, self.event1),
        )
        self.assertEqual(
            [self.friendly_team[1]],
            filt.filter(self.friendly_team, self.event2),
        )
        # Pet at front of team (with enemy)
        filt = AdjacentFilter(self.friendly_team[0])
        self.assertEqual(
            [self.friendly_team[1]],
            filt.filter(self.friendly_team[::-1] + self.enemy_team, self.event1),
        )
        self.assertEqual(
            [self.friendly_team[1], self.enemy_team[0]],
            filt.filter(self.friendly_team[::-1] + self.enemy_team, self.event2),
        )


class FilterToDictTestCase(TestCase):
    def test_simple_filter_to_dict(self):
        """Tests non op filters (not multi)"""
        test_dict = {
            AdjacentFilter: {"filter": "ADJACENT"},
            AheadFilter: {"filter": "AHEAD"},
            BehindFilter: {"filter": "BEHIND"},
            EnemyFilter: {"filter": "ENEMY"},
            FriendlyFilter: {"filter": "FRIENDLY"},
            NotSelfFilter: {"filter": "NOT_SELF"},
            SelfFilter: {"filter": "SELF"},
        }
        owner = Mock(Pet)
        for filt, result in test_dict.items():
            self.assertEqual(result, filt(owner).to_dict())

    def test_multi_filter_to_dict(self):
        """Test MultiTargetFilter to_dict"""

        class TestMultiFilter(MultiFilter):
            def to_dict(self) -> dict:
                return super().to_dict()

            def filter(self, pets: list[Pet], event: Event):
                pass

        owner = Mock(Pet)
        self.assertEqual(
            {"filters": [{"filter": "AHEAD"}]},
            TestMultiFilter(owner, [AheadFilter(owner)]).to_dict(),
        )
        self.assertEqual(
            {"filters": [{"filter": "AHEAD"}, {"filter": "BEHIND"}]},
            TestMultiFilter(owner, [AheadFilter(owner), BehindFilter(owner)]).to_dict(),
        )
        self.assertEqual(
            {"filters": []},
            TestMultiFilter(owner, []).to_dict(),
        )

    def test_all_any_filter_to_dict(self):
        """Tests to_dict of any or all filter"""
        owner = Mock(Pet)
        filters_list = [{"filter": "AHEAD"}, {"filter": "BEHIND"}]

        self.assertEqual(
            {"op": "ALL", "filters": filters_list},
            AllFilter(owner, [AheadFilter(owner), BehindFilter(owner)]).to_dict(),
        )
        self.assertEqual(
            {"op": "ANY", "filters": filters_list},
            AnyFilter(owner, [AheadFilter(owner), BehindFilter(owner)]).to_dict(),
        )


class FilterFromDictTestCase(TestCase):
    def test_simple_filter_from_dict(self):
        """Creation of filter from dict representation"""
        filter_names = [f.name for f in FilterType]
        owner = Mock(Pet)
        for name in filter_names:
            Filter.from_dict({"filter": name}, owner)

        with self.assertRaises(ValueError):
            Filter.from_dict({"filter": "!?NOTVALID"}, owner)

    def test_multi_filter_from_dict(self):
        owner = Mock(Pet)

        with self.assertRaises(ValueError):
            Filter.from_dict({"op": "ANY"}, owner)
        with self.assertRaises(ValueError):
            Filter.from_dict({"op": "ALL"}, owner)
        with self.assertRaises(ValueError):
            Filter.from_dict({"filters": [SelfFilter(owner).to_dict()]}, owner)

        filt = Filter.from_dict(
            {
                "op": "ANY",
                "filters": [SelfFilter(owner).to_dict(), AheadFilter(owner).to_dict()],
            },
            owner,
        )
        self.assertIsInstance(filt, AnyFilter)
        self.assertEqual(len(filt._filters), 2)

        filt = Filter.from_dict(
            {
                "op": "ALL",
                "filters": [SelfFilter(owner).to_dict(), AheadFilter(owner).to_dict()],
            },
            owner,
        )
        self.assertIsInstance(filt, AllFilter)
        self.assertEqual(len(filt._filters), 2)
