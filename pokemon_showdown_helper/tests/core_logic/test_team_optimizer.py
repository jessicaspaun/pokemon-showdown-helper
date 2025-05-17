"""
Tests for the team optimizer module.
"""
import pytest
from core_logic.team_optimizer import TeamOptimizer
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team

@pytest.fixture
def optimizer():
    return TeamOptimizer()

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
            moves=["Fleur Cannon Fairy", "Flash Cannon Steel", "Volt Switch Electric", "Focus Blast Fighting"]
        ),
        PokemonInstance(
            species="Heatran",
            level=100,
            base_stats={"hp": 91, "atk": 90, "def": 106, "spa": 130, "spd": 106, "spe": 77},
            iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
            ev={"hp": 0, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 252},
            nature="Timid",
            ability="Flash Fire",
            item="Leftovers",
            types=["Fire", "Steel"],
            moves=["Magma Storm Fire", "Earth Power Ground", "Flash Cannon Steel", "Taunt"]
        )
    ])

def test_optimize_team(optimizer, sample_team, sample_opponent_team):
    """Test the main team optimization function."""
    result = optimizer.optimize_team(
        team=sample_team,
        opponent_team=sample_opponent_team,
        optimization_goals={
            "type_coverage": 0.3,
            "role_balance": 0.3,
            "matchup_score": 0.4
        }
    )
    
    assert isinstance(result, dict)
    assert "current_analysis" in result
    assert "suggestions" in result
    assert "improvement_scores" in result
    
    # Check current analysis
    current_analysis = result["current_analysis"]
    assert "synergy_analysis" in current_analysis
    assert "matchup_analysis" in current_analysis
    assert "type_coverage_score" in current_analysis
    assert "role_balance_score" in current_analysis
    
    # Check suggestions
    suggestions = result["suggestions"]
    assert isinstance(suggestions, list)
    if suggestions:  # If any suggestions were generated
        suggestion = suggestions[0]
        assert "id" in suggestion
        assert "type" in suggestion
        assert "description" in suggestion
        assert "suggested_team" in suggestion
        assert "improvement" in suggestion
    
    # Check improvement scores
    improvement_scores = result["improvement_scores"]
    assert isinstance(improvement_scores, dict)
    if improvement_scores:  # If any scores were calculated
        assert all(isinstance(score, float) for score in improvement_scores.values())

def test_analyze_current_team(optimizer, sample_team, sample_opponent_team):
    """Test the current team analysis function."""
    analysis = optimizer._analyze_current_team(sample_team, sample_opponent_team)
    
    assert isinstance(analysis, dict)
    assert "synergy_analysis" in analysis
    assert "matchup_analysis" in analysis
    assert "type_coverage_score" in analysis
    assert "role_balance_score" in analysis
    
    # Check type coverage score
    assert 0 <= analysis["type_coverage_score"] <= 1
    
    # Check role balance score
    assert 0 <= analysis["role_balance_score"] <= 1

def test_calculate_type_coverage_score(optimizer, sample_team):
    """Test the type coverage score calculation."""
    score = optimizer._calculate_type_coverage_score(sample_team)
    
    assert isinstance(score, float)
    assert 0 <= score <= 1

def test_calculate_role_balance_score(optimizer, sample_team):
    """Test the role balance score calculation."""
    score = optimizer._calculate_role_balance_score(sample_team)
    
    assert isinstance(score, float)
    assert 0 <= score <= 1

def test_generate_type_suggestions(optimizer, sample_team):
    """Test generating type coverage suggestions."""
    current_analysis = optimizer._analyze_current_team(sample_team, None)
    suggestions = optimizer._generate_type_suggestions(sample_team, current_analysis)
    
    assert isinstance(suggestions, list)
    if suggestions:  # If any suggestions were generated
        suggestion = suggestions[0]
        assert "id" in suggestion
        assert suggestion["type"] == "type_coverage"
        assert "description" in suggestion
        assert "suggested_team" in suggestion
        assert "improvement" in suggestion

def test_generate_role_suggestions(optimizer, sample_team):
    """Test generating role balance suggestions."""
    current_analysis = optimizer._analyze_current_team(sample_team, None)
    suggestions = optimizer._generate_role_suggestions(sample_team, current_analysis)
    
    assert isinstance(suggestions, list)
    if suggestions:  # If any suggestions were generated
        suggestion = suggestions[0]
        assert "id" in suggestion
        assert suggestion["type"] == "role_balance"
        assert "description" in suggestion
        assert "suggested_team" in suggestion
        assert "improvement" in suggestion

def test_generate_matchup_suggestions(optimizer, sample_team, sample_opponent_team):
    """Test generating matchup-based suggestions."""
    current_analysis = optimizer._analyze_current_team(sample_team, sample_opponent_team)
    suggestions = optimizer._generate_matchup_suggestions(
        sample_team,
        current_analysis["matchup_analysis"]
    )
    
    assert isinstance(suggestions, list)
    if suggestions:  # If any suggestions were generated
        suggestion = suggestions[0]
        assert "id" in suggestion
        assert suggestion["type"] == "matchup_improvement"
        assert "description" in suggestion
        assert "suggested_team" in suggestion
        assert "matchup_improvement" in suggestion

def test_can_handle_threat(optimizer, sample_team):
    """Test threat handling assessment."""
    # Create a threat
    threat = PokemonInstance(
        species="Magearna",
        level=100,
        base_stats={"hp": 80, "atk": 95, "def": 115, "spa": 130, "spd": 115, "spe": 65},
        iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
        ev={"hp": 0, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 252},
        nature="Timid",
        ability="Soul-Heart",
        item="Fairium Z",
        types=["Steel", "Fairy"],
        moves=["Fleur Cannon Fairy", "Flash Cannon Steel", "Volt Switch Electric", "Focus Blast Fighting"]
    )
    
    # Test each Pokémon in the team
    for pokemon in sample_team.pokemon:
        can_handle = optimizer._can_handle_threat(pokemon, threat)
        assert isinstance(can_handle, bool)

def test_calculate_matchup_improvement(optimizer, sample_team):
    """Test matchup improvement calculation."""
    # Create a threat
    threat = PokemonInstance(
        species="Magearna",
        level=100,
        base_stats={"hp": 80, "atk": 95, "def": 115, "spa": 130, "spd": 115, "spe": 65},
        iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
        ev={"hp": 0, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 252},
        nature="Timid",
        ability="Soul-Heart",
        item="Fairium Z",
        types=["Steel", "Fairy"],
        moves=["Fleur Cannon Fairy", "Flash Cannon Steel", "Volt Switch Electric", "Focus Blast Fighting"]
    )
    
    # Test each Pokémon in the team
    for pokemon in sample_team.pokemon:
        improvement = optimizer._calculate_matchup_improvement(pokemon, threat)
        assert isinstance(improvement, float)
        assert 0 <= improvement <= 1 