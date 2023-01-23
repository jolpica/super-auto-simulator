import pytest

from sapai.rewrite.pets import Pet
from sapai.rewrite.teams import Team


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
