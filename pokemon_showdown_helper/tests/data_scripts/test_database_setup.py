"""
Tests for the database_setup module.
"""
import sqlite3
from pathlib import Path
import os
import pytest
from data_scripts import database_setup, constants

def test_init_database_and_tables(tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    database_setup.init_database(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Check tables exist
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert "Formats" in tables
    assert "FormatRules" in tables
    assert "Natures" in tables
    conn.close()

def test_populate_natures(tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    database_setup.init_database(db_path)
    database_setup.populate_natures(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name, increased_stat, decreased_stat FROM Natures")
    natures = {row[0]: (row[1], row[2]) for row in cur.fetchall()}
    # Check that all natures from constants are present
    for nature, mods in constants.NATURES_DATA.items():
        assert nature in natures
        inc = dec = None
        for stat, value in mods.items():
            if value == 1.1:
                inc = stat
            elif value == 0.9:
                dec = stat
        assert natures[nature] == (inc, dec)
    conn.close() 