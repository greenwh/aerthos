# AERTHOS - Comprehensive Technical Architecture Breakdown

⚠️ **ARCHIVED DOCUMENT** - This file is outdated as of December 6, 2025
- Campaign system was completed (not abandoned)
- Test coverage is now 541/541 (not 417)
- See `CLAUDE.md` for current development documentation
- See `ROADMAP.md` for current issue tracking
- This file preserved for historical technical reference

---

**Project:** AD&D 1e Text Adventure Game
**Location:** `/mnt/d/Development/aerthos`
**Language:** Python 3.10+
**Status:** ~~Active Development - Core Systems Complete, Campaign System Abandoned~~ **OUTDATED**
**Test Coverage:** ~~417/417 tests passing (100%)~~ **Now 541/541**

---

## 1. CORE ARCHITECTURE OVERVIEW

### 1.1 High-Level Design Philosophy

Aerthos is built as a **thin-layer architecture** where:
- **Core Engine** (`aerthos/` modules) implements all game mechanics
- **CLI Interface** (`main.py`) and **Web UI** (`web_ui/app.py`) are lightweight wrappers
- **Data-Driven Approach** - All game content (spells, monsters, items, equipment) externalized to JSON files
- **No External Dependencies** for core game (Python stdlib only)
- **Configuration-Centric** - Game tuning through constants files, not code changes

### 1.2 Main Component Layers

```
┌─────────────────────────────────────────┐
│   UI Layer                              │
│  ┌─────────────────┐  ┌──────────────┐  │
│  │  CLI (main.py)  │  │ Web UI       │  │
│  │  (1519 lines)   │  │ (Flask app)  │  │
│  └─────────────────┘  └──────────────┘  │
└────────────┬────────────────────────────┘
             │ Uses identical core APIs
┌────────────▼────────────────────────────┐
│   Engine Layer (CORE GAME LOGIC)        │
│  ┌─────────────────────────────────────┐│
│  │  GameState                          ││ Central coordinator
│  │  ├─ CombatResolver (THAC0)          ││ All systems interconnect
│  │  ├─ MagicSystem (Vancian)           ││ here
│  │  ├─ TimeTracker                     ││
│  │  ├─ Parser (NLP)                    ││
│  │  └─ EncounterManager                ││
│  └─────────────────────────────────────┘│
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   Systems Layer (SUBSYSTEMS)            │
│  ├─ Combat (combat.py)                  │
│  ├─ Magic (magic.py)                    │
│  ├─ Skills (skills.py)                  │
│  ├─ Ability Modifiers                   │
│  ├─ Saving Throws                       │
│  ├─ Monster AI                          │
│  ├─ Traps, Treasure, Movement           │
│  └─ Narrator (DMNarrator)               │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   Entity Layer (GAME OBJECTS)           │
│  ├─ Character (base)                    │
│  ├─ PlayerCharacter (with inventory)    │
│  ├─ Monster (with AI)                   │
│  ├─ Party (4-6 members)                 │
│  ├─ Equipment (weapons, armor, shields) │
│  └─ Items (consumables, treasure)       │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   World Layer (DUNGEONS & LOCATIONS)    │
│  ├─ Dungeon (navigation graph)          │
│  ├─ MultiLevelDungeon                   │
│  ├─ Room (with encounters)              │
│  ├─ Village/Shop/Inn/Guild              │
│  └─ Encounter (combat/trap/puzzle)      │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   Generation Layer (PROCEDURAL)         │
│  ├─ DungeonGenerator                    │
│  ├─ MultiLevelGenerator                 │
│  ├─ MonsterScaling                      │
│  ├─ TreasureGeneration                  │
│  └─ EncounterGeneration                 │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   Storage Layer (PERSISTENCE)           │
│  ├─ CharacterRoster                     │
│  ├─ PartyManager                        │
│  ├─ ScenarioLibrary                     │
│  └─ SessionManager                      │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   Data Layer (JSON FILES)               │
│  ├─ classes.json / races.json           │
│  ├─ monsters.json (269KB)               │
│  ├─ spells.json (158KB)                 │
│  ├─ weapons.json / armor.json           │
│  ├─ equipment.json                      │
│  └─ Ability/Save/Skill tables           │
└─────────────────────────────────────────┘
```

---

## 2. MODULE STRUCTURE & RESPONSIBILITIES

### 2.1 Engine Module (`aerthos/engine/`)

#### **GameState** (game_state.py)
- **Role**: Central coordinator of all game systems
- **Responsibilities**:
  - Manages player, dungeon, party, and active monsters
  - Routes all commands to appropriate handlers
  - Tracks combat state, encounters, and progression
  - Handles multi-level dungeon awareness
  - Serialization/deserialization of game state
- **Key Methods**:
  - `execute_command(command)` - Main command dispatcher
  - `_handle_move()`, `_handle_attack()`, `_handle_cast()` - Command handlers (25+ total)
  - `load_game_data()` - Loads all JSON data files
- **Internal Systems**: Combat, Magic, Time, Skills, Encounters, Monster AI, Narrator

#### **CombatResolver** (combat.py)
- **Role**: THAC0 combat system implementation
- **Core Mechanic**: `roll d20, hit if roll >= (THAC0 - target AC)`
- **Features**:
  - Descending AC (10=unarmored, 0=armored, -5=exceptional)
  - Critical hits (d20=20) and misses (d20=1)
  - Damage rolls by weapon and target size (S/M vs L)
  - Initiative (d6 for side)
  - Monster targeting with formation awareness
- **DiceRoller Utility**: Parses XdY±Z dice notation

#### **CommandParser** (parser.py)
- **Role**: Natural language command processing
- **Approach**: Verb-based with flexible tokenization
- **Supported Verbs**: 45+ verb groups (attack, cast, take, equip, move, rest, etc.)
- **Features**:
  - Stopword filtering (the, a, an, at)
  - Direction mapping (n→north, u→up, etc.)
  - Multi-target parsing ("cast magic missile at orc")
  - Direction shortcuts (n, s, e, w, u, d)
- **Returns**: Command(action, target, modifier, instrument)

#### **TimeTracker** (time_tracker.py)
- **Role**: Dungeon time management
- **Time Units**:
  - Turns (10 minutes each)
  - Hours (6 turns)
  - Days
- **Tracked Resources**:
  - Light source burn-down (torches 6 turns, lanterns 24 turns)
  - Ration consumption
  - Spell recovery
- **RestSystem**: Enables HP/spell recovery in safe rooms (requires rations, 15% wandering monster chance)

### 2.2 Entities Module (`aerthos/entities/`)

#### **Character** (character.py) - Base Class
- **Type**: Dataclass with AD&D 1e attributes
- **Attributes**:
  - 6 core abilities (STR, DEX, CON, INT, WIS, CHA) - 3-18 range
  - Combat stats (HP, AC, THAC0, level)
  - 5-category saving throws
  - Alignment (9-point system)
  - Size (S/M/L for damage calculations)
- **Methods**:
  - `take_damage()`, `heal()` - HP management
  - `get_to_hit_bonus()`, `get_damage_bonus()` - From ability modifiers
  - `get_ac_bonus()` - From DEX

#### **PlayerCharacter** (player.py) - Extends Character
- **Unique Attributes**:
  - Inventory (with encumbrance system)
  - Equipment (worn/wielded items)
  - Spells memorized (slots by level)
  - Thief skills (8 percentile skills)
  - Experience points
  - Gold
- **Key Classes**:
  - `Item`, `Weapon`, `Armor`, `Shield`, `LightSource` - Equipment types
  - `Inventory` - Weight-based with current_weight/max_weight
  - `Spell`, `SpellSlot` - Vancian magic system
- **Spell System**:
  - Pre-memorized slots (limited per level)
  - Cast consumes slot
  - Restore on rest
  - Magic components abstracted (standard vs rare)

#### **Monster** (monster.py) - Extends Character
- **Unique Attributes**:
  - Hit dice (e.g., "2+1", "3")
  - Treasure type (A-Z from DMG)
  - AI behavior (aggressive, defensive, flee_low_hp)
  - Special abilities (poison, breath, magic resistance)
  - Size and movement rate
- **AI System**:
  - MonsterTargetingAI: Formation-aware targeting
  - Target front-line 70% of time
  - Target spellcasters if high INT
  - Opportunistic targeting if front line falls

#### **Party** (party.py)
- **Composition**: 4-6 player characters
- **Formation**: Front/back line positioning
  - Fighters and Clerics default front
  - Others default back
  - Affects combat targeting
- **Operations**:
  - Add/remove members
  - Get front/back line
  - Track living/dead members
  - Combat damage propagation
- **Multi-character play**: Player controls entire party as one unit

### 2.3 Systems Module (`aerthos/systems/`)

#### **MagicSystem** (magic.py)
- **Mechanics**: Full Vancian spell memorization
- **Implemented Spells** (332 total across levels 1-9):
  - Cleric: Cure Light Wounds, Turn Undead, Hold Person, etc.
  - Magic-User: Magic Missile, Sleep, Fireball, etc.
  - Spell handlers: Sleep (2d4 HD affected), Magic Missile (1d4+1 damage), etc.
- **Spell Effects**:
  - Target selection with saving throws
  - Area of effect handling
  - Damage application
  - Narrative descriptions via DMNarrator

#### **SkillResolver** (skills.py)
- **Thief Skills** (percentile-based rolls):
  1. Open Locks
  2. Find/Remove Traps
  3. Pick Pockets
  4. Move Silently
  5. Hide in Shadows
  6. Hear Noise
  7. Climb Walls
  8. Read Languages
- **Modifiers**:
  - Race bonuses/penalties
  - DEX modifiers
  - Armor restrictions
  - Usage penalty ("In darkness" -20%)
- **Check**: Roll d100, succeed if <= skill%

#### **SavingThrowResolver** (saving_throws.py)
- **5 Categories** (AD&D 1e standard):
  1. Poison/Death Magic
  2. Rod/Staff/Wand
  3. Petrification/Paralysis
  4. Breath Weapon
  5. Spell
- **Mechanics**: Roll d20, succeed if roll <= save value
- **Modifiers**: Magic items, spells, conditions

#### **AbilityModifierSystem** (ability_modifiers.py)
- **Source**: Complete Players Handbook ability score tables
- **Modifiers by Ability**:
  - STR: Hit probability, damage, encumbrance
  - DEX: AC bonus, initiative
  - CON: HP per level, system shock
  - INT: Languages, XP bonus/penalty
  - WIS: Magic save bonus, spell resistance
  - CHA: Reaction adjustments, max henchmen
- **Exceptional STR** (Fighters): 18/01-18/00 with percentile

#### **ArmorSystem** (armor_system.py)
- **AC Calculation**: Base AC ± DEX ± magic bonuses ± conditions
- **Armor Types**: Light (leather), Medium (chain), Heavy (plate)
- **Class Restrictions**: Enforced (clerics can't wear helms, magic-users limited)
- **Magic Bonuses**: +1/+2/+3 armor/shields reduce AC further

#### **Other Key Systems**:
- **MonsterAbilities** - Special attacks (poison, breath, petrification)
- **MonsterAI** - Target selection based on formation and intelligence
- **Narrator** (DMNarrator) - Atmospheric descriptions and combat narration
- **EnvironmentFilter** - Dungeon/wilderness/underwater monster filtering
- **XPCalculator** - Dynamic XP based on monster difficulty vs party level
- **TurningUndead** - Cleric ability to turn undead
- **TrapSystem** - Detection and disarming
- **TreasureGeneration** - Encounter loot generation

### 2.4 World Module (`aerthos/world/`)

#### **Dungeon** (dungeon.py)
- **Role**: Single-level dungeon navigation
- **Structure**:
  - Rooms connected by exits (north, south, east, west)
  - Navigation graph with room ID references
  - Start room designation
- **Loading**: From JSON file or generator output
- **Methods**:
  - `move(current_room_id, direction)` - Navigate to adjacent room
  - `get_room(id)` - Retrieve room
  - Room data stored separately for encounter/loot info

#### **MultiLevelDungeon** (multilevel_dungeon.py)
- **Enhancement**: Multiple levels connected by stairs
- **Features**:
  - Per-level roomfrom data
  - Stair navigation (up/down between levels)
  - Multi-level awareness in GameState
  - Auto-map per level
- **Levels**: Stored as list of Dungeon objects

#### **Room** (room.py)
- **Attributes**:
  - Title, description, light level
  - Exits dict: `{direction: room_id}`
  - Items (takeable objects)
  - Safe for rest flag
  - Encounter reference (if any)
- **Light Levels**: Bright, dim, dark
- **Interactions**: Can search, open, examine

#### **Encounter** (encounter.py)
- **Types**: Combat, Trap, Puzzle, Treasure
- **CombatEncounter**:
  - Monster roster
  - Surprise/ambush chance
  - Treasure generation
  - Morale tracking
- **TrapEncounter**: Detection DC, damage, effects
- **Manager**: Route rooms to encounters, handle triggers

#### **Village/Shop/Inn/Guild** (village.py, shop.py, inn.py, guild.py)
- **Village**: Aggregates shops, inns, guilds (currently disconnected from overworld)
- **Shop**: Inventory with stock, buy/sell mechanics (50% buy price)
- **Inn**: Rest facilities (10gp/night, restore HP)
- **Guild**: Class-specific services (quest boards, training)
- **Status**: Standalone systems, not yet integrated into campaign

#### **Automap** (automap.py)
- **ASCII Map Generation**: Shows explored rooms as grid
- **Visual Format**:
  ```
       [ ]
        |
  [ ]-[X]-[ ]    (X = current position)
        |
       [ ]
  ```
- **Exploration**: Maps update as player explores

### 2.5 Generator Module (`aerthos/generator/`)

#### **DungeonGenerator** (dungeon_generator.py)
- **Algorithm**:
  1. Generate room graph (random connectivity)
  2. Create room objects from graph
  3. Populate encounters (combat 50%, traps 20%, empty 30%)
  4. Place treasures and items
  5. Designate 1-2 safe rest rooms
- **Configurability**:
  - Num rooms (5-30)
  - Layout type (linear, branching, network)
  - Combat/trap frequency
  - Monster pool
  - Encounter density
- **Theming**: Room titles/descriptions by theme (mine, crypt, cave, ruins, sewer)
- **Seeding**: Reproducible dungeons with seed parameter
- **Narrator Integration**: Uses DMNarrator for descriptions

#### **MultiLevelGenerator** (multilevel_generator.py)
- **Creates**: Multi-level dungeons with stairs
- **Per-level Generation**: Uses DungeonGenerator for each level
- **Stair Connections**: Links levels with up/down stairs
- **Difficulty Scaling**: Monsters tougher on lower levels

#### **Config** (config.py)
- **Presets**: EASY_DUNGEON, STANDARD_DUNGEON, HARD_DUNGEON
- **Parameters**:
  - num_rooms (rooms per level)
  - party_level (for scaling)
  - combat_frequency (0.0-1.0)
  - trap_frequency
  - layout_type
  - monster_pool
  - seed (optional, for reproducibility)

#### **MonsterScaling** (monster_scaling.py)
- **Difficulty Tiers**: Easy/standard/hard
- **Adjustments**:
  - Monster count per encounter
  - Monster HD range
  - Treasure multiplier
  - Encounter frequency

### 2.6 Storage Module (`aerthos/storage/`)

#### **CharacterRoster** (character_roster.py)
- **Directory**: `~/.aerthos/characters/`
- **Format**: JSON files with UUID names
- **Operations**: Create, load, list, delete characters
- **Persistence**: Survives game sessions

#### **PartyManager** (party_manager.py)
- **Directory**: `~/.aerthos/parties/`
- **Operations**: Create parties from roster characters
- **Composition**: 4-6 characters
- **Reusability**: Parties can be played across multiple sessions

#### **ScenarioLibrary** (scenario_library.py)
- **Directory**: `~/.aerthos/scenarios/`
- **Content**: Saved generated dungeons
- **Sharing**: Can replay exact same dungeon by loading scenario

#### **SessionManager** (session_manager.py)
- **Directory**: `~/.aerthos/sessions/`
- **Scope**: Full game state (party + dungeon + progress)
- **Multiple Sessions**: Can have concurrent games
- **Metadata**: Created date, last played, current room, turns elapsed
- **Persistence**: Save/load full game snapshots
- **Interconnection**: Uses Character Roster, Party Manager, Scenario Library

### 2.7 UI Module (`aerthos/ui/`)

#### **Display** (display.py)
- **Text Formatting**: Headers, separators, boxes
- **Output Management**: Color ANSI codes, pagination
- **Narrative Display**: Combat results, spell effects, exploration

#### **CharacterCreator** (character_creation.py)
- **Method**: Roll 3d6 six times
- **Class Selection**: Fighter, Cleric, Magic-User, Thief
- **Race Selection**: Human, Elf, Dwarf, Halfling
- **Alignment Selection**: 9-point system with class restrictions
- **Starting Equipment**: Assigned automatically
- **HP Calculation**: With CON modifiers

#### **CharacterSheet** (character_sheet.py)
- **Display Format**: Full character stats, abilities, equipment, spells
- **Formatting**: ASCII table with sections

#### **SaveSystem** (save_system.py)
- **Quick Save**: `~/.aerthos/saves/quick_save.json`
- **Serialization**: Full game state to JSON
- **Deserialization**: Restore from JSON

---

## 3. DATA FLOW ARCHITECTURE

### 3.1 Command Execution Pipeline

```
User Input (string)
    ↓
CommandParser.parse()
    ├─ Tokenize: lower, split on spaces
    ├─ Extract verb (action) from token #1
    ├─ Extract target, modifier, instrument from remaining tokens
    ↓ Returns Command(action, target, modifier, instrument)
    ↓
GameState.execute_command(command)
    ├─ Check if player alive (blocks action commands if dead)
    ├─ Route to handler dict (25+ handlers)
    ├─ Call appropriate handler: _handle_move(), _handle_attack(), etc.
    ↓ Each handler returns Dict with {success, message, effects}
    ↓
Handler Implementation (e.g., _handle_attack)
    ├─ Parse target name → find monster in current_monsters
    ├─ Get equipped weapon
    ├─ Call CombatResolver.attack_roll()
    │   ├─ Roll d20
    │   ├─ Calculate hit: roll >= (THAC0 - AC)
    │   ├─ If hit, roll weapon damage (+ STR bonus)
    │   ├─ Apply damage to monster
    │   └─ Return {success, narrative, damage}
    ├─ Check if monster dead → remove from active_monsters
    ├─ If combat ended, set in_combat = False
    └─ Return results
    ↓
Display.format_output(results)
    ├─ Narrative text
    ├─ Updated game state
    ├─ Current room description
    └─ Print to terminal
```

### 3.2 Combat Round Flow

```
Player Command: "attack orc"
    ↓
CombatResolver.attack_roll()
    ├─ Roll d20
    ├─ Check critical hit (20) / miss (1)
    ├─ Calculate needed: attacker.thac0 - defender.ac
    ├─ Hit if: roll >= needed
    ├─ If hit: Roll weapon damage (1d8 for longsword, or 1d4 vs large)
    ├─ Add STR damage bonus
    └─ Apply to monster HP
    ↓
Monster AI Responds (MonsterTargetingAI)
    ├─ Select target
    │   ├─ Formation-aware: 70% front line if alive
    │   ├─ 20% back line if reachable
    │   └─ 10% opportunistic
    ├─ Check spell requirement (if magic-using monster)
    ├─ Perform attack (or cast spell)
    └─ Apply damage to selected party member
    ↓
Turn Complete
    ├─ Time advances (1 turn = 10 minutes)
    ├─ Light sources burn down
    ├─ Spells/conditions process
    └─ Check for encounter triggers (wandering monsters)
```

### 3.3 Spell Casting Flow

```
Player Command: "cast magic missile at orc"
    ↓
GameState._handle_cast()
    ├─ Parse spell name, target name
    ├─ Find target in active_monsters
    ├─ Call MagicSystem.cast_spell()
    ├─ Check if spell memorized & available (slot not used)
    ├─ Mark spell slot as used (consumed)
    ├─ Call MagicSystem._execute_spell_effect()
    │   ├─ Route to spell handler (e.g., _spell_magic_missile)
    │   ├─ Handler applies spell logic
    │   │   ├─ Roll 1d4+1 damage
    │   │   ├─ Check saving throw (target rolls d20 <= save value)
    │   │   ├─ Apply effects (damage, condition, buff, debuff)
    │   │   └─ Generate narrative description
    │   └─ Return {narrative, affected, effects}
    ├─ Apply damage to target
    ├─ Check target death
    └─ Return results
    ↓
Combat AI responds (same as melee attack)
```

### 3.4 Game State Persistence Flow

```
Player Command: "save"
    ↓
SaveSystem.save_game()
    ├─ Serialize GameState
    │   ├─ Player character to JSON
    │   ├─ Dungeon structure (or MultiLevelDungeon)
    │   ├─ Active monsters
    │   ├─ Time tracker state
    │   ├─ Combat state
    │   └─ Current room/level
    ├─ Serialize Party (if multi-character)
    ├─ Write to ~/.aerthos/saves/quick_save.json
    └─ Return success message

Player Command: "load" (on next game start)
    ↓
SaveSystem.load_game()
    ├─ Read ~/.aerthos/saves/quick_save.json
    ├─ Deserialize to GameState object
    ├─ Restore player character
    ├─ Restore dungeon and room references
    ├─ Restore active monsters and combat state
    └─ Resume game at saved point
```

---

## 4. KEY SYSTEMS DEEP DIVE

### 4.1 THAC0 Combat System

**Core Formula:**
```
To Hit Number = THAC0 - Target AC

Attack Succeeds if: d20 roll >= To Hit Number

Example:
- Attacking Fighter (THAC0 20) vs Goblin (AC 6)
- To Hit = 20 - 6 = 14
- Need 14+ on d20 to hit
```

**Base THAC0 by Class:**
- Fighter: 20 (improves every level)
- Cleric: 20 (improves every 2 levels)
- Thief: 20 (improves every 2 levels)
- Magic-User: 21 (improves every 3 levels)

**AC Categories:**
- 10 = Unarmored/Light clothing
- 9 = Leather armor
- 7 = Scale/Chain mail
- 5 = Plate armor
- 3 = Plate + Shield
- 0 = Exceptional armor
- -5 = Magical armor (+3 equivalent)

**Modifiers:**
- Strength bonus/penalty (melee only)
- Dexterity bonus/penalty (all attacks)
- Weapon vs AC adjustments
- Magic item bonuses

### 4.2 Vancian Magic System

**Mechanics:**
- Spells are pre-memorized in slots
- Each slot holds ONE spell of that level
- Casting CONSUMES the slot
- Only way to recover: Rest (8 hours) + consume rations
- Spell components abstracted (standard vs rare)

**Spell Slots by Level:**

| Character | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|-----------|---------|---------|---------|---------|---------|
| Cleric Lv1 | 1 | — | — | — | — |
| Cleric Lv2 | 2 | 1 | — | — | — |
| Magic-User Lv1 | 1 | — | — | — | — |
| Magic-User Lv2 | 2 | 1 | — | — | — |

**Implemented Spells (7 core, 332 total in database):**
1. Sleep - 2d4 HD affected
2. Magic Missile - 1d4+1 each
3. Cure Light Wounds - 1d8 healing
4. Protection from Evil - +2 AC, saves, attack/damage vs evil
5. Detect Magic - Reveal magical auras
6. Burning Hands - 1d6 per caster level
7. Charm Person - Save or become friendly

**Database**: 332 spells across all levels (1-9)
- Cleric spells: Divine magic
- Magic-User spells: Arcane magic
- Handlers: Implemented for all 7 core spells

### 4.3 Saving Throws System

**Five Categories (AD&D 1e standard):**

1. **Poison/Death Magic** - Magic missiles, poisoned attacks
2. **Rod/Staff/Wand** - Magical devices
3. **Petrification/Paralysis** - Petrification, hold spells
4. **Breath Weapon** - Dragon breath, area effects
5. **Spell** - General magic spells

**Mechanics:**
- Roll d20, succeed if roll ≤ save value
- Save values based on class + level
- Magic items/conditions can modify
- Some spells allow saving throw for half damage

**Base Save Values (Level 1):**
| Class | Poison | Rod/Staff | Petrify | Breath | Spell |
|-------|--------|-----------|---------|--------|-------|
| Fighter | 12 | 13 | 14 | 15 | 16 |
| Cleric | 14 | 13 | 12 | 16 | 15 |
| Magic-User | 15 | 14 | 13 | 16 | 14 |
| Thief | 13 | 14 | 13 | 16 | 15 |

### 4.4 Thief Skills System

**Eight Percentile-Based Skills:**

| Skill | Roll Type | Modifiers |
|-------|-----------|-----------|
| Open Locks | d100, ≤ skill% | DEX ±10%, Race ±5%, Light -20% |
| Find/Remove Traps | d100, ≤ skill% | INT ±10%, Darkness -30% |
| Pick Pockets | d100, ≤ skill% | DEX ±10%, Crowd ±10% |
| Move Silently | d100, ≤ skill% | DEX ±10%, Encumbrance -10% |
| Hide in Shadows | d100, ≤ skill% | DEX ±10%, Darkness +20% |
| Hear Noise | d100, ≤ skill% | WIS ±10%, Noise environment ±20% |
| Climb Walls | d100, ≤ skill% | STR ±10%, Encumbrance -5% |
| Read Languages | d100, ≤ skill% | INT ±10%, Ancient languages -30% |

**Base Percentages by Level:**
- Level 1: 20-35% depending on skill
- Improves by 5% per level
- Race bonuses: +10% (Elf), -5% (Dwarf), etc.

---

## 5. DATA STRUCTURES & SCHEMAS

### 5.1 Character Data Structure

```python
@dataclass
class Character:
    # Identity
    name: str
    race: str  # Human, Elf, Dwarf, Halfling
    char_class: str  # Fighter, Cleric, Magic-User, Thief
    level: int = 1
    alignment: str = "True Neutral"  # 9-point system
    
    # Abilities (3-18, 3d6 each)
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    # Combat
    hp_current: int = 1
    hp_max: int = 1
    ac: int = 10  # Descending
    thac0: int = 20
    attacks_per_round: float = 1.0
    
    # Saving Throws
    save_poison: int = 16
    save_rod_staff_wand: int = 17
    save_petrify_paralyze: int = 15
    save_breath: int = 20
    save_spell: int = 18
    
    # State
    is_alive: bool = True
    conditions: List[str] = []  # ['poisoned', 'paralyzed', 'sleeping', etc.]
    xp: int = 0
```

### 5.2 Room/Dungeon Structure

```json
{
  "id": "room_001",
  "title": "Entry Hall",
  "description": "A vast stone chamber...",
  "light_level": "dark",
  "exits": {
    "north": "room_002",
    "east": "room_003"
  },
  "items": [
    {"name": "Gold Coins", "quantity": 50, "weight": 5},
    {"name": "Leather Pouch", "quantity": 1, "weight": 0.5}
  ],
  "encounters": [
    {
      "type": "combat",
      "monsters": ["goblin", "goblin", "goblin_archer"],
      "treasure_type": "C",
      "surprise_chance": 0.3
    }
  ],
  "safe_rest": false
}
```

### 5.3 Monster Data Structure

```json
{
  "monster_id": {
    "name": "Orc",
    "hit_dice": "1+1",
    "ac": 6,
    "thac0": 19,
    "damage": "1d8",
    "movement": 9,
    "size": "M",
    "xp_value": 65,
    "treasure_type": "D",
    "ai_behavior": "aggressive",
    "special_abilities": ["leader_bonus"],
    "alignment": "Chaotic Evil",
    "morale": 8
  }
}
```

---

## 6. TESTING INFRASTRUCTURE

### 6.1 Test Coverage

**Total Tests**: 417 passing (100%)

**Test Categories:**
- **Unit Tests**: Core mechanics (combat, magic, saves)
- **Integration Tests**: End-to-end scenarios
- **Combat Tests**: THAC0, damage, criticals
- **Parser Tests**: Command parsing variations
- **Ability Tests**: Modifiers, racial adjustments
- **Web API Tests**: Flask endpoints
- **Storage Tests**: Save/load mechanics
- **Monster Tests**: AI, abilities, encounters
- **Magic Tests**: Spell casting, memorization
- **Armor Tests**: AC calculations
- **Thief Skills Tests**: Percentile checks
- **XP Tests**: Dynamic calculation
- **Party Tests**: Multi-character operations
- **Dungeon Tests**: Navigation, generation
- **Village Tests**: Shop/inn mechanics
- **Multi-level Tests**: Stair navigation

### 6.2 Test Running

```bash
# Run all tests
python3 run_tests.py --no-web

# Categories
python3 run_tests.py --unit
python3 run_tests.py --integration
python3 run_tests.py --web

# Specific test
python3 -m unittest tests.test_combat -v
```

---

## 7. CAMPAIGN SYSTEM - THE FAILED ATTEMPT

### 7.1 What Was Attempted

**Branch**: `backup-before-rollback-20251121-214217` (still in git)

**Commits in Campaign Branch:**
1. `f338456` - [Phases 2-3] Complete travel system and location framework
2. `c06734f` - [Phase 3 Week 2] PAUSE - Command infrastructure complete
3. `dd57e09` - Fix JSON serialization and add party character switching
4. `98b9a56` - [Phase 7] Add hex map visualization for campaign overworld
5. `4a64b25` - Add campaign/overworld commands to help system
6. `91dd137` - Fix web UI crash when entering overworld mode
7. `a5e8415` - Add context-aware UI panels (4 contexts: dungeon, overworld, village, encounter)
8. `cc4929d` - Replace SVG hex map with Unicode/emoji-based map renderer

### 7.2 What Was Implemented

**Code Files Created** (all in /pycache/ on main, preserved in branch):
```
aerthos/campaigns/
├── __init__.py
├── campaign.py              # Campaign class (metadata, state)
├── campaign_loader.py       # Campaign JSON loading
└── faction.py               # Faction definitions
```

**Features Attempted:**
1. **Hex-based overworld map** (30x40 grid)
2. **Travel system** with time costs and encounters
3. **Multiple locations** (Oakhaven, Eldoria, villages)
4. **Faction/reputation** system
5. **Weather generation**
6. **Context-aware UI panels** (dungeon/overworld/village/encounter)
7. **Web UI hex map visualization** (SVG → Unicode emoji replacement)
8. **Campaign-aware GameState** integration

**Planning Document**: `docs/CAMPAIGN_IMPLEMENTATION_PLAN.md`
- 7-phase plan: Foundation, Travel, Locations, Factions, Weather, Web UI, Content
- Estimated 10-15 weeks of development
- Data-driven architecture (JSON campaigns)
- Backward compatible (existing dungeons work without campaign)

### 7.3 Why It Was Abandoned

**Reasons (Inferred from git history):**
1. **Scope Creep**: Campaign system was too ambitious (7 phases × 2-3 weeks)
2. **Web UI Complexity**: 4-context UI panels required major frontend refactoring
3. **Command Parser Overhaul**: Travel commands and context switching needed parser redesign
4. **Integration Challenges**: Connecting overworld → village → dungeon transitions was non-trivial
5. **Testing Burden**: 417 tests would need campaign-aware updates
6. **Active Bugs**: Crashes during overworld transitions and web UI rendering

**Decision Point**: Roll back instead of debugging (commit `458006d` "Organize documentation")
- Main branch retains stable core game
- Campaign branch preserved for future reference
- Focus shifted to alignment system, character management, UI improvements

### 7.4 Current State of Campaign Code

**On Main Branch (`aerthos/campaigns/`):**
```
Only __pycache__ directory exists
- Python bytecode from previous campaign build
- Actual source files removed
```

**On Backup Branch (`backup-before-rollback-20251121-214217`):**
```
Full campaign implementation:
- campaign.py (100+ lines)
- campaign_loader.py (80+ lines)
- faction.py (60+ lines)
+ Travel system implementation
+ Hex map utilities
+ Encounter generation
+ Web UI overworld rendering
```

**Recovery Option**: If campaign work is desired:
```bash
# Check out campaign code from backup branch
git show backup-before-rollback-20251121-214217:aerthos/campaigns/campaign.py

# Or switch entire branch
git checkout backup-before-rollback-20251121-214217
```

### 7.5 What Would Have Been Needed to Complete

**Estimated Remaining Work**:
1. **Debug Overworld Transitions** (1-2 weeks)
   - Fix HTML/JavaScript hex map rendering
   - Seamless dungeon → overworld → village flow
   - Context panel switching

2. **Complete Faction System** (1 week)
   - Reputation storage/updates
   - NPC reactions to faction standing
   - Reputation effects on prices

3. **Weather & Environment** (1 week)
   - Random weather generation
   - Travel hazard checks
   - Seasonal effects

4. **Integration Testing** (2-3 weeks)
   - 200+ new tests for campaign features
   - CLI and Web UI parity on overworld
   - Save/load campaign state

5. **Content Data** (1-2 weeks)
   - campaign.json schema
   - world_map.json (30x40 grid)
   - locations.json (villages, dungeons, POIs)
   - factions.json (power groups)
   - encounters.json (wilderness tables)

**Total Estimate**: 6-9 additional weeks

---

## 8. CURRENT GAME LIMITATIONS & STRENGTHS

### 8.1 Strengths

✅ **Solid Core Systems**:
- THAC0 combat is faithful to AD&D 1e spec
- Vancian magic system works perfectly
- 5-category saving throws implemented
- Percentile thief skills functional
- Ability modifiers from Players Handbook

✅ **Content Dense**:
- 332 spells across 9 levels
- 269KB monster database (100+ creatures)
- 65 equipment items
- 25+ ability score modifiers tables
- Complete AD&D 1e rule coverage

✅ **Well Architected**:
- Clean separation of concerns
- Data-driven (JSON externalized)
- Easy to extend (add spells/monsters in JSON)
- Configuration-based game balance

✅ **Robust Testing**:
- 417 tests, 100% passing
- All major systems covered
- Integration tests for complex flows
- Web API tests

✅ **Dual Interfaces**:
- CLI (1519 lines main.py) - pure text
- Web UI (75KB app.py, Gold Box style) - visual
- Code shared between both

✅ **Persistence**:
- 5-layer save system (quick save, character roster, parties, scenarios, sessions)
- Full game state serialization
- Multi-session support

### 8.2 Limitations

❌ **Single-Player Only**:
- No multiplayer or networking
- Party is NPC under player control (not separate players)

❌ **Low-Level Play**:
- Currently designed for levels 1-3
- Experience tables go to level 10, but untested
- No high-level spells (9th level implemented but untested)

❌ **Dungeon-Only**:
- No overworld map
- No wilderness encounters (except via generator)
- No travel system
- Villages disconnected from game world

❌ **Limited Classes/Races**:
- 4 classes (Fighter, Cleric, Magic-User, Thief)
- 4 races (Human, Elf, Dwarf, Halfling)
- No Paladin, Ranger, Druid, Bard

❌ **Combat Simplification**:
- Monster HP hidden from player
- Summary combat (not turn-by-turn details)
- No morale rules (implemented but unused)
- Simplified spellcasting (no components search)

❌ **Generator Quality**:
- Random dungeon generation is basic (room+corridor)
- No complex shapes or thematic layouts
- Limited encounter variety

❌ **Web UI Gaps**:
- No hex map visualization (campaign attempt failed)
- Limited keyboard shortcuts (basic arrows/WASD)
- No drag-and-drop equipment management

---

## 9. SYNCHRONIZATION POINTS (CLI/Web UI)

### 9.1 Critical Sync Requirements

Both `main.py` and `web_ui/app.py` must call game functions identically:

**Dungeon Generation**:
```python
# Both must call:
DungeonGenerator.generate(config)  # Consistent config object
MultiLevelGenerator.generate(num_levels, rooms_per_level, dungeon_name)
```

**Character Creation**:
```python
# Both must create characters with:
CharacterCreator.create_character()
# And initialize equipment identically
```

**Game State Access**:
```python
# Both must serialize via:
GameState.serialize()  # For save files
GameState.deserialize(json_data)  # For loading
```

**Command Execution**:
```python
# Both must parse via:
CommandParser.parse(user_input)
# And execute via:
GameState.execute_command(command)
```

### 9.2 Recent Sync Issues Fixed

**Issue 1** (commit `ff3db4f`): MultiLevelGenerator.generate() parameter change
- Old: `base_config=config`
- New: No parameter, uses defaults
- Fix: Updated both `main.py:159` and `web_ui/app.py:932`

**Issue 2** (commit `a280bc2`): JSON serialization of PartyCharacter objects
- Problem: Party members not serializing correctly
- Fix: Updated Party.to_json() and from_json() methods
- Both UIs now serialize party state identically

---

## 10. PROJECT STATISTICS

### 10.1 Code Metrics

| Metric | Value |
|--------|-------|
| Total Lines of Code (aerthos/) | ~15,000 |
| Main.py | 1,519 lines |
| Web UI app.py | 1,938 lines |
| Engine/Combat/Parser/Core | ~3,500 lines |
| Systems (magic, skills, combat) | ~4,200 lines |
| Entities (character, monster, party) | ~1,800 lines |
| World (dungeon, room, encounters) | ~1,500 lines |
| Generator (dungeon, multilevel) | ~2,000 lines |
| Storage (persistence managers) | ~1,200 lines |
| Tests | ~3,500 lines |
| JSON Data Files | ~1.2 MB |
| Documentation | ~30 files, 100+ KB |

### 10.2 Data Metrics

| Data | Count |
|------|-------|
| Monsters | 100+ |
| Spells | 332 (all levels) |
| Equipment Items | 65 |
| Ability Modifiers Tables | 25+ |
| Character Classes | 4 (7 more in design) |
| Character Races | 4 (additional in design) |
| Tests | 417 (100% passing) |
| Test Files | 27 |
| Documentation Files | 50+ |
| Git Commits | 200+ |

### 10.3 Feature Completion

| Feature | Status | Completeness |
|---------|--------|--------------|
| Core Combat | ✅ Complete | 100% |
| Vancian Magic | ✅ Complete | 100% |
| Character Creation | ✅ Complete | 100% |
| Dungeon Navigation | ✅ Complete | 100% |
| Saving Throws | ✅ Complete | 100% |
| Thief Skills | ✅ Complete | 100% |
| Multi-Level Dungeons | ✅ Complete | 100% |
| Party Management | ✅ Complete | 100% |
| Persistence (5 layers) | ✅ Complete | 100% |
| Village System | ✅ Complete | 100% |
| Alignment System | ✅ Complete | 100% |
| XP Calculation | ✅ Complete | 100% |
| Formation Combat | ✅ Complete | 100% |
| Campaign System | ❌ Abandoned | 25% |
| Overworld Map | ❌ Not Started | 0% |
| Quest System | ❌ Not Started | 0% |
| NPC Dialogue | ❌ Not Started | 0% |
| Faction Reputation | ❌ Partial | 15% |

---

## 11. DESIGN PATTERNS USED

### 11.1 Architectural Patterns

**Layered Architecture**: UI → Engine → Systems → Entities → World → Storage
- Clear separation of concerns
- Easy to test each layer independently
- Can swap UI without touching game logic

**Data-Driven Design**: Game content in JSON, not code
- Modders can customize without coding
- Balance tweaks in constants.py
- Extensible to new content

**Service Locator Pattern**: GameState as central hub
- All systems registered in GameState
- Single point of access to all game functionality
- Easy to inject mocks for testing

**Strategy Pattern**: Multiple monster AI strategies
- AggressiveAI, DefensiveAI, FleeAI
- Selected based on monster type
- Easy to add new behaviors

**Observer Pattern** (implicit): Encounter triggers
- Dungeon exploration triggers encounters
- Combat triggers monster AI
- Rest triggers restoration systems

### 11.2 Design Principles

**SOLID Principles:**
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension (new spells/monsters in JSON), closed for modification
- **Liskov Substitution**: Character → PlayerCharacter, Monster maintains contracts
- **Interface Segregation**: GameData loads only needed data
- **Dependency Inversion**: Systems depend on GameState abstractions, not concrete implementations

**AD&D 1e Authenticity**: Faithful to original rules
- THAC0 not d20 modern
- Descending AC not ascending
- Vancian magic not spell points
- Percentile skills not d20 checks

---

## 12. CONFIGURATION MANAGEMENT

### 12.1 Constants File

All magic numbers in `aerthos/constants.py`:
```python
# Mechanics
D20_MAX = 20
CRITICAL_HIT = 20
CRITICAL_MISS = 1

# Time
MINUTES_PER_TURN = 10
TURNS_PER_HOUR = 6

# Combat
THAC0_FIGHTER_BASE = 20
THAC0_CLERIC_BASE = 20
FRONT_LINE_TARGET_CHANCE = 70

# Abilities
ABILITY_MIN = 3
ABILITY_MAX = 18

# Resources
TORCH_DURATION_TURNS = 6
LANTERN_DURATION_TURNS = 24

# Encumbrance
COINS_PER_POUND = 10
ENCUMBRANCE_LIGHT = 350
```

### 12.2 Generator Config

`aerthos/generator/config.py` defines dungeon difficulty:
```python
class DungeonConfig:
    num_rooms: int = 12
    party_level: int = 1
    combat_frequency: float = 0.6
    trap_frequency: float = 0.2
    monster_pool: List[str] = []
    layout_type: str = 'branching'
    seed: Optional[int] = None
    theme: str = 'mine'

EASY_DUNGEON = DungeonConfig(num_rooms=8, combat_frequency=0.4)
STANDARD_DUNGEON = DungeonConfig(num_rooms=12, combat_frequency=0.6)
HARD_DUNGEON = DungeonConfig(num_rooms=15, combat_frequency=0.8)
```

### 12.3 Persistence Paths

`aerthos/constants.py` also defines save locations:
```python
SAVE_DIR = Path.home() / '.aerthos' / 'saves'
CHARACTER_DIR = Path.home() / '.aerthos' / 'characters'
PARTY_DIR = Path.home() / '.aerthos' / 'parties'
SCENARIO_DIR = Path.home() / '.aerthos' / 'scenarios'
SESSION_DIR = Path.home() / '.aerthos' / 'sessions'
```

---

## 13. SUMMARY & RECOMMENDATIONS

### 13.1 What's Production-Ready

✅ **Core Game Loop**: Fully playable, tested, stable
- Character creation through dungeon completion
- All core mechanics (combat, magic, saves, skills)
- Save/load working perfectly
- Both CLI and Web UI fully functional

✅ **Content Database**: Rich and expansive
- 332 spells ready to use
- 100+ creatures with AI
- 65 equipment items
- Complete ability modifier tables

✅ **Architecture**: Solid foundation for future work
- Clean, maintainable code
- Easy to extend (new spells/monsters in JSON)
- Well-tested (100% pass rate)
- Documentation complete

### 13.2 Recommended Next Steps

**If Adding Features:**
1. **Complete Additional Classes** (Paladin, Ranger, Druid)
   - Requires data in classes.json
   - New ability restrictions in character creation
   - Tests for new mechanics
   - Estimated: 2-3 weeks

2. **Higher Character Levels** (4-10)
   - THAC0 tables extend to level 10
   - Spell level 6-9 need testing
   - Monster scaling for high-level parties
   - Estimated: 1-2 weeks

3. **Fix Campaign System** (Option A: Complete It)
   - Debug overworld transitions
   - Implement hex map rendering
   - Complete faction system
   - Estimated: 6-9 weeks
   - Risk: High complexity, previous attempt failed

4. **Alternative: Simpler Features** (Option B: Skip Campaign)
   - Quest system (1-2 weeks)
   - NPC dialogue system (1-2 weeks)
   - Wilderness encounter tables (1 week)
   - Multiple dungeons/hand-crafted scenarios (2-3 weeks)

### 13.3 Campaign System Lessons

**Why It Failed:**
- Attempted too much scope at once (7 phases)
- UI required major refactoring (4-context system)
- Web UI hex map visualization too complex
- No incremental way to test in-game

**How to Approach It Better:**
1. **Start Minimal**: Single village + overworld map, no fancy visualization
2. **Add Incrementally**: Village → travel to dungeon → return to village
3. **Skip Fancy UI**: Use ASCII/text for hex map, not SVG/emoji
4. **Test Early**: Each feature should be playable within 1 week
5. **Focus on Mechanics**: Travel system before visualization

**If Continuing Campaign:**
- Branch from stable main (commit `3c55863`)
- Start fresh without old code
- Implement travel system FIRST (simplest piece)
- Add locations ONE at a time
- Skip weather/faction system initially
- Get basic overworld working before Web UI enhancements

---

## 14. FILE REFERENCE GUIDE

### Core Engine Files
- `aerthos/engine/game_state.py` (600+ lines) - Central coordinator
- `aerthos/engine/combat.py` (300+ lines) - THAC0 system
- `aerthos/engine/parser.py` (250+ lines) - Command parsing
- `aerthos/engine/time_tracker.py` (200+ lines) - Time/resources

### Entity Classes
- `aerthos/entities/character.py` (150 lines) - Base entity
- `aerthos/entities/player.py` (300+ lines) - Player characters + inventory
- `aerthos/entities/monster.py` (200+ lines) - Creatures with AI
- `aerthos/entities/party.py` (150 lines) - Party management

### Systems (25+ subsystems)
- `aerthos/systems/magic.py` - Spell casting (332 spells)
- `aerthos/systems/skills.py` - Thief skills
- `aerthos/systems/saving_throws.py` - Save mechanics
- `aerthos/systems/ability_modifiers.py` - Ability bonuses
- `aerthos/systems/monster_ai.py` - Monster targeting
- `aerthos/systems/monster_abilities.py` - Special attacks
- ... 20+ more

### World Building
- `aerthos/world/dungeon.py` - Single-level dungeons
- `aerthos/world/multilevel_dungeon.py` - Multi-level support
- `aerthos/world/room.py` - Room class
- `aerthos/world/encounter.py` - Combat/trap/puzzle encounters
- `aerthos/world/village.py` - Village system
- `aerthos/world/shop.py`, `inn.py`, `guild.py` - Services
- `aerthos/world/automap.py` - ASCII mapping

### Generation
- `aerthos/generator/dungeon_generator.py` - Room generation
- `aerthos/generator/multilevel_generator.py` - Multi-level generation
- `aerthos/generator/config.py` - Difficulty presets

### Storage/Persistence
- `aerthos/storage/session_manager.py` - Full game saves
- `aerthos/storage/character_roster.py` - Character database
- `aerthos/storage/party_manager.py` - Party storage
- `aerthos/storage/scenario_library.py` - Saved dungeons

### UI
- `main.py` (1519 lines) - CLI entry point
- `web_ui/app.py` (1938 lines) - Flask web server
- `aerthos/ui/character_creation.py` - Character builder
- `aerthos/ui/display.py` - Text formatting

### Data Files (~1.2 MB total)
- `aerthos/data/monsters.json` (269 KB) - 100+ creatures
- `aerthos/data/spells.json` (158 KB) - 332 spells
- `aerthos/data/ability_modifiers.json` (10 KB) - Ability tables
- `aerthos/data/monsters_enhanced.json` (410 KB) - Backup version
- Plus 20+ other data files (abilities, classes, races, equipment, etc.)

### Tests (~3500 lines)
- 27 test files in `tests/` directory
- 417 total tests, all passing
- Coverage of combat, magic, parser, storage, AI, and more

### Documentation (~30 files, 100+ KB)
- `CLAUDE.md` - Main development guide
- `README.md` - Player guide
- `API_REFERENCE.md` - Game systems documentation
- `CAMPAIGN_IMPLEMENTATION_PLAN.md` - Failed campaign work
- `docs/archive/` - Completed feature documentation (40+ files)
- `docs/players_handbook/` - AD&D 1e rules reference

---

## CONCLUSION

Aerthos is a **complete, functional AD&D 1e text adventure game** with:
- Solid core systems (100% tested)
- Rich content database (332 spells, 100+ monsters)
- Dual interfaces (CLI + Web UI)
- Persistent save system
- Extensible architecture

The **campaign system was attempted but abandoned** due to complexity. The code survives in a backup branch for future reference, but the main branch maintains a stable, playable core game.

**Future work** should focus on either:
1. **Completing simpler features** (quests, more classes, higher levels)
2. **Redesigning campaign** from scratch with minimal scope
3. **Expanding content** (more dungeons, monsters, spells, items)

The architecture is solid enough to support any of these directions without major refactoring.
