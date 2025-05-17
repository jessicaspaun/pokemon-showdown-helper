"""
Tests for fetch_ps_core_data module parse functions.
"""
import pytest
from data_scripts import fetch_ps_core_data

def test_parse_pokedex_json():
    sample = {
        "pikachu": {
            "num": 25,
            "species": "Pikachu",
            "types": ["Electric"],
            "baseStats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        }
    }
    parsed = fetch_ps_core_data.parse_pokedex_json(sample)
    assert "pikachu" in parsed
    assert parsed["pikachu"]["species"] == "Pikachu"

def test_parse_moves_json():
    sample = {
        "thunderbolt": {
            "num": 85,
            "name": "Thunderbolt",
            "type": "Electric",
            "power": 90,
            "accuracy": 100,
        }
    }
    parsed = fetch_ps_core_data.parse_moves_json(sample)
    assert "thunderbolt" in parsed
    assert parsed["thunderbolt"]["power"] == 90

def test_parse_abilities_json():
    sample = {
        "static": {
            "name": "Static",
            "desc": "May paralyze on contact."
        }
    }
    parsed = fetch_ps_core_data.parse_abilities_json(sample)
    assert "static" in parsed
    assert parsed["static"]["name"] == "Static"

def test_parse_items_json():
    sample = {
        "lightball": {
            "name": "Light Ball",
            "desc": "Doubles Pikachu's Attack and Sp. Atk."
        }
    }
    parsed = fetch_ps_core_data.parse_items_json(sample)
    assert "lightball" in parsed
    assert parsed["lightball"]["name"] == "Light Ball"

def test_parse_learnsets_json():
    sample = {
        "pikachu": {
            "learnset": ["thunderbolt", "quickattack"]
        }
    }
    parsed = fetch_ps_core_data.parse_learnsets_json(sample)
    assert "pikachu" in parsed
    assert "thunderbolt" in parsed["pikachu"]["learnset"]

def test_parse_typechart_json():
    sample = {
        "Electric": {
            "damageTaken": {"Ground": 2, "Flying": 0, "Steel": 1}
        }
    }
    parsed = fetch_ps_core_data.parse_typechart_json(sample)
    assert "Electric" in parsed
    assert "damageTaken" in parsed["Electric"] 