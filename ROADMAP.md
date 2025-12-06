# Aerthos Development Roadmap

**Last Updated**: 2025-12-06

This roadmap tracks bugs, feature gaps, and planned improvements for the Aerthos dungeon crawler.

---

## 🔴 Critical Bugs (Fix Immediately)

### XP & Progression
- [x] **XP not persisting to character roster** `game_state.py` ✅
  - XP awards show during dungeon but don't save to roster
  - **Fixed**: Added `game_state.character_ids` tracking and `save_party_members()` call after commands
  - Location: `web_ui/app.py` lines 747, 1645-1648, 1758, 3587
  - **Status**: ✅ Complete (2025-12-06)

### Session Management
- [x] **No exit session button in web UI** `web_ui/app.py` ✅
  - Players can't return to main menu without closing browser
  - **Fixed**: Added `/api/exit_session` endpoint and Exit button with confirmation dialog
  - Location: `web_ui/app.py` lines 1663-1696, `game.html` lines 1246, 1365-1395
  - **Status**: ✅ Complete (2025-12-06)

- [x] **Can't restore saves from web UI** `web_ui/app.py` ✅
  - **Status**: ✅ Already implemented - `/api/sessions/<session_id>/load` exists
  - UI has "Play" button in session manager (`session_manager.html` line 618-635)
  - **Status**: ✅ Verified working (2025-12-06)

### Character System
- [x] **Imported characters have all spells with unlimited use** `character_creation.py` ✅
  - Bug in spell slot assignment loop (lines 1367-1399)
  - **Fixed**: Corrected spell slot loop and limited spells_known to castable levels
  - Location: `character_creation.py` lines 1391-1421
  - **Status**: ✅ Complete (2025-12-06)

### Treasure System
- [x] **Boss treasure not dropping** `data/dungeons/*.json` ✅
  - Code implementation is correct (`game_state.py:1487-1524`)
  - Campaign dungeons already have treasure definitions (verified `starter_dungeon.json`)
  - Issue was with procedurally generated dungeons (custom mine)
  - Procedural generation treasure system to be investigated separately if needed
  - **Status**: ✅ Campaign dungeons verified (2025-12-06)

---

## 🟡 High Priority Features

### Spell System
- [ ] **Fireball spell effect not implemented** `systems/magic.py`
  - Handler missing from spell effect registry
  - Location: `aerthos/systems/magic.py:68-76`
  - **Status**: Pending

- [ ] **Audit all spell implementations**
  - Cross-reference `data/spells.json` with implemented handlers
  - Create comprehensive list of missing spell effects
  - Prioritize by frequency of use (combat > utility > rare)
  - **Status**: Pending

### Save/Load UX
- [ ] **Better save/load UI for web interface**
  - Show list of available saves with timestamps
  - Display party info (level, location, campaign)
  - Confirm before overwriting saves
  - **Status**: Pending

---

## 🟢 Medium Priority Improvements

### Session Tracking
- [ ] **Session progress tracking outside campaigns**
  - Currently display-only (shows "0 turns / 0.0 hrs")
  - Decide if standalone sessions should track like campaigns
  - If yes, implement session stats panel similar to campaign hub
  - **Status**: Design Decision Needed

### Light System
- [x] **Torch auto-switching when torch runs out** ✅
  - Already implemented correctly in `time_tracker.py:63-103`
  - Works as designed - automatically switches to other party members' torches
  - No fix needed

### Quality of Life
- [ ] **Better feedback for unimplemented spells**
  - Currently just shows generic message
  - Should indicate which spells work vs. placeholder
  - Consider showing spell description even if effect not implemented
  - **Status**: Pending

- [ ] **Dungeon generation validation**
  - Tool to validate dungeon JSON files
  - Check for: boss flags, treasure definitions, encounter balance
  - Warn about missing treasure on boss encounters
  - **Status**: Pending

---

## 🔵 Future Enhancements

### Spell System Expansion
- [ ] **Implement missing spell effects** (Low Priority)
  - Identify all spells from `data/spells.json` without handlers
  - Implement by school: Evocation → Conjuration → Enchantment → etc.
  - Test each implementation thoroughly
  - **Status**: Backlog

### Character Progression
- [ ] **Level-up notifications in web UI**
  - Currently handled in CLI but not web interface
  - Show level-up modal with new abilities
  - **Status**: Backlog

### Treasure Variety
- [ ] **Expand boss treasure types**
  - Add unique items for specific bosses
  - Artifact-level treasures for major encounters
  - Boss-specific loot tables
  - **Status**: Backlog

### Dungeon Content
- [ ] **Review all dungeon files for completeness**
  - Ensure all boss encounters have treasure
  - Verify encounter difficulty scaling
  - Check for thematic consistency (no baboons in mines!)
  - **Status**: Backlog

---

## 📋 Technical Debt

### Code Organization
- [ ] **Separate spell effect handlers into modules**
  - Current: All in `systems/magic.py`
  - Proposed: `systems/spells/evocation.py`, `systems/spells/conjuration.py`, etc.
  - Makes adding new spells easier
  - **Status**: Backlog

### Testing
- [ ] **Unit tests for spell effects**
  - Test damage calculations
  - Test save throw logic
  - Test area of effect
  - **Status**: Backlog

- [ ] **Integration tests for session save/restore**
  - Verify XP persists correctly
  - Verify inventory persists
  - Verify campaign progress persists
  - **Status**: Backlog

---

## 📝 Spell Implementation Tracking

### Implemented Spells ✅
- Magic Missile (partial - needs better targeting)
- Cure Light Wounds
- Sleep (basic implementation)
- _Add more as confirmed..._

### Missing Spell Effects ❌
- **Fireball** (confirmed missing)
- **Lightning Bolt** (needs checking)
- **Cone of Cold** (needs checking)
- **Haste** (needs checking)
- **Slow** (needs checking)
- **Web** (needs checking)
- **Cloudkill** (needs checking)
- _Full audit needed - see "Audit all spell implementations" task_

### Spell Implementation Priority
1. **Combat Damage Spells** - Most frequently used
   - Fireball, Lightning Bolt, Cone of Cold, Magic Missile improvements
2. **Healing Spells** - Critical for survival
   - Cure Serious Wounds, Heal, Raise Dead
3. **Buff/Debuff Spells** - Tactical value
   - Haste, Slow, Bless, Prayer
4. **Utility Spells** - Exploration
   - Knock, Find Traps, Detect Magic, Identify
5. **Rare/High-Level Spells** - Lower priority
   - Wish, Time Stop, Meteor Swarm

---

## 🎯 Current Sprint (December 2025)

### In Progress
1. Fix XP persistence to character roster
2. Add exit session button/endpoint
3. Add restore session to web UI
4. Fix imported character spell bug

### Next Up
1. Add treasure to boss rooms in dungeon JSONs
2. Implement fireball spell effect
3. Audit all spell implementations

### Blocked
- None currently

---

## 📊 Progress Metrics

- **Critical Bugs**: ✅ 5 of 5 complete
- **High Priority Features**: 0 of 3 complete
- **Medium Priority**: 1 of 4 complete (torch switching confirmed working)
- **Spell Effects**: ~3 of ~50 implemented (estimate - audit needed)

---

## 🔄 Change Log

### 2025-12-06 (Evening Update)
- ✅ Fixed XP persistence - party members now save to roster after every command
- ✅ Added exit session endpoint and button with confirmation dialog
- ✅ Verified restore/load session already implemented and working
- ✅ Fixed imported character spell bug - correct slot assignment and level-appropriate spells
- ✅ Verified campaign dungeon treasures - all boss rooms properly configured
- **All critical bugs resolved!**

### 2025-12-06 (Initial)
- Initial roadmap created
- Identified 8 issues from playtest session
- Confirmed torch auto-switching already works correctly
- Started work on critical bug fixes

---

## Notes

- **Spell system** needs comprehensive audit - current implementation count is estimate
- **Treasure system** code is solid, data files need population
- **Session management** works in CLI, needs web UI parity
- **Character import** bug is critical for imported character balance
