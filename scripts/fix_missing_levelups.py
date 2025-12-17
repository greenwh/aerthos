#!/usr/bin/env python3
"""
Fix missing level-ups for Eryndor and Valorian.
The XP_TABLES was missing Ranger/Paladin, so gain_xp() didn't trigger level-ups.
"""

import sys
from pathlib import Path

# Add aerthos module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aerthos.storage.character_roster import CharacterRoster

def main():
    """Manually trigger level-ups for characters who have the XP but didn't level"""

    char_roster = CharacterRoster()

    print("Checking for missed level-ups...\n")

    # Eryndor: Ranger with 4,647 XP (should be level 3)
    # Level 2: 2,250 XP, Level 3: 4,500 XP
    print("=== Eryndor (Ranger) ===")
    eryndor = char_roster.load_character(character_id='54a51250')
    print(f"Current: Level {eryndor.level}, {eryndor.xp:,} XP")
    print(f"Should be: Level 3 (4,500 XP required)")

    if eryndor.level == 1:
        # Level up to 2
        msg = eryndor._level_up()
        print(f"\n{msg}")

        # Level up to 3
        msg = eryndor._level_up()
        print(f"{msg}")

        char_roster.save_character(eryndor, '54a51250')
        print(f"\n✓ Eryndor leveled to {eryndor.level}")

    # Valorian: Paladin with 3,976 XP (level 1, needs 2,750 for level 2)
    print("\n\n=== Valorian (Paladin) ===")
    valorian = char_roster.load_character(character_id='ba7be2d2')
    print(f"Current: Level {valorian.level}, {valorian.xp:,} XP")
    print(f"Level 2 requires: 2,750 XP")
    print(f"Level 3 requires: 5,500 XP")

    if valorian.level == 1 and valorian.xp >= 2750:
        # Level up to 2
        msg = valorian._level_up()
        print(f"\n{msg}")

        char_roster.save_character(valorian, 'ba7be2d2')
        print(f"\n✓ Valorian leveled to {valorian.level}")

    print("\n✓ All missing level-ups applied!")

    return 0

if __name__ == "__main__":
    sys.exit(main())
