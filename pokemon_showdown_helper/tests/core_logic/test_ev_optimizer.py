"""
Tests for the EV optimizer module.
"""
import unittest
from unittest.mock import Mock, patch
from core_logic.ev_optimizer import EVOptimizer, EVOptimizationGoal
from core_logic.pokemon_object import PokemonInstance

class TestEVOptimizer(unittest.TestCase):
    """Test cases for the EV optimizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock database connection
        self.db_patcher = patch('core_logic.ev_optimizer.get_db_connection')
        self.mock_db = self.db_patcher.start()
        
        # Mock cursor
        self.mock_cursor = Mock()
        self.mock_db.return_value.cursor.return_value = self.mock_cursor
        
        # Mock special moves query
        self.mock_cursor.fetchall.return_value = [
            ('Flamethrower',),
            ('Thunderbolt',),
            ('Ice Beam',)
        ]
        
        # Create optimizer instance
        self.optimizer = EVOptimizer()
        
        # Create test Pokémon
        self.attacker = PokemonInstance(
            species='Charizard',
            level=100,
            nature='timid',
            iv={'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31},
            ev={'hp': 0, 'atk': 0, 'def': 0, 'spa': 252, 'spd': 0, 'spe': 252},
            moves=['Flamethrower', 'Air Slash', 'Dragon Pulse', 'Roost'],
            ability='Blaze',
            item='Choice Specs'
        )
        
        self.defender = PokemonInstance(
            species='Ferrothorn',
            level=100,
            nature='relaxed',
            iv={'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31},
            ev={'hp': 252, 'atk': 0, 'def': 252, 'spa': 0, 'spd': 0, 'spe': 0},
            moves=['Gyro Ball', 'Power Whip', 'Stealth Rock', 'Spikes'],
            ability='Iron Barbs',
            item='Leftovers'
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.db_patcher.stop()
    
    def test_optimize_survival(self):
        """Test optimizing EVs for survival."""
        # Create survival goal
        goal = EVOptimizationGoal(
            type='survive',
            target_pokemon=self.attacker,
            move='Flamethrower'
        )
        
        # Optimize EVs
        optimized_evs = self.optimizer.optimize_evs(
            self.defender,
            [goal]
        )
        
        # Verify results
        self.assertLessEqual(sum(optimized_evs.values()), 510)
        self.assertLessEqual(optimized_evs['hp'], 252)
        self.assertLessEqual(optimized_evs['spd'], 252)
    
    def test_optimize_ohko(self):
        """Test optimizing EVs for OHKO."""
        # Create OHKO goal
        goal = EVOptimizationGoal(
            type='ohko',
            target_pokemon=self.defender,
            move='Flamethrower'
        )
        
        # Optimize EVs
        optimized_evs = self.optimizer.optimize_evs(
            self.attacker,
            [goal]
        )
        
        # Verify results
        self.assertLessEqual(sum(optimized_evs.values()), 510)
        self.assertLessEqual(optimized_evs['spa'], 252)
    
    def test_optimize_2hko(self):
        """Test optimizing EVs for 2HKO."""
        # Create 2HKO goal
        goal = EVOptimizationGoal(
            type='2hko',
            target_pokemon=self.defender,
            move='Flamethrower'
        )
        
        # Optimize EVs
        optimized_evs = self.optimizer.optimize_evs(
            self.attacker,
            [goal]
        )
        
        # Verify results
        self.assertLessEqual(sum(optimized_evs.values()), 510)
        self.assertLessEqual(optimized_evs['spa'], 252)
    
    def test_optimize_speed(self):
        """Test optimizing EVs for speed."""
        # Create speed goal
        goal = EVOptimizationGoal(
            type='outspeed',
            target_pokemon=self.defender
        )
        
        # Optimize EVs
        optimized_evs = self.optimizer.optimize_evs(
            self.attacker,
            [goal]
        )
        
        # Verify results
        self.assertLessEqual(sum(optimized_evs.values()), 510)
        self.assertLessEqual(optimized_evs['spe'], 252)
    
    def test_optimize_custom(self):
        """Test optimizing EVs for custom stat target."""
        # Create custom goal
        goal = EVOptimizationGoal(
            type='custom',
            stat='spa',
            value=300
        )
        
        # Optimize EVs
        optimized_evs = self.optimizer.optimize_evs(
            self.attacker,
            [goal]
        )
        
        # Verify results
        self.assertLessEqual(sum(optimized_evs.values()), 510)
        self.assertLessEqual(optimized_evs['spa'], 252)
    
    def test_multiple_goals(self):
        """Test optimizing EVs for multiple goals."""
        # Create multiple goals
        goals = [
            EVOptimizationGoal(
                type='ohko',
                target_pokemon=self.defender,
                move='Flamethrower',
                priority=2
            ),
            EVOptimizationGoal(
                type='outspeed',
                target_pokemon=self.defender,
                priority=1
            )
        ]
        
        # Optimize EVs
        optimized_evs = self.optimizer.optimize_evs(
            self.attacker,
            goals
        )
        
        # Verify results
        self.assertLessEqual(sum(optimized_evs.values()), 510)
        self.assertLessEqual(optimized_evs['spa'], 252)
        self.assertLessEqual(optimized_evs['spe'], 252)
    
    def test_fixed_evs(self):
        """Test optimizing EVs with fixed values."""
        # Create goal
        goal = EVOptimizationGoal(
            type='ohko',
            target_pokemon=self.defender,
            move='Flamethrower'
        )
        
        # Fixed EVs
        fixed_evs = {'hp': 4, 'atk': 0, 'def': 0, 'spa': 252, 'spd': 0, 'spe': 252}
        
        # Optimize EVs
        optimized_evs = self.optimizer.optimize_evs(
            self.attacker,
            [goal],
            fixed_evs=fixed_evs
        )
        
        # Verify results
        self.assertEqual(optimized_evs['hp'], 4)
        self.assertEqual(optimized_evs['spe'], 252)
        self.assertLessEqual(sum(optimized_evs.values()), 510)
    
    def test_nature_effects(self):
        """Test that nature effects are properly considered."""
        # Create test Pokémon with different natures
        modest_attacker = PokemonInstance(
            species='Charizard',
            level=100,
            nature='modest',
            iv={'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31},
            ev={'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0},
            moves=['Flamethrower'],
            ability='Blaze',
            item='Choice Specs'
        )
        
        timid_attacker = PokemonInstance(
            species='Charizard',
            level=100,
            nature='timid',
            iv={'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31},
            ev={'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0},
            moves=['Flamethrower'],
            ability='Blaze',
            item='Choice Specs'
        )
        
        # Create OHKO goal
        goal = EVOptimizationGoal(
            type='ohko',
            target_pokemon=self.defender,
            move='Flamethrower'
        )
        
        # Optimize EVs for both Pokémon
        modest_evs = self.optimizer.optimize_evs(modest_attacker, [goal])
        timid_evs = self.optimizer.optimize_evs(timid_attacker, [goal])
        
        # Verify that nature affects required EVs
        self.assertNotEqual(modest_evs['spa'], timid_evs['spa'])

if __name__ == '__main__':
    unittest.main() 