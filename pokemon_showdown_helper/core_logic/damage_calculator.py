"""
Implements the Gen 7 damage formula for Pokémon battles.
"""
from typing import Dict, List, Optional, Tuple
from core_logic.pokemon_object import PokemonInstance
import random

class DamageCalculator:
    """
    Calculates damage for a move in Gen 7.
    """
    def __init__(self):
        # Type effectiveness multipliers
        self.type_effectiveness = {
            "normal": {"rock": 0.5, "ghost": 0, "steel": 0.5},
            "fire": {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "bug": 2, "rock": 0.5, "dragon": 0.5, "steel": 2},
            "water": {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, "rock": 2, "dragon": 0.5},
            "electric": {"water": 2, "electric": 0.5, "grass": 0.5, "ground": 0, "flying": 2, "dragon": 0.5},
            "grass": {"fire": 0.5, "water": 2, "grass": 0.5, "poison": 0.5, "ground": 2, "flying": 0.5, "bug": 0.5, "rock": 2, "dragon": 0.5, "steel": 0.5},
            "ice": {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 0.5, "ground": 2, "flying": 2, "dragon": 2, "steel": 0.5},
            "fighting": {"normal": 2, "ice": 2, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2, "ghost": 0, "dark": 2, "steel": 2, "fairy": 0.5},
            "poison": {"grass": 2, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0, "fairy": 2},
            "ground": {"fire": 2, "electric": 2, "grass": 0.5, "poison": 2, "flying": 0, "bug": 0.5, "rock": 2, "steel": 2},
            "flying": {"electric": 0.5, "grass": 2, "fighting": 2, "bug": 2, "rock": 0.5, "steel": 0.5},
            "psychic": {"fighting": 2, "poison": 2, "psychic": 0.5, "dark": 0, "steel": 0.5},
            "bug": {"fire": 0.5, "grass": 2, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2, "ghost": 0.5, "dark": 2, "steel": 0.5, "fairy": 0.5},
            "rock": {"fire": 2, "ice": 2, "fighting": 0.5, "ground": 0.5, "flying": 2, "bug": 2, "steel": 0.5},
            "ghost": {"normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5},
            "dragon": {"dragon": 2, "steel": 0.5, "fairy": 0},
            "dark": {"fighting": 0.5, "psychic": 2, "ghost": 2, "dark": 0.5, "fairy": 0.5},
            "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2, "rock": 2, "steel": 0.5, "fairy": 2},
            "fairy": {"fighting": 2, "poison": 0.5, "dragon": 2, "dark": 2, "steel": 0.5}
        }
        
        # Weather effects on move power
        self.weather_boost = {
            "sun": {"fire": 1.5, "water": 0.5},
            "rain": {"water": 1.5, "fire": 0.5},
            "sand": {"rock": 1.5},
            "hail": {"ice": 1.5}
        }
        
        # Field effects on move power
        self.field_boost = {
            "electric_terrain": {"electric": 1.5},
            "grassy_terrain": {"grass": 1.5},
            "psychic_terrain": {"psychic": 1.5},
            "misty_terrain": {"dragon": 0.5}
        }
        
        # Ability modifiers
        self.ability_modifiers = {
            "adaptability": 2.0,  # STAB multiplier becomes 2.0 instead of 1.5
            "technician": 1.5,    # For moves with power <= 60
            "tinted_lens": 2.0,   # For not very effective moves
            "aerilate": 1.2,      # Normal moves become Flying and get 1.2x power
            "pixilate": 1.2,      # Normal moves become Fairy and get 1.2x power
            "refrigerate": 1.2,   # Normal moves become Ice and get 1.2x power
            "galvanize": 1.2      # Normal moves become Electric and get 1.2x power
        }

    def _get_attack_defense_stats(self, attacker: PokemonInstance, defender: PokemonInstance, move_type: str) -> Tuple[int, int]:
        """Get the appropriate attack and defense stats based on move type."""
        if move_type in ["fire", "water", "electric", "grass", "ice", "psychic", "dragon", "dark", "fairy"]:
            return attacker.calculate_stats()["spa"], defender.calculate_stats()["spd"]
        return attacker.calculate_stats()["atk"], defender.calculate_stats()["def"]

    def _calculate_stab(self, attacker: PokemonInstance, move_type: str) -> float:
        """Calculate STAB (Same Type Attack Bonus)."""
        if move_type in attacker.types:
            # Check for Adaptability
            if attacker.ability == "adaptability":
                return 2.0
            return 1.5
        return 1.0

    def _calculate_type_effectiveness(self, move_type: str, defender: PokemonInstance) -> float:
        """Calculate type effectiveness against defender."""
        effectiveness = 1.0
        for defender_type in defender.types:
            if defender_type in self.type_effectiveness.get(move_type, {}):
                effectiveness *= self.type_effectiveness[move_type][defender_type]
        return effectiveness

    def _calculate_weather_modifier(self, move_type: str, weather: Optional[str] = None) -> float:
        """Calculate weather modifier for move power."""
        if weather and weather in self.weather_boost:
            return self.weather_boost[weather].get(move_type, 1.0)
        return 1.0

    def _calculate_field_modifier(self, move_type: str, field: Optional[str] = None) -> float:
        """Calculate field effect modifier for move power."""
        if field and field in self.field_boost:
            return self.field_boost[field].get(move_type, 1.0)
        return 1.0

    def _calculate_ability_modifier(self, attacker: PokemonInstance, move_type: str, move_power: int, effectiveness: float) -> float:
        """Calculate ability-based modifiers."""
        modifier = 1.0
        if attacker.ability:
            if attacker.ability == "technician" and move_power <= 60:
                modifier *= self.ability_modifiers["technician"]
            elif attacker.ability == "tinted_lens" and effectiveness < 1.0:
                modifier *= self.ability_modifiers["tinted_lens"]
            elif attacker.ability in ["aerilate", "pixilate", "refrigerate", "galvanize"]:
                # These abilities change Normal moves to their respective types
                if move_type == "normal":
                    modifier *= self.ability_modifiers[attacker.ability]
        return modifier

    def _calculate_item_modifier(self, attacker: PokemonInstance, move_type: str) -> float:
        """Calculate item-based modifiers."""
        if not attacker.item:
            return 1.0
            
        item_modifiers = {
            "choice_band": 1.5 if move_type not in ["fire", "water", "electric", "grass", "ice", "psychic", "dragon", "dark", "fairy"] else 1.0,
            "choice_specs": 1.5 if move_type in ["fire", "water", "electric", "grass", "ice", "psychic", "dragon", "dark", "fairy"] else 1.0,
            "life_orb": 1.3,
            "expert_belt": 1.2,  # For super-effective moves
            "metronome": 1.0,    # Would need to track consecutive uses
            "muscle_band": 1.1 if move_type not in ["fire", "water", "electric", "grass", "ice", "psychic", "dragon", "dark", "fairy"] else 1.0,
            "wise_glasses": 1.1 if move_type in ["fire", "water", "electric", "grass", "ice", "psychic", "dragon", "dark", "fairy"] else 1.0
        }
        return item_modifiers.get(attacker.item.lower(), 1.0)

    def _calculate_status_modifier(self, attacker: PokemonInstance) -> float:
        """Calculate status effect modifiers."""
        if attacker.status == "burn" and move_type not in ["fire", "water", "electric", "grass", "ice", "psychic", "dragon", "dark", "fairy"]:
            return 0.5
        return 1.0

    def calculate_damage(
        self,
        attacker: PokemonInstance,
        defender: PokemonInstance,
        move: str,
        move_type: str,
        move_power: int,
        is_critical: bool = False,
        weather: Optional[str] = None,
        field: Optional[str] = None
    ) -> int:
        """
        Calculate damage for a move using the Gen 7 formula.
        Formula: ((2 * level / 5 + 2) * power * attack / defense / 50 + 2) * modifier
        Modifier = STAB * type_effectiveness * critical * random * weather * field * ability * item * status
        """
        level = attacker.level
        attack, defense = self._get_attack_defense_stats(attacker, defender, move_type)
        
        # Calculate all modifiers
        stab = self._calculate_stab(attacker, move_type)
        effectiveness = self._calculate_type_effectiveness(move_type, defender)
        critical = 1.5 if is_critical else 1.0
        random_factor = random.uniform(0.85, 1.00)  # Gen 7 random factor
        weather_mod = self._calculate_weather_modifier(move_type, weather)
        field_mod = self._calculate_field_modifier(move_type, field)
        ability_mod = self._calculate_ability_modifier(attacker, move_type, move_power, effectiveness)
        item_mod = self._calculate_item_modifier(attacker, move_type)
        status_mod = self._calculate_status_modifier(attacker)
        
        # Calculate base damage
        base_damage = ((2 * level / 5 + 2) * move_power * attack / defense / 50 + 2)
        
        # Apply all modifiers
        modifier = stab * effectiveness * critical * random_factor * weather_mod * field_mod * ability_mod * item_mod * status_mod
        
        return int(base_damage * modifier) 