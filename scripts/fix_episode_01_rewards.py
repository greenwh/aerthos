#!/usr/bin/env python3
"""
Fix Episode 01 rewards - give FULL XP and gold to each character (not split).
Campaign is balanced with XP_DIVIDE_AMONG_PARTY = False.

Also uses gain_xp() method to trigger automatic level-ups.
"""

import sys
from pathlib import Path

# Add aerthos module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aerthos.storage.character_roster import CharacterRoster
from aerthos.storage.party_manager import PartyManager

def main():
    """Fix Episode 01 rewards - give full XP/gold to each character"""

    # Party ID
    party_id = "c0dd5d91"

    # Episode 01 rewards (FULL amount per character, not split)
    XP_BONUS = 2500  # Each character gets this
    GOLD_BONUS = 100  # Each character gets this

    # Current XP after incorrect split distribution
    current_xp = {
        'c1658b4c': 1970,  # Grim
        'ba7be2d2': 1892,  # Valorian
        '54a51250': 2563,  # Eryndor
        '469a5593': 2595,  # Canon
        'f8ddd970': 2595,  # Aether
        '93cc8188': 2316   # Pip
    }

    # Original XP before any rewards
    original_xp = {
        'c1658b4c': 1550,  # Grim
        'ba7be2d2': 1476,  # Valorian
        '54a51250': 2147,  # Eryndor
        '469a5593': 2179,  # Canon
        'f8ddd970': 2179,  # Aether
        '93cc8188': 1900   # Pip
    }

    # Current gold after incorrect split
    current_gold = {
        'c1658b4c': 1277,  # Grim
        'ba7be2d2': 110,   # Valorian
        '54a51250': 1206,  # Eryndor
        '469a5593': 110,   # Canon
        'f8ddd970': 110,   # Aether
        '93cc8188': 1101   # Pip
    }

    # Initialize managers
    char_roster = CharacterRoster()
    party_mgr = PartyManager()

    # Load party
    print("Loading party...")
    party_data = party_mgr.load_party(party_id)
    character_ids = party_data['character_ids']

    print(f"Party: {party_data['name']} ({len(character_ids)} members)")
    print(f"\nCampaign Design: XP_DIVIDE_AMONG_PARTY = False")
    print(f"Each character receives: {XP_BONUS} XP, {GOLD_BONUS} gold")

    # Load and update each character
    characters = []
    for char_id in character_ids:
        char = char_roster.load_character(character_id=char_id)
        if char is None:
            print(f"  Warning: Could not load character {char_id}")
            continue

        # Calculate correct totals
        correct_xp = original_xp[char_id] + XP_BONUS
        correct_gold = current_gold[char_id] - (current_gold[char_id] - original_xp.get(char_id, 0)) + GOLD_BONUS

        # Calculate how much to add
        xp_to_add = correct_xp - current_xp[char_id]
        gold_to_add = correct_gold - current_gold[char_id]

        print(f"\n{char.name} ({char.char_class} {char.level}):")
        print(f"  Current XP: {current_xp[char_id]:,}")
        print(f"  Correct XP: {correct_xp:,} (original {original_xp[char_id]:,} + {XP_BONUS:,})")
        print(f"  Adding: {xp_to_add:,} XP")

        # Use gain_xp() to trigger level-up checks
        level_up_msg = char.gain_xp(xp_to_add)
        if level_up_msg:
            print(f"  {level_up_msg}")

        # Fix gold calculation - simpler approach
        original_gold = {
            'c1658b4c': 1257,  # Grim
            'ba7be2d2': 94,    # Valorian
            '54a51250': 1190,  # Eryndor
            '469a5593': 94,    # Canon
            'f8ddd970': 94,    # Aether
            '93cc8188': 1085   # Pip
        }

        correct_gold = original_gold[char_id] + GOLD_BONUS
        gold_to_add = correct_gold - current_gold[char_id]

        char.gold_pieces += gold_to_add
        print(f"  Gold: {current_gold[char_id]:,} → {char.gold_pieces:,} gp (+{gold_to_add})")

        characters.append((char, char_id))

    # Save all characters
    print("\nSaving characters...")
    for char, char_id in characters:
        char_roster.save_character(char, char_id)

    print("\n✓ All rewards corrected successfully!")

    # Summary
    print("\nCorrected Reward Summary:")
    print(f"  XP per character: {XP_BONUS:,} (FULL, not split)")
    print(f"  Gold per character: {GOLD_BONUS} gp (FULL, not split)")
    print(f"  Magic items: Dagger +1 (already added)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
