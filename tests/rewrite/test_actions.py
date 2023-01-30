from unittest.mock import Mock

import pytest

from sapai.rewrite.actions import Action, ActionType, AddStatsAction, TargetedAction
from sapai.rewrite.targets import TargetGenerator


@pytest.fixture
def target_generator(friendly_team):
    target_generator = Mock(TargetGenerator)
    target_generator.get = lambda *args: [pet for pet in friendly_team]
    return target_generator


def test_add_stats_action(target_generator):
    addstats_action = AddStatsAction(target_generator)
