"""
Team Optimizer for improving team compositions based on various factors.
"""
from typing import List, Dict, Set, Tuple, Optional
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team
from core_logic.team_synergy_analyzer import TeamSynergyAnalyzer
from core_logic.matchup_analyzer import MatchupAnalyzer
from core_logic.damage_calculator import DamageCalculator
from core_logic.team_validator import TeamValidator
from data_scripts.database import get_db_session

class TeamOptimizer:
    """
    Optimizes team compositions by analyzing and improving various aspects
    such as type coverage, role distribution, and matchup effectiveness.
    """
    
    def __init__(self):
        self.synergy_analyzer = TeamSynergyAnalyzer()
        self.matchup_analyzer = MatchupAnalyzer()
        self.damage_calculator = DamageCalculator()
        self.team_validator = TeamValidator()
    
    def get_db_data(self, query: str, params: tuple = None) -> List[Dict]:
        """Get data from the database using a session."""
        with get_db_session() as session:
            result = session.execute(query, params or ())
            return [dict(row) for row in result]
    
    def optimize_team(self, 
                     team: Team,
                     opponent_team: Optional[Team] = None,
                     optimization_goals: Optional[Dict[str, float]] = None) -> Dict:
        """
        Optimize a team based on specified goals and opponent team.
        
        Args:
            team: The team to optimize
            opponent_team: Optional opponent team for matchup-based optimization
            optimization_goals: Dictionary of optimization goals and their weights
                (e.g., {"type_coverage": 0.3, "role_balance": 0.3, "matchup_score": 0.4})
        
        Returns:
            Dictionary containing optimization results and suggestions
        """
        if optimization_goals is None:
            optimization_goals = {
                "type_coverage": 0.3,
                "role_balance": 0.3,
                "matchup_score": 0.4
            }
        
        # Analyze current team state
        current_analysis = self._analyze_current_team(team, opponent_team)
        
        # Generate optimization suggestions
        suggestions = self._generate_suggestions(
            team, 
            current_analysis,
            optimization_goals
        )
        
        # Calculate improvement scores
        improvement_scores = self._calculate_improvement_scores(
            current_analysis,
            suggestions
        )
        
        return {
            "current_analysis": current_analysis,
            "suggestions": suggestions,
            "improvement_scores": improvement_scores
        }
    
    def _analyze_current_team(self, team: Team, opponent_team: Optional[Team]) -> Dict:
        """Analyze the current state of the team."""
        # Get synergy analysis
        synergy_analysis = self.synergy_analyzer.analyze_synergy(team)
        
        # Get matchup analysis if opponent team is provided
        matchup_analysis = None
        if opponent_team:
            matchup_analysis = self.matchup_analyzer.analyze_matchup(team, opponent_team)
        
        # Calculate type coverage score
        type_coverage = self._calculate_type_coverage_score(team)
        
        # Calculate role balance score
        role_balance = self._calculate_role_balance_score(team)
        
        return {
            "synergy_analysis": synergy_analysis,
            "matchup_analysis": matchup_analysis,
            "type_coverage_score": type_coverage,
            "role_balance_score": role_balance
        }
    
    def _generate_suggestions(self,
                            team: Team,
                            current_analysis: Dict,
                            optimization_goals: Dict[str, float]) -> List[Dict]:
        """Generate optimization suggestions based on current analysis."""
        suggestions = []
        
        # Type coverage suggestions
        if optimization_goals.get("type_coverage", 0) > 0:
            type_suggestions = self._generate_type_suggestions(team, current_analysis)
            suggestions.extend(type_suggestions)
        
        # Role balance suggestions
        if optimization_goals.get("role_balance", 0) > 0:
            role_suggestions = self._generate_role_suggestions(team, current_analysis)
            suggestions.extend(role_suggestions)
        
        # Matchup-based suggestions
        if optimization_goals.get("matchup_score", 0) > 0 and current_analysis["matchup_analysis"]:
            matchup_suggestions = self._generate_matchup_suggestions(
                team,
                current_analysis["matchup_analysis"]
            )
            suggestions.extend(matchup_suggestions)
        
        return suggestions
    
    def _calculate_improvement_scores(self,
                                   current_analysis: Dict,
                                   suggestions: List[Dict]) -> Dict[str, float]:
        """Calculate potential improvement scores for each suggestion."""
        improvement_scores = {}
        
        for suggestion in suggestions:
            score = 0.0
            
            # Type coverage improvement
            if "type_coverage" in suggestion:
                current_score = current_analysis["type_coverage_score"]
                new_score = self._calculate_type_coverage_score(
                    Team(suggestion["suggested_team"])
                )
                score += (new_score - current_score) * 0.3
            
            # Role balance improvement
            if "role_balance" in suggestion:
                current_score = current_analysis["role_balance_score"]
                new_score = self._calculate_role_balance_score(
                    Team(suggestion["suggested_team"])
                )
                score += (new_score - current_score) * 0.3
            
            # Matchup improvement
            if "matchup_improvement" in suggestion:
                score += suggestion["matchup_improvement"] * 0.4
            
            improvement_scores[suggestion["id"]] = score
        
        return improvement_scores
    
    def _calculate_type_coverage_score(self, team: Team) -> float:
        """Calculate a score for the team's type coverage."""
        coverage = self.synergy_analyzer._get_team_type_coverage(team)
        
        # Calculate offensive coverage
        offensive_score = sum(
            effectiveness for effectiveness in coverage.values()
            if effectiveness > 1.0
        ) / len(coverage)
        
        # Calculate defensive coverage
        defensive_score = sum(
            1.0 / effectiveness for effectiveness in coverage.values()
            if effectiveness < 1.0
        ) / len(coverage)
        
        return (offensive_score + defensive_score) / 2.0
    
    def _calculate_role_balance_score(self, team: Team) -> float:
        """Calculate a score for the team's role balance."""
        roles = self.synergy_analyzer._get_team_roles(team)
        
        # Ideal role distribution
        ideal_distribution = {
            "sweeper": 2,
            "wallbreaker": 1,
            "tank": 1,
            "support": 1,
            "hazard_setter": 1
        }
        
        # Calculate deviation from ideal
        deviation = sum(
            abs(roles.get(role, 0) - ideal_distribution[role])
            for role in ideal_distribution
        )
        
        # Convert to score (lower deviation = higher score)
        return 1.0 - (deviation / (len(ideal_distribution) * 2))
    
    def _generate_type_suggestions(self, team: Team, current_analysis: Dict) -> List[Dict]:
        """Generate suggestions for improving type coverage."""
        suggestions = []
        
        # Get current type coverage
        current_coverage = self.synergy_analyzer._get_team_type_coverage(team)
        
        # Find missing or weak coverage
        weak_coverage = {
            type_name: effectiveness
            for type_name, effectiveness in current_coverage.items()
            if effectiveness < 1.0
        }
        
        # Generate suggestions for each weak coverage
        for type_name, effectiveness in weak_coverage.items():
            # Find Pokémon that can improve this coverage
            candidates = self._find_type_coverage_candidates(type_name, team)
            
            for candidate in candidates:
                suggestions.append({
                    "id": f"type_{type_name}_{candidate.species}",
                    "type": "type_coverage",
                    "description": f"Add {candidate.species} to improve {type_name} coverage",
                    "suggested_team": team.pokemon + [candidate],
                    "improvement": 1.0 - effectiveness
                })
        
        return suggestions
    
    def _generate_role_suggestions(self, team: Team, current_analysis: Dict) -> List[Dict]:
        """Generate suggestions for improving role balance."""
        suggestions = []
        
        # Get current role distribution
        current_roles = self.synergy_analyzer._get_team_roles(team)
        
        # Find missing or underrepresented roles
        ideal_distribution = {
            "sweeper": 2,
            "wallbreaker": 1,
            "tank": 1,
            "support": 1,
            "hazard_setter": 1
        }
        
        for role, ideal_count in ideal_distribution.items():
            current_count = current_roles.get(role, 0)
            if current_count < ideal_count:
                # Find Pokémon that can fill this role
                candidates = self._find_role_candidates(role, team)
                
                for candidate in candidates:
                    suggestions.append({
                        "id": f"role_{role}_{candidate.species}",
                        "type": "role_balance",
                        "description": f"Add {candidate.species} as a {role}",
                        "suggested_team": team.pokemon + [candidate],
                        "improvement": (ideal_count - current_count) / ideal_count
                    })
        
        return suggestions
    
    def _generate_matchup_suggestions(self,
                                    team: Team,
                                    matchup_analysis: Dict) -> List[Dict]:
        """Generate suggestions for improving matchup effectiveness."""
        suggestions = []
        
        # Get key threats from opponent
        key_threats = matchup_analysis.get("key_threats", [])
        
        for threat in key_threats:
            # Find Pokémon that can handle this threat
            candidates = self._find_threat_counter_candidates(threat, team)
            
            for candidate in candidates:
                suggestions.append({
                    "id": f"matchup_{threat.species}_{candidate.species}",
                    "type": "matchup_improvement",
                    "description": f"Add {candidate.species} to handle {threat.species}",
                    "suggested_team": team.pokemon + [candidate],
                    "matchup_improvement": self._calculate_matchup_improvement(
                        candidate, threat
                    )
                })
        
        return suggestions
    
    def _find_type_coverage_candidates(self,
                                     type_name: str,
                                     current_team: Team) -> List[PokemonInstance]:
        """Find Pokémon candidates that can provide the specified type coverage."""
        # Query database for Pokémon with this type
        query = """
        SELECT p.* FROM Pokemon p
        WHERE p.type1 = ? OR p.type2 = ?
        AND p.name NOT IN (
            SELECT species FROM TeamMembers
            WHERE team_id = ?
        )
        """
        cursor = self.get_db_data(query, (type_name, type_name, current_team.id))
        
        candidates = []
        for row in cursor:
            # Convert to PokemonInstance
            candidate = self._create_pokemon_instance(row)
            if self.team_validator.validate_pokemon(candidate):
                candidates.append(candidate)
        
        return candidates
    
    def _find_role_candidates(self,
                            role: str,
                            current_team: Team) -> List[PokemonInstance]:
        """Find Pokémon candidates that can fulfill the specified role."""
        # Query database for Pokémon that typically fulfill this role
        query = """
        SELECT p.* FROM Pokemon p
        JOIN Gen7OUSets s ON p.name = s.pokemon_name
        WHERE s.role = ?
        AND p.name NOT IN (
            SELECT species FROM TeamMembers
            WHERE team_id = ?
        )
        ORDER BY s.usage_percentage DESC
        """
        cursor = self.get_db_data(query, (role, current_team.id))
        
        candidates = []
        for row in cursor:
            # Convert to PokemonInstance
            candidate = self._create_pokemon_instance(row)
            if self.team_validator.validate_pokemon(candidate):
                candidates.append(candidate)
        
        return candidates
    
    def _find_threat_counter_candidates(self,
                                      threat: PokemonInstance,
                                      current_team: Team) -> List[PokemonInstance]:
        """Find Pokémon candidates that can counter the specified threat."""
        # Get threat's types and moves
        threat_types = threat.types
        threat_moves = threat.moves
        
        # Query database for Pokémon that resist the threat's types
        query = """
        SELECT p.* FROM Pokemon p
        WHERE p.name NOT IN (
            SELECT species FROM TeamMembers
            WHERE team_id = ?
        )
        """
        cursor = self.get_db_data(query, (current_team.id,))
        
        candidates = []
        for row in cursor:
            candidate = self._create_pokemon_instance(row)
            
            # Check if candidate can handle the threat
            if self._can_handle_threat(candidate, threat):
                candidates.append(candidate)
        
        return candidates
    
    def _can_handle_threat(self,
                          candidate: PokemonInstance,
                          threat: PokemonInstance) -> bool:
        """Check if a candidate Pokémon can handle a threat."""
        # Check type effectiveness
        for move in threat.moves:
            move_type = move.split()[1] if ' ' in move else "Normal"
            effectiveness = self.damage_calculator.calculate_type_effectiveness(
                move_type,
                candidate.types
            )
            if effectiveness >= 2.0:  # Super effective
                return False
        
        # Check if candidate can outspeed and OHKO
        candidate_stats = candidate.calculate_stats()
        threat_stats = threat.calculate_stats()
        
        if candidate_stats['spe'] > threat_stats['spe']:
            # Check if candidate can OHKO
            for move in candidate.moves:
                damage = self.damage_calculator.calculate_damage(
                    candidate,
                    threat,
                    move
                )
                if damage >= threat_stats['hp']:
                    return True
        
        return False
    
    def _calculate_matchup_improvement(self,
                                     candidate: PokemonInstance,
                                     threat: PokemonInstance) -> float:
        """Calculate how much a candidate improves the matchup against a threat."""
        improvement = 0.0
        
        # Type effectiveness improvement
        for move in threat.moves:
            move_type = move.split()[1] if ' ' in move else "Normal"
            effectiveness = self.damage_calculator.calculate_type_effectiveness(
                move_type,
                candidate.types
            )
            if effectiveness < 1.0:  # Resistant
                improvement += 1.0 - effectiveness
        
        # Speed and damage improvement
        candidate_stats = candidate.calculate_stats()
        threat_stats = threat.calculate_stats()
        
        if candidate_stats['spe'] > threat_stats['spe']:
            improvement += 0.5
        
        for move in candidate.moves:
            damage = self.damage_calculator.calculate_damage(
                candidate,
                threat,
                move
            )
            if damage >= threat_stats['hp']:
                improvement += 1.0
        
        return min(improvement / 3.0, 1.0)  # Normalize to 0-1 range
    
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