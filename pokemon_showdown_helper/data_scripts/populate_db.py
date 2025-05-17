"""
Populate the database with core Pokémon Showdown data.
"""
from pathlib import Path
from data_scripts import database_setup, fetch_ps_core_data, constants
import sqlite3

def main_populate(db_path: Path = constants.DB_PATH):
    """
    Orchestrator function to initialize the database and populate it with core data.
    Args:
        db_path: Path to the SQLite database file.
    """
    # Initialize the database schema
    database_setup.init_database(db_path)
    # Populate natures
    database_setup.populate_natures(db_path)
    # Fetch and parse core data
    pokedex_data = fetch_ps_core_data.fetch_pokedex_json()
    moves_data = fetch_ps_core_data.fetch_moves_json()
    abilities_data = fetch_ps_core_data.fetch_abilities_json()
    items_data = fetch_ps_core_data.fetch_items_json()
    learnsets_data = fetch_ps_core_data.fetch_learnsets_json()
    typechart_data = fetch_ps_core_data.fetch_typechart_json()
    # Insert parsed data into the database
    insert_pokedex_data(pokedex_data, db_path)
    insert_moves_data(moves_data, db_path)
    insert_abilities_data(abilities_data, db_path)
    insert_items_data(items_data, db_path)
    insert_learnsets_data(learnsets_data, db_path)
    insert_typechart_data(typechart_data, db_path)

def insert_pokedex_data(pokedex_data, db_path):
    """
    Insert parsed pokedex data into the Pokemon table.
    Args:
        pokedex_data: Parsed pokedex JSON data.
        db_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for pokemon_id, data in pokedex_data.items():
        cur.execute('''
            INSERT OR REPLACE INTO Pokemon (id, name, num, types, base_stats)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            pokemon_id,
            data.get('species', ''),
            data.get('num', 0),
            ','.join(data.get('types', [])),
            ','.join(str(data.get('baseStats', {}).get(stat, 0)) for stat in ['hp', 'atk', 'def', 'spa', 'spd', 'spe'])
        ))
    conn.commit()
    conn.close()

def insert_moves_data(moves_data, db_path):
    """
    Insert parsed moves data into the Moves table.
    Args:
        moves_data: Parsed moves JSON data.
        db_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for move_id, data in moves_data.items():
        cur.execute('''
            INSERT OR REPLACE INTO Moves (id, name, num, type, power, accuracy)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            move_id,
            data.get('name', ''),
            data.get('num', 0),
            data.get('type', ''),
            data.get('power', 0),
            data.get('accuracy', 0)
        ))
    conn.commit()
    conn.close()

def insert_abilities_data(abilities_data, db_path):
    """
    Insert parsed abilities data into the Abilities table.
    Args:
        abilities_data: Parsed abilities JSON data.
        db_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for ability_id, data in abilities_data.items():
        cur.execute('''
            INSERT OR REPLACE INTO Abilities (id, name, description)
            VALUES (?, ?, ?)
        ''', (
            ability_id,
            data.get('name', ''),
            data.get('desc', '')
        ))
    conn.commit()
    conn.close()

def insert_items_data(items_data, db_path):
    """
    Insert parsed items data into the Items table.
    Args:
        items_data: Parsed items JSON data.
        db_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for item_id, data in items_data.items():
        cur.execute('''
            INSERT OR REPLACE INTO Items (id, name, description)
            VALUES (?, ?, ?)
        ''', (
            item_id,
            data.get('name', ''),
            data.get('desc', '')
        ))
    conn.commit()
    conn.close()

def insert_learnsets_data(learnsets_data, db_path):
    """
    Insert parsed learnsets data into the PokemonLearnset table.
    Args:
        learnsets_data: Parsed learnsets JSON data.
        db_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for pokemon_id, data in learnsets_data.items():
        learnset = data.get('learnset', [])
        for move in learnset:
            cur.execute('''
                INSERT OR REPLACE INTO PokemonLearnset (pokemon_id, move_id)
                VALUES (?, ?)
            ''', (pokemon_id, move))
    conn.commit()
    conn.close()

def insert_typechart_data(typechart_data, db_path):
    """
    Insert parsed typechart data into the Typechart table.
    Args:
        typechart_data: Parsed typechart JSON data.
        db_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for type_name, data in typechart_data.items():
        damage_taken = data.get('damageTaken', {})
        for target_type, multiplier in damage_taken.items():
            cur.execute('''
                INSERT OR REPLACE INTO Typechart (attacking_type, defending_type, multiplier)
                VALUES (?, ?, ?)
            ''', (type_name, target_type, multiplier))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main_populate()
    print("Database populated with core data.") 