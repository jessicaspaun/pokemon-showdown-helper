# Streamlit Application Flow and State Management

## Overview

The Pokémon Showdown Helper Streamlit application provides an interactive interface for building and analyzing Gen 7 OU teams. This document outlines the application's structure, state management, and user flow.

## Application Structure

### Main Components

1. **Sidebar (Team Builder)**
   - Pokémon selection dropdown
   - Nature selection dropdown
   - Ability selection dropdown
   - Item selection dropdown
   - Move selection multiselect (4 moves required)
   - EV sliders for all stats
   - Add Pokémon button

2. **Main Content Area**
   - Your Team display (left column)
   - Opponent's Team display (right column)
   - Team Analysis section (bottom)

### State Management

The application uses Streamlit's session state to maintain data between reruns:

```python
# Session state variables
st.session_state.user_team = []  # List of PokemonInstance objects
st.session_state.opponent_team = []  # List of PokemonInstance objects
st.session_state.analysis_results = None  # Analysis results cache
```

## User Flow

1. **Team Building**
   - User selects a Pokémon from the dropdown
   - User configures the Pokémon's:
     - Nature
     - Ability (filtered based on selected Pokémon)
     - Item
     - Moves (must select exactly 4)
     - EVs (using sliders)
   - User clicks "Add Pokémon" to add to their team
   - Process repeats until team has 6 Pokémon

2. **Team Management**
   - Each Pokémon in the team is displayed in an expandable section
   - Users can view details and remove Pokémon
   - Team validation occurs when analysis is requested

3. **Analysis**
   - Available when team has 6 Pokémon
   - Performs multiple analyses:
     - Team validation
     - Team synergy analysis
     - Matchup analysis (if opponent team provided)
     - Strategy suggestions
     - Move recommendations
     - Item recommendations

## Database Integration

The application interacts with the SQLite database through several functions:

- `get_pokemon_list()`: Retrieves all Pokémon names
- `get_moves_for_pokemon()`: Gets available moves for a Pokémon
- `get_items()`: Retrieves all items
- `get_abilities_for_pokemon()`: Gets available abilities for a Pokémon

## Error Handling

The application includes several validation checks:

1. **Move Selection**
   - Ensures exactly 4 moves are selected
   - Shows error message if incorrect number of moves

2. **Team Size**
   - Requires 6 Pokémon for analysis
   - Shows warning if team is incomplete

3. **Team Validation**
   - Checks team legality using TeamValidator
   - Displays validation errors if team is invalid

## Analysis Components

When analysis is requested, the application:

1. Creates Team objects from session state
2. Initializes all necessary analyzers
3. Performs validation
4. If valid, runs:
   - Team synergy analysis
   - Matchup analysis (if opponent team exists)
   - Strategy generation
   - Move recommendations
   - Item recommendations

## UI Updates

The application uses Streamlit's reactive framework to update the UI:

- State changes trigger automatic reruns
- Results are displayed in real-time
- Error messages and success notifications provide feedback
- Expanders organize information hierarchically

## Future Improvements

Potential enhancements to consider:

1. **Performance Optimization**
   - Cache database queries
   - Implement lazy loading for large datasets

2. **User Experience**
   - Add team import/export functionality
   - Implement team templates
   - Add visual type effectiveness charts

3. **Analysis Features**
   - Add EV optimization
   - Implement team building suggestions
   - Add battle simulation capabilities 