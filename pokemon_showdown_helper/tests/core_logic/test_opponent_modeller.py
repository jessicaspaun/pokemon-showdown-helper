"""
Unit tests for the OpponentModeller class.
"""
import sqlite3
import tempfile
import os
from core_logic.opponent_modeller import OpponentModeller
from core_logic.pokemon_object import PokemonInstance
import pytest

def setup_temp_db():
    db_fd, db_path = tempfile.mkstemp()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE Gen7OUSets (
            species TEXT,
            moves TEXT,
            ability TEXT,
            item TEXT,
            nature TEXT,
            ev TEXT,
            iv TEXT,
            types TEXT,
            source TEXT,
            usage REAL
        )
    """)
    # Insert usage_stats and smogon_analysis_page sets
    cur.execute("""
        INSERT INTO Gen7OUSets (species, moves, ability, item, nature, ev, iv, types, source, usage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("Pikachu", '["Thunderbolt","Volt Tackle"]', "Static", "Light Ball", "Jolly", '{"atk":252,"spe":252}', '{"hp":31}', '["electric"]', "usage_stats_2021-01", 0.25))
    cur.execute("""
        INSERT INTO Gen7OUSets (species, moves, ability, item, nature, ev, iv, types, source, usage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("Pikachu", '["Thunderbolt"]', "Static", "Light Ball", "Timid", '{"spa":252,"spe":252}', '{"hp":31}', '["electric"]', "smogon_analysis_page", 0.0))
    conn.commit()
    conn.close()
    return db_fd, db_path

def teardown_temp_db(db_fd, db_path):
    os.close(db_fd)
    os.remove(db_path)

def test_predict_set_usage_stats():
    db_fd, db_path = setup_temp_db()
    modeller = OpponentModeller(db_path)
    poke = modeller.predict_set("Pikachu")
    assert isinstance(poke, PokemonInstance)
    assert poke.nature == "Jolly"
    assert "Volt Tackle" in poke.moves or "Thunderbolt" in poke.moves
    modeller.close()
    teardown_temp_db(db_fd, db_path)

def test_predict_set_fallback_smogon():
    db_fd, db_path = setup_temp_db()
    # Remove usage_stats row
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM Gen7OUSets WHERE source LIKE 'usage_stats%'")
    conn.commit()
    conn.close()
    modeller = OpponentModeller(db_path)
    poke = modeller.predict_set("Pikachu")
    assert isinstance(poke, PokemonInstance)
    assert poke.nature == "Timid"
    modeller.close()
    teardown_temp_db(db_fd, db_path)

def test_predict_set_none():
    db_fd, db_path = setup_temp_db()
    modeller = OpponentModeller(db_path)
    poke = modeller.predict_set("Bulbasaur")
    assert poke is None
    modeller.close()
    teardown_temp_db(db_fd, db_path)

@pytest.fixture
def modeller():
    return OpponentModeller()

def test_predict_opponent_team_with_usage_stats(modeller):
    """Test predicting opponent team using usage statistics."""
    # Test with a common OU Pokémon that should have usage stats
    team = modeller.predict_opponent_team(["Landorus-Therian"])
    assert len(team) == 1
    assert isinstance(team[0], PokemonInstance)
    assert team[0].species == "Landorus-Therian"
    assert team[0].level == 100
    assert team[0].types == ["Ground", "Flying"]
    assert len(team[0].moves) > 0
    assert team[0].ability is not None
    assert team[0].item is not None

def test_predict_opponent_team_with_analysis_sets(modeller):
    """Test predicting opponent team using analysis sets when usage stats aren't available."""
    # Test with a less common Pokémon that might only have analysis sets
    team = modeller.predict_opponent_team(["Mantine"])
    assert len(team) == 1
    assert isinstance(team[0], PokemonInstance)
    assert team[0].species == "Mantine"
    assert team[0].level == 100
    assert team[0].types == ["Water", "Flying"]
    assert len(team[0].moves) > 0
    assert team[0].ability is not None
    assert team[0].item is not None

def test_predict_opponent_team_with_default_values(modeller):
    """Test predicting opponent team for a Pokémon with no known sets."""
    # Test with a Pokémon that might not have any sets in the database
    team = modeller.predict_opponent_team(["Pikachu"])
    assert len(team) == 1
    assert isinstance(team[0], PokemonInstance)
    assert team[0].species == "Pikachu"
    assert team[0].level == 100
    assert team[0].types == ["Electric"]
    assert team[0].nature == "Serious"
    assert all(iv == 31 for iv in team[0].iv.values())
    assert all(ev == 0 for ev in team[0].ev.values())

def test_predict_opponent_team_multiple_pokemon(modeller):
    """Test predicting opponent team with multiple Pokémon."""
    team = modeller.predict_opponent_team([
        "Landorus-Therian",
        "Mantine",
        "Pikachu"
    ])
    assert len(team) == 3
    assert all(isinstance(pokemon, PokemonInstance) for pokemon in team)
    assert team[0].species == "Landorus-Therian"
    assert team[1].species == "Mantine"
    assert team[2].species == "Pikachu"

def test_parse_ivs(modeller):
    """Test parsing IV strings."""
    iv_string = "hp:31/atk:31/def:31/spa:31/spd:31/spe:31"
    ivs = modeller._parse_ivs(iv_string)
    assert ivs == {
        'hp': 31,
        'atk': 31,
        'def': 31,
        'spa': 31,
        'spd': 31,
        'spe': 31
    }

def test_parse_evs(modeller):
    """Test parsing EV strings."""
    ev_string = "hp:252/atk:0/def:0/spa:252/spd:0/spe:4"
    evs = modeller._parse_evs(ev_string)
    assert evs == {
        'hp': 252,
        'atk': 0,
        'def': 0,
        'spa': 252,
        'spd': 0,
        'spe': 4
    }

def test_get_types(modeller):
    """Test getting Pokémon types."""
    # Test single type
    types = modeller._get_types("Pikachu")
    assert types == ["Electric"]
    
    # Test dual type
    types = modeller._get_types("Landorus-Therian")
    assert types == ["Ground", "Flying"] 