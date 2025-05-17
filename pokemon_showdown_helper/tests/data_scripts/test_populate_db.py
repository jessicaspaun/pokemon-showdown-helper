"""
Tests for the populate_db module insertion functions.
"""
import sqlite3
from pathlib import Path
import pytest
from data_scripts import populate_db
import sys
import types

def test_insert_pokedex_data(tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    # Create a temporary database with the Pokemon table
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Pokemon (
            id TEXT PRIMARY KEY,
            name TEXT,
            num INTEGER,
            types TEXT,
            base_stats TEXT
        )
    ''')
    conn.commit()
    conn.close()
    # Sample pokedex data
    pokedex_data = {
        "pikachu": {
            "species": "Pikachu",
            "num": 25,
            "types": ["Electric"],
            "baseStats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90}
        }
    }
    populate_db.insert_pokedex_data(pokedex_data, db_path)
    # Verify insertion
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Pokemon WHERE id = 'pikachu'")
    row = cur.fetchone()
    assert row is not None
    assert row[1] == "Pikachu"
    conn.close()

def test_insert_moves_data(tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Moves (
            id TEXT PRIMARY KEY,
            name TEXT,
            num INTEGER,
            type TEXT,
            power INTEGER,
            accuracy INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    moves_data = {
        "thunderbolt": {
            "name": "Thunderbolt",
            "num": 85,
            "type": "Electric",
            "power": 90,
            "accuracy": 100
        }
    }
    populate_db.insert_moves_data(moves_data, db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Moves WHERE id = 'thunderbolt'")
    row = cur.fetchone()
    assert row is not None
    assert row[1] == "Thunderbolt"
    conn.close()

def test_insert_abilities_data(tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Abilities (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()
    abilities_data = {
        "static": {
            "name": "Static",
            "desc": "May paralyze on contact."
        }
    }
    populate_db.insert_abilities_data(abilities_data, db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Abilities WHERE id = 'static'")
    row = cur.fetchone()
    assert row is not None
    assert row[1] == "Static"
    conn.close()

def test_insert_items_data(tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Items (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()
    items_data = {
        "lightball": {
            "name": "Light Ball",
            "desc": "Doubles Pikachu's Attack and Sp. Atk."
        }
    }
    populate_db.insert_items_data(items_data, db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Items WHERE id = 'lightball'")
    row = cur.fetchone()
    assert row is not None
    assert row[1] == "Light Ball"
    conn.close()

def test_insert_learnsets_data(tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS PokemonLearnset (
            pokemon_id TEXT,
            move_id TEXT,
            PRIMARY KEY (pokemon_id, move_id)
        )
    ''')
    conn.commit()
    conn.close()
    learnsets_data = {
        "pikachu": {
            "learnset": ["thunderbolt", "quickattack"]
        }
    }
    populate_db.insert_learnsets_data(learnsets_data, db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT move_id FROM PokemonLearnset WHERE pokemon_id = 'pikachu'")
    moves = {row[0] for row in cur.fetchall()}
    assert moves == {"thunderbolt", "quickattack"}
    conn.close()

def test_insert_typechart_data(tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Typechart (
            attacking_type TEXT,
            defending_type TEXT,
            multiplier INTEGER,
            PRIMARY KEY (attacking_type, defending_type)
        )
    ''')
    conn.commit()
    conn.close()
    typechart_data = {
        "Electric": {
            "damageTaken": {"Ground": 2, "Flying": 0, "Steel": 1}
        }
    }
    populate_db.insert_typechart_data(typechart_data, db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT defending_type, multiplier FROM Typechart WHERE attacking_type = 'Electric'")
    results = dict(cur.fetchall())
    assert results == {"Ground": 2, "Flying": 0, "Steel": 1}
    conn.close()

def test_insert_format(tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Formats (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()
    populate_db.insert_format('gen7ou', '[Gen 7] OU', 'Smogon OU (OverUsed)', db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Formats WHERE id = 'gen7ou'")
    row = cur.fetchone()
    assert row is not None
    assert row[1] == '[Gen 7] OU'
    assert row[2] == 'Smogon OU (OverUsed)'
    conn.close()

def test_insert_format_rules(tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS FormatRules (
            format_id TEXT,
            rule_type TEXT,
            rule TEXT,
            PRIMARY KEY (format_id, rule_type, rule)
        )
    ''')
    conn.commit()
    conn.close()
    ruleset = ['Standard', 'Team Preview']
    banlist = ['Aegislash', 'Blaziken']
    populate_db.insert_format_rules('gen7ou', ruleset, banlist, db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT rule FROM FormatRules WHERE format_id = 'gen7ou' AND rule_type = 'ruleset'")
    rules = [row[0] for row in cur.fetchall()]
    assert set(rules) == set(ruleset)
    cur.execute("SELECT rule FROM FormatRules WHERE format_id = 'gen7ou' AND rule_type = 'banlist'")
    bans = [row[0] for row in cur.fetchall()]
    assert set(bans) == set(banlist)
    conn.close()

def test_insert_smogon_analysis_sets(monkeypatch, tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    # Create minimal required tables
    populate_db.create_gen7ou_sets_table(db_path)
    # Mock fetch_smogon_analysis_sets module
    mock_module = types.SimpleNamespace()
    mock_module.get_gen7ou_pokemon_list = lambda db_path: ["Pikachu"]
    mock_module.workspace_pokemon_smogon_page_html = lambda name: "<html></html>"
    mock_module.parse_smogon_page_for_sets = lambda html: [
        {
            "name": "Offensive",
            "moves": ["Thunderbolt", "Volt Switch"],
            "ability": "Static",
            "item": "Light Ball",
            "nature": "Timid",
            "evs": {"spa": 252, "spe": 252, "hp": 4}
        }
    ]
    monkeypatch.setitem(sys.modules, "data_scripts.fetch_smogon_analysis_sets", mock_module)
    # Run insertion
    populate_db.insert_smogon_analysis_sets(db_path)
    # Check DB
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT pokemon_name, set_name, moves, ability, item, nature, evs, source FROM Gen7OUSets")
    row = cur.fetchone()
    assert row is not None
    assert row[0] == "Pikachu"
    assert row[1] == "Offensive"
    assert row[2] == "Thunderbolt,Volt Switch"
    assert row[3] == "Static"
    assert row[4] == "Light Ball"
    assert row[5] == "Timid"
    assert row[6] == "{'spa': 252, 'spe': 252, 'hp': 4}"
    assert row[7] == "smogon_analysis_page"
    conn.close() 