"""
Tests for the TeamIO class.
"""
import pytest
from app.team_io import TeamIO
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team

@pytest.fixture
def team_io():
    return TeamIO()

@pytest.fixture
def sample_showdown_team():
    return """Tapu Koko @ Life Orb
Ability: Electric Surge
Level: 100
EVs: 252 Atk / 4 SpA / 252 Spe
Naive Nature
- Wild Charge
- Brave Bird
- Hidden Power Ice
- U-turn

Landorus-Therian @ Choice Scarf
Ability: Intimidate
Level: 100
EVs: 252 Atk / 4 Def / 252 Spe
Jolly Nature
- Earthquake
- U-turn
- Stone Edge
- Defog"""

@pytest.fixture
def sample_team():
    tapu_koko = PokemonInstance(
        species="Tapu Koko",
        level=100,
        base_stats={
            'hp': 70,
            'atk': 115,
            'def': 85,
            'spa': 95,
            'spd': 75,
            'spe': 130
        },
        iv={'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31},
        ev={'hp': 0, 'atk': 252, 'def': 0, 'spa': 4, 'spd': 0, 'spe': 252},
        nature='Naive',
        ability='Electric Surge',
        item='Life Orb',
        types=['Electric', 'Fairy'],
        moves=['Wild Charge', 'Brave Bird', 'Hidden Power Ice', 'U-turn']
    )
    
    landorus = PokemonInstance(
        species="Landorus-Therian",
        level=100,
        base_stats={
            'hp': 89,
            'atk': 145,
            'def': 90,
            'spa': 105,
            'spd': 80,
            'spe': 91
        },
        iv={'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31},
        ev={'hp': 0, 'atk': 252, 'def': 4, 'spa': 0, 'spd': 0, 'spe': 252},
        nature='Jolly',
        ability='Intimidate',
        item='Choice Scarf',
        types=['Ground', 'Flying'],
        moves=['Earthquake', 'U-turn', 'Stone Edge', 'Defog']
    )
    
    return Team([tapu_koko, landorus])

def test_import_from_showdown(team_io, sample_showdown_team):
    """Test importing a team from Showdown format."""
    pokemon_list = team_io.import_from_showdown(sample_showdown_team)
    
    assert len(pokemon_list) == 2
    
    # Check Tapu Koko
    koko = pokemon_list[0]
    assert koko.species == "Tapu Koko"
    assert koko.item == "Life Orb"
    assert koko.ability == "Electric Surge"
    assert koko.level == 100
    assert koko.nature == "Naive"
    assert koko.ev == {'hp': 0, 'atk': 252, 'def': 0, 'spa': 4, 'spd': 0, 'spe': 252}
    assert koko.moves == ['Wild Charge', 'Brave Bird', 'Hidden Power Ice', 'U-turn']
    
    # Check Landorus-Therian
    lando = pokemon_list[1]
    assert lando.species == "Landorus-Therian"
    assert lando.item == "Choice Scarf"
    assert lando.ability == "Intimidate"
    assert lando.level == 100
    assert lando.nature == "Jolly"
    assert lando.ev == {'hp': 0, 'atk': 252, 'def': 4, 'spa': 0, 'spd': 0, 'spe': 252}
    assert lando.moves == ['Earthquake', 'U-turn', 'Stone Edge', 'Defog']

def test_export_to_showdown(team_io, sample_team):
    """Test exporting a team to Showdown format."""
    showdown_text = team_io.export_to_showdown(sample_team)
    
    # Verify the exported text contains key information
    assert "Tapu Koko @ Life Orb" in showdown_text
    assert "Ability: Electric Surge" in showdown_text
    assert "EVs: 252 ATK / 4 SPA / 252 SPE" in showdown_text
    assert "Naive Nature" in showdown_text
    assert "- Wild Charge" in showdown_text
    
    assert "Landorus-Therian @ Choice Scarf" in showdown_text
    assert "Ability: Intimidate" in showdown_text
    assert "EVs: 252 ATK / 4 DEF / 252 SPE" in showdown_text
    assert "Jolly Nature" in showdown_text
    assert "- Earthquake" in showdown_text

def test_import_export_roundtrip(team_io, sample_team):
    """Test that importing and exporting a team preserves all information."""
    # Export the team
    showdown_text = team_io.export_to_showdown(sample_team)
    
    # Import it back
    pokemon_list = team_io.import_from_showdown(showdown_text)
    imported_team = Team(pokemon_list)
    
    # Compare the teams
    assert len(imported_team.pokemon) == len(sample_team.pokemon)
    
    for original, imported in zip(sample_team.pokemon, imported_team.pokemon):
        assert original.species == imported.species
        assert original.item == imported.item
        assert original.ability == imported.ability
        assert original.level == imported.level
        assert original.nature == imported.nature
        assert original.ev == imported.ev
        assert original.iv == imported.iv
        assert original.moves == imported.moves

def test_template_operations(team_io, sample_team):
    """Test saving and loading team templates."""
    template_name = "Test Template"
    
    # Save the team as a template
    team_io.save_as_template(sample_team, template_name)
    
    # Get available templates
    templates = team_io.get_available_templates()
    assert template_name in templates
    
    # Load the template
    pokemon_list = team_io.import_from_template(template_name)
    imported_team = Team(pokemon_list)
    
    # Compare the teams
    assert len(imported_team.pokemon) == len(sample_team.pokemon)
    
    for original, imported in zip(sample_team.pokemon, imported_team.pokemon):
        assert original.species == imported.species
        assert original.item == imported.item
        assert original.ability == imported.ability
        assert original.level == imported.level
        assert original.nature == imported.nature
        assert original.ev == imported.ev
        assert original.iv == imported.iv
        assert original.moves == imported.moves

def test_parse_evs(team_io):
    """Test parsing EV lines from Showdown format."""
    ev_line = "EVs: 252 Atk / 4 SpA / 252 Spe"
    evs = team_io._parse_evs(ev_line)
    
    assert evs == {
        'hp': 0,
        'atk': 252,
        'def': 0,
        'spa': 4,
        'spd': 0,
        'spe': 252
    }

def test_parse_ivs(team_io):
    """Test parsing IV lines from Showdown format."""
    iv_line = "IVs: 0 Atk / 30 SpA"
    ivs = team_io._parse_ivs(iv_line)
    
    assert ivs == {
        'hp': 31,
        'atk': 0,
        'def': 31,
        'spa': 30,
        'spd': 31,
        'spe': 31
    }

def test_format_evs(team_io):
    """Test formatting EVs for Showdown export."""
    evs = {
        'hp': 0,
        'atk': 252,
        'def': 0,
        'spa': 4,
        'spd': 0,
        'spe': 252
    }
    
    ev_str = team_io._format_evs(evs)
    assert ev_str == "252 ATK / 4 SPA / 252 SPE"

def test_format_ivs(team_io):
    """Test formatting IVs for Showdown export."""
    ivs = {
        'hp': 31,
        'atk': 0,
        'def': 31,
        'spa': 30,
        'spd': 31,
        'spe': 31
    }
    
    iv_str = team_io._format_ivs(ivs)
    assert iv_str == "0 ATK / 30 SPA" 