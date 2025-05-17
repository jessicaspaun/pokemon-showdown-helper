"""
Validates a Team object against Gen 7 OU rules using the database.
"""
from typing import List, Optional
from core_logic.team_object import Team
import sqlite3

class TeamValidator:
    """
    Validates a Team object against Gen 7 OU rules.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._load_rules()

    def _load_rules(self):
        """
        Load banlists and rules from the database for Gen 7 OU.
        """
        cur = self.conn.cursor()
        # Get banned Pokémon, abilities, items, moves for Gen 7 OU
        cur.execute("SELECT rule FROM FormatRules WHERE format_id = ? AND rule_type = 'ban'", ("gen7ou",))
        bans = [row[0] for row in cur.fetchall()]
        self.banned_pokemon = set()
        self.banned_abilities = set()
        self.banned_items = set()
        self.banned_moves = set()
        for ban in bans:
            if ": " in ban:
                # e.g., "Ability: Arena Trap", "Item: Soul Dew", "Move: Baton Pass"
                prefix, name = ban.split(": ", 1)
                if prefix == "Ability":
                    self.banned_abilities.add(name)
                elif prefix == "Item":
                    self.banned_items.add(name)
                elif prefix == "Move":
                    self.banned_moves.add(name)
            else:
                self.banned_pokemon.add(ban)

    def validate(self, team: Team) -> List[str]:
        """
        Validate the team. Returns a list of error messages (empty if valid).
        """
        errors = []
        # Team size
        if team.get_team_size() != 6:
            errors.append("Team must have exactly 6 Pokémon.")
        # Unique species
        species = [p.species for p in team.get_members()]
        if len(set(species)) != len(species):
            errors.append("Duplicate Pokémon species are not allowed.")
        # Banned Pokémon
        for p in team.get_members():
            if p.species in self.banned_pokemon:
                errors.append(f"{p.species} is banned in Gen 7 OU.")
            if p.ability and p.ability in self.banned_abilities:
                errors.append(f"Ability {p.ability} is banned in Gen 7 OU.")
            if p.item and p.item in self.banned_items:
                errors.append(f"Item {p.item} is banned in Gen 7 OU.")
            for move in p.moves:
                if move in self.banned_moves:
                    errors.append(f"Move {move} is banned in Gen 7 OU.")
        # TODO: Add complex clause checks (e.g., Baton Pass clause)
        return errors

    def close(self):
        self.conn.close() 