"""
Tests for the populate_db module insertion functions.
"""
import sqlite3
from pathlib import Path
import pytest
from data_scripts import populate_db

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