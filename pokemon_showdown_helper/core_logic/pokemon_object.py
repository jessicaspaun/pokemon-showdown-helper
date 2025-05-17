"""
Represents a single Pokémon instance with stat calculation logic for Gen 7.
"""
from typing import Dict, List, Optional
from data_scripts.constants import NATURES_DATA

class PokemonInstance:
    """
    Represents a Pokémon with all properties needed for stat calculation and battle logic.
    """
    def __init__(
        self,
        species: str,
        level: int = 100,
        base_stats: Optional[Dict[str, int]] = None,
        iv: Optional[Dict[str, int]] = None,
        ev: Optional[Dict[str, int]] = None,
        nature: str = "serious",
        ability: Optional[str] = None,
        item: Optional[str] = None,
        moves: Optional[List[str]] = None,
    ):
        self.species = species
        self.level = level
        self.base_stats = base_stats or {k: 0 for k in ["hp", "atk", "def", "spa", "spd", "spe"]}
        self.iv = iv or {k: 31 for k in ["hp", "atk", "def", "spa", "spd", "spe"]}
        self.ev = ev or {k: 0 for k in ["hp", "atk", "def", "spa", "spd", "spe"]}
        self.nature = nature.lower()
        self.ability = ability
        self.item = item
        self.moves = moves or []

    def calculate_stats(self) -> Dict[str, int]:
        """
        Calculate the final stats for this Pokémon instance (Gen 7 formula).
        Returns:
            Dict[str, int]: Final stats for hp, atk, def, spa, spd, spe.
        """
        stats = {}
        nature_mods = NATURES_DATA.get(self.nature, {})
        for stat in ["hp", "atk", "def", "spa", "spd", "spe"]:
            base = self.base_stats.get(stat, 0)
            iv = self.iv.get(stat, 31)
            ev = self.ev.get(stat, 0)
            if stat == "hp":
                if base == 1:  # For Shedinja
                    stats[stat] = 1
                else:
                    stats[stat] = ((2 * base + iv + (ev // 4)) * self.level) // 100 + self.level + 10
            else:
                nature_mod = 1.0
                if stat in nature_mods:
                    nature_mod = nature_mods[stat]
                stats[stat] = int((((2 * base + iv + (ev // 4)) * self.level) // 100 + 5) * nature_mod)
        return stats

    @classmethod
    def from_db_row(cls, row: Dict[str, any]) -> "PokemonInstance":
        """
        Factory method to create a PokemonInstance from a DB row or dict.
        """
        return cls(
            species=row.get("name") or row.get("species"),
            base_stats={
                "hp": int(row.get("hp", 0)),
                "atk": int(row.get("atk", 0)),
                "def": int(row.get("def", 0)),
                "spa": int(row.get("spa", 0)),
                "spd": int(row.get("spd", 0)),
                "spe": int(row.get("spe", 0)),
            },
            # Other fields can be filled as needed
        ) 