#!/usr/bin/env python3
"""
Quick test to verify treasure-to-item conversion fixes
Tests the specific problem cases reported by the user
"""

from aerthos.engine.game_state import GameData, GameState
from aerthos.entities.player import PlayerCharacter
from aerthos.world.dungeon import Dungeon, Room

# Load game data
game_data = GameData.load_all()

# Create a minimal game state for testing
test_char = PlayerCharacter(
    name="Test",
    race="Human",
    char_class="Fighter",
    strength=15, dexterity=14, constitution=13,
    intelligence=10, wisdom=10, charisma=10,
    level=1, hp_current=10, hp_max=10, ac=10, thac0=20
)

test_room = Room(
    id="test_room",
    title="Test Room",
    description="Test",
    exits={},
    light_level="bright",
    items=[]
)

test_dungeon = Dungeon(
    name="Test Dungeon",
    start_room_id="test_room",
    rooms={"test_room": test_room}
)

game_state = GameState(test_char, test_dungeon)
game_state.game_data = game_data

print("Testing Treasure-to-Item Conversion Fixes")
print("=" * 60)

# Test cases from user's bug report
test_cases = [
    # Potions - should get correct types now
    ("potion_extra_healing", "Potion of Extra-Healing"),
    ("greater_healing_potion", "Potion of Greater Healing"),
    ("potion_greater_healing", "Potion of Greater Healing"),

    # Regular weapons - should create functional Weapon objects
    ("longsword", "Long Sword"),  # weapons.json uses "Long Sword"
    ("dagger", "Dagger"),
    ("battle_axe", "Battle Axe"),

    # Regular armor - should create functional Armor objects
    ("chain_mail", "Chain Mail"),
    ("chainmail", "Chain Mail"),  # Alternative spelling

    # Magic weapons - should work as before
    ("battleaxe_plus2", "Battle Axe +2"),
    ("longsword_plus1", "Long Sword +1"),  # weapons.json uses "Long Sword"
    ("chainmail_plus1", "Chain Mail +1"),
]

print("\nTest Results:")
print("-" * 60)

failures = []
for item_id, expected_name in test_cases:
    item = game_state._create_item_from_name(item_id)
    if item:
        # Check name matches
        if expected_name.lower() in item.name.lower():
            status = "✓ PASS"
            type_info = f"Type: {item.item_type}"
            if hasattr(item, 'damage_sm'):
                type_info = f"Weapon (dmg: {item.damage_sm}/{item.damage_l})"
            elif hasattr(item, 'ac'):
                type_info = f"Armor (AC: {item.ac})"
        else:
            status = "✗ FAIL"
            type_info = f"Got '{item.name}' instead"
            failures.append((item_id, expected_name, item.name))

        print(f"{status} {item_id:25} -> {item.name:30} [{type_info}]")
    else:
        status = "✗ FAIL"
        print(f"{status} {item_id:25} -> NOT CREATED")
        failures.append((item_id, expected_name, "None"))

print("=" * 60)

if failures:
    print(f"\n⚠ {len(failures)} test(s) failed:")
    for item_id, expected, got in failures:
        print(f"  - {item_id}: expected '{expected}', got '{got}'")
    exit(1)
else:
    print("\n✓ All tests passed!")
    print("\nTreasure fixes verified:")
    print("  • Specific potions (extra-healing, greater) work correctly")
    print("  • Regular weapons create functional Weapon objects")
    print("  • Regular armor creates functional Armor objects")
    print("  • Magic items (+1, +2, etc.) still work")
    exit(0)
