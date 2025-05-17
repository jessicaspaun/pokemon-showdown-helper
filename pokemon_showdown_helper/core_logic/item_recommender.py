"""
Item Recommender for suggesting optimal items based on matchup analysis.
"""
from typing import List, Dict, Optional
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team
from core_logic.matchup_analyzer import MatchupAnalyzer
from core_logic.damage_calculator import DamageCalculator

class ItemRecommender:
    """
    Recommends optimal items based on matchup analysis.
    """
    
    def __init__(self):
        self.matchup_analyzer = MatchupAnalyzer()
        self.damage_calculator = DamageCalculator()
    
    def recommend_items(self, user_pokemon: PokemonInstance, opponent_team: Team) -> Dict:
        """
        Recommend optimal items for a Pokémon against the opponent's team.
        
        Args:
            user_pokemon: The user's Pokémon to recommend items for
            opponent_team: The opponent's team
            
        Returns:
            Dictionary containing:
            - recommended_items: List of recommended items with reasoning
            - offensive_items: List of offensive items that could be useful
            - defensive_items: List of defensive items that could be useful
            - utility_items: List of utility items that could be useful
        """
        # Get matchup analysis
        analysis = self.matchup_analyzer.analyze_matchup(Team([user_pokemon]), opponent_team)
        
        return {
            'recommended_items': self._get_recommended_items(user_pokemon, opponent_team, analysis),
            'offensive_items': self._get_offensive_items(user_pokemon, opponent_team),
            'defensive_items': self._get_defensive_items(user_pokemon, opponent_team),
            'utility_items': self._get_utility_items(user_pokemon, opponent_team)
        }
    
    def _get_recommended_items(self, pokemon: PokemonInstance, opponent_team: Team, analysis: Dict) -> List[Dict]:
        """Get recommended items based on matchup analysis."""
        item_scores = []
        
        # Get all possible items for this Pokémon
        possible_items = self._get_possible_items(pokemon)
        
        for item in possible_items:
            score = 0
            reasoning = []
            
            # Check if it's an offensive item
            if self._is_offensive_item(item):
                score += self._score_offensive_item(item, pokemon, opponent_team)
                reasoning.append(self._get_offensive_reasoning(item, pokemon))
            
            # Check if it's a defensive item
            if self._is_defensive_item(item):
                score += self._score_defensive_item(item, pokemon, opponent_team)
                reasoning.append(self._get_defensive_reasoning(item, pokemon))
            
            # Check if it's a utility item
            if self._is_utility_item(item):
                score += self._score_utility_item(item, pokemon, opponent_team)
                reasoning.append(self._get_utility_reasoning(item, pokemon))
            
            item_scores.append({
                'item': item,
                'score': score,
                'reasoning': reasoning
            })
        
        # Sort by score and return top items
        item_scores.sort(key=lambda x: x['score'], reverse=True)
        return item_scores[:3]  # Return top 3 items
    
    def _get_offensive_items(self, pokemon: PokemonInstance, opponent_team: Team) -> List[Dict]:
        """Get offensive items that could be useful."""
        offensive_items = []
        
        for item in self._get_possible_items(pokemon):
            if self._is_offensive_item(item):
                offensive_items.append({
                    'item': item,
                    'reasoning': self._get_offensive_reasoning(item, pokemon)
                })
        
        return offensive_items
    
    def _get_defensive_items(self, pokemon: PokemonInstance, opponent_team: Team) -> List[Dict]:
        """Get defensive items that could be useful."""
        defensive_items = []
        
        for item in self._get_possible_items(pokemon):
            if self._is_defensive_item(item):
                defensive_items.append({
                    'item': item,
                    'reasoning': self._get_defensive_reasoning(item, pokemon)
                })
        
        return defensive_items
    
    def _get_utility_items(self, pokemon: PokemonInstance, opponent_team: Team) -> List[Dict]:
        """Get utility items that could be useful."""
        utility_items = []
        
        for item in self._get_possible_items(pokemon):
            if self._is_utility_item(item):
                utility_items.append({
                    'item': item,
                    'reasoning': self._get_utility_reasoning(item, pokemon)
                })
        
        return utility_items
    
    def _get_possible_items(self, pokemon: PokemonInstance) -> List[str]:
        """Get all possible items for a Pokémon."""
        # This would typically come from a database or configuration
        # For now, return a list of common items
        return [
            "Life Orb", "Choice Scarf", "Choice Band", "Choice Specs",
            "Leftovers", "Black Sludge", "Rocky Helmet", "Assault Vest",
            "Focus Sash", "Air Balloon", "Zap Plate", "Flame Plate",
            "Splash Plate", "Meadow Plate", "Icicle Plate", "Fist Plate",
            "Toxic Plate", "Earth Plate", "Sky Plate", "Mind Plate",
            "Insect Plate", "Stone Plate", "Spooky Plate", "Draco Plate",
            "Dread Plate", "Iron Plate", "Pixie Plate"
        ]
    
    def _is_offensive_item(self, item: str) -> bool:
        """Check if an item is offensive."""
        offensive_items = [
            "Life Orb", "Choice Scarf", "Choice Band", "Choice Specs",
            "Zap Plate", "Flame Plate", "Splash Plate", "Meadow Plate",
            "Icicle Plate", "Fist Plate", "Toxic Plate", "Earth Plate",
            "Sky Plate", "Mind Plate", "Insect Plate", "Stone Plate",
            "Spooky Plate", "Draco Plate", "Dread Plate", "Iron Plate",
            "Pixie Plate"
        ]
        return item in offensive_items
    
    def _is_defensive_item(self, item: str) -> bool:
        """Check if an item is defensive."""
        defensive_items = [
            "Leftovers", "Black Sludge", "Rocky Helmet", "Assault Vest",
            "Focus Sash"
        ]
        return item in defensive_items
    
    def _is_utility_item(self, item: str) -> bool:
        """Check if an item is utility."""
        utility_items = [
            "Air Balloon"
        ]
        return item in utility_items
    
    def _score_offensive_item(self, item: str, pokemon: PokemonInstance, opponent_team: Team) -> float:
        """Score an offensive item based on its effectiveness."""
        score = 0
        
        if item == "Life Orb":
            score += 1.0  # Universal damage boost
        elif item in ["Choice Scarf", "Choice Band", "Choice Specs"]:
            # Check if speed or attack boost would be useful
            if item == "Choice Scarf":
                score += 0.8  # Speed boost is generally useful
            else:
                score += 0.6  # Attack boost is situational
        elif "Plate" in item:
            # Check if the plate type matches any of the Pokémon's moves
            plate_type = item.split()[0].lower()
            for move in pokemon.moves:
                if ' ' in move and move.split()[1].lower() == plate_type:
                    score += 0.7
                    break
        
        return score
    
    def _score_defensive_item(self, item: str, pokemon: PokemonInstance, opponent_team: Team) -> float:
        """Score a defensive item based on its effectiveness."""
        score = 0
        
        if item == "Leftovers":
            score += 0.8  # Universal recovery
        elif item == "Black Sludge" and "Poison" in pokemon.types:
            score += 0.9  # Better than Leftovers for Poison types
        elif item == "Rocky Helmet":
            # Check if the Pokémon is physically defensive
            if pokemon.base_stats["def"] > 90:
                score += 0.7
        elif item == "Assault Vest":
            # Check if the Pokémon has high Special Defense
            if pokemon.base_stats["spd"] > 90:
                score += 0.8
        elif item == "Focus Sash":
            # Check if the Pokémon is frail
            if pokemon.base_stats["hp"] < 70 and (pokemon.base_stats["def"] < 70 or pokemon.base_stats["spd"] < 70):
                score += 0.9
        
        return score
    
    def _score_utility_item(self, item: str, pokemon: PokemonInstance, opponent_team: Team) -> float:
        """Score a utility item based on its effectiveness."""
        score = 0
        
        if item == "Air Balloon":
            # Check if the Pokémon is weak to Ground
            if "Ground" in self._get_team_weaknesses(Team([pokemon])):
                score += 0.9
        
        return score
    
    def _get_offensive_reasoning(self, item: str, pokemon: PokemonInstance) -> str:
        """Get reasoning for why an offensive item could be useful."""
        if item == "Life Orb":
            return "Universal damage boost for all moves"
        elif item == "Choice Scarf":
            return "Speed boost for revenge killing or sweeping"
        elif item in ["Choice Band", "Choice Specs"]:
            return "Attack boost for wallbreaking"
        elif "Plate" in item:
            plate_type = item.split()[0]
            return f"Boosts {plate_type} type moves"
        return "Offensive item for damage output"
    
    def _get_defensive_reasoning(self, item: str, pokemon: PokemonInstance) -> str:
        """Get reasoning for why a defensive item could be useful."""
        if item == "Leftovers":
            return "Passive recovery for longevity"
        elif item == "Black Sludge":
            return "Better recovery than Leftovers for Poison types"
        elif item == "Rocky Helmet":
            return "Chip damage against physical attackers"
        elif item == "Assault Vest":
            return "Special Defense boost for bulky attackers"
        elif item == "Focus Sash":
            return "Survive one hit for setup or revenge killing"
        return "Defensive item for survivability"
    
    def _get_utility_reasoning(self, item: str, pokemon: PokemonInstance) -> str:
        """Get reasoning for why a utility item could be useful."""
        if item == "Air Balloon":
            return "Temporary Ground immunity"
        return "Utility item for specific situations"
    
    def _get_team_weaknesses(self, team: Team) -> List[str]:
        """Get a list of types that the team is weak to."""
        # This would typically use the type chart and team composition
        # For now, return a simplified version
        weaknesses = []
        for pokemon in team.pokemon:
            if "Ground" in pokemon.types:
                weaknesses.append("Ground")
            if "Fire" in pokemon.types:
                weaknesses.append("Fire")
            if "Water" in pokemon.types:
                weaknesses.append("Water")
        return list(set(weaknesses))  # Remove duplicates 