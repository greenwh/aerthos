#!/usr/bin/env python3
"""
Comprehensive character fix script to address all validation issues:
1. Fix equipped items missing type fields
2. Level up characters with sufficient XP
3. Fix spell slot issues
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add aerthos module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aerthos.constants import _AERTHOS_HOME, DATA_DIR
from aerthos.storage.character_roster import CharacterRoster
from aerthos.engine.game_state import GameData


class CharacterFixer:
    """Fixes character data integrity issues"""

    def __init__(self):
        self.roster_dir = _AERTHOS_HOME / 'characters'
        self.char_roster = CharacterRoster()
        self.game_data = GameData.load_all()

        # Load level progression data
        level_prog_file = Path(DATA_DIR) / 'level_progression.json'
        with open(level_prog_file, 'r') as f:
            self.level_data = json.load(f)

        self.fixes_applied = {
            'equipped_items': 0,
            'level_ups': 0,
            'spell_slots': 0
        }

    def fix_all_characters(self):
        """Fix all characters in the roster"""
        if not self.roster_dir.exists():
            print(f"Character roster directory not found: {self.roster_dir}")
            return

        char_files = list(self.roster_dir.glob('*.json'))
        # Skip backup files
        char_files = [f for f in char_files if '.bak' not in str(f)]

        if not char_files:
            print("No character files found.")
            return

        print(f"Processing {len(char_files)} character files...\n")

        for filepath in char_files:
            try:
                with open(filepath, 'r') as f:
                    char_data = json.load(f)

                char_name = char_data.get('name', filepath.name)
                char_id = char_data.get('id', filepath.stem.split('_')[-1])

                print(f"=== {char_name} ({char_id}) ===")

                # Fix equipped items
                self.fix_equipped_items(char_data, filepath)

                # Level up if needed
                self.level_up_character(char_data, char_id, filepath)

                # Fix spell slots
                self.fix_spell_slots(char_data, filepath)

                print()

            except Exception as e:
                print(f"Error processing {filepath.name}: {e}")
                import traceback
                traceback.print_exc()

    def fix_equipped_items(self, char_data: Dict[str, Any], filepath: Path):
        """Fix equipped items missing type field"""
        equipped = char_data.get('equipped', {})
        modified = False

        for slot, item in equipped.items():
            if item and isinstance(item, dict) and 'type' not in item:
                # Try to determine type from slot and name
                item_name = item.get('name', '')

                # Determine type from slot
                if slot == 'weapon':
                    item['type'] = 'weapon'
                    # Add missing weapon fields if needed
                    if 'damage_sm' not in item:
                        item['damage_sm'] = '1d6'
                    if 'damage_l' not in item:
                        item['damage_l'] = '1d8'
                    if 'speed_factor' not in item:
                        item['speed_factor'] = 5
                    if 'magic_bonus' not in item:
                        item['magic_bonus'] = 0
                    modified = True
                    print(f"  Fixed weapon: {item_name}")

                elif slot == 'armor':
                    item['type'] = 'armor'
                    # Add missing armor fields if needed
                    if 'armor_type' not in item:
                        item['armor_type'] = 'medium'
                    if 'movement_rate' not in item:
                        item['movement_rate'] = 9
                    if 'magic_bonus' not in item:
                        item['magic_bonus'] = 0
                    modified = True
                    print(f"  Fixed armor: {item_name}")

                elif slot == 'shield':
                    item['type'] = 'shield'
                    if 'ac_bonus' not in item:
                        item['ac_bonus'] = 1
                    if 'magic_bonus' not in item:
                        item['magic_bonus'] = 0
                    modified = True
                    print(f"  Fixed shield: {item_name}")

                elif slot == 'light':
                    item['type'] = 'light_source'
                    if 'burn_time_turns' not in item:
                        item['burn_time_turns'] = 6  # Default torch
                    if 'turns_remaining' not in item:
                        item['turns_remaining'] = 6
                    if 'light_radius' not in item:
                        item['light_radius'] = 30
                    modified = True
                    print(f"  Fixed light source: {item_name}")

        if modified:
            char_data['equipped'] = equipped
            with open(filepath, 'w') as f:
                json.dump(char_data, f, indent=2)
            self.fixes_applied['equipped_items'] += 1

    def level_up_character(self, char_data: Dict[str, Any], char_id: str, filepath: Path):
        """Level up character if they have enough XP"""
        char_class = char_data.get('class')
        current_level = char_data.get('level', 1)
        current_xp = char_data.get('xp', 0)

        if not char_class or char_class not in self.level_data:
            return

        xp_table = self.level_data[char_class].get('xp_table', [])

        # Determine target level
        target_level = current_level
        for level_idx, required_xp in enumerate(xp_table):
            if current_xp >= required_xp:
                target_level = level_idx + 2  # +2 because index 0 is level 2

        if target_level > current_level:
            # Load character object to level up properly
            try:
                character = self.char_roster.load_character(character_id=char_id)

                if character:
                    print(f"  Leveling up from {current_level} to {target_level}...")

                    levels_gained = 0
                    while character.level < target_level:
                        msg = character._level_up()
                        levels_gained += 1
                        print(f"    {msg}")

                    # Save leveled character
                    self.char_roster.save_character(character, char_id)
                    self.fixes_applied['level_ups'] += levels_gained
                    print(f"  ✓ Leveled to {character.level} (+{levels_gained} levels)")

            except Exception as e:
                print(f"  Error leveling up: {e}")

    def fix_spell_slots(self, char_data: Dict[str, Any], filepath: Path):
        """Fix spell slot count mismatches"""
        char_class = char_data.get('class')
        char_level = char_data.get('level', 1)

        if not char_class or char_class not in self.level_data:
            return

        class_data = self.level_data[char_class]
        if 'spell_slots' not in class_data:
            return

        spell_slots_table = class_data['spell_slots']
        level_index = char_level - 1

        # Get current slots
        spells_memorized = char_data.get('spells_memorized', [])

        # Count slots by level
        current_slots = {}
        for slot in spells_memorized:
            slot_level = slot.get('level')
            if slot_level:
                current_slots[slot_level] = current_slots.get(slot_level, 0) + 1

        # Build expected slot counts
        expected_slots = {}
        for spell_level_str, counts in spell_slots_table.items():
            spell_level = int(spell_level_str)
            if level_index < len(counts):
                expected = counts[level_index]
                if expected > 0:
                    expected_slots[spell_level] = expected

        # Check if adjustment needed
        needs_fix = False
        for spell_level, expected in expected_slots.items():
            actual = current_slots.get(spell_level, 0)
            if actual != expected:
                needs_fix = True
                break

        if needs_fix:
            print(f"  Fixing spell slots...")
            new_memorized = []

            for spell_level, expected_count in expected_slots.items():
                # Keep existing slots for this level
                existing = [s for s in spells_memorized if s.get('level') == spell_level]

                # Add or remove slots to match expected
                if len(existing) < expected_count:
                    # Add empty slots
                    for _ in range(expected_count - len(existing)):
                        new_memorized.append({
                            'level': spell_level,
                            'spell': None,
                            'is_used': False
                        })
                    # Add existing slots
                    new_memorized.extend(existing)
                    print(f"    Added {expected_count - len(existing)} L{spell_level} slots")
                else:
                    # Keep only the expected number
                    new_memorized.extend(existing[:expected_count])
                    if len(existing) > expected_count:
                        print(f"    Removed {len(existing) - expected_count} extra L{spell_level} slots")

            char_data['spells_memorized'] = new_memorized
            with open(filepath, 'w') as f:
                json.dump(char_data, f, indent=2)
            self.fixes_applied['spell_slots'] += 1
            print(f"  ✓ Spell slots fixed")

    def print_summary(self):
        """Print summary of fixes applied"""
        print("\n" + "=" * 70)
        print("FIX SUMMARY")
        print("=" * 70)
        print(f"  Equipped items fixed: {self.fixes_applied['equipped_items']}")
        print(f"  Level-ups applied: {self.fixes_applied['level_ups']}")
        print(f"  Spell slots fixed: {self.fixes_applied['spell_slots']}")
        print("=" * 70)


def main():
    """Run comprehensive character fixes"""
    print("=== Character Fix Tool ===\n")

    fixer = CharacterFixer()
    fixer.fix_all_characters()
    fixer.print_summary()

    return 0


if __name__ == "__main__":
    sys.exit(main())
