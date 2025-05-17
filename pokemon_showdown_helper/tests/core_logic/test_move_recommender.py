"""
Tests for the move recommender module.
"""
import pytest
from core_logic.move_recommender import MoveRecommender
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team

@pytest.fixture
def recommender():
    return MoveRecommender()

@pytest.fixture
def sample_user_pokemon():
    return PokemonInstance(
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
    )

@pytest.fixture
def sample_opponent_team():
    return Team([
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
        ),
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
        )
    ])

def test_recommend_moves(recommender, sample_user_pokemon, sample_opponent_team):
    """Test the main move recommendation function."""
    recommendations = recommender.recommend_moves(sample_user_pokemon, sample_opponent_team)
    
    assert 'recommended_moves' in recommendations
    assert 'coverage_analysis' in recommendations
    assert 'priority_moves' in recommendations
    assert 'utility_moves' in recommendations
    
    # Check recommended moves
    assert isinstance(recommendations['recommended_moves'], list)
    assert len(recommendations['recommended_moves']) <= 4  # Should return at most 4 moves
    if recommendations['recommended_moves']:
        assert 'move' in recommendations['recommended_moves'][0]
        assert 'score' in recommendations['recommended_moves'][0]
        assert 'reasoning' in recommendations['recommended_moves'][0]
    
    # Check coverage analysis
    assert isinstance(recommendations['coverage_analysis'], dict)
    
    # Check priority moves
    assert isinstance(recommendations['priority_moves'], list)
    if recommendations['priority_moves']:
        assert 'move' in recommendations['priority_moves'][0]
        assert 'reasoning' in recommendations['priority_moves'][0]
    
    # Check utility moves
    assert isinstance(recommendations['utility_moves'], list)
    if recommendations['utility_moves']:
        assert 'move' in recommendations['utility_moves'][0]
        assert 'reasoning' in recommendations['utility_moves'][0]

def test_get_recommended_moves(recommender, sample_user_pokemon, sample_opponent_team):
    """Test move recommendation logic."""
    analysis = recommender.matchup_analyzer.analyze_matchup(
        Team([sample_user_pokemon]), sample_opponent_team
    )
    moves = recommender._get_recommended_moves(sample_user_pokemon, sample_opponent_team, analysis)
    
    assert isinstance(moves, list)
    assert len(moves) <= 4  # Should return at most 4 moves
    if moves:
        assert 'move' in moves[0]
        assert 'score' in moves[0]
        assert 'reasoning' in moves[0]
        assert isinstance(moves[0]['reasoning'], list)

def test_analyze_coverage(recommender, sample_user_pokemon, sample_opponent_team):
    """Test coverage analysis."""
    coverage = recommender._analyze_coverage(sample_user_pokemon, sample_opponent_team)
    
    assert isinstance(coverage, dict)
    for move_type, targets in coverage.items():
        assert isinstance(targets, list)
        assert all(isinstance(target, str) for target in targets)

def test_get_priority_moves(recommender, sample_user_pokemon, sample_opponent_team):
    """Test priority move identification."""
    priority_moves = recommender._get_priority_moves(sample_user_pokemon, sample_opponent_team)
    
    assert isinstance(priority_moves, list)
    if priority_moves:
        assert 'move' in priority_moves[0]
        assert 'reasoning' in priority_moves[0]

def test_get_utility_moves(recommender, sample_user_pokemon, sample_opponent_team):
    """Test utility move identification."""
    utility_moves = recommender._get_utility_moves(sample_user_pokemon, sample_opponent_team)
    
    assert isinstance(utility_moves, list)
    if utility_moves:
        assert 'move' in utility_moves[0]
        assert 'reasoning' in utility_moves[0]

def test_is_priority_move(recommender):
    """Test priority move detection."""
    assert recommender._is_priority_move("Extreme Speed")
    assert recommender._is_priority_move("Quick Attack")
    assert not recommender._is_priority_move("Thunderbolt")

def test_is_utility_move(recommender):
    """Test utility move detection."""
    assert recommender._is_utility_move("Defog")
    assert recommender._is_utility_move("Roost")
    assert not recommender._is_utility_move("Thunderbolt")

def test_get_utility_reasoning(recommender, sample_opponent_team):
    """Test utility move reasoning."""
    assert "Hazard removal" in recommender._get_utility_reasoning("Defog", sample_opponent_team)
    assert "Recovery" in recommender._get_utility_reasoning("Roost", sample_opponent_team)
    assert "Status spreading" in recommender._get_utility_reasoning("Toxic", sample_opponent_team) 