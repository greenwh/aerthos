#!/usr/bin/env python3
"""
Add missing monsters to monsters.json
"""

import json

# Load monsters
with open('aerthos/data/monsters.json', 'r') as f:
    monsters = json.load(f)

# Add missing monsters
missing_monsters = {
    "thug": {
        "name": "Thug",
        "hit_dice": "2d8",
        "ac": 7,
        "thac0": 19,
        "damage": "1d6",
        "size": "M",
        "movement": 12,
        "morale": 8,
        "treasure_type": "Individuals P",
        "xp_value": 20,
        "special_abilities": [],
        "description": "A common criminal enforcer or hired muscle, skilled with clubs and daggers."
    },
    "silas_merchant": {
        "name": "Silas the Corrupt Merchant",
        "hit_dice": "5d8",
        "ac": 5,
        "thac0": 16,
        "damage": "1d8+2",
        "size": "M",
        "movement": 12,
        "morale": 12,
        "treasure_type": "Q, X, magic items",
        "xp_value": 300,
        "special_abilities": ["cunning_defense", "poison_dagger"],
        "description": "A wealthy merchant corrupted by the cult, Silas uses his resources and connections to further the serpent cult's goals. He fights with a poisoned dagger and tactical cunning."
    },
    "grathak_soulless": {
        "name": "Grathak the Soulless",
        "hit_dice": "7d8+7",
        "ac": 3,
        "thac0": 14,
        "damage": "2d6+3",
        "size": "M",
        "movement": 9,
        "morale": 14,
        "treasure_type": "Q, X, magic weapon, magic armor",
        "xp_value": 500,
        "special_abilities": ["duergar_invisibility", "command_presence", "dark_magic"],
        "description": "The soulless duergar chieftain who sold his people to the cult. Grathak wields dark magic and a massive warhammer, and can turn invisible like all duergar."
    },
    "giant_snake": {
        "name": "Giant Constrictor Snake",
        "hit_dice": "4d8",
        "ac": 5,
        "thac0": 16,
        "damage": "1d6",
        "size": "L",
        "movement": 9,
        "morale": 7,
        "treasure_type": "None",
        "xp_value": 120,
        "special_abilities": ["constrict"],
        "description": "A massive serpent that crushes prey in its coils. After a successful hit, it constricts for automatic 2d4 damage per round until the victim escapes."
    }
}

# Add monsters
added = []
for monster_id, monster_data in missing_monsters.items():
    if monster_id not in monsters:
        monsters[monster_id] = monster_data
        added.append(monster_id)
        print(f"✅ Added: {monster_id} ({monster_data['name']})")
    else:
        print(f"⚠️  Already exists: {monster_id}")

# Save updated monsters
with open('aerthos/data/monsters.json', 'w') as f:
    json.dump(monsters, f, indent=2)

print(f"\n✅ Added {len(added)} missing monsters to monsters.json")
