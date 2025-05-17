# Pokémon Showdown Gen 7 OU Team Optimizer & Strategist

A Python-based application that assists Pokémon Showdown players in building and optimizing teams for the Generation 7 OverUsed (Gen 7 OU) metagame.

## Features

- Team suggestion from user's roster against opponent's roster
- Detailed build suggestions for selected Pokémon
- Opponent team prediction based on usage statistics
- Matchup analysis and strategy generation
- Gen 7 OU legality enforcement

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/pokemon-showdown-helper.git
cd pokemon-showdown-helper
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# OR
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

- `data_scripts/`: Scripts for data acquisition and management
- `core_logic/`: Core game mechanics and team analysis logic
- `app/`: Streamlit application code
- `database/`: Database schema and management
- `raw_data/`: Raw data files and caches
- `docs/`: Project documentation
- `tests/`: Test suite

## Development

See `CONTRIBUTING.md` for development guidelines and setup instructions.

## License

[License details to be added] 