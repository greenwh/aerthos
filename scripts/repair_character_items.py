#!/usr/bin/env python3
"""
Repair broken treasure items in saved character files

This script fixes items that were stored as type="treasure" instead of
proper Weapon/Armor/Item objects due to the old conversion bug.
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import aerthos modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from aerthos.engine.game_state import GameData

def item_to_dict(item):
    """Convert an Item/Weapon/Armor object to a dictionary for JSON serialization"""
    from aerthos.entities.player import Weapon, Armor, Shield, LightSource, Item

    data = {
        'name': item.name,
        'type': item.item_type,
        'weight': item.weight,
    }

    # Add weapon-specific fields
    if isinstance(item, Weapon):
        data['type'] = 'weapon'
        data['damage_sm'] = item.damage_sm
        data['damage_l'] = item.damage_l
        data['speed_factor'] = item.speed_factor
        data['magic_bonus'] = item.magic_bonus

    # Add armor-specific fields
    elif isinstance(item, Armor):
        data['type'] = 'armor'
        data['ac'] = item.ac
        data['armor_type'] = item.armor_type
        data['movement_rate'] = item.movement_rate
        data['magic_bonus'] = item.magic_bonus

    # Add shield-specific fields
    elif isinstance(item, Shield):
        data['type'] = 'shield'
        data['ac_bonus'] = item.ac_bonus

    # Add light source-specific fields
    elif isinstance(item, LightSource):
        data['type'] = 'light_source'
        data['burn_time_turns'] = item.burn_time_turns
        data['light_radius'] = item.light_radius
        if hasattr(item, 'turns_remaining'):
            data['turns_remaining'] = item.turns_remaining

    # Add properties if present
    if hasattr(item, 'properties') and item.properties:
        # Only add non-empty properties
        if item.properties:
            data['properties'] = item.properties

    # Add description if present
    if hasattr(item, 'description') and item.description:
        data['description'] = item.description

    return data


def repair_character_file(filepath, game_data, dry_run=False):
    """Repair broken treasure items in a character file"""

    # Temporary game state to use _create_item_from_name
    class TempGameState:
        def __init__(self, game_data):
            self.game_data = game_data

        # Import the actual _create_item_from_name method
        from aerthos.engine.game_state import GameState
        _create_item_from_name = GameState._create_item_from_name

    temp_state = TempGameState(game_data)

    # Load character file
    with open(filepath, 'r') as f:
        char_data = json.load(f)

    char_name = char_data.get('name', 'Unknown')
    inventory = char_data.get('inventory', [])

    print(f"\nChecking: {char_name} ({filepath.name})")

    # Find and fix broken items
    fixed_items = []
    fixed_count = 0

    for item in inventory:
        item_name = item.get('name', '')
        item_type = item.get('type', '')

        # Check if it's a broken treasure item
        if item_type == 'treasure' and item_name:
            print(f"  Found broken item: {item_name} (type: treasure)")

            # Try to recreate it properly
            fixed_item = temp_state._create_item_from_name(item_name)

            if fixed_item:
                # Convert to dict
                fixed_dict = item_to_dict(fixed_item)

                # Check if it's actually different (not just treasure anymore)
                if fixed_dict['type'] != 'treasure':
                    print(f"    ✓ Fixed: {fixed_item.name} (type: {fixed_dict['type']})")
                    fixed_items.append(fixed_dict)
                    fixed_count += 1
                else:
                    print(f"    ⚠ Still treasure: {item_name} (no conversion available)")
                    fixed_items.append(item)
            else:
                print(f"    ✗ Could not convert: {item_name}")
                fixed_items.append(item)
        else:
            # Keep item as-is
            fixed_items.append(item)

    # Update inventory
    if fixed_count > 0:
        print(f"  Total fixed: {fixed_count} item(s)")

        if not dry_run:
            # Backup original file
            backup_path = str(filepath) + f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            with open(backup_path, 'w') as f:
                json.dump(char_data, f, indent=2)
            print(f"  Backup saved: {backup_path}")

            # Update character data
            char_data['inventory'] = fixed_items

            # Save repaired file
            with open(filepath, 'w') as f:
                json.dump(char_data, f, indent=2)
            print(f"  ✓ Character file updated!")
        else:
            print(f"  (DRY RUN - no changes made)")

        return fixed_count
    else:
        print(f"  No broken items found")
        return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Repair broken treasure items in character files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')
    parser.add_argument('--character', help='Repair specific character file (otherwise repairs all)')
    args = parser.parse_args()

    print("=" * 70)
    print("Character Item Repair Tool")
    print("=" * 70)

    # Load game data
    print("\nLoading game data...")
    game_data = GameData.load_all()
    print("✓ Game data loaded")

    # Find character files
    char_dir = Path.home() / '.aerthos' / 'characters'

    if not char_dir.exists():
        print(f"\n✗ Character directory not found: {char_dir}")
        return

    if args.character:
        # Repair specific character
        char_file = char_dir / args.character
        if not char_file.exists():
            print(f"\n✗ Character file not found: {char_file}")
            return
        char_files = [char_file]
    else:
        # Find all character files
        char_files = list(char_dir.glob('*.json'))
        # Exclude backups
        char_files = [f for f in char_files if '.bak' not in str(f)]

    if not char_files:
        print(f"\n✗ No character files found in {char_dir}")
        return

    print(f"\nFound {len(char_files)} character file(s)")

    if args.dry_run:
        print("\n⚠ DRY RUN MODE - No changes will be made\n")

    # Repair each character
    total_fixed = 0
    for char_file in sorted(char_files):
        fixed = repair_character_file(char_file, game_data, dry_run=args.dry_run)
        total_fixed += fixed

    # Summary
    print("\n" + "=" * 70)
    if args.dry_run:
        print(f"DRY RUN COMPLETE - {total_fixed} item(s) would be fixed")
    else:
        print(f"REPAIR COMPLETE - {total_fixed} item(s) fixed")
    print("=" * 70)


if __name__ == '__main__':
    main()
