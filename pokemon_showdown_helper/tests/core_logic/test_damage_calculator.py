"""
Tests for the damage calculator module.
"""
import pytest
from core_logic.damage_calculator import DamageCalculator
from core_logic.pokemon_object import PokemonInstance

@pytest.fixture
def calculator():
    return DamageCalculator()

@pytest.fixture
def pikachu():
    return PokemonInstance(
        species="Pikachu",
        level=50,
        base_stats={"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
        ev={"hp": 0, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 252},
        nature="Timid",
        ability="Static",
        item="Light Ball",
        types=["Electric"]
    )

@pytest.fixture
def gyarados():
    return PokemonInstance(
        species="Gyarados",
        level=50,
        base_stats={"hp": 95, "atk": 125, "def": 79, "spa": 60, "spd": 100, "spe": 81},
        iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
        ev={"hp": 0, "atk": 252, "def": 0, "spa": 0, "spd": 0, "spe": 252},
        nature="Adamant",
        ability="Intimidate",
        item="Choice Band",
        types=["Water", "Flying"]
    )

def test_basic_damage_calculation(calculator, pikachu, gyarados):
    """Test basic damage calculation with STAB and type effectiveness."""
    damage = calculator.calculate_damage(
        attacker=pikachu,
        defender=gyarados,
        move="Thunderbolt",
        move_type="electric",
        move_power=90
    )
    assert damage > 0
    # Thunderbolt should be super effective against Gyarados
    assert damage > 90  # Base power

def test_weather_effects(calculator, pikachu, gyarados):
    """Test weather effects on damage."""
    # Test in rain (water moves boosted, fire moves weakened)
    damage_rain = calculator.calculate_damage(
        attacker=gyarados,
        defender=pikachu,
        move="Waterfall",
        move_type="water",
        move_power=80,
        weather="rain"
    )
    damage_normal = calculator.calculate_damage(
        attacker=gyarados,
        defender=pikachu,
        move="Waterfall",
        move_type="water",
        move_power=80
    )
    assert damage_rain > damage_normal

def test_field_effects(calculator, pikachu, gyarados):
    """Test field effects on damage."""
    # Test in Electric Terrain (electric moves boosted)
    damage_terrain = calculator.calculate_damage(
        attacker=pikachu,
        defender=gyarados,
        move="Thunderbolt",
        move_type="electric",
        move_power=90,
        field="electric_terrain"
    )
    damage_normal = calculator.calculate_damage(
        attacker=pikachu,
        defender=gyarados,
        move="Thunderbolt",
        move_type="electric",
        move_power=90
    )
    assert damage_terrain > damage_normal

def test_ability_effects(calculator, pikachu, gyarados):
    """Test ability effects on damage."""
    # Test Adaptability
    pikachu.ability = "Adaptability"
    damage_adaptability = calculator.calculate_damage(
        attacker=pikachu,
        defender=gyarados,
        move="Thunderbolt",
        move_type="electric",
        move_power=90
    )
    pikachu.ability = "Static"
    damage_normal = calculator.calculate_damage(
        attacker=pikachu,
        defender=gyarados,
        move="Thunderbolt",
        move_type="electric",
        move_power=90
    )
    assert damage_adaptability > damage_normal

def test_item_effects(calculator, pikachu, gyarados):
    """Test item effects on damage."""
    # Test Choice Band
    damage_band = calculator.calculate_damage(
        attacker=gyarados,
        defender=pikachu,
        move="Waterfall",
        move_type="water",
        move_power=80
    )
    gyarados.item = None
    damage_no_item = calculator.calculate_damage(
        attacker=gyarados,
        defender=pikachu,
        move="Waterfall",
        move_type="water",
        move_power=80
    )
    assert damage_band > damage_no_item

def test_status_effects(calculator, pikachu, gyarados):
    """Test status effects on damage."""
    # Test burn
    gyarados.status = "burn"
    damage_burned = calculator.calculate_damage(
        attacker=gyarados,
        defender=pikachu,
        move="Waterfall",
        move_type="water",
        move_power=80
    )
    gyarados.status = None
    damage_normal = calculator.calculate_damage(
        attacker=gyarados,
        defender=pikachu,
        move="Waterfall",
        move_type="water",
        move_power=80
    )
    assert damage_burned < damage_normal

def test_critical_hits(calculator, pikachu, gyarados):
    """Test critical hit damage."""
    damage_crit = calculator.calculate_damage(
        attacker=pikachu,
        defender=gyarados,
        move="Thunderbolt",
        move_type="electric",
        move_power=90,
        is_critical=True
    )
    damage_normal = calculator.calculate_damage(
        attacker=pikachu,
        defender=gyarados,
        move="Thunderbolt",
        move_type="electric",
        move_power=90,
        is_critical=False
    )
    assert damage_crit > damage_normal

def test_type_effectiveness(calculator, pikachu, gyarados):
    """Test type effectiveness calculations."""
    # Test super effective
    damage_se = calculator.calculate_damage(
        attacker=pikachu,
        defender=gyarados,
        move="Thunderbolt",
        move_type="electric",
        move_power=90
    )
    # Test not very effective
    damage_nve = calculator.calculate_damage(
        attacker=gyarados,
        defender=pikachu,
        move="Waterfall",
        move_type="water",
        move_power=80
    )
    assert damage_se > damage_nve

def test_random_factor(calculator, pikachu, gyarados):
    """Test that random factor is within expected range."""
    damages = []
    for _ in range(100):
        damage = calculator.calculate_damage(
            attacker=pikachu,
            defender=gyarados,
            move="Thunderbolt",
            move_type="electric",
            move_power=90
        )
        damages.append(damage)
    
    # Check that we have some variation in damage
    assert len(set(damages)) > 1
    # Check that all damages are within reasonable range
    min_damage = min(damages)
    max_damage = max(damages)
    assert max_damage / min_damage <= 1.18  # 1.00/0.85 ≈ 1.18 