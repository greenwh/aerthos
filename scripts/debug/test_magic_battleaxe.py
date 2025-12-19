#!/usr/bin/env python3
"""Test that battleaxe_plus2 actually works"""

from aerthos.engine.game_state import GameData, GameState
from aerthos.entities.player import PlayerCharacter
from aerthos.world.dungeon import Dungeon, Room

# Load game data
game_data = GameData.load_all()

# Create minimal game state
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

print("Testing: battleaxe_plus2")
print("=" * 60)

item = game_state._create_item_from_name("battleaxe_plus2")

if item:
    print(f"✓ Item created successfully!")
    print(f"  Name: {item.name}")
    print(f"  Type: {type(item).__name__}")

    if hasattr(item, 'damage_sm'):
        print(f"  Damage (SM): {item.damage_sm}")
        print(f"  Damage (L): {item.damage_l}")
        print(f"  Magic Bonus: {item.magic_bonus}")
        print(f"  Weight: {item.weight}")
        print(f"  Can equip: YES")
        print(f"\n✓ This is a FUNCTIONAL weapon with +2 magic bonus!")
    else:
        print(f"  Type: {item.item_type}")
        print(f"  Weight: {item.weight}")
        print(f"\n✗ WARNING: This is just a treasure item, not a functional weapon!")
else:
    print("✗ FAILED: Item was not created at all!")

print("=" * 60)
