"""
Tests for the matchup analyzer module.
"""
import pytest
from core_logic.matchup_analyzer import MatchupAnalyzer
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team

@pytest.fixture
def analyzer():
    return MatchupAnalyzer()

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

def test_analyze_matchup(analyzer, sample_user_team, sample_opponent_team):
    """Test the main matchup analysis function."""
    analysis = analyzer.analyze_matchup(sample_user_team, sample_opponent_team)
    
    assert 'key_threats' in analysis
    assert 'type_matchup_summary' in analysis
    assert 'speed_comparison' in analysis
    assert 'vulnerabilities' in analysis
    
    # Check key threats
    assert len(analysis['key_threats']) > 0
    assert all('attacker' in threat for threat in analysis['key_threats'])
    assert all('defender' in threat for threat in analysis['key_threats'])
    assert all('ko_type' in threat for threat in analysis['key_threats'])
    
    # Check type matchup summary
    assert 'user_team' in analysis['type_matchup_summary']
    assert 'opponent_team' in analysis['type_matchup_summary']
    assert 'weaknesses' in analysis['type_matchup_summary']['user_team']
    assert 'resistances' in analysis['type_matchup_summary']['user_team']
    
    # Check speed comparison
    assert len(analysis['speed_comparison']) == 4  # 2 Pokémon from each team
    assert all('pokemon' in entry for entry in analysis['speed_comparison'])
    assert all('speed' in entry for entry in analysis['speed_comparison'])
    assert all('team' in entry for entry in analysis['speed_comparison'])
    
    # Check vulnerabilities
    assert 'common_weaknesses' in analysis['vulnerabilities']
    assert 'speed_vulnerabilities' in analysis['vulnerabilities']
    assert 'coverage_gaps' in analysis['vulnerabilities']

def test_identify_key_threats(analyzer, sample_user_team, sample_opponent_team):
    """Test identification of key threats."""
    threats = analyzer._identify_key_threats(sample_user_team, sample_opponent_team)
    
    assert len(threats) > 0
    assert all('attacker' in threat for threat in threats)
    assert all('defender' in threat for threat in threats)
    assert all('move' in threat for threat in threats)
    assert all('ko_type' in threat for threat in threats)
    assert all(threat['ko_type'] in ['OHKO', '2HKO'] for threat in threats)

def test_analyze_type_matchups(analyzer, sample_user_team, sample_opponent_team):
    """Test type matchup analysis."""
    matchups = analyzer._analyze_type_matchups(sample_user_team, sample_opponent_team)
    
    assert 'user_team' in matchups
    assert 'opponent_team' in matchups
    assert 'weaknesses' in matchups['user_team']
    assert 'resistances' in matchups['user_team']
    assert 'weaknesses' in matchups['opponent_team']
    assert 'resistances' in matchups['opponent_team']
    
    # Check that weaknesses and resistances are dictionaries with type counts
    assert all(isinstance(count, int) for count in matchups['user_team']['weaknesses'].values())
    assert all(isinstance(count, int) for count in matchups['user_team']['resistances'].values())

def test_compare_speed_tiers(analyzer, sample_user_team, sample_opponent_team):
    """Test speed tier comparison."""
    speed_tiers = analyzer._compare_speed_tiers(sample_user_team, sample_opponent_team)
    
    assert len(speed_tiers) == 4  # 2 Pokémon from each team
    assert all('pokemon' in entry for entry in speed_tiers)
    assert all('speed' in entry for entry in speed_tiers)
    assert all('team' in entry for entry in speed_tiers)
    assert all(entry['team'] in ['user', 'opponent'] for entry in speed_tiers)
    
    # Check that speed tiers are sorted in descending order
    speeds = [entry['speed'] for entry in speed_tiers]
    assert speeds == sorted(speeds, reverse=True)

def test_identify_vulnerabilities(analyzer, sample_user_team, sample_opponent_team):
    """Test vulnerability identification."""
    vulnerabilities = analyzer._identify_vulnerabilities(sample_user_team, sample_opponent_team)
    
    assert 'common_weaknesses' in vulnerabilities
    assert 'speed_vulnerabilities' in vulnerabilities
    assert 'coverage_gaps' in vulnerabilities
    
    # Check common weaknesses
    assert isinstance(vulnerabilities['common_weaknesses'], list)
    assert all(isinstance(weakness, str) for weakness in vulnerabilities['common_weaknesses'])
    
    # Check speed vulnerabilities
    assert isinstance(vulnerabilities['speed_vulnerabilities'], list)
    assert all('user_pokemon' in vuln for vuln in vulnerabilities['speed_vulnerabilities'])
    assert all('opponent_pokemon' in vuln for vuln in vulnerabilities['speed_vulnerabilities'])
    assert all('speed_difference' in vuln for vuln in vulnerabilities['speed_vulnerabilities'])
    
    # Check coverage gaps
    assert isinstance(vulnerabilities['coverage_gaps'], list)
    assert all(isinstance(gap, str) for gap in vulnerabilities['coverage_gaps']) 