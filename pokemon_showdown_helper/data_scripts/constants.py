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
POKEDEX_URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/pokedex.ts"
MOVES_URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/moves.ts"
ABILITIES_URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/abilities.ts"
ITEMS_URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/items.ts"
LEARNSETS_URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/learnsets.ts"
TYPECHART_URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/data/typechart.ts"
FORMATS_URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/config/formats.ts"

# Smogon usage statistics URL (Gen 7 OU)
SMOGON_USAGE_STATS_URL = "https://www.smogon.com/stats/2017-11/gen7ou-0.json"

# Nature data for stat modifications
NATURES_DATA = {
    "Adamant": {"atk": 1.1, "spa": 0.9},
    "Bashful": {},
    "Bold": {"def": 1.1, "atk": 0.9},
    "Brave": {"atk": 1.1, "spe": 0.9},
    "Calm": {"spd": 1.1, "atk": 0.9},
    "Careful": {"spd": 1.1, "spa": 0.9},
    "Docile": {},
    "Gentle": {"spd": 1.1, "def": 0.9},
    "Hardy": {},
    "Hasty": {"spe": 1.1, "def": 0.9},
    "Impish": {"def": 1.1, "spa": 0.9},
    "Jolly": {"spe": 1.1, "spa": 0.9},
    "Lax": {"def": 1.1, "spd": 0.9},
    "Lonely": {"atk": 1.1, "def": 0.9},
    "Mild": {"spa": 1.1, "def": 0.9},
    "Modest": {"spa": 1.1, "atk": 0.9},
    "Naive": {"spe": 1.1, "spd": 0.9},
    "Naughty": {"atk": 1.1, "spd": 0.9},
    "Quiet": {"spa": 1.1, "spe": 0.9},
    "Quirky": {},
    "Rash": {"spa": 1.1, "spd": 0.9},
    "Relaxed": {"def": 1.1, "spe": 0.9},
    "Sassy": {"spd": 1.1, "spe": 0.9},
    "Serious": {},
    "Timid": {"spe": 1.1, "atk": 0.9}
}

# Create necessary directories
for directory in [DB_DIR, POKEMON_SHOWDOWN_RAW_DIR, SMOGON_RAW_DIR]:
    directory.mkdir(parents=True, exist_ok=True) 