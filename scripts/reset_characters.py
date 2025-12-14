#!/usr/bin/env python3
"""
Reset characters to fresh state - useful for testing or "long rest" simulation.

This script can:
1. Reset HP to maximum
2. Reset spell "is_used" flags (restore all memorized spells)
3. Optionally clear all memorized spells
4. Optionally clear all conditions
"""

import json
import shutil
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path so we can import from aerthos
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == 'scripts' else SCRIPT_DIR
sys.path.insert(0, str(PROJECT_ROOT))

def reset_character(character_data: dict, args) -> tuple[dict, list]:
    """
    Reset character data based on options.
    Returns (updated_character, list_of_changes)
    """
    changes = []
    name = character_data.get('name', 'Unknown')
    char_class = character_data.get('char_class', 'Unknown')
    level = character_data.get('level', 1)

    # 1. Reset HP to maximum (always done)
    hp_current = character_data.get('hp_current', 0)
    hp_max = character_data.get('hp_max', 0)

    if hp_current != hp_max:
        character_data['hp_current'] = hp_max
        changes.append(f"HP: {hp_current} → {hp_max}")

    # 2. Reset spell "is_used" flags
    spells_memorized = character_data.get('spells_memorized', [])

    if spells_memorized:
        spells_restored = 0
        for slot in spells_memorized:
            if slot.get('is_used', False):
                slot['is_used'] = False
                spells_restored += 1

        if spells_restored > 0:
            changes.append(f"Restored {spells_restored} spent spell slot(s)")

    # 3. Optionally clear all memorized spells
    if args.clear_spells and spells_memorized:
        # Count how many slots had spells
        spells_cleared = sum(1 for slot in spells_memorized if slot.get('spell') is not None)

        # Clear all spell references but keep slots
        for slot in spells_memorized:
            slot['spell'] = None
            slot['is_used'] = False

        character_data['spells_memorized'] = spells_memorized

        if spells_cleared > 0:
            changes.append(f"Cleared {spells_cleared} memorized spell(s) from {len(spells_memorized)} slot(s)")

    # 4. Optionally clear conditions
    conditions = character_data.get('conditions', [])

    if args.clear_conditions and conditions:
        conditions_cleared = len(conditions)
        character_data['conditions'] = []
        changes.append(f"Cleared {conditions_cleared} condition(s): {', '.join(conditions)}")

    return character_data, changes

def process_save_file(save_path: Path, args) -> tuple[bool, list]:
    """Process a save file. Returns (was_modified, changes)"""
    changes = []

    # Load save file
    with open(save_path, 'r') as f:
        save_data = json.load(f)

    # Check if this save has a player
    if 'player' not in save_data:
        return False, ["No player data found"]

    # Reset player
    player_data, player_changes = reset_character(save_data['player'], args)

    if player_changes:
        # Backup original
        if args.backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = save_path.with_suffix(f'.json.{timestamp}.bak')
            shutil.copy2(save_path, backup_path)
            changes.append(f"Backup: {backup_path.name}")

        # Save updated version
        save_data['player'] = player_data
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)

        return True, player_changes + changes

    return False, ["No changes needed"]

def process_character_file(char_path: Path, args) -> tuple[bool, list]:
    """Process a character file. Returns (was_modified, changes)"""
    changes = []

    # Load character file
    with open(char_path, 'r') as f:
        char_data = json.load(f)

    # Reset character
    char_data, char_changes = reset_character(char_data, args)

    if char_changes:
        # Backup original
        if args.backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = char_path.with_suffix(f'.json.{timestamp}.bak')
            shutil.copy2(char_path, backup_path)
            changes.append(f"Backup: {backup_path.name}")

        # Save updated version
        with open(char_path, 'w') as f:
            json.dump(char_data, f, indent=2)

        return True, char_changes + changes

    return False, ["No changes needed"]

def process_party_file(party_path: Path, args) -> tuple[bool, list]:
    """Process a party file. Returns (was_modified, changes)"""
    all_changes = []

    # Load party file
    with open(party_path, 'r') as f:
        party_data = json.load(f)

    # Check if this party has members
    if 'members' not in party_data:
        return False, ["No members data found"]

    modified = False
    for i, member in enumerate(party_data['members']):
        member_data, member_changes = reset_character(member, args)

        if member_changes:
            party_data['members'][i] = member_data
            modified = True
            member_name = member.get('name', f'Member {i+1}')
            all_changes.append(f"{member_name}: {', '.join(member_changes)}")

    if modified:
        # Backup original
        if args.backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = party_path.with_suffix(f'.json.{timestamp}.bak')
            shutil.copy2(party_path, backup_path)
            all_changes.insert(0, f"Backup: {backup_path.name}")

        # Save updated version
        with open(party_path, 'w') as f:
            json.dump(party_data, f, indent=2)

        return True, all_changes

    return False, ["No changes needed"]

def main():
    parser = argparse.ArgumentParser(
        description='Reset characters in save/character/party files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Reset HP and restore spell slots (default):
  python3 reset_characters.py

  # Reset HP, restore spells, and clear conditions:
  python3 reset_characters.py --clear-conditions

  # Full reset (HP, clear all spells, clear conditions):
  python3 reset_characters.py --clear-spells --clear-conditions

  # Process only save files:
  python3 reset_characters.py --saves-only

  # Process specific file:
  python3 reset_characters.py --file ~/.aerthos/saves/save_1.json

  # Dry run (show what would change without modifying files):
  python3 reset_characters.py --dry-run

  # Disable backups (not recommended):
  python3 reset_characters.py --no-backup
        """
    )

    # What to reset
    parser.add_argument('--clear-spells', action='store_true',
                      help='Clear all memorized spells (keeps slots empty)')
    parser.add_argument('--clear-conditions', action='store_true',
                      help='Clear all conditions (poisoned, diseased, etc.)')

    # Which files to process
    parser.add_argument('--saves-only', action='store_true',
                      help='Only process save files')
    parser.add_argument('--characters-only', action='store_true',
                      help='Only process character files')
    parser.add_argument('--parties-only', action='store_true',
                      help='Only process party files')
    parser.add_argument('--file', type=str,
                      help='Process a specific file instead of all files')

    # Options
    parser.add_argument('--no-backup', action='store_true',
                      help='Do not create backup files (not recommended)')
    parser.add_argument('--dry-run', action='store_true',
                      help='Show what would be changed without modifying files')

    args = parser.parse_args()

    # Set backup flag (opposite of --no-backup)
    args.backup = not args.no_backup

    print("=" * 70)
    print("CHARACTER RESET SCRIPT")
    print("=" * 70)
    print()
    print("Settings:")
    print(f"  Reset HP to max:        YES (always)")
    print(f"  Restore spell slots:    YES (always)")
    print(f"  Clear memorized spells: {'YES' if args.clear_spells else 'NO'}")
    print(f"  Clear conditions:       {'YES' if args.clear_conditions else 'NO'}")
    print(f"  Create backups:         {'NO' if args.no_backup else 'YES'}")
    print(f"  Dry run:                {'YES (no files will be modified)' if args.dry_run else 'NO'}")
    print()

    # Get aerthos data directory from constants.py
    from aerthos.constants import _AERTHOS_HOME
    aerthos_dir = Path(_AERTHOS_HOME)

    files_processed = 0
    files_modified = 0

    # Process specific file if requested
    if args.file:
        file_path = Path(args.file).expanduser()

        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return

        print(f"Processing: {file_path}")

        if args.dry_run:
            print("  [DRY RUN - No changes will be made]")

        # Detect file type and process
        if 'save' in file_path.parent.name:
            modified, changes = process_save_file(file_path, args)
        elif 'character' in file_path.parent.name:
            modified, changes = process_character_file(file_path, args)
        elif 'part' in file_path.parent.name:
            modified, changes = process_party_file(file_path, args)
        else:
            # Try to detect by content
            with open(file_path, 'r') as f:
                data = json.load(f)

            if 'player' in data and 'dungeon_state' in data:
                modified, changes = process_save_file(file_path, args)
            elif 'members' in data:
                modified, changes = process_party_file(file_path, args)
            else:
                modified, changes = process_character_file(file_path, args)

        for change in changes:
            print(f"  {change}")

        if modified:
            files_modified += 1
        files_processed += 1

    else:
        # Process all files in standard directories

        # Process save files
        if not args.characters_only and not args.parties_only:
            saves_dir = aerthos_dir / 'saves'
            if saves_dir.exists():
                print(f"--- Save Files ({saves_dir}) ---")
                for save_file in sorted(saves_dir.glob('*.json')):
                    if not save_file.name.endswith('.bak'):
                        print(f"\n{save_file.name}:")

                        if args.dry_run:
                            print("  [DRY RUN - No changes will be made]")
                            # Read and analyze but don't modify
                            with open(save_file, 'r') as f:
                                save_data = json.load(f)
                            if 'player' in save_data:
                                _, changes = reset_character(save_data['player'], args)
                                for change in changes:
                                    print(f"  Would apply: {change}")
                                if changes:
                                    files_modified += 1
                        else:
                            modified, changes = process_save_file(save_file, args)
                            for change in changes:
                                print(f"  {change}")
                            if modified:
                                files_modified += 1

                        files_processed += 1

        # Process character files
        if not args.saves_only and not args.parties_only:
            chars_dir = aerthos_dir / 'characters'
            if chars_dir.exists():
                print(f"\n--- Character Files ({chars_dir}) ---")
                for char_file in sorted(chars_dir.glob('*.json')):
                    if not char_file.name.endswith('.bak'):
                        print(f"\n{char_file.name}:")

                        if args.dry_run:
                            print("  [DRY RUN - No changes will be made]")
                            with open(char_file, 'r') as f:
                                char_data = json.load(f)
                            _, changes = reset_character(char_data, args)
                            for change in changes:
                                print(f"  Would apply: {change}")
                            if changes:
                                files_modified += 1
                        else:
                            modified, changes = process_character_file(char_file, args)
                            for change in changes:
                                print(f"  {change}")
                            if modified:
                                files_modified += 1

                        files_processed += 1

        # Process party files
        if not args.saves_only and not args.characters_only:
            parties_dir = aerthos_dir / 'parties'
            if parties_dir.exists():
                print(f"\n--- Party Files ({parties_dir}) ---")
                for party_file in sorted(parties_dir.glob('*.json')):
                    if not party_file.name.endswith('.bak'):
                        print(f"\n{party_file.name}:")

                        if args.dry_run:
                            print("  [DRY RUN - No changes will be made]")
                            with open(party_file, 'r') as f:
                                party_data = json.load(f)
                            if 'members' in party_data:
                                modified = False
                                for member in party_data['members']:
                                    _, changes = reset_character(member, args)
                                    if changes:
                                        member_name = member.get('name', 'Unknown')
                                        print(f"  {member_name}: {', '.join(changes)}")
                                        modified = True
                                if modified:
                                    files_modified += 1
                        else:
                            modified, changes = process_party_file(party_file, args)
                            for change in changes:
                                print(f"  {change}")
                            if modified:
                                files_modified += 1

                        files_processed += 1

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files processed: {files_processed}")
    print(f"Files modified:  {files_modified}")
    print(f"Files unchanged: {files_processed - files_modified}")

    if args.dry_run:
        print("\n⚠ DRY RUN - No files were actually modified")
        print("  Run without --dry-run to apply changes")
    elif files_modified > 0:
        print("\n✓ Characters have been reset!")
        if args.backup:
            print("✓ Original files backed up with timestamp")
        print("\nChanges applied:")
        print("  • HP restored to maximum")
        print("  • Spell slots restored (is_used flags cleared)")
        if args.clear_spells:
            print("  • Memorized spells cleared")
        if args.clear_conditions:
            print("  • Conditions cleared")
    else:
        print("\n✓ All characters already at full health with restored spells!")

if __name__ == '__main__':
    main()
