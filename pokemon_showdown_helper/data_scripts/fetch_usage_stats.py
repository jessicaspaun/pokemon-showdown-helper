"""
Module for fetching and parsing Smogon Gen 7 OU usage statistics (chaos data).
"""
import requests
from pathlib import Path
from typing import Dict, Any, Optional
import json
from data_scripts import constants

def workspace_gen7ou_chaos_data(month: str = "2022-12", save_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Download the Gen 7 OU chaos JSON for a given month from Smogon.
    Args:
        month: Month in YYYY-MM format (default: "2022-12").
        save_path: Optional path to save the downloaded JSON.
    Returns:
        Parsed JSON data as a dictionary.
    Raises:
        Exception if download or parsing fails.
    """
    url = f"https://www.smogon.com/stats/{month}/chaos/gen7ou-0.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        return data
    except Exception as e:
        print(f"Error downloading or parsing chaos data: {e}")
        raise

def parse_chaos_data(chaos_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Parse chaos JSON for top abilities, items, moves, and EV spreads per Pokémon.
    Args:
        chaos_data: Parsed chaos JSON data.
    Returns:
        Dictionary mapping Pokémon names to their top abilities, items, moves, and EV spreads.
    """
    results = {}
    pokedex = chaos_data.get("data", {})
    for poke, poke_data in pokedex.items():
        poke_stats = {}
        # Top abilities
        abilities = poke_data.get("Abilities", {})
        poke_stats["top_abilities"] = sorted(abilities.items(), key=lambda x: -x[1]["usage"])
        # Top items
        items = poke_data.get("Items", {})
        poke_stats["top_items"] = sorted(items.items(), key=lambda x: -x[1]["usage"])
        # Top moves
        moves = poke_data.get("Moves", {})
        poke_stats["top_moves"] = sorted(moves.items(), key=lambda x: -x[1]["usage"])
        # Top EV spreads
        spreads = poke_data.get("Spreads", {})
        poke_stats["top_spreads"] = sorted(spreads.items(), key=lambda x: -x[1]["usage"])
        results[poke] = poke_stats
    return results

if __name__ == "__main__":
    chaos = workspace_gen7ou_chaos_data()
    parsed = parse_chaos_data(chaos)
    print(f"Parsed usage stats for {len(parsed)} Pokémon.") 