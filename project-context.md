# Project: Pokémon Showdown Gen 7 OU Team Optimizer & Strategist

**Last Updated:** May 16, 2025

## 1. Objective

To develop a Python-based application with a Streamlit frontend that assists Pokémon Showdown players in building and optimizing teams for the Generation 7 OverUsed (Gen 7 OU) metagame. The program will suggest the best combination of 6 Pokémon from a user's roster to compete against an opponent's given roster, provide detailed build suggestions for the user's team, analyze the matchup, and offer a strategy for winning. All suggestions and analyses must adhere strictly to Gen 7 OU legality rules.

## 2. Core Features

* **Team Suggestion:**
    * Given a user's roster (larger pool of Pokémon) and an opponent's roster (larger pool), select an optimal team of 6 Pokémon for the user.
    * Focus on countering specific threats on the opponent's likely team and achieving speed control.
* **User's Team Configuration (for the selected 6 Pokémon):**
    * Suggest an initial competitive build (4 moves, 1 item, 1 ability, nature, EVs) for each of the user's 6 selected Pokémon.
    * Allow full customization of these builds via the UI.
    * Implement a (future) advanced EV optimization algorithm to calculate spreads based on specific benchmarks (e.g., outspeeding threats, surviving key attacks, securing KOs).
* **Opponent Team Prediction:**
    * For the opponent's selected/rostered 6 Pokémon, predict their most likely movesets, items, abilities, and EVs based on usage statistics and common Smogon sets.
* **Matchup Analysis & Strategy:**
    * Provide a detailed comparison between the user's configured team and the predicted opponent team.
    * Identify key threats on both sides.
    * Visualize type matchups.
    * Display speed tier comparisons.
    * Highlight potential vulnerabilities for the user's team.
    * Suggest a lead Pokémon for the user.
* **Gen 7 OU Legality Enforcement:**
    * All team suggestions and user configurations must be validated against official Gen 7 OU rules (clauses, banned Pokémon, abilities, items, moves).
    * The UI will provide feedback on illegal selections.

## 3. Technical Stack

* **Backend:** Python
    * **Data Handling/Manipulation:** Pandas
    * **Web Scraping (if necessary for Smogon pages):** Requests, BeautifulSoup4, Selenium (only if dynamic content blocks data)
    * **Database:** SQLite
* **Frontend:** Streamlit
* **Data Sources:**
    * **Primary Foundational Data (Pokémon stats, all moves, abilities, items, learnsets, type chart):** Pokémon Showdown data files (e.g., `pokedex.json`, `moves.json` from `play.pokemonshowdown.com/data/`).
    * **Competitive Sets & Analysis Text:** Smogon Strategy Dex for Gen 7 OU (e.g., `smogon.com/dex/sm/pokemon/`).
    * **Usage Statistics (for opponent modeling & popular sets):** Smogon Usage Statistics "chaos" JSON files for Gen 7 OU.
    * **Format Rules & Banlists:** Pokémon Showdown GitHub repository (`config/formats.ts`, `data/rulesets.ts` or their processed equivalents).

## 4. Key Modules & Architecture (Conceptual)

1.  **Data Manager (`data_manager`):**
    * Scripts to fetch, parse, and store all necessary data into the local SQLite database.
        * `Workspace_ps_core_data.py`: For base Pokémon/move/ability/item data from Showdown JSONs.
        * `Workspace_smogon_analysis_sets.py`: For scraping competitive sets from Smogon Dex pages.
        * `Workspace_usage_stats.py`: For Smogon usage statistics.
        * `Workspace_ps_rules_and_formats.py`: For Gen 7 OU rules and banlists from Showdown config files.
    * `database_setup.py`: Defines and initializes the SQLite schema.
    * `populate_db.py`: Orchestrates data fetching and database population.
    * `constants.py`, `utils.py`: For shared constants and helper functions.

2.  **Team Analyzer (`team_analyzer`):**
    * `pokemon_object.py`: Defines `PokemonInstance` (species with a specific build).
    * `team_object.py`: Defines `Team` (6 `PokemonInstance`s).
    * `damage_calculator.py`: Gen 7 damage calculation logic.
    * `team_validator.py`: Validates teams and Pokémon builds against Gen 7 OU rules.
    * `opponent_modeller.py`: Predicts opponent Pokémon builds.
    * `team_builder_logic.py`: Suggests optimal user team and default builds based on rosters and strategic priorities (threat countering, speed control).
    * `ev_optimizer.py`: (Advanced Feature) Algorithm for complex EV spread optimization.
    * `matchup_analyzer.py`: Generates threat lists, type matchup analysis, speed comparisons, vulnerability reports.
    * `strategy_generator.py`: Suggests leads and basic game plan elements.

3.  **Streamlit Application (`app.py`):**
    * **User Input:**
        * 12 slots (6 user, 6 opponent) for Pokémon selection via searchable dropdowns.
        * Customization for user's 6 Pokémon:
            * Moves (4 searchable dropdowns).
            * Item (searchable dropdown).
            * Ability (searchable dropdown).
            * Nature (dropdown).
            * EVs (6 sliders).
        * "Analyze" button to trigger processing.
    * **Output Display:**
        * User's final team vs. Opponent's predicted team.
        * Legality warnings/feedback.
        * Detailed matchup analysis and strategic advice as outlined above.
    * **Workflow:**
        1.  User inputs their roster and opponent's roster.
        2.  Program suggests an initial team for the user with default builds (or user builds their team from scratch).
        3.  User customizes their team's builds.
        4.  User clicks "Analyze."
        5.  Backend validates the user's team, predicts the opponent's team, performs analysis, and generates strategy.
        6.  Frontend displays results.

## 5. Key Challenges & Considerations

* **Parsing Pokémon Showdown Config Files (`.ts`):** Extracting rules and banlists accurately from TypeScript files requires careful parsing or finding reliable pre-parsed JSON/API sources.
* **Complex EV Optimization:** Implementing a truly "optimal" EV calculation algorithm is a significant sub-project requiring deep game mechanics knowledge and algorithmic design. A phased approach will be taken.
* **Scraping Smogon:** Ensuring robust scraping of Smogon pages if necessary, and handling potential site structure changes over time (though Gen 7 pages are likely stable). Selenium use adds complexity if required.
* **Defining "Best Combination":** Quantifying this based on "countering threats" and "speed control" will require careful heuristic design and potentially weighting different factors.
* **Streamlit State Management:** Managing the state of user selections, team configurations, and analysis results effectively in a multi-step Streamlit application.

## 6. Development Principles

* **DRY (Don't Repeat Yourself):** Minimize redundant code.
* **SOLID:** Adhere to SOLID principles for maintainable and scalable object-oriented design.
* **Meaningful Names:** Use clear and descriptive names for variables, functions, classes, and modules.
* **KISS (Keep It Simple, Stupid):** Favor simpler solutions where possible, avoiding over-engineering, especially in initial versions.
* **Modularity:** Break down the application into logical, loosely coupled modules.
* **Iterative Development:** Start with core functionality and add more complex features (like advanced EV optimization) in later phases.

This document provides a snapshot of the project's goals, structure, and key considerations. It will evolve as development progresses.