#!/usr/bin/env python3
"""
Script to distribute Episode 01 completion rewards to all party members.
Adds XP bonus, gold bonus, and the dagger_plus_1 magic item.
"""

import sys
from pathlib import Path

# Add aerthos module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aerthos.storage.character_roster import CharacterRoster
from aerthos.storage.party_manager import PartyManager
from aerthos.entities.player import Weapon

def main():
    """Distribute Episode 01 rewards to party members"""

    # Party ID
    party_id = "c0dd5d91"

    # Episode 01 rewards
    XP_BONUS = 2500
    GOLD_BONUS = 100

    # Initialize managers
    char_roster = CharacterRoster()
    party_mgr = PartyManager()

    # Load party
    print("Loading party...")
    party_data = party_mgr.load_party(party_id)
    character_ids = party_data['character_ids']
    party_size = len(character_ids)

    print(f"Party: {party_data['name']} ({party_size} members)")

    # Calculate rewards per character
    xp_per_char = XP_BONUS // party_size
    xp_remainder = XP_BONUS % party_size
    gold_per_char = GOLD_BONUS // party_size
    gold_remainder = GOLD_BONUS % party_size

    print(f"\nDistributing rewards:")
    print(f"  Total XP: {XP_BONUS} → {xp_per_char} XP per character")
    print(f"  Total Gold: {GOLD_BONUS} → {gold_per_char} gold per character")

    # Load and update each character
    characters = []
    for i, char_id in enumerate(character_ids):
        char = char_roster.load_character(character_id=char_id)
        if char is None:
            print(f"  Warning: Could not load character {char_id}")
            continue

        old_xp = char.xp
        old_gold = char.gold_pieces

        # Add XP (first character gets remainder)
        bonus_xp = xp_per_char + (xp_remainder if i == 0 else 0)
        char.xp += bonus_xp

        # Add gold (first character gets remainder)
        bonus_gold = gold_per_char + (gold_remainder if i == 0 else 0)
        char.gold_pieces += bonus_gold

        print(f"\n  {char.name} ({char.char_class} {char.level}):")
        print(f"    XP: {old_xp:,} → {char.xp:,} (+{bonus_xp})")
        print(f"    Gold: {old_gold:,} gp → {char.gold_pieces:,} gp (+{bonus_gold})")

        characters.append((char, char_id))

    # Add dagger_plus_1 to party leader
    leader, leader_id = characters[0]
    has_dagger = any(item.name == "Dagger +1" for item in leader.inventory.items)

    if not has_dagger:
        print(f"\nAdding Dagger +1 to {leader.name}'s inventory...")
        dagger_plus_1 = Weapon(
            name="Dagger +1",
            weight=1.0,
            damage_sm="1d4+1",
            damage_l="1d3+1",
            speed_factor=2,
            magic_bonus=1
        )
        leader.inventory.add_item(dagger_plus_1)
        print("  ✓ Dagger +1 added")
    else:
        print(f"\n{leader.name} already has Dagger +1")

    # Save all characters
    print("\nSaving characters...")
    for char, char_id in characters:
        char_roster.save_character(char, char_id)

    print("\n✓ All rewards distributed successfully!")

    # Summary
    print("\nReward Summary:")
    print(f"  XP distributed: {XP_BONUS:,}")
    print(f"  Gold distributed: {GOLD_BONUS}")
    print(f"  Items added: Dagger +1")

    return 0

if __name__ == "__main__":
    sys.exit(main())
