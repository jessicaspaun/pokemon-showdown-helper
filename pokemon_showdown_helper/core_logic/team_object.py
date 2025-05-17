"""
Represents a team of up to 6 PokemonInstance objects.
"""
from typing import List, Optional
from core_logic.pokemon_object import PokemonInstance

class Team:
    """
    Represents a Pokémon team (up to 6 members).
    """
    MAX_TEAM_SIZE = 6

    def __init__(self, members: Optional[List[PokemonInstance]] = None):
        """
        Initialize a Team with an optional list of PokemonInstance members.
        """
        self.members: List[PokemonInstance] = members[:] if members else []

    def add_pokemon(self, pokemon: PokemonInstance) -> bool:
        """
        Add a PokemonInstance to the team if not full and no duplicate species.
        Returns True if added, False otherwise.
        """
        if len(self.members) >= self.MAX_TEAM_SIZE:
            return False
        if any(p.species == pokemon.species for p in self.members):
            return False
        self.members.append(pokemon)
        return True

    def remove_pokemon(self, species: str) -> bool:
        """
        Remove a Pokémon by species name. Returns True if removed, False if not found.
        """
        for i, p in enumerate(self.members):
            if p.species == species:
                del self.members[i]
                return True
        return False

    def get_team_size(self) -> int:
        """
        Return the current number of Pokémon on the team.
        """
        return len(self.members)

    def get_members(self) -> List[PokemonInstance]:
        """
        Return a list of team members.
        """
        return self.members[:]

    def is_valid(self) -> bool:
        """
        Check if the team is valid (1-6 unique Pokémon).
        """
        if not (1 <= len(self.members) <= self.MAX_TEAM_SIZE):
            return False
        species_set = set(p.species for p in self.members)
        return len(species_set) == len(self.members)

    def export_showdown(self) -> str:
        """
        Export the team in Pokémon Showdown text format (basic version).
        """
        lines = []
        for p in self.members:
            lines.append(f"{p.species} @ {p.item if p.item else ''}")
            lines.append(f"Ability: {p.ability if p.ability else ''}")
            lines.append(f"Level: {p.level}")
            lines.append(f"EVs: {' / '.join(f'{v} {k.upper()}' for k, v in p.ev.items() if v > 0) if p.ev else ''}")
            lines.append(f"{p.nature.capitalize()} Nature")
            for move in p.moves:
                lines.append(f"- {move}")
            lines.append("")
        return "\n".join(lines).strip() 