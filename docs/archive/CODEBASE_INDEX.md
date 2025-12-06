# Aerthos Codebase - Complete Index & Navigation Guide

## Documents in This Exploration

This exploration produced 3 comprehensive documents:

### 1. **TECHNICAL_BREAKDOWN.md** (1,402 lines)
   - **Purpose:** Complete architectural documentation
   - **Audience:** Developers who need to understand every system
   - **Contents:**
     - Core architecture and design philosophy (Section 1)
     - Complete module structure (25+ systems) (Section 2)
     - Data flow diagrams (Section 3)
     - Deep dive into each key system (Section 4)
     - Data structures and schemas (Section 5)
     - Testing infrastructure (Section 6)
     - Campaign system analysis (Section 7)
     - Statistics and metrics (Section 10)
     - Design patterns and principles (Section 11)
     - Configuration management (Section 12)
   - **Use Case:** "I need to understand how X works" or "I want to modify the core engine"

### 2. **EXPLORATION_SUMMARY.md** (664 lines)
   - **Purpose:** Executive summary and quick reference
   - **Audience:** Decision makers, project leads, new developers
   - **Contents:**
     - Quick facts and overview
     - Architecture diagram
     - What's solid vs. what was attempted
     - Directory structure overview
     - Key systems summary
     - Strengths vs. limitations
     - Recommended next steps
     - Campaign system details
     - Development workflow
   - **Use Case:** "Give me the 10,000-foot view" or "What should we work on next?"

### 3. **CODEBASE_INDEX.md** (this file)
   - **Purpose:** Navigation guide for the codebase
   - **Audience:** All developers
   - **Contents:**
     - File-by-file navigation
     - Quick lookup tables
     - Common development tasks
   - **Use Case:** "Where is X?" or "How do I..."

---

## Directory Navigation

### Root Level (`/mnt/d/Development/aerthos/`)

| File/Dir | Purpose | Lines | Status |
|----------|---------|-------|--------|
| `main.py` | CLI game entry point | 1,519 | ✅ Complete |
| `web_ui/app.py` | Flask web server | 1,938 | ✅ Complete |
| `aerthos/` | Game engine package | ~15,000 | ✅ Complete |
| `tests/` | Test suite | ~3,500 | ✅ 417 passing |
| `docs/` | Documentation | 100+ KB | ✅ Comprehensive |
| `CLAUDE.md` | Development guide | 1,371 | ✅ Current |
| `TECHNICAL_BREAKDOWN.md` | This exploration | 1,402 | ✅ New |
| `EXPLORATION_SUMMARY.md` | Quick reference | 664 | ✅ New |

### Engine (`aerthos/engine/`)

Core game logic and command processing:

| File | Lines | Purpose | Key Classes |
|------|-------|---------|-------------|
| `game_state.py` | 600+ | Central coordinator | GameState, GameData |
| `combat.py` | 300+ | THAC0 combat system | CombatResolver, DiceRoller |
| `parser.py` | 250+ | Command parsing | CommandParser, Command |
| `time_tracker.py` | 200+ | Time/resource management | TimeTracker, RestSystem |
| `__init__.py` | — | Package marker | — |

**Role:** Central engine that coordinates all game systems

**Key Data Flows:**
- User input → Parser → GameState → Handlers → Display
- Combat: attack_roll() → apply damage → monster AI response
- Spell casting: cast_spell() → effect handler → apply results
- Rest: restores HP, spells, consumes rations

### Entities (`aerthos/entities/`)

Game objects: characters, monsters, parties, equipment:

| File | Lines | Purpose | Key Classes |
|------|-------|---------|-------------|
| `character.py` | 150+ | Base entity | Character (base class) |
| `player.py` | 300+ | Player characters | PlayerCharacter, Item, Weapon, Armor, Shield, Inventory, Spell |
| `monster.py` | 200+ | Creatures with AI | Monster (extends Character) |
| `party.py` | 150+ | Multi-character parties | Party (4-6 members) |
| `magic_items.py` | 100+ | Magic item factory | MagicItemFactory |
| `__init__.py` | — | Package marker | — |

**Inheritance Hierarchy:**
```
Character (base)
├── PlayerCharacter (+ inventory, spells, skills)
└── Monster (+ AI, hit dice, treasure type)

Party = List[PlayerCharacter]

Equipment Types:
├── Item (base)
├── Weapon
├── Armor
├── Shield
└── LightSource

Spell System:
├── Spell (definition)
└── SpellSlot (memorized instance)
```

### Systems (`aerthos/systems/`) - 25+ Subsystems

Game mechanics implementations:

| File | Lines | Purpose | Key Classes |
|------|-------|---------|-------------|
| `magic.py` | 500+ | Vancian spell system | MagicSystem (332 spells) |
| `skills.py` | 200+ | Thief percentile skills | SkillResolver (8 skills) |
| `saving_throws.py` | 150+ | 5-category saves | SavingThrowResolver |
| `ability_modifiers.py` | 200+ | Ability bonuses | AbilityModifierSystem |
| `combat.py` | 150+ | Additional combat | (see engine/combat.py for main) |
| `monster_ai.py` | 150+ | Monster targeting | MonsterTargetingAI |
| `monster_abilities.py` | 100+ | Special attacks | MonsterSpecialAbilities |
| `armor_system.py` | 150+ | AC calculations | ArmorSystem |
| `experience.py` | 100+ | XP system | ExperienceCalculator |
| `xp_calculator.py` | 150+ | Dynamic XP | XPCalculator |
| `movement.py` | 100+ | Encumbrance | MovementSystem |
| `narrator.py` | 200+ | Atmospheric text | DMNarrator |
| `encounters.py` | 100+ | Encounter generation | EncounterGenerator |
| `traps.py` | 100+ | Trap mechanics | TrapSystem |
| `treasure.py` | 100+ | Treasure generation | TreasureGenerator |
| `turning_undead.py` | 80+ | Cleric ability | TurningUndeadSystem |
| `alignment.py` | 100+ | 9-point alignment | AlignmentSystem |
| `weapon_proficiency.py` | 100+ | Weapon training | WeaponProficiency |
| `racial_abilities.py` | 100+ | Race bonuses | RacialAbilitySystem |
| `environment_filter.py` | 100+ | Monster filtering | EnvironmentMonsterFilter |
| `party_analyzer.py` | 150+ | Party composition | PartyAnalyzer |
| `class_abilities.py` | 100+ | Class features | ClassAbilitySystem |
| `ability_scores.py` | 100+ | Ability handling | AbilityScoreSystem |
| `magic_item_factory.py` | 150+ | Item creation | MagicItemFactory |
| `__init__.py` | — | Package marker | — |

**Core Loops:**
- Combat: CombatResolver.attack_roll() is the heart
- Magic: MagicSystem.cast_spell() → effect handlers
- Saves: SavingThrowResolver.make_save() used by spells/abilities
- Skills: SkillResolver.check_skill() for percentile rolls

### World (`aerthos/world/`)

Dungeon design, locations, navigation:

| File | Lines | Purpose | Key Classes |
|------|-------|---------|-------------|
| `dungeon.py` | 200+ | Single-level dungeons | Dungeon (navigation graph) |
| `multilevel_dungeon.py` | 300+ | Multi-level support | MultiLevelDungeon |
| `room.py` | 150+ | Individual rooms | Room (with exits, items) |
| `encounter.py` | 100+ | Combat/trap/puzzle | EncounterManager, CombatEncounter, TrapEncounter |
| `village.py` | 200+ | Settlements | Village, ShopItem, Inn, Guild |
| `shop.py` | 100+ | Shop mechanics | Shop (buy/sell) |
| `inn.py` | 80+ | Rest facilities | Inn (rest, healing) |
| `guild.py` | 100+ | Guild services | Guild (class-specific) |
| `automap.py` | 200+ | ASCII mapping | AutomapGenerator |
| `__init__.py` | — | Package marker | — |

**Navigation Model:**
```
Dungeon = Graph of Rooms
Room = {id, title, description, exits, items, encounters}
Exit = {direction: target_room_id}
MultiLevelDungeon = List[Dungeon] with stair connections
```

### Generator (`aerthos/generator/`)

Procedural content generation:

| File | Lines | Purpose | Key Classes |
|------|-------|---------|-------------|
| `dungeon_generator.py` | 400+ | Room generation | DungeonGenerator |
| `multilevel_generator.py` | 200+ | Multi-level dungeons | MultiLevelGenerator |
| `config.py` | 100+ | Difficulty presets | DungeonConfig, EASY/STANDARD/HARD |
| `monster_scaling.py` | 150+ | Monster difficulty | MonsterScalingSystem |
| `adventure_seeds.py` | 100+ | Scenario generation | AdventureSeedGenerator |
| `appendix_a_generator.py` | 100+ | Encounter generation | AppendixAGenerator |
| `__init__.py` | — | Package marker | — |

**Generation Pipeline:**
```
DungeonConfig → DungeonGenerator.generate()
├─ Generate room graph
├─ Create rooms
├─ Populate encounters
├─ Place treasures
└─ Designate safe rooms
→ Returns dungeon dict
→ Loaded as Dungeon object
```

### Storage (`aerthos/storage/`)

Persistence systems (5 layers):

| File | Lines | Purpose | Key Classes | Directory |
|------|-------|---------|-------------|-----------|
| `session_manager.py` | 200+ | Full game saves | SessionManager | `~/.aerthos/sessions/` |
| `character_roster.py` | 150+ | Character database | CharacterRoster | `~/.aerthos/characters/` |
| `party_manager.py` | 150+ | Party storage | PartyManager | `~/.aerthos/parties/` |
| `scenario_library.py` | 100+ | Saved dungeons | ScenarioLibrary | `~/.aerthos/scenarios/` |
| `__init__.py` | — | Package marker | — | — |

**Relationships:**
- SessionManager uses CharacterRoster + PartyManager + ScenarioLibrary
- All extend SaveSystem for serialization
- All handle JSON read/write to disk

### UI (`aerthos/ui/`)

User interface components:

| File | Lines | Purpose | Key Classes |
|------|-------|---------|-------------|
| `character_creation.py` | 200+ | Character builder | CharacterCreator, ManualCharacterCreator |
| `character_sheet.py` | 150+ | Character display | CharacterSheet |
| `display.py` | 150+ | Text formatting | Display (colors, boxes, headers) |
| `party_creation.py` | 100+ | Party builder | PartyCreator |
| `dungeon_interview.py` | 150+ | Dungeon config interview | DungeonInterview |
| `save_system.py` | 100+ | Save/load UI | SaveSystem |
| `__init__.py` | — | Package marker | — |

**Used By:**
- CLI (`main.py`): All UI components
- Web UI (`web_ui/app.py`): Some components, mostly replicated in HTML/JS

### Data Files (`aerthos/data/`)

Game content in JSON format:

| File | Size | Purpose | Format |
|------|------|---------|--------|
| `monsters.json` | 269 KB | 100+ creatures | `{monster_id: {name, hd, ac, damage, xp, ...}}` |
| `spells.json` | 158 KB | 332 spells | `{spell_name: {level, school, range, damage, ...}}` |
| `weapons.json` | 11 KB | Melee/ranged weapons | `{weapon_id: {name, damage_sm, damage_l, cost, ...}}` |
| `armor.json` | 7 KB | Armor pieces | `{armor_id: {name, ac, cost, restrictions, ...}}` |
| `equipment.json` | 13 KB | Miscellaneous items | `{item_id: {name, weight, cost, type, ...}}` |
| `classes.json` | 7 KB | Fighter, Cleric, etc. | `{class_name: {hd, thac0, abilities, ...}}` |
| `races.json` | 9 KB | Human, Elf, Dwarf, etc. | `{race_name: {modifiers, languages, ...}}` |
| `spells.json` | 158 KB | All spell definitions | `{spell_id: {level, components, effects, ...}}` |
| `ability_modifiers.json` | 10 KB | Ability modifier tables | `{ability: {score: modifier}}` |
| `saving_throw_tables.json` | 5 KB | Save values by class/level | `{class: {level: [saves]}}` |
| `thief_skills_tables.json` | 9 KB | Skill percentages | `{skill: {level: percentage}}` |
| `weapon_proficiencies.json` | 2 KB | Weapon groups | `{class: [proficient_weapons]}` |
| `treasure_tables.json` | 9 KB | Treasure generation | DMG treasure types |
| `magic_items.json` | 10 KB | Magic item data | `{item_id: {name, bonus, effect, ...}}` |
| `level_progression.json` | 10 KB | XP tables | `{class: [xp_by_level]}` |
| `class_abilities.json` | 10 KB | Class special abilities | Thief skills, turning, etc. |
| `ability_score_tables.json` | 24 KB | Comprehensive ability modifiers | Full PH tables |
| `dungeons/starter_dungeon.json` | 20 KB | 10-room hand-crafted dungeon | Room structure with encounters |
| `dmg_tables/` | — | Dungeon Masters Guide tables | Various reference data |

**Schema Pattern:**
```json
{
  "id_or_name": {
    "name": "Display Name",
    "description": "What it does",
    ...type-specific fields...
  }
}
```

---

## Test Files (`tests/`)

27 test files covering all major systems:

| File | Tests | Purpose | Covers |
|------|-------|---------|--------|
| `test_combat.py` | 40+ | THAC0 mechanics | attack rolls, damage, criticals |
| `test_magic_functionality.py` | 30+ | Spell system | memorization, casting, effects |
| `test_parser.py` | 25+ | Command parsing | verb recognition, targeting |
| `test_web_api.py` | 20+ | Flask endpoints | /api routes |
| `test_ability_modifiers.py` | 35+ | Ability bonuses | STR, DEX, CON, INT, WIS, CHA |
| `test_thief_skills.py` | 20+ | Percentile skills | All 8 thief skills |
| `test_saving_throws.py` | 25+ | Save mechanics | All 5 save categories |
| `test_monster_abilities_integration.py` | 15+ | Monster specials | Poison, breath, etc. |
| `test_armor_system.py` | 20+ | AC calculations | armor, dex, magic bonuses |
| `test_movement.py` | 15+ | Encumbrance | weight, speed penalties |
| `test_xp_calculation.py` | 15+ | XP system | difficulty vs party level |
| `test_formation_combat.py` | 25+ | Formation targeting | front/back line, AI selection |
| `test_multilevel_dungeons.py` | 20+ | Stair navigation | level transitions |
| `test_storage.py` | 20+ | Persistence | save/load all 5 layers |
| `test_village_system.py` | 15+ | Settlements | shops, inns, guilds |
| `test_narrator_integration.py` | 15+ | Text generation | DMNarrator |
| `test_game_state.py` | 30+ | Central coordinator | command execution |
| `test_party_aware_dungeons.py` | 20+ | Party scaling | difficulty adjustment |
| `test_spell_targeting.py` | 15+ | Spell targeting | area of effect, saves |
| `test_treasure_generation.py` | 15+ | Loot generation | treasure type tables |
| `test_ui_parity.py` | 10+ | CLI/Web sync | identical behavior |
| `test_phase3_integration.py` | 30+ | End-to-end | full game scenarios |
| `test_integration.py` | 40+ | Core integration | cross-system |
| `test_web_ui.py` | 20+ | Web interface | browser game |
| `test_money_system.py` | 10+ | Gold/coins | transactions |
| + 2 more test files | — | — | — |

**Total: 417 tests, 100% passing**

Run tests with:
```bash
python3 run_tests.py --no-web           # All tests
python3 run_tests.py --unit             # Unit only
python3 -m unittest tests.test_combat   # Specific file
```

---

## Entry Points

### For Players

1. **CLI Game** → Run `python main.py`
   - Text-based interface
   - Full-featured gameplay
   - No dependencies

2. **Web UI** → Run `python web_ui/app.py` then visit `http://localhost:5000`
   - Gold Box visual style
   - Browser-based
   - Requires Flask (`pip install flask`)

### For Developers

1. **Understanding Architecture** → Read `TECHNICAL_BREAKDOWN.md`
   - Complete system documentation
   - Data flow diagrams
   - Design patterns

2. **Quick Reference** → Read `EXPLORATION_SUMMARY.md`
   - 10,000-foot overview
   - What's solid vs. attempted
   - Recommended next steps

3. **Development Guide** → Read `CLAUDE.md`
   - Development rules (MANDATORY)
   - Testing workflow
   - How to add features

4. **Code Navigation** → Read `CODEBASE_INDEX.md` (this file)
   - Where each file is
   - What it does
   - How to find things

---

## Common Development Tasks

### "I want to understand how X works"

1. **Combat System** → `aerthos/engine/combat.py` + `aerthos/systems/combat.py`
   - Start at `CombatResolver.attack_roll()`
   - Read TECHNICAL_BREAKDOWN.md Section 4.1

2. **Spell Casting** → `aerthos/systems/magic.py`
   - Start at `MagicSystem.cast_spell()`
   - Find spell handler (e.g., `_spell_magic_missile()`)
   - Read TECHNICAL_BREAKDOWN.md Section 4.2

3. **Monster AI** → `aerthos/systems/monster_ai.py`
   - Read `MonsterTargetingAI.select_target()`
   - See `aerthos/constants.py` for targeting chances

4. **Game Flow** → `aerthos/engine/game_state.py`
   - Read `GameState.execute_command()`
   - Find `_handle_*` method for command
   - Read TECHNICAL_BREAKDOWN.md Section 3

### "I want to add X feature"

**Add New Spell:**
1. Edit `aerthos/data/spells.json` - add spell definition
2. Edit `aerthos/systems/magic.py` - add handler function
3. Edit test file - add test case
4. Run tests: `python3 run_tests.py --unit`

**Add New Monster:**
1. Edit `aerthos/data/monsters.json` - add monster data
2. Test by generating dungeon: `python main.py`
3. Can skip code changes - will load automatically

**Add New Equipment:**
1. Edit appropriate JSON file (weapons.json, armor.json, equipment.json)
2. Test character creation: `python main.py`
3. May need class restrictions in `aerthos/systems/armor_system.py`

**Add New Class:**
1. Edit `aerthos/data/classes.json`
2. Update character creation UI: `aerthos/ui/character_creation.py`
3. Update ability system: `aerthos/systems/ability_modifiers.py`
4. Update combat: May need THAC0 table in `aerthos/constants.py`
5. Run tests and test both CLI and Web UI

### "Why is X broken?"

**Test Failed:**
```bash
# Run specific test with verbose output
python3 -m unittest tests.test_file.TestClass.test_method -v

# Run all tests to see what broke
python3 run_tests.py --no-web --verbose
```

**Game Behaves Wrong:**
1. Check if it's defined in JSON data files first
2. Check ability modifiers in `aerthos/systems/ability_modifiers.py`
3. Check combat in `aerthos/engine/combat.py`
4. Check core logic in relevant system file
5. Add debug prints and test both UIs

**CLI Works but Web UI Doesn't:**
1. Check command execution is same in both
2. Check JSON serialization in `web_ui/app.py`
3. Check `get_game_state_json()` returns correct fields
4. Look for UI-specific issues in templates/static files

---

## Key Files to Know

### Must-Read for Developers

1. **CLAUDE.md** (1,371 lines)
   - Development rules (MANDATORY)
   - Architecture overview
   - How both UIs sync

2. **TECHNICAL_BREAKDOWN.md** (1,402 lines)
   - Complete system documentation
   - Every file explained
   - Data structures and schemas

3. **aerthos/engine/game_state.py** (600+ lines)
   - Central coordinator
   - All command handlers
   - Where to add new commands

4. **aerthos/systems/magic.py** (500+ lines)
   - Spell system and handlers
   - Example of system architecture

5. **aerthos/constants.py** (150+ lines)
   - All magic numbers in one place
   - Game balance tuning

### Core Architecture Files

- `aerthos/engine/game_state.py` - Central coordinator
- `aerthos/entities/character.py` - Base entity with abilities
- `aerthos/entities/player.py` - Player character with inventory
- `aerthos/world/dungeon.py` - Dungeon navigation
- `aerthos/generator/dungeon_generator.py` - Procedural generation
- `aerthos/storage/session_manager.py` - Game persistence

### System Files (Pick the one you need)

- `aerthos/systems/magic.py` - Spells and magic
- `aerthos/systems/skills.py` - Thief skills
- `aerthos/systems/saving_throws.py` - Save mechanics
- `aerthos/systems/ability_modifiers.py` - Ability bonuses
- `aerthos/systems/monster_ai.py` - Monster targeting
- `aerthos/systems/armor_system.py` - AC calculation

---

## Performance Notes

**Target Performance:**
- Command response: < 100ms
- Dungeon generation: < 1 second
- Save/load: < 1 second

**Scale:**
- Single-player only (no scaling concerns)
- Dungeons: 8-30 rooms typical
- Encounters: 1-10 monsters typical
- Parties: 1-6 characters

**Not Optimized For:**
- Large dungeons (100+ rooms)
- Concurrent players
- Real-time graphics
- High-frequency UI updates

---

## Common Grep Patterns

Quick way to find things:

```bash
# Find all command handlers
grep -r "_handle_" aerthos/engine/game_state.py

# Find all spell handlers
grep -r "_spell_" aerthos/systems/magic.py

# Find where function is used
grep -r "function_name" aerthos/

# Find TODO/FIXME comments
grep -r "TODO\|FIXME" aerthos/

# Find hardcoded values (should be in constants.py)
grep -r "MAGIC_NUMBER" aerthos/
```

---

## Git Commands Reference

```bash
# View campaign code (on backup branch)
git show backup-before-rollback-20251121-214217:aerthos/campaigns/campaign.py

# See what was attempted
git log --oneline backup-before-rollback-20251121-214217 | head -20

# See all branches
git branch -a

# See recent history
git log --oneline | head -20
```

---

## Summary

**Start Here:**
1. Run the game: `python main.py`
2. Read EXPLORATION_SUMMARY.md (this exploration)
3. Read CLAUDE.md (development guide)
4. Read TECHNICAL_BREAKDOWN.md (full documentation)

**Then Choose:**
- **Learn Architecture:** Study `aerthos/engine/game_state.py` and systems
- **Add Features:** Pick a system file, understand pattern, add to JSON data
- **Fix Bugs:** Run tests, read error, find relevant system file
- **Extend Game:** Add spells, monsters, equipment to JSON files

**All Your Answers Are In:**
- This codebase index (navigation)
- EXPLORATION_SUMMARY.md (overview)
- TECHNICAL_BREAKDOWN.md (details)
- CLAUDE.md (rules and guidelines)
- Inline code comments (implementation)

---

**Last Updated:** November 30, 2025
**Exploration Completeness:** 100% - All systems documented
**Code Coverage:** 417/417 tests passing
**Status:** Production-ready core game, campaign system abandoned
