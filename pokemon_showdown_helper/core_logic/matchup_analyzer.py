"""
Matchup Analyzer for analyzing team matchups and generating strategic insights.
"""
from typing import List, Dict, Set, Tuple
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team
from core_logic.damage_calculator import DamageCalculator

class MatchupAnalyzer:
    """
    Analyzes matchups between two teams and generates strategic insights.
    """
    
    def __init__(self):
        self.damage_calculator = DamageCalculator()
    
    def analyze_matchup(self, user_team: Team, opponent_team: Team) -> Dict:
        """
        Analyze the matchup between user's team and opponent's team.
        
        Args:
            user_team: Team object representing user's team
            opponent_team: Team object representing opponent's team
            
        Returns:
            Dictionary containing:
            - key_threats: List of Pokémon that can OHKO/2HKO others
            - type_matchup_summary: Count of weaknesses/resistances for each team
            - speed_comparison: List of all Pokémon with their speed stats
            - vulnerabilities: Summary of potential vulnerabilities for user's team
        """
        return {
            'key_threats': self._identify_key_threats(user_team, opponent_team),
            'type_matchup_summary': self._analyze_type_matchups(user_team, opponent_team),
            'speed_comparison': self._compare_speed_tiers(user_team, opponent_team),
            'vulnerabilities': self._identify_vulnerabilities(user_team, opponent_team)
        }
    
    def _identify_key_threats(self, user_team: Team, opponent_team: Team) -> List[Dict]:
        """Identify Pokémon that can OHKO/2HKO others."""
        key_threats = []
        
        for attacker in user_team.pokemon + opponent_team.pokemon:
            for defender in user_team.pokemon + opponent_team.pokemon:
                if attacker == defender:
                    continue
                
                # Check each move of the attacker
                for move in attacker.moves:
                    damage = self.damage_calculator.calculate_damage(
                        attacker, defender, move
                    )
                    defender_hp = defender.calculate_stats()['hp']
                    
                    if damage >= defender_hp:  # OHKO
                        key_threats.append({
                            'attacker': attacker.species,
                            'defender': defender.species,
                            'move': move,
                            'damage': damage,
                            'defender_hp': defender_hp,
                            'ko_type': 'OHKO'
                        })
                    elif damage >= defender_hp * 0.5:  # 2HKO
                        key_threats.append({
                            'attacker': attacker.species,
                            'defender': defender.species,
                            'move': move,
                            'damage': damage,
                            'defender_hp': defender_hp,
                            'ko_type': '2HKO'
                        })
        
        return key_threats
    
    def _analyze_type_matchups(self, user_team: Team, opponent_team: Team) -> Dict:
        """Analyze type matchups between teams."""
        user_weaknesses = self._get_team_weaknesses(user_team)
        opponent_weaknesses = self._get_team_weaknesses(opponent_team)
        user_resistances = self._get_team_resistances(user_team)
        opponent_resistances = self._get_team_resistances(opponent_team)
        
        return {
            'user_team': {
                'weaknesses': user_weaknesses,
                'resistances': user_resistances
            },
            'opponent_team': {
                'weaknesses': opponent_weaknesses,
                'resistances': opponent_resistances
            }
        }
    
    def _get_team_weaknesses(self, team: Team) -> Dict[str, int]:
        """Get count of weaknesses for each type in the team."""
        weaknesses = {}
        for pokemon in team.pokemon:
            for type_name in pokemon.types:
                query = "SELECT * FROM TypeChart WHERE defending_type = ?"
                cursor = self.damage_calculator.db.cursor()
                cursor.execute(query, (type_name,))
                type_chart = cursor.fetchone()
                
                for attacking_type, effectiveness in type_chart.items():
                    if effectiveness > 1.0:  # Weak to this type
                        weaknesses[attacking_type] = weaknesses.get(attacking_type, 0) + 1
        
        return weaknesses
    
    def _get_team_resistances(self, team: Team) -> Dict[str, int]:
        """Get count of resistances for each type in the team."""
        resistances = {}
        for pokemon in team.pokemon:
            for type_name in pokemon.types:
                query = "SELECT * FROM TypeChart WHERE defending_type = ?"
                cursor = self.damage_calculator.db.cursor()
                cursor.execute(query, (type_name,))
                type_chart = cursor.fetchone()
                
                for attacking_type, effectiveness in type_chart.items():
                    if effectiveness < 1.0:  # Resistant to this type
                        resistances[attacking_type] = resistances.get(attacking_type, 0) + 1
        
        return resistances
    
    def _compare_speed_tiers(self, user_team: Team, opponent_team: Team) -> List[Dict]:
        """Compare speed tiers between teams."""
        speed_tiers = []
        
        for pokemon in user_team.pokemon:
            speed_tiers.append({
                'pokemon': pokemon.species,
                'speed': pokemon.calculate_stats()['spe'],
                'team': 'user'
            })
        
        for pokemon in opponent_team.pokemon:
            speed_tiers.append({
                'pokemon': pokemon.species,
                'speed': pokemon.calculate_stats()['spe'],
                'team': 'opponent'
            })
        
        return sorted(speed_tiers, key=lambda x: x['speed'], reverse=True)
    
    def _identify_vulnerabilities(self, user_team: Team, opponent_team: Team) -> Dict:
        """Identify potential vulnerabilities in user's team."""
        vulnerabilities = {
            'common_weaknesses': self._find_common_weaknesses(user_team, opponent_team),
            'speed_vulnerabilities': self._find_speed_vulnerabilities(user_team, opponent_team),
            'coverage_gaps': self._find_coverage_gaps(user_team, opponent_team)
        }
        return vulnerabilities
    
    def _find_common_weaknesses(self, user_team: Team, opponent_team: Team) -> List[str]:
        """Find types that user's team is weak to and opponent's team can exploit."""
        user_weaknesses = self._get_team_weaknesses(user_team)
        opponent_offensive_types = set()
        
        for pokemon in opponent_team.pokemon:
            for move in pokemon.moves:
                if ' ' in move:  # Move with type
                    move_type = move.split()[1]
                    opponent_offensive_types.add(move_type)
        
        return [type_name for type_name, count in user_weaknesses.items()
                if count >= 2 and type_name in opponent_offensive_types]
    
    def _find_speed_vulnerabilities(self, user_team: Team, opponent_team: Team) -> List[Dict]:
        """Find cases where opponent's Pokémon outspeed user's Pokémon."""
        vulnerabilities = []
        speed_tiers = self._compare_speed_tiers(user_team, opponent_team)
        
        for i, pokemon in enumerate(speed_tiers):
            if pokemon['team'] == 'user':
                # Check if any opponent Pokémon outspeeds this one
                for opponent in speed_tiers[:i]:
                    if opponent['team'] == 'opponent':
                        vulnerabilities.append({
                            'user_pokemon': pokemon['pokemon'],
                            'opponent_pokemon': opponent['pokemon'],
                            'speed_difference': opponent['speed'] - pokemon['speed']
                        })
        
        return vulnerabilities
    
    def _find_coverage_gaps(self, user_team: Team, opponent_team: Team) -> List[str]:
        """Find types that user's team lacks coverage for."""
        user_coverage = set()
        opponent_types = set()
        
        # Get all types user's team can hit
        for pokemon in user_team.pokemon:
            for move in pokemon.moves:
                if ' ' in move:  # Move with type
                    move_type = move.split()[1]
                    user_coverage.add(move_type)
        
        # Get all types opponent's team has
        for pokemon in opponent_team.pokemon:
            opponent_types.update(pokemon.types)
        
        # Find types opponent has that user can't hit effectively
        return [type_name for type_name in opponent_types
                if not any(self.damage_calculator._get_type_effectiveness(attacking_type, [type_name]) > 1.0
                          for attacking_type in user_coverage)] 