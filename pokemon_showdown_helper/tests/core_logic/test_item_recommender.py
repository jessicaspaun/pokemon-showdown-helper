"""
Tests for the item recommender module.
"""
import pytest
from core_logic.item_recommender import ItemRecommender
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team

@pytest.fixture
def recommender():
    return ItemRecommender()

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

def test_recommend_items(recommender, sample_user_pokemon, sample_opponent_team):
    """Test the main item recommendation function."""
    recommendations = recommender.recommend_items(sample_user_pokemon, sample_opponent_team)
    
    assert 'recommended_items' in recommendations
    assert 'offensive_items' in recommendations
    assert 'defensive_items' in recommendations
    assert 'utility_items' in recommendations
    
    # Check recommended items
    assert isinstance(recommendations['recommended_items'], list)
    assert len(recommendations['recommended_items']) <= 3  # Should return at most 3 items
    if recommendations['recommended_items']:
        assert 'item' in recommendations['recommended_items'][0]
        assert 'score' in recommendations['recommended_items'][0]
        assert 'reasoning' in recommendations['recommended_items'][0]
    
    # Check offensive items
    assert isinstance(recommendations['offensive_items'], list)
    if recommendations['offensive_items']:
        assert 'item' in recommendations['offensive_items'][0]
        assert 'reasoning' in recommendations['offensive_items'][0]
    
    # Check defensive items
    assert isinstance(recommendations['defensive_items'], list)
    if recommendations['defensive_items']:
        assert 'item' in recommendations['defensive_items'][0]
        assert 'reasoning' in recommendations['defensive_items'][0]
    
    # Check utility items
    assert isinstance(recommendations['utility_items'], list)
    if recommendations['utility_items']:
        assert 'item' in recommendations['utility_items'][0]
        assert 'reasoning' in recommendations['utility_items'][0]

def test_get_recommended_items(recommender, sample_user_pokemon, sample_opponent_team):
    """Test item recommendation logic."""
    analysis = recommender.matchup_analyzer.analyze_matchup(
        Team([sample_user_pokemon]), sample_opponent_team
    )
    items = recommender._get_recommended_items(sample_user_pokemon, sample_opponent_team, analysis)
    
    assert isinstance(items, list)
    assert len(items) <= 3  # Should return at most 3 items
    if items:
        assert 'item' in items[0]
        assert 'score' in items[0]
        assert 'reasoning' in items[0]
        assert isinstance(items[0]['reasoning'], list)

def test_get_offensive_items(recommender, sample_user_pokemon, sample_opponent_team):
    """Test offensive item identification."""
    offensive_items = recommender._get_offensive_items(sample_user_pokemon, sample_opponent_team)
    
    assert isinstance(offensive_items, list)
    if offensive_items:
        assert 'item' in offensive_items[0]
        assert 'reasoning' in offensive_items[0]

def test_get_defensive_items(recommender, sample_user_pokemon, sample_opponent_team):
    """Test defensive item identification."""
    defensive_items = recommender._get_defensive_items(sample_user_pokemon, sample_opponent_team)
    
    assert isinstance(defensive_items, list)
    if defensive_items:
        assert 'item' in defensive_items[0]
        assert 'reasoning' in defensive_items[0]

def test_get_utility_items(recommender, sample_user_pokemon, sample_opponent_team):
    """Test utility item identification."""
    utility_items = recommender._get_utility_items(sample_user_pokemon, sample_opponent_team)
    
    assert isinstance(utility_items, list)
    if utility_items:
        assert 'item' in utility_items[0]
        assert 'reasoning' in utility_items[0]

def test_is_offensive_item(recommender):
    """Test offensive item detection."""
    assert recommender._is_offensive_item("Life Orb")
    assert recommender._is_offensive_item("Choice Scarf")
    assert not recommender._is_offensive_item("Leftovers")

def test_is_defensive_item(recommender):
    """Test defensive item detection."""
    assert recommender._is_defensive_item("Leftovers")
    assert recommender._is_defensive_item("Focus Sash")
    assert not recommender._is_defensive_item("Life Orb")

def test_is_utility_item(recommender):
    """Test utility item detection."""
    assert recommender._is_utility_item("Air Balloon")
    assert not recommender._is_utility_item("Life Orb")

def test_score_offensive_item(recommender, sample_user_pokemon, sample_opponent_team):
    """Test offensive item scoring."""
    score = recommender._score_offensive_item("Life Orb", sample_user_pokemon, sample_opponent_team)
    assert score > 0

def test_score_defensive_item(recommender, sample_user_pokemon, sample_opponent_team):
    """Test defensive item scoring."""
    score = recommender._score_defensive_item("Leftovers", sample_user_pokemon, sample_opponent_team)
    assert score > 0

def test_score_utility_item(recommender, sample_user_pokemon, sample_opponent_team):
    """Test utility item scoring."""
    score = recommender._score_utility_item("Air Balloon", sample_user_pokemon, sample_opponent_team)
    assert score >= 0

def test_get_offensive_reasoning(recommender, sample_user_pokemon):
    """Test offensive item reasoning."""
    assert "damage boost" in recommender._get_offensive_reasoning("Life Orb", sample_user_pokemon)
    assert "Speed boost" in recommender._get_offensive_reasoning("Choice Scarf", sample_user_pokemon)

def test_get_defensive_reasoning(recommender, sample_user_pokemon):
    """Test defensive item reasoning."""
    assert "recovery" in recommender._get_defensive_reasoning("Leftovers", sample_user_pokemon)
    assert "survive" in recommender._get_defensive_reasoning("Focus Sash", sample_user_pokemon)

def test_get_utility_reasoning(recommender, sample_user_pokemon):
    """Test utility item reasoning."""
    assert "Ground immunity" in recommender._get_utility_reasoning("Air Balloon", sample_user_pokemon)

def test_get_team_weaknesses(recommender):
    """Test team weakness detection."""
    team = Team([
        PokemonInstance(
            species="Pikachu",
            level=100,
            base_stats={"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
            iv={"hp": 31, "atk": 31, "def": 31, "spa": 31, "spd": 31, "spe": 31},
            ev={"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
            nature="Timid",
            ability="Static",
            item="Light Ball",
            types=["Electric"],
            moves=["Thunderbolt", "Quick Attack", "Iron Tail", "Volt Switch"]
        )
    ])
    weaknesses = recommender._get_team_weaknesses(team)
    assert isinstance(weaknesses, list)
    assert len(weaknesses) > 0 