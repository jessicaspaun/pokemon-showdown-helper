# Project Task List: Pokémon Showdown Gen 7 OU Optimizer & Strategist

**Legend:**
* `[ ]`: Task to be done
* `[x]`: Task completed (for tracking by the engineer)
* **Principle Reminder:** Notes on applying clean code/design principles.
* **GoF Note:** Potential Gang of Four design pattern applicability.
* **Git Commit:** Suggestion for a commit point.

---

## Phase 0: Project Setup & Initial Configuration

* [x] **Task 0.1:** Create a new repository on GitHub (e.g., `pokemon-showdown-helper`).
    * **Documentation 0.1.1:** Add a link to the repository in project planning documents.
    * **Testing 0.1.2:** Repository created successfully.

* [x] **Task 0.2:** Clone the repository to your local machine.
    * **Testing 0.2.1:** Local repository cloned and `git status` is clean.

* [x] **Task 0.3:** Set up the project directory structure (as outlined previously):
    * `pokemon_showdown_helper/` (root)
        * `data_scripts/`, `core_logic/`, `app/`, `database/`, `raw_data/`, `docs/`, `tests/` (with `__init__.py` in relevant subdirectories)
    * **Documentation 0.3.1:** Create a `README.md` in the root directory with a brief project overview and initial setup instructions (cloning, virtual env).
    * **Testing 0.3.2:** Confirm directory structure is as expected.
    * **Git Commit 0.3.3:** `feat: Initial project structure and README`

* [x] **Task 0.4:** Initialize a Python virtual environment (e.g., `venv` or `conda`).
    * Add `.venv` (or your virtual environment folder name) to a new `.gitignore` file.
    * **Documentation 0.4.1:** Add instructions for virtual environment setup to `README.md`.
    * **Testing 0.4.2:** Activate virtual environment successfully.
    * **Git Commit 0.4.3:** `chore: Add .gitignore and virtual environment setup instructions`

* [x] **Task 0.5:** Create `requirements.txt` and add initial dependencies:
    * `python` (specify version, e.g., 3.9+)
    * `requests`
    * `pandas`
    * `beautifulsoup4`
    * `streamlit`
    * `selenium`
    * **Documentation 0.5.1:** Add `pip install -r requirements.txt` to setup instructions in `README.md`.
    * **Testing 0.5.2:** Install dependencies successfully.
    * **Git Commit 0.5.3:** `feat: Add initial dependencies to requirements.txt`

* [x] **Task 0.6:** Set up basic linting (e.g., `flake8`) and formatting (e.g., `black` or `autopep8`) tools.
    * Add configuration files for these tools (e.g., `setup.cfg`, `.flake8`, `pyproject.toml` for black).
    * **Documentation 0.6.1:** Document chosen tools and relevant commands in `CONTRIBUTING.md` (create this file).
    * **Testing 0.6.2:** Run linters/formatters on initial empty files to ensure setup.
    * **Git Commit 0.6.3:** `chore: Configure linting and formatting tools`

---

## Phase 1: Data Foundation - Data Acquisition & Management (`data_scripts` module)

### Section 1.1: Constants, Utilities, and Database Schema

* [x] **Task 1.1.1:** Implement `data_scripts/constants.py` (URLs, DB paths, `NATURES_DATA`, etc.).
    * **Principle Reminder (DRY):** Centralize all static configurations.
    * **Documentation 1.1.1.1:** Add comments within `constants.py`.
    * **Testing 1.1.1.2:** Basic unit tests in `tests/data_scripts/test_constants.py`.

* [x] **Task 1.1.2:** Implement `data_scripts/utils.py` (`download_json`, `to_ps_id`, `clean_name`, placeholder `init_selenium_driver`).
    * **Principle Reminder (SRP):** Each function with a clear purpose.
    * **Documentation 1.1.2.1:** Add docstrings.
    * **Testing 1.1.2.2:** Unit tests in `tests/data_scripts/test_utils.py`.

* [x] **Task 1.1.3:** Implement `data_scripts/database_setup.py` (all table creations including `Formats`, `FormatRules`, and `populate_natures`).
    * **Principle Reminder (SRP):** Module responsible for DB schema.
    * **Documentation 1.1.3.1:** Create `docs/database_schema.md`. Docstrings in `database_setup.py`.
    * **Testing 1.1.3.2:** Run script, inspect DB, unit tests for schema.
    * **Git Commit 1.1.3.3:** `feat(data): Implement constants, utils, and database schema setup` (Commit after 1.1.1, 1.1.2, 1.1.3 are done and tested together).

### Section 1.2: Fetching and Populating Core Pokémon Showdown Data

* [x] **Task 1.2.1:** Implement `data_scripts/fetch_ps_core_data.py` (fetch and parse functions for pokedex, moves, abilities, items, learnsets, typechart from Showdown JSONs).
    * **Principle Reminder (SRP, KISS):** Focus on one data source per function pair.
    * **Documentation 1.2.1.1:** Docstrings. Document expected JSON structures in `docs/data_sources.md`.
    * **Testing 1.2.1.2:** Unit tests for parsers using local sample JSON files.

* [x] **Task 1.2.2:** Update `data_scripts/populate_db.py` for Core Data:
    * Create `populate_db.py` with `main_populate` orchestrator.
    * Implement functions to insert parsed core data into respective tables (`Pokemon`, `Abilities`, `PokemonAbilities`, `Moves`, `PokemonLearnset`, `Items`).
    * Call `init_database()` from `database_setup.py` at the start of `main_populate`.
    * **Principle Reminder (Idempotency):** Ensure re-runs don't break data.
    * **Documentation 1.2.2.1:** Update `docs/database_schema.md` if needed. Document population order.
    * **Testing 1.2.2.2:** After running `populate_db.py` (with only core data population active), query DB. Robust, order-agnostic unit tests for insertion functions added in `tests/data_scripts/test_populate_db.py`.
    * **Git Commit 1.2.2.3:** `feat(data): Fetch and populate core Pokemon Showdown data (Pokedex, Moves, etc.)`

### Section 1.3: Fetching and Populating Pokémon Showdown Format Rules & Banlists

* [x] **Task 1.3.1:** Implement `data_scripts/fetch_ps_rules_and_formats.py`:
    * `Workspace_ps_formats_ts_raw()`: Downloads `config/formats.ts`.
    * `parse_gen7ou_rules_from_formats_ts()`: Parses TS for Gen 7 OU ruleset and banlist (regex-based parser implemented).
    * **Principle Reminder (KISS):** Prioritize reliable pre-parsed sources if TS parsing is too complex/brittle.
    * **Documentation 1.3.1.1:** Heavily document parsing approach or alternative source.
    * **Testing 1.3.1.2:** Unit test parser with a saved snippet of `formats.ts` or mock JSON. Parser and tests implemented and passing.

* [x] **Task 1.3.2:** Update `data_scripts/populate_db.py` for Format Rules:
    * Add functions to insert parsed rules into `Formats` and `FormatRules`.
    * Integrate into `main_populate`.
    * **Documentation 1.3.2.1:** Document rule storage in `docs/database_schema.md`.
    * **Testing 1.3.2.2:** Query `FormatRules` for "gen7ou" after population.
    * **Git Commit 1.3.2.3:** `feat(data): Fetch and populate Gen7OU format rules and banlists`

### Section 1.4: Fetching and Populating Smogon Analysis Sets

* [ ] **Task 1.4.1:** Implement `data_scripts/fetch_smogon_analysis_sets.py`:
    * `get_gen7ou_pokemon_list()`: Retrieves Pokémon list from DB.
    * `Workspace_pokemon_smogon_page_html()`: Downloads Smogon dex page (requests, with Selenium as fallback if confirmed necessary).
    * `parse_smogon_page_for_sets()`: Parses HTML with BeautifulSoup for competitive sets.
    * **Documentation 1.4.1.1:** Document Smogon HTML structure targeted.
    * **Testing 1.4.1.2:** Unit test parser with local Smogon page HTML samples.

* [ ] **Task 1.4.2:** Update `data_scripts/populate_db.py` for Smogon Analysis Sets:
    * Iterate, fetch, parse, and insert into `Gen7OUSets` (source `smogon_analysis_page`).
    * Handle foreign key resolution and placeholders.
    * **Documentation 1.4.2.1:** Note data source precedence in `docs/data_sources.md`.
    * **Testing 1.4.2.2:** Query `Gen7OUSets` for these sets.
    * **Git Commit 1.4.2.3:** `feat(data): Fetch and populate competitive sets from Smogon analysis pages`

### Section 1.5: Fetching and Populating Smogon Usage Statistics

* [ ] **Task 1.5.1:** Implement `data_scripts/fetch_usage_stats.py`:
    * `Workspace_gen7ou_chaos_data()`: Downloads Gen 7 OU chaos JSON.
    * `parse_chaos_data()`: Parses chaos JSON for top abilities, items, moves, EV spreads per Pokémon.
    * **Documentation 1.5.1.1:** Document chaos JSON structure and EV string parsing in `docs/data_sources.md`.
    * **Testing 1.5.1.2:** Unit test parser with local chaos JSON sample.

* [ ] **Task 1.5.2:** Update `data_scripts/populate_db.py` for Usage Stats Sets:
    * Create `Gen7OUSets` entries from parsed usage stats (source `usage_stats_YYYY-MM`).
    * **Documentation 1.5.2.1:** Clarify derivation of sets from usage stats.
    * **Testing 1.5.2.2:** Query `Gen7OUSets` for usage-derived sets.
    * **Git Commit 1.5.2.3:** `feat(data): Fetch and populate sets derived from Smogon usage statistics`

* [x] **Task 1.5.3 (Overall Data Population Test & Refinement):**
    * Perform comprehensive checks after all data population scripts are integrated into `main_populate`.
    * Refine any parsing logic or DB insertion based on issues found.
    * **Documentation 1.5.3.1:** Created `docs/runbook_data_population.md` with steps to run all scripts and verify.
    * **Testing 1.5.3.2:** Integration test for `main_populate` implemented and passing.
    * **Git Commit 1.5.3.3:** `test(data): Add integration test for main_populate and fix schema for full data population (Task 1.5.3)`

---

## Phase 2: Core Logic Implementation (`core_logic` module)

### Section 2.1: Basic Game Object Representation

* [x] **Task 2.1.1:** Implement `core_logic/pokemon_object.py` (`PokemonInstance` class with stat calculation).
    * **GoF Note (Builder):** Evaluate if Builder pattern is needed for `PokemonInstance` construction if it gets complex.
    * **Documentation 2.1.1.1:** Class/method docstrings.
    * **Testing 2.1.1.2:** Unit tests for `calculate_stats`.

* [x] **Task 2.1.2:** Implement `core_logic/team_object.py` (`Team` class).
    * **Documentation 2.1.2.1:** Class/method docstrings.
    * **Testing 2.1.2.2:** Unit tests for `Team` operations.
    * **Git Commit 2.1.2.3:** `feat(core): Implement PokemonInstance and Team objects`

### Section 2.2: Team Legality Validator

* [x] **Task 2.2.1:** Implement `core_logic/team_validator.py` (`TeamValidator` class/module with all validation checks against DB rules for Gen 7 OU).
    * **Principle Reminder (SRP):** Focus on validation.
    * **Documentation 2.2.1.1:** Detailed docstrings, especially for complex clauses (Baton Pass) and assumptions for dynamic clauses at build time.
    * **Testing 2.2.1.2:** Extensive unit tests for validator with mock rule data.
    * **Git Commit 2.2.1.3:** `feat(core): Implement team legality validator for Gen7OU`

### Section 2.3: Damage Calculator

* [x] **Task 2.3.1:** Implement `core_logic/damage_calculator.py` (Gen 7 damage formula).
    * **Principle Reminder (Accuracy):** Cross-reference with established calculators.
    * **GoF Note (Strategy):** Consider for complex modifier application.
    * **Documentation 2.3.1.1:** Detailed comments on formula and modifiers.
    * **Testing 2.3.1.2:** Unit tests against known damage calculation examples.
    * **Git Commit 2.3.1.3:** `feat(core): Implement Gen7 damage calculator`

### Section 2.4: Opponent Modeller

* [x] **Task 2.4.1:** Implement `core_logic/opponent_modeller.py`:
    * Function/class to take opponent Pokémon names and predict their most likely builds (species, moves, item, ability, nature, EVs) using data from `Gen7OUSets` (prioritizing `usage_stats` source, then `smogon_analysis_page`).
    * Convert these predicted builds into `PokemonInstance` objects.
    * **Documentation 2.4.1.1:** Document logic for selecting "most likely" set.
    * **Testing 2.4.1.2:** Unit tests to ensure it picks high-usage or standard sets from mock DB data.
    * **Git Commit 2.4.1.3:** `feat(core): Implement opponent team modeller`

### Section 2.5: Team Builder Logic (Initial Version)

* [x] **Task 2.5.1:** Implement team builder logic in `core_logic/team_builder_logic.py`
  * [x] Create TeamBuilderLogic class
  * [x] Implement team suggestion based on opponent's team
  * [x] Add threat and defensive scoring
  * [x] Add type effectiveness calculations
  * [x] Add database interactions
  * [x] Add comprehensive tests

### Section 2.6: Matchup Analyzer & Strategy Generator (Initial Version)

* [x] **Task 2.6.1:** Implement `core_logic/matchup_analyzer.py`:
    * Functions to take user's `Team` and opponent's predicted `Team`.
    * Generate:
        * Key threats list (Pokémon that can OHKO/2HKO others, based on damage calculator).
        * Type matchup summary (count weaknesses/resistances for each team).
        * Speed comparison data (list of all Pokémon with their speed stats).
        * Potential vulnerabilities summary for user's team (e.g., common offensive types opponent has that user is weak to).
    * **Documentation 2.6.1.1:** Document data structures returned by analysis functions.
    * **Testing 2.6.1.2:** Unit tests with sample teams, verify outputs.

* [x] **Task 2.6.2:** Implement `core_logic/strategy_generator.py`:
    * Function to take analysis results.
    * Suggest a lead Pokémon for the user based on favorable matchups against likely opponent leads.
    * **Documentation 2.6.2.1:** Document lead suggestion logic.
    * **Testing 2.6.2.2:** Unit tests for lead suggestion.
    * **Git Commit 2.6.2.3:** `feat(core): Implement matchup analyzer and initial strategy generator (lead suggestion)`

### Section 2.7: Move Recommender

* [x] **Task 2.7.1:** Implement MoveRecommender class
  * [x] Add move recommendation logic
  * [x] Add coverage analysis
  * [x] Add priority move identification
  * [x] Add utility move identification
  * [x] Add comprehensive tests

* [x] **Task 2.7.2:** Item Recommender
  * [x] Create ItemRecommender class
  * [x] Implement item recommendation logic
  * [x] Add offensive item suggestions
  * [x] Add defensive item suggestions
  * [x] Add utility item suggestions
  * [x] Add comprehensive tests

### Section 2.8: Team Synergy Analyzer

* [x] **Task 2.8.1:** Team Synergy Analyzer
  * [x] Create TeamSynergyAnalyzer class
  * [x] Implement type synergy analysis
  * [x] Implement role synergy analysis
  * [x] Implement defensive synergy analysis
  * [x] Implement offensive synergy analysis
  * [x] Add comprehensive tests

* [x] **Task 2.8.2:** Team Builder Logic (Advanced Version)
  * [x] Create advanced TeamBuilderLogic class
  * [x] Implement multiple team building strategies
  * [x] Add role-based team building
  * [x] Add weather team support
  * [x] Add comprehensive tests

### Section 2.9: Team Optimizer

* [x] **Task 2.9.1:** Team Optimizer
  * [x] Create TeamOptimizer class
  * [x] Implement team analysis
  * [x] Add type coverage optimization
  * [x] Add role balance optimization
  * [x] Add matchup-based optimization
  * [x] Add comprehensive tests

* [x] **Task 2.9.2:** Team Builder Logic (Final Version)
  * [x] Create final TeamBuilderLogic class
  * [x] Implement multiple team building strategies
  * [x] Add role-based team building
  * [x] Add weather team support
  * [x] Add optimization integration
  * [x] Add comprehensive tests

---

## Phase 3: Streamlit Application (`app` module) - MVP

* [x] **Task 3.1:** Implement Streamlit UI
  * [x] Create main Streamlit application file
  * [x] Implement team building interface
  * [x] Add Pokémon selection and configuration
  * [x] Add team management functionality
  * [x] Integrate core logic modules
  * [x] Add analysis display
  * [x] Create application flow documentation

* [x] **Task 3.2:** Add Team Import/Export
  * [x] Implement team import from Showdown format
  * [x] Add team export to Showdown format
  * [x] Add team templates
  * [x] Add comprehensive tests

---

## Phase 4: Advanced Features & Refinements (Iterative)

### Section 4.1: Advanced EV Optimizer

* [x] **Task 4.1.1:** Research and Design the `EVOptimizer` module in `core_logic/ev_optimizer.py`.
    * Define specific optimization goals (e.g., maximize damage against X, survive Y from Z, outspeed Q).
    * Design algorithm (heuristic-based, iterative, potentially constraint satisfaction or simple optimization).
    * This phase itself will have sub-tasks for algorithm design, implementation, and testing.
    * **Documentation 4.1.1.1:** Created comprehensive docstrings and comments explaining the optimization approach.
    * **Testing 4.1.1.2:** Implemented extensive test suite covering all optimization scenarios.
    * **Git Commit 4.1.1.3:** `feat(core): Implement EV Optimizer with goal-based optimization`

* [ ] **Task 4.1.2 - ...:** Implement and test `EVOptimizer`.

* [ ] **Task 4.1.3:** Integrate "Optimize EVs" button/feature into the Streamlit UI.
    * **Documentation 4.1.X:** Detailed documentation of the EV optimization algorithm and its usage.
    * **Testing 4.1.X:** Rigorous testing of EV optimization results.
    * **Git Commit:** `feat(core): Implement advanced EV optimization algorithm (Phase X)`

### Section 4.2: Enhanced Strategy & Analysis

* [ ] **Task 4.2.1:** Improve `StrategyGenerator` to provide more detailed advice beyond just leads.
* [ ] **Task 4.2.2:** Add more sophisticated visualizations for type matchups or threat analysis.
* [ ] **Task 4.2.X:** User feedback incorporation and general refinements.
    * **Git Commit (multiple):** Commits for each significant enhancement.

---

This provides a very granular breakdown. The engineer can pick up tasks and commit changes progressively. Remember that documentation and testing are integral parts of each development step, not afterthoughts.