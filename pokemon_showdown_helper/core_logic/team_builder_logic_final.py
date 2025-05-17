"""
Final version of the Team Builder Logic with advanced team building capabilities.
"""
from typing import List, Dict, Set, Tuple, Optional
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team
from core_logic.team_synergy_analyzer import TeamSynergyAnalyzer
from core_logic.matchup_analyzer import MatchupAnalyzer
from core_logic.damage_calculator import DamageCalculator
from core_logic.team_validator import TeamValidator
from core_logic.team_optimizer import TeamOptimizer
from data_scripts.database import get_db_connection

class TeamBuilderLogicFinal:
    """
    Advanced team builder that generates optimal teams based on various strategies,
    incorporating synergy analysis, threat coverage, role balance, and optimization.
    """
    
    def __init__(self):
        self.db = get_db_connection()
        self.synergy_analyzer = TeamSynergyAnalyzer()
        self.matchup_analyzer = MatchupAnalyzer()
        self.damage_calculator = DamageCalculator()
        self.team_validator = TeamValidator()
        self.team_optimizer = TeamOptimizer()
    
    def build_team(self,
                  strategy: str = "balanced",
                  core_pokemon: Optional[List[PokemonInstance]] = None,
                  opponent_team: Optional[Team] = None,
                  banned_pokemon: Optional[List[str]] = None,
                  required_roles: Optional[Dict[str, int]] = None,
                  optimization_goals: Optional[Dict[str, float]] = None) -> Team:
        """
        Build an optimized team based on the specified strategy and constraints.
        
        Args:
            strategy: Team building strategy ("balanced", "hyper_offense", "stall", "weather")
            core_pokemon: List of Pokémon that must be included in the team
            opponent_team: Optional opponent team for matchup-based optimization
            banned_pokemon: List of Pokémon species to exclude
            required_roles: Dictionary specifying required roles and their counts
            optimization_goals: Dictionary of optimization goals and their weights
            
        Returns:
            A Team object containing the built team
        """
        # Initialize constraints
        if banned_pokemon is None:
            banned_pokemon = []
        if required_roles is None:
            required_roles = self._get_default_roles(strategy)
        if optimization_goals is None:
            optimization_goals = {
                "type_coverage": 0.3,
                "role_balance": 0.3,
                "matchup_score": 0.4
            }
        
        # Start with core Pokémon if provided
        team_pokemon = core_pokemon.copy() if core_pokemon else []
        
        # Build initial team based on strategy
        if strategy == "balanced":
            team_pokemon.extend(self._build_balanced_team(team_pokemon, banned_pokemon, required_roles))
        elif strategy == "hyper_offense":
            team_pokemon.extend(self._build_hyper_offense_team(team_pokemon, banned_pokemon, required_roles))
        elif strategy == "stall":
            team_pokemon.extend(self._build_stall_team(team_pokemon, banned_pokemon, required_roles))
        elif strategy == "weather":
            team_pokemon.extend(self._build_weather_team(team_pokemon, banned_pokemon, required_roles))
        
        # Create initial team
        team = Team(team_pokemon)
        
        # Optimize the team
        if opponent_team:
            optimization_result = self.team_optimizer.optimize_team(
                team,
                opponent_team,
                optimization_goals
            )
            
            # Apply the best suggestions
            team = self._apply_optimization_suggestions(team, optimization_result)
        
        # Validate final team
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
    
    def _apply_optimization_suggestions(self, team: Team, optimization_result: Dict) -> Team:
        """Apply the best optimization suggestions to the team."""
        suggestions = optimization_result["suggestions"]
        improvement_scores = optimization_result["improvement_scores"]
        
        if not suggestions:
            return team
        
        # Sort suggestions by improvement score
        sorted_suggestions = sorted(
            suggestions,
            key=lambda s: improvement_scores.get(s["id"], 0),
            reverse=True
        )
        
        # Apply the best suggestion
        best_suggestion = sorted_suggestions[0]
        return Team(best_suggestion["suggested_team"])
    
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
        # Query database for potential candidates
        query = """
        SELECT p.* FROM Pokemon p
        JOIN Gen7OUSets s ON p.name = s.pokemon_name
        WHERE s.role = ?
        AND p.name NOT IN ?
        ORDER BY s.usage_percentage DESC
        """
        cursor = self.db.cursor()
        cursor.execute(query, (role, banned_pokemon))
        
        candidates = []
        for row in cursor.fetchall():
            candidate = self._create_pokemon_instance(row)
            
            # Score the candidate
            score = self._score_candidate(
                candidate,
                current_team,
                current_coverage,
                offensive_bias,
                defensive_bias,
                weather_abuser
            )
            
            if score > 0:
                candidates.append((candidate, score))
        
        # Return the highest-scoring candidate
        if candidates:
            return max(candidates, key=lambda x: x[1])[0]
        return None
    
    def _find_weather_setter(self,
                           current_team: List[PokemonInstance],
                           banned_pokemon: List[str]) -> Optional[PokemonInstance]:
        """Find the best weather setter for the team."""
        weather_abilities = ["Drizzle", "Drought", "Sand Stream", "Snow Warning"]
        
        query = """
        SELECT p.* FROM Pokemon p
        WHERE p.ability1 IN ?
        AND p.name NOT IN ?
        ORDER BY (
            SELECT usage_percentage 
            FROM Gen7OUSets s 
            WHERE s.pokemon_name = p.name 
            ORDER BY usage_percentage DESC 
            LIMIT 1
        ) DESC
        """
        cursor = self.db.cursor()
        cursor.execute(query, (weather_abilities, banned_pokemon))
        
        candidates = []
        for row in cursor.fetchall():
            candidate = self._create_pokemon_instance(row)
            
            # Score the candidate based on team synergy
            score = self._score_weather_setter(candidate, current_team)
            
            if score > 0:
                candidates.append((candidate, score))
        
        # Return the highest-scoring candidate
        if candidates:
            return max(candidates, key=lambda x: x[1])[0]
        return None
    
    def _score_candidate(self,
                        candidate: PokemonInstance,
                        current_team: List[PokemonInstance],
                        current_coverage: Dict[str, int],
                        offensive_bias: bool,
                        defensive_bias: bool,
                        weather_abuser: bool) -> float:
        """Score a candidate Pokémon based on various factors."""
        score = 0.0
        
        # Type coverage score
        coverage_score = self._calculate_coverage_score(candidate, current_coverage)
        score += coverage_score * 0.3
        
        # Role fit score
        role_score = self._calculate_role_fit_score(candidate)
        score += role_score * 0.3
        
        # Team synergy score
        synergy_score = self._calculate_synergy_score(candidate, current_team)
        score += synergy_score * 0.2
        
        # Offensive/defensive bias
        if offensive_bias:
            score += self._calculate_offensive_score(candidate) * 0.1
        elif defensive_bias:
            score += self._calculate_defensive_score(candidate) * 0.1
        
        # Weather abuse potential
        if weather_abuser:
            score += self._calculate_weather_abuse_score(candidate) * 0.1
        
        return score
    
    def _score_weather_setter(self,
                            candidate: PokemonInstance,
                            current_team: List[PokemonInstance]) -> float:
        """Score a weather setter candidate."""
        score = 0.0
        
        # Usage score
        query = """
        SELECT usage_percentage FROM Gen7OUSets
        WHERE pokemon_name = ?
        ORDER BY usage_percentage DESC
        LIMIT 1
        """
        cursor = self.db.cursor()
        cursor.execute(query, (candidate.species,))
        result = cursor.fetchone()
        if result:
            score += result[0] * 0.4
        
        # Team synergy score
        synergy_score = self._calculate_synergy_score(candidate, current_team)
        score += synergy_score * 0.6
        
        return score
    
    def _calculate_coverage_score(self,
                                candidate: PokemonInstance,
                                current_coverage: Dict[str, int]) -> float:
        """Calculate how well a candidate improves type coverage."""
        score = 0.0
        
        # Check offensive coverage
        for move in candidate.moves:
            if ' ' in move:
                move_type = move.split()[1]
                if current_coverage.get(move_type, 0) < 1.0:
                    score += 0.25
        
        # Check defensive coverage
        for type_name in candidate.types:
            if current_coverage.get(type_name, 0) < 1.0:
                score += 0.25
        
        return min(score, 1.0)
    
    def _calculate_role_fit_score(self, candidate: PokemonInstance) -> float:
        """Calculate how well a candidate fits its intended role."""
        query = """
        SELECT usage_percentage FROM Gen7OUSets
        WHERE pokemon_name = ?
        ORDER BY usage_percentage DESC
        LIMIT 1
        """
        cursor = self.db.cursor()
        cursor.execute(query, (candidate.species,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        return 0.0
    
    def _calculate_synergy_score(self,
                               candidate: PokemonInstance,
                               current_team: List[PokemonInstance]) -> float:
        """Calculate how well a candidate synergizes with the current team."""
        score = 0.0
        
        # Type synergy
        team_coverage = self._get_current_coverage(current_team)
        coverage_score = self._calculate_coverage_score(candidate, team_coverage)
        score += coverage_score * 0.5
        
        # Role synergy
        team_roles = self._get_current_roles(current_team)
        role_score = 1.0 - (team_roles.get(self.synergy_analyzer._determine_pokemon_role(candidate), 0) / 6.0)
        score += role_score * 0.5
        
        return score
    
    def _calculate_offensive_score(self, candidate: PokemonInstance) -> float:
        """Calculate a candidate's offensive potential."""
        stats = candidate.calculate_stats()
        
        # Consider both physical and special attack
        attack_score = max(stats['atk'], stats['spa']) / 150.0
        speed_score = stats['spe'] / 150.0
        
        return (attack_score + speed_score) / 2.0
    
    def _calculate_defensive_score(self, candidate: PokemonInstance) -> float:
        """Calculate a candidate's defensive potential."""
        stats = candidate.calculate_stats()
        
        # Consider HP and both defenses
        hp_score = stats['hp'] / 150.0
        defense_score = (stats['def'] + stats['spd']) / 300.0
        
        return (hp_score + defense_score) / 2.0
    
    def _calculate_weather_abuse_score(self, candidate: PokemonInstance) -> float:
        """Calculate a candidate's potential as a weather abuser."""
        score = 0.0
        
        # Check for weather-boosted moves
        weather_moves = {
            "Drizzle": ["Water"],
            "Drought": ["Fire"],
            "Sand Stream": ["Rock", "Ground", "Steel"],
            "Snow Warning": ["Ice"]
        }
        
        for ability, types in weather_moves.items():
            for move in candidate.moves:
                if ' ' in move:
                    move_type = move.split()[1]
                    if move_type in types:
                        score += 0.25
        
        return min(score, 1.0)
    
    def _create_pokemon_instance(self, row: Dict) -> PokemonInstance:
        """Create a PokemonInstance from a database row."""
        return PokemonInstance(
            species=row['name'],
            level=100,
            base_stats={
                'hp': row['hp'],
                'atk': row['atk'],
                'def': row['def'],
                'spa': row['spa'],
                'spd': row['spd'],
                'spe': row['spe']
            },
            iv={'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31},
            ev={'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0},
            nature='Timid',
            ability=row['ability1'],
            item='',
            types=[row['type1']] + ([row['type2']] if row['type2'] else []),
            moves=[]
        ) 