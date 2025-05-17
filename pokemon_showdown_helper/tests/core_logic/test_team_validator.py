"""
Unit tests for the TeamValidator class.
"""
import sqlite3
import tempfile
import os
import pytest
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team
from core_logic.team_validator import TeamValidator

def make_pokemon(name, **kwargs):
    return PokemonInstance(species=name, **kwargs)

def setup_temp_db():
    db_fd, db_path = tempfile.mkstemp()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE FormatRules (
            id INTEGER PRIMARY KEY,
            format_id TEXT,
            rule_type TEXT,
            rule TEXT
        )
    """)
    # Insert bans for testing
    bans = [
        ("gen7ou", "ban", "Ubermon"),
        ("gen7ou", "ban", "Ability: Arena Trap"),
        ("gen7ou", "ban", "Item: Soul Dew"),
        ("gen7ou", "ban", "Move: Baton Pass")
    ]
    cur.executemany("INSERT INTO FormatRules (format_id, rule_type, rule) VALUES (?, ?, ?)", bans)
    conn.commit()
    conn.close()
    return db_fd, db_path

def teardown_temp_db(db_fd, db_path):
    os.close(db_fd)
    os.remove(db_path)

def test_team_validator_basic():
    db_fd, db_path = setup_temp_db()
    validator = TeamValidator(db_path)
    # Team with 6 unique, legal Pokémon
    team = Team([make_pokemon(f"Poke{i}") for i in range(6)])
    assert validator.validate(team) == []
    # Team with <6 Pokémon
    team = Team([make_pokemon(f"Poke{i}") for i in range(5)])
    errors = validator.validate(team)
    assert "Team must have exactly 6 Pokémon." in errors
    # Team with duplicate species
    team = Team([make_pokemon("A"), make_pokemon("A")] + [make_pokemon(f"B{i}") for i in range(4)])
    errors = validator.validate(team)
    assert "Duplicate Pokémon species are not allowed." in errors
    validator.close()
    teardown_temp_db(db_fd, db_path)

def test_team_validator_bans():
    db_fd, db_path = setup_temp_db()
    validator = TeamValidator(db_path)
    # Team with banned Pokémon
    team = Team([make_pokemon("Ubermon")] + [make_pokemon(f"Poke{i}") for i in range(5)])
    errors = validator.validate(team)
    assert any("Ubermon is banned" in e for e in errors)
    # Team with banned ability
    team = Team([make_pokemon("A", ability="Arena Trap")] + [make_pokemon(f"Poke{i}") for i in range(5)])
    errors = validator.validate(team)
    print("Ability errors:", errors)
    assert any("Ability Arena Trap is banned" in e for e in errors)
    # Team with banned item
    team = Team([make_pokemon("A", item="Soul Dew")] + [make_pokemon(f"Poke{i}") for i in range(5)])
    errors = validator.validate(team)
    assert any("Item Soul Dew is banned" in e for e in errors)
    # Team with banned move
    team = Team([make_pokemon("A", moves=["Baton Pass"])] + [make_pokemon(f"Poke{i}") for i in range(5)])
    errors = validator.validate(team)
    assert any("Move Baton Pass is banned" in e for e in errors)
    validator.close()
    teardown_temp_db(db_fd, db_path) 