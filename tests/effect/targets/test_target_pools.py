from unittest import TestCase
from unittest.mock import Mock
from sapai.effect.events import Event, EventType
from sapai.effect.targets import BattlefieldTargetPool
from sapai.pets import Pet


class TargetPoolTestCase(TestCase):
    def setUp(self):
        self.friendly_team = [Mock(Pet) for i in range(5)]
        self.enemy_team = [Mock(Pet) for i in range(5)]
        self.event0 = Event(
            EventType.NONE,
            pet=self.friendly_team[0],
            in_battle=True,
            teams=tuple(),
        )
        self.event1 = Event(
            EventType.NONE,
            pet=self.friendly_team[0],
            in_battle=True,
            teams=(self.friendly_team,),
        )
        self.event2 = Event(
            EventType.NONE,
            pet=self.friendly_team[0],
            in_battle=True,
            teams=(self.friendly_team, self.enemy_team),
        )

    def test_battlefield_target_pool(self):
        """Tests AllTargetPool returns all friendly and enemy pets"""
        target_pool = BattlefieldTargetPool()
        pets = target_pool.get_targets(self.event0, self.friendly_team[0])
        self.assertEqual(len(pets), 0)

        pets = target_pool.get_targets(self.event1, self.friendly_team[0])
        self.assertEqual(len(pets), 5)

        pets = target_pool.get_targets(self.event2, self.friendly_team[0])
        self.assertEqual(len(pets), 10)
