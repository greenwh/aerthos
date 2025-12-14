#!/usr/bin/env python3
"""
Fix spell slots in existing save files and character files to match the new spell progression.
"""

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path so we can import from aerthos
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == 'scripts' else SCRIPT_DIR
sys.path.insert(0, str(PROJECT_ROOT))

# Load class data to get proper spell slot progression
classes_json = PROJECT_ROOT / 'aerthos' / 'data' / 'classes.json'
with open(classes_json) as f:
    classes_data = json.load(f)

def get_correct_spell_slots(char_class: str, level: int) -> list:
    """Get the correct spell slots for a character class and level"""
    if char_class not in classes_data:
        print(f"  Warning: Unknown class '{char_class}', no spell slots assigned")
        return []

    class_data = classes_data[char_class]
    slot_key = f'spell_slots_level_{level}'

    if slot_key not in class_data:
        # No spell slots for this level (e.g., Fighter, Thief, or caster at level 1)
        return []

    slots_by_level = class_data[slot_key]

    # Convert array format to list of spell slot objects
    spell_slots = []
    for spell_level_idx, num_slots in enumerate(slots_by_level):
        spell_level = spell_level_idx + 1
        for _ in range(num_slots):
            spell_slots.append({
                'level': spell_level,
                'spell': None,
                'is_used': False
            })

    return spell_slots

def fix_character_spell_slots(character_data: dict) -> tuple[dict, bool]:
    """Fix spell slots for a character. Returns (fixed_character, was_changed)"""
    char_class = character_data.get('char_class', 'Fighter')
    level = character_data.get('level', 1)
    current_slots = character_data.get('spells_memorized', [])

    # Get correct spell slots
    correct_slots = get_correct_spell_slots(char_class, level)

    # Check if current slots match correct slots
    if len(current_slots) != len(correct_slots):
        print(f"  {character_data.get('name', 'Unknown')}: Level {level} {char_class}")
        print(f"    Old: {len(current_slots)} slots {[s.get('level') for s in current_slots]}")
        print(f"    New: {len(correct_slots)} slots {[s.get('level') for s in correct_slots]}")
        character_data['spells_memorized'] = correct_slots
        return character_data, True

    # Check if slot levels are correct
    for i, (current, correct) in enumerate(zip(current_slots, correct_slots)):
        if current.get('level') != correct.get('level'):
            print(f"  {character_data.get('name', 'Unknown')}: Level {level} {char_class}")
            print(f"    Slot levels mismatch at index {i}")
            print(f"    Old: {[s.get('level') for s in current_slots]}")
            print(f"    New: {[s.get('level') for s in correct_slots]}")
            character_data['spells_memorized'] = correct_slots
            return character_data, True

    return character_data, False

def fix_save_file(save_path: Path) -> bool:
    """Fix spell slots in a save file. Returns True if file was modified."""
    print(f"\nProcessing: {save_path}")

    # Load save file
    with open(save_path, 'r') as f:
        save_data = json.load(f)

    # Check if this save has a player
    if 'player' not in save_data:
        print("  No player data found, skipping")
        return False

    # Fix player spell slots
    player_data, player_changed = fix_character_spell_slots(save_data['player'])

    if player_changed:
        # Backup original
        backup_path = save_path.with_suffix('.json.bak')
        shutil.copy2(save_path, backup_path)
        print(f"  ✓ Backup created: {backup_path}")

        # Save fixed version
        save_data['player'] = player_data
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"  ✓ Fixed and saved")
        return True
    else:
        print(f"  ✓ Already correct, no changes needed")
        return False

def fix_character_file(char_path: Path) -> bool:
    """Fix spell slots in a character file. Returns True if file was modified."""
    print(f"\nProcessing: {char_path}")

    # Load character file
    with open(char_path, 'r') as f:
        char_data = json.load(f)

    # Fix spell slots
    char_data, changed = fix_character_spell_slots(char_data)

    if changed:
        # Backup original
        backup_path = char_path.with_suffix('.json.bak')
        shutil.copy2(char_path, backup_path)
        print(f"  ✓ Backup created: {backup_path}")

        # Save fixed version
        with open(char_path, 'w') as f:
            json.dump(char_data, f, indent=2)
        print(f"  ✓ Fixed and saved")
        return True
    else:
        print(f"  ✓ Already correct, no changes needed")
        return False

def fix_party_file(party_path: Path) -> bool:
    """Fix spell slots in a party file. Returns True if file was modified."""
    print(f"\nProcessing: {party_path}")

    # Load party file
    with open(party_path, 'r') as f:
        party_data = json.load(f)

    # Check if this party has members
    if 'members' not in party_data:
        print("  No members data found, skipping")
        return False

    changed = False
    for i, member in enumerate(party_data['members']):
        member_data, member_changed = fix_character_spell_slots(member)
        if member_changed:
            party_data['members'][i] = member_data
            changed = True

    if changed:
        # Backup original
        backup_path = party_path.with_suffix('.json.bak')
        shutil.copy2(party_path, backup_path)
        print(f"  ✓ Backup created: {backup_path}")

        # Save fixed version
        with open(party_path, 'w') as f:
            json.dump(party_data, f, indent=2)
        print(f"  ✓ Fixed and saved")
        return True
    else:
        print(f"  ✓ Already correct, no changes needed")
        return False

def main():
    print("=" * 70)
    print("FIXING SPELL SLOTS IN EXISTING CHARACTERS")
    print("=" * 70)

    # Get aerthos data directory from constants.py
    from aerthos.constants import _AERTHOS_HOME
    aerthos_dir = Path(_AERTHOS_HOME)

    files_fixed = 0
    files_checked = 0

    # Fix save files
    saves_dir = aerthos_dir / 'saves'
    if saves_dir.exists():
        print(f"\n--- Checking Save Files in {saves_dir} ---")
        for save_file in saves_dir.glob('*.json'):
            if save_file.suffix == '.json' and not save_file.name.endswith('.bak'):
                files_checked += 1
                if fix_save_file(save_file):
                    files_fixed += 1

    # Fix character files
    chars_dir = aerthos_dir / 'characters'
    if chars_dir.exists():
        print(f"\n--- Checking Character Files in {chars_dir} ---")
        for char_file in chars_dir.glob('*.json'):
            if char_file.suffix == '.json' and not char_file.name.endswith('.bak'):
                files_checked += 1
                if fix_character_file(char_file):
                    files_fixed += 1

    # Fix party files
    parties_dir = aerthos_dir / 'parties'
    if parties_dir.exists():
        print(f"\n--- Checking Party Files in {parties_dir} ---")
        for party_file in parties_dir.glob('*.json'):
            if party_file.suffix == '.json' and not party_file.name.endswith('.bak'):
                files_checked += 1
                if fix_party_file(party_file):
                    files_fixed += 1

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files checked: {files_checked}")
    print(f"Files fixed:   {files_fixed}")
    print(f"Files OK:      {files_checked - files_fixed}")

    if files_fixed > 0:
        print("\n✓ Spell slots have been corrected!")
        print("✓ Original files backed up with .bak extension")
        print("\nNote: If you have any active game sessions, you may need to reload them")
        print("      to see the corrected spell slots.")
    else:
        print("\n✓ All files already have correct spell slots!")

if __name__ == '__main__':
    main()
