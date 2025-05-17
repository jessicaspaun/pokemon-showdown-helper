"""
Database schema setup for Pokémon Showdown Helper.

Defines and initializes the database tables for formats, format rules, and natures.
"""

import sqlite3
from pathlib import Path
from data_scripts import constants


def init_database(db_path: Path = constants.DB_PATH):
    """
    Initialize the database and create tables if they do not exist.
    Args:
        db_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Table for competitive formats (e.g., Gen 7 OU)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Formats (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')

    # Table for format rules (banlists, clauses, etc.)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS FormatRules (
            format_id TEXT NOT NULL,
            rule_type TEXT NOT NULL,  -- e.g., 'banlist', 'ruleset'
            rule TEXT NOT NULL,
            PRIMARY KEY (format_id, rule_type, rule),
            FOREIGN KEY(format_id) REFERENCES Formats(id)
        )
    ''')

    # Table for natures
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Natures (
            name TEXT PRIMARY KEY,
            increased_stat TEXT,
            decreased_stat TEXT
        )
    ''')

    # Table for Pokemon
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Pokemon (
            id TEXT PRIMARY KEY,
            name TEXT,
            num INTEGER,
            types TEXT,
            base_stats TEXT
        )
    ''')

    # Table for Moves
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

    # Table for Abilities
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Abilities (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT
        )
    ''')

    # Table for Items
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Items (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT
        )
    ''')

    # Table for PokemonLearnset
    cur.execute('''
        CREATE TABLE IF NOT EXISTS PokemonLearnset (
            pokemon_id TEXT,
            move_id TEXT,
            PRIMARY KEY (pokemon_id, move_id)
        )
    ''')

    # Table for Typechart
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Typechart (
            attacking_type TEXT,
            defending_type TEXT,
            multiplier INTEGER,
            PRIMARY KEY (attacking_type, defending_type)
        )
    ''')

    # Table for Gen7OUSets
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Gen7OUSets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pokemon_name TEXT,
            set_name TEXT,
            moves TEXT,
            ability TEXT,
            item TEXT,
            nature TEXT,
            evs TEXT,
            source TEXT
        )
    ''')

    conn.commit()
    conn.close()


def populate_natures(db_path: Path = constants.DB_PATH):
    """
    Populate the Natures table using NATURES_DATA from constants.py.
    Args:
        db_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for nature, mods in constants.NATURES_DATA.items():
        increased = None
        decreased = None
        for stat, value in mods.items():
            if value == 1.1:
                increased = stat
            elif value == 0.9:
                decreased = stat
        cur.execute('''
            INSERT OR IGNORE INTO Natures (name, increased_stat, decreased_stat)
            VALUES (?, ?, ?)
        ''', (nature, increased, decreased))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
    populate_natures()
    print("Database initialized and natures populated.") 