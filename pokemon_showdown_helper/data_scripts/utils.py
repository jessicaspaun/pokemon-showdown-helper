"""
Utility functions for data acquisition and processing.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from data_scripts import constants


def download_json(url: str, save_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Download JSON data from a URL and optionally save it to a file.

    Args:
        url: The URL to download JSON from.
        save_path: Optional path to save the JSON data to.

    Returns:
        The parsed JSON data as a dictionary.

    Raises:
        requests.RequestException: If the download fails.
        json.JSONDecodeError: If the response is not valid JSON.
    """
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return data


def to_ps_id(name: str) -> str:
    """
    Convert a Pokémon name to its Pokémon Showdown ID format.

    Args:
        name: The Pokémon name to convert.

    Returns:
        The Pokémon Showdown ID format of the name.

    Examples:
        >>> to_ps_id("Pikachu")
        'pikachu'
        >>> to_ps_id("Mr. Mime")
        'mrmime'
        >>> to_ps_id("Nidoran♀")
        'nidoranf'
    """
    # Remove special characters and spaces
    name = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
    
    # Handle special cases
    special_cases = {
        'nidoranf': 'nidoran♀',
        'nidoranm': 'nidoran♂',
        'mrmime': 'mr. mime',
        'mimejr': 'mime jr.',
        'typenull': 'type: null',
        'porygonz': 'porygon-z',
        'jangmoo': 'jangmo-o',
        'hakamoo': 'hakamo-o',
        'kommoo': 'kommo-o',
    }
    
    # Check if the cleaned name matches any special cases
    for ps_id, original in special_cases.items():
        if name == ps_id:
            return ps_id
    
    return name


def clean_name(name: str) -> str:
    """
    Clean a name by removing special characters and converting to lowercase.

    Args:
        name: The name to clean.

    Returns:
        The cleaned name.

    Examples:
        >>> clean_name("Pikachu")
        'pikachu'
        >>> clean_name("Mr. Mime")
        'mr mime'
        >>> clean_name("Nidoran♀")
        'nidoran'
    """
    # Remove special characters and convert to lowercase
    return re.sub(r'[^a-zA-Z0-9\s]', '', name.lower()).strip()


def init_selenium_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Initialize a Selenium WebDriver instance.

    Args:
        headless: Whether to run the browser in headless mode.

    Returns:
        A configured Chrome WebDriver instance.

    Note:
        This is a placeholder function. The actual implementation will depend on
        whether we need Selenium for scraping Smogon pages. If we can get all
        the data we need through their API or static pages, we might not need this.
    """
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options) 