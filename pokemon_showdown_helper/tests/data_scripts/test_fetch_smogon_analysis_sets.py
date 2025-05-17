"""
Tests for the fetch_smogon_analysis_sets module.
"""
import sqlite3
from pathlib import Path
import pytest
from data_scripts import fetch_smogon_analysis_sets

def test_get_gen7ou_pokemon_list(tmp_path):
    db_path = tmp_path / "test_db.sqlite3"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create necessary tables
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Pokemon (
            id TEXT PRIMARY KEY,
            name TEXT,
            num INTEGER,
            types TEXT,
            base_stats TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS FormatRules (
            format_id TEXT,
            rule_type TEXT,
            rule TEXT,
            PRIMARY KEY (format_id, rule_type, rule)
        )
    ''')
    
    # Insert test data
    cur.execute("INSERT INTO Pokemon (id, name) VALUES ('pikachu', 'Pikachu')")
    cur.execute("INSERT INTO Pokemon (id, name) VALUES ('charizard', 'Charizard')")
    cur.execute("INSERT INTO FormatRules (format_id, rule_type, rule) VALUES ('gen7ou', 'banlist', 'Charizard')")
    
    conn.commit()
    conn.close()
    
    # Test the function
    pokemon_list = fetch_smogon_analysis_sets.get_gen7ou_pokemon_list(db_path)
    assert len(pokemon_list) == 1
    assert pokemon_list[0] == 'Pikachu'

def test_parse_smogon_page_for_sets():
    # Sample HTML content from a Smogon analysis page
    html_content = """
    <div class="Set">
        <h3 class="Set-name">Offensive</h3>
        <div class="Move">
            <a class="Move-name">Thunderbolt</a>
        </div>
        <div class="Move">
            <a class="Move-name">Volt Switch</a>
        </div>
        <div class="Ability">
            <a class="Ability-name">Static</a>
        </div>
        <div class="Item">
            <a class="Item-name">Choice Specs</a>
        </div>
        <div class="Nature">
            <span class="Nature-name">Timid</span>
        </div>
        <div class="EVs">252 SpA / 252 Spe / 4 HP</div>
    </div>
    """
    
    sets = fetch_smogon_analysis_sets.parse_smogon_page_for_sets(html_content)
    assert len(sets) == 1
    
    set_data = sets[0]
    assert set_data['name'] == 'Offensive'
    assert set_data['moves'] == ['Thunderbolt', 'Volt Switch']
    assert set_data['ability'] == 'Static'
    assert set_data['item'] == 'Choice Specs'
    assert set_data['nature'] == 'Timid'
    assert set_data['evs'] == {'spa': 252, 'spe': 252, 'hp': 4}

def test_parse_smogon_page_for_sets_empty():
    # Test with empty HTML content
    sets = fetch_smogon_analysis_sets.parse_smogon_page_for_sets("")
    assert len(sets) == 0

def test_parse_smogon_page_for_sets_invalid_evs():
    # Test with invalid EV format
    html_content = """
    <div class="Set">
        <div class="EVs">Invalid EV format</div>
    </div>
    """
    sets = fetch_smogon_analysis_sets.parse_smogon_page_for_sets(html_content)
    assert len(sets) == 1
    assert 'evs' not in sets[0]  # EVs should be skipped if invalid 