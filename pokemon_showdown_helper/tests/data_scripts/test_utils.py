"""
Tests for the utils module.
"""

import json
from pathlib import Path
import pytest
import requests
from unittest.mock import patch, MagicMock

from data_scripts import utils


def test_download_json(tmp_path):
    """Test downloading and saving JSON data."""
    # Mock response data
    mock_data = {"test": "data"}
    mock_response = MagicMock()
    mock_response.json.return_value = mock_data
    
    # Test successful download
    with patch('requests.get', return_value=mock_response):
        data = utils.download_json("https://example.com/test.json")
        assert data == mock_data
    
    # Test saving to file
    save_path = tmp_path / "test.json"
    with patch('requests.get', return_value=mock_response):
        data = utils.download_json("https://example.com/test.json", save_path)
        assert data == mock_data
        assert save_path.exists()
        with open(save_path) as f:
            saved_data = json.load(f)
        assert saved_data == mock_data
    
    # Test error handling
    with patch('requests.get', side_effect=requests.RequestException):
        with pytest.raises(requests.RequestException):
            utils.download_json("https://example.com/test.json")


def test_to_ps_id():
    """Test conversion of Pokémon names to Showdown IDs."""
    # Test basic cases
    assert utils.to_ps_id("Pikachu") == "pikachu"
    assert utils.to_ps_id("Charizard") == "charizard"
    
    # Test special cases
    assert utils.to_ps_id("Mr. Mime") == "mrmime"
    assert utils.to_ps_id("Nidoran♀") == "nidoranf"
    assert utils.to_ps_id("Nidoran♂") == "nidoranm"
    assert utils.to_ps_id("Type: Null") == "typenull"
    assert utils.to_ps_id("Porygon-Z") == "porygonz"
    assert utils.to_ps_id("Jangmo-o") == "jangmoo"
    
    # Test case insensitivity
    assert utils.to_ps_id("PIKACHU") == "pikachu"
    assert utils.to_ps_id("Mr. MIME") == "mrmime"


def test_clean_name():
    """Test cleaning of names."""
    # Test basic cases
    assert utils.clean_name("Pikachu") == "pikachu"
    assert utils.clean_name("Charizard") == "charizard"
    
    # Test special characters
    assert utils.clean_name("Mr. Mime") == "mr mime"
    assert utils.clean_name("Nidoran♀") == "nidoran"
    assert utils.clean_name("Type: Null") == "type null"
    
    # Test case insensitivity
    assert utils.clean_name("PIKACHU") == "pikachu"
    assert utils.clean_name("Mr. MIME") == "mr mime"
    
    # Test extra spaces
    assert utils.clean_name("  Pikachu  ") == "pikachu"
    assert utils.clean_name("Mr.  Mime") == "mr mime"


@pytest.mark.skip(reason="Selenium tests require browser installation")
def test_init_selenium_driver():
    """Test Selenium WebDriver initialization."""
    # Test headless mode
    driver = utils.init_selenium_driver(headless=True)
    assert driver is not None
    driver.quit()
    
    # Test non-headless mode
    driver = utils.init_selenium_driver(headless=False)
    assert driver is not None
    driver.quit() 