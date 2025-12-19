#!/usr/bin/env python3
"""Test the drop/take cycle for magic items"""

from aerthos.engine.game_state import GameData, GameState
from aerthos.entities.player import PlayerCharacter
from aerthos.world.dungeon import Dungeon, Room

# Load game data
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

print("Testing Drop/Take Cycle for Magic Items")
print("=" * 60)

# Test both underscore and space formats
test_items = [
    "battleaxe_plus2",      # Original dungeon format
    "Battle Axe +2",        # After-drop format (with spaces and +)
    "chainmail_plus1",      # Original format
    "Chain Mail +1",        # After-drop format
]

for item_name in test_items:
    print(f"\nTesting: {item_name}")
    print("-" * 60)

    item = game_state._create_item_from_name(item_name)

    if item:
        print(f"✓ Conversion successful!")
        print(f"  Created: {item.name}")
        print(f"  Type: {type(item).__name__}")

        if hasattr(item, 'magic_bonus'):
            print(f"  Magic Bonus: +{item.magic_bonus}")
        if hasattr(item, 'damage_sm'):
            print(f"  Damage: {item.damage_sm}/{item.damage_l}")
        if hasattr(item, 'ac'):
            print(f"  AC: {item.ac}")

        # Simulate drop - what name goes back to room?
        dropped_name = item.name
        print(f"\n  If dropped, room gets: '{dropped_name}'")

        # Can we take it again?
        item2 = game_state._create_item_from_name(dropped_name)
        if item2 and hasattr(item2, 'magic_bonus'):
            print(f"  ✓ Taking '{dropped_name}' works! (+{item2.magic_bonus})")
        elif item2:
            print(f"  ✓ Taking '{dropped_name}' works! (Item created)")
        else:
            print(f"  ✗ ERROR: Can't take '{dropped_name}' again!")
    else:
        print(f"✗ FAILED: Could not create item from '{item_name}'")

print("\n" + "=" * 60)
