from unittest.mock import Mock

import pytest

from superautosim.actions import Action, ActionType, AddStatsAction, TargetedAction
from superautosim.targets import TargetGenerator
from superautosim.teams import Team


@pytest.fixture
def friendly_targen(friendly_team):
    return get_mock_target_generator(friendly_team)


def get_mock_target_generator(pets) -> TargetGenerator:
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
def test_add_stats_action(
    friendly_team: Team, friendly_targen, is_temp, added_stats, expected_stats
):
    addstats_action = AddStatsAction(
        friendly_targen,
        max_targets=5,
        attack=added_stats[0],
        health=added_stats[1],
        temp_stats=is_temp,
    )

    addstats_action.run(1, None, 0)
    assert len(list(friendly_team)) == len(expected_stats)
    for p, stats in zip(friendly_team.pets, expected_stats):
        assert p.stats == stats


@pytest.mark.parametrize(
    ["level", "added_stats", "expected_stats"],
    [
        (2, (1, 1), [(i + 2, i + 2) for i in range(1, 6)]),
        (3, (1, -1), [(4, 1), (5, 1), (6, 1), (7, 1), (8, 2)]),
        (3, (-1, 1), [(1, 4), (1, 5), (1, 6), (1, 7), (2, 8)]),
    ],
)
def test_add_stats_action_level_multiply(
    friendly_team: Team, friendly_targen, level, added_stats, expected_stats
):
    addstats_action = AddStatsAction(
        friendly_targen,
        max_targets=5,
        attack=added_stats[0],
        health=added_stats[1],
        level_multiply=True,
    )

    addstats_action.run(level, None, 0)
    assert len(list(friendly_team)) == len(expected_stats)
    for p, stats in zip(friendly_team.pets, expected_stats):
        assert p.stats[:2] == stats


def test_add_stats_action_max_targets(friendly_team, friendly_targen):

    values = [(1, [2, 2, 3, 4, 5]), (4, [3, 3, 4, 5, 5]), (9, [4, 4, 5, 6, 6])]
    for num_targets, exp_atks in values:
        addstats_action = AddStatsAction(
            friendly_targen, max_targets=num_targets, attack=1
        )

        addstats_action.run(1, None, 0)
        assert [p.attack for p in friendly_team] == exp_atks
