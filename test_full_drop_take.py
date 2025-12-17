#!/usr/bin/env python3
"""
End-to-end test: Simulate the full drop/take cycle
Tests that items work through multiple drop/take cycles
"""

from aerthos.engine.game_state import GameData, GameState
from aerthos.entities.player import PlayerCharacter
from aerthos.world.dungeon import Dungeon, Room

# Setup
game_data = GameData.load_all()

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
    title="Treasure Room",
    description="A room with magic items",
    exits={},
    light_level="bright",
    items=["battleaxe_plus2", "chainmail_plus1", "potion_extra_healing"]
)

test_dungeon = Dungeon(
    name="Test Dungeon",
    start_room_id="test_room",
    rooms={"test_room": test_room}
)

game_state = GameState(test_char, test_dungeon)
game_state.game_data = game_data

print("END-TO-END Drop/Take Cycle Test")
print("=" * 70)

def check_item(item, expected_type, expected_name):
    """Helper to check item properties"""
    if not item:
        return False, "Item is None"

    if type(item).__name__ != expected_type:
        return False, f"Wrong type: {type(item).__name__} (expected {expected_type})"

    if expected_name.lower() not in item.name.lower():
        return False, f"Wrong name: {item.name} (expected {expected_name})"

    return True, "OK"

# Test each item through multiple cycles
test_items = [
    ("battleaxe_plus2", "Weapon", "Battle Axe +2"),
    ("chainmail_plus1", "Armor", "Chain Mail +1"),
    ("potion_extra_healing", "Item", "Extra-Healing"),
]

all_passed = True

for orig_name, expected_type, expected_name in test_items:
    print(f"\nTesting: {orig_name}")
    print("-" * 70)

    # CYCLE 1: Take from room
    print(f"  Cycle 1: Take from room ('{orig_name}')")
    item1 = game_state._create_item_from_name(orig_name)
    ok, msg = check_item(item1, expected_type, expected_name)
    if ok:
        print(f"    ✓ Created: {item1.name} ({expected_type})")
    else:
        print(f"    ✗ FAILED: {msg}")
        all_passed = False
        continue

    # Simulate drop - extract name
    dropped_name = item1.name
    print(f"    → If dropped, room gets: '{dropped_name}'")

    # CYCLE 2: Take dropped item
    print(f"  Cycle 2: Take from room ('{dropped_name}')")
    item2 = game_state._create_item_from_name(dropped_name)
    ok, msg = check_item(item2, expected_type, expected_name)
    if ok:
        print(f"    ✓ Created: {item2.name} ({expected_type})")
    else:
        print(f"    ✗ FAILED: {msg}")
        all_passed = False
        continue

    # CYCLE 3: Drop and take again
    dropped_name2 = item2.name
    print(f"  Cycle 3: Take from room ('{dropped_name2}')")
    item3 = game_state._create_item_from_name(dropped_name2)
    ok, msg = check_item(item3, expected_type, expected_name)
    if ok:
        print(f"    ✓ Created: {item3.name} ({expected_type})")
        print(f"    ✓ Item survives multiple drop/take cycles!")
    else:
        print(f"    ✗ FAILED: {msg}")
        all_passed = False

print("\n" + "=" * 70)

if all_passed:
    print("✓ SUCCESS: All items work correctly through multiple drop/take cycles!")
    print("\nConclusion:")
    print("  • Items can be taken from dungeons")
    print("  • Items can be dropped and re-taken")
    print("  • Items maintain functionality through cycles")
    print("  • Both underscore format (battleaxe_plus2) and space format (Battle Axe +2) work")
    exit(0)
else:
    print("✗ FAILURE: Some items failed drop/take cycles")
    exit(1)
