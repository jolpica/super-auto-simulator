import pytest

from superautosim.pets import Pet


@pytest.mark.parametrize(
    ["pet", "attack", "health", "temp_stats", "exp_stats"],
    [
        (Pet(stats=(1, 1)), 0, 0, False, (1, 1)),
        (Pet(stats=(1, 1)), 1, 1, False, (2, 2)),
        (Pet(stats=(1, 1)), 1, 1, True, (2, 2)),
        (Pet(stats=(1, 1)), 9, 1, True, (10, 2)),
        (Pet(stats=(1, 1)), 1, 9, False, (2, 10)),
        (Pet(stats=(5, 7)), 9, 0, True, (14, 7)),
        (Pet(stats=(5, 7)), 0, 9, False, (5, 16)),
        (Pet(stats=(10, 10)), -5, -9, False, (5, 1)),
        (Pet(stats=(10, 10)), -9, -5, True, (1, 5)),
    ],
)
def test_pet_add_stats(pet: Pet, attack: int, health: int, temp_stats: bool, exp_stats):
    """Adding / removing stats within max/mins"""
    base_atk, base_hea = pet._perm_attack, pet._perm_health
    base_tatk, base_thea = pet._temp_attack, pet._temp_health
    pet.add_stats(attack, health, temp_stats)
    # Stats increase as expected
    assert (pet.attack, pet.health) == exp_stats
    assert pet.attack == base_atk + base_tatk + attack
    assert pet.health == base_hea + base_thea + health
    # Perm / temp stats only changed when supposed to
    if temp_stats:
        assert (base_atk, base_hea) == (pet._perm_attack, pet._perm_health)
        assert (pet._temp_attack, pet._temp_health) == (
            attack + base_tatk,
            health + base_thea,
        )
    else:
        assert (base_tatk, base_thea) == (pet._temp_attack, pet._temp_health)
        assert (pet._perm_attack, pet._perm_health) == (
            attack + base_atk,
            health + base_hea,
        )


@pytest.mark.parametrize(
    ["pet", "is_temp", "stats"],
    [
        (Pet(stats=(1, 1)), False, (-1, -1)),
        (Pet(stats=(1, 1)), True, (-1, -1)),
        (Pet(stats=(5, 4)), False, (-20, -9)),
        (Pet(stats=(5, 4)), True, (-20, -9)),
        (Pet(stats=(10, 10, -9, -9)), False, (-3, -3)),
        (Pet(stats=(10, 10, -9, -9)), True, (-3, -3)),
    ],
)
def test_pet_add_stats_min(pet, is_temp, stats):
    """pet total stats never go below 1"""
    pet.add_stats(*stats, is_temp)
    assert pet.attack == 1 and pet.health == 1
    # Permanent stats always above 1
    assert pet._perm_attack >= 1 and pet._perm_health >= 1


@pytest.mark.parametrize(
    ["pet", "is_temp"],
    [
        (Pet(stats=(3, 3)), False),
        (Pet(stats=(3, 3)), True),
        (Pet(stats=(15, 27)), False),
        (Pet(stats=(15, 27)), True),
    ],
)
def test_pet_add_stats_temp_min_with_add(pet, is_temp):
    """add stats after reducing to minimum stats"""
    is_temp = False
    pet = Pet(stats=(3, 3))
    pet.add_stats(-50, -50, is_temp)
    pet.add_stats(1, 3)
    assert pet.attack == 2 and pet.health == 4


@pytest.mark.parametrize(
    ["pet", "is_temp", "stats"],
    [
        (Pet(stats=(1, 1)), False, (50, 50)),
        (Pet(stats=(1, 1)), True, (50, 50)),
        (Pet(stats=(1, 1, 10, 10)), False, (50, 50)),
        (Pet(stats=(1, 1, 10, 10)), True, (50, 50)),
    ],
)
def test_pet_add_stats_max(pet, is_temp, stats):
    """attack/health both stay below STAT_CAP"""
    pet.add_stats(*stats, is_temp)
    assert pet.attack == Pet.STAT_CAP and pet.health == Pet.STAT_CAP


@pytest.mark.parametrize(
    ["pet", "stats", "is_temp", "exp_stats"],
    [
        (Pet(stats=(25, 25, 25, 25)), (10, 12), False, (35, 37, 15, 13)),
        (Pet(stats=(25, 25, 25, 25)), (10, 12), True, (25, 25, 25, 25)),
        (Pet(stats=(25, 10, 15, 10)), (20, 20), False, (45, 30, 5, 10)),
        (Pet(stats=(10, 10, 40, 40)), (20, 00), False, (30, 10, 20, 40)),
    ],
)
def test_pet_add_stats_max_temp_to_perm(pet, stats, is_temp, exp_stats):
    """Adding perm stats should override temp stats when the stat is at STAT_CAP"""
    pet.add_stats(*stats, is_temp)
    assert pet.attack <= Pet.STAT_CAP and pet.health <= Pet.STAT_CAP

    assert pet._perm_attack == exp_stats[0] and pet._perm_health == exp_stats[1]
    assert pet._temp_attack == exp_stats[2] and pet._temp_health == exp_stats[3]
