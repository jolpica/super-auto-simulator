from unittest import TestCase
from unittest.mock import Mock
from sapai.rewrite.triggers import (
    AheadTrigger,
    AllTrigger,
    AlwaysTrigger,
    AnyTrigger,
    CountTrigger,
    EnemyTrigger,
    FriendlyTrigger,
    LimitTrigger,
    ModifierTrigger,
    SelfTrigger,
    NeverTrigger,
    Trigger,
    TypeTrigger,
    MultiTrigger,
)
from sapai.rewrite.events import Event, EventType
from sapai.pets import Pet


class TriggerFactoryTestCase(TestCase):
    def test_trigger_to_dict(self):
        trigger_dict = {"op": False}
        self.assertEqual(NeverTrigger().to_dict(), trigger_dict)
        trigger_dict = {"op": True}
        self.assertEqual(AlwaysTrigger().to_dict(), trigger_dict)

    def test_trigger_from_dict(self):
        trigger_dict = {"op": False}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), NeverTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        trigger_dict = {"op": True}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), AlwaysTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)

    def test_multi_trigger_to_dict(self):
        sub_triggers = [NeverTrigger(), AlwaysTrigger(), TypeTrigger(EventType.ATTACK)]
        sub_triggers = sorted(sub_triggers)
        sub_triggers_dict = [t.to_dict() for t in sub_triggers]

        trigger_dict = {"op": "ANY", "triggers": []}
        self.assertEqual(AnyTrigger([]).to_dict(), trigger_dict)
        trigger_dict = {"op": "ANY", "triggers": sub_triggers_dict}
        self.assertEqual(AnyTrigger(sub_triggers).to_dict(), trigger_dict)
        trigger_dict = {"op": "ALL", "triggers": []}
        self.assertEqual(AllTrigger([]).to_dict(), trigger_dict)
        trigger_dict = {"op": "ALL", "triggers": sub_triggers_dict}
        self.assertEqual(AllTrigger(sub_triggers).to_dict(), trigger_dict)

        # Assert order is irrelavent
        trigger1 = AllTrigger(sub_triggers)
        trigger2 = AllTrigger(sub_triggers[::-1])
        trigger_dict = {"op": "ALL", "triggers": sub_triggers_dict}
        self.assertEqual(trigger1.to_dict(), trigger2.to_dict())

    def test_multi_trigger_from_dict(self):
        sub_triggers = [NeverTrigger(), AlwaysTrigger(), TypeTrigger(EventType.ATTACK)]
        sub_triggers = sorted(sub_triggers)
        sub_triggers_dict = [t.to_dict() for t in sub_triggers]

        # Throw errors when no op specified
        trigger_dict = {"triggers": []}
        with self.assertRaises(ValueError):
            Trigger.from_dict(trigger_dict)
        trigger_dict = {"triggers": sub_triggers_dict}
        with self.assertRaises(ValueError):
            Trigger.from_dict(trigger_dict)

        trigger_dict = {"op": "ANY", "triggers": []}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), AnyTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        trigger_dict = {"op": "ANY", "triggers": sub_triggers_dict}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), AnyTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        trigger_dict = {"op": "ALL", "triggers": []}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), AllTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        trigger_dict = {"op": "ALL", "triggers": sub_triggers_dict}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), AllTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)

        # Assert order is irrelavent
        trigger_dict = {"op": "ALL", "triggers": sub_triggers_dict}
        trigger1 = Trigger.from_dict(trigger_dict)
        trigger_dict = {"op": "ALL", "triggers": sub_triggers_dict[::-1]}
        trigger2 = Trigger.from_dict(trigger_dict)
        self.assertEqual(trigger1.to_dict(), trigger2.to_dict())
        self.assertEqual(
            trigger1._triggers[0].to_dict(), trigger2._triggers[0].to_dict()
        )
        print()
        print(trigger.to_dict())
        print(trigger_dict)

    def test_type_trigger_to_dict(self):
        trigger_dict = {"event": "NONE"}
        self.assertEqual(TypeTrigger(EventType.NONE).to_dict(), trigger_dict)
        trigger_dict = {"event": "END_OF_TURN"}
        self.assertEqual(TypeTrigger(EventType.END_OF_TURN).to_dict(), trigger_dict)
        # Ensure alias END_TURN is the same as END_OF_TURN
        self.assertEqual(
            TypeTrigger(EventType.END_TURN).to_dict(),
            TypeTrigger(EventType.END_OF_TURN).to_dict(),
        )

    def test_type_trigger_from_dict(self):
        trigger_dict = {"event": "NONE"}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), TypeTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        trigger_dict = {"event": "END_OF_TURN"}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), TypeTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)

    def test_modifier_trigger_to_dict(self):
        trigger_dict = {"event": "NONE", "modifiers": []}
        self.assertEqual(ModifierTrigger(EventType.NONE).to_dict(), trigger_dict)
        # Limit trigger
        trigger_dict = {
            "event": "NONE",
            "modifiers": [{"type": "limit", "n": 3, "reset_event": "START_OF_TURN"}],
        }
        trigger = LimitTrigger(EventType.NONE, n=3, reset_event=EventType.START_OF_TURN)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        trigger = LimitTrigger(EventType.NONE, n=5, reset_event=EventType.NONE)
        trigger_dict = {
            "event": "NONE",
            "modifiers": [{"type": "limit", "n": 5, "reset_event": "NONE"}],
        }
        self.assertEqual(trigger.to_dict(), trigger_dict)
        # Count Trigger
        trigger_dict = {
            "event": "NONE",
            "modifiers": [{"type": "count", "n": 3, "reset_event": "START_OF_TURN"}],
        }
        trigger = CountTrigger(EventType.NONE, n=3, reset_event=EventType.START_OF_TURN)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        trigger = CountTrigger(EventType.NONE, n=5, reset_event=EventType.NONE)
        trigger_dict = {
            "event": "NONE",
            "modifiers": [{"type": "count", "n": 5, "reset_event": "NONE"}],
        }
        self.assertEqual(trigger.to_dict(), trigger_dict)
        # Self Trigger
        trigger_dict = {"event": "NONE", "modifiers": [{"type": "self"}]}
        trigger = SelfTrigger(EventType.NONE)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        # Friendly Trigger
        trigger_dict = {"event": "NONE", "modifiers": [{"type": "friendly"}]}
        trigger = FriendlyTrigger(EventType.NONE)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        # Enemy Trigger
        trigger_dict = {"event": "NONE", "modifiers": [{"type": "enemy"}]}
        trigger = EnemyTrigger(EventType.NONE)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        # Ahead Trigger
        trigger_dict = {"event": "NONE", "modifiers": [{"type": "ahead"}]}
        trigger = AheadTrigger(EventType.NONE)
        self.assertEqual(trigger.to_dict(), trigger_dict)

    def test_modifier_trigger_from_dict(self):
        # Type trigger when given empty list of modifiers
        trigger_dict = {"event": "NONE", "modifiers": []}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), TypeTrigger)
        del trigger_dict["modifiers"]
        self.assertEqual(trigger.to_dict(), trigger_dict)

        # Limit trigger
        trigger_dict = {
            "event": "NONE",
            "modifiers": [{"type": "limit", "n": 3, "reset_event": "START_OF_TURN"}],
        }
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), LimitTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        trigger_dict = {
            "event": "NONE",
            "modifiers": [{"type": "limit", "n": 5, "reset_event": "NONE"}],
        }
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), LimitTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        # Count Trigger
        trigger_dict = {
            "event": "NONE",
            "modifiers": [{"type": "count", "n": 3, "reset_event": "START_OF_TURN"}],
        }
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), CountTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        trigger_dict = {
            "event": "NONE",
            "modifiers": [{"type": "count", "n": 5, "reset_event": "NONE"}],
        }
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), CountTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        # Self Trigger
        trigger_dict = {"event": "NONE", "modifiers": [{"type": "self"}]}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), SelfTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        # Friendly Trigger
        trigger_dict = {"event": "NONE", "modifiers": [{"type": "friendly"}]}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), FriendlyTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        # Enemy Trigger
        trigger_dict = {"event": "NONE", "modifiers": [{"type": "enemy"}]}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), EnemyTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)
        # Ahead Trigger
        trigger_dict = {"event": "NONE", "modifiers": [{"type": "ahead"}]}
        trigger = Trigger.from_dict(trigger_dict)
        self.assertEqual(type(trigger), AheadTrigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)

    def test_nested_trigger_to_dict(self):
        """Test nesting of triggers"""
        modi_trigger_dict = {
            "event": "NONE",
            "modifiers": [{"type": "ahead"}, {"type": "friendly"}],
        }
        modi_trigger = FriendlyTrigger(AheadTrigger(EventType.NONE))
        self.assertEqual(modi_trigger.to_dict(), modi_trigger_dict)
        multi_trigger_dict = {
            "op": "ALL",
            "triggers": [modi_trigger_dict],
        }
        multi_trigger = AllTrigger([modi_trigger])
        self.assertEqual(multi_trigger.to_dict(), multi_trigger_dict)
        trigger_dict = {
            "op": "ALL",
            "triggers": [modi_trigger_dict],
            "modifiers": [{"type": "self"}],
        }
        trigger = SelfTrigger(multi_trigger)
        self.assertEqual(trigger.to_dict(), trigger_dict)

    def test_nested_trigger_from_dict(self):
        """Test nesting of triggers"""
        modi_trigger_dict = {
            "event": "NONE",
            "modifiers": [{"type": "ahead"}, {"type": "friendly"}],
        }
        trigger1 = Trigger.from_dict(modi_trigger_dict)
        modi_trigger_dict["modifiers"] = modi_trigger_dict["modifiers"][::-1]
        trigger2 = Trigger.from_dict(modi_trigger_dict)
        self.assertEqual(type(trigger1), type(trigger2))
        self.assertEqual(trigger1.to_dict(), trigger2.to_dict())

        multi_trigger_dict = {
            "op": "ALL",
            "triggers": [modi_trigger_dict, {"event": "START_OF_BATTLE"}],
        }
        trigger1 = Trigger.from_dict(multi_trigger_dict)
        multi_trigger_dict["triggers"] = multi_trigger_dict["triggers"][::-1]
        trigger2 = Trigger.from_dict(multi_trigger_dict)
        self.assertEqual(type(trigger1), type(trigger2))
        self.assertEqual(trigger1.to_dict(), trigger2.to_dict())

        multi_trigger_dict = {
            "op": "ALL",
            "triggers": [modi_trigger_dict, {"event": "START_OF_BATTLE"}],
            "modifiers": [{"type": "self"}, {"type": "ahead"}],
        }
        trigger1 = Trigger.from_dict(multi_trigger_dict)
        multi_trigger_dict["triggers"][0]["modifiers"] = modi_trigger_dict["modifiers"][
            ::-1
        ]
        multi_trigger_dict["triggers"] = multi_trigger_dict["triggers"][::-1]
        multi_trigger_dict["modifiers"] = multi_trigger_dict["modifiers"][::-1]
        trigger2 = Trigger.from_dict(multi_trigger_dict)
        self.assertEqual(type(trigger1), type(trigger2))
        self.assertEqual(trigger1.to_dict(), trigger2.to_dict())


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

    def test_never_trigger(self):
        """Never trigger is always false"""
        trigger = NeverTrigger()

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
        # Multitrigger is an abstract class so no instances can be made
        # Test by using a mock self instance
        multi = Mock(MultiTrigger)
        try:
            MultiTrigger.__init__(multi, [])
            MultiTrigger.__init__(multi, [NeverTrigger()])
            MultiTrigger.__init__(multi, (NeverTrigger(), AlwaysTrigger()))
        except:
            self.fail("Multitrigger should accept iterables of triggers")
        # Check with None
        with self.assertRaises(TypeError) as terr:
            MultiTrigger.__init__(multi, None)
        if "abstract" in terr.exception.args[0]:
            self.fail()
        with self.assertRaises(TypeError) as terr:
            MultiTrigger.__init__(multi, [None])
        if "abstract" in terr.exception.args[0]:
            self.fail()

    def test_any_trigger(self):
        """Test AnyTrigger will do boolean OR on given triggers"""
        # Empty list
        trigger = AnyTrigger([])
        self.assertFalse(trigger.is_triggered(self.none_event))
        # False
        trigger = AnyTrigger([NeverTrigger()])
        self.assertFalse(trigger.is_triggered(self.none_event))
        trigger = AnyTrigger([NeverTrigger(), NeverTrigger()])
        self.assertFalse(trigger.is_triggered(self.none_event))
        # True
        trigger = AnyTrigger([AlwaysTrigger()])
        self.assertTrue(trigger.is_triggered(self.none_event))
        trigger = AnyTrigger([AlwaysTrigger(), AlwaysTrigger()])
        self.assertTrue(trigger.is_triggered(self.none_event))
        trigger = AnyTrigger([NeverTrigger(), NeverTrigger(), AlwaysTrigger()])
        self.assertTrue(trigger.is_triggered(self.none_event))
        trigger = AnyTrigger([AlwaysTrigger(), NeverTrigger(), NeverTrigger()])
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
        trigger = AllTrigger([NeverTrigger()])
        self.assertFalse(trigger.is_triggered(self.none_event))
        trigger = AllTrigger([NeverTrigger(), NeverTrigger()])
        self.assertFalse(trigger.is_triggered(self.none_event))
        trigger = AllTrigger([NeverTrigger(), NeverTrigger(), AlwaysTrigger()])
        self.assertFalse(trigger.is_triggered(self.none_event))
        trigger = AllTrigger([AlwaysTrigger(), NeverTrigger(), NeverTrigger()])
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
        trigger = ModifierTrigger(NeverTrigger())
        self.assertFalse(trigger.is_triggered(None))
        trigger = ModifierTrigger(AlwaysTrigger())
        self.assertTrue(trigger.is_triggered(None))

    def test_limit_trigger(self):
        """Limited Trigger only triggers a maximum amount of times"""
        trigger = LimitTrigger(
            AlwaysTrigger(), n=3, reset_event=EventType.START_OF_TURN
        )
        count = 0
        for i in range(5):
            if trigger.is_triggered(self.none_event):
                count += 1
        self.assertEqual(count, 3)
        # Test trigger that sometimes is false
        trigger = LimitTrigger(
            TypeTrigger(EventType.NONE), n=3, reset_event=EventType.START_OF_TURN
        )
        count = 0
        for i in range(5):
            if trigger.is_triggered(self.none_event):
                count += 1
            if trigger.is_triggered(self.start_of_battle_event):
                count += 1
        self.assertEqual(count, 3)
        # Test trigger can reset
        trigger = LimitTrigger(
            TypeTrigger(EventType.NONE), n=1, reset_event=EventType.START_OF_TURN
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

        with self.assertRaises(TypeError):
            LimitTrigger(EventType.NONE, n=1, reset_event="NONE")
        with self.assertRaises(TypeError):
            LimitTrigger(EventType.NONE, n=1, reset_event=None)

    def test_count_trigger(self):
        """count Trigger only triggers a every n times"""
        trigger = CountTrigger(AlwaysTrigger(), n=2)
        count = 0
        for i in range(5):
            if trigger.is_triggered(self.none_event):
                count += 1
        self.assertEqual(count, 2)
        trigger = CountTrigger(AlwaysTrigger(), n=3)
        count = 0
        for i in range(5):
            if trigger.is_triggered(self.none_event):
                count += 1
        self.assertEqual(count, 1)
        # Test trigger that sometimes is false
        trigger = CountTrigger(TypeTrigger(EventType.NONE), n=2)
        count = 0
        for i in range(5):
            if trigger.is_triggered(self.none_event):
                count += 1
            if trigger.is_triggered(self.start_of_battle_event):
                count += 1
        self.assertEqual(count, 2)
        # Test trigger can reset
        trigger = CountTrigger(
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

        with self.assertRaises(TypeError):
            CountTrigger(EventType.NONE, n=1, reset_event="NONE")
        with self.assertRaises(TypeError):
            CountTrigger(EventType.NONE, n=1, reset_event=None)

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
        trigger = CountTrigger(FriendlyTrigger(EventType.FAINT), n=2)

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
