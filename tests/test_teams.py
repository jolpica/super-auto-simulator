import pytest

from superautosim.pets import Pet
from superautosim.teams import Team


@pytest.mark.parametrize(
    "team",
    [
        Team(),
        Team(pets=[Pet()]),
        Team(pets=[Pet(), Pet(), Pet(), Pet(), Pet()]),
        Team(pets=[Pet(), None, Pet(), None, Pet()]),
        Team(pets=[None, None]),
    ],
)
def test_team_iteration(team: Team):
    count = 0
    for pet in team:
        assert pet is None or isinstance(pet, Pet)
        count += 1
    assert count == 5


@pytest.mark.parametrize(
    ["pets", "error"],
    [
        ([None] * 6, ValueError),
        ([Pet()] * 6, ValueError),
    ],
)
def test_team_init_validation(pets, error):
    with pytest.raises(error):
        Team(pets=pets)


@pytest.mark.parametrize(
    ["slots", "index", "expected"],
    [
        ((1, 2, None, 3, 4), 4, [1, 2, 3, 4, 100]),
        ((1, 2, 3, 4, None), 3, [1, 2, 3, 100, 4]),
        ((1, 2, None, 3, 4), 2, [1, 2, 100, 3, 4]),
        ((None, 1, 2, 3, 4), 1, [1, 100, 2, 3, 4]),
        ((1, 2, None, 3, 4), 0, [100, 1, 2, 3, 4]),
        ((None, 1, 2, 3, 4), 0, [100, 1, 2, 3, 4]),
        ((None, 1, 2, 3, 4), 4, [1, 2, 3, 4, 100]),
        ((1, None, 2, 3, None), 2, [1, None, 100, 2, 3]),
        ((1, 2, 3, None, None), 2, [1, 2, 100, 3, None]),
        ((None, None, None, None, None), 2, [None, None, 100, None, None]),
        ((None, None, 1, None, None), 1, [None, 100, 1, None, None]),
        ((None, 1, None, 1, None), 1, [None, 100, 1, 1, None]),
        ((None, 1, None, 2, 3), 3, [None, 1, 2, 100, 3]),
    ],
)
def test_team_insert_pet(slots, index, expected):
    team = Team(slots)
    assert team.insert_pet(100, index)
    assert team._slots == expected


def test_validate_index(friendly_team: Team):
    with pytest.raises(IndexError):
        friendly_team._validate_index(-1)
    with pytest.raises(IndexError):
        friendly_team._validate_index(friendly_team.MAX_TEAM_SIZE)
    for i in range(friendly_team.MAX_TEAM_SIZE):
        friendly_team._validate_index(i)
