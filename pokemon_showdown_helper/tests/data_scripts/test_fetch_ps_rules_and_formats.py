import pytest
from data_scripts import fetch_ps_rules_and_formats
from unittest.mock import patch, Mock

SAMPLE_FORMATS_TS = """
export const Formats: FormatList = [
  {
    name: "[Gen 7] OU",
    desc: "Smogon OU (OverUsed)",
    ruleset: [
      'Standard',
      'Team Preview',
      'Sleep Clause Mod',
      'Species Clause',
      'Evasion Moves Clause',
      'Endless Battle Clause',
      'HP Percentage Mod',
      'Mega Rayquaza Clause',
    ],
    banlist: [
      'Aegislash',
      'Blaziken',
      'Genesect',
      'Greninja',
      'Hoopa-Unbound',
      'Kangaskhanite',
      'Lucarionite',
      'Mawilite',
      'Medichamite',
      'Metagrossite',
      'Pheromosa',
      'Shadow Tag',
      'Speed Boost',
      'Swagger',
    ],
  },
  // ... other formats ...
];
"""

def test_parse_gen7ou_rules_from_formats_ts_extracts_rules_and_banlist():
    result = fetch_ps_rules_and_formats.parse_gen7ou_rules_from_formats_ts(SAMPLE_FORMATS_TS)
    assert result["ruleset"] == [
        'Standard',
        'Team Preview',
        'Sleep Clause Mod',
        'Species Clause',
        'Evasion Moves Clause',
        'Endless Battle Clause',
        'HP Percentage Mod',
        'Mega Rayquaza Clause',
    ]
    assert result["banlist"] == [
        'Aegislash',
        'Blaziken',
        'Genesect',
        'Greninja',
        'Hoopa-Unbound',
        'Kangaskhanite',
        'Lucarionite',
        'Mawilite',
        'Medichamite',
        'Metagrossite',
        'Pheromosa',
        'Shadow Tag',
        'Speed Boost',
        'Swagger',
    ]

@patch('requests.get')
def test_workspace_ps_formats_ts_raw(mock_get, tmp_path):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = 'test content'
    mock_get.return_value = mock_response
    # Test return value
    content = fetch_ps_rules_and_formats.workspace_ps_formats_ts_raw()
    assert content == 'test content'
    # Test saving to file
    save_path = tmp_path / 'formats.ts'
    content2 = fetch_ps_rules_and_formats.workspace_ps_formats_ts_raw(save_path)
    assert save_path.read_text(encoding='utf-8') == 'test content' 