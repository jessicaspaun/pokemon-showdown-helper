"""
Tests for the strategy generator module.
"""
import pytest
from core_logic.strategy_generator import StrategyGenerator
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team

@pytest.fixture
def generator():
    return StrategyGenerator()

@pytest.fixture
def sample_user_team():
    return Team([
        PokemonInstance(
            species="Tapu Koko",
            level=100,
            base_stats={"hp": 70, "atk": 115, "def": 85, "spa": 95, "spd": 75, "spe": 130},
            iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
            ev={"hp": 0, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 252},
            nature="Timid",
            ability="Electric Surge",
            item="Life Orb",
            types=["Electric", "Fairy"],
            moves=["Thunderbolt", "Dazzling Gleam", "Hidden Power Ice", "U-turn"]
        ),
        PokemonInstance(
            species="Landorus-Therian",
            level=100,
            base_stats={"hp": 89, "atk": 145, "def": 90, "spa": 105, "spd": 80, "spe": 91},
            iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
            ev={"hp": 0, "atk": 252, "def": 0, "spa": 0, "spd": 0, "spe": 252},
            nature="Adamant",
            ability="Intimidate",
            item="Choice Scarf",
            types=["Ground", "Flying"],
            moves=["Earthquake", "U-turn", "Stone Edge", "Superpower"]
        )
    ])

@pytest.fixture
def sample_opponent_team():
    return Team([
        PokemonInstance(
            species="Magearna",
            level=100,
            base_stats={"hp": 80, "atk": 95, "def": 115, "spa": 130, "spd": 115, "spe": 65},
            iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
            ev={"hp": 0, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 252},
            nature="Timid",
            ability="Soul-Heart",
            item="Fairium Z",
            types=["Steel", "Fairy"],
            moves=["Fleur Cannon", "Flash Cannon", "Volt Switch", "Focus Blast"]
        ),
        PokemonInstance(
            species="Toxapex",
            level=100,
            base_stats={"hp": 50, "atk": 63, "def": 152, "spa": 53, "spd": 142, "spe": 35},
            iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
            ev={"hp": 252, "atk": 0, "def": 252, "spa": 0, "spd": 4, "spe": 0},
            nature="Bold",
            ability="Regenerator",
            item="Black Sludge",
            types=["Poison", "Water"],
            moves=["Scald", "Recover", "Haze", "Toxic"]
        )
    ])

def test_generate_strategy(generator, sample_user_team, sample_opponent_team):
    """Test the main strategy generation function."""
    strategy = generator.generate_strategy(sample_user_team, sample_opponent_team)
    
    assert 'suggested_lead' in strategy
    assert 'key_threats_to_handle' in strategy
    assert 'win_conditions' in strategy
    assert 'general_strategy' in strategy
    
    # Check suggested lead
    assert 'pokemon' in strategy['suggested_lead']
    assert 'reasoning' in strategy['suggested_lead']
    assert isinstance(strategy['suggested_lead']['reasoning'], list)
    
    # Check key threats
    assert isinstance(strategy['key_threats_to_handle'], list)
    if strategy['key_threats_to_handle']:
        assert 'pokemon' in strategy['key_threats_to_handle'][0]
        assert 'move' in strategy['key_threats_to_handle'][0]
        assert 'ko_type' in strategy['key_threats_to_handle'][0]
    
    # Check win conditions
    assert isinstance(strategy['win_conditions'], list)
    if strategy['win_conditions']:
        assert 'type' in strategy['win_conditions'][0]
        assert 'pokemon' in strategy['win_conditions'][0]
        assert 'reasoning' in strategy['win_conditions'][0]
    
    # Check general strategy
    assert isinstance(strategy['general_strategy'], list)
    assert all(isinstance(advice, str) for advice in strategy['general_strategy'])

def test_suggest_lead(generator, sample_user_team, sample_opponent_team):
    """Test lead suggestion."""
    analysis = generator.matchup_analyzer.analyze_matchup(sample_user_team, sample_opponent_team)
    lead = generator._suggest_lead(sample_user_team, sample_opponent_team, analysis)
    
    assert 'pokemon' in lead
    assert 'reasoning' in lead
    assert isinstance(lead['reasoning'], list)
    assert lead['pokemon'] in [p.species for p in sample_user_team.pokemon]

def test_identify_key_threats_to_handle(generator, sample_user_team, sample_opponent_team):
    """Test identification of key threats to handle."""
    analysis = generator.matchup_analyzer.analyze_matchup(sample_user_team, sample_opponent_team)
    threats = generator._identify_key_threats_to_handle(analysis)
    
    assert isinstance(threats, list)
    if threats:
        assert 'pokemon' in threats[0]
        assert 'move' in threats[0]
        assert 'ko_type' in threats[0]
        assert 'targets' in threats[0]
        assert all(threat['pokemon'] in [p.species for p in sample_opponent_team.pokemon] for threat in threats)

def test_identify_win_conditions(generator, sample_user_team, sample_opponent_team):
    """Test identification of win conditions."""
    analysis = generator.matchup_analyzer.analyze_matchup(sample_user_team, sample_opponent_team)
    win_conditions = generator._identify_win_conditions(sample_user_team, sample_opponent_team, analysis)
    
    assert isinstance(win_conditions, list)
    if win_conditions:
        assert 'type' in win_conditions[0]
        assert 'pokemon' in win_conditions[0]
        assert 'reasoning' in win_conditions[0]
        assert win_conditions[0]['type'] in ['sweep', 'wallbreak']
        assert all(condition['pokemon'] in [p.species for p in sample_user_team.pokemon] for condition in win_conditions)

def test_is_sweeper(generator, sample_user_team, sample_opponent_team):
    """Test sweeper identification."""
    analysis = generator.matchup_analyzer.analyze_matchup(sample_user_team, sample_opponent_team)
    
    # Tapu Koko should be identified as a sweeper
    assert generator._is_sweeper(sample_user_team.pokemon[0], sample_opponent_team, analysis)
    
    # Toxapex should not be identified as a sweeper
    assert not generator._is_sweeper(sample_opponent_team.pokemon[1], sample_user_team, analysis)

def test_is_wallbreaker(generator, sample_user_team, sample_opponent_team):
    """Test wallbreaker identification."""
    analysis = generator.matchup_analyzer.analyze_matchup(sample_user_team, sample_opponent_team)
    
    # Landorus-Therian should be identified as a wallbreaker
    assert generator._is_wallbreaker(sample_user_team.pokemon[1], sample_opponent_team, analysis)
    
    # Toxapex should not be identified as a wallbreaker
    assert not generator._is_wallbreaker(sample_opponent_team.pokemon[1], sample_user_team, analysis)

def test_generate_general_strategy(generator, sample_user_team, sample_opponent_team):
    """Test generation of general strategy advice."""
    analysis = generator.matchup_analyzer.analyze_matchup(sample_user_team, sample_opponent_team)
    strategy = generator._generate_general_strategy(analysis)
    
    assert isinstance(strategy, list)
    assert all(isinstance(advice, str) for advice in strategy)
    assert len(strategy) > 0  # Should provide at least some advice 