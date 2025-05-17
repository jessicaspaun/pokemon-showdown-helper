"""
Strategy Generator for providing strategic advice based on matchup analysis.
"""
from typing import List, Dict, Optional
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team
from core_logic.matchup_analyzer import MatchupAnalyzer

class StrategyGenerator:
    """
    Generates strategic advice based on matchup analysis.
    """
    
    def __init__(self):
        self.matchup_analyzer = MatchupAnalyzer()
    
    def generate_strategy(self, user_team: Team, opponent_team: Team) -> Dict:
        """
        Generate strategic advice based on matchup analysis.
        
        Args:
            user_team: Team object representing user's team
            opponent_team: Team object representing opponent's team
            
        Returns:
            Dictionary containing:
            - suggested_lead: Recommended lead Pokémon and reasoning
            - key_threats_to_handle: List of opponent's threats to watch out for
            - win_conditions: List of win conditions for the user's team
            - general_strategy: General strategic advice
        """
        # Get matchup analysis
        analysis = self.matchup_analyzer.analyze_matchup(user_team, opponent_team)
        
        return {
            'suggested_lead': self._suggest_lead(user_team, opponent_team, analysis),
            'key_threats_to_handle': self._identify_key_threats_to_handle(analysis),
            'win_conditions': self._identify_win_conditions(user_team, opponent_team, analysis),
            'general_strategy': self._generate_general_strategy(analysis)
        }
    
    def _suggest_lead(self, user_team: Team, opponent_team: Team, analysis: Dict) -> Dict:
        """Suggest a lead Pokémon based on matchup analysis."""
        lead_scores = []
        
        for pokemon in user_team.pokemon:
            score = 0
            reasoning = []
            
            # Check type matchups against opponent's team
            for opponent in opponent_team.pokemon:
                for move in pokemon.moves:
                    if ' ' in move:  # Move with type
                        move_type = move.split()[1]
                        effectiveness = self.matchup_analyzer.damage_calculator._get_type_effectiveness(
                            move_type, opponent.types
                        )
                        if effectiveness > 1.0:
                            score += effectiveness
                            reasoning.append(f"Super effective against {opponent.species} with {move}")
            
            # Check speed advantage
            pokemon_speed = pokemon.calculate_stats()['spe']
            for opponent in opponent_team.pokemon:
                opponent_speed = opponent.calculate_stats()['spe']
                if pokemon_speed > opponent_speed:
                    score += 0.5
                    reasoning.append(f"Outspeeds {opponent.species}")
            
            # Check if it can handle common leads
            if any(pokemon.species in threat['defender'] for threat in analysis['key_threats']):
                score += 1
                reasoning.append("Can handle key threats")
            
            lead_scores.append({
                'pokemon': pokemon.species,
                'score': score,
                'reasoning': reasoning
            })
        
        # Sort by score and return the best lead
        lead_scores.sort(key=lambda x: x['score'], reverse=True)
        best_lead = lead_scores[0]
        
        return {
            'pokemon': best_lead['pokemon'],
            'reasoning': best_lead['reasoning']
        }
    
    def _identify_key_threats_to_handle(self, analysis: Dict) -> List[Dict]:
        """Identify key threats from the opponent's team that need to be handled."""
        threats_to_handle = []
        
        # Filter threats to only those from opponent's team
        opponent_threats = [
            threat for threat in analysis['key_threats']
            if any(pokemon.species == threat['attacker'] for pokemon in analysis['opponent_team'])
        ]
        
        for threat in opponent_threats:
            threats_to_handle.append({
                'pokemon': threat['attacker'],
                'move': threat['move'],
                'ko_type': threat['ko_type'],
                'targets': [
                    defender for defender in analysis['user_team']
                    if defender.species == threat['defender']
                ]
            })
        
        return threats_to_handle
    
    def _identify_win_conditions(self, user_team: Team, opponent_team: Team, analysis: Dict) -> List[Dict]:
        """Identify potential win conditions for the user's team."""
        win_conditions = []
        
        # Check for sweepers
        for pokemon in user_team.pokemon:
            if self._is_sweeper(pokemon, opponent_team, analysis):
                win_conditions.append({
                    'type': 'sweep',
                    'pokemon': pokemon.species,
                    'reasoning': f"{pokemon.species} can sweep with proper setup"
                })
        
        # Check for wallbreakers
        for pokemon in user_team.pokemon:
            if self._is_wallbreaker(pokemon, opponent_team, analysis):
                win_conditions.append({
                    'type': 'wallbreak',
                    'pokemon': pokemon.species,
                    'reasoning': f"{pokemon.species} can break through opponent's defensive core"
                })
        
        return win_conditions
    
    def _is_sweeper(self, pokemon: PokemonInstance, opponent_team: Team, analysis: Dict) -> bool:
        """Check if a Pokémon has sweeping potential."""
        # Check speed
        pokemon_speed = pokemon.calculate_stats()['spe']
        if pokemon_speed < 100:  # Too slow to sweep
            return False
        
        # Check if it can OHKO/2HKO most of the opponent's team
        ko_count = 0
        for opponent in opponent_team.pokemon:
            for move in pokemon.moves:
                if ' ' in move:  # Move with type
                    move_type = move.split()[1]
                    effectiveness = self.matchup_analyzer.damage_calculator._get_type_effectiveness(
                        move_type, opponent.types
                    )
                    if effectiveness > 1.0:
                        ko_count += 1
                        break
        
        return ko_count >= len(opponent_team.pokemon) * 0.7  # Can handle 70% of the team
    
    def _is_wallbreaker(self, pokemon: PokemonInstance, opponent_team: Team, analysis: Dict) -> bool:
        """Check if a Pokémon has wallbreaking potential."""
        # Check attack stats
        stats = pokemon.calculate_stats()
        if stats['atk'] < 100 and stats['spa'] < 100:  # Too weak to break walls
            return False
        
        # Check if it can hit most of the opponent's team super effectively
        super_effective_count = 0
        for opponent in opponent_team.pokemon:
            for move in pokemon.moves:
                if ' ' in move:  # Move with type
                    move_type = move.split()[1]
                    effectiveness = self.matchup_analyzer.damage_calculator._get_type_effectiveness(
                        move_type, opponent.types
                    )
                    if effectiveness > 1.0:
                        super_effective_count += 1
                        break
        
        return super_effective_count >= len(opponent_team.pokemon) * 0.5  # Can hit 50% of the team super effectively
    
    def _generate_general_strategy(self, analysis: Dict) -> List[str]:
        """Generate general strategic advice based on matchup analysis."""
        strategy = []
        
        # Add advice based on type matchups
        user_weaknesses = analysis['type_matchup_summary']['user_team']['weaknesses']
        if user_weaknesses:
            common_weakness = max(user_weaknesses.items(), key=lambda x: x[1])[0]
            strategy.append(f"Watch out for {common_weakness} type moves from the opponent")
        
        # Add advice based on speed tiers
        speed_tiers = analysis['speed_comparison']
        user_speed_advantage = sum(1 for entry in speed_tiers if entry['team'] == 'user')
        if user_speed_advantage > len(speed_tiers) / 2:
            strategy.append("You have a speed advantage - consider playing aggressively")
        else:
            strategy.append("Opponent has speed advantage - play carefully and use priority moves")
        
        # Add advice based on vulnerabilities
        vulnerabilities = analysis['vulnerabilities']
        if vulnerabilities['common_weaknesses']:
            strategy.append(f"Your team is weak to: {', '.join(vulnerabilities['common_weaknesses'])}")
        if vulnerabilities['coverage_gaps']:
            strategy.append(f"Consider adding coverage for: {', '.join(vulnerabilities['coverage_gaps'])}")
        
        return strategy 