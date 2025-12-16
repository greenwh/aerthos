#!/usr/bin/env python3
"""
Fix spell slots in existing save files and character files to match the character's class and level.

This script intelligently adjusts spell slots by:
- Adding new empty slots if character should have more (e.g., after leveling up)
- Removing excess slots if character should have fewer
- Preserving existing memorized spells where possible

IMPORTANT: Empty slots have NO 'spell' field. The field is only added when a spell is memorized.
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

def get_correct_spell_slot_counts(char_class: str, level: int) -> dict:
    """
    Get the correct number of spell slots per level for a character class and level.

    Returns:
        Dict mapping spell_level -> num_slots, e.g., {1: 2, 2: 1} for a level 3 Magic-User
        Empty dict {} if class is non-caster or has no slots at this level
    """
    if char_class not in classes_data:
        print(f"  ⚠ Warning: Unknown class '{char_class}'")
        print(f"     Available classes: {', '.join(sorted(classes_data.keys()))}")
        return {}

    class_data = classes_data[char_class]
    slot_key = f'spell_slots_level_{level}'

    if slot_key not in class_data:
        # No spell slots for this level (e.g., Fighter, Thief, or caster at low level)
        return {}

    slots_by_level = class_data[slot_key]

    # Convert array format to dict
    slot_counts = {}
    for spell_level_idx, num_slots in enumerate(slots_by_level):
        if num_slots > 0:
            spell_level = spell_level_idx + 1
            slot_counts[spell_level] = num_slots

    return slot_counts

def create_empty_slot(spell_level: int) -> dict:
    """
    Create an empty spell slot.

    IMPORTANT: Empty slots do NOT have a 'spell' field!
    The 'spell' field is only added when a spell is memorized.
    """
    return {
        'level': spell_level,
        'is_used': False
    }

def fix_character_spell_slots(character_data: dict) -> tuple[dict, bool]:
    """
    Fix spell slots for a character while preserving memorized spells.

    Returns (fixed_character, was_changed)
    """
    # Check both 'class' and 'char_class' keys (files use 'class', code uses 'char_class')
    char_class = character_data.get('char_class') or character_data.get('class', 'Fighter')
    level = character_data.get('level', 1)
    current_slots = character_data.get('spells_memorized', [])

    # Get correct spell slot counts per level
    correct_slot_counts = get_correct_spell_slot_counts(char_class, level)

    # If no spell slots needed (Fighter, Thief, etc.), clear any existing slots
    if not correct_slot_counts:
        if current_slots:
            print(f"  {character_data.get('name', 'Unknown')}: Level {level} {char_class}")
            print(f"    Removing all spell slots (non-caster class or no slots at this level)")
            character_data['spells_memorized'] = []
            return character_data, True
        return character_data, False

    # Count current slots by level
    current_slot_counts = {}
    for slot in current_slots:
        spell_level = slot.get('level', 1)
        current_slot_counts[spell_level] = current_slot_counts.get(spell_level, 0) + 1

    # Check if adjustment is needed
    needs_adjustment = current_slot_counts != correct_slot_counts

    if not needs_adjustment:
        return character_data, False

    # Need to adjust slots - preserve existing spells where possible
    print(f"  {character_data.get('name', 'Unknown')}: Level {level} {char_class}")
    print(f"    Current slots: {current_slot_counts}")
    print(f"    Correct slots: {correct_slot_counts}")

    # Build new slot list, preserving spells where possible
    new_slots = []

    # Group current slots by spell level
    slots_by_level = {}
    for slot in current_slots:
        spell_level = slot.get('level', 1)
        if spell_level not in slots_by_level:
            slots_by_level[spell_level] = []
        slots_by_level[spell_level].append(slot)

    # For each spell level that should exist, add the correct number of slots
    for spell_level in sorted(correct_slot_counts.keys()):
        num_slots_needed = correct_slot_counts[spell_level]
        existing_slots = slots_by_level.get(spell_level, [])

        # Reuse existing slots first (to preserve memorized spells)
        for i in range(num_slots_needed):
            if i < len(existing_slots):
                # Reuse existing slot (preserves spell if any)
                existing_slot = existing_slots[i]

                # Clean up the slot - remove 'spell' field if it's None
                # (empty slots should not have 'spell' field at all)
                if 'spell' in existing_slot and existing_slot['spell'] is None:
                    cleaned_slot = {
                        'level': existing_slot.get('level', spell_level),
                        'is_used': existing_slot.get('is_used', False)
                    }
                    new_slots.append(cleaned_slot)
                else:
                    # Keep as-is (has a memorized spell or is already clean)
                    new_slots.append(existing_slot)
            else:
                # Add new empty slot (NO 'spell' field!)
                new_slots.append(create_empty_slot(spell_level))

    # Count preserved spells
    spells_preserved = sum(1 for slot in new_slots if 'spell' in slot and slot['spell'] is not None)

    character_data['spells_memorized'] = new_slots

    print(f"    ✓ Adjusted to {len(new_slots)} slots, preserved {spells_preserved} memorized spell(s)")

    return character_data, True

def fix_save_file(save_path: Path) -> bool:
    """Fix spell slots in a save file. Returns True if file was modified."""
    print(f"\nProcessing: {save_path.name}")

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
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = save_path.with_suffix(f'.json.{timestamp}.bak')
        shutil.copy2(save_path, backup_path)
        print(f"  ✓ Backup created: {backup_path.name}")

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
    print(f"\nProcessing: {char_path.name}")

    # Load character file
    with open(char_path, 'r') as f:
        char_data = json.load(f)

    # Fix spell slots
    char_data, changed = fix_character_spell_slots(char_data)

    if changed:
        # Backup original
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = char_path.with_suffix(f'.json.{timestamp}.bak')
        shutil.copy2(char_path, backup_path)
        print(f"  ✓ Backup created: {backup_path.name}")

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
    print(f"\nProcessing: {party_path.name}")

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
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = party_path.with_suffix(f'.json.{timestamp}.bak')
        shutil.copy2(party_path, backup_path)
        print(f"  ✓ Backup created: {backup_path.name}")

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
    print("\nThis script will:")
    print("  • Check spell slots against character class and level")
    print("  • Add missing slots for characters who leveled up")
    print("  • Remove excess slots if any exist")
    print("  • Preserve memorized spells where possible")
    print("  • Create timestamped backups of all modified files")
    print("\nNOTE: Empty slots do NOT have a 'spell' field.")
    print("      The 'spell' field is only present when a spell is memorized.")

    # Get aerthos data directory from constants.py
    from aerthos.constants import _AERTHOS_HOME
    aerthos_dir = Path(_AERTHOS_HOME)

    files_fixed = 0
    files_checked = 0

    # Fix save files
    saves_dir = aerthos_dir / 'saves'
    if saves_dir.exists():
        print(f"\n--- Checking Save Files in {saves_dir} ---")
        for save_file in sorted(saves_dir.glob('*.json')):
            if save_file.suffix == '.json' and not '.bak' in save_file.name:
                files_checked += 1
                if fix_save_file(save_file):
                    files_fixed += 1

    # Fix character files
    chars_dir = aerthos_dir / 'characters'
    if chars_dir.exists():
        print(f"\n--- Checking Character Files in {chars_dir} ---")
        for char_file in sorted(chars_dir.glob('*.json')):
            if char_file.suffix == '.json' and not '.bak' in char_file.name:
                files_checked += 1
                if fix_character_file(char_file):
                    files_fixed += 1

    # Fix party files
    parties_dir = aerthos_dir / 'parties'
    if parties_dir.exists():
        print(f"\n--- Checking Party Files in {parties_dir} ---")
        for party_file in sorted(parties_dir.glob('*.json')):
            if party_file.suffix == '.json' and not '.bak' in party_file.name:
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
        print("✓ Memorized spells were preserved where possible")
        print("✓ Original files backed up with timestamp")
        print("\nNote: If you have any active game sessions, you may need to reload them")
        print("      to see the corrected spell slots.")
    else:
        print("\n✓ All files already have correct spell slots!")

if __name__ == '__main__':
    main()
