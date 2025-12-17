#!/usr/bin/env python3
"""
Character validation script to check for data integrity issues.
Prevents save/load errors by validating character files.
"""

import sys
from pathlib import Path
import json
from typing import List, Dict, Any

# Add aerthos module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aerthos.constants import _AERTHOS_HOME, DATA_DIR

class ValidationError:
    """Represents a validation error"""
    def __init__(self, severity: str, character: str, field: str, message: str):
        self.severity = severity  # 'ERROR', 'WARNING'
        self.character = character
        self.field = field
        self.message = message

    def __str__(self):
        return f"[{self.severity}] {self.character} - {self.field}: {self.message}"


class CharacterValidator:
    """Validates character files for data integrity"""

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.roster_dir = _AERTHOS_HOME / 'characters'

        # Load spell progression tables
        level_prog_file = Path(DATA_DIR) / 'level_progression.json'
        with open(level_prog_file, 'r') as f:
            self.level_data = json.load(f)

    def validate_all_characters(self):
        """Validate all characters in the roster"""
        if not self.roster_dir.exists():
            print(f"Character roster directory not found: {self.roster_dir}")
            return

        char_files = list(self.roster_dir.glob('*.json'))
        if not char_files:
            print("No character files found.")
            return

        print(f"Validating {len(char_files)} character files...\n")

        for filepath in char_files:
            # Skip backup files
            if '.bak' in filepath.name:
                continue

            try:
                with open(filepath, 'r') as f:
                    char_data = json.load(f)
                self.validate_character(char_data, filepath.name)
            except json.JSONDecodeError as e:
                self.errors.append(ValidationError(
                    'ERROR', filepath.name, 'JSON', f'Invalid JSON: {e}'
                ))
            except Exception as e:
                self.errors.append(ValidationError(
                    'ERROR', filepath.name, 'LOAD', f'Failed to load: {e}'
                ))

    def validate_character(self, data: Dict[str, Any], filename: str):
        """Validate a single character's data"""
        char_name = data.get('name', filename)

        # Required fields
        required_fields = [
            'id', 'name', 'race', 'class', 'level', 'xp',
            'hp_max', 'hp_current', 'ac', 'thac0',
            'strength', 'dexterity', 'constitution',
            'intelligence', 'wisdom', 'charisma'
        ]

        for field in required_fields:
            if field not in data:
                self.errors.append(ValidationError(
                    'ERROR', char_name, field, 'Missing required field'
                ))

        # Validate inventory items
        if 'inventory' in data:
            for i, item in enumerate(data['inventory']):
                self.validate_item(item, char_name, f'inventory[{i}]')

        # Validate equipped items
        if 'equipped' in data:
            for slot, item in data['equipped'].items():
                if item:  # Slot might be None/empty
                    self.validate_item(item, char_name, f'equipped.{slot}')

        # Validate spell slots for casters
        char_class = data.get('class')
        char_level = data.get('level', 1)
        if char_class in ['Cleric', 'Druid', 'Magic-User', 'Illusionist', 'Paladin', 'Ranger']:
            self.validate_spell_slots(data, char_name, char_class, char_level)

        # Validate HP
        hp_current = data.get('hp_current', 0)
        hp_max = data.get('hp_max', 0)
        if hp_max <= 0:
            self.errors.append(ValidationError(
                'ERROR', char_name, 'hp_max', f'Invalid hp_max: {hp_max}'
            ))
        if hp_current < -10:
            self.errors.append(ValidationError(
                'WARNING', char_name, 'hp_current', f'Character may be dead: {hp_current}'
            ))

        # Validate level vs XP
        if char_class and char_level:
            self.validate_xp_level(char_name, char_class, char_level, data.get('xp', 0))

    def validate_item(self, item: Dict[str, Any], char_name: str, location: str):
        """Validate an item's data structure"""
        # Required fields for all items
        if 'name' not in item:
            self.errors.append(ValidationError(
                'ERROR', char_name, location, 'Item missing name field'
            ))
            return

        if 'type' not in item:
            self.errors.append(ValidationError(
                'ERROR', char_name, location, f"Item '{item['name']}' missing type field"
            ))
            return

        if 'weight' not in item:
            self.errors.append(ValidationError(
                'WARNING', char_name, location, f"Item '{item['name']}' missing weight field"
            ))

        # Type-specific validation
        item_type = item['type']

        if item_type == 'weapon':
            required = ['damage_sm', 'damage_l', 'speed_factor']
            for field in required:
                if field not in item:
                    self.errors.append(ValidationError(
                        'ERROR', char_name, location,
                        f"Weapon '{item['name']}' missing {field}"
                    ))

        elif item_type == 'armor':
            if 'ac' not in item:
                self.errors.append(ValidationError(
                    'ERROR', char_name, location,
                    f"Armor '{item['name']}' missing ac field"
                ))

        elif item_type == 'light_source':
            # CRITICAL: This was causing the save error!
            required = ['burn_time_turns', 'turns_remaining']
            for field in required:
                if field not in item:
                    self.errors.append(ValidationError(
                        'ERROR', char_name, location,
                        f"Light source '{item['name']}' missing {field} (will cause save error!)"
                    ))

    def validate_spell_slots(self, data: Dict[str, Any], char_name: str,
                            char_class: str, char_level: int):
        """Validate spell slots match class progression"""
        if char_class not in self.level_data:
            return  # No spell progression for this class

        class_data = self.level_data[char_class]
        if 'spell_slots' not in class_data:
            return  # Class doesn't have spell slots

        spell_slots_table = class_data['spell_slots']
        level_index = char_level - 1

        # Count current slots
        current_slots = {}
        spells_memorized = data.get('spells_memorized', [])
        for slot in spells_memorized:
            slot_level = slot.get('level')
            if slot_level:
                current_slots[slot_level] = current_slots.get(slot_level, 0) + 1

        # Check expected vs actual
        for spell_level_str, counts in spell_slots_table.items():
            spell_level = int(spell_level_str)
            if level_index < len(counts):
                expected = counts[level_index]
                actual = current_slots.get(spell_level, 0)

                if actual < expected:
                    self.errors.append(ValidationError(
                        'WARNING', char_name, 'spells_memorized',
                        f"Missing spell slots: L{spell_level} (has {actual}, needs {expected})"
                    ))
                elif actual > expected:
                    self.errors.append(ValidationError(
                        'WARNING', char_name, 'spells_memorized',
                        f"Too many spell slots: L{spell_level} (has {actual}, should be {expected})"
                    ))

    def validate_xp_level(self, char_name: str, char_class: str,
                         char_level: int, xp: int):
        """Validate XP matches level"""
        if char_class not in self.level_data:
            return

        xp_table = self.level_data[char_class].get('xp_table', [])
        level_index = char_level - 1

        # Check if XP is enough for current level
        if level_index > 0 and level_index < len(xp_table):
            required_xp = xp_table[level_index - 1]
            if xp < required_xp:
                self.errors.append(ValidationError(
                    'ERROR', char_name, 'xp',
                    f"Insufficient XP for level {char_level} (has {xp:,}, needs {required_xp:,})"
                ))

        # Check if should be higher level
        if level_index + 1 < len(xp_table):
            next_level_xp = xp_table[level_index]
            if xp >= next_level_xp:
                self.errors.append(ValidationError(
                    'WARNING', char_name, 'level',
                    f"Has enough XP for level {char_level + 1} ({xp:,} >= {next_level_xp:,})"
                ))

    def print_report(self):
        """Print validation report"""
        if not self.errors:
            print("✓ All characters validated successfully!")
            print("  No errors or warnings found.")
            return 0

        # Group by severity
        errors = [e for e in self.errors if e.severity == 'ERROR']
        warnings = [e for e in self.errors if e.severity == 'WARNING']

        print(f"Validation complete: {len(errors)} errors, {len(warnings)} warnings\n")

        if errors:
            print("ERRORS (will cause save/load failures):")
            print("=" * 60)
            for error in errors:
                print(f"  {error}")
            print()

        if warnings:
            print("WARNINGS (potential issues):")
            print("=" * 60)
            for warning in warnings:
                print(f"  {warning}")
            print()

        return 1 if errors else 0


def main():
    """Run character validation"""
    print("=== Character Validation ===\n")

    validator = CharacterValidator()
    validator.validate_all_characters()
    return validator.print_report()


if __name__ == "__main__":
    sys.exit(main())
