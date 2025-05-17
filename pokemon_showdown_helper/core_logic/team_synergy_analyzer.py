"""
Team Synergy Analyzer for analyzing how well Pokémon work together in a team.
"""
from typing import List, Dict, Set, Tuple
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team
from core_logic.damage_calculator import DamageCalculator

class TeamSynergyAnalyzer:
    """
    Analyzes team synergy and provides recommendations for improvement.
    """
    
    def __init__(self):
        self.damage_calculator = DamageCalculator()
    
    def analyze_synergy(self, team: Team) -> Dict:
        """
        Analyze the synergy of a team and provide recommendations.
        
        Args:
            team: The team to analyze
            
        Returns:
            Dictionary containing:
            - type_synergy: Analysis of type coverage and weaknesses
            - role_synergy: Analysis of team roles and balance
            - defensive_synergy: Analysis of defensive coverage
            - offensive_synergy: Analysis of offensive coverage
            - recommendations: List of recommendations for improvement
        """
        return {
            'type_synergy': self._analyze_type_synergy(team),
            'role_synergy': self._analyze_role_synergy(team),
            'defensive_synergy': self._analyze_defensive_synergy(team),
            'offensive_synergy': self._analyze_offensive_synergy(team),
            'recommendations': self._generate_recommendations(team)
        }
    
    def _analyze_type_synergy(self, team: Team) -> Dict:
        """Analyze type coverage and weaknesses of the team."""
        type_coverage = self._get_team_type_coverage(team)
        type_weaknesses = self._get_team_type_weaknesses(team)
        type_resistances = self._get_team_type_resistances(team)
        
        return {
            'coverage': type_coverage,
            'weaknesses': type_weaknesses,
            'resistances': type_resistances,
            'analysis': self._analyze_type_balance(type_coverage, type_weaknesses, type_resistances)
        }
    
    def _analyze_role_synergy(self, team: Team) -> Dict:
        """Analyze the balance of team roles."""
        roles = {
            'sweeper': 0,
            'wallbreaker': 0,
            'tank': 0,
            'support': 0,
            'hazard_setter': 0,
            'hazard_remover': 0
        }
        
        for pokemon in team.pokemon:
            role = self._determine_pokemon_role(pokemon)
            roles[role] += 1
        
        return {
            'role_distribution': roles,
            'analysis': self._analyze_role_balance(roles)
        }
    
    def _analyze_defensive_synergy(self, team: Team) -> Dict:
        """Analyze defensive coverage and synergy."""
        defensive_cores = self._identify_defensive_cores(team)
        defensive_gaps = self._identify_defensive_gaps(team)
        
        return {
            'defensive_cores': defensive_cores,
            'defensive_gaps': defensive_gaps,
            'analysis': self._analyze_defensive_balance(defensive_cores, defensive_gaps)
        }
    
    def _analyze_offensive_synergy(self, team: Team) -> Dict:
        """Analyze offensive coverage and synergy."""
        offensive_cores = self._identify_offensive_cores(team)
        offensive_gaps = self._identify_offensive_gaps(team)
        
        return {
            'offensive_cores': offensive_cores,
            'offensive_gaps': offensive_gaps,
            'analysis': self._analyze_offensive_balance(offensive_cores, offensive_gaps)
        }
    
    def _get_team_type_coverage(self, team: Team) -> Dict[str, int]:
        """Get the offensive type coverage of the team."""
        coverage = {}
        for pokemon in team.pokemon:
            for move in pokemon.moves:
                if ' ' in move:  # If move has a type (e.g., "Thunderbolt Electric")
                    move_type = move.split()[1]
                    coverage[move_type] = coverage.get(move_type, 0) + 1
        return coverage
    
    def _get_team_type_weaknesses(self, team: Team) -> Dict[str, int]:
        """Get the type weaknesses of the team."""
        weaknesses = {}
        for pokemon in team.pokemon:
            for type_ in pokemon.types:
                # This would use the type chart to determine weaknesses
                # For now, using a simplified version
                if type_ == "Water":
                    weaknesses["Electric"] = weaknesses.get("Electric", 0) + 1
                    weaknesses["Grass"] = weaknesses.get("Grass", 0) + 1
                elif type_ == "Fire":
                    weaknesses["Water"] = weaknesses.get("Water", 0) + 1
                    weaknesses["Ground"] = weaknesses.get("Ground", 0) + 1
                    weaknesses["Rock"] = weaknesses.get("Rock", 0) + 1
                # Add more type weaknesses as needed
        return weaknesses
    
    def _get_team_type_resistances(self, team: Team) -> Dict[str, int]:
        """Get the type resistances of the team."""
        resistances = {}
        for pokemon in team.pokemon:
            for type_ in pokemon.types:
                # This would use the type chart to determine resistances
                # For now, using a simplified version
                if type_ == "Water":
                    resistances["Fire"] = resistances.get("Fire", 0) + 1
                    resistances["Water"] = resistances.get("Water", 0) + 1
                elif type_ == "Fire":
                    resistances["Fire"] = resistances.get("Fire", 0) + 1
                    resistances["Grass"] = resistances.get("Grass", 0) + 1
                # Add more type resistances as needed
        return resistances
    
    def _analyze_type_balance(self, coverage: Dict[str, int], weaknesses: Dict[str, int], resistances: Dict[str, int]) -> str:
        """Analyze the balance of type coverage and weaknesses."""
        analysis = []
        
        # Check for redundant coverage
        redundant_types = [t for t, count in coverage.items() if count > 2]
        if redundant_types:
            analysis.append(f"Redundant coverage in types: {', '.join(redundant_types)}")
        
        # Check for common weaknesses
        common_weaknesses = [t for t, count in weaknesses.items() if count >= 3]
        if common_weaknesses:
            analysis.append(f"Team is weak to: {', '.join(common_weaknesses)}")
        
        # Check for type coverage gaps
        important_types = ["Fire", "Water", "Electric", "Ground", "Flying", "Steel"]
        missing_types = [t for t in important_types if t not in coverage]
        if missing_types:
            analysis.append(f"Missing coverage for types: {', '.join(missing_types)}")
        
        return "\n".join(analysis) if analysis else "Team has good type balance"
    
    def _determine_pokemon_role(self, pokemon: PokemonInstance) -> str:
        """Determine the role of a Pokémon based on its stats and moves."""
        # This is a simplified version - in practice, this would be more sophisticated
        if pokemon.base_stats["spe"] > 100 and (pokemon.base_stats["atk"] > 100 or pokemon.base_stats["spa"] > 100):
            return "sweeper"
        elif pokemon.base_stats["atk"] > 120 or pokemon.base_stats["spa"] > 120:
            return "wallbreaker"
        elif pokemon.base_stats["def"] > 100 and pokemon.base_stats["spd"] > 100:
            return "tank"
        elif "Stealth Rock" in pokemon.moves or "Spikes" in pokemon.moves:
            return "hazard_setter"
        elif "Defog" in pokemon.moves or "Rapid Spin" in pokemon.moves:
            return "hazard_remover"
        else:
            return "support"
    
    def _analyze_role_balance(self, roles: Dict[str, int]) -> str:
        """Analyze the balance of team roles."""
        analysis = []
        
        if roles['sweeper'] + roles['wallbreaker'] < 2:
            analysis.append("Team lacks offensive presence")
        if roles['tank'] < 1:
            analysis.append("Team lacks defensive presence")
        if roles['hazard_setter'] == 0:
            analysis.append("Team lacks hazard setting")
        if roles['hazard_remover'] == 0:
            analysis.append("Team lacks hazard removal")
        
        return "\n".join(analysis) if analysis else "Team has good role balance"
    
    def _identify_defensive_cores(self, team: Team) -> List[Tuple[PokemonInstance, PokemonInstance]]:
        """Identify defensive cores in the team."""
        cores = []
        for i, pokemon1 in enumerate(team.pokemon):
            for pokemon2 in team.pokemon[i+1:]:
                if self._is_defensive_core(pokemon1, pokemon2):
                    cores.append((pokemon1, pokemon2))
        return cores
    
    def _is_defensive_core(self, pokemon1: PokemonInstance, pokemon2: PokemonInstance) -> bool:
        """Check if two Pokémon form a defensive core."""
        # This would use the type chart to determine if they cover each other's weaknesses
        # For now, using a simplified version
        types1 = set(pokemon1.types)
        types2 = set(pokemon2.types)
        
        # Example: Water + Grass is a classic defensive core
        if "Water" in types1 and "Grass" in types2:
            return True
        if "Water" in types2 and "Grass" in types1:
            return True
        
        return False
    
    def _identify_defensive_gaps(self, team: Team) -> List[str]:
        """Identify defensive gaps in the team."""
        gaps = []
        all_types = set()
        for pokemon in team.pokemon:
            all_types.update(pokemon.types)
        
        # Check for common types that the team can't handle
        if "Ground" not in all_types and "Flying" not in all_types:
            gaps.append("No Ground immunity")
        if "Fire" not in all_types and "Water" not in all_types:
            gaps.append("No Fire resistance")
        
        return gaps
    
    def _analyze_defensive_balance(self, cores: List[Tuple[PokemonInstance, PokemonInstance]], gaps: List[str]) -> str:
        """Analyze the defensive balance of the team."""
        analysis = []
        
        if not cores:
            analysis.append("No defensive cores identified")
        if gaps:
            analysis.append(f"Defensive gaps: {', '.join(gaps)}")
        
        return "\n".join(analysis) if analysis else "Team has good defensive balance"
    
    def _identify_offensive_cores(self, team: Team) -> List[Tuple[PokemonInstance, PokemonInstance]]:
        """Identify offensive cores in the team."""
        cores = []
        for i, pokemon1 in enumerate(team.pokemon):
            for pokemon2 in team.pokemon[i+1:]:
                if self._is_offensive_core(pokemon1, pokemon2):
                    cores.append((pokemon1, pokemon2))
        return cores
    
    def _is_offensive_core(self, pokemon1: PokemonInstance, pokemon2: PokemonInstance) -> bool:
        """Check if two Pokémon form an offensive core."""
        # This would analyze their move coverage and types
        # For now, using a simplified version
        types1 = set(pokemon1.types)
        types2 = set(pokemon2.types)
        
        # Example: Fire + Ground is a classic offensive core
        if "Fire" in types1 and "Ground" in types2:
            return True
        if "Fire" in types2 and "Ground" in types1:
            return True
        
        return False
    
    def _identify_offensive_gaps(self, team: Team) -> List[str]:
        """Identify offensive gaps in the team."""
        gaps = []
        coverage = self._get_team_type_coverage(team)
        
        # Check for common types that the team can't hit effectively
        if "Steel" not in coverage:
            gaps.append("No Steel coverage")
        if "Ground" not in coverage:
            gaps.append("No Ground coverage")
        
        return gaps
    
    def _analyze_offensive_balance(self, cores: List[Tuple[PokemonInstance, PokemonInstance]], gaps: List[str]) -> str:
        """Analyze the offensive balance of the team."""
        analysis = []
        
        if not cores:
            analysis.append("No offensive cores identified")
        if gaps:
            analysis.append(f"Offensive gaps: {', '.join(gaps)}")
        
        return "\n".join(analysis) if analysis else "Team has good offensive balance"
    
    def _generate_recommendations(self, team: Team) -> List[str]:
        """Generate recommendations for improving team synergy."""
        recommendations = []
        
        # Analyze type synergy
        type_synergy = self._analyze_type_synergy(team)
        if "Team is weak to" in type_synergy['analysis']:
            recommendations.append(f"Consider adding a Pokémon that resists: {type_synergy['analysis'].split('Team is weak to: ')[1]}")
        
        # Analyze role synergy
        role_synergy = self._analyze_role_synergy(team)
        if "Team lacks" in role_synergy['analysis']:
            recommendations.append(role_synergy['analysis'])
        
        # Analyze defensive synergy
        defensive_synergy = self._analyze_defensive_synergy(team)
        if "No defensive cores" in defensive_synergy['analysis']:
            recommendations.append("Consider adding a defensive core to improve team durability")
        if "Defensive gaps" in defensive_synergy['analysis']:
            recommendations.append(defensive_synergy['analysis'])
        
        # Analyze offensive synergy
        offensive_synergy = self._analyze_offensive_synergy(team)
        if "No offensive cores" in offensive_synergy['analysis']:
            recommendations.append("Consider adding an offensive core to improve team pressure")
        if "Offensive gaps" in offensive_synergy['analysis']:
            recommendations.append(offensive_synergy['analysis'])
        
        return recommendations 