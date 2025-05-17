"""
Unit tests for the Team class.
"""
import pytest
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team

def make_pokemon(name, **kwargs):
    return PokemonInstance(species=name, **kwargs)

def test_add_and_remove_pokemon():
    team = Team()
    pikachu = make_pokemon("Pikachu")
    bulbasaur = make_pokemon("Bulbasaur")
    assert team.add_pokemon(pikachu) is True
    assert team.add_pokemon(bulbasaur) is True
    assert team.get_team_size() == 2
    assert team.remove_pokemon("Pikachu") is True
    assert team.get_team_size() == 1
    assert team.remove_pokemon("Charmander") is False

def test_no_duplicates_and_max_size():
    team = Team()
    for i in range(Team.MAX_TEAM_SIZE):
        assert team.add_pokemon(make_pokemon(f"Poke{i}")) is True
    assert team.get_team_size() == Team.MAX_TEAM_SIZE
    # Can't add duplicate species
    assert team.add_pokemon(make_pokemon("Poke0")) is False
    # Can't add more than 6
    assert team.add_pokemon(make_pokemon("Extra")) is False

def test_is_valid():
    team = Team()
    assert not team.is_valid()  # Empty team
    team.add_pokemon(make_pokemon("A"))
    assert team.is_valid()  # 1 member
    for i in range(1, Team.MAX_TEAM_SIZE):
        team.add_pokemon(make_pokemon(f"B{i}"))
    assert team.is_valid()  # 6 unique
    team.add_pokemon(make_pokemon("A"))  # Should not add duplicate
    assert team.is_valid()  # Still valid
    # Remove one, should still be valid
    team.remove_pokemon("B1")
    assert team.is_valid()

def test_export_showdown():
    team = Team()
    pika = make_pokemon(
        "Pikachu",
        level=50,
        base_stats={"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        ev={"hp": 0, "atk": 252, "def": 0, "spa": 0, "spd": 4, "spe": 252},
        nature="timid",
        ability="Static",
        item="Light Ball",
        moves=["Thunderbolt", "Volt Tackle"]
    )
    team.add_pokemon(pika)
    output = team.export_showdown()
    assert "Pikachu @ Light Ball" in output
    assert "Ability: Static" in output
    assert "Level: 50" in output
    assert "EVs: 252 ATK / 4 SPD / 252 SPE" in output
    assert "Timid Nature" in output
    assert "- Thunderbolt" in output
    assert "- Volt Tackle" in output 