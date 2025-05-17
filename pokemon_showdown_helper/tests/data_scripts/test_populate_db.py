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

def test_insert_usage_stats_sets(monkeypatch, tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    # Create minimal required tables
    populate_db.create_gen7ou_sets_table(db_path)
    
    # Mock fetch_usage_stats module
    mock_module = types.SimpleNamespace()
    mock_module.workspace_gen7ou_chaos_data = lambda month: {
        "data": {
            "Pikachu": {
                "Abilities": {
                    "Static": {"usage": 0.7},
                    "Lightning Rod": {"usage": 0.3}
                },
                "Items": {
                    "Light Ball": {"usage": 0.8},
                    "Choice Scarf": {"usage": 0.2}
                },
                "Moves": {
                    "Thunderbolt": {"usage": 0.9},
                    "Volt Switch": {"usage": 0.8},
                    "Hidden Power Ice": {"usage": 0.7},
                    "Grass Knot": {"usage": 0.6},
                    "Quick Attack": {"usage": 0.5}
                },
                "Spreads": {
                    "Timid:252/0/0/252/4/0": {"usage": 0.6},
                    "Jolly:0/252/0/0/4/252": {"usage": 0.4}
                }
            }
        }
    }
    mock_module.parse_chaos_data = lambda data: {
        "Pikachu": {
            "top_abilities": [("Static", {"usage": 0.7}), ("Lightning Rod", {"usage": 0.3})],
            "top_items": [("Light Ball", {"usage": 0.8}), ("Choice Scarf", {"usage": 0.2})],
            "top_moves": [
                ("Thunderbolt", {"usage": 0.9}),
                ("Volt Switch", {"usage": 0.8}),
                ("Hidden Power Ice", {"usage": 0.7}),
                ("Grass Knot", {"usage": 0.6})
            ],
            "top_spreads": [("Timid:252/0/0/252/4/0", {"usage": 0.6})]
        }
    }
    monkeypatch.setitem(sys.modules, "data_scripts.fetch_usage_stats", mock_module)
    
    # Run insertion
    populate_db.insert_usage_stats_sets(db_path, month="2022-12")
    
    # Check DB
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT pokemon_name, set_name, moves, ability, item, nature, evs, source FROM Gen7OUSets")
    row = cur.fetchone()
    assert row is not None
    assert row[0] == "Pikachu"
    assert row[1] == "Usage Stats 2022-12"
    assert row[2] == "Thunderbolt,Volt Switch,Hidden Power Ice,Grass Knot"
    assert row[3] == "Static"
    assert row[4] == "Light Ball"
    assert row[5] == "Timid"
    assert row[6] == "{'hp': 252, 'atk': 0, 'def': 0, 'spa': 252, 'spd': 4, 'spe': 0}"
    assert row[7] == "usage_stats_2022-12"
    conn.close()

def test_main_populate_integration(monkeypatch, tmp_path):
    """Integration test for main_populate to verify all data types are correctly populated."""
    db_path = tmp_path / "test_db.sqlite3"
    
    # Mock utils.download_json to prevent real HTTP requests
    def mock_download_json(url, save_path):
        if "pokedex" in url:
            return {
                "pikachu": {
                    "species": "Pikachu",
                    "num": 25,
                    "types": ["Electric"],
                    "baseStats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90}
                }
            }
        elif "moves" in url:
            return {
                "thunderbolt": {
                    "name": "Thunderbolt",
                    "num": 85,
                    "type": "Electric",
                    "power": 90,
                    "accuracy": 100
                }
            }
        elif "abilities" in url:
            return {
                "static": {
                    "name": "Static",
                    "desc": "May paralyze on contact."
                }
            }
        elif "items" in url:
            return {
                "lightball": {
                    "name": "Light Ball",
                    "desc": "Doubles Pikachu's Attack and Sp. Atk."
                }
            }
        elif "learnsets" in url:
            return {
                "pikachu": {
                    "learnset": ["thunderbolt", "quickattack"]
                }
            }
        elif "typechart" in url:
            return {
                "Electric": {
                    "damageTaken": {"Ground": 2, "Flying": 0, "Steel": 1}
                }
            }
        return {}
    
    monkeypatch.setattr("data_scripts.utils.download_json", mock_download_json)
    
    # Mock format rules fetching
    mock_fetch_ps_rules_and_formats = types.SimpleNamespace()
    mock_fetch_ps_rules_and_formats.workspace_ps_formats_ts_raw = lambda: "mock formats.ts content"
    monkeypatch.setattr(
        "data_scripts.fetch_ps_rules_and_formats.parse_gen7ou_rules_from_formats_ts",
        lambda _: {"ruleset": ["Standard", "Team Preview"], "banlist": ["Aegislash", "Blaziken"]}
    )
    monkeypatch.setitem(sys.modules, "data_scripts.fetch_ps_rules_and_formats", mock_fetch_ps_rules_and_formats)
    
    # Mock Smogon analysis sets fetching
    mock_fetch_smogon_analysis_sets = types.SimpleNamespace()
    mock_fetch_smogon_analysis_sets.get_gen7ou_pokemon_list = lambda db_path: ["Pikachu"]
    mock_fetch_smogon_analysis_sets.workspace_pokemon_smogon_page_html = lambda name: "<html></html>"
    mock_fetch_smogon_analysis_sets.parse_smogon_page_for_sets = lambda html: [
        {
            "name": "Offensive",
            "moves": ["Thunderbolt", "Volt Switch"],
            "ability": "Static",
            "item": "Light Ball",
            "nature": "Timid",
            "evs": {"spa": 252, "spe": 252, "hp": 4}
        }
    ]
    monkeypatch.setitem(sys.modules, "data_scripts.fetch_smogon_analysis_sets", mock_fetch_smogon_analysis_sets)
    
    # Mock usage stats fetching
    mock_fetch_usage_stats = types.SimpleNamespace()
    mock_fetch_usage_stats.workspace_gen7ou_chaos_data = lambda month: {
        "data": {
            "Pikachu": {
                "Abilities": {"Static": {"usage": 0.7}},
                "Items": {"Light Ball": {"usage": 0.8}},
                "Moves": {
                    "Thunderbolt": {"usage": 0.9},
                    "Volt Switch": {"usage": 0.8},
                    "Hidden Power Ice": {"usage": 0.7},
                    "Grass Knot": {"usage": 0.6}
                },
                "Spreads": {"Timid:252/0/0/252/4/0": {"usage": 0.6}}
            }
        }
    }
    mock_fetch_usage_stats.parse_chaos_data = lambda data: {
        "Pikachu": {
            "top_abilities": [("Static", {"usage": 0.7})],
            "top_items": [("Light Ball", {"usage": 0.8})],
            "top_moves": [
                ("Thunderbolt", {"usage": 0.9}),
                ("Volt Switch", {"usage": 0.8}),
                ("Hidden Power Ice", {"usage": 0.7}),
                ("Grass Knot", {"usage": 0.6})
            ],
            "top_spreads": [("Timid:252/0/0/252/4/0", {"usage": 0.6})]
        }
    }
    monkeypatch.setitem(sys.modules, "data_scripts.fetch_usage_stats", mock_fetch_usage_stats)
    
    # Run main_populate
    populate_db.main_populate(db_path)
    
    # Verify all data types are populated
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check Pokemon
    cur.execute("SELECT * FROM Pokemon WHERE id = 'pikachu'")
    assert cur.fetchone() is not None
    
    # Check Moves
    cur.execute("SELECT * FROM Moves WHERE id = 'thunderbolt'")
    assert cur.fetchone() is not None
    
    # Check Abilities
    cur.execute("SELECT * FROM Abilities WHERE id = 'static'")
    assert cur.fetchone() is not None
    
    # Check Items
    cur.execute("SELECT * FROM Items WHERE id = 'lightball'")
    assert cur.fetchone() is not None
    
    # Check Learnset
    cur.execute("SELECT * FROM PokemonLearnset WHERE pokemon_id = 'pikachu'")
    assert len(cur.fetchall()) == 2
    
    # Check Typechart
    cur.execute("SELECT * FROM Typechart WHERE attacking_type = 'Electric'")
    assert len(cur.fetchall()) == 3
    
    # Check Format Rules
    cur.execute("SELECT rule_type, rule FROM FormatRules WHERE format_id = 'gen7ou'")
    rules = set(cur.fetchall())
    # The expected rules from the mock
    expected_rules = {('ruleset', 'Standard'), ('ruleset', 'Team Preview'), ('banlist', 'Aegislash'), ('banlist', 'Blaziken')}
    assert expected_rules.issubset(rules)
    
    # Check Gen7OUSets (should have both analysis and usage stats sets)
    cur.execute("SELECT source FROM Gen7OUSets WHERE pokemon_name = 'Pikachu'")
    sources = {row[0] for row in cur.fetchall()}
    assert sources == {'smogon_analysis_page', 'usage_stats_2022-12'}
    
    conn.close() 