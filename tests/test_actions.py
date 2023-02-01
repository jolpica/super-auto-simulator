from unittest.mock import Mock

import pytest

from superautosim.actions import Action, ActionType, AddStatsAction, TargetedAction
from superautosim.targets import TargetGenerator
from superautosim.teams import Team


def get_mock_target_generator(pets):
    target_generator = Mock(TargetGenerator)
    target_generator.get = lambda _, max_targets=5, *args: list(pets)[:max_targets]
    return target_generator


@pytest.mark.parametrize(
    ["is_temp", "added_stats", "expected_stats"],
    [
        (False, (1, 1), [(i + 1, i + 1, 0, 0) for i in range(1, 6)]),
        (False, (0, 1), [(i, i + 1, 0, 0) for i in range(1, 6)]),
        (False, (-1, 0), [(1, 1, 0, 0), *[(i - 1, i, 0, 0) for i in range(2, 6)]]),
        (True, (-1, 1), [(1, 1, 0, 1), *[(i, i, -1, 1) for i in range(2, 6)]]),
        (True, (100, 100), [(i, i, 50 - i, 50 - i) for i in range(1, 6)]),
    ],
)
def test_add_stats_action(friendly_team: Team, is_temp, added_stats, expected_stats):
    target_generator = get_mock_target_generator(friendly_team)
    addstats_action = AddStatsAction(
        target_generator,
        max_targets=5,
        attack=added_stats[0],
        health=added_stats[1],
        temp_stats=is_temp,
    )

    addstats_action.run(1, None, 0)
    assert len(list(friendly_team)) == len(expected_stats)
    for p, stats in zip(friendly_team, expected_stats):
        assert p.stats == stats


def test_add_stats_action_max_targets(friendly_team):
    target_generator = get_mock_target_generator(friendly_team)

    values = [(1, [2, 2, 3, 4, 5]), (4, [3, 3, 4, 5, 5]), (9, [4, 4, 5, 6, 6])]
    for num_targets, exp_atks in values:
        addstats_action = AddStatsAction(
            target_generator, max_targets=num_targets, attack=1
        )

        addstats_action.run(1, None, 0)
        assert [p.attack for p in friendly_team] == exp_atks
