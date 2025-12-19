# AERTHOS TECHNICAL REFERENCE

**Comprehensive System Documentation for AD&D 1e Text Adventure**

*Last Updated: December 2025*
*Version: 2.0 - Campaign Complete*
*Test Status: 593/593 tests passing (631 with web tests)*

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Core Game Systems](#3-core-game-systems)
4. [Data Models & Schemas](#4-data-models--schemas)
5. [State Management](#5-state-management)
6. [Combat System](#6-combat-system)
7. [Magic System](#7-magic-system)
8. [Character System](#8-character-system)
9. [Campaign & Quest System](#9-campaign--quest-system)
10. [Persistence & Storage](#10-persistence--storage)
11. [CLI & Web UI Synchronization](#11-cli--web-ui-synchronization)
12. [Common Gotchas & Bug Patterns](#12-common-gotchas--bug-patterns)
13. [Testing Strategy](#13-testing-strategy)
14. [File Reference](#14-file-reference)

---

## 1. EXECUTIVE SUMMARY

### What is Aerthos?

Aerthos is a faithful recreation of AD&D 1st Edition mechanics as a single-player text adventure game. It features:

- **Full THAC0 combat system** with descending AC
- **Vancian magic** with spell memorization
- **10-episode campaign** ("The Serpent's Shadow")
- **11 character classes**, 4 races, 321 monsters, 333 spells
- **Dual interfaces**: CLI (`main.py`) and Web UI (`web_ui/app.py`)
- **5-tier persistence**: Quick saves, character roster, party manager, scenario library, session manager

### Key Statistics

| Metric | Value |
|--------|-------|
| Python Modules | 77 |
| JSON Data Files | 711 |
| Total Data Size | 25.6 MB |
| Tests | 593/593 passing (631 with web) |
| Character Classes | 11 |
| Playable Races | 4 |
| Campaign Episodes | 10 |
| Hand-Crafted Dungeons | 11 |
| Monsters | 321 |
| Spells | 333 |
| Side Quests | 20 |
| City Hubs | 5 |

### Technology Stack

- **Core**: Python 3.10+ (standard library only)
- **Web UI**: Flask 2.3+ (optional)
- **Data Format**: JSON
- **Testing**: Python unittest

---

## 2. ARCHITECTURE OVERVIEW

### 2.1 System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     ENTRY POINTS                             │
│         main.py (CLI)  |  web_ui/app.py (Web UI)            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                     GAME STATE                               │
│              engine/game_state.py                            │
│   • Central coordinator for ALL game systems                 │
│   • Command dispatch and execution                           │
│   • Combat, movement, exploration orchestration              │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬─────────────┐
        │              │              │             │
┌───────▼────┐  ┌─────▼──────┐  ┌──▼──────┐  ┌──▼───────┐
│  ENTITIES  │  │  SYSTEMS   │  │  WORLD  │  │ CAMPAIGN │
│  (Data)    │  │  (Logic)   │  │  (Map)  │  │ (Story)  │
├────────────┤  ├────────────┤  ├─────────┤  ├──────────┤
│ Player     │  │ Magic      │  │ Dungeon │  │ Episode  │
│ Character  │  │ Combat     │  │ Room    │  │ Campaign │
│ Monster    │  │ Skills     │  │ Encounter│ │ Hub      │
│ Party      │  │ Saves      │  │ Automap │  │ Quest    │
│ Items      │  │ Abilities  │  │ Village │  │ Manager  │
└────────────┘  └────────────┘  └─────────┘  └──────────┘
        │              │              │             │
        └──────────────┼──────────────┴─────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        │              │              │              │
┌───────▼────┐  ┌─────▼──────┐  ┌───▼────┐  ┌──────▼───┐
│  STORAGE   │  │ GENERATOR  │  │   UI   │  │   DATA   │
│ (Persist)  │  │ (Procedural)│ │(Display)│ │  (JSON)  │
├────────────┤  ├────────────┤  ├────────┤  ├──────────┤
│ Character  │  │ Dungeon    │  │ Create │  │ classes  │
│ Roster     │  │ Generator  │  │ Sheet  │  │ races    │
│ Party Mgr  │  │ Appendix A │  │ Display│  │ monsters │
│ Scenario   │  │ Multi-level│  │ Save   │  │ spells   │
│ Session    │  │ Scaling    │  │ System │  │ equipment│
└────────────┘  └────────────┘  └────────┘  └──────────┘
```

### 2.2 Data Flow

```
User Input
    │
    ▼
┌─────────────────┐
│     Parser      │  (engine/parser.py)
│ Natural Language│  Converts "attack orc" → Command object
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Game State    │  (engine/game_state.py)
│ Command Router  │  Routes to appropriate handler
└────────┬────────┘
         │
    ┌────┴────┐
    │ Combat? │───Yes──▶ Combat Resolver ──▶ XP Distribution
    └────┬────┘          (engine/combat.py)
         │No
    ┌────┴────┐
    │ Magic?  │───Yes──▶ Magic System ──▶ Spell Effects
    └────┬────┘          (systems/magic.py)
         │No
    ┌────┴────┐
    │Movement?│───Yes──▶ Room Navigation ──▶ Encounter Check
    └────┬────┘          (world/dungeon.py)
         │
         ▼
┌─────────────────┐
│  State Update   │  Update HP, inventory, position, time
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Display      │  Format and return response
└─────────────────┘
```

### 2.3 Key File Locations

| Component | Primary File | Lines | Purpose |
|-----------|--------------|-------|---------|
| Game State | `engine/game_state.py` | 85,185 | Central coordinator |
| Combat | `engine/combat.py` | 18,159 | THAC0 resolution |
| Magic | `systems/magic.py` | 121,595 | Spell system |
| Parser | `engine/parser.py` | 12,258 | Command parsing |
| Player | `entities/player.py` | 28,831 | Character class |
| Character Creation | `ui/character_creation.py` | 69,691 | Character builder |
| Dungeon Generator | `generator/dungeon_generator.py` | 31,889 | Procedural gen |

---

## 3. CORE GAME SYSTEMS

### 3.1 Game Loop

The fundamental game loop operates as follows:

```python
# Simplified game loop (actual implementation in main.py and game_state.py)
while game_state.is_active:
    # 1. Display current state
    display_room()
    display_party_status()

    # 2. Get and parse input
    user_input = get_input()
    command = parser.parse(user_input)

    # 3. Execute command
    result = game_state.execute_command(command)

    # 4. Check for triggered events
    if result.triggers_encounter:
        handle_encounter()

    # 5. Advance time
    time_tracker.advance_turn()

    # 6. Check resource depletion
    check_light_sources()
    check_hunger()

    # 7. Display result
    display_result(result)
```

### 3.2 Command System

**Available Commands** (30+ types):

| Category | Commands | Handler Location |
|----------|----------|------------------|
| Movement | `north`, `south`, `east`, `west`, `up`, `down`, `go` | `game_state.handle_movement()` |
| Combat | `attack`, `defend`, `wait` | `game_state.handle_combat()` |
| Magic | `cast`, `memorize`, `spells` | `systems/magic.py` |
| Items | `take`, `drop`, `use`, `equip`, `unequip`, `inventory` | `game_state.handle_item()` |
| Exploration | `look`, `search`, `open` | `game_state.handle_exploration()` |
| Character | `status`, `sheet`, `rest` | `game_state.handle_character()` |
| Navigation | `map`, `directions` | `world/automap.py` |
| Meta | `save`, `load`, `help`, `quit` | `game_state.handle_meta()` |
| Party | `formation` | `game_state.handle_party()` |

### 3.3 Time System

**Time Units**:
- **1 Turn** = 10 minutes (dungeon exploration unit)
- **1 Round** = 1 minute (combat unit)
- **1 Segment** = 6 seconds (spell casting unit)

**Time Tracking** (`engine/time_tracker.py`):
```python
class TimeTracker:
    turns_elapsed: int      # Total turns since game start
    hours_elapsed: int      # Calculated from turns

    def advance_turn(self):
        self.turns_elapsed += 1
        # Check light source depletion
        # Check hunger (every 8 hours)
        # Check wandering monster (15% on rest)
```

**Resource Depletion Rates**:
- Torch: 6 turns (1 hour)
- Lantern: 24 turns (4 hours)
- Rations: 1 per rest
- HP Recovery: 1 per day of rest
- Spell Restoration: 8 hours of rest

---

## 4. DATA MODELS & SCHEMAS

### 4.1 Character Data Structure

**Complete Character JSON Schema**:

```json
{
  "$schema": "character_v2",
  "id": "string (8 hex chars, unique)",
  "name": "string",
  "race": "Human|Elf|Dwarf|Halfling",
  "class": "Fighter|Cleric|Magic-User|Thief|Ranger|Paladin|Druid|Illusionist|Assassin|Monk|Bard",
  "level": "number (1-20)",
  "xp": "number",
  "alignment": "Lawful Good|Lawful Neutral|Lawful Evil|Neutral Good|True Neutral|Neutral Evil|Chaotic Good|Chaotic Neutral|Chaotic Evil",
  "created": "ISO 8601 timestamp",

  "hp_current": "number",
  "hp_max": "number",
  "ac": "number (descending, 10=unarmored, lower=better)",
  "thac0": "number (20 at level 1, decreases with level)",

  "strength": "number (3-18)",
  "strength_percentile": "number (0-100, 0=none, 18/xx for fighters only)",
  "dexterity": "number (3-18)",
  "constitution": "number (3-18)",
  "intelligence": "number (3-18)",
  "wisdom": "number (3-18)",
  "charisma": "number (3-18)",

  "copper_pieces": "number",
  "silver_pieces": "number",
  "electrum_pieces": "number",
  "gold_pieces": "number",
  "platinum_pieces": "number",

  "inventory": [
    {
      "name": "string",
      "type": "weapon|armor|consumable|treasure|light_source|container|magic_equipment|quest_item",
      "weight": "number (lbs)",
      "properties": {}
    }
  ],

  "equipped": {
    "weapon": "weapon object or null",
    "armor": "armor object or null",
    "shield": "shield object or null",
    "light": "light_source object or null",
    "gauntlets": "object or null",
    "ring": "object or null",
    "cloak": "object or null",
    "helmet": "object or null"
  },

  "spells_known": [
    {
      "name": "string",
      "level": "number (1-9)",
      "school": "string",
      "casting_time": "string",
      "range": "string",
      "duration": "string",
      "saving_throw": "string",
      "description": "string"
    }
  ],

  "spells_memorized": [
    {
      "level": "number (spell level)",
      "is_used": "boolean",
      "spell": "spell object"
    }
  ],

  "thief_skills": {
    "pick_pockets": "number (percentage)",
    "open_locks": "number",
    "find_remove_traps": "number",
    "move_silently": "number",
    "hide_in_shadows": "number",
    "hear_noise": "number",
    "climb_walls": "number",
    "read_languages": "number"
  },

  "conditions": ["poisoned", "paralyzed", "blinded", "etc"],
  "special_abilities": ["detect_evil", "lay_on_hands", "etc"]
}
```

### 4.2 Monster Data Structure

**Monster JSON Schema** (`aerthos/data/monsters.json`):

```json
{
  "monster_id": {
    "name": "string",
    "hit_dice": "string (e.g., '2d8', '4+1', '16d8')",
    "ac": "number (descending)",
    "thac0": "number",
    "damage": "string (e.g., '1d6', '2d8')",
    "size": "S|M|L",
    "movement": "number (ft/round)",
    "morale": "number (2-12)",
    "treasure_type": "string",
    "xp_value": "number",

    "special_abilities": ["regeneration", "level_drain", "paralysis", "etc"],
    "ai_behavior": "aggressive|defensive|flee_low_hp|intelligent",
    "alignment": "string",
    "magic_resistance": "number (percentage) or null",

    "num_attacks": "number",
    "special_attacks": "string description",
    "special_defenses": "string description",

    "intelligence": {
      "category": "Animal|Low|Semi|Average|High|Very High|Genius",
      "score_range": "string (e.g., '17-18')"
    },

    "frequency": {
      "description": "string",
      "percentage": "number"
    },

    "no_appearing": {
      "wilderness": {"min": "number", "max": "number"},
      "lair": {"min": "number", "max": "number"}
    },

    "pct_in_lair": "number (0-100)",

    "xp_formula": {
      "base_xp": "number",
      "xp_per_hp": "number",
      "dungeon_level": "number"
    }
  }
}
```

### 4.3 Spell Data Structure

**Spell JSON Schema** (`aerthos/data/spells.json`):

```json
{
  "spell_id": {
    "name": "string",
    "level": "number (1-9)",
    "school": "abjuration|conjuration|divination|enchantment|evocation|illusion|necromancy|transmutation",
    "casting_time": "string (e.g., '1 segment')",
    "range": "string (e.g., '60 feet', 'touch')",
    "duration": "string (e.g., '1 turn/level', 'instantaneous')",
    "area_of_effect": "string or null",
    "saving_throw": "None|Negates|Half|Special",
    "components": "standard|rare",
    "description": "string (game mechanics)",
    "class_availability": ["Magic-User", "Cleric", "Druid", "etc"]
  }
}
```

### 4.4 Dungeon Data Structure

**Dungeon JSON Schema** (`aerthos/data/dungeons/*.json`):

```json
{
  "name": "string",
  "description": "string",
  "theme": "string (ruins|cave|stronghold|temple|etc)",
  "levels": "number (1-3)",
  "start_room": "string (room_id)",

  "rooms": {
    "room_id": {
      "id": "string",
      "title": "string",
      "description": "string (narrative text)",
      "light_level": "bright|normal|dim|dark",

      "exits": {
        "north": "room_id or null",
        "south": "room_id or null",
        "east": "room_id or null",
        "west": "room_id or null",
        "up": "room_id or null",
        "down": "room_id or null"
      },

      "items": [
        {
          "id": "string",
          "name": "string",
          "type": "string",
          "properties": {}
        }
      ],

      "encounters": [
        {
          "id": "string",
          "type": "combat|trap|puzzle",
          "triggered": "boolean",
          "monsters": ["monster_id"],
          "description": "string"
        }
      ],

      "safe_rest": "boolean (true if party can rest here)",
      "special": "string (special room effects) or null"
    }
  },

  "bosses": {
    "boss_id": {
      "name": "string",
      "monster_id": "string",
      "location": "room_id",
      "unique_properties": {}
    }
  }
}
```

### 4.5 Campaign Data Structure

**Episode JSON Schema** (`aerthos/data/episodes/episode_XX.json`):

```json
{
  "$schema": "episode_v1",
  "id": "episode_01",
  "title": "string",
  "act": "number (1-10)",
  "recommended_level": "number",
  "hub_id": "string (city hub reference)",

  "intro_text": "string (narrative introduction)",

  "briefing": {
    "quest_giver": "string (NPC name)",
    "location": "string",
    "dialogue": "string"
  },

  "dungeon": {
    "type": "hand_crafted|procedural",
    "file": "string (path to dungeon JSON)",
    "name": "string",
    "theme": "string",
    "levels": "number",
    "boss": "string (boss name)"
  },

  "completion_criteria": {
    "type": "boss_defeated|objective_complete|item_retrieved",
    "target": "string"
  },

  "completion_text": "string (narrative conclusion)",

  "rewards": {
    "xp_bonus": "number",
    "gold_bonus": "number",
    "items": ["item_id"],
    "unlocks": ["episode_id"],
    "story_flags": ["flag_name"]
  },

  "rumors": ["string"],
  "prerequisites": ["episode_id"]
}
```

### 4.6 Save Game Structure

**Campaign Save** (`~/.aerthos/campaigns/*.json`):

```json
{
  "id": "UUID",
  "name": "campaign name",
  "party_id": "string",
  "current_episode_id": "string",
  "current_hub_id": "string",

  "completed_episodes": ["episode_id"],
  "unlocked_episodes": ["episode_id"],
  "unlocked_hubs": ["hub_id"],

  "story_flags": {
    "flag_name": "boolean"
  },

  "reputation": {
    "faction_name": "number (-100 to +100)"
  },

  "active_session_id": "string or null",
  "play_time_minutes": "number",

  "created_at": "ISO 8601",
  "last_played": "ISO 8601"
}
```

---

## 5. STATE MANAGEMENT

### 5.1 GameState Class

**Location**: `aerthos/engine/game_state.py`

The `GameState` class is the **central coordinator** for all game systems:

```python
class GameState:
    # Core state
    player: PlayerCharacter          # Single-player mode
    party: Party                     # Party mode (list of characters)
    dungeon: Dungeon                 # Current dungeon
    current_room: Room               # Current location
    current_level: int               # For multi-level dungeons

    # Combat state
    is_active: bool                  # Game running
    in_combat: bool                  # Currently in combat
    active_monsters: List[Monster]   # Monsters in current encounter
    current_encounter: Encounter     # Active encounter object

    # Campaign state
    episode_runner: EpisodeRunner    # Campaign quest tracking
    campaign: Campaign               # Campaign progress

    # Loaded data (from JSON files)
    game_data: dict                  # All loaded JSON data

    # Systems (injected dependencies)
    magic_system: MagicSystem
    time_tracker: TimeTracker
    skill_resolver: SkillResolver
    saving_throw_resolver: SavingThrowResolver
    narrator: Narrator
```

### 5.2 State Transitions

**Critical State Transitions**:

```
┌─────────────┐
│   MENU      │  (not in game)
└──────┬──────┘
       │ Start Game
       ▼
┌─────────────┐
│ EXPLORATION │  (in_combat = false)
└──────┬──────┘
       │ Encounter triggered
       ▼
┌─────────────┐
│   COMBAT    │  (in_combat = true, active_monsters > 0)
└──────┬──────┘
       │ All monsters defeated / party fled / party wiped
       ▼
┌─────────────┐
│ EXPLORATION │  or  │ GAME OVER │
└─────────────┘      └───────────┘
```

### 5.3 Command Dispatch

**Command routing in `game_state.execute_command()`**:

```python
def execute_command(self, command: Command) -> Result:
    # Validate command in current context
    if self.in_combat and command.type not in COMBAT_COMMANDS:
        return Result.error("You're in combat!")

    # Route to handler
    handlers = {
        'move': self.handle_movement,
        'attack': self.handle_attack,
        'cast': self.handle_cast,
        'take': self.handle_take,
        'equip': self.handle_equip,
        'unequip': self.handle_unequip,
        'use': self.handle_use,
        'drop': self.handle_drop,
        'look': self.handle_look,
        'search': self.handle_search,
        'rest': self.handle_rest,
        'inventory': self.handle_inventory,
        'status': self.handle_status,
        'map': self.handle_map,
        'save': self.handle_save,
        'help': self.handle_help,
        # ... 30+ command types
    }

    handler = handlers.get(command.type)
    if handler:
        return handler(command)
    else:
        return Result.error("Unknown command")
```

### 5.4 Web UI State Tracking

**CRITICAL**: Web UI tracks `character_ids` for persistence:

```python
# In web_ui/app.py
game_state.character_ids = [char.id for char in party.members]

# After each command, save party members to roster
def save_party_members():
    for i, char in enumerate(game_state.party.members):
        char_id = game_state.character_ids[i]
        roster.update_character(char_id, char.to_dict())
```

**Why this matters**: Without `character_ids` tracking, XP and inventory changes won't persist to the character roster when exiting the game.

---

## 6. COMBAT SYSTEM

### 6.1 THAC0 Attack Resolution

**Location**: `aerthos/engine/combat.py`

**Core Formula**:
```
target_number = attacker.THAC0 - defender.AC
roll = d20
hit = roll >= target_number
```

**Attack Roll Modifiers**:
- Strength bonus (melee)
- Dexterity bonus (ranged)
- Weapon magic bonus (+1, +2, etc.)
- Weapon proficiency (-4 if non-proficient)
- Special weapon bonuses (Dragon Slayer +3 vs dragons)

**Critical Hits/Misses**:
- Natural 20: Always hits, double damage
- Natural 1: Always misses

### 6.2 Damage Calculation

```python
def calculate_damage(attacker, defender, weapon):
    # Base damage by target size
    if defender.size in ['S', 'M']:
        base_damage = roll_dice(weapon.damage_sm)  # e.g., "1d8"
    else:
        base_damage = roll_dice(weapon.damage_l)   # e.g., "1d12"

    # Apply modifiers
    damage = base_damage
    damage += attacker.strength_damage_bonus
    damage += weapon.magic_bonus

    # Special weapon effects
    if weapon.special and defender.type in weapon.special_targets:
        damage += weapon.special_bonus

    return max(1, damage)  # Minimum 1 damage on hit
```

### 6.3 Combat Flow

```
1. Player initiates combat ("attack orc")
2. Check weapon proficiency
3. Roll d20 for attack
4. Calculate target number (THAC0 - AC)
5. Determine hit/miss/critical
6. Roll damage if hit
7. Apply damage to target
8. Check if target defeated
9. Monster counter-attack (if alive)
   - 30% chance of special ability instead
10. Check party status
11. Award XP if combat ends in victory
```

### 6.4 Monster AI

**AI Behaviors** (`systems/monster_ai.py`):

| Behavior | Description |
|----------|-------------|
| `aggressive` | Always attacks nearest target |
| `defensive` | Attacks only if attacked first |
| `flee_low_hp` | Flees when HP < 25% |
| `intelligent` | Targets weakest party member, uses abilities strategically |
| `pack_tactics` | Coordinates with other monsters |

**Special Ability Trigger**: 30% chance per round for monster to use special ability instead of normal attack.

### 6.5 Formation Combat

**Party Formation**:
- Front line: Primary melee targets (70% targeting chance)
- Back line: Protected from melee (30% targeting chance)

```python
# Formation targeting in combat.py
def select_target(monsters_perspective=True):
    front_line = [c for c in party if c.formation == 'front']
    back_line = [c for c in party if c.formation == 'back']

    if random.random() < 0.70 and front_line:
        return random.choice(front_line)
    elif back_line:
        return random.choice(back_line)
    else:
        return random.choice(front_line)
```

### 6.6 XP Distribution

**XP Award Calculation**:
```python
def award_xp(party, monsters_defeated):
    total_xp = sum(monster.xp_value for monster in monsters_defeated)

    # Optional: Divide by party size
    # xp_per_member = total_xp // len(party)

    # Current implementation: Full XP to each member
    for character in party.members:
        character.xp += total_xp
        check_level_up(character)
```

---

## 7. MAGIC SYSTEM

### 7.1 Vancian Magic Model

**Location**: `aerthos/systems/magic.py`

**Core Concept**: Spells must be **memorized** before casting. Each memorized spell can be cast **once**, then the slot is expended. Slots restore after **8 hours of rest**.

### 7.2 Spell Slot Structure

```python
class SpellSlot:
    level: int          # Spell level (1-9)
    spell: Spell        # The memorized spell
    is_used: bool       # True if already cast
```

**Slots Per Level** (Magic-User example):
```
Level 1: [1]                    # 1 first-level spell
Level 2: [2]                    # 2 first-level spells
Level 3: [2, 1]                 # 2 first, 1 second
Level 4: [3, 2]                 # 3 first, 2 second
Level 5: [4, 2, 1]              # 4 first, 2 second, 1 third
...
```

### 7.3 Spell Casting Flow

```
1. Player: "cast magic missile at orc"
2. Parser: Extract spell name and target
3. Validation:
   - Is spell known? (in spells_known)
   - Is spell memorized? (in spells_memorized)
   - Is slot unused? (is_used == false)
   - Is target valid? (harmful spell = monster, beneficial = party)
4. Execute spell effect
5. Mark slot as used (is_used = true)
6. Apply saving throw if applicable
7. Apply damage/effect to target
```

### 7.4 Spell Categories

| Category | Target | Examples |
|----------|--------|----------|
| Damage | Monsters | Magic Missile, Fireball, Lightning Bolt |
| Healing | Party | Cure Light Wounds, Heal |
| Control | Monsters | Hold Person, Web, Sleep |
| Buff | Party | Bless, Haste, Protection from Evil |
| Debuff | Monsters | Slow, Curse |
| Utility | Any | Detect Magic, Light, Knock |

### 7.5 Saving Throws for Spells

```python
def apply_spell_with_save(spell, target):
    if spell.saving_throw == 'None':
        return apply_full_effect(spell, target)

    # Roll saving throw
    save_roll = roll_d20()
    save_target = target.saves[spell.save_category]

    if save_roll <= save_target:  # Save succeeds
        if spell.saving_throw == 'Negates':
            return "Target resisted the spell"
        elif spell.saving_throw == 'Half':
            return apply_half_effect(spell, target)
    else:  # Save fails
        return apply_full_effect(spell, target)
```

### 7.6 Spell Restoration

**Rest Requirements**:
- 8 hours of uninterrupted rest
- Must be in a safe room (safe_rest = true)
- Consumes 1 ration per character
- 15% chance of wandering monster interrupt

```python
def handle_rest(self):
    if not self.current_room.safe_rest:
        return "This area is too dangerous to rest"

    # Check for wandering monster
    if random.random() < 0.15:
        return self.trigger_wandering_monster()

    # Restore spells
    for slot in character.spells_memorized:
        slot.is_used = False

    # Restore HP (1 per day, or full with healing)
    character.hp_current = min(character.hp_current + 1, character.hp_max)

    # Advance time
    self.time_tracker.advance_hours(8)
```

---

## 8. CHARACTER SYSTEM

### 8.1 Character Classes

**11 Classes** with unique mechanics:

| Class | Hit Die | THAC0 Progression | Special Abilities |
|-------|---------|-------------------|-------------------|
| Fighter | d10 | -1/level | Multiple attacks at high level |
| Ranger | d8 | -1/level | Tracking, dual-wield, limited spells |
| Paladin | d10 | -1/level | Detect Evil, Lay on Hands, Turn Undead |
| Cleric | d8 | -2/3 levels | Divine spells, Turn Undead |
| Druid | d8 | -2/3 levels | Nature spells, shapeshift |
| Magic-User | d4 | -1/3 levels | Arcane spells |
| Illusionist | d4 | -1/3 levels | Illusion spells |
| Thief | d6 | -2/3 levels | Thief skills, backstab |
| Assassin | d6 | -2/3 levels | Thief skills, assassination |
| Monk | d4 | -2/3 levels | Unarmed combat, special abilities |
| Bard | d6 | Variable | Jack of all trades, inspiration |

### 8.2 Races

**4 Races** with modifiers:

| Race | STR | DEX | CON | INT | WIS | CHA | Special |
|------|-----|-----|-----|-----|-----|-----|---------|
| Human | - | - | - | - | - | - | Unlimited level advancement |
| Elf | - | +1 | -1 | - | - | - | Infravision, resist sleep/charm |
| Dwarf | - | - | +1 | - | - | -1 | Infravision, resist poison/magic |
| Halfling | -1 | +1 | - | - | - | - | Saving throw bonuses |

### 8.3 Ability Score System

**Six Abilities** (3-18 range):

| Ability | Primary Effects |
|---------|-----------------|
| Strength | Melee to-hit, melee damage, encumbrance |
| Dexterity | AC bonus, ranged to-hit, thief skills |
| Constitution | HP bonus per level, system shock |
| Intelligence | Bonus languages, magic-user spells |
| Wisdom | Spell bonus (clerics), mental saves |
| Charisma | NPC reactions, max hirelings |

**Exceptional Strength** (Fighters only):
- STR 18/01-50: +1 to-hit, +3 damage
- STR 18/51-75: +2 to-hit, +3 damage
- STR 18/76-90: +2 to-hit, +4 damage
- STR 18/91-99: +2 to-hit, +5 damage
- STR 18/00: +3 to-hit, +6 damage

### 8.4 Experience & Leveling

**XP Tables** (per class in `level_progression.json`):

```
Fighter: 0 → 2,000 → 4,000 → 8,000 → 16,000 → ...
Magic-User: 0 → 2,500 → 5,000 → 10,000 → 22,500 → ...
Cleric: 0 → 1,500 → 3,000 → 6,000 → 13,000 → ...
Thief: 0 → 1,250 → 2,500 → 5,000 → 10,000 → ...
```

**Level-Up Process**:
```python
def check_level_up(character):
    xp_required = get_xp_for_level(character.class, character.level + 1)

    if character.xp >= xp_required:
        character.level += 1

        # Roll HP
        hp_roll = roll_dice(character.hit_die)
        hp_roll += character.con_hp_bonus
        hp_roll = max(1, hp_roll)  # Minimum 1 HP per level
        character.hp_max += hp_roll
        character.hp_current += hp_roll

        # Update THAC0
        character.thac0 = calculate_thac0(character.class, character.level)

        # Update spell slots (if caster)
        if is_spellcaster(character):
            update_spell_slots(character)

        # Update thief skills (if thief)
        if character.class == 'Thief':
            update_thief_skills(character)
```

### 8.5 Saving Throws

**5 Categories**:

| Category | Typical Triggers |
|----------|------------------|
| Poison/Death | Poison attacks, death magic |
| Rod/Staff/Wand | Magical device effects |
| Petrification/Paralysis | Medusa gaze, ghoul touch |
| Breath Weapon | Dragon breath, acid spray |
| Spell | Direct magical attacks |

**Roll Mechanic**: d20, succeed if roll <= save value

**Save Progression** (lower = better):
```
Fighter 1: 14/15/16/17/17
Fighter 5: 13/14/15/16/16
Fighter 10: 11/12/13/13/14
```

### 8.6 Thief Skills

**8 Percentile Skills**:

| Skill | Level 1 Base | Per Level |
|-------|--------------|-----------|
| Pick Pockets | 30% | +5% |
| Open Locks | 25% | +5% |
| Find/Remove Traps | 20% | +5% |
| Move Silently | 15% | +5% |
| Hide in Shadows | 10% | +5% |
| Hear Noise | 10% | +5% |
| Climb Walls | 85% | +2% |
| Read Languages | 0% | +5% (level 4+) |

**Modifiers**:
- Race adjustments (Elf +5% Hide, Dwarf +10% Open Locks, etc.)
- Dexterity adjustments
- Armor penalties (leather = no penalty, heavier = penalties)

---

## 9. CAMPAIGN & QUEST SYSTEM

### 9.1 Campaign Structure

**"The Serpent's Shadow"** - 10 Episodes across 5 City Hubs:

| Episode | Title | Hub | Dungeon | Recommended Level |
|---------|-------|-----|---------|-------------------|
| 1 | Into the Caves | Oakhaven | Goblin Caves | 1 |
| 2 | Sewer Secrets | Oakhaven | Oakhaven Sewers | 2 |
| 3 | The Merchant's Scheme | Oakhaven | Silas Warehouse | 2-3 |
| 4 | Beneath the Mountains | Ironfast | Duergar Hold | 3-4 |
| 5 | Temple of Scales | Eldoria | Serpent Temple | 4-5 |
| 6 | The Sunken Temple | Coastal Haven | Sunken Temple | 5-6 |
| 7 | Drowned Ruins | Coastal Haven | Drowned Ruins | 6-7 |
| 8 | Elemental Chaos | Mires Edge | Elemental Chaos | 7-8 |
| 9 | The Keep of Kaldor | Ironfast | Keep of Kaldor | 8-9 |
| 10 | Scorched Earth | Eldoria | Scorched Fortress | 9-10 |

### 9.2 Episode Runner

**Location**: `aerthos/campaign/episode_runner.py`

```python
class EpisodeRunner:
    episode: Episode            # Current episode
    objectives: List[Objective] # Quest objectives
    completed_objectives: set   # Tracking

    def check_objective_completion(self, event):
        """Called after every game event to check quest progress"""
        for objective in self.objectives:
            if objective.matches(event):
                self.completed_objectives.add(objective.id)
                self.notify_objective_complete(objective)

        if all(obj.id in self.completed_objectives for obj in self.required_objectives):
            self.episode_complete()
```

### 9.3 Quest Objectives

**Objective Types**:

| Type | Trigger | Example |
|------|---------|---------|
| `kill_monster` | Monster defeated | "Kill the Goblin Chieftain" |
| `collect_item` | Item picked up | "Find the Ancient Scroll" |
| `search_room` | Room searched | "Search the throne room" |
| `enter_room` | Room entered | "Reach the inner sanctum" |
| `talk_npc` | NPC dialogue | "Speak with Elder Mira" |

### 9.4 Side Quests

**20 Side Quests** (`aerthos/data/side_quests.json`):

- Available independently of main story
- Provide additional XP/gold/items
- Some unlock unique rewards
- Contribute to reputation

**Side Quest Structure**:
```json
{
  "quest_id": {
    "title": "Scout Elimination",
    "description": "Eliminate goblin scouts before they warn others",
    "episode_id": "episode_01",
    "trigger_type": "enter_room",
    "trigger_conditions": {"room_id": "entrance"},
    "objectives": [
      {"type": "kill_monster", "target": "goblin", "count": 3}
    ],
    "rewards": {
      "xp": 250,
      "gold": 50,
      "reputation": 5
    }
  }
}
```

### 9.5 City Hubs

**5 City Hubs** with services:

| Service | Purpose | Mechanics |
|---------|---------|-----------|
| Shop | Buy/sell equipment | Price modifier per city |
| Inn | Rest and recover | Cost per night, rumors |
| Temple | Healing, resurrection | Service costs by spell level |
| Guild | Side quests, hirelings | Reputation-gated content |

**Hub Progression**:
- Oakhaven: Starting hub (Episode 1-3)
- Ironfast Outpost: Dwarven stronghold (Episode 4, 9)
- Eldoria: Ancient city (Episode 5, 10)
- Coastal Haven: Port town (Episode 6-7)
- Mires Edge: Swamp settlement (Episode 8)

### 9.6 Reputation System

**Faction Tracking**:
```python
reputation = {
    "serpent_eye_cult": -100,  # Always enemy
    "bloodfang_orcs": -50,     # Initially hostile
    "ironfast_dwarves": 0,     # Neutral
    "mires_edge_folk": 10,     # Slightly friendly
    "silvan_concordance": 25,  # Friendly
}
```

**Reputation Effects** (planned):
- Shop price modifiers
- Quest availability
- NPC reactions
- Multiple endings

---

## 10. PERSISTENCE & STORAGE

### 10.1 Storage Hierarchy

**5-Tier Persistence System**:

```
┌─────────────────────────────────────────┐
│ TIER 1: Quick Save                       │
│ Location: ~/.aerthos/saves/quick_save.json│
│ Purpose: Single-slot save during play    │
├─────────────────────────────────────────┤
│ TIER 2: Character Roster                 │
│ Location: ~/.aerthos/characters/         │
│ Purpose: Persistent character database   │
├─────────────────────────────────────────┤
│ TIER 3: Party Manager                    │
│ Location: ~/.aerthos/parties/            │
│ Purpose: Saved party configurations      │
├─────────────────────────────────────────┤
│ TIER 4: Scenario Library                 │
│ Location: ~/.aerthos/scenarios/          │
│ Purpose: Saved/generated dungeons        │
├─────────────────────────────────────────┤
│ TIER 5: Session Manager                  │
│ Location: ~/.aerthos/sessions/           │
│ Purpose: Full game state snapshots       │
└─────────────────────────────────────────┘
```

### 10.2 Character Roster

**Location**: `aerthos/storage/character_roster.py`

**Operations**:
- `create_character(data)` → Returns character ID
- `get_character(id)` → Returns character dict
- `update_character(id, data)` → Updates character
- `delete_character(id)` → Removes character
- `list_characters()` → Returns all characters

**File Format**: `~/.aerthos/characters/{name}_{id}.json`

### 10.3 Party Manager

**Location**: `aerthos/storage/party_manager.py`

**Party Structure**:
```json
{
  "id": "c0dd5d91",
  "name": "Guardians",
  "character_ids": ["char1", "char2", "char3", "char4"],
  "formation": ["front", "front", "back", "back"],
  "size": 4,
  "created": "2025-12-19T10:30:00"
}
```

### 10.4 Session Manager

**Location**: `aerthos/storage/session_manager.py`

**Session State**:
```json
{
  "id": "session_uuid",
  "name": "Session Name",
  "party_id": "party_id",
  "dungeon_id": "dungeon_id",
  "current_room": "room_id",
  "current_level": 1,
  "time": {"turns": 45, "hours": 7},
  "explored_rooms": ["room1", "room2"],
  "defeated_encounters": ["enc1", "enc2"],
  "collected_items": ["item1"],
  "party_state": [/* character snapshots */],
  "created": "timestamp",
  "last_played": "timestamp"
}
```

### 10.5 Data Directory Structure

```
~/.aerthos/
├── saves/
│   └── quick_save.json
├── characters/
│   ├── thorin_a1b2c3d4.json
│   ├── elara_e5f6g7h8.json
│   └── archive/
│       └── deleted_characters/
├── parties/
│   ├── guardians_c0dd5d91.json
│   └── heroes_d1e2f3g4.json
├── scenarios/
│   ├── custom_dungeon_1.json
│   └── generated_easy_1.json
├── sessions/
│   ├── campaign_session_1.json
│   └── quickplay_session_1.json
└── campaigns/
    └── serpents_shadow_active.json
```

---

## 11. CLI & WEB UI SYNCHRONIZATION

### 11.1 Architecture Principle

**CRITICAL**: Both CLI (`main.py`) and Web UI (`web_ui/app.py`) are **thin wrappers** around the same core engine (`aerthos/` modules).

```
┌─────────────────┐     ┌─────────────────┐
│   main.py       │     │  web_ui/app.py  │
│   (CLI)         │     │   (Flask)       │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └──────────┬────────────┘
                    │
         ┌──────────▼──────────┐
         │   aerthos/ modules   │
         │   (Core Engine)      │
         └─────────────────────┘
```

### 11.2 Synchronization Points

**When modifying these areas, BOTH UIs must be updated**:

| Area | CLI Location | Web UI Location |
|------|--------------|-----------------|
| Dungeon Generation | `main.py:150-200` | `web_ui/app.py:900-950` |
| Character Creation | `main.py:300-400` | `web_ui/app.py:400-600` |
| Game State Init | `main.py:100-150` | `web_ui/app.py:700-800` |
| Command Execution | Uses GameState directly | `/api/command` endpoint |
| Save/Load | Uses SaveSystem | `/api/save`, `/api/load` |
| Session Management | Uses SessionManager | `/api/exit_session` |

### 11.3 API Contract

**Endpoint Response Structures:**

`/api/new_game` (POST):
```python
{
    'success': bool,
    'session_id': str,        # Unique session identifier (required for subsequent calls)
    'message': str,
    'state': { ... }          # Game state JSON (see below)
}
```

`/api/command` (POST):
```python
# Request: {'session_id': str, 'command': str}
# Success (200):
{'success': True, 'message': str, 'state': { ... }}
# Invalid session (404):
{'success': False, 'error': 'No active game'}
# Bad JSON (400):
{'success': False, 'error': str}
```

**Game State JSON Structure** (DO NOT BREAK):

```python
{
    'room': {
        'id': str,
        'title': str,
        'description': str,
        'exits': dict,
        'light_level': str,
        'items': list
    },
    'party': [{
        'name': str,
        'class': str,
        'race': str,
        'level': int,
        'hp': int,
        'hp_max': int,
        'ac': int,
        'thac0': int,
        'xp': int,
        'gold': int,
        'is_alive': bool,
        'inventory': list,
        'equipped': dict
    }],
    'in_combat': bool,
    'active_monsters': list,
    'available_spells': list,
    'time': {
        'turns': int,
        'hours': int
    },
    'map': {
        'rooms': dict
    }
}
```

### 11.4 Safe vs Dangerous Operations

**SAFE Operations**:
- ✅ Adding NEW fields to JSON response
- ✅ Adding NEW optional fields
- ✅ Changing field VALUES (same type)

**DANGEROUS Operations**:
- ❌ Removing fields → breaks Web UI
- ❌ Renaming fields → breaks Web UI
- ❌ Changing field types → breaks Web UI

### 11.5 Synchronization Workflow

**When changing core functions**:

```bash
# 1. Find all callers
grep -n "function_name" main.py web_ui/app.py

# 2. Update BOTH files with identical changes

# 3. Test CLI
python3 main.py

# 4. Test Web UI
python3 web_ui/app.py
# Open http://localhost:5000

# 5. Run full test suite
python3 run_tests.py --no-web
```

---

## 12. COMMON GOTCHAS & BUG PATTERNS

### 12.1 Spell Slot Bugs

**Problem**: Spell slots not assigned correctly during character creation.

**Root Cause**: Loop variable shadowing in `ui/character_creation.py`:

```python
# BUG: Using wrong variable in inner loop
for spell_level in range(1, max_spell_level + 1):
    for i in range(slots_per_level[spell_level - 1]):
        # BUG: Using 'spell_level' when should use 'i'
        slot = SpellSlot(level=spell_level, spell=None, is_used=False)
```

**Fix**: Ensure correct variable usage and bounds checking.

### 12.2 XP Persistence in Web UI

**Problem**: XP gained during session doesn't save to character roster.

**Root Cause**: Web UI not tracking `character_ids` for roster persistence.

**Fix**: Track character IDs and save after each command:

```python
# In web_ui/app.py after creating party
game_state.character_ids = [char.id for char in party.members]

# After each command
for i, char in enumerate(game_state.party.members):
    roster.update_character(game_state.character_ids[i], char.to_dict())
```

### 12.3 Multi-Level Dungeon Generator Parameters

**Problem**: Web UI crashes with "unexpected keyword argument 'base_config'".

**Root Cause**: Generator signature changed but only CLI was updated.

**Fix**: Always update BOTH UIs when changing core function signatures.

### 12.4 Item Creation Inconsistencies

**Problem**: Items created differently in CLI vs Web UI.

**Pattern**: Both UIs must use identical item creation:

```python
# CORRECT: Use factory method
item = Item.from_dict(item_data)

# WRONG: Create differently in each UI
item = Item(name=..., type=..., ...)  # Different in each UI
```

### 12.5 Formation Not Persisting

**Problem**: Party formation resets after load.

**Root Cause**: Formation stored on Party object but not serialized.

**Fix**: Include formation in party serialization:

```python
def to_dict(self):
    return {
        'character_ids': self.character_ids,
        'formation': self.formation,  # MUST include
        'size': self.size
    }
```

### 12.6 Monster Abilities Not Triggering

**Problem**: Special abilities never trigger in combat.

**Root Cause**: AI check happens but ability execution fails silently.

**Fix**: Add error handling and logging:

```python
def monster_turn(self, monster):
    if random.random() < 0.30 and monster.special_abilities:
        ability = random.choice(monster.special_abilities)
        try:
            self.execute_ability(monster, ability)
        except Exception as e:
            logging.error(f"Ability {ability} failed: {e}")
            self.monster_normal_attack(monster)
```

### 12.7 Encounter Not Clearing

**Problem**: Defeated monsters reappear when re-entering room.

**Root Cause**: Encounter completion not persisted to session state.

**Fix**: Mark encounter as completed in dungeon state:

```python
def complete_encounter(self, encounter_id):
    self.dungeon.rooms[self.current_room.id].encounters[encounter_id].triggered = True
    self.dungeon.rooms[self.current_room.id].encounters[encounter_id].completed = True
```

### 12.8 Saving Throw Resolution

**Problem**: Saving throws always fail or always succeed.

**Root Cause**: Comparison direction reversed.

**AD&D 1e Rule**: Roll d20, succeed if roll <= save value (lower is better).

```python
# CORRECT
save_succeeds = roll <= character.saves[category]

# WRONG (common mistake)
save_succeeds = roll >= character.saves[category]
```

### 12.9 Rest Not Restoring Spells

**Problem**: Spells don't restore after rest.

**Root Cause**: `is_used` flag not reset.

**Fix**: Explicitly reset all spell slots:

```python
def restore_spells(self, character):
    for slot in character.spells_memorized:
        slot.is_used = False
```

### 12.10 Character Death Not Handled

**Problem**: Dead character can still act.

**Fix**: Check `is_alive` before all character actions:

```python
def execute_character_action(self, character, action):
    if not character.is_alive:
        return Result.error(f"{character.name} is dead and cannot act")
    # ... rest of action
```

---

## 13. TESTING STRATEGY

### 13.1 Test Categories

**38 Test Modules** organized by system:

| Category | Tests | Coverage |
|----------|-------|----------|
| Combat | 45 | THAC0, damage, crits |
| Magic | 38 | Spell casting, slots, effects |
| Character | 52 | Creation, leveling, saves |
| Parser | 28 | Command parsing |
| Dungeon | 35 | Generation, navigation |
| Campaign | 67 | Episodes, quests |
| Storage | 43 | Save/load, roster |
| Integration | 89 | End-to-end scenarios |
| Web API | 44 | Flask endpoints |

### 13.2 Running Tests

```bash
# All tests (recommended)
python3 run_tests.py --no-web

# Specific categories
python3 run_tests.py --unit          # Core systems
python3 run_tests.py --integration   # End-to-end
python3 run_tests.py --web           # Flask API (requires Flask)

# Verbose output
python3 run_tests.py --no-web --verbose

# Single test file
python3 -m unittest tests.test_combat -v
```

### 13.3 Testing Workflow

**MANDATORY Before/After Any Change**:

1. **BEFORE changes**: `python3 run_tests.py --no-web` (establish baseline)
2. **Make changes**
3. **AFTER changes**: `python3 run_tests.py --no-web` (verify no regressions)
4. **If tests fail**: Fix code OR update tests if behavior intentionally changed
5. **Only commit when all 593 tests pass** (or 631 with web tests)

### 13.4 Key Test Files

| Test File | Purpose |
|-----------|---------|
| `test_combat.py` | THAC0, damage, critical hits |
| `test_magic_functionality.py` | Spell casting, memorization |
| `test_game_state.py` | State transitions, commands |
| `test_campaign_playthrough.py` | Full campaign simulation |
| `test_integration.py` | End-to-end scenarios |
| `test_storage.py` | Save/load operations |
| `test_quest_manager.py` | Quest triggers, completion |
| `test_xp_calculation.py` | XP awards, leveling |
| `test_armor_system.py` | AC calculations |

---

## 14. FILE REFERENCE

### 14.1 Core Engine Files

| File | Lines | Purpose |
|------|-------|---------|
| `engine/game_state.py` | 85,185 | Central game coordinator |
| `engine/combat.py` | 18,159 | THAC0 combat resolution |
| `engine/parser.py` | 12,258 | Natural language command parser |
| `engine/time_tracker.py` | 8,161 | Turn/time management |

### 14.2 Entity Files

| File | Lines | Purpose |
|------|-------|---------|
| `entities/player.py` | 28,831 | PlayerCharacter class |
| `entities/character.py` | 6,753 | Base Character class |
| `entities/monster.py` | 3,868 | Monster entities |
| `entities/party.py` | 7,492 | Party management |
| `entities/magic_items.py` | 14,144 | Magic item system |

### 14.3 System Files

| File | Lines | Purpose |
|------|-------|---------|
| `systems/magic.py` | 121,595 | Vancian magic system |
| `systems/saving_throws.py` | 12,747 | 5-category saves |
| `systems/skills.py` | 8,678 | Thief skill system |
| `systems/encounters.py` | 16,957 | Monster encounters |
| `systems/treasure.py` | 23,766 | Treasure generation |
| `systems/traps.py` | 17,008 | Trap mechanics |

### 14.4 World Files

| File | Lines | Purpose |
|------|-------|---------|
| `world/dungeon.py` | 6,780 | Single-level dungeons |
| `world/multilevel_dungeon.py` | 14,058 | Multi-level dungeons |
| `world/room.py` | 7,633 | Room entities |
| `world/automap.py` | 8,477 | Auto-mapping display |
| `world/village.py` | 7,031 | City hub system |

### 14.5 Campaign Files

| File | Lines | Purpose |
|------|-------|---------|
| `campaign/campaign.py` | 7,627 | Campaign definition |
| `campaign/episode_runner.py` | 16,184 | Episode execution |
| `campaign/quest_manager.py` | 8,639 | Quest tracking |
| `campaign/city_hub.py` | 9,824 | Hub management |

### 14.6 Storage Files

| File | Lines | Purpose |
|------|-------|---------|
| `storage/character_roster.py` | 23,021 | Character persistence |
| `storage/party_manager.py` | 9,517 | Party persistence |
| `storage/scenario_library.py` | 11,928 | Dungeon library |
| `storage/session_manager.py` | 9,238 | Session persistence |

### 14.7 Data Files

| File | Size | Contents |
|------|------|----------|
| `data/classes.json` | 10,160 lines | 11 character classes |
| `data/races.json` | 9,862 lines | 4 playable races |
| `data/monsters.json` | 15,121 lines | 321 monsters |
| `data/spells.json` | 15,121 lines | 333 spells |
| `data/equipment.json` | 6,209 lines | Equipment items |
| `data/side_quests.json` | 638 lines | 20 side quests |

---

## APPENDIX A: Quick Reference Card

### THAC0 Combat

```
Hit if: d20 roll >= (THAC0 - target AC)
Natural 20 = Critical hit (double damage)
Natural 1 = Critical miss (always misses)
```

### Saving Throws

```
Succeed if: d20 roll <= save value
Categories: Poison, Rod/Staff/Wand, Petrify/Paralyze, Breath, Spell
```

### Spell Slots

```
Memorize → Cast (slot used) → Rest 8 hours → Restore
```

### AC Scale

```
10 = Unarmored
8 = Leather
6 = Chain
4 = Plate
2 = Plate + Shield
0 = Plate + Shield + Magic
-5 = Exceptional
```

### XP Distribution

```
Full XP to each party member
Check level-up after each combat
```

### Test Command

```bash
python3 run_tests.py --no-web  # ALWAYS run before and after changes
```

---

## APPENDIX B: Development Checklist

### Before Starting Work

- [ ] Read relevant sections of this document
- [ ] Run `python3 run_tests.py --no-web` (baseline)
- [ ] Check `ROADMAP.md` for current priorities

### During Development

- [ ] Follow patterns in existing code
- [ ] Update BOTH CLI and Web UI if changing core
- [ ] Check constants in `aerthos/constants.py`
- [ ] No hardcoded paths or magic numbers

### Before Committing

- [ ] Run `python3 run_tests.py --no-web` (all pass)
- [ ] Test CLI: `python3 main.py`
- [ ] Test Web UI if applicable: `python3 web_ui/app.py`
- [ ] Update documentation if needed

---

**Document Maintained By**: Claude Code
**Last Review**: December 2025
**Next Review**: As needed when systems change
