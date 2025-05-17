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
    
    # Handle TypeScript files
    if url.endswith('.ts'):
        content = response.text
        
        # Remove export statement and trailing semicolon
        content = re.sub(r'^export const [^=]+ = ', '', content, flags=re.MULTILINE)
        content = re.sub(r';\s*$', '', content, flags=re.MULTILINE)
        
        # Remove comments (both single-line and multi-line)
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*[\s\S]*?\*/', '', content)
        
        # Remove trailing commas before closing braces/brackets
        content = re.sub(r',([ \t\r\n]*[}\]])', r'\1', content)
        
        # Handle string literals
        def replace_string(match):
            s = match.group(1)
            # Escape backslashes and double quotes only
            s = s.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{s}"'
        
        # Convert single-quoted strings to double-quoted strings
        content = re.sub(r"'((?:[^'\\]|\\.)*)'", replace_string, content)
        
        # Quote unquoted property names
        content = re.sub(r'([,{\[]\s*)([a-zA-Z0-9_\-]+)\s*:', r'\1"\2":', content)
        
        # Remove invalid control characters
        content = re.sub(r'[\x00-\x1F\x7F]', '', content)
        
        # Handle TypeScript-specific syntax
        content = re.sub(r':\s*([A-Z][a-zA-Z0-9]*)\s*\[\]', r': []', content)  # Remove type annotations for arrays
        content = re.sub(r':\s*([A-Z][a-zA-Z0-9]*)', r': null', content)  # Replace type annotations with null
        content = re.sub(r'as\s+[A-Z][a-zA-Z0-9]*', '', content)  # Remove type assertions
        
        # Find the object between the first { and the last }
        start = content.find('{')
        end = content.rfind('}') + 1
        if start == -1 or end == 0:
            raise ValueError(f"Could not find JSON object in TypeScript file: {url}")
        
        json_str = content[start:end]
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from {url}")
            print(f"JSON string: {json_str[:200]}...")  # Print first 200 chars for debugging
            # Save the problematic JSON string to a file for inspection
            with open("debug_failed_json.txt", "w") as debug_file:
                debug_file.write(json_str)
            # Print the problematic line and its surrounding context
            lines = json_str.split('\n')
            error_line = e.lineno - 1  # Adjust for 0-indexing
            start_line = max(0, error_line - 2)
            end_line = min(len(lines), error_line + 3)
            print("Problematic line and context:")
            for i in range(start_line, end_line):
                print(f"Line {i + 1}: {lines[i]}")
            raise e
    else:
        data = response.json()
    
    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)
    
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
    # Handle special cases first
    special_cases = {
        'nidoran♀': 'nidoranf',
        'nidoran♂': 'nidoranm',
        'mr. mime': 'mrmime',
        'mime jr.': 'mimejr',
        'type: null': 'typenull',
        'porygon-z': 'porygonz',
        'jangmo-o': 'jangmoo',
        'hakamo-o': 'hakamoo',
        'kommo-o': 'kommoo',
    }
    
    # Check if the name matches any special cases
    name_lower = name.lower()
    for original, ps_id in special_cases.items():
        if name_lower == original:
            return ps_id
    
    # If no special case matches, remove special characters and spaces
    return re.sub(r'[^a-zA-Z0-9]', '', name_lower)


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
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
    # Replace multiple spaces with a single space and strip
    return re.sub(r'\s+', ' ', cleaned).strip()


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