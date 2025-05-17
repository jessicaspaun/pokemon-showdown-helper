"""
Constants used throughout the data acquisition and processing pipeline.
"""

import os
from pathlib import Path

# Base URLs
POKEMON_SHOWDOWN_BASE_URL = "https://play.pokemonshowdown.com/data"
SMOGON_BASE_URL = "https://www.smogon.com/dex/sm/pokemon"

# Database paths
DB_DIR = Path(__file__).parent.parent / "database"
DB_PATH = DB_DIR / "pokemon_showdown.db"

# Raw data paths
RAW_DATA_DIR = Path(__file__).parent.parent / "raw_data"
POKEMON_SHOWDOWN_RAW_DIR = RAW_DATA_DIR / "pokemon_showdown"
SMOGON_RAW_DIR = RAW_DATA_DIR / "smogon"

# Pokémon Showdown data file URLs
POKEDEX_URL = f"{POKEMON_SHOWDOWN_BASE_URL}/pokedex.json"
MOVES_URL = f"{POKEMON_SHOWDOWN_BASE_URL}/moves.json"
ABILITIES_URL = f"{POKEMON_SHOWDOWN_BASE_URL}/abilities.json"
ITEMS_URL = f"{POKEMON_SHOWDOWN_BASE_URL}/items.json"
LEARNSETS_URL = f"{POKEMON_SHOWDOWN_BASE_URL}/learnsets.json"
TYPECHART_URL = f"{POKEMON_SHOWDOWN_BASE_URL}/typechart.json"

# Smogon usage statistics URL (Gen 7 OU)
SMOGON_USAGE_STATS_URL = "https://www.smogon.com/stats/2017-11/gen7ou-0.json"

# Nature data for stat modifications
NATURES_DATA = {
    "adamant": {"atk": 1.1, "spa": 0.9},
    "bashful": {},
    "bold": {"def": 1.1, "atk": 0.9},
    "brave": {"atk": 1.1, "spe": 0.9},
    "calm": {"spd": 1.1, "atk": 0.9},
    "careful": {"spd": 1.1, "spa": 0.9},
    "docile": {},
    "gentle": {"spd": 1.1, "def": 0.9},
    "hardy": {},
    "hasty": {"spe": 1.1, "def": 0.9},
    "impish": {"def": 1.1, "spa": 0.9},
    "jolly": {"spe": 1.1, "spa": 0.9},
    "lax": {"def": 1.1, "spd": 0.9},
    "lonely": {"atk": 1.1, "def": 0.9},
    "mild": {"spa": 1.1, "def": 0.9},
    "modest": {"spa": 1.1, "atk": 0.9},
    "naive": {"spe": 1.1, "spd": 0.9},
    "naughty": {"atk": 1.1, "spd": 0.9},
    "quiet": {"spa": 1.1, "spe": 0.9},
    "quirky": {},
    "rash": {"spa": 1.1, "spd": 0.9},
    "relaxed": {"def": 1.1, "spe": 0.9},
    "sassy": {"spd": 1.1, "spe": 0.9},
    "serious": {},
    "timid": {"spe": 1.1, "atk": 0.9},
}

# Create necessary directories
for directory in [DB_DIR, POKEMON_SHOWDOWN_RAW_DIR, SMOGON_RAW_DIR]:
    directory.mkdir(parents=True, exist_ok=True) 