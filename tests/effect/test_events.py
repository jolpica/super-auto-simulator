from unittest import TestCase
from unittest.mock import Mock
from sapai.effect.events import Event, EventType
from sapai.pets import Pet


class EventTestCase(TestCase):
    def setUp(self):
        self.friendly_team = [Mock(Pet) for i in range(5)]
        self.enemy_team = [Mock(Pet) for i in range(5)]
        self.other_pet = Mock(Pet)

    def test_init_more_than_2_teams(self):
        """Raises an error if more than 2 teams are supplied"""
        with self.assertRaises(ValueError):
            Event(
                EventType.NONE,
                in_battle=True,
                teams=(
                    self.friendly_team,
                    self.enemy_team,
                    [Mock(Pet) for i in range(5)],
                ),
            )

    def test_pet_in_event_teams(self):
        """Tests pet_in_event_teams returns true when pet is in the event"""
        event0 = Event(EventType.NONE, teams=(self.friendly_team,))
        event1 = Event(EventType.NONE, teams=(self.friendly_team, self.enemy_team))
        event2 = Event(EventType.NONE, teams=(self.enemy_team, self.friendly_team))

        for i in range(5):
            # Pet in only team
            self.assertTrue(event0.pet_in_event_teams(self.friendly_team[i]))
            # Pet in first of 2 teams
            self.assertTrue(event1.pet_in_event_teams(self.friendly_team[i]))
            # Pet in second team
            self.assertTrue(event2.pet_in_event_teams(self.friendly_team[i]))

        # No teams given
        event3 = Event(EventType.NONE, teams=tuple())
        self.assertFalse(event3.pet_in_event_teams(self.other_pet))
        # Pet not in either team
        self.assertFalse(event1.pet_in_event_teams(self.other_pet))
        # Pet is owner, but not in either team
        event4 = Event(
            EventType.NONE,
            pet=self.other_pet,
            teams=(self.friendly_team, self.enemy_team),
        )
        self.assertFalse(event4.pet_in_event_teams(self.other_pet))

    def test_get_named_teams(self):
        event0 = Event(EventType.NONE, teams=tuple())
        event1 = Event(EventType.NONE, teams=(self.friendly_team,))
        event2 = Event(EventType.NONE, teams=(self.friendly_team, self.enemy_team))

        # Error raised when not in any team
        with self.assertRaises(ValueError):
            event0.get_ordered_teams(self.other_pet)
        with self.assertRaises(ValueError):
            event1.get_ordered_teams(self.other_pet)
        with self.assertRaises(ValueError):
            event2.get_ordered_teams(self.other_pet)

        # Pet in first team
        friendly, enemy = event1.get_ordered_teams(self.friendly_team[0])
        self.assertEqual(friendly, self.friendly_team)
        self.assertEqual(enemy, [])
        friendly, enemy = event2.get_ordered_teams(self.friendly_team[0])
        self.assertEqual(friendly, self.friendly_team)
        self.assertEqual(enemy, self.enemy_team)
        # Pet in second team
        friendly, enemy = event2.get_ordered_teams(self.enemy_team[0])
        self.assertEqual(enemy, self.friendly_team)
        self.assertEqual(friendly, self.enemy_team)
