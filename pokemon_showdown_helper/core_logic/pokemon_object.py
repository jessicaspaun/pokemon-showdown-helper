"""
Represents a single Pokémon instance with stat calculation logic for Gen 7.
"""
from typing import Dict, List, Optional
from data_scripts.constants import NATURES_DATA
import json
import sqlite3

class PokemonInstance:
    """
    Represents a specific instance of a Pokémon with its stats and attributes.
    """
    def __init__(
        self,
        species: str,
        level: int = 100,
        base_stats: Dict[str, int] = None,
        iv: Dict[str, int] = None,
        ev: Dict[str, int] = None,
        nature: str = "Serious",
        ability: str = None,
        item: str = None,
        moves: List[str] = None,
        types: List[str] = None,
    ):
        self.species = species
        self.level = level
        self.base_stats = base_stats or {"hp": 50, "atk": 50, "def": 50, "spa": 50, "spd": 50, "spe": 50}
        self.iv = iv or {"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31}
        self.ev = ev or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
        self.nature = nature
        self.ability = ability
        self.item = item
        self.moves = moves or []
        self.types = types or []

    def calculate_stats(self) -> Dict[str, int]:
        """
        Calculate the Pokémon's stats based on Gen 7 formulas.
        Includes nature modifiers which affect non-HP stats.
        """
        print(f"[DEBUG] calculate_stats: species={self.species}, base_stats={self.base_stats}")
        print(f"[DEBUG] base_stats keys: {list(self.base_stats.keys())}")
        stats = {}
        
        # Get nature modifiers
        nature_modifiers = NATURES_DATA.get(self.nature, {"hp": 1.0, "atk": 1.0, "def": 1.0, "spa": 1.0, "spd": 1.0, "spe": 1.0})
        
        for stat in ["hp", "atk", "def", "spa", "spd", "spe"]:
            # Base stat calculation
            base = (2 * self.base_stats[stat] + self.iv[stat] + self.ev[stat] // 4) * self.level / 100
            
            if stat == "hp":
                stats[stat] = int(base + self.level + 10)
            else:
                # Apply nature modifier to non-HP stats
                stats[stat] = int((base + 5) * nature_modifiers[stat])
                
        return stats

    @classmethod
    def from_db_row(cls, row, db_path=None) -> 'PokemonInstance':
        """
        Create a PokemonInstance from a database row (dict or sqlite3.Row).
        If base_stats is missing, fetch from the Pokemon table using db_path.
        """
        def get_val(key, default):
            try:
                return row[key]
            except (KeyError, IndexError):
                return default
        def parse_json_field(val, default):
            if isinstance(val, str):
                try:
                    return json.loads(val)
                except Exception:
                    return default
            return val if val is not None else default
        # Try to get base_stats from row, else fetch from Pokemon table
        base_stats = parse_json_field(get_val("base_stats", None), None)
        species = get_val("species", get_val("pokemon_name", None))
        if base_stats is None and db_path and species:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT base_stats FROM Pokemon WHERE name = ?", (species,))
            result = cur.fetchone()
            if result and result[0]:
                # base_stats is stored as comma-separated string, e.g. '35,55,40,50,50,90'
                stat_vals = [int(x) for x in result[0].split(",")]
                stat_keys = ["hp", "atk", "def", "spa", "spd", "spe"]
                base_stats = dict(zip(stat_keys, stat_vals))
            else:
                base_stats = {"hp": 50, "atk": 50, "def": 50, "spa": 50, "spd": 50, "spe": 50}
            conn.close()
        elif base_stats is None:
            base_stats = {"hp": 50, "atk": 50, "def": 50, "spa": 50, "spd": 50, "spe": 50}
        # print(f"[DEBUG] from_db_row: species={species}, base_stats={base_stats}")
        return cls(
            species=species,
            level=get_val("level", 100),
            base_stats=base_stats,
            iv=parse_json_field(get_val("iv", None), {stat: 31 for stat in ["hp", "atk", "def", "spa", "spd", "spe"]}),
            ev=parse_json_field(get_val("ev", get_val("evs", None)), {stat: 0 for stat in ["hp", "atk", "def", "spa", "spd", "spe"]}),
            nature=get_val("nature", "Serious"),
            ability=get_val("ability", None),
            item=get_val("item", None),
            moves=parse_json_field(get_val("moves", []), []),
            types=parse_json_field(get_val("types", []), [])
        ) 