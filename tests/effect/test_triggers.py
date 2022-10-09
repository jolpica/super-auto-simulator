from unittest import TestCase
from unittest.mock import Mock
from sapai.effect.triggers import (
    AheadTrigger,
    AllTrigger,
    AlwaysTrigger,
    AnyTrigger,
    CountNTrigger,
    EnemyTrigger,
    FriendlyTrigger,
    LimitedTrigger,
    ModifierTrigger,
    SelfTrigger,
    Trigger,
    TypeTrigger,
    MultiTrigger,
)
from sapai.effect.events import Event, EventType
from sapai.pets import Pet
from sapai.teams import Team


class TriggerTestCase(TestCase):
    def setUp(self):
        self.pet1 = Mock(Pet)
        self.pet2 = Mock(Pet)
        self.pet3 = Mock(Pet)
        self.pet4 = Mock(Pet)
        self.pet5 = Mock(Pet)
        self.none_event = Event(EventType.NONE)
        self.start_of_turn_event = Event(
            EventType.START_OF_TURN,
            self.pet1,
            teams=[[self.pet1, self.pet2]],
        )
        self.end_of_turn_event = Event(
            EventType.END_OF_TURN,
            self.pet2,
            teams=[[self.pet1, self.pet2, self.pet3, self.pet4]],
        )
        self.start_of_battle_event = Event(
            EventType.START_OF_BATTLE,
            self.pet1,
            teams=[[self.pet1, self.pet2], [self.pet3, self.pet4]],
        )
        self.start_of_battle_pet3_event = Event(
            EventType.START_OF_BATTLE,
            self.pet3,
            teams=[[self.pet1, self.pet2], [self.pet3, self.pet4]],
        )

    def test_trigger(self):
        """Default trigger is false"""
        trigger = Trigger()

        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event), self.pet1)

    def test_always_trigger(self):
        """Always trigger returns true"""
        trigger = AlwaysTrigger()
        self.assertTrue(trigger.is_triggered(self.none_event))
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event))
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event), self.pet1)

    def test_multi_trigger(self):
        """Test MultiTrigger validates input"""
        try:
            MultiTrigger([])
            MultiTrigger([Trigger()])
            MultiTrigger((Trigger(), AlwaysTrigger()))
        except:
            self.fail("Multitrigger should accept iterables of triggers")
        # Check with None
        with self.assertRaises(TypeError):
            MultiTrigger(None)
        with self.assertRaises(TypeError):
            MultiTrigger([None])

    def test_any_trigger(self):
        """Test AnyTrigger will do boolean OR on given triggers"""
        # Empty list
        trigger = AnyTrigger([])
        self.assertFalse(trigger.is_triggered(self.none_event))
        # False
        trigger = AnyTrigger([Trigger()])
        self.assertFalse(trigger.is_triggered(self.none_event))
        trigger = AnyTrigger([Trigger(), Trigger()])
        self.assertFalse(trigger.is_triggered(self.none_event))
        # True
        trigger = AnyTrigger([AlwaysTrigger()])
        self.assertTrue(trigger.is_triggered(self.none_event))
        trigger = AnyTrigger([AlwaysTrigger(), AlwaysTrigger()])
        self.assertTrue(trigger.is_triggered(self.none_event))
        trigger = AnyTrigger([Trigger(), Trigger(), AlwaysTrigger()])
        self.assertTrue(trigger.is_triggered(self.none_event))
        trigger = AnyTrigger([AlwaysTrigger(), Trigger(), Trigger()])
        self.assertTrue(trigger.is_triggered(self.none_event))
        # Check with None
        with self.assertRaises(TypeError):
            trigger = AnyTrigger(None)
        with self.assertRaises(TypeError):
            trigger = AnyTrigger([None])

    def test_all_trigger(self):
        """Test AllTrigger will do boolean AND on given triggers"""
        # Empty list
        trigger = AllTrigger([])
        self.assertFalse(trigger.is_triggered(self.none_event))
        # True
        trigger = AllTrigger([AlwaysTrigger()])
        self.assertTrue(trigger.is_triggered(self.none_event))
        trigger = AllTrigger([AlwaysTrigger(), AlwaysTrigger()])
        self.assertTrue(trigger.is_triggered(self.none_event))
        # False
        trigger = AllTrigger([Trigger()])
        self.assertFalse(trigger.is_triggered(self.none_event))
        trigger = AllTrigger([Trigger(), Trigger()])
        self.assertFalse(trigger.is_triggered(self.none_event))
        trigger = AllTrigger([Trigger(), Trigger(), AlwaysTrigger()])
        self.assertFalse(trigger.is_triggered(self.none_event))
        trigger = AllTrigger([AlwaysTrigger(), Trigger(), Trigger()])
        self.assertFalse(trigger.is_triggered(self.none_event))
        # Check with None
        with self.assertRaises(TypeError):
            trigger = AllTrigger(None)
        with self.assertRaises(TypeError):
            trigger = AllTrigger([None])

    def test_type_trigger(self):
        """Type Trigger is true when event type matches"""
        trigger = TypeTrigger(EventType.START_OF_BATTLE)
        # False when event doesn't match
        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertFalse(trigger.is_triggered(self.none_event, self.pet1))
        # True when event matches
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event))
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event, self.pet2))

        # Test with none values
        trigger = TypeTrigger(EventType.START_OF_BATTLE)
        self.assertFalse(trigger.is_triggered(None))
        self.assertFalse(trigger.is_triggered(None, self.pet1))

        trigger = TypeTrigger(None)
        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertFalse(trigger.is_triggered(self.none_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet2))
        self.assertFalse(trigger.is_triggered(None))
        self.assertFalse(trigger.is_triggered(None, self.pet1))

    def test_modifier_trigger(self):
        """modifier Trigger validates input"""
        # Error on invalid input
        with self.assertRaises(ValueError):
            ModifierTrigger(None)
        # TypeTrigger when EventType given
        trigger = ModifierTrigger(EventType.START_OF_BATTLE)
        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event))

        # Given trigger works as expected
        trigger = ModifierTrigger(Trigger())
        self.assertFalse(trigger.is_triggered(None))
        trigger = ModifierTrigger(AlwaysTrigger())
        self.assertTrue(trigger.is_triggered(None))

    def test_limited_trigger(self):
        """Limited Trigger only triggers a maximum amount of times"""
        trigger = LimitedTrigger(
            AlwaysTrigger(), limit=3, reset_event=EventType.START_OF_TURN
        )
        count = 0
        for i in range(5):
            if trigger.is_triggered(self.none_event):
                count += 1
        self.assertEqual(count, 3)
        # Test trigger that sometimes is false
        trigger = LimitedTrigger(
            TypeTrigger(EventType.NONE), limit=3, reset_event=EventType.START_OF_TURN
        )
        count = 0
        for i in range(5):
            if trigger.is_triggered(self.none_event):
                count += 1
            if trigger.is_triggered(self.start_of_battle_event):
                count += 1
        self.assertEqual(count, 3)
        # Test trigger can reset
        trigger = LimitedTrigger(
            TypeTrigger(EventType.NONE), limit=1, reset_event=EventType.START_OF_TURN
        )
        count = 0
        for i in range(20):
            if i % 5 == 0 and trigger.is_triggered(self.start_of_turn_event):
                count += 1
            if trigger.is_triggered(self.none_event):
                count += 1
            if trigger.is_triggered(self.start_of_battle_event):
                count += 1
        self.assertEqual(count, 4)

    def test_count_n_trigger(self):
        """count Trigger only triggers a every n times"""
        trigger = CountNTrigger(AlwaysTrigger(), n=2)
        count = 0
        for i in range(5):
            if trigger.is_triggered(self.none_event):
                count += 1
        self.assertEqual(count, 2)
        trigger = CountNTrigger(AlwaysTrigger(), n=3)
        count = 0
        for i in range(5):
            if trigger.is_triggered(self.none_event):
                count += 1
        self.assertEqual(count, 1)
        # Test trigger that sometimes is false
        trigger = CountNTrigger(TypeTrigger(EventType.NONE), n=2)
        count = 0
        for i in range(5):
            if trigger.is_triggered(self.none_event):
                count += 1
            if trigger.is_triggered(self.start_of_battle_event):
                count += 1
        self.assertEqual(count, 2)
        # Test trigger can reset
        trigger = CountNTrigger(
            TypeTrigger(EventType.NONE), n=3, reset_event=EventType.START_OF_TURN
        )
        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event))
        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event))
        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertTrue(trigger.is_triggered(self.none_event))

    def test_self_trigger(self):
        """self Trigger tests"""
        # False when no event pet is given
        trigger = SelfTrigger(EventType.NONE)
        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertFalse(trigger.is_triggered(self.none_event, self.pet1))
        # When only 1 team is given
        trigger = SelfTrigger(EventType.START_OF_TURN)
        self.assertTrue(trigger.is_triggered(self.start_of_turn_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.none_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event, self.pet2))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event, self.pet3))
        # When 2 teams are given
        trigger = SelfTrigger(EventType.START_OF_BATTLE)
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertTrue(
            trigger.is_triggered(self.start_of_battle_pet3_event, self.pet3)
        )
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet3))
        self.assertFalse(
            trigger.is_triggered(self.start_of_battle_pet3_event, self.pet1)
        )

    def test_friendly_trigger(self):
        """friendly Trigger does NOT trigger on self, but does trigger on friends"""
        # False when no event pet is given
        trigger = FriendlyTrigger(EventType.NONE)
        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertFalse(trigger.is_triggered(self.none_event, self.pet1))
        # When only 1 team is given
        trigger = FriendlyTrigger(EventType.START_OF_TURN)
        # False when pet is self (friendly pet is not trigger pet)
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event, self.pet1))
        self.assertTrue(trigger.is_triggered(self.start_of_turn_event, self.pet2))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event, self.pet3))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.none_event, self.pet1))
        # When 2 teams are given
        trigger = FriendlyTrigger(EventType.START_OF_BATTLE)
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event, self.pet2))
        self.assertFalse(
            trigger.is_triggered(self.start_of_battle_pet3_event, self.pet3)
        )
        self.assertTrue(
            trigger.is_triggered(self.start_of_battle_pet3_event, self.pet4)
        )
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet3))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet4))
        self.assertFalse(
            trigger.is_triggered(self.start_of_battle_pet3_event, self.pet1)
        )
        self.assertFalse(
            trigger.is_triggered(self.start_of_battle_pet3_event, self.pet2)
        )

    def test_enemy_trigger(self):
        """enemy Trigger triggers on enemy team"""
        # False when no event pet is given
        trigger = EnemyTrigger(EventType.NONE)
        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertFalse(trigger.is_triggered(self.none_event, self.pet1))
        # When only 1 team is given (always false)
        trigger = EnemyTrigger(EventType.START_OF_TURN)
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event, self.pet2))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event, self.pet3))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event, self.pet4))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event, self.pet5))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet3))
        self.assertFalse(trigger.is_triggered(self.none_event, self.pet1))
        # When 2 teams are given
        trigger = EnemyTrigger(EventType.START_OF_BATTLE)
        with self.assertRaises(ValueError):
            trigger.is_triggered(self.start_of_battle_event, self.pet5)
        self.assertTrue(
            trigger.is_triggered(self.start_of_battle_pet3_event, self.pet1)
        )
        self.assertTrue(
            trigger.is_triggered(self.start_of_battle_pet3_event, self.pet2)
        )
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event, self.pet3))
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event, self.pet4))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet2))
        self.assertFalse(
            trigger.is_triggered(self.start_of_battle_pet3_event, self.pet3)
        )
        self.assertFalse(
            trigger.is_triggered(self.start_of_battle_pet3_event, self.pet4)
        )

    def test_ahead_trigger(self):
        """enemy Trigger triggers on enemy team"""
        # False when no event pet is given
        trigger = AheadTrigger(EventType.NONE)
        self.assertFalse(trigger.is_triggered(self.none_event))
        self.assertFalse(trigger.is_triggered(self.none_event, self.pet1))
        # When only 1 team is given
        trigger = AheadTrigger(EventType.END_OF_TURN)  # event pet is pet2
        self.assertTrue(trigger.is_triggered(self.end_of_turn_event, self.pet3))
        self.assertFalse(trigger.is_triggered(self.end_of_turn_event))
        self.assertFalse(trigger.is_triggered(self.end_of_turn_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.end_of_turn_event, self.pet2))
        self.assertFalse(trigger.is_triggered(self.end_of_turn_event, self.pet4))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet3))
        self.assertFalse(trigger.is_triggered(self.none_event, self.pet1))
        trigger = AheadTrigger(EventType.START_OF_TURN)  # event pet is pet1
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event, self.pet1))
        self.assertTrue(trigger.is_triggered(self.start_of_turn_event, self.pet2))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event, self.pet3))
        self.assertFalse(trigger.is_triggered(self.start_of_turn_event, self.pet4))
        # When 2 teams are given
        trigger = AheadTrigger(EventType.START_OF_BATTLE)
        # pet 1 event
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event, self.pet2))
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event, self.pet3))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet4))
        # pet 2 event
        self.start_of_battle_event.pet = self.pet2
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet2))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet3))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet4))
        # pet 3 event
        self.start_of_battle_event.pet = self.pet3
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet2))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet3))
        self.assertTrue(trigger.is_triggered(self.start_of_battle_event, self.pet4))
        # pet 4 event
        self.start_of_battle_event.pet = self.pet4
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet3))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet1))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet2))
        self.assertFalse(trigger.is_triggered(self.start_of_battle_event, self.pet3))


class CompoundTriggerTestCase(TestCase):
    def setUp(self):
        self.pet1 = Mock(Pet)
        self.pet2 = Mock(Pet)
        self.pet3 = Mock(Pet)
        self.pet4 = Mock(Pet)
        self.none_event = Event(EventType.NONE)
        self.start_of_turn_event = Event(
            EventType.START_OF_TURN,
            self.pet1,
            teams=[[self.pet1, self.pet2]],
        )

    def test_friendly_pet_level_up(self):
        """Test clownfish Friendly pet level-up ability trigger"""
        trigger1 = AnyTrigger(
            [
                FriendlyTrigger(EventType.LEVEL_UP),
                SelfTrigger(EventType.LEVEL_UP),
            ]
        )
        trigger2 = AnyTrigger(
            [
                SelfTrigger(EventType.LEVEL_UP),
                FriendlyTrigger(EventType.LEVEL_UP),
            ]
        )
        trigger3 = AnyTrigger(
            [
                FriendlyTrigger(TypeTrigger(EventType.LEVEL_UP)),
                SelfTrigger(EventType.LEVEL_UP),
            ]
        )

        for trigger in (trigger1, trigger2, trigger3):
            # No pet, no teams
            event = Event(EventType.LEVEL_UP)
            self.assertFalse(trigger.is_triggered(event, self.pet1))
            # no team
            event.pet = self.pet1
            self.assertTrue(trigger.is_triggered(event, self.pet1))
            self.assertFalse(trigger.is_triggered(event, self.pet2))
            # singe team
            event.teams = [[self.pet1, self.pet2]]
            self.assertTrue(trigger.is_triggered(event, self.pet1))
            self.assertTrue(trigger.is_triggered(event, self.pet2))
            # two teams
            event.teams.append([self.pet3, self.pet4])
            self.assertTrue(trigger.is_triggered(event, self.pet1))
            self.assertTrue(trigger.is_triggered(event, self.pet2))
            self.assertFalse(trigger.is_triggered(event, self.pet3))
            self.assertFalse(trigger.is_triggered(event, self.pet4))

    def test_two_friends_faint(self):
        """Test vulture Two friends faint ability trigger"""
        trigger = CountNTrigger(FriendlyTrigger(EventType.FAINT), n=2)

        # No pet, no teams
        event = Event(EventType.FAINT, self.pet1)
        self.assertFalse(trigger.is_triggered(event, self.pet1))
        self.assertFalse(trigger.is_triggered(event, self.pet1))
        # Only friendly team
        event.teams = [[self.pet1, self.pet2]]
        self.assertFalse(trigger.is_triggered(event, self.pet1))
        self.assertFalse(trigger.is_triggered(event, self.pet1))
        event.pet = self.pet2
        self.assertFalse(trigger.is_triggered(event, self.pet1))
        self.assertTrue(trigger.is_triggered(event, self.pet1))
        # friendly + enemy team
        event.pet = self.pet1
        event.teams = [[self.pet1, self.pet2], [self.pet3, self.pet4]]
        self.assertFalse(trigger.is_triggered(event, self.pet2))
        self.assertTrue(trigger.is_triggered(event, self.pet2))
        self.assertFalse(trigger.is_triggered(event, self.pet3))
        self.assertFalse(trigger.is_triggered(event, self.pet3))
