# Pre-Episode Testing Protocol for Aerthos

## Purpose

This document provides a systematic approach to verify game functionality **before** playing an episode. The goal is to catch the recurring bug patterns that have disrupted gameplay in Episodes 1-2 before they occur in Episode 3+.

---

## Known Bug Categories (from bugs.md and development history)

### Critical (Game-Breaking)
1. **Save/Load Failures** - KeyError on item deserialization (missing `damage_sm`)
2. **Treasure Conversion** - Items stay as "Treasure" type instead of converting to Weapon/Armor
3. **Episode Completion** - Boss defeat doesn't trigger episode completion

### Major (Gameplay-Disrupting)
4. **Shop Sell Errors** - 'Weapon'/'Armor' object has no attribute 'get'
5. **Dead Character State** - Characters at 0 HP not marked as dead
6. **THAC0 Updates** - Inconsistent on leveling

### Minor (Annoying but Playable)
7. **Special Attacks** - Monster abilities (disease, poison, etc.) have no effect
8. **Spell Slots** - May not restore properly after rest

---

## Phase 1: Pre-Session Integrity Check (5 minutes)

Run these checks BEFORE loading your campaign:

### 1.1 Test Suite Baseline
```bash
cd /mnt/d/Development/aerthos
python3 run_tests.py --no-web
```
**Expected:** All 593 tests pass. If failures, investigate before playing.

### 1.2 Campaign File Validation
```bash
# Check campaign save exists and is valid JSON
python3 -c "
import json
from pathlib import Path
campaign_file = Path('path/to/your/campaign.json')  # Update path
data = json.load(open(campaign_file))
print('Campaign ID:', data.get('id'))
print('Current Episode:', data.get('current_episode'))
print('Party ID:', data.get('party_id'))
print('Characters:', len(data.get('characters', [])))
"
```

### 1.3 Character Integrity Check
```bash
python3 -c "
import json
from pathlib import Path
# Check each character in roster
roster_dir = Path('~/.aerthos/roster').expanduser()
for char_file in roster_dir.glob('*.json'):
    data = json.load(open(char_file))
    # Check for common serialization issues
    inv = data.get('inventory', [])
    for item in inv:
        if isinstance(item, dict):
            if item.get('type') == 'weapon' and 'damage_sm' not in item:
                print(f'WARNING: {char_file.name} has weapon missing damage_sm')
            if item.get('item_type') == 'Treasure':
                print(f'WARNING: {char_file.name} has unconverted treasure: {item.get(\"name\")}')
"
```

---

## Phase 2: Quick Functional Smoke Test (10 minutes)

Load a **test session** (not your real campaign) and verify core systems:

### 2.1 Character Creation → Leveling → Save/Load Cycle
```
1. Start new game with temp character
2. Note THAC0 value
3. Use debug/cheat to add XP for level-up
4. Verify THAC0 updated correctly
5. Save game
6. Load game
7. Verify THAC0 still correct after load
```

### 2.2 Item Pickup → Inventory → Equip Cycle
```
1. Enter dungeon with treasure room
2. Pick up weapon item
3. Check inventory - verify type is "Weapon" not "Treasure"
4. Equip item
5. Check character sheet
6. Save game
7. Load game
8. Verify item still equipped and correct type
```

### 2.3 Combat → Death → Temple Cycle
```
1. Enter combat
2. Let character take damage to exactly 0 HP
3. Verify character marked as dead
4. Return to hub
5. Visit temple
6. Attempt to raise dead character
7. Verify resurrection works correctly
```

### 2.4 Shop Buy/Sell Cycle
```
1. Go to shop
2. Buy an item
3. Verify item in inventory
4. Try to sell the item
5. Verify no "object has no attribute 'get'" error
```

### 2.5 Spell Memorize → Cast → Rest Cycle (for spellcasters)
```
1. Memorize spells
2. Cast a spell
3. Verify slot marked as used
4. Rest for 8 hours
5. Verify spell slot restored
```

---

## Phase 3: Episode-Specific Pre-Flight (15 minutes)

Before starting Episode 3, verify the specific systems that episode will use:

### 3.1 Check Episode Definition
```bash
# Verify episode 3 dungeon exists and is valid
python3 -c "
import json
episode_file = 'path/to/episodes/episode_3.json'  # Update path
data = json.load(open(episode_file))
print('Episode:', data.get('title'))
print('Dungeon levels:', data.get('levels', 1))
print('Boss:', data.get('boss', 'None defined'))
print('Completion trigger:', data.get('completion_trigger', 'Unknown'))
"
```

### 3.2 Check Dungeon Structure
```bash
# Verify dungeon has proper level transitions if multi-level
python3 -c "
from aerthos.campaign.episode_runner import EpisodeRunner
# Load episode and check structure
# Look for:
# - Stairs up/down connections
# - Boss room placement
# - Completion trigger location
"
```

### 3.3 Verify Party State
```
1. Load campaign
2. Check each character:
   - HP > 0 (alive)
   - Correct THAC0 for level
   - Spell slots properly memorized
   - Equipment correctly equipped
   - No "Treasure" items in inventory
3. Check party gold total
4. Check for any quest items needed for episode
```

---

## Phase 4: Defensive Play Strategies

During Episode 3, use these practices to catch issues early:

### 4.1 Save Frequently
- Save after each major combat
- Save before and after leveling
- Save before boss encounters
- Use descriptive save names: "ep3_level2_preboss"

### 4.2 Verify After Key Events
After each of these events, pause and verify:

| Event | Check |
|-------|-------|
| Level up | THAC0 updated, spell slots added |
| Pick up treasure | Item type is correct (not "Treasure") |
| Character death | Marked as dead, can't act |
| Boss defeat | Episode completion triggered |
| Return to hub | XP/gold persisted |

### 4.3 Keep Console Visible
Run the web UI with console visible to catch errors:
```bash
python3 web_ui/app.py 2>&1 | tee gameplay_log.txt
```

### 4.4 Bug Documentation Template
When something goes wrong, capture:
```
## Bug Report
- Episode: 3
- Location: Level 2, Room 5
- Action: Picked up "Longsword +1"
- Expected: Weapon in inventory
- Actual: "Treasure" in inventory with weapon name
- Console output: [paste error if any]
- Save file: ep3_before_bug.json
```

---

## Phase 5: Targeted Code Inspection

For the specific bugs you've documented, here are the code locations to examine:

### 5.1 Treasure Conversion Bug
```
Files to check:
- aerthos/systems/treasure.py - convert_treasure_to_item()
- aerthos/engine/game_state.py - handle_take() or handle_pickup()
- aerthos/entities/magic_items.py - item creation

Look for:
- Is item.item_type being set correctly?
- Is the treasure.convert() being called?
- Is the converted item replacing the treasure object?
```

### 5.2 Save/Load KeyError Bug
```
Files to check:
- aerthos/storage/character_roster.py:530 - _deserialize_item()

Look for:
- What fields are required vs optional?
- Are defaults provided for missing fields?
- Is there version migration for old saves?
```

### 5.3 Episode Completion Bug
```
Files to check:
- aerthos/campaign/episode_runner.py - check_completion()
- Episode JSON definition - completion_trigger field

Look for:
- What defines "episode complete"?
- Is boss death being tracked?
- Are all rooms marked explored being checked?
- Is there a multi-level completion check?
```

### 5.4 Shop Sell Bug
```
Files to check:
- aerthos/campaign/hub_interfaces.py:160 - sell_item()

Look for:
- item.get('cost_gp') assumes dict, but item is object
- Need item.cost_gp attribute access instead
```

### 5.5 Death State Bug
```
Files to check:
- aerthos/engine/combat.py - damage handling
- aerthos/entities/player.py - take_damage(), is_alive property

Look for:
- Is is_alive set to False when HP <= 0?
- Is the check HP == 0 or HP <= 0?
```

---

## Recommended Workflow for Episode 3

### Before Play
1. Run Phase 1 checks (5 min)
2. Run Phase 2 smoke tests (10 min)
3. Run Phase 3 episode-specific checks (15 min)
4. Total: 30 minutes of verification

### During Play
1. Keep console visible
2. Save after every major event
3. Verify after key events (see 4.2)
4. Document any issues immediately

### After Play
1. Verify campaign save is valid
2. Check character XP/gold persisted
3. Note any bugs for fixing before Episode 4

---

## Code Fix Priority

Based on your bug list, fix these in order:

### Priority 1 (Fix Before Episode 3)
1. **Save/Load KeyError** - Game-breaking, prevents saving
2. **Treasure Conversion** - Ruins loot, core gameplay

### Priority 2 (Fix During Episode 3 if Encountered)
3. **Shop Sell Error** - Can work around by not selling
4. **Episode Completion** - Can manually advance if needed

### Priority 3 (Fix After Campaign)
5. **Special Attacks** - Doesn't break gameplay
6. **THAC0 Updates** - Can manually verify
7. **Death State** - Can work around with careful play

---

## Quick Reference: Test Commands

```bash
# Full test suite
python3 run_tests.py --no-web

# Just storage tests (save/load)
python3 -m unittest tests.test_storage -v

# Just combat tests
python3 -m unittest tests.test_combat -v

# Campaign tests
python3 -m unittest tests.test_campaign_playthrough -v

# Quest completion tests
python3 -m unittest tests.test_quest_manager -v
```

---

*Document created to address systematic bug prevention for Aerthos campaign play*
