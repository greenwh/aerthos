#!/usr/bin/env python3
"""Create test characters to verify reset/fix scripts work on character files"""

import json
import sys
from pathlib import Path

# Sample character data matching the game's format
def create_test_character(name, char_class, level, hp_current=None):
    """Create a test character JSON structure"""

    # HP by class (simplified)
    hp_max_by_class = {
        'Fighter': 10,
        'Cleric': 8,
        'Magic-User': 4,
        'Thief': 6
    }

    hp_max = hp_max_by_class.get(char_class, 8) * level

    char = {
        "id": f"test_{name.lower()}",
        "name": name,
        "race": "Human",
        "char_class": char_class,
        "level": level,
        "strength": 14,
        "dexterity": 12,
        "constitution": 13,
        "intelligence": 11,
        "wisdom": 10,
        "charisma": 9,
        "strength_percentile": 0,
        "hp_current": hp_current if hp_current is not None else hp_max,
        "hp_max": hp_max,
        "ac": 5,
        "thac0": 20 - level,
        "xp": 0,
        "xp_to_next_level": 2000,
        "gold": 100,
        "copper_pieces": 0,
        "silver_pieces": 0,
        "electrum_pieces": 0,
        "gold_pieces": 100,
        "platinum_pieces": 0,
        "conditions": [],
        "inventory": [],
        "equipment": {},
        "thief_skills": {},
        "spells_known": [],
        "spells_memorized": []
    }

    # Add spell slots for casters
    if char_class in ['Cleric', 'Magic-User']:
        # Add some test spell slots with old broken format for testing
        if level >= 5:
            # This mimics the OLD broken format
            char["spells_memorized"] = [
                {"level": 1, "spell": None, "is_used": False},
                {"level": 1, "spell": None, "is_used": False},
                {"level": 2, "spell": None, "is_used": True},  # One used spell
            ]

    # Add some conditions for testing
    if name == "Gandor":
        char["conditions"] = ["poisoned", "weakened"]
        char["hp_current"] = hp_max // 2  # Half health

    return char

def create_test_party(name, members):
    """Create a test party JSON structure"""
    return {
        "id": f"test_{name.lower().replace(' ', '_')}",
        "name": name,
        "created_at": "2025-12-14T14:00:00",
        "members": members
    }

# Create test directory
home = Path.home()
aerthos_dir = home / '.aerthos'
chars_dir = aerthos_dir / 'characters'
parties_dir = aerthos_dir / 'parties'

chars_dir.mkdir(parents=True, exist_ok=True)
parties_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("CREATING TEST CHARACTERS")
print("=" * 70)
print()

# Create individual character files
test_chars = [
    ("Thorgrim", "Fighter", 5, 40),  # Level 5 fighter, damaged
    ("Elara", "Cleric", 7, 56),      # Level 7 cleric, full health
    ("Gandor", "Magic-User", 5, None),  # Level 5 wizard, will add conditions
    ("Whisper", "Thief", 3, 18),     # Level 3 thief, full health
]

created_chars = []

for name, char_class, level, hp_current in test_chars:
    char = create_test_character(name, char_class, level, hp_current)
    created_chars.append(char)

    # Save character file
    char_file = chars_dir / f"{char['id']}.json"
    with open(char_file, 'w') as f:
        json.dump(char, f, indent=2)

    print(f"✓ Created: {name} ({char_class} {level})")
    print(f"  File: {char_file.name}")
    print(f"  HP: {char['hp_current']}/{char['hp_max']}")
    if char.get('conditions'):
        print(f"  Conditions: {', '.join(char['conditions'])}")
    if char.get('spells_memorized'):
        used_spells = sum(1 for s in char['spells_memorized'] if s.get('is_used'))
        print(f"  Spell slots: {len(char['spells_memorized'])} ({used_spells} used)")
    print()

# Create a test party
party = create_test_party("The Brave Adventurers", created_chars[:3])  # First 3 chars
party_file = parties_dir / f"{party['id']}.json"
with open(party_file, 'w') as f:
    json.dump(party, f, indent=2)

print(f"✓ Created party: {party['name']}")
print(f"  File: {party_file.name}")
print(f"  Members: {', '.join(m['name'] for m in party['members'])}")
print()

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Characters created: {len(created_chars)}")
print(f"Parties created: 1")
print()
print("You can now test the scripts:")
print("  python3 reset_characters.py --dry-run")
print("  python3 scripts/fix_character_spell_slots.py")
