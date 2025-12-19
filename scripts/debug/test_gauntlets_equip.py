#!/usr/bin/env python3
"""Test that Gauntlets of Ogre Power can be equipped"""

from aerthos.engine.game_state import GameData, GameState
from aerthos.entities.player import PlayerCharacter
from aerthos.world.dungeon import Dungeon, Room
from aerthos.engine.parser import Command

# Setup
game_data = GameData.load_all()

test_char = PlayerCharacter(
    name="Test",
    race="Human",
    char_class="Fighter",
    strength=12, dexterity=14, constitution=13,  # Normal strength
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

print("Testing Gauntlets of Ogre Power")
print("=" * 70)

# Create gauntlets
print("\n1. Creating Gauntlets of Ogre Power...")
gauntlets = game_state._create_item_from_name("gauntlets_ogre_power")

if gauntlets:
    print(f"   ✓ Created: {gauntlets.name}")
    print(f"   Type: {gauntlets.item_type}")
    print(f"   Weight: {gauntlets.weight}")
else:
    print("   ✗ FAILED to create gauntlets")
    exit(1)

# Add to inventory
print("\n2. Adding to inventory...")
game_state.player.inventory.add_item(gauntlets)
print(f"   ✓ Added to inventory")
print(f"   Current STR: {game_state.player.strength}")

# Try to equip
print("\n3. Equipping gauntlets...")
result = game_state._handle_equip(Command(action='equip', target='gauntlets'))

if result['success']:
    print(f"   ✓ {result['message']}")
    print(f"   New STR: {game_state.player.strength}")
    print(f"   STR %ile: {game_state.player.strength_percentile}")

    if game_state.player.strength == 18 and game_state.player.strength_percentile == 100:
        print(f"   ✓ Gauntlets effect applied! (18/00)")
    else:
        print(f"   ✗ Gauntlets effect NOT applied properly")
        exit(1)

    # Check if equipped
    if game_state.player.equipment.gauntlets:
        print(f"   ✓ Gauntlets in equipment slot: {game_state.player.equipment.gauntlets.name}")
    else:
        print(f"   ✗ Gauntlets NOT in equipment slot")
        exit(1)
else:
    print(f"   ✗ FAILED: {result['message']}")
    exit(1)

# Try to unequip
print("\n4. Unequipping gauntlets...")
result = game_state._handle_unequip(Command(action='unequip', target='gauntlets'))

if result['success']:
    print(f"   ✓ {result['message']}")

    # Check if unequipped
    if not game_state.player.equipment.gauntlets:
        print(f"   ✓ Gauntlets removed from equipment slot")
    else:
        print(f"   ✗ Gauntlets still in equipment slot")
        exit(1)
else:
    print(f"   ✗ FAILED: {result['message']}")
    exit(1)

print("\n" + "=" * 70)
print("✓ SUCCESS: Gauntlets of Ogre Power work correctly!")
print("\nFeatures verified:")
print("  • Gauntlets can be created from treasure name")
print("  • Gauntlets can be equipped")
print("  • Equipping sets STR to 18/00")
print("  • Gauntlets can be unequipped")
print("  • Equipment slot management works")
