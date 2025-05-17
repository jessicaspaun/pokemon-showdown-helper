"""
Tests for the final version of the team builder logic module.
"""
import pytest
from core_logic.team_builder_logic_final import TeamBuilderLogicFinal
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team

@pytest.fixture
def builder():
    return TeamBuilderLogicFinal()

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
        )
    ])

def test_build_balanced_team(builder, sample_core_pokemon):
    """Test building a balanced team."""
    team = builder.build_team(
        strategy="balanced",
        core_pokemon=sample_core_pokemon
    )
    
    assert isinstance(team, Team)
    assert len(team.pokemon) == 6
    assert team.pokemon[0].species == "Tapu Koko"
    
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
        core_pokemon=sample_core_pokemon
    )
    
    assert isinstance(team, Team)
    assert len(team.pokemon) == 6
    assert team.pokemon[0].species == "Tapu Koko"
    
    # Check role distribution
    roles = builder._get_current_roles(team.pokemon)
    assert roles["sweeper"] >= 3
    assert roles["wallbreaker"] >= 2
    assert roles["hazard_setter"] >= 1

def test_build_stall_team(builder, sample_core_pokemon):
    """Test building a stall team."""
    team = builder.build_team(
        strategy="stall",
        core_pokemon=sample_core_pokemon
    )
    
    assert isinstance(team, Team)
    assert len(team.pokemon) == 6
    assert team.pokemon[0].species == "Tapu Koko"
    
    # Check role distribution
    roles = builder._get_current_roles(team.pokemon)
    assert roles["tank"] >= 3
    assert roles["support"] >= 2
    assert roles["hazard_setter"] >= 1

def test_build_weather_team(builder, sample_core_pokemon):
    """Test building a weather team."""
    team = builder.build_team(
        strategy="weather",
        core_pokemon=sample_core_pokemon
    )
    
    assert isinstance(team, Team)
    assert len(team.pokemon) == 6
    assert team.pokemon[0].species == "Tapu Koko"
    
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

def test_build_team_with_opponent(builder, sample_core_pokemon, sample_opponent_team):
    """Test building a team with opponent consideration."""
    team = builder.build_team(
        strategy="balanced",
        core_pokemon=sample_core_pokemon,
        opponent_team=sample_opponent_team
    )
    
    assert isinstance(team, Team)
    assert len(team.pokemon) == 6
    assert team.pokemon[0].species == "Tapu Koko"

def test_build_team_with_banned_pokemon(builder, sample_core_pokemon):
    """Test building a team with banned Pokémon."""
    banned = ["Landorus-Therian", "Magearna", "Heatran"]
    team = builder.build_team(
        strategy="balanced",
        core_pokemon=sample_core_pokemon,
        banned_pokemon=banned
    )
    
    assert isinstance(team, Team)
    assert len(team.pokemon) == 6
    assert team.pokemon[0].species == "Tapu Koko"
    
    # Check that banned Pokémon are not in the team
    for pokemon in team.pokemon:
        assert pokemon.species not in banned

def test_build_team_with_custom_roles(builder, sample_core_pokemon):
    """Test building a team with custom role requirements."""
    custom_roles = {
        "sweeper": 3,
        "wallbreaker": 2,
        "tank": 1
    }
    team = builder.build_team(
        strategy="balanced",
        core_pokemon=sample_core_pokemon,
        required_roles=custom_roles
    )
    
    assert isinstance(team, Team)
    assert len(team.pokemon) == 6
    assert team.pokemon[0].species == "Tapu Koko"
    
    # Check role distribution
    roles = builder._get_current_roles(team.pokemon)
    assert roles["sweeper"] >= 3
    assert roles["wallbreaker"] >= 2
    assert roles["tank"] >= 1

def test_get_default_roles(builder):
    """Test getting default role requirements."""
    balanced_roles = builder._get_default_roles("balanced")
    assert balanced_roles["sweeper"] == 2
    assert balanced_roles["wallbreaker"] == 1
    assert balanced_roles["tank"] == 1
    assert balanced_roles["support"] == 1
    assert balanced_roles["hazard_setter"] == 1
    
    hyper_offense_roles = builder._get_default_roles("hyper_offense")
    assert hyper_offense_roles["sweeper"] == 3
    assert hyper_offense_roles["wallbreaker"] == 2
    assert hyper_offense_roles["hazard_setter"] == 1
    
    stall_roles = builder._get_default_roles("stall")
    assert stall_roles["tank"] == 3
    assert stall_roles["support"] == 2
    assert stall_roles["hazard_setter"] == 1

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
    
    required["sweeper"] = 3
    assert not builder._roles_satisfied(current, required)

def test_get_next_role(builder):
    """Test getting the next role to fill."""
    current = {
        "sweeper": 1,
        "wallbreaker": 1,
        "tank": 0
    }
    required = {
        "sweeper": 2,
        "wallbreaker": 1,
        "tank": 1
    }
    assert builder._get_next_role(current, required) == "sweeper"
    
    current["sweeper"] = 2
    assert builder._get_next_role(current, required) == "tank"

def test_calculate_coverage_score(builder, sample_core_pokemon):
    """Test calculating type coverage score."""
    coverage = {"Electric": 1.0, "Fairy": 1.0}
    score = builder._calculate_coverage_score(sample_core_pokemon[0], coverage)
    assert isinstance(score, float)
    assert 0 <= score <= 1

def test_calculate_role_fit_score(builder, sample_core_pokemon):
    """Test calculating role fit score."""
    score = builder._calculate_role_fit_score(sample_core_pokemon[0])
    assert isinstance(score, float)
    assert 0 <= score <= 1

def test_calculate_synergy_score(builder, sample_core_pokemon):
    """Test calculating team synergy score."""
    score = builder._calculate_synergy_score(sample_core_pokemon[0], sample_core_pokemon)
    assert isinstance(score, float)
    assert 0 <= score <= 1

def test_calculate_offensive_score(builder, sample_core_pokemon):
    """Test calculating offensive score."""
    score = builder._calculate_offensive_score(sample_core_pokemon[0])
    assert isinstance(score, float)
    assert 0 <= score <= 1

def test_calculate_defensive_score(builder, sample_core_pokemon):
    """Test calculating defensive score."""
    score = builder._calculate_defensive_score(sample_core_pokemon[0])
    assert isinstance(score, float)
    assert 0 <= score <= 1

def test_calculate_weather_abuse_score(builder, sample_core_pokemon):
    """Test calculating weather abuse score."""
    score = builder._calculate_weather_abuse_score(sample_core_pokemon[0])
    assert isinstance(score, float)
    assert 0 <= score <= 1 