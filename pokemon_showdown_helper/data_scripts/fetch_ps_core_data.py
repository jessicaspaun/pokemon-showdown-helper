"""
Fetch and parse core Pokémon Showdown data (pokedex, moves, abilities, items, learnsets, typechart).
"""
from pathlib import Path
from typing import Dict, Any
from data_scripts import constants, utils

# --- Pokedex ---
def fetch_pokedex_json(save_path: Path = None) -> Dict[str, Any]:
    """
    Fetch the pokedex JSON from Pokémon Showdown and optionally save it.
    Args:
        save_path: Optional path to save the JSON file.
    Returns:
        The parsed pokedex JSON as a dictionary.
    """
    return utils.download_json(constants.POKEDEX_URL, save_path)

def parse_pokedex_json(pokedex_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the pokedex JSON into a structure suitable for DB insertion.
    Args:
        pokedex_json: The raw pokedex JSON data.
    Returns:
        Parsed data with validated and transformed fields.
    """
    parsed_data = {}
    for pokemon_id, data in pokedex_json.items():
        # Ensure required fields exist
        if not all(key in data for key in ['num', 'species', 'types', 'baseStats']):
            print(f"Warning: Skipping {pokemon_id} due to missing required fields")
            continue
            
        # Transform and validate data
        parsed_data[pokemon_id] = {
            'num': int(data['num']),
            'species': str(data['species']),
            'types': [str(t) for t in data['types']],
            'baseStats': {
                stat: int(data['baseStats'].get(stat, 0))
                for stat in ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
            }
        }
    return parsed_data

# --- Moves ---
def fetch_moves_json(save_path: Path = None) -> Dict[str, Any]:
    """
    Fetch the moves JSON from Pokémon Showdown and optionally save it.
    """
    return utils.download_json(constants.MOVES_URL, save_path)

def parse_moves_json(moves_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the moves JSON into a structure suitable for DB insertion.
    """
    parsed_data = {}
    for move_id, data in moves_json.items():
        # Ensure required fields exist
        if not all(key in data for key in ['name', 'type']):
            print(f"Warning: Skipping {move_id} due to missing required fields")
            continue
            
        # Transform and validate data
        parsed_data[move_id] = {
            'name': str(data['name']),
            'type': str(data['type']),
            'power': int(data.get('power', 0)),
            'accuracy': int(data.get('accuracy', 0)),
            'pp': int(data.get('pp', 0)),
            'category': str(data.get('category', 'Status')),
            'description': str(data.get('desc', ''))
        }
    return parsed_data

# --- Abilities ---
def fetch_abilities_json(save_path: Path = None) -> Dict[str, Any]:
    """
    Fetch the abilities JSON from Pokémon Showdown and optionally save it.
    """
    return utils.download_json(constants.ABILITIES_URL, save_path)

def parse_abilities_json(abilities_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the abilities JSON into a structure suitable for DB insertion.
    """
    parsed_data = {}
    for ability_id, data in abilities_json.items():
        # Ensure required fields exist
        if not all(key in data for key in ['name']):
            print(f"Warning: Skipping {ability_id} due to missing required fields")
            continue
            
        # Transform and validate data
        parsed_data[ability_id] = {
            'name': str(data['name']),
            'description': str(data.get('desc', '')),
            'short_description': str(data.get('shortDesc', ''))
        }
    return parsed_data

# --- Items ---
def fetch_items_json(save_path: Path = None) -> Dict[str, Any]:
    """
    Fetch the items JSON from Pokémon Showdown and optionally save it.
    """
    return utils.download_json(constants.ITEMS_URL, save_path)

def parse_items_json(items_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the items JSON into a structure suitable for DB insertion.
    """
    parsed_data = {}
    for item_id, data in items_json.items():
        # Ensure required fields exist
        if not all(key in data for key in ['name']):
            print(f"Warning: Skipping {item_id} due to missing required fields")
            continue
            
        # Transform and validate data
        parsed_data[item_id] = {
            'name': str(data['name']),
            'description': str(data.get('desc', '')),
            'short_description': str(data.get('shortDesc', '')),
            'gen': int(data.get('gen', 1))
        }
    return parsed_data

# --- Learnsets ---
def fetch_learnsets_json(save_path: Path = None) -> Dict[str, Any]:
    """
    Fetch the learnsets JSON from Pokémon Showdown and optionally save it.
    """
    return utils.download_json(constants.LEARNSETS_URL, save_path)

def parse_learnsets_json(learnsets_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the learnsets JSON into a structure suitable for DB insertion.
    """
    parsed_data = {}
    for pokemon_id, data in learnsets_json.items():
        # Ensure required fields exist
        if 'learnset' not in data:
            print(f"Warning: Skipping {pokemon_id} due to missing learnset")
            continue
            
        # Transform and validate data
        parsed_data[pokemon_id] = {
            'learnset': [str(move) for move in data['learnset']]
        }
    return parsed_data

# --- Typechart ---
def fetch_typechart_json(save_path: Path = None) -> Dict[str, Any]:
    """
    Fetch the typechart JSON from Pokémon Showdown and optionally save it.
    """
    return utils.download_json(constants.TYPECHART_URL, save_path)

def parse_typechart_json(typechart_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the typechart JSON into a structure suitable for DB insertion.
    """
    parsed_data = {}
    for attacking_type, data in typechart_json.items():
        if 'damageTaken' not in data:
            print(f"Warning: Skipping {attacking_type} due to missing damageTaken")
            continue
            
        # Transform and validate data
        parsed_data[attacking_type] = {
            'damage_taken': {
                defending_type: int(multiplier)
                for defending_type, multiplier in data['damageTaken'].items()
            }
        }
    return parsed_data 