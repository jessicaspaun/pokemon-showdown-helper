"""
Module for fetching and parsing competitive sets from Smogon analysis pages.
"""
import sqlite3
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from data_scripts import constants, utils

def get_gen7ou_pokemon_list(db_path: Path = constants.DB_PATH) -> List[str]:
    """
    Retrieve the list of Pokémon that are legal in Gen 7 OU from the database.
    Args:
        db_path: Path to the SQLite database file.
    Returns:
        List of Pokémon names that are legal in Gen 7 OU.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Get all Pokémon that are not in the banlist
    cur.execute("""
        SELECT p.name 
        FROM Pokemon p
        WHERE p.name NOT IN (
            SELECT rule 
            FROM FormatRules 
            WHERE format_id = 'gen7ou' 
            AND rule_type = 'banlist'
        )
        ORDER BY p.name
    """)
    
    pokemon_list = [row[0] for row in cur.fetchall()]
    conn.close()
    return pokemon_list

def workspace_pokemon_smogon_page_html(pokemon_name: str) -> Optional[str]:
    """
    Download the Smogon analysis page HTML for a given Pokémon.
    Args:
        pokemon_name: Name of the Pokémon to fetch analysis for.
    Returns:
        HTML content of the Smogon analysis page, or None if the request fails.
    """
    # Convert Pokémon name to Smogon URL format
    smogon_name = pokemon_name.lower().replace(' ', '')
    url = f"https://www.smogon.com/dex/sm/pokemon/{smogon_name}/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching Smogon page for {pokemon_name}: {e}")
        return None

def parse_smogon_page_for_sets(html_content: str) -> List[Dict[str, Any]]:
    """
    Parse the Smogon analysis page HTML to extract competitive sets.
    Args:
        html_content: HTML content of the Smogon analysis page.
    Returns:
        List of dictionaries containing set information (moves, ability, item, nature, EVs).
    """
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    sets = []
    
    # Find all set containers
    set_containers = soup.find_all('div', class_='Set')
    
    for container in set_containers:
        set_data = {}
        
        # Extract set name/description
        name_elem = container.find('h3', class_='Set-name')
        if name_elem:
            set_data['name'] = name_elem.text.strip()
        
        # Extract moves
        moves = []
        move_elems = container.find_all('div', class_='Move')
        for move_elem in move_elems:
            move_name = move_elem.find('a', class_='Move-name')
            if move_name:
                moves.append(move_name.text.strip())
        set_data['moves'] = moves
        
        # Extract ability
        ability_elem = container.find('div', class_='Ability')
        if ability_elem:
            ability_name = ability_elem.find('a', class_='Ability-name')
            if ability_name:
                set_data['ability'] = ability_name.text.strip()
        
        # Extract item
        item_elem = container.find('div', class_='Item')
        if item_elem:
            item_name = item_elem.find('a', class_='Item-name')
            if item_name:
                set_data['item'] = item_name.text.strip()
        
        # Extract nature
        nature_elem = container.find('div', class_='Nature')
        if nature_elem:
            nature_name = nature_elem.find('span', class_='Nature-name')
            if nature_name:
                set_data['nature'] = nature_name.text.strip()
        
        # Extract EVs
        ev_elem = container.find('div', class_='EVs')
        if ev_elem:
            ev_text = ev_elem.text.strip()
            # Parse EV text (e.g., "252 HP / 252 Atk / 4 Def")
            evs = {}
            valid_evs = True
            for stat_pair in ev_text.split('/'):
                if stat_pair.strip():
                    try:
                        value, stat = stat_pair.strip().split()
                        evs[stat.lower()] = int(value)
                    except ValueError:
                        valid_evs = False
                        break
            if valid_evs and evs:  # Only add EVs if parsing was successful and we have some
                set_data['evs'] = evs
        
        sets.append(set_data)
    
    return sets

def main_fetch_smogon_sets(db_path: Path = constants.DB_PATH) -> None:
    """
    Main function to fetch and parse Smogon analysis sets for all Gen 7 OU Pokémon.
    Args:
        db_path: Path to the SQLite database file.
    """
    pokemon_list = get_gen7ou_pokemon_list(db_path)
    
    for pokemon_name in pokemon_list:
        print(f"Fetching sets for {pokemon_name}...")
        html_content = workspace_pokemon_smogon_page_html(pokemon_name)
        if html_content:
            sets = parse_smogon_page_for_sets(html_content)
            print(f"Found {len(sets)} sets for {pokemon_name}")
            # TODO: Insert sets into database (will be implemented in Task 1.4.2)
        else:
            print(f"Failed to fetch sets for {pokemon_name}")

if __name__ == "__main__":
    main_fetch_smogon_sets() 