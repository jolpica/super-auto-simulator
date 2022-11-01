from unittest import TestCase
from unittest.mock import Mock
from sapai.effect.events import Event, EventType
from sapai.effect.targets import SelfFilter, NotSelfFilter, FriendlyFilter, EnemyFilter
from sapai.pets import Pet


class TargetFilterTestCase(TestCase):
    def setUp(self):
        self.friendly_team = [Mock(Pet) for i in range(5)]
        self.enemy_team = [Mock(Pet) for i in range(5)]
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
