# Claude Code Bug Trace Guide

## Purpose

This document provides specific instructions for Claude Code to trace and fix the critical bugs affecting Aerthos gameplay. These bugs have persisted across multiple fix attempts because previous fixes addressed symptoms rather than root causes.

**CRITICAL INSTRUCTION**: Do NOT create workaround scripts. Trace each bug to its root cause and fix the actual code. Verify fixes with tests.

---

## Bug #1: Treasure Conversion Failure (HIGHEST PRIORITY)

### Symptom
Items picked up from dungeons remain as "Treasure" type instead of converting to Weapon/Armor/etc. Example: "Longsword +1" shows as item_type="Treasure" in inventory instead of item_type="Weapon".

### Trace Path
Follow this exact flow through the code:

```
1. Dungeon Generation (where treasure is placed)
   → generator/dungeon_generator.py
   → systems/treasure.py - how are treasure items created?
   → What class/dict structure is used?

2. Room Contents (how treasure is stored in rooms)
   → world/room.py - room.items or room.treasure?
   → What format are items stored in?

3. Pickup Action (when player takes item)
   → engine/game_state.py - handle_take() or similar
   → Is there a conversion step here?
   → Does it call treasure.convert_to_item() or similar?

4. Inventory Storage (how item enters inventory)
   → entities/player.py - add_to_inventory()
   → What type checking happens?
   → Is item_type being set/preserved?

5. Serialization (when game saves)
   → storage/character_roster.py - _serialize_item()
   → Is item_type being saved?

6. Deserialization (when game loads)
   → storage/character_roster.py - _deserialize_item()
   → Is the correct class being instantiated?
```

### Questions to Answer
1. Where does Treasure class get instantiated vs Weapon/Armor classes?
2. Is there a convert() method that should be called but isn't?
3. Are magic items (like longsword_plus_1) handled differently than mundane items?
4. Is the issue in generation, pickup, or serialization?

### Verification Test
After fixing, this must work:
```python
def test_treasure_converts_to_weapon_on_pickup():
    # Setup: Create room with treasure that should be a weapon
    # Action: Player picks up item
    # Assert: item.item_type == 'Weapon' (not 'Treasure')
    # Assert: item has damage_sm, damage_lg attributes
    # Action: Save game
    # Action: Load game
    # Assert: item still has correct type and attributes
```

---

## Bug #2: Save/Load KeyError (damage_sm)

### Symptom
```
KeyError: 'damage_sm'
File "character_roster.py", line 530, in _deserialize_item
    damage_sm=item_data['damage_sm'],
```

### Trace Path
```
1. Item Serialization
   → storage/character_roster.py - _serialize_item()
   → What fields are being saved for weapons?
   → Is damage_sm always included?

2. Item Deserialization  
   → storage/character_roster.py - _deserialize_item() (line 530)
   → Is it assuming all weapons have damage_sm?
   → What about items that were "Treasure" but should be weapons?

3. Weapon Class Definition
   → entities/ - find Weapon class
   → What fields are required vs optional?
   → What's the constructor signature?

4. Magic Item Handling
   → entities/magic_items.py
   → Do magic weapons have different attributes?
```

### Root Cause Hypothesis
The Treasure→Weapon conversion (Bug #1) is creating items that lack weapon-specific fields like damage_sm. When these malformed items are saved and loaded, deserialization fails.

### Fix Approach
Either:
A. Fix Bug #1 so conversion creates complete weapon objects, OR
B. Add defensive defaults in _deserialize_item():
```python
damage_sm = item_data.get('damage_sm', '1d4')  # default if missing
```

### Verification Test
```python
def test_save_load_with_converted_treasure():
    # Create character with converted treasure item
    # Save character
    # Load character - should not raise KeyError
    # Verify item attributes intact
```

---

## Bug #3: Shop Sell Error ('Weapon' has no attribute 'get')

### Symptom
```
AttributeError: 'Weapon' object has no attribute 'get'
File "hub_interfaces.py", line 160, in sell_item
    base_value = item.get('cost_gp', item.get('cost', 0))
```

### Trace Path
```
1. Shop Sell Handler
   → campaign/hub_interfaces.py - sell_item() (line 160)
   → Code assumes item is a dict, but it's a Weapon object

2. Item Representation
   → How are items stored in character inventory?
   → Are they objects or dicts?
   → Is this inconsistent across the codebase?
```

### Fix
```python
# WRONG (current code)
base_value = item.get('cost_gp', item.get('cost', 0))

# RIGHT (handle both object and dict)
if hasattr(item, 'cost_gp'):
    base_value = item.cost_gp
elif hasattr(item, 'cost'):
    base_value = item.cost
elif isinstance(item, dict):
    base_value = item.get('cost_gp', item.get('cost', 0))
else:
    base_value = 0
```

### Verification Test
```python
def test_sell_weapon_object():
    # Create Weapon object (not dict)
    # Call sell_item()
    # Should not raise AttributeError
    # Should return correct gold value
```

---

## Bug #4: Episode Completion Not Triggering

### Symptom
Boss defeated but episode not marked complete. Session file shows all rooms explored but campaign didn't advance.

### Trace Path
```
1. Episode Definition
   → data/campaigns/episodes/episode_X.json
   → What is the completion_trigger field?
   → Is it "boss_defeated", "all_rooms_explored", or something else?

2. Completion Check
   → campaign/episode_runner.py - check_completion() or similar
   → What conditions are checked?
   → Is boss death being detected?

3. Boss Death Detection
   → engine/combat.py - when combat ends
   → Is there a flag set when boss dies?
   → How is "boss" identified vs regular monster?

4. Multi-Level Handling
   → Does completion require all levels explored?
   → Episode 2 had 3 levels but boss on level 1 - is this correct?
```

### Questions to Answer
1. What defines a "boss" in the episode data?
2. Is boss death being communicated to episode runner?
3. Is multi-level completion logic correct?

### Verification Test
```python
def test_episode_completes_on_boss_defeat():
    # Load episode with boss
    # Simulate boss death
    # Check episode.is_complete == True
    # Check campaign advances to next episode
```

---

## Bug #5: Dead Character State

### Symptom
Character reaches 0 HP but isn't marked as dead. Can still be "healed" at temple (shows as "Still Alive").

### Trace Path
```
1. Damage Application
   → entities/player.py or entities/character.py
   → take_damage() method
   → Is is_alive set to False when HP <= 0?

2. HP Property
   → Is there an HP setter that checks for death?
   → Or is death check only in take_damage()?

3. Death State
   → How is is_alive stored/checked?
   → Is it a property or an attribute?
   → Could HP be set directly without triggering death check?
```

### Likely Root Cause
HP is being set to 0 without going through take_damage(), so is_alive never gets set to False.

### Fix Approach
```python
@property
def hp(self):
    return self._hp

@hp.setter
def hp(self, value):
    self._hp = max(0, value)
    if self._hp <= 0:
        self.is_alive = False
```

---

## Bug #6: THAC0 Not Updating on Level

### Symptom
Character levels up but THAC0 doesn't change to match new level.

### Trace Path
```
1. Level Up Handler
   → entities/player.py - level_up() or gain_level()
   → Is THAC0 recalculated?

2. THAC0 Calculation
   → Where is THAC0 stored/calculated?
   → Is it a property that calculates from level, or a stored value?
   → If stored, is it updated on level up?

3. Class Data
   → data/classes.json
   → Is THAC0 progression defined per class?
```

### Fix Approach
Either:
A. Make THAC0 a calculated property based on class and level, OR
B. Ensure level_up() explicitly recalculates and updates THAC0

---

## Testing Strategy After Fixes

### Run Existing Tests
```bash
python3 run_tests.py --no-web
```
All 593 tests must still pass.

### Add New Integration Test
Create `tests/test_gameplay_integration.py`:

```python
"""
Integration tests that simulate actual gameplay scenarios.
These test the full flow, not individual components.
"""

class TestTreasureFlow(unittest.TestCase):
    def test_treasure_pickup_to_save_load(self):
        """Full cycle: generate → pickup → equip → save → load"""
        pass

class TestCombatFlow(unittest.TestCase):
    def test_combat_death_state(self):
        """Verify death at 0 HP"""
        pass
    
    def test_level_up_updates_thaco(self):
        """Verify THAC0 changes on level"""
        pass

class TestEpisodeFlow(unittest.TestCase):
    def test_boss_defeat_completes_episode(self):
        """Verify episode completion trigger"""
        pass

class TestShopFlow(unittest.TestCase):
    def test_sell_item_object(self):
        """Verify selling works with item objects"""
        pass
```

---

## Fix Order

1. **Bug #1 (Treasure Conversion)** - Root cause of #2
2. **Bug #2 (Save/Load)** - May be fixed by #1, add defensive code anyway
3. **Bug #3 (Shop Sell)** - Quick fix, isolated code
4. **Bug #4 (Episode Completion)** - Needs investigation
5. **Bug #5 (Death State)** - Quick fix if HP setter approach
6. **Bug #6 (THAC0)** - Quick fix once location found

---

## Success Criteria

Before declaring bugs fixed:
1. All 593 existing tests pass
2. New integration tests pass
3. Manual playtest: Start Episode 3, pick up treasure, level up, defeat enemies, save/load, return to hub, sell items
4. No workaround scripts needed

---

## Do NOT Do

- Create workaround scripts that fix save files
- Add bandaid fixes without understanding root cause
- Fix only one code path when multiple paths have same bug
- Skip the verification tests
- Assume fix works without testing save/load cycle
