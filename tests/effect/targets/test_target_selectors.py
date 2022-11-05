from unittest import TestCase
from unittest.mock import Mock
from sapai.effect.events import Event, EventType
from sapai.effect.targets import FirstTargetSelector, LastTargetSelector
from sapai.pets import Pet


class TargetSelectorTestCase(TestCase):
    def setUp(self):
        self.friendly_team = [Mock(Pet) for i in range(5)]
        self.enemy_team = [Mock(Pet) for i in range(5)]

    def test_first_target_selector(self):
        """Tests AllTargetPool returns all friendly and enemy pets"""
        selector = FirstTargetSelector()
        self.assertEqual([], selector.select(self.friendly_team, n=0))
        self.assertEqual(
            [self.friendly_team[0]], selector.select(self.friendly_team, n=1)
        )
        self.assertEqual(self.friendly_team, selector.select(self.friendly_team, n=5))
        self.assertEqual(self.friendly_team, selector.select(self.friendly_team, n=10))
