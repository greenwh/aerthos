#!/usr/bin/env python3
"""
Test script to verify spell slot manipulation scripts work correctly.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to Python path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == 'scripts' else SCRIPT_DIR
sys.path.insert(0, str(PROJECT_ROOT))

# Import the functions we want to test
from reset_characters import reset_character
from fix_character_spell_slots import fix_character_spell_slots

class Args:
    """Mock args for testing"""
    def __init__(self, clear_spells=False, clear_conditions=False, backup=False):
        self.clear_spells = clear_spells
        self.clear_conditions = clear_conditions
        self.backup = backup

def test_reset_preserves_slots():
    """Test that reset_characters --clear-spells preserves slot structure"""
    print("\n" + "="*70)
    print("TEST 1: reset_characters.py --clear-spells preserves slots")
    print("="*70)

    # Create a test character with memorized spells
    test_char = {
        'name': 'Gandalf',
        'char_class': 'Magic-User',
        'level': 5,
        'hp_current': 10,
        'hp_max': 20,
        'spells_memorized': [
            {'level': 1, 'spell': 'magic_missile', 'is_used': False},
            {'level': 1, 'spell': 'sleep', 'is_used': True},
            {'level': 2, 'spell': 'invisibility', 'is_used': False},
            {'level': 2, 'spell': 'web', 'is_used': False},
            {'level': 3, 'spell': 'fireball', 'is_used': False},
        ],
        'conditions': ['poisoned', 'diseased']
    }

    print(f"\nBefore reset:")
    print(f"  HP: {test_char['hp_current']}/{test_char['hp_max']}")
    print(f"  Spell slots: {len(test_char['spells_memorized'])}")
    print(f"  Memorized spells: {sum(1 for s in test_char['spells_memorized'] if 'spell' in s and s.get('spell'))}")
    print(f"  Conditions: {test_char['conditions']}")

    # Test with --clear-spells
    args = Args(clear_spells=True, clear_conditions=True)
    reset_char, changes = reset_character(test_char, args)

    print(f"\nAfter reset with --clear-spells --clear-conditions:")
    print(f"  HP: {reset_char['hp_current']}/{reset_char['hp_max']}")
    print(f"  Spell slots: {len(reset_char['spells_memorized'])}")
    print(f"  Empty slots (no 'spell' field): {sum(1 for s in reset_char['spells_memorized'] if 'spell' not in s)}")
    print(f"  Conditions: {reset_char['conditions']}")
    print(f"\nChanges:")
    for change in changes:
        print(f"  - {change}")

    # Print slot structure for verification
    print(f"\nSlot structure:")
    for i, slot in enumerate(reset_char['spells_memorized']):
        print(f"  Slot {i+1}: {slot}")

    # Verify
    assert reset_char['hp_current'] == reset_char['hp_max'], "HP not restored!"
    assert len(reset_char['spells_memorized']) == 5, "Slots were deleted!"
    # IMPORTANT: Empty slots should NOT have 'spell' field at all
    assert all('spell' not in s for s in reset_char['spells_memorized']), "Slots still have 'spell' field!"
    assert all(not s.get('is_used') for s in reset_char['spells_memorized']), "is_used not cleared!"
    assert len(reset_char['conditions']) == 0, "Conditions not cleared!"

    print("\n✓ TEST PASSED: Slots preserved, spells cleared (no 'spell' field)!")
    return True

def test_fix_adjusts_slots():
    """Test that fix_character_spell_slots adjusts slots correctly"""
    print("\n" + "="*70)
    print("TEST 2: fix_character_spell_slots.py adjusts slots intelligently")
    print("="*70)

    # Test character with WRONG number of slots for their level
    # A level 5 Magic-User should have: [4, 2, 1] = 4 level 1, 2 level 2, 1 level 3
    test_char = {
        'name': 'Merlin',
        'char_class': 'Magic-User',
        'level': 5,
        'hp_current': 25,
        'hp_max': 25,
        'spells_memorized': [
            # Only has 2 level 1 slots (should have 4)
            {'level': 1, 'spell': 'magic_missile', 'is_used': False},
            {'level': 1, 'spell': 'shield', 'is_used': False},
        ]
    }

    print(f"\nBefore fix:")
    print(f"  Class/Level: {test_char['char_class']} {test_char['level']}")
    print(f"  Current slots: {len(test_char['spells_memorized'])}")
    print(f"  Slot breakdown: {[s['level'] for s in test_char['spells_memorized']]}")
    print(f"  Memorized spells: {[s.get('spell', 'EMPTY') for s in test_char['spells_memorized']]}")

    fixed_char, was_changed = fix_character_spell_slots(test_char)

    print(f"\nAfter fix:")
    print(f"  New slots: {len(fixed_char['spells_memorized'])}")
    print(f"  Slot breakdown: {[s['level'] for s in fixed_char['spells_memorized']]}")
    print(f"  Memorized spells: {[s.get('spell', 'EMPTY') for s in fixed_char['spells_memorized']]}")

    # Verify correct slot counts for level 5 Magic-User
    level_1_slots = sum(1 for s in fixed_char['spells_memorized'] if s['level'] == 1)
    level_2_slots = sum(1 for s in fixed_char['spells_memorized'] if s['level'] == 2)
    level_3_slots = sum(1 for s in fixed_char['spells_memorized'] if s['level'] == 3)

    print(f"\n  Level 1 slots: {level_1_slots} (expected 4)")
    print(f"  Level 2 slots: {level_2_slots} (expected 2)")
    print(f"  Level 3 slots: {level_3_slots} (expected 1)")

    # Print slot structure for verification
    print(f"\nSlot structure:")
    for i, slot in enumerate(fixed_char['spells_memorized']):
        print(f"  Slot {i+1}: {slot}")

    assert was_changed, "Should have been changed!"
    assert level_1_slots == 4, f"Wrong number of level 1 slots: {level_1_slots}"
    assert level_2_slots == 2, f"Wrong number of level 2 slots: {level_2_slots}"
    assert level_3_slots == 1, f"Wrong number of level 3 slots: {level_3_slots}"

    # Verify original spells were preserved
    preserved_spells = [s.get('spell') for s in fixed_char['spells_memorized'] if 'spell' in s and s.get('spell')]
    assert 'magic_missile' in preserved_spells, "Lost magic_missile!"
    assert 'shield' in preserved_spells, "Lost shield!"

    # Verify empty slots don't have 'spell' field
    empty_slots = [s for s in fixed_char['spells_memorized'] if 'spell' not in s]
    assert len(empty_slots) == 5, f"Should have 5 empty slots, got {len(empty_slots)}"

    print("\n✓ TEST PASSED: Slots adjusted correctly, spells preserved, empty slots correct!")
    return True

def test_fix_removes_excess_slots():
    """Test that fix removes excess slots for non-casters"""
    print("\n" + "="*70)
    print("TEST 3: fix_character_spell_slots.py removes slots from non-casters")
    print("="*70)

    # Fighter shouldn't have spell slots
    test_char = {
        'name': 'Conan',
        'char_class': 'Fighter',
        'level': 5,
        'hp_current': 45,
        'hp_max': 45,
        'spells_memorized': [
            {'level': 1, 'spell': 'magic_missile', 'is_used': False},
            {'level': 1, 'spell': 'shield', 'is_used': False},
        ]
    }

    print(f"\nBefore fix:")
    print(f"  Class/Level: {test_char['char_class']} {test_char['level']}")
    print(f"  Current slots: {len(test_char['spells_memorized'])} (should be 0)")

    fixed_char, was_changed = fix_character_spell_slots(test_char)

    print(f"\nAfter fix:")
    print(f"  New slots: {len(fixed_char['spells_memorized'])}")

    assert was_changed, "Should have been changed!"
    assert len(fixed_char['spells_memorized']) == 0, "Fighter should have no spell slots!"

    print("\n✓ TEST PASSED: Excess slots removed from non-caster!")
    return True

def main():
    print("=" * 70)
    print("SPELL SLOT SCRIPT VERIFICATION TESTS")
    print("=" * 70)

    try:
        test_reset_preserves_slots()
        test_fix_adjusts_slots()
        test_fix_removes_excess_slots()

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        print("\nBoth scripts are working correctly:")
        print("  ✓ reset_characters.py --clear-spells preserves slot structure")
        print("  ✓ fix_character_spell_slots.py adjusts slots intelligently")
        print("  ✓ Memorized spells are preserved where possible")

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
