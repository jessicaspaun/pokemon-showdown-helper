"""
Opponent Modeller for predicting opponent's most likely builds based on usage statistics and analysis sets.
"""
from typing import List, Dict, Optional
from core_logic.pokemon_object import PokemonInstance
from data_scripts.database import get_db_connection

class OpponentModeller:
    """
    Predicts opponent's most likely builds based on usage statistics and analysis sets.
    Prioritizes usage statistics over analysis sets when available.
    """
    
    def __init__(self):
        self.db = get_db_connection()
    
    def _get_usage_stats_sets(self, pokemon_name: str) -> List[Dict]:
        """
        Get sets from usage statistics for a given Pokémon.
        Returns a list of dictionaries containing set information.
        """
        query = """
        SELECT * FROM Gen7OUSets 
        WHERE pokemon_name = ? AND source LIKE 'usage_stats_%'
        ORDER BY usage_percentage DESC
        """
        cursor = self.db.cursor()
        cursor.execute(query, (pokemon_name,))
        return cursor.fetchall()
    
    def _get_analysis_sets(self, pokemon_name: str) -> List[Dict]:
        """
        Get sets from Smogon analysis pages for a given Pokémon.
        Returns a list of dictionaries containing set information.
        """
        query = """
        SELECT * FROM Gen7OUSets 
        WHERE pokemon_name = ? AND source = 'smogon_analysis_page'
        """
        cursor = self.db.cursor()
        cursor.execute(query, (pokemon_name,))
        return cursor.fetchall()
    
    def _convert_set_to_pokemon_instance(self, set_data: Dict) -> PokemonInstance:
        """
        Convert a set from the database into a PokemonInstance object.
        """
        return PokemonInstance(
            species=set_data['pokemon_name'],
            level=100,  # Standard level for Gen 7 OU
            base_stats=self._get_base_stats(set_data['pokemon_name']),
            iv=self._parse_ivs(set_data['ivs']),
            ev=self._parse_evs(set_data['evs']),
            nature=set_data['nature'],
            ability=set_data['ability'],
            item=set_data['item'],
            types=self._get_types(set_data['pokemon_name']),
            moves=set_data['moves'].split(',')
        )
    
    def _get_base_stats(self, pokemon_name: str) -> Dict[str, int]:
        """Get base stats for a Pokémon from the database."""
        query = "SELECT * FROM Pokemon WHERE name = ?"
        cursor = self.db.cursor()
        cursor.execute(query, (pokemon_name,))
        pokemon_data = cursor.fetchone()
        return {
            'hp': pokemon_data['hp'],
            'atk': pokemon_data['atk'],
            'def': pokemon_data['def'],
            'spa': pokemon_data['spa'],
            'spd': pokemon_data['spd'],
            'spe': pokemon_data['spe']
        }
    
    def _get_types(self, pokemon_name: str) -> List[str]:
        """Get types for a Pokémon from the database."""
        query = "SELECT type1, type2 FROM Pokemon WHERE name = ?"
        cursor = self.db.cursor()
        cursor.execute(query, (pokemon_name,))
        pokemon_data = cursor.fetchone()
        types = [pokemon_data['type1']]
        if pokemon_data['type2']:
            types.append(pokemon_data['type2'])
        return types
    
    def _parse_ivs(self, iv_string: str) -> Dict[str, int]:
        """Parse IV string into dictionary."""
        if not iv_string:
            return {'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31}
        
        ivs = {}
        for stat in iv_string.split('/'):
            stat_name, value = stat.split(':')
            ivs[stat_name.lower()] = int(value)
        return ivs
    
    def _parse_evs(self, ev_string: str) -> Dict[str, int]:
        """Parse EV string into dictionary."""
        if not ev_string:
            return {'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0}
        
        evs = {}
        for stat in ev_string.split('/'):
            stat_name, value = stat.split(':')
            evs[stat_name.lower()] = int(value)
        return evs
    
    def predict_opponent_team(self, opponent_pokemon_names: List[str]) -> List[PokemonInstance]:
        """
        Predict the most likely builds for opponent's team based on usage statistics and analysis sets.
        
        Args:
            opponent_pokemon_names: List of Pokémon names in opponent's team
            
        Returns:
            List of PokemonInstance objects representing predicted builds
        """
        predicted_team = []
        
        for pokemon_name in opponent_pokemon_names:
            # Try to get sets from usage statistics first
            usage_sets = self._get_usage_stats_sets(pokemon_name)
            
            if usage_sets:
                # Use the highest usage set
                predicted_team.append(self._convert_set_to_pokemon_instance(usage_sets[0]))
            else:
                # Fall back to analysis sets
                analysis_sets = self._get_analysis_sets(pokemon_name)
                if analysis_sets:
                    predicted_team.append(self._convert_set_to_pokemon_instance(analysis_sets[0]))
                else:
                    # If no sets found, create a basic instance with default values
                    predicted_team.append(PokemonInstance(
                        species=pokemon_name,
                        level=100,
                        base_stats=self._get_base_stats(pokemon_name),
                        iv={'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31},
                        ev={'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0},
                        nature='Serious',
                        ability=None,
                        item=None,
                        types=self._get_types(pokemon_name),
                        moves=[]
                    ))
        
        return predicted_team 