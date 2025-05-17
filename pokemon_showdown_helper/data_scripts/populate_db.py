"""
Populate the database with core Pokémon Showdown data.
"""
from pathlib import Path
from data_scripts import database_setup, fetch_ps_core_data, constants, fetch_ps_rules_and_formats
import sqlite3
from typing import Dict, Any

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
    # Insert Gen 7 OU format and rules
    formats_ts = fetch_ps_rules_and_formats.workspace_ps_formats_ts_raw()
    gen7ou = fetch_ps_rules_and_formats.parse_gen7ou_rules_from_formats_ts(formats_ts)
    if gen7ou:
        insert_format('gen7ou', '[Gen 7] OU', 'Smogon OU (OverUsed)', db_path)
        insert_format_rules('gen7ou', gen7ou.get('ruleset', []), gen7ou.get('banlist', []), db_path)
    insert_smogon_analysis_sets(db_path)
    insert_usage_stats_sets(db_path, month="2022-12")

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

def insert_learnsets_data(learnsets_data: Dict[str, Any], db_path: Path) -> None:
    """Insert learnsets data into the PokemonLearnset table."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for pokemon_id, data in learnsets_data.items():
        for move_id in data.get("learnset", []):
            cur.execute(
                "INSERT OR REPLACE INTO PokemonLearnset (pokemon_id, move_id) VALUES (?, ?)",
                (pokemon_id, move_id)
            )
    conn.commit()
    conn.close()

def insert_typechart_data(typechart_data: Dict[str, Any], db_path: Path) -> None:
    """Insert typechart data into the Typechart table."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for attacking_type, data in typechart_data.items():
        for defending_type, multiplier in data.get("damageTaken", {}).items():
            cur.execute(
                "INSERT OR REPLACE INTO Typechart (attacking_type, defending_type, multiplier) VALUES (?, ?, ?)",
                (attacking_type, defending_type, multiplier)
            )
    conn.commit()
    conn.close()

def insert_format(format_id: str, name: str, description: str, db_path: Path) -> None:
    """Insert a format into the Formats table."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO Formats (id, name, description) VALUES (?, ?, ?)",
        (format_id, name, description)
    )
    conn.commit()
    conn.close()

def insert_format_rules(format_id: str, ruleset: list, banlist: list, db_path: Path) -> None:
    """Insert rules and bans for a format into the FormatRules table."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for rule in ruleset:
        cur.execute(
            "INSERT OR REPLACE INTO FormatRules (format_id, rule_type, rule) VALUES (?, ?, ?)",
            (format_id, 'ruleset', rule)
        )
    for ban in banlist:
        cur.execute(
            "INSERT OR REPLACE INTO FormatRules (format_id, rule_type, rule) VALUES (?, ?, ?)",
            (format_id, 'banlist', ban)
        )
    conn.commit()
    conn.close()

def create_gen7ou_sets_table(db_path: Path):
    """Create the Gen7OUSets table if it does not exist."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
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

def insert_smogon_analysis_sets(db_path: Path):
    """
    Fetch, parse, and insert Smogon analysis sets for all Gen 7 OU Pokémon into the Gen7OUSets table.
    Args:
        db_path: Path to the SQLite database file.
    """
    from data_scripts import fetch_smogon_analysis_sets
    create_gen7ou_sets_table(db_path)
    pokemon_list = fetch_smogon_analysis_sets.get_gen7ou_pokemon_list(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for pokemon_name in pokemon_list:
        html_content = fetch_smogon_analysis_sets.workspace_pokemon_smogon_page_html(pokemon_name)
        if html_content:
            sets = fetch_smogon_analysis_sets.parse_smogon_page_for_sets(html_content)
            for set_data in sets:
                cur.execute('''
                    INSERT INTO Gen7OUSets (pokemon_name, set_name, moves, ability, item, nature, evs, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pokemon_name,
                    set_data.get('name', ''),
                    ','.join(set_data.get('moves', [])),
                    set_data.get('ability', ''),
                    set_data.get('item', ''),
                    set_data.get('nature', ''),
                    str(set_data.get('evs', {})),
                    'smogon_analysis_page'
                ))
    conn.commit()
    conn.close()

def insert_usage_stats_sets(db_path: Path, month: str = "2022-12"):
    """
    Fetch, parse, and insert usage stats-derived sets for Gen 7 OU into the Gen7OUSets table.
    Args:
        db_path: Path to the SQLite database file.
        month: Month in YYYY-MM format (default: "2022-12").
    """
    from data_scripts import fetch_usage_stats
    create_gen7ou_sets_table(db_path)
    chaos_data = fetch_usage_stats.workspace_gen7ou_chaos_data(month=month)
    parsed = fetch_usage_stats.parse_chaos_data(chaos_data)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for pokemon_name, stats in parsed.items():
        # Compose a set from the most used ability, item, moves, and spread
        set_name = f"Usage Stats {month}"
        moves = [m[0] for m in stats.get("top_moves", [])[:4]]
        ability = stats.get("top_abilities", [{}])[0][0] if stats.get("top_abilities") else ""
        item = stats.get("top_items", [{}])[0][0] if stats.get("top_items") else ""
        nature, evs = "", {}
        if stats.get("top_spreads"):
            spread_str = stats["top_spreads"][0][0]
            # Example: Timid:252/0/0/252/4/0
            if ":" in spread_str:
                nature, ev_str = spread_str.split(":", 1)
                ev_keys = ["hp", "atk", "def", "spa", "spd", "spe"]
                ev_vals = ev_str.split("/")
                if len(ev_vals) == 6:
                    evs = {k: int(v) for k, v in zip(ev_keys, ev_vals)}
        cur.execute('''
            INSERT INTO Gen7OUSets (pokemon_name, set_name, moves, ability, item, nature, evs, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pokemon_name,
            set_name,
            ','.join(moves),
            ability,
            item,
            nature,
            str(evs),
            f'usage_stats_{month}'
        ))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main_populate()
    print("Database populated with core data.") 