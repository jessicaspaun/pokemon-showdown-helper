"""
Main Streamlit application for the Pokémon Showdown Helper.
"""
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from typing import List, Dict, Optional
import pandas as pd
from sqlalchemy import text
from core_logic.pokemon_object import PokemonInstance
from core_logic.team_object import Team
from core_logic.team_validator import TeamValidator
from core_logic.team_builder_logic_final import TeamBuilderLogicFinal
from core_logic.opponent_modeller import OpponentModeller
from core_logic.matchup_analyzer import MatchupAnalyzer
from core_logic.strategy_generator import StrategyGenerator
from core_logic.move_recommender import MoveRecommender
from core_logic.item_recommender import ItemRecommender
from core_logic.team_synergy_analyzer import TeamSynergyAnalyzer
from core_logic.team_optimizer import TeamOptimizer
from core_logic.ev_optimizer import EVOptimizer, EVOptimizationGoal
from data_scripts.database import get_db_session
from app.team_io import TeamIO

# Initialize session state
if 'user_team' not in st.session_state:
    st.session_state.user_team = []
if 'opponent_team' not in st.session_state:
    st.session_state.opponent_team = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'optimized_evs' not in st.session_state:
    st.session_state.optimized_evs = None
if 'optimization_goals' not in st.session_state:
    st.session_state.optimization_goals = []

# Initialize team IO and EV optimizer
team_io = TeamIO()
ev_optimizer = EVOptimizer()

def get_pokemon_list() -> List[str]:
    """Get list of all Pokémon from database."""
    with get_db_session() as session:
        result = session.execute(text("SELECT name FROM Pokemon ORDER BY name"))
        return [row[0] for row in result]

def get_moves_for_pokemon(pokemon_name: str) -> List[str]:
    """Get list of moves for a specific Pokémon."""
    with get_db_session() as session:
        result = session.execute(text("""
            SELECT m.name 
            FROM Moves m
            JOIN PokemonLearnset pl ON m.id = pl.move_id
            JOIN Pokemon p ON pl.pokemon_id = p.id
            WHERE p.name = :pokemon_name
            ORDER BY m.name
        """), {"pokemon_name": pokemon_name})
        return [row[0] for row in result]

def get_items() -> List[str]:
    """Get list of all items from database."""
    with get_db_session() as session:
        result = session.execute(text("SELECT name FROM Items ORDER BY name"))
        return [row[0] for row in result]

def get_abilities_for_pokemon(pokemon_name: str) -> List[str]:
    """Get list of abilities for a specific Pokémon."""
    with get_db_session() as session:
        result = session.execute(text("""
            SELECT a.name 
            FROM Abilities a
            JOIN PokemonAbilities pa ON a.id = pa.ability_id
            JOIN Pokemon p ON pa.pokemon_id = p.id
            WHERE p.name = :pokemon_name
            ORDER BY a.name
        """), {"pokemon_name": pokemon_name})
        return [row[0] for row in result]

def get_natures() -> List[str]:
    """Get list of all natures from database."""
    with get_db_session() as session:
        result = session.execute(text("SELECT name FROM Natures ORDER BY name"))
        return [row[0] for row in result]

def get_usage_stats_sets(pokemon_name: str) -> List[Dict]:
    """Get usage statistics sets for a specific Pokémon."""
    with get_db_session() as session:
        result = session.execute(text("""
            SELECT * FROM Gen7OUSets 
            WHERE pokemon_name = :pokemon_name AND source LIKE 'usage_stats_%'
            ORDER BY usage_percentage DESC
        """), {"pokemon_name": pokemon_name})
        return [dict(row) for row in result]

def get_analysis_sets(pokemon_name: str) -> List[Dict]:
    """Get analysis sets for a specific Pokémon."""
    with get_db_session() as session:
        result = session.execute(text("""
            SELECT * FROM Gen7OUSets 
            WHERE pokemon_name = :pokemon_name AND source = 'smogon_analysis_page'
        """), {"pokemon_name": pokemon_name})
        return [dict(row) for row in result]

def create_pokemon_instance(
    species: str,
    level: int,
    nature: str,
    ability: str,
    item: str,
    moves: List[str],
    evs: Dict[str, int]
) -> PokemonInstance:
    """Create a PokemonInstance from user input."""
    with get_db_session() as session:
        result = session.execute(text("""
            SELECT hp, atk, def, spa, spd, spe, type1, type2
            FROM Pokemon
            WHERE name = :species
        """), {"species": species})
        row = result.fetchone()
        
        return PokemonInstance(
            species=species,
            level=level,
            base_stats={
                'hp': row[0],
                'atk': row[1],
                'def': row[2],
                'spa': row[3],
                'spd': row[4],
                'spe': row[5]
            },
            iv={'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31},
            ev=evs,
            nature=nature,
            ability=ability,
            item=item,
            types=[row[6]] + ([row[7]] if row[7] else []),
            moves=moves
        )

def main():
    st.title("Pokémon Showdown Helper")
    st.write("Build and analyze your Gen 7 OU team!")
    
    # Sidebar for team building
    with st.sidebar:
        st.header("Team Builder")
        
        # Team import/export section
        st.subheader("Import/Export")
        
        # Import from Showdown
        showdown_text = st.text_area("Import from Showdown", height=200)
        if st.button("Import Team"):
            try:
                pokemon_list = team_io.import_from_showdown(showdown_text)
                st.session_state.user_team = pokemon_list
                st.success("Team imported successfully!")
            except Exception as e:
                st.error(f"Error importing team: {str(e)}")
        
        # Export to Showdown
        if st.session_state.user_team:
            if st.button("Export to Showdown"):
                team = Team(st.session_state.user_team)
                showdown_text = team_io.export_to_showdown(team)
                st.text_area("Exported Team", showdown_text, height=200)
        
        # Team templates
        st.subheader("Team Templates")
        templates = team_io.get_available_templates()
        if templates:
            selected_template = st.selectbox("Load Template", templates)
            if st.button("Load Template"):
                try:
                    pokemon_list = team_io.import_from_template(selected_template)
                    st.session_state.user_team = pokemon_list
                    st.success(f"Loaded template: {selected_template}")
                except Exception as e:
                    st.error(f"Error loading template: {str(e)}")
        
        if st.session_state.user_team:
            template_name = st.text_input("Save as Template")
            if st.button("Save Template") and template_name:
                try:
                    team = Team(st.session_state.user_team)
                    team_io.save_as_template(team, template_name)
                    st.success(f"Saved template: {template_name}")
                except Exception as e:
                    st.error(f"Error saving template: {str(e)}")
        
        # EV Optimization section
        if st.session_state.user_team:
            st.divider()
            st.subheader("EV Optimization")
            
            # Select Pokémon to optimize
            pokemon_to_optimize = st.selectbox(
                "Select Pokémon to optimize",
                options=[p.species for p in st.session_state.user_team],
                key="optimize_select"
            )
            
            if pokemon_to_optimize:
                # Get the selected Pokémon instance
                selected_pokemon = next(p for p in st.session_state.user_team if p.species == pokemon_to_optimize)
                
                # Optimization goals
                st.write("Set optimization goals:")
                
                # Goal type selection
                goal_type = st.selectbox(
                    "Goal Type",
                    options=["Survive", "OHKO", "2HKO", "Speed", "Custom Stat"],
                    key="goal_type"
                )
                
                # Priority for the goal
                priority = st.number_input(
                    "Goal Priority (higher = more important)",
                    min_value=1,
                    max_value=5,
                    value=1,
                    key="goal_priority"
                )
                
                if goal_type in ["Survive", "OHKO", "2HKO"]:
                    # Select opponent's Pokémon
                    opponent_pokemon = st.selectbox(
                        "Opponent's Pokémon",
                        options=[p.species for p in st.session_state.opponent_team] if st.session_state.opponent_team else ["No opponent team"],
                        key="opponent_select"
                    )
                    
                    if opponent_pokemon != "No opponent team":
                        # Get the opponent's Pokémon instance
                        opponent_instance = next(p for p in st.session_state.opponent_team if p.species == opponent_pokemon)
                        
                        # Select move
                        opponent_moves = get_moves_for_pokemon(opponent_pokemon)
                        opponent_move = st.selectbox(
                            "Opponent's Move",
                            options=opponent_moves,
                            key="opponent_move"
                        )
                        
                        # Add goal button
                        if st.button("Add Goal"):
                            goal = EVOptimizationGoal(
                                type=goal_type.lower(),
                                target_pokemon=opponent_instance,
                                move=opponent_move,
                                priority=priority
                            )
                            st.session_state.optimization_goals.append(goal)
                            st.success(f"Added {goal_type} goal against {opponent_pokemon}'s {opponent_move}")
                
                elif goal_type == "Speed":
                    # Target speed
                    target_speed = st.number_input(
                        "Target Speed",
                        min_value=0,
                        max_value=999,
                        value=100,
                        key="target_speed"
                    )
                    
                    # Add goal button
                    if st.button("Add Goal"):
                        goal = EVOptimizationGoal(
                            type="outspeed",
                            value=target_speed,
                            priority=priority
                        )
                        st.session_state.optimization_goals.append(goal)
                        st.success(f"Added Speed goal: {target_speed}")
                
                elif goal_type == "Custom Stat":
                    # Select stat to optimize
                    stat_to_optimize = st.selectbox(
                        "Stat to Optimize",
                        options=["hp", "atk", "def", "spa", "spd", "spe"],
                        key="stat_select"
                    )
                    
                    # Target value
                    target_value = st.number_input(
                        "Target Value",
                        min_value=0,
                        max_value=999,
                        value=100,
                        key="target_value"
                    )
                    
                    # Add goal button
                    if st.button("Add Goal"):
                        goal = EVOptimizationGoal(
                            type="custom",
                            stat=stat_to_optimize,
                            value=target_value,
                            priority=priority
                        )
                        st.session_state.optimization_goals.append(goal)
                        st.success(f"Added Custom goal: {stat_to_optimize} = {target_value}")
                
                # Display current goals
                if st.session_state.optimization_goals:
                    st.write("Current Goals:")
                    for i, goal in enumerate(st.session_state.optimization_goals):
                        goal_desc = f"{i+1}. {goal.type.upper()}"
                        if goal.target_pokemon:
                            goal_desc += f" vs {goal.target_pokemon.species}"
                        if goal.move:
                            goal_desc += f" ({goal.move})"
                        if goal.stat:
                            goal_desc += f" {goal.stat}"
                        if goal.value:
                            goal_desc += f" = {goal.value}"
                        goal_desc += f" (Priority: {goal.priority})"
                        st.write(goal_desc)
                    
                    # Clear goals button
                    if st.button("Clear All Goals"):
                        st.session_state.optimization_goals = []
                        st.success("Cleared all goals")
                    
                    # Optimize button
                    if st.button("Optimize EVs"):
                        try:
                            # Get current EVs as fixed values
                            fixed_evs = selected_pokemon.ev.copy()
                            
                            # Optimize EVs
                            optimized_evs = ev_optimizer.optimize_evs(
                                selected_pokemon,
                                st.session_state.optimization_goals,
                                fixed_evs=fixed_evs
                            )
                            
                            # Store optimized EVs
                            st.session_state.optimized_evs = optimized_evs
                            
                            # Display results
                            st.success("EVs optimized successfully!")
                            st.write("Optimized EVs:")
                            for stat, ev in optimized_evs.items():
                                st.write(f"{stat.upper()}: {ev}")
                            
                            # Apply button
                            if st.button("Apply Optimized EVs"):
                                selected_pokemon.ev = optimized_evs
                                st.success("Applied optimized EVs!")
                        
                        except Exception as e:
                            st.error(f"Error optimizing EVs: {str(e)}")
        
        st.divider()
        
        # Pokémon selection
        pokemon_list = get_pokemon_list()
        st.write(f"Number of Pokémon in database: {len(pokemon_list)}")  # DEBUG
        selected_pokemon = st.selectbox(
            "Select Pokémon",
            options=pokemon_list,
            key="pokemon_select"
        )
        
        if selected_pokemon:
            # Nature selection
            nature = st.selectbox(
                "Nature",
                options=["Adamant", "Bashful", "Bold", "Brave", "Calm", "Careful", "Docile", "Gentle", "Hardy", "Hasty", "Impish", "Jolly", "Lax", "Lonely", "Mild", "Modest", "Naive", "Naughty", "Quiet", "Quirky", "Rash", "Relaxed", "Sassy", "Serious", "Timid"],
                key="nature_select"
            )
            
            # Ability selection
            abilities = get_abilities_for_pokemon(selected_pokemon)
            ability = st.selectbox(
                "Ability",
                options=abilities,
                key="ability_select"
            )
            
            # Item selection
            items = get_items()
            item = st.selectbox(
                "Item",
                options=items,
                key="item_select"
            )
            
            # Move selection
            moves = get_moves_for_pokemon(selected_pokemon)
            selected_moves = st.multiselect(
                "Moves (select 4)",
                options=moves,
                max_selections=4,
                key="moves_select"
            )
            
            # EV sliders
            st.subheader("EVs")
            col1, col2 = st.columns(2)
            with col1:
                hp_ev = st.slider("HP", 0, 252, 0, 4)
                atk_ev = st.slider("Attack", 0, 252, 0, 4)
                def_ev = st.slider("Defense", 0, 252, 0, 4)
            with col2:
                spa_ev = st.slider("Sp. Attack", 0, 252, 0, 4)
                spd_ev = st.slider("Sp. Defense", 0, 252, 0, 4)
                spe_ev = st.slider("Speed", 0, 252, 0, 4)
            
            evs = {
                'hp': hp_ev,
                'atk': atk_ev,
                'def': def_ev,
                'spa': spa_ev,
                'spd': spd_ev,
                'spe': spe_ev
            }
            
            # Add Pokémon button
            if st.button("Add Pokémon") and len(selected_moves) == 4:
                pokemon = create_pokemon_instance(
                    selected_pokemon,
                    100,  # Level
                    nature,
                    ability,
                    item,
                    selected_moves,
                    evs
                )
                st.session_state.user_team.append(pokemon)
                st.success(f"Added {selected_pokemon} to your team!")
            elif len(selected_moves) != 4:
                st.error("Please select exactly 4 moves.")
    
    # Main content area
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Your Team")
        if st.session_state.user_team:
            for i, pokemon in enumerate(st.session_state.user_team):
                with st.expander(f"{pokemon.species} ({pokemon.nature})"):
                    st.write(f"Ability: {pokemon.ability}")
                    st.write(f"Item: {pokemon.item}")
                    st.write("Moves:")
                    for move in pokemon.moves:
                        st.write(f"- {move}")
                    st.write("EVs:")
                    st.write(pokemon.ev)
                    if st.button(f"Remove {pokemon.species}", key=f"remove_{i}"):
                        st.session_state.user_team.pop(i)
                        st.experimental_rerun()
        else:
            st.write("No Pokémon in your team yet.")
    
    with col2:
        st.header("Opponent's Team")
        if st.session_state.opponent_team:
            for i, pokemon in enumerate(st.session_state.opponent_team):
                with st.expander(f"{pokemon.species}"):
                    st.write(f"Ability: {pokemon.ability}")
                    st.write(f"Item: {pokemon.item}")
                    st.write("Moves:")
                    for move in pokemon.moves:
                        st.write(f"- {move}")
                    st.write("EVs:")
                    st.write(pokemon.ev)
                    if st.button(f"Remove {pokemon.species}", key=f"remove_opp_{i}"):
                        st.session_state.opponent_team.pop(i)
                        st.experimental_rerun()
        else:
            st.write("No Pokémon in opponent's team yet.")
    
    # Analysis section
    st.header("Team Analysis")
    if len(st.session_state.user_team) == 6:
        if st.button("Analyze Team"):
            # Create Team objects
            user_team = Team(st.session_state.user_team)
            opponent_team = Team(st.session_state.opponent_team) if st.session_state.opponent_team else None
            
            # Initialize analyzers
            validator = TeamValidator()
            builder = TeamBuilderLogicFinal()
            modeller = OpponentModeller()
            analyzer = MatchupAnalyzer()
            strategy = StrategyGenerator()
            move_recommender = MoveRecommender()
            item_recommender = ItemRecommender()
            synergy_analyzer = TeamSynergyAnalyzer()
            optimizer = TeamOptimizer()
            
            # Perform analysis
            validation_result = validator.validate_team(user_team)
            if not validation_result["is_valid"]:
                st.error("Team validation failed:")
                for error in validation_result["errors"]:
                    st.error(error)
            else:
                st.success("Team is valid!")
                
                # Team synergy analysis
                synergy_result = synergy_analyzer.analyze_synergy(user_team)
                st.subheader("Team Synergy Analysis")
                st.write("Type Synergy:", synergy_result["type_synergy"])
                st.write("Role Synergy:", synergy_result["role_synergy"])
                st.write("Defensive Synergy:", synergy_result["defensive_synergy"])
                st.write("Offensive Synergy:", synergy_result["offensive_synergy"])
                
                # Recommendations
                st.subheader("Recommendations")
                st.write(synergy_result["recommendations"])
                
                if opponent_team:
                    # Matchup analysis
                    matchup_result = analyzer.analyze_matchup(user_team, opponent_team)
                    st.subheader("Matchup Analysis")
                    st.write("Key Threats:", matchup_result["key_threats"])
                    st.write("Type Matchup Summary:", matchup_result["type_matchup_summary"])
                    st.write("Speed Comparison:", matchup_result["speed_comparison"])
                    st.write("Vulnerabilities:", matchup_result["vulnerabilities"])
                    
                    # Strategy suggestions
                    strategy_result = strategy.generate_strategy(matchup_result)
                    st.subheader("Strategy Suggestions")
                    st.write("Recommended Lead:", strategy_result["recommended_lead"])
                    st.write("Strategy Notes:", strategy_result["strategy_notes"])
                    
                    # Move recommendations
                    st.subheader("Move Recommendations")
                    for pokemon in user_team.pokemon:
                        move_recs = move_recommender.recommend_moves(pokemon, opponent_team)
                        st.write(f"\n{pokemon.species} Move Recommendations:")
                        st.write(move_recs["recommended_moves"])
                        st.write("Reasoning:", move_recs["reasoning"])
                    
                    # Item recommendations
                    st.subheader("Item Recommendations")
                    for pokemon in user_team.pokemon:
                        item_recs = item_recommender.recommend_items(pokemon, opponent_team)
                        st.write(f"\n{pokemon.species} Item Recommendations:")
                        st.write("Recommended Items:", item_recs["recommended_items"])
                        st.write("Offensive Items:", item_recs["offensive_items"])
                        st.write("Defensive Items:", item_recs["defensive_items"])
                        st.write("Utility Items:", item_recs["utility_items"])
    else:
        st.warning("Please add 6 Pokémon to your team before analysis.")

if __name__ == "__main__":
    main() 