"""
Unit tests for the PokemonInstance class.
"""
import pytest
from core_logic.pokemon_object import PokemonInstance

def test_calculate_stats():
    """Test stat calculation for a standard Pokémon."""
    pikachu = PokemonInstance(
        species="Pikachu",
        base_stats={"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
        ev={"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        nature="serious"
    )
    stats = pikachu.calculate_stats()
    # HP: ((2*35 + 31 + 0) * 100) // 100 + 100 + 10 = 211
    assert stats["hp"] == 211
    # Other stats: int((((2*base + iv + (ev//4)) * level) // 100 + 5) * nature_mod)
    # For serious nature, nature_mod = 1.0
    # atk: int((((2*55 + 31 + 0) * 100) // 100 + 5) * 1.0) = int((141 + 5) * 1.0) = 146
    assert stats["atk"] == 146
    assert stats["def"] == 116  # ((2*40+31)*100)//100+5 = 111+5=116
    assert stats["spa"] == 136  # ((2*50+31)*100)//100+5 = 131+5=136
    assert stats["spd"] == 136  # ((2*50+31)*100)//100+5 = 131+5=136
    assert stats["spe"] == 216  # ((2*90+31)*100)//100+5 = 211+5=216

def test_nature_modifier():
    """Test that nature modifiers are applied correctly."""
    pikachu = PokemonInstance(
        species="Pikachu",
        base_stats={"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        nature="timid"  # Increases Speed, decreases Attack
    )
    stats = pikachu.calculate_stats()
    assert stats["spe"] > stats["atk"]  # Speed should be higher than Attack due to nature

def test_from_db_row():
    """Test the from_db_row factory method."""
    db_row = {
        "name": "Pikachu",
        "hp": 35,
        "atk": 55,
        "def": 40,
        "spa": 50,
        "spd": 50,
        "spe": 90
    }
    pikachu = PokemonInstance.from_db_row(db_row)
    assert pikachu.species == "Pikachu"
    assert pikachu.base_stats["hp"] == 35
    assert pikachu.base_stats["atk"] == 55
    assert pikachu.base_stats["def"] == 40
    assert pikachu.base_stats["spa"] == 50
    assert pikachu.base_stats["spd"] == 50
    assert pikachu.base_stats["spe"] == 90 