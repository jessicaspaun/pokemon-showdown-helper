"""
Fetch and parse Pokémon Showdown format rules and banlists (Gen 7 OU).
"""
import requests
from pathlib import Path
from typing import Optional
import re
import ast

PS_FORMATS_TS_URL = "https://raw.githubusercontent.com/smogon/pokemon-showdown/master/config/formats.ts"


def workspace_ps_formats_ts_raw(save_path: Optional[Path] = None) -> str:
    """
    Download the formats.ts file from Pokémon Showdown's GitHub repository.
    Args:
        save_path: Optional path to save the downloaded file.
    Returns:
        The raw text content of formats.ts.
    """
    response = requests.get(PS_FORMATS_TS_URL)
    response.raise_for_status()
    content = response.text
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(content)
    return content


def parse_gen7ou_rules_from_formats_ts(formats_ts_text: str) -> dict:
    """
    Parse the formats.ts text to extract Gen 7 OU ruleset and banlist.
    Args:
        formats_ts_text: The raw text of formats.ts.
    Returns:
        A dictionary with ruleset and banlist for Gen 7 OU.
    """
    # Find the [Gen 7] OU block
    pattern = re.compile(r"\{[^\{\}]*name:\s*\\?\"\[Gen 7\] OU\\?\"[^\{\}]*?\},", re.DOTALL)
    match = pattern.search(formats_ts_text)
    if not match:
        return {}
    block = match.group(0)
    # Extract ruleset array
    ruleset_match = re.search(r"ruleset:\s*\[(.*?)\]", block, re.DOTALL)
    banlist_match = re.search(r"banlist:\s*\[(.*?)\]", block, re.DOTALL)
    def parse_array(array_str):
        # Convert JS array to Python list
        items = re.findall(r"'([^']+)'", array_str)
        return items
    ruleset = parse_array(ruleset_match.group(1)) if ruleset_match else []
    banlist = parse_array(banlist_match.group(1)) if banlist_match else []
    return {"ruleset": ruleset, "banlist": banlist}

# If a JSON source for formats/rules is found, add a function to fetch and parse it here. 