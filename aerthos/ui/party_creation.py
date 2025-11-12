"""
Party creation UI - Create multiple characters for party-based gameplay
"""

from typing import List
from ..entities.player import PlayerCharacter
from ..entities.party import Party
from ..engine.game_state import GameData
from .character_creation import CharacterCreator
from .character_sheet import CharacterSheet


class PartyCreator:
    """
    Handles creation of a full adventuring party (4-6 characters)
    """

    def __init__(self, game_data: GameData):
        self.game_data = game_data
        self.character_creator = CharacterCreator(game_data)

    def create_party(self, min_size: int = 4, max_size: int = 6) -> Party:
        """
        Guide user through creating a full party

        Args:
            min_size: Minimum party size
            max_size: Maximum party size

        Returns:
            Party instance with created characters
        """

        print("\n" + "═" * 70)
        print("PARTY CREATION")
        print("═" * 70)
        print()
        print("Welcome to party-based adventuring!")
        print()
        print(f"You can create {min_size}-{max_size} characters for your party.")
        print("A balanced party typically includes:")
        print("  - Fighter(s): Front-line combat")
        print("  - Cleric: Healing and support")
        print("  - Magic-User: Offensive spells")
        print("  - Thief: Skills and scouting")
        print()

        # Ask for party size
        while True:
            try:
                size_input = input(f"How many characters? ({min_size}-{max_size}, default {min_size}): ").strip()
                if not size_input:
                    party_size = min_size
                    break

                party_size = int(size_input)
                if min_size <= party_size <= max_size:
                    break
                else:
                    print(f"Please enter a number between {min_size} and {max_size}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        print()
        print(f"Creating a party of {party_size} characters...")
        print()

        # Create characters
        characters: List[PlayerCharacter] = []

        for i in range(party_size):
            print("═" * 70)
            print(f"CHARACTER {i + 1} OF {party_size}")
            print("═" * 70)
            print()

            character = self.character_creator.create_character()
            characters.append(character)

            # Show character sheet
            print("\n" + CharacterSheet.format_character(character))
            print()

            if i < party_size - 1:
                input("Press Enter to create next character...")
                print("\n")

        # Create party
        party = Party(members=characters)

        # Show party summary
        print("\n" + "═" * 70)
        print("PARTY COMPLETE")
        print("═" * 70)
        print()
        self.show_party_summary(party)
        print()

        # Confirm formation
        self.configure_formation(party)

        input("\nPress Enter to begin your adventure...")
        print()

        return party

    def show_party_summary(self, party: Party):
        """Display party roster summary"""

        print(f"Party Size: {party.size()}")
        print(f"Average Level: {party.average_level:.1f}")
        print()
        print("Party Roster:")
        print("-" * 70)

        for i, member in enumerate(party.members):
            position = party.formation[i]
            pos_marker = "[FRONT]" if position == 'front' else "[BACK] "

            print(f"{i + 1}. {pos_marker} {member.name} - Level {member.level} {member.race} {member.char_class}")
            print(f"   HP: {member.hp_current}/{member.hp_max} | AC: {member.get_effective_ac()} | "
                  f"THAC0: {member.thac0}")

            # Show key stats
            if member.char_class == 'Fighter':
                print(f"   STR: {member.strength} DEX: {member.dexterity} CON: {member.constitution}")
            elif member.char_class == 'Cleric':
                print(f"   WIS: {member.wisdom} STR: {member.strength} CON: {member.constitution}")
            elif member.char_class == 'Magic-User':
                print(f"   INT: {member.intelligence} DEX: {member.dexterity} CON: {member.constitution}")
            elif member.char_class == 'Thief':
                print(f"   DEX: {member.dexterity} INT: {member.intelligence} CON: {member.constitution}")

            print()

    def configure_formation(self, party: Party):
        """Allow user to configure party formation"""

        print("\n" + "═" * 70)
        print("FORMATION CONFIGURATION")
        print("═" * 70)
        print()
        print("Current formation:")
        self._display_formation(party)
        print()

        change = input("Change formation? (y/n, default n): ").strip().lower()

        if change != 'y':
            return

        print()
        print("Select characters for FRONT line (fighters take more hits):")
        print("Enter character numbers separated by spaces (e.g., '1 3 4')")
        print()

        while True:
            front_input = input("Front line characters: ").strip()

            if not front_input:
                print("At least one character must be in the front line!")
                continue

            try:
                front_indices = [int(x) - 1 for x in front_input.split()]

                # Validate indices
                if all(0 <= i < party.size() for i in front_indices):
                    # Update formation
                    for i in range(party.size()):
                        if i in front_indices:
                            party.formation[i] = 'front'
                        else:
                            party.formation[i] = 'back'

                    print("\nNew formation:")
                    self._display_formation(party)
                    break
                else:
                    print(f"Invalid character numbers. Use 1-{party.size()}.")

            except ValueError:
                print("Invalid input. Enter numbers separated by spaces.")

    def _display_formation(self, party: Party):
        """Display current party formation"""

        front = party.get_front_line()
        back = party.get_back_line()

        print("  FRONT LINE:")
        if front:
            for char in front:
                print(f"    {char.name} ({char.char_class})")
        else:
            print("    (none)")

        print()
        print("  BACK LINE:")
        if back:
            for char in back:
                print(f"    {char.name} ({char.char_class})")
        else:
            print("    (none)")
