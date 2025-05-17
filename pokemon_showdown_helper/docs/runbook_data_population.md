# Data Population Runbook

This document outlines the process for populating the database with all required data for the Pokémon Showdown Gen 7 OU Optimizer & Strategist.

## Prerequisites

1. Python 3.9+ installed
2. Virtual environment set up and activated
3. All dependencies installed (`pip install -r requirements.txt`)
4. SQLite3 installed (usually comes with Python)

## Database Population Process

### 1. Initial Setup

The database population process is handled by the `main_populate` function in `data_scripts/populate_db.py`. This function orchestrates the entire data population process in the following order:

1. Core Pokémon Showdown Data
   - Pokedex data (species, types, base stats)
   - Moves data
   - Abilities data
   - Items data
   - Learnsets data
   - Typechart data

2. Format Rules & Banlists
   - Gen 7 OU format rules
   - Banlist

3. Smogon Analysis Sets
   - Competitive sets from Smogon analysis pages
   - Includes moves, abilities, items, natures, and EVs

4. Usage Statistics Sets
   - Sets derived from Smogon usage statistics
   - Includes top abilities, items, moves, and EV spreads

### 2. Running the Population Script

To populate the database, run:

```bash
python -m data_scripts.populate_db
```

This will:
1. Create a new SQLite database if it doesn't exist
2. Create all necessary tables
3. Fetch and populate all data types
4. Handle any errors during the process

### 3. Verification Steps

After running the population script, verify the data using the following SQL queries:

```sql
-- Check core data
SELECT COUNT(*) FROM Pokemon;  -- Should be > 0
SELECT COUNT(*) FROM Moves;    -- Should be > 0
SELECT COUNT(*) FROM Abilities;  -- Should be > 0
SELECT COUNT(*) FROM Items;    -- Should be > 0
SELECT COUNT(*) FROM PokemonLearnset;  -- Should be > 0
SELECT COUNT(*) FROM Typechart;  -- Should be > 0

-- Check format rules
SELECT * FROM FormatRules WHERE format_id = 'gen7ou';

-- Check competitive sets
SELECT COUNT(*) FROM Gen7OUSets;  -- Should be > 0
SELECT DISTINCT source FROM Gen7OUSets;  -- Should include both 'smogon_analysis_page' and 'usage_stats_YYYY-MM'
```

### 4. Troubleshooting

If you encounter issues:

1. Check the error messages in the console
2. Verify your internet connection (required for fetching data)
3. Check if the Smogon website is accessible
4. Verify that all required Python packages are installed
5. Check the database file permissions

### 5. Data Sources

The data is fetched from the following sources:

1. Pokémon Showdown JSON files (core data)
2. Pokémon Showdown formats.ts (rules and banlists)
3. Smogon analysis pages (competitive sets)
4. Smogon usage statistics (chaos data)

### 6. Maintenance

The database should be repopulated:
- When new Pokémon Showdown data is released
- When Smogon analysis pages are updated
- When new usage statistics are available
- If the database becomes corrupted

To repopulate, simply run the population script again. The script is idempotent and will handle updates appropriately.

## Testing

Run the integration tests to verify the data population process:

```bash
python -m pytest tests/data_scripts/test_populate_db.py -v
```

This will run all tests, including the comprehensive integration test that verifies all data types are correctly populated. 