"""
Tests for the team synergy analyzer module.
"""
import pytest
from core_logic.team_synergy_analyzer import TeamSynergyAnalyzer
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team

@pytest.fixture
def analyzer():
    return TeamSynergyAnalyzer()

@pytest.fixture
def sample_team():
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
            moves=["Thunderbolt Electric", "Dazzling Gleam Fairy", "Hidden Power Ice", "U-turn"]
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
            moves=["Earthquake Ground", "U-turn", "Stone Edge Rock", "Superpower Fighting"]
        ),
        PokemonInstance(
            species="Ferrothorn",
            level=100,
            base_stats={"hp": 74, "atk": 94, "def": 131, "spa": 54, "spd": 116, "spe": 20},
            iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
            ev={"hp": 252, "atk": 0, "def": 88, "spa": 0, "spd": 168, "spe": 0},
            nature="Relaxed",
            ability="Iron Barbs",
            item="Leftovers",
            types=["Grass", "Steel"],
            moves=["Stealth Rock Rock", "Spikes", "Leech Seed", "Power Whip Grass"]
        )
    ])

def test_analyze_synergy(analyzer, sample_team):
    """Test the main synergy analysis function."""
    analysis = analyzer.analyze_synergy(sample_team)
    
    assert 'type_synergy' in analysis
    assert 'role_synergy' in analysis
    assert 'defensive_synergy' in analysis
    assert 'offensive_synergy' in analysis
    assert 'recommendations' in analysis
    
    # Check type synergy
    assert 'coverage' in analysis['type_synergy']
    assert 'weaknesses' in analysis['type_synergy']
    assert 'resistances' in analysis['type_synergy']
    assert 'analysis' in analysis['type_synergy']
    
    # Check role synergy
    assert 'role_distribution' in analysis['role_synergy']
    assert 'analysis' in analysis['role_synergy']
    
    # Check defensive synergy
    assert 'defensive_cores' in analysis['defensive_synergy']
    assert 'defensive_gaps' in analysis['defensive_synergy']
    assert 'analysis' in analysis['defensive_synergy']
    
    # Check offensive synergy
    assert 'offensive_cores' in analysis['offensive_synergy']
    assert 'offensive_gaps' in analysis['offensive_synergy']
    assert 'analysis' in analysis['offensive_synergy']

def test_analyze_type_synergy(analyzer, sample_team):
    """Test type synergy analysis."""
    type_synergy = analyzer._analyze_type_synergy(sample_team)
    
    assert 'coverage' in type_synergy
    assert 'weaknesses' in type_synergy
    assert 'resistances' in type_synergy
    assert 'analysis' in type_synergy
    
    # Check coverage
    assert isinstance(type_synergy['coverage'], dict)
    assert 'Electric' in type_synergy['coverage']
    assert 'Fairy' in type_synergy['coverage']
    
    # Check weaknesses
    assert isinstance(type_synergy['weaknesses'], dict)
    
    # Check resistances
    assert isinstance(type_synergy['resistances'], dict)

def test_analyze_role_synergy(analyzer, sample_team):
    """Test role synergy analysis."""
    role_synergy = analyzer._analyze_role_synergy(sample_team)
    
    assert 'role_distribution' in role_synergy
    assert 'analysis' in role_synergy
    
    # Check role distribution
    assert isinstance(role_synergy['role_distribution'], dict)
    assert 'sweeper' in role_synergy['role_distribution']
    assert 'wallbreaker' in role_synergy['role_distribution']
    assert 'tank' in role_synergy['role_distribution']

def test_analyze_defensive_synergy(analyzer, sample_team):
    """Test defensive synergy analysis."""
    defensive_synergy = analyzer._analyze_defensive_synergy(sample_team)
    
    assert 'defensive_cores' in defensive_synergy
    assert 'defensive_gaps' in defensive_synergy
    assert 'analysis' in defensive_synergy
    
    # Check defensive cores
    assert isinstance(defensive_synergy['defensive_cores'], list)
    
    # Check defensive gaps
    assert isinstance(defensive_synergy['defensive_gaps'], list)

def test_analyze_offensive_synergy(analyzer, sample_team):
    """Test offensive synergy analysis."""
    offensive_synergy = analyzer._analyze_offensive_synergy(sample_team)
    
    assert 'offensive_cores' in offensive_synergy
    assert 'offensive_gaps' in offensive_synergy
    assert 'analysis' in offensive_synergy
    
    # Check offensive cores
    assert isinstance(offensive_synergy['offensive_cores'], list)
    
    # Check offensive gaps
    assert isinstance(offensive_synergy['offensive_gaps'], list)

def test_get_team_type_coverage(analyzer, sample_team):
    """Test team type coverage analysis."""
    coverage = analyzer._get_team_type_coverage(sample_team)
    
    assert isinstance(coverage, dict)
    assert 'Electric' in coverage
    assert 'Fairy' in coverage
    assert 'Ground' in coverage
    assert 'Rock' in coverage

def test_get_team_type_weaknesses(analyzer, sample_team):
    """Test team type weaknesses analysis."""
    weaknesses = analyzer._get_team_type_weaknesses(sample_team)
    
    assert isinstance(weaknesses, dict)
    # Should have weaknesses based on the team's types
    assert len(weaknesses) > 0

def test_get_team_type_resistances(analyzer, sample_team):
    """Test team type resistances analysis."""
    resistances = analyzer._get_team_type_resistances(sample_team)
    
    assert isinstance(resistances, dict)
    # Should have resistances based on the team's types
    assert len(resistances) > 0

def test_determine_pokemon_role(analyzer, sample_team):
    """Test Pokémon role determination."""
    # Test sweeper
    assert analyzer._determine_pokemon_role(sample_team.pokemon[0]) == "sweeper"
    
    # Test wallbreaker
    assert analyzer._determine_pokemon_role(sample_team.pokemon[1]) == "wallbreaker"
    
    # Test hazard setter
    assert analyzer._determine_pokemon_role(sample_team.pokemon[2]) == "hazard_setter"

def test_is_defensive_core(analyzer, sample_team):
    """Test defensive core identification."""
    # Create a Water + Grass core
    water_pokemon = PokemonInstance(
        species="Swampert",
        level=100,
        base_stats={"hp": 100, "atk": 110, "def": 90, "spa": 85, "spd": 90, "spe": 60},
        iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
        ev={"hp": 252, "atk": 0, "def": 252, "spa": 0, "spd": 4, "spe": 0},
        nature="Relaxed",
        ability="Torrent",
        item="Leftovers",
        types=["Water", "Ground"],
        moves=["Scald Water", "Earthquake Ground", "Toxic", "Protect"]
    )
    
    grass_pokemon = PokemonInstance(
        species="Tangrowth",
        level=100,
        base_stats={"hp": 100, "atk": 100, "def": 125, "spa": 110, "spd": 50, "spe": 50},
        iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
        ev={"hp": 252, "atk": 0, "def": 252, "spa": 0, "spd": 4, "spe": 0},
        nature="Relaxed",
        ability="Regenerator",
        item="Assault Vest",
        types=["Grass"],
        moves=["Giga Drain Grass", "Knock Off", "Hidden Power Fire", "Earthquake Ground"]
    )
    
    assert analyzer._is_defensive_core(water_pokemon, grass_pokemon)

def test_is_offensive_core(analyzer, sample_team):
    """Test offensive core identification."""
    # Create a Fire + Ground core
    fire_pokemon = PokemonInstance(
        species="Heatran",
        level=100,
        base_stats={"hp": 91, "atk": 90, "def": 106, "spa": 130, "spd": 106, "spe": 77},
        iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
        ev={"hp": 0, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 252},
        nature="Timid",
        ability="Flash Fire",
        item="Air Balloon",
        types=["Fire", "Steel"],
        moves=["Magma Storm Fire", "Earth Power Ground", "Flash Cannon Steel", "Taunt"]
    )
    
    ground_pokemon = PokemonInstance(
        species="Excadrill",
        level=100,
        base_stats={"hp": 110, "atk": 135, "def": 60, "spa": 50, "spd": 65, "spe": 88},
        iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
        ev={"hp": 0, "atk": 252, "def": 0, "spa": 0, "spd": 0, "spe": 252},
        nature="Adamant",
        ability="Mold Breaker",
        item="Life Orb",
        types=["Ground", "Steel"],
        moves=["Earthquake Ground", "Iron Head Steel", "Rock Slide Rock", "Swords Dance"]
    )
    
    assert analyzer._is_offensive_core(fire_pokemon, ground_pokemon)

def test_generate_recommendations(analyzer, sample_team):
    """Test recommendation generation."""
    recommendations = analyzer._generate_recommendations(sample_team)
    
    assert isinstance(recommendations, list)
    # Should have at least some recommendations based on the team's composition
    assert len(recommendations) >= 0 