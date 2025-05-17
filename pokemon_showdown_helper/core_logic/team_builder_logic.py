"""
Advanced Team Builder Logic for generating optimal teams based on various strategies and constraints.
"""
from typing import List, Dict, Set, Tuple, Optional
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team
from core_logic.team_synergy_analyzer import TeamSynergyAnalyzer
from core_logic.damage_calculator import DamageCalculator
from core_logic.team_validator import TeamValidator
from data_scripts.database import get_db_connection

class TeamBuilderLogic:
    """
    Advanced team builder that generates optimal teams based on various strategies,
    incorporating synergy analysis, threat coverage, and role balance.
    """
    
    def __init__(self):
        self.db = get_db_connection()
        self.synergy_analyzer = TeamSynergyAnalyzer()
        self.damage_calculator = DamageCalculator()
        self.team_validator = TeamValidator()
    
    def _get_type_effectiveness(self, attacker_type: str, defender_types: List[str]) -> float:
        """Calculate type effectiveness between attacker and defender."""
        query = "SELECT * FROM TypeChart WHERE attacking_type = ?"
        cursor = self.db.cursor()
        cursor.execute(query, (attacker_type,))
        type_chart = cursor.fetchone()
        
        effectiveness = 1.0
        for defender_type in defender_types:
            if defender_type in type_chart:
                effectiveness *= type_chart[defender_type]
        return effectiveness
    
    def _calculate_threat_score(self, pokemon: PokemonInstance, opponent_team: List[PokemonInstance]) -> float:
        """
        Calculate how threatening a Pokémon is to the opponent's team.
        Based on type effectiveness and move power.
        """
        threat_score = 0.0
        
        for opponent in opponent_team:
            # Check type effectiveness
            for move_type in set(move.split()[1] for move in pokemon.moves if ' ' in move):
                effectiveness = self._get_type_effectiveness(move_type, opponent.types)
                if effectiveness > 1.0:  # Super effective
                    threat_score += effectiveness
            
            # Check if we can outspeed
            if pokemon.calculate_stats()['spe'] > opponent.calculate_stats()['spe']:
                threat_score += 0.5
        
        return threat_score
    
    def _calculate_defensive_score(self, pokemon: PokemonInstance, opponent_team: List[PokemonInstance]) -> float:
        """
        Calculate how well a Pokémon can defend against the opponent's team.
        Based on type resistances and bulk.
        """
        defensive_score = 0.0
        
        for opponent in opponent_team:
            # Check type effectiveness against us
            for move_type in set(move.split()[1] for move in opponent.moves if ' ' in move):
                effectiveness = self._get_type_effectiveness(move_type, pokemon.types)
                if effectiveness < 1.0:  # Resistant
                    defensive_score += 1.0 / effectiveness
                elif effectiveness > 1.0:  # Weak
                    defensive_score -= effectiveness
            
            # Add bulk consideration
            defensive_score += (pokemon.calculate_stats()['hp'] + 
                              pokemon.calculate_stats()['def'] + 
                              pokemon.calculate_stats()['spd']) / 300.0
        
        return defensive_score
    
    def _get_pokemon_sets(self, pokemon_name: str) -> List[Dict]:
        """Get available sets for a Pokémon from the database."""
        query = """
        SELECT * FROM Gen7OUSets 
        WHERE pokemon_name = ? 
        ORDER BY CASE 
            WHEN source LIKE 'usage_stats_%' THEN 1 
            WHEN source = 'smogon_analysis_page' THEN 2 
            ELSE 3 
        END,
        usage_percentage DESC
        """
        cursor = self.db.cursor()
        cursor.execute(query, (pokemon_name,))
        return cursor.fetchall()
    
    def _convert_set_to_pokemon_instance(self, set_data: Dict) -> PokemonInstance:
        """Convert a set from the database into a PokemonInstance object."""
        return PokemonInstance(
            species=set_data['pokemon_name'],
            level=100,
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
    
    def build_team(self, 
                  strategy: str = "balanced",
                  core_pokemon: Optional[List[PokemonInstance]] = None,
                  banned_pokemon: Optional[List[str]] = None,
                  required_roles: Optional[Dict[str, int]] = None) -> Team:
        """
        Build a team based on the specified strategy and constraints.
        
        Args:
            strategy: Team building strategy ("balanced", "hyper_offense", "stall", "weather")
            core_pokemon: List of Pokémon that must be included in the team
            banned_pokemon: List of Pokémon species to exclude
            required_roles: Dictionary specifying required roles and their counts
            
        Returns:
            A Team object containing the built team
        """
        # Initialize constraints
        if banned_pokemon is None:
            banned_pokemon = []
        if required_roles is None:
            required_roles = self._get_default_roles(strategy)
        
        # Start with core Pokémon if provided
        team_pokemon = core_pokemon.copy() if core_pokemon else []
        
        # Build team based on strategy
        if strategy == "balanced":
            team_pokemon.extend(self._build_balanced_team(team_pokemon, banned_pokemon, required_roles))
        elif strategy == "hyper_offense":
            team_pokemon.extend(self._build_hyper_offense_team(team_pokemon, banned_pokemon, required_roles))
        elif strategy == "stall":
            team_pokemon.extend(self._build_stall_team(team_pokemon, banned_pokemon, required_roles))
        elif strategy == "weather":
            team_pokemon.extend(self._build_weather_team(team_pokemon, banned_pokemon, required_roles))
        
        # Create and validate team
        team = Team(team_pokemon)
        if not self.team_validator.validate_team(team):
            raise ValueError("Generated team failed validation")
        
        return team
    
    def _get_default_roles(self, strategy: str) -> Dict[str, int]:
        """Get default role requirements based on strategy."""
        if strategy == "balanced":
            return {
                "sweeper": 2,
                "wallbreaker": 1,
                "tank": 1,
                "support": 1,
                "hazard_setter": 1
            }
        elif strategy == "hyper_offense":
            return {
                "sweeper": 3,
                "wallbreaker": 2,
                "hazard_setter": 1
            }
        elif strategy == "stall":
            return {
                "tank": 3,
                "support": 2,
                "hazard_setter": 1
            }
        elif strategy == "weather":
            return {
                "sweeper": 2,
                "wallbreaker": 1,
                "tank": 1,
                "support": 1,
                "hazard_setter": 1
            }
        return {}
    
    def _build_balanced_team(self, 
                           current_team: List[PokemonInstance],
                           banned_pokemon: List[str],
                           required_roles: Dict[str, int]) -> List[PokemonInstance]:
        """Build a balanced team with good type coverage and role distribution."""
        team = current_team.copy()
        
        # Analyze current team
        current_roles = self._get_current_roles(team)
        current_coverage = self._get_current_coverage(team)
        
        # Fill missing roles
        while not self._roles_satisfied(current_roles, required_roles):
            next_role = self._get_next_role(current_roles, required_roles)
            candidate = self._find_best_candidate(next_role, team, banned_pokemon, current_coverage)
            if candidate:
                team.append(candidate)
                current_roles = self._get_current_roles(team)
                current_coverage = self._get_current_coverage(team)
        
        return team[len(current_team):]
    
    def _build_hyper_offense_team(self,
                                current_team: List[PokemonInstance],
                                banned_pokemon: List[str],
                                required_roles: Dict[str, int]) -> List[PokemonInstance]:
        """Build a hyper offense team focusing on offensive pressure."""
        team = current_team.copy()
        
        # Analyze current team
        current_roles = self._get_current_roles(team)
        current_coverage = self._get_current_coverage(team)
        
        # Prioritize offensive Pokémon
        while not self._roles_satisfied(current_roles, required_roles):
            next_role = self._get_next_role(current_roles, required_roles)
            candidate = self._find_best_candidate(next_role, team, banned_pokemon, current_coverage,
                                                offensive_bias=True)
            if candidate:
                team.append(candidate)
                current_roles = self._get_current_roles(team)
                current_coverage = self._get_current_coverage(team)
        
        return team[len(current_team):]
    
    def _build_stall_team(self,
                         current_team: List[PokemonInstance],
                         banned_pokemon: List[str],
                         required_roles: Dict[str, int]) -> List[PokemonInstance]:
        """Build a stall team focusing on defensive synergy."""
        team = current_team.copy()
        
        # Analyze current team
        current_roles = self._get_current_roles(team)
        current_coverage = self._get_current_coverage(team)
        
        # Prioritize defensive Pokémon
        while not self._roles_satisfied(current_roles, required_roles):
            next_role = self._get_next_role(current_roles, required_roles)
            candidate = self._find_best_candidate(next_role, team, banned_pokemon, current_coverage,
                                                defensive_bias=True)
            if candidate:
                team.append(candidate)
                current_roles = self._get_current_roles(team)
                current_coverage = self._get_current_coverage(team)
        
        return team[len(current_team):]
    
    def _build_weather_team(self,
                           current_team: List[PokemonInstance],
                           banned_pokemon: List[str],
                           required_roles: Dict[str, int]) -> List[PokemonInstance]:
        """Build a weather-based team with appropriate abusers."""
        team = current_team.copy()
        
        # Analyze current team
        current_roles = self._get_current_roles(team)
        current_coverage = self._get_current_coverage(team)
        
        # Ensure weather setter is present
        if not any(pokemon.ability in ["Drizzle", "Drought", "Sand Stream", "Snow Warning"] 
                  for pokemon in team):
            weather_setter = self._find_weather_setter(team, banned_pokemon)
            if weather_setter:
                team.append(weather_setter)
                current_roles = self._get_current_roles(team)
                current_coverage = self._get_current_coverage(team)
        
        # Fill remaining roles with weather abusers
        while not self._roles_satisfied(current_roles, required_roles):
            next_role = self._get_next_role(current_roles, required_roles)
            candidate = self._find_best_candidate(next_role, team, banned_pokemon, current_coverage,
                                                weather_abuser=True)
            if candidate:
                team.append(candidate)
                current_roles = self._get_current_roles(team)
                current_coverage = self._get_current_coverage(team)
        
        return team[len(current_team):]
    
    def _get_current_roles(self, team: List[PokemonInstance]) -> Dict[str, int]:
        """Get the current role distribution in the team."""
        roles = {
            "sweeper": 0,
            "wallbreaker": 0,
            "tank": 0,
            "support": 0,
            "hazard_setter": 0
        }
        
        for pokemon in team:
            role = self.synergy_analyzer._determine_pokemon_role(pokemon)
            roles[role] = roles.get(role, 0) + 1
        
        return roles
    
    def _get_current_coverage(self, team: List[PokemonInstance]) -> Dict[str, int]:
        """Get the current type coverage in the team."""
        return self.synergy_analyzer._get_team_type_coverage(Team(team))
    
    def _roles_satisfied(self, current: Dict[str, int], required: Dict[str, int]) -> bool:
        """Check if current role distribution satisfies requirements."""
        return all(current.get(role, 0) >= count for role, count in required.items())
    
    def _get_next_role(self, current: Dict[str, int], required: Dict[str, int]) -> str:
        """Get the next role that needs to be filled."""
        for role, count in required.items():
            if current.get(role, 0) < count:
                return role
        return "support"  # Default to support if all required roles are filled
    
    def _find_best_candidate(self,
                           role: str,
                           current_team: List[PokemonInstance],
                           banned_pokemon: List[str],
                           current_coverage: Dict[str, int],
                           offensive_bias: bool = False,
                           defensive_bias: bool = False,
                           weather_abuser: bool = False) -> Optional[PokemonInstance]:
        """
        Find the best Pokémon candidate for the given role and team context.
        This would typically query the database for potential candidates and score them.
        """
        # This is a placeholder - in practice, this would:
        # 1. Query the database for potential candidates
        # 2. Score them based on:
        #    - Role suitability
        #    - Type coverage
        #    - Synergy with current team
        #    - Offensive/defensive bias if specified
        #    - Weather abuse potential if specified
        # 3. Return the highest-scoring candidate
        return None
    
    def _find_weather_setter(self,
                           current_team: List[PokemonInstance],
                           banned_pokemon: List[str]) -> Optional[PokemonInstance]:
        """
        Find the best weather setter for the team.
        This would typically query the database for potential weather setters and score them.
        """
        # This is a placeholder - in practice, this would:
        # 1. Query the database for potential weather setters
        # 2. Score them based on:
        #    - Weather setting ability
        #    - Synergy with current team
        #    - Overall viability
        # 3. Return the highest-scoring candidate
        return None 