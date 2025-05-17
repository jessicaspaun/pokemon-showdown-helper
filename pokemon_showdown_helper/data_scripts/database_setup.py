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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')

    # Table for format rules (banlists, clauses, etc.)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS FormatRules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            format_id INTEGER NOT NULL,
            rule_type TEXT NOT NULL,  -- e.g., 'ban', 'clause', 'restriction'
            rule_text TEXT NOT NULL,
            FOREIGN KEY(format_id) REFERENCES Formats(id)
        )
    ''')

    # Table for natures
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Natures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            increased_stat TEXT,
            decreased_stat TEXT
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