"""
Tests for the constants module.
"""

import os
from pathlib import Path
import pytest
from data_scripts import constants

def test_directory_paths():
    """Test that all required directories exist."""
    assert constants.DB_DIR.exists()
    assert constants.RAW_DATA_DIR.exists()
    assert constants.POKEMON_SHOWDOWN_RAW_DIR.exists()
    assert constants.SMOGON_RAW_DIR.exists()

def test_urls():
    """Test that all URLs are properly formatted."""
    assert constants.POKEMON_SHOWDOWN_BASE_URL.startswith("https://")
    assert constants.SMOGON_BASE_URL.startswith("https://")
    assert constants.POKEDEX_URL.startswith(constants.POKEMON_SHOWDOWN_BASE_URL)
    assert constants.MOVES_URL.startswith(constants.POKEMON_SHOWDOWN_BASE_URL)
    assert constants.ABILITIES_URL.startswith(constants.POKEMON_SHOWDOWN_BASE_URL)
    assert constants.ITEMS_URL.startswith(constants.POKEMON_SHOWDOWN_BASE_URL)
    assert constants.LEARNSETS_URL.startswith(constants.POKEMON_SHOWDOWN_BASE_URL)
    assert constants.TYPECHART_URL.startswith(constants.POKEMON_SHOWDOWN_BASE_URL)
    assert constants.SMOGON_USAGE_STATS_URL.startswith("https://")

def test_natures_data():
    """Test that nature data is properly structured."""
    # Test that all natures have valid stat modifications
    valid_stats = {"atk", "def", "spa", "spd", "spe"}
    for nature, modifiers in constants.NATURES_DATA.items():
        # Check that all modified stats are valid
        for stat in modifiers:
            assert stat in valid_stats
        # Check that modifier values are correct
        for modifier in modifiers.values():
            assert modifier in {0.9, 1.1} 