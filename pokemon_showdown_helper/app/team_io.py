"""
Module for handling team import/export functionality.
"""
from typing import List, Dict, Optional, Tuple
import re
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team
from data_scripts.database import get_db_connection

class TeamIO:
    """Handles importing and exporting teams in various formats."""
    
    def __init__(self):
        self.db = get_db_connection()
    
    def import_from_showdown(self, showdown_text: str) -> List[PokemonInstance]:
        """
        Import a team from Pokémon Showdown format.
        
        Args:
            showdown_text: Team in Showdown format
            
        Returns:
            List of PokemonInstance objects
        """
        pokemon_list = []
        current_pokemon = None
        current_moves = []
        
        for line in showdown_text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # New Pokémon entry
            if not line.startswith('-'):
                if current_pokemon:
                    current_pokemon.moves = current_moves
                    pokemon_list.append(current_pokemon)
                    current_moves = []
                
                # Parse Pokémon line
                parts = line.split(' @ ')
                species = parts[0].strip()
                item = parts[1].strip() if len(parts) > 1 else ''
                
                # Get base stats and types from database
                cursor = self.db.cursor()
                cursor.execute("""
                    SELECT hp, atk, def, spa, spd, spe, type1, type2
                    FROM Pokemon
                    WHERE name = ?
                """, (species,))
                row = cursor.fetchone()
                
                if not row:
                    raise ValueError(f"Pokémon {species} not found in database")
                
                current_pokemon = PokemonInstance(
                    species=species,
                    level=100,
                    base_stats={
                        'hp': row[0],
                        'atk': row[1],
                        'def': row[2],
                        'spa': row[3],
                        'spd': row[4],
                        'spe': row[5]
                    },
                    iv={'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31},
                    ev={'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0},
                    nature='Timid',  # Default, will be updated
                    ability='',  # Will be updated
                    item=item,
                    types=[row[6]] + ([row[7]] if row[7] else []),
                    moves=[]
                )
            else:
                # Parse move or other attribute
                line = line[1:].strip()  # Remove leading '-'
                
                if line.startswith('Ability:'):
                    current_pokemon.ability = line.split(':')[1].strip()
                elif line.startswith('Level:'):
                    current_pokemon.level = int(line.split(':')[1].strip())
                elif line.startswith('EVs:'):
                    evs = self._parse_evs(line)
                    current_pokemon.ev = evs
                elif line.startswith('IVs:'):
                    ivs = self._parse_ivs(line)
                    current_pokemon.iv = ivs
                elif line.startswith('Nature'):
                    nature = line.split('Nature')[0].strip()
                    current_pokemon.nature = nature
                else:
                    # Assume it's a move
                    current_moves.append(line)
        
        # Add the last Pokémon
        if current_pokemon:
            current_pokemon.moves = current_moves
            pokemon_list.append(current_pokemon)
        
        return pokemon_list
    
    def export_to_showdown(self, team: Team) -> str:
        """
        Export a team to Pokémon Showdown format.
        
        Args:
            team: Team object to export
            
        Returns:
            String in Showdown format
        """
        lines = []
        
        for pokemon in team.pokemon:
            # Pokémon name and item
            if pokemon.item:
                lines.append(f"{pokemon.species} @ {pokemon.item}")
            else:
                lines.append(pokemon.species)
            
            # Ability
            if pokemon.ability:
                lines.append(f"- Ability: {pokemon.ability}")
            
            # Level
            lines.append(f"- Level: {pokemon.level}")
            
            # EVs
            ev_str = self._format_evs(pokemon.ev)
            if ev_str:
                lines.append(f"- EVs: {ev_str}")
            
            # IVs
            iv_str = self._format_ivs(pokemon.iv)
            if iv_str:
                lines.append(f"- IVs: {iv_str}")
            
            # Nature
            if pokemon.nature:
                lines.append(f"- {pokemon.nature} Nature")
            
            # Moves
            for move in pokemon.moves:
                lines.append(f"- {move}")
            
            # Add blank line between Pokémon
            lines.append("")
        
        return '\n'.join(lines)
    
    def import_from_template(self, template_name: str) -> List[PokemonInstance]:
        """
        Import a team from a predefined template.
        
        Args:
            template_name: Name of the template to import
            
        Returns:
            List of PokemonInstance objects
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT team_data
            FROM TeamTemplates
            WHERE name = ?
        """, (template_name,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"Template {template_name} not found")
        
        return self.import_from_showdown(row[0])
    
    def save_as_template(self, team: Team, template_name: str) -> None:
        """
        Save a team as a template.
        
        Args:
            team: Team to save
            template_name: Name for the template
        """
        showdown_text = self.export_to_showdown(team)
        
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO TeamTemplates (name, team_data)
            VALUES (?, ?)
        """, (template_name, showdown_text))
        self.db.commit()
    
    def get_available_templates(self) -> List[str]:
        """Get list of available team templates."""
        cursor = self.db.cursor()
        cursor.execute("SELECT name FROM TeamTemplates ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    
    def _parse_evs(self, ev_line: str) -> Dict[str, int]:
        """Parse EV line from Showdown format."""
        evs = {'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0}
        
        # Remove 'EVs:' prefix
        ev_line = ev_line.split(':', 1)[1].strip()
        
        # Parse each stat
        for stat in ev_line.split('/'):
            stat = stat.strip()
            if not stat:
                continue
            
            # Extract number and stat name
            match = re.match(r'(\d+)\s+(\w+)', stat)
            if match:
                value, stat_name = match.groups()
                stat_name = stat_name.lower()
                if stat_name in evs:
                    evs[stat_name] = int(value)
        
        return evs
    
    def _parse_ivs(self, iv_line: str) -> Dict[str, int]:
        """Parse IV line from Showdown format."""
        ivs = {'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31}
        
        # Remove 'IVs:' prefix
        iv_line = iv_line.split(':', 1)[1].strip()
        
        # Parse each stat
        for stat in iv_line.split('/'):
            stat = stat.strip()
            if not stat:
                continue
            
            # Extract number and stat name
            match = re.match(r'(\d+)\s+(\w+)', stat)
            if match:
                value, stat_name = match.groups()
                stat_name = stat_name.lower()
                if stat_name in ivs:
                    ivs[stat_name] = int(value)
        
        return ivs
    
    def _format_evs(self, evs: Dict[str, int]) -> str:
        """Format EVs for Showdown export."""
        parts = []
        for stat, value in evs.items():
            if value > 0:
                parts.append(f"{value} {stat.upper()}")
        return ' / '.join(parts)
    
    def _format_ivs(self, ivs: Dict[str, int]) -> str:
        """Format IVs for Showdown export."""
        parts = []
        for stat, value in ivs.items():
            if value != 31:  # Only include non-31 IVs
                parts.append(f"{value} {stat.upper()}")
        return ' / '.join(parts) 