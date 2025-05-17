"""
Tests for the team builder logic module.
"""
import pytest
from core_logic.team_builder_logic import TeamBuilderLogic
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team

@pytest.fixture
def builder():
    return TeamBuilderLogic()

@pytest.fixture
def sample_opponent_team():
    return [
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
    ]

@pytest.fixture
def sample_core_pokemon():
    return [
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
        )
    ]

def test_suggest_team(builder, sample_opponent_team):
    """Test team suggestion with a sample roster and opponent team."""
    user_roster = [
        "Greninja",
        "Tapu Koko",
        "Ferrothorn",
        "Heatran",
        "Toxapex",
        "Mimikyu",
        "Magnezone",
        "Celesteela"
    ]
    
    team = builder.suggest_team(user_roster, sample_opponent_team)
    
    assert isinstance(team, Team)
    assert len(team.pokemon) == 6
    assert all(isinstance(p, PokemonInstance) for p in team.pokemon)
    
    # Check that we have some Pokémon that can handle the opponent's threats
    has_ground_resist = any("Water" in p.types or "Flying" in p.types for p in team.pokemon)
    has_fairy_resist = any("Steel" in p.types or "Poison" in p.types for p in team.pokemon)
    assert has_ground_resist or has_fairy_resist

def test_calculate_threat_score(builder, sample_opponent_team):
    """Test threat score calculation."""
    # Create a Pokémon that should be threatening to the opponent's team
    attacker = PokemonInstance(
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
    
    threat_score = builder._calculate_threat_score(attacker, sample_opponent_team)
    assert threat_score > 0  # Should have some threat value

def test_calculate_defensive_score(builder, sample_opponent_team):
    """Test defensive score calculation."""
    # Create a Pokémon that should be defensive against the opponent's team
    defender = PokemonInstance(
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
    
    defensive_score = builder._calculate_defensive_score(defender, sample_opponent_team)
    assert defensive_score > 0  # Should have some defensive value

def test_type_effectiveness(builder):
    """Test type effectiveness calculation."""
    # Test super effective
    effectiveness = builder._get_type_effectiveness("Water", ["Fire"])
    assert effectiveness == 2.0
    
    # Test not very effective
    effectiveness = builder._get_type_effectiveness("Fire", ["Water"])
    assert effectiveness == 0.5
    
    # Test immune
    effectiveness = builder._get_type_effectiveness("Normal", ["Ghost"])
    assert effectiveness == 0.0
    
    # Test dual type
    effectiveness = builder._get_type_effectiveness("Ground", ["Fire", "Flying"])
    assert effectiveness == 0.0  # Ground is immune against Flying

def test_get_pokemon_sets(builder):
    """Test getting Pokémon sets from database."""
    sets = builder._get_pokemon_sets("Landorus-Therian")
    assert len(sets) > 0
    assert all(isinstance(s, dict) for s in sets)
    assert all('pokemon_name' in s for s in sets)
    assert all('moves' in s for s in sets)
    assert all('ability' in s for s in sets)
    assert all('item' in s for s in sets)

def test_build_balanced_team(builder, sample_core_pokemon):
    """Test building a balanced team."""
    team = builder.build_team(
        strategy="balanced",
        core_pokemon=sample_core_pokemon,
        banned_pokemon=["Mega Rayquaza"]
    )
    
    assert isinstance(team, Team)
    assert len(team.pokemon) == 6
    assert team.pokemon[0] == sample_core_pokemon[0]  # Core Pokémon should be included
    
    # Check role distribution
    roles = builder._get_current_roles(team.pokemon)
    assert roles["sweeper"] >= 2
    assert roles["wallbreaker"] >= 1
    assert roles["tank"] >= 1
    assert roles["support"] >= 1
    assert roles["hazard_setter"] >= 1

def test_build_hyper_offense_team(builder, sample_core_pokemon):
    """Test building a hyper offense team."""
    team = builder.build_team(
        strategy="hyper_offense",
        core_pokemon=sample_core_pokemon,
        banned_pokemon=["Mega Rayquaza"]
    )
    
    assert isinstance(team, Team)
    assert len(team.pokemon) == 6
    
    # Check role distribution
    roles = builder._get_current_roles(team.pokemon)
    assert roles["sweeper"] >= 3
    assert roles["wallbreaker"] >= 2
    assert roles["hazard_setter"] >= 1

def test_build_stall_team(builder, sample_core_pokemon):
    """Test building a stall team."""
    team = builder.build_team(
        strategy="stall",
        core_pokemon=sample_core_pokemon,
        banned_pokemon=["Mega Rayquaza"]
    )
    
    assert isinstance(team, Team)
    assert len(team.pokemon) == 6
    
    # Check role distribution
    roles = builder._get_current_roles(team.pokemon)
    assert roles["tank"] >= 3
    assert roles["support"] >= 2
    assert roles["hazard_setter"] >= 1

def test_build_weather_team(builder, sample_core_pokemon):
    """Test building a weather team."""
    team = builder.build_team(
        strategy="weather",
        core_pokemon=sample_core_pokemon,
        banned_pokemon=["Mega Rayquaza"]
    )
    
    assert isinstance(team, Team)
    assert len(team.pokemon) == 6
    
    # Check for weather setter
    has_weather_setter = any(
        pokemon.ability in ["Drizzle", "Drought", "Sand Stream", "Snow Warning"]
        for pokemon in team.pokemon
    )
    assert has_weather_setter
    
    # Check role distribution
    roles = builder._get_current_roles(team.pokemon)
    assert roles["sweeper"] >= 2
    assert roles["wallbreaker"] >= 1
    assert roles["tank"] >= 1
    assert roles["support"] >= 1
    assert roles["hazard_setter"] >= 1

def test_get_default_roles(builder):
    """Test getting default role requirements."""
    # Test balanced strategy
    balanced_roles = builder._get_default_roles("balanced")
    assert balanced_roles["sweeper"] == 2
    assert balanced_roles["wallbreaker"] == 1
    assert balanced_roles["tank"] == 1
    assert balanced_roles["support"] == 1
    assert balanced_roles["hazard_setter"] == 1
    
    # Test hyper offense strategy
    ho_roles = builder._get_default_roles("hyper_offense")
    assert ho_roles["sweeper"] == 3
    assert ho_roles["wallbreaker"] == 2
    assert ho_roles["hazard_setter"] == 1
    
    # Test stall strategy
    stall_roles = builder._get_default_roles("stall")
    assert stall_roles["tank"] == 3
    assert stall_roles["support"] == 2
    assert stall_roles["hazard_setter"] == 1
    
    # Test weather strategy
    weather_roles = builder._get_default_roles("weather")
    assert weather_roles["sweeper"] == 2
    assert weather_roles["wallbreaker"] == 1
    assert weather_roles["tank"] == 1
    assert weather_roles["support"] == 1
    assert weather_roles["hazard_setter"] == 1

def test_get_current_roles(builder, sample_core_pokemon):
    """Test getting current role distribution."""
    roles = builder._get_current_roles(sample_core_pokemon)
    assert isinstance(roles, dict)
    assert "sweeper" in roles
    assert "wallbreaker" in roles
    assert "tank" in roles
    assert "support" in roles
    assert "hazard_setter" in roles

def test_get_current_coverage(builder, sample_core_pokemon):
    """Test getting current type coverage."""
    coverage = builder._get_current_coverage(sample_core_pokemon)
    assert isinstance(coverage, dict)
    assert "Electric" in coverage
    assert "Fairy" in coverage

def test_roles_satisfied(builder):
    """Test checking if role requirements are satisfied."""
    current = {
        "sweeper": 2,
        "wallbreaker": 1,
        "tank": 1,
        "support": 1,
        "hazard_setter": 1
    }
    required = {
        "sweeper": 2,
        "wallbreaker": 1,
        "tank": 1
    }
    assert builder._roles_satisfied(current, required)
    
    # Test with unsatisfied requirements
    required["sweeper"] = 3
    assert not builder._roles_satisfied(current, required)

def test_get_next_role(builder):
    """Test getting next role to fill."""
    current = {
        "sweeper": 1,
        "wallbreaker": 1,
        "tank": 0,
        "support": 1,
        "hazard_setter": 1
    }
    required = {
        "sweeper": 2,
        "wallbreaker": 1,
        "tank": 1
    }
    assert builder._get_next_role(current, required) == "sweeper"
    
    # Test when all required roles are filled
    current["sweeper"] = 2
    current["tank"] = 1
    assert builder._get_next_role(current, required) == "support" 