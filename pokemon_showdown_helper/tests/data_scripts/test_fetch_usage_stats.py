"""
Tests for the fetch_usage_stats module.
"""
import pytest
from data_scripts import fetch_usage_stats

def test_parse_chaos_data_basic():
    # Sample chaos JSON structure
    chaos_data = {
        "data": {
            "Pikachu": {
                "Abilities": {
                    "Static": {"usage": 0.7},
                    "Lightning Rod": {"usage": 0.3}
                },
                "Items": {
                    "Light Ball": {"usage": 0.8},
                    "Choice Scarf": {"usage": 0.2}
                },
                "Moves": {
                    "Thunderbolt": {"usage": 0.9},
                    "Volt Tackle": {"usage": 0.1}
                },
                "Spreads": {
                    "Timid:252/0/0/252/4/0": {"usage": 0.6},
                    "Jolly:0/252/0/0/4/252": {"usage": 0.4}
                }
            }
        }
    }
    result = fetch_usage_stats.parse_chaos_data(chaos_data)
    assert "Pikachu" in result
    pikachu = result["Pikachu"]
    # Abilities sorted by usage
    assert pikachu["top_abilities"][0][0] == "Static"
    assert pikachu["top_abilities"][1][0] == "Lightning Rod"
    # Items sorted by usage
    assert pikachu["top_items"][0][0] == "Light Ball"
    assert pikachu["top_items"][1][0] == "Choice Scarf"
    # Moves sorted by usage
    assert pikachu["top_moves"][0][0] == "Thunderbolt"
    assert pikachu["top_moves"][1][0] == "Volt Tackle"
    # Spreads sorted by usage
    assert pikachu["top_spreads"][0][0] == "Timid:252/0/0/252/4/0"
    assert pikachu["top_spreads"][1][0] == "Jolly:0/252/0/0/4/252"

def test_parse_chaos_data_empty():
    chaos_data = {"data": {}}
    result = fetch_usage_stats.parse_chaos_data(chaos_data)
    assert result == {}

def test_parse_chaos_data_missing_keys():
    chaos_data = {"data": {"Pikachu": {}}}
    result = fetch_usage_stats.parse_chaos_data(chaos_data)
    assert "Pikachu" in result
    assert result["Pikachu"]["top_abilities"] == []
    assert result["Pikachu"]["top_items"] == []
    assert result["Pikachu"]["top_moves"] == []
    assert result["Pikachu"]["top_spreads"] == [] 