from unittest import TestCase
from unittest.mock import Mock
from sapai.effect.triggers import (
    AllTrigger,
    AlwaysTrigger,
    AnyTrigger,
    LimitedTrigger,
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
        self.none_event = Event(EventType.NONE)
        self.start_of_battle_event = Event(
            EventType.START_OF_BATTLE, self.pet1, in_battle=True
        )
        self.start_of_turn_event = Event(EventType.START_OF_TURN, in_battle=False)

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

    def test_type_trigger_none(self):
        """Type Trigger with None values"""
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
