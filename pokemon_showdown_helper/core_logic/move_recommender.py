"""
Move Recommender for suggesting optimal moves based on matchup analysis.
"""
from typing import List, Dict, Optional
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team
from core_logic.matchup_analyzer import MatchupAnalyzer
from core_logic.damage_calculator import DamageCalculator

class MoveRecommender:
    """
    Recommends optimal moves based on matchup analysis.
    """
    
    def __init__(self):
        self.matchup_analyzer = MatchupAnalyzer()
        self.damage_calculator = DamageCalculator()
    
    def recommend_moves(self, user_pokemon: PokemonInstance, opponent_team: Team) -> Dict:
        """
        Recommend optimal moves for a Pokémon against the opponent's team.
        
        Args:
            user_pokemon: The user's Pokémon to recommend moves for
            opponent_team: The opponent's team
            
        Returns:
            Dictionary containing:
            - recommended_moves: List of recommended moves with reasoning
            - coverage_analysis: Analysis of type coverage against opponent's team
            - priority_moves: List of priority moves that could be useful
            - utility_moves: List of utility moves that could be useful
        """
        # Get matchup analysis
        analysis = self.matchup_analyzer.analyze_matchup(Team([user_pokemon]), opponent_team)
        
        return {
            'recommended_moves': self._get_recommended_moves(user_pokemon, opponent_team, analysis),
            'coverage_analysis': self._analyze_coverage(user_pokemon, opponent_team),
            'priority_moves': self._get_priority_moves(user_pokemon, opponent_team),
            'utility_moves': self._get_utility_moves(user_pokemon, opponent_team)
        }
    
    def _get_recommended_moves(self, pokemon: PokemonInstance, opponent_team: Team, analysis: Dict) -> List[Dict]:
        """Get recommended moves based on matchup analysis."""
        move_scores = []
        
        for move in pokemon.moves:
            score = 0
            reasoning = []
            
            # Check type effectiveness against opponent's team
            if ' ' in move:  # Move with type
                move_type = move.split()[1]
                for opponent in opponent_team.pokemon:
                    effectiveness = self.damage_calculator._get_type_effectiveness(
                        move_type, opponent.types
                    )
                    if effectiveness > 1.0:
                        score += effectiveness
                        reasoning.append(f"Super effective against {opponent.species}")
                    elif effectiveness == 0:
                        score -= 1
                        reasoning.append(f"Immune against {opponent.species}")
            
            # Check if it's a priority move
            if self._is_priority_move(move):
                score += 0.5
                reasoning.append("Priority move for revenge killing")
            
            # Check if it's a utility move
            if self._is_utility_move(move):
                score += 0.3
                reasoning.append("Utility move for team support")
            
            move_scores.append({
                'move': move,
                'score': score,
                'reasoning': reasoning
            })
        
        # Sort by score and return top moves
        move_scores.sort(key=lambda x: x['score'], reverse=True)
        return move_scores[:4]  # Return top 4 moves
    
    def _analyze_coverage(self, pokemon: PokemonInstance, opponent_team: Team) -> Dict:
        """Analyze type coverage against opponent's team."""
        coverage = {}
        
        for move in pokemon.moves:
            if ' ' in move:  # Move with type
                move_type = move.split()[1]
                for opponent in opponent_team.pokemon:
                    effectiveness = self.damage_calculator._get_type_effectiveness(
                        move_type, opponent.types
                    )
                    if effectiveness > 1.0:
                        if move_type not in coverage:
                            coverage[move_type] = []
                        coverage[move_type].append(opponent.species)
        
        return coverage
    
    def _get_priority_moves(self, pokemon: PokemonInstance, opponent_team: Team) -> List[Dict]:
        """Get priority moves that could be useful."""
        priority_moves = []
        
        for move in pokemon.moves:
            if self._is_priority_move(move):
                priority_moves.append({
                    'move': move,
                    'reasoning': "Priority move for revenge killing or finishing off weakened Pokémon"
                })
        
        return priority_moves
    
    def _get_utility_moves(self, pokemon: PokemonInstance, opponent_team: Team) -> List[Dict]:
        """Get utility moves that could be useful."""
        utility_moves = []
        
        for move in pokemon.moves:
            if self._is_utility_move(move):
                utility_moves.append({
                    'move': move,
                    'reasoning': self._get_utility_reasoning(move, opponent_team)
                })
        
        return utility_moves
    
    def _is_priority_move(self, move: str) -> bool:
        """Check if a move has priority."""
        priority_moves = [
            "Extreme Speed", "Fake Out", "First Impression", "Ice Shard",
            "Mach Punch", "Quick Attack", "Shadow Sneak", "Sucker Punch",
            "Vacuum Wave", "Water Shuriken"
        ]
        return move in priority_moves
    
    def _is_utility_move(self, move: str) -> bool:
        """Check if a move is a utility move."""
        utility_moves = [
            "Defog", "Heal Bell", "Roost", "Recover", "Wish", "Toxic",
            "Will-O-Wisp", "Thunder Wave", "Stealth Rock", "Spikes",
            "Toxic Spikes", "Sticky Web", "Taunt", "Encore", "Haze"
        ]
        return move in utility_moves
    
    def _get_utility_reasoning(self, move: str, opponent_team: Team) -> str:
        """Get reasoning for why a utility move could be useful."""
        if move in ["Defog", "Rapid Spin"]:
            return "Hazard removal for team support"
        elif move in ["Heal Bell", "Aromatherapy"]:
            return "Status healing for team support"
        elif move in ["Roost", "Recover", "Wish"]:
            return "Recovery for longevity"
        elif move in ["Toxic", "Will-O-Wisp", "Thunder Wave"]:
            return "Status spreading for team support"
        elif move in ["Stealth Rock", "Spikes", "Toxic Spikes", "Sticky Web"]:
            return "Hazard setting for team support"
        elif move in ["Taunt", "Encore"]:
            return "Disruption for team support"
        elif move == "Haze":
            return "Stat reset for team support"
        return "Utility move for team support" 