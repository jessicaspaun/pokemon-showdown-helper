"""
Module for optimizing EV spreads for Pokémon in Gen 7 OU.
"""
from typing import List, Dict, Optional, Tuple, Set
import numpy as np
from dataclasses import dataclass
from core_logic.pokemon_object import PokemonInstance
from core_logic.damage_calculator import DamageCalculator
from data_scripts.database import get_db_connection

@dataclass
class EVOptimizationGoal:
    """Represents a goal for EV optimization."""
    type: str  # 'survive', 'ohko', '2hko', 'outspeed', 'custom'
    target_pokemon: Optional[PokemonInstance] = None  # For survive/ohko/2hko goals
    move: Optional[str] = None  # For survive/ohko/2hko goals
    stat: Optional[str] = None  # For outspeed/custom goals
    value: Optional[float] = None  # For custom goals
    priority: int = 1  # Higher priority goals are optimized first

class EVOptimizer:
    """
    Optimizes EV spreads for Pokémon based on specific goals.
    
    The optimizer uses a combination of:
    1. Linear programming for basic optimization
    2. Heuristic search for complex scenarios
    3. Role-based optimization for common builds
    """
    
    def __init__(self):
        self.db = get_db_connection()
        self.damage_calculator = DamageCalculator()
        self.max_evs = 510
        self.max_stat_evs = 252
        
        # Load special moves from database
        self.special_moves = self._load_special_moves()
    
    def _load_special_moves(self) -> Set[str]:
        """Load special moves from the database."""
        cursor = self.db.cursor()
        cursor.execute("SELECT name FROM moves WHERE category = 'Special'")
        return {row[0] for row in cursor.fetchall()}
    
    def optimize_evs(
        self,
        pokemon: PokemonInstance,
        goals: List[EVOptimizationGoal],
        fixed_evs: Optional[Dict[str, int]] = None
    ) -> Dict[str, int]:
        """
        Optimize EVs for a Pokémon based on given goals.
        
        Args:
            pokemon: The Pokémon to optimize EVs for
            goals: List of optimization goals
            fixed_evs: Dictionary of EVs that should remain fixed
            
        Returns:
            Dictionary of optimized EVs
        """
        # Sort goals by priority
        goals.sort(key=lambda g: g.priority, reverse=True)
        
        # Initialize EVs
        evs = fixed_evs.copy() if fixed_evs else {
            'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0
        }
        
        # Track remaining EVs
        remaining_evs = self.max_evs - sum(evs.values())
        
        # Process each goal
        for goal in goals:
            if remaining_evs <= 0:
                break
                
            if goal.type == 'survive':
                evs = self._optimize_survival(
                    pokemon, goal.target_pokemon, goal.move, evs, remaining_evs
                )
            elif goal.type == 'ohko':
                evs = self._optimize_ohko(
                    pokemon, goal.target_pokemon, goal.move, evs, remaining_evs
                )
            elif goal.type == '2hko':
                evs = self._optimize_2hko(
                    pokemon, goal.target_pokemon, goal.move, evs, remaining_evs
                )
            elif goal.type == 'outspeed':
                evs = self._optimize_speed(
                    pokemon, goal.target_pokemon, evs, remaining_evs
                )
            elif goal.type == 'custom':
                evs = self._optimize_custom(
                    pokemon, goal.stat, goal.value, evs, remaining_evs
                )
            
            # Update remaining EVs
            remaining_evs = self.max_evs - sum(evs.values())
        
        return evs
    
    def _optimize_survival(
        self,
        pokemon: PokemonInstance,
        attacker: PokemonInstance,
        move: str,
        current_evs: Dict[str, int],
        remaining_evs: int
    ) -> Dict[str, int]:
        """Optimize EVs to survive a specific hit."""
        evs = current_evs.copy()
        
        # Calculate damage with current EVs
        damage = self.damage_calculator.calculate_damage(
            attacker, pokemon, move, attacker.ev, evs
        )
        
        # If already surviving, return current EVs
        if damage < pokemon.calculate_hp(evs['hp']):
            return evs
        
        # Try to optimize HP and relevant defense stat
        defense_stat = 'spd' if move in self.special_moves else 'def'
        
        # Calculate required EVs for survival
        required_hp = self._calculate_required_hp_evs(pokemon, damage)
        required_def = self._calculate_required_def_evs(pokemon, damage, defense_stat)
        
        # Allocate EVs
        if required_hp + required_def <= remaining_evs:
            evs['hp'] = min(required_hp, self.max_stat_evs)
            evs[defense_stat] = min(required_def, self.max_stat_evs)
        else:
            # Distribute EVs proportionally
            total_required = required_hp + required_def
            evs['hp'] = min(int(remaining_evs * required_hp / total_required), self.max_stat_evs)
            evs[defense_stat] = min(int(remaining_evs * required_def / total_required), self.max_stat_evs)
        
        return evs
    
    def _optimize_ohko(
        self,
        pokemon: PokemonInstance,
        target: PokemonInstance,
        move: str,
        current_evs: Dict[str, int],
        remaining_evs: int
    ) -> Dict[str, int]:
        """Optimize EVs to achieve an OHKO."""
        evs = current_evs.copy()
        
        # Calculate damage with current EVs
        damage = self.damage_calculator.calculate_damage(
            pokemon, target, move, evs, target.ev
        )
        
        # If already OHKOing, return current EVs
        if damage >= target.calculate_hp(target.ev['hp']):
            return evs
        
        # Determine attack stat to optimize
        attack_stat = 'spa' if move in self.special_moves else 'atk'
        
        # Calculate required EVs for OHKO
        required_atk = self._calculate_required_atk_evs(pokemon, target, move, attack_stat)
        
        # Allocate EVs
        if required_atk <= remaining_evs:
            evs[attack_stat] = min(required_atk, self.max_stat_evs)
        else:
            evs[attack_stat] = min(remaining_evs, self.max_stat_evs)
        
        return evs
    
    def _optimize_2hko(
        self,
        pokemon: PokemonInstance,
        target: PokemonInstance,
        move: str,
        current_evs: Dict[str, int],
        remaining_evs: int
    ) -> Dict[str, int]:
        """Optimize EVs to achieve a 2HKO."""
        evs = current_evs.copy()
        
        # Calculate damage with current EVs
        damage = self.damage_calculator.calculate_damage(
            pokemon, target, move, evs, target.ev
        )
        
        # If already 2HKOing, return current EVs
        if damage >= target.calculate_hp(target.ev['hp']) / 2:
            return evs
        
        # Determine attack stat to optimize
        attack_stat = 'spa' if move in self.special_moves else 'atk'
        
        # Calculate required EVs for 2HKO
        required_atk = self._calculate_required_atk_evs(
            pokemon, target, move, attack_stat, is_2hko=True
        )
        
        # Allocate EVs
        if required_atk <= remaining_evs:
            evs[attack_stat] = min(required_atk, self.max_stat_evs)
        else:
            evs[attack_stat] = min(remaining_evs, self.max_stat_evs)
        
        return evs
    
    def _optimize_speed(
        self,
        pokemon: PokemonInstance,
        target: PokemonInstance,
        current_evs: Dict[str, int],
        remaining_evs: int
    ) -> Dict[str, int]:
        """Optimize EVs to outspeed a target Pokémon."""
        evs = current_evs.copy()
        
        # Calculate required speed EVs
        target_speed = target.calculate_speed(target.ev['spe'])
        required_speed = self._calculate_required_speed_evs(pokemon, target_speed)
        
        # Allocate EVs
        if required_speed <= remaining_evs:
            evs['spe'] = min(required_speed, self.max_stat_evs)
        else:
            evs['spe'] = min(remaining_evs, self.max_stat_evs)
        
        return evs
    
    def _optimize_custom(
        self,
        pokemon: PokemonInstance,
        stat: str,
        target_value: float,
        current_evs: Dict[str, int],
        remaining_evs: int
    ) -> Dict[str, int]:
        """Optimize EVs for a custom stat target."""
        evs = current_evs.copy()
        
        # Calculate required EVs for target value
        required_evs = self._calculate_required_evs_for_stat(
            pokemon, stat, target_value
        )
        
        # Allocate EVs
        if required_evs <= remaining_evs:
            evs[stat] = min(required_evs, self.max_stat_evs)
        else:
            evs[stat] = min(remaining_evs, self.max_stat_evs)
        
        return evs
    
    def _calculate_required_hp_evs(
        self,
        pokemon: PokemonInstance,
        damage: float
    ) -> int:
        """Calculate required HP EVs to survive a hit."""
        base_hp = pokemon.base_stats['hp']
        hp_iv = pokemon.iv['hp']
        hp_nature = 1.0  # HP is not affected by nature
        
        # Calculate minimum HP needed to survive
        min_hp = damage + 1
        
        # Calculate required EVs
        required_evs = int(((min_hp / hp_nature - 10) * 100 / base_hp - 2 * base_hp - hp_iv) * 4)
        
        return max(0, min(required_evs, self.max_stat_evs))
    
    def _calculate_required_def_evs(
        self,
        pokemon: PokemonInstance,
        damage: float,
        defense_stat: str
    ) -> int:
        """Calculate required defense EVs to survive a hit."""
        base_def = pokemon.base_stats[defense_stat]
        def_iv = pokemon.iv[defense_stat]
        def_nature = 1.1 if pokemon.nature in self._get_positive_natures(defense_stat) else 0.9 if pokemon.nature in self._get_negative_natures(defense_stat) else 1.0
        
        # Calculate minimum defense needed
        min_def = (damage * 100) / (pokemon.calculate_hp(pokemon.ev['hp']) * 0.85)  # 0.85 is a rough estimate for damage formula
        
        # Calculate required EVs
        required_evs = int(((min_def / def_nature - 5) * 100 / base_def - 2 * base_def - def_iv) * 4)
        
        return max(0, min(required_evs, self.max_stat_evs))
    
    def _calculate_required_atk_evs(
        self,
        pokemon: PokemonInstance,
        target: PokemonInstance,
        move: str,
        attack_stat: str,
        is_2hko: bool = False
    ) -> int:
        """Calculate required attack EVs for OHKO/2HKO."""
        base_atk = pokemon.base_stats[attack_stat]
        atk_iv = pokemon.iv[attack_stat]
        atk_nature = 1.1 if pokemon.nature in self._get_positive_natures(attack_stat) else 0.9 if pokemon.nature in self._get_negative_natures(attack_stat) else 1.0
        
        # Get move base power
        cursor = self.db.cursor()
        cursor.execute("SELECT base_power FROM moves WHERE name = ?", (move,))
        base_power = cursor.fetchone()[0]
        
        # Calculate target HP
        target_hp = target.calculate_hp(target.ev['hp'])
        if is_2hko:
            target_hp /= 2
        
        # Calculate required attack stat
        min_atk = (target_hp * 100) / (base_power * 0.85)  # 0.85 is a rough estimate for damage formula
        
        # Calculate required EVs
        required_evs = int(((min_atk / atk_nature - 5) * 100 / base_atk - 2 * base_atk - atk_iv) * 4)
        
        return max(0, min(required_evs, self.max_stat_evs))
    
    def _calculate_required_speed_evs(
        self,
        pokemon: PokemonInstance,
        target_speed: float
    ) -> int:
        """Calculate required speed EVs to outspeed a target."""
        base_spe = pokemon.base_stats['spe']
        spe_iv = pokemon.iv['spe']
        spe_nature = 1.1 if pokemon.nature in self._get_positive_natures('spe') else 0.9 if pokemon.nature in self._get_negative_natures('spe') else 1.0
        
        # Calculate required speed stat
        required_speed = target_speed + 1
        
        # Calculate required EVs
        required_evs = int(((required_speed / spe_nature - 5) * 100 / base_spe - 2 * base_spe - spe_iv) * 4)
        
        return max(0, min(required_evs, self.max_stat_evs))
    
    def _calculate_required_evs_for_stat(
        self,
        pokemon: PokemonInstance,
        stat: str,
        target_value: float
    ) -> int:
        """Calculate required EVs to reach a target stat value."""
        base_stat = pokemon.base_stats[stat]
        stat_iv = pokemon.iv[stat]
        stat_nature = 1.1 if pokemon.nature in self._get_positive_natures(stat) else 0.9 if pokemon.nature in self._get_negative_natures(stat) else 1.0
        
        # Calculate required EVs
        required_evs = int(((target_value / stat_nature - 5) * 100 / base_stat - 2 * base_stat - stat_iv) * 4)
        
        return max(0, min(required_evs, self.max_stat_evs))
    
    def _get_positive_natures(self, stat: str) -> Set[str]:
        """Get natures that positively affect a stat."""
        nature_map = {
            'atk': {'adamant', 'brave', 'naughty', 'lonely'},
            'def': {'bold', 'relaxed', 'impish', 'lax'},
            'spa': {'modest', 'quiet', 'mild', 'rash'},
            'spd': {'calm', 'sassy', 'careful', 'gentle'},
            'spe': {'timid', 'hasty', 'jolly', 'naive'}
        }
        return nature_map.get(stat, set())
    
    def _get_negative_natures(self, stat: str) -> Set[str]:
        """Get natures that negatively affect a stat."""
        nature_map = {
            'atk': {'modest', 'timid', 'bold', 'calm'},
            'def': {'lonely', 'hasty', 'mild', 'gentle'},
            'spa': {'adamant', 'impish', 'careful', 'jolly'},
            'spd': {'naughty', 'lax', 'rash', 'naive'},
            'spe': {'brave', 'relaxed', 'quiet', 'sassy'}
        }
        return nature_map.get(stat, set()) 