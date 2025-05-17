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
        Parsed data (to be defined based on DB schema).
    """
    # Example: just return as-is for now
    return pokedex_json

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
    return moves_json

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
    return abilities_json

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
    return items_json

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
    return learnsets_json

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
    return typechart_json 