#!/usr/bin/env python3
"""
Fix missing spell slots for casters who leveled up.
The _level_up() method doesn't grant new spell slots automatically.
"""

import sys
from pathlib import Path

# Add aerthos module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aerthos.storage.character_roster import CharacterRoster
from aerthos.entities.player import SpellSlot

def main():
    """Add missing spell slots to Canon and Aether"""

    roster = CharacterRoster()

    print("=== Fixing Spell Slots ===\n")

    # Canon - Cleric Level 3 (needs 1 second-level slot)
    print("Canon (Cleric Level 3):")
    canon = roster.load_character(character_id='469a5593')
    print(f"  Current slots: {len([s for s in canon.spells_memorized if s.level == 1])} L1, {len([s for s in canon.spells_memorized if s.level == 2])} L2")
    print(f"  Should have: 2 L1, 1 L2")

    # Add missing second-level slot
    if len([s for s in canon.spells_memorized if s.level == 2]) == 0:
        new_slot = SpellSlot(level=2, is_used=False)
        canon.spells_memorized.append(new_slot)
        print(f"  ✓ Added 1 second-level spell slot")
        roster.save_character(canon, '469a5593')

    # Aether - Magic-User Level 2 (needs 1 more first-level slot)
    print("\nAether (Magic-User Level 2):")
    aether = roster.load_character(character_id='f8ddd970')
    print(f"  Current slots: {len([s for s in aether.spells_memorized if s.level == 1])} L1")
    print(f"  Should have: 2 L1")

    # Add missing first-level slot
    if len([s for s in aether.spells_memorized if s.level == 1]) == 1:
        new_slot = SpellSlot(level=1, is_used=False)
        aether.spells_memorized.append(new_slot)
        print(f"  ✓ Added 1 first-level spell slot")
        roster.save_character(aether, 'f8ddd970')

    print("\n✓ All spell slots fixed!")

    return 0

if __name__ == "__main__":
    sys.exit(main())
