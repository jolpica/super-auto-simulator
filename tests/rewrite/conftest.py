import pytest

from sapai.rewrite.pets import Pet
from sapai.rewrite.teams import Team


@pytest.fixture
def friendly_team():
    return Team(
        [
            Pet("friend1", (1, 1)),
            Pet("friend2", (2, 2)),
            Pet("friend3", (3, 3)),
            Pet("friend4", (4, 4)),
            Pet("friend5", (5, 5)),
        ]
    )


@pytest.fixture
def enemy_team():
    return Team(
        [
            Pet("enemy1", (1, 1)),
            Pet("enemy2", (2, 2)),
            Pet("enemy3", (3, 3)),
            Pet("enemy4", (4, 4)),
            Pet("enemy5", (5, 5)),
        ]
    )
