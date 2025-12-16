# Spell Slot Management Scripts

This directory contains two scripts for managing character spell slots. Both scripts create backups before modifying files.

## Scripts Overview

### 1. `reset_characters.py` - Character Health & Spell Reset

**Purpose:** Reset characters to a "fresh" state after a long rest or for testing.

**What it does:**
- ✓ **Always:** Restores HP to maximum
- ✓ **Always:** Restores spent spell slots (clears `is_used` flags)
- ✓ **Optional:** Clears memorized spells from slots (**keeps slot structure**)
- ✓ **Optional:** Clears conditions (poisoned, diseased, etc.)

**Important:** `--clear-spells` empties the spell slots but **preserves the slot structure**. Characters will still have the correct number of empty slots available for memorizing new spells.

**Usage Examples:**

```bash
# Basic reset (HP + restore spent spells):
python3 scripts/reset_characters.py

# Full long rest (HP + restore spells + clear conditions):
python3 scripts/reset_characters.py --clear-conditions

# Complete wipe (HP + empty all slots + clear conditions):
python3 scripts/reset_characters.py --clear-spells --clear-conditions

# Dry run (see what would change):
python3 scripts/reset_characters.py --dry-run

# Process specific file:
python3 scripts/reset_characters.py --file ~/.aerthos/characters/gandalf.json

# Process only character files (skip saves and parties):
python3 scripts/reset_characters.py --characters-only
```

**Options:**
- `--clear-spells` - Clear memorized spells (keeps empty slots)
- `--clear-conditions` - Remove all status conditions
- `--saves-only` - Only process save files
- `--characters-only` - Only process character files
- `--parties-only` - Only process party files
- `--file <path>` - Process specific file
- `--no-backup` - Skip creating backups (not recommended)
- `--dry-run` - Preview changes without modifying files

---

### 2. `fix_character_spell_slots.py` - Spell Slot Correction

**Purpose:** Fix spell slots to match character class and level (e.g., after leveling up or importing characters).

**What it does:**
- ✓ Checks current slots against correct slots for class/level
- ✓ Adds missing slots (e.g., character leveled up)
- ✓ Removes excess slots (e.g., non-caster has slots)
- ✓ **Preserves memorized spells where possible**

**When to use:**
- After manually editing character files
- After importing characters from other sources
- After leveling up characters outside the game
- If spell slots seem incorrect for character level

**Usage:**

```bash
# Fix all character, save, and party files:
python3 scripts/fix_character_spell_slots.py

# The script will:
# - Check all files in ~/.aerthos/saves/
# - Check all files in ~/.aerthos/characters/
# - Check all files in ~/.aerthos/parties/
# - Create timestamped backups of modified files
# - Preserve memorized spells when adjusting slots
```

**Example Output:**

```
Processing: /home/user/.aerthos/characters/gandalf.json
  Gandalf: Level 5 Magic-User
    Current slots: {1: 2}
    Correct slots: {1: 4, 2: 2, 3: 1}
    ✓ Adjusted to 7 slots, preserved 2 memorized spell(s)
  ✓ Backup created: gandalf.json.20231215_143022.bak
  ✓ Fixed and saved
```

---

## Correct Spell Slot Counts by Class and Level

### Magic-User

| Level | Spell Levels (1st, 2nd, 3rd, 4th, 5th, 6th, 7th, 8th, 9th) |
|-------|-----------------------------------------------------------|
| 1     | 1                                                         |
| 2     | 2                                                         |
| 3     | 2, 1                                                      |
| 4     | 3, 2                                                      |
| 5     | 4, 2, 1                                                   |
| 6     | 4, 2, 2                                                   |
| 7     | 4, 3, 2, 1                                                |
| 8     | 4, 3, 3, 2                                                |
| 9     | 4, 3, 3, 2, 1                                             |
| 10    | 4, 4, 3, 2, 2                                             |

### Cleric

| Level | Spell Levels (1st, 2nd, 3rd, 4th, 5th, 6th, 7th) |
|-------|--------------------------------------------------|
| 1     | 1                                                |
| 2     | 2                                                |
| 3     | 2, 1                                             |
| 4     | 3, 2                                             |
| 5     | 3, 3, 1                                          |
| 6     | 3, 3, 2                                          |
| 7     | 3, 3, 2, 1                                       |
| 8     | 3, 3, 3, 2                                       |
| 9     | 4, 4, 3, 2, 1                                    |
| 10    | 4, 4, 3, 3, 2                                    |

### Non-Casters (Fighter, Thief, Monk)

**No spell slots** at any level.

### Multi-Class Casters (Ranger, Paladin, Druid, Bard, Illusionist, Assassin)

Refer to `aerthos/data/classes.json` for specific spell progression.

---

## Backup Files

Both scripts create backups before modifying files:

**reset_characters.py:**
- Format: `filename.json.YYYYMMDD_HHMMSS.bak`
- Example: `gandalf.json.20231215_143022.bak`
- Created only when `--no-backup` is NOT used

**fix_character_spell_slots.py:**
- Format: `filename.json.YYYYMMDD_HHMMSS.bak`
- Example: `party_01.json.20231215_143530.bak`
- Always created when files are modified

To restore from backup:
```bash
cp ~/.aerthos/characters/gandalf.json.20231215_143022.bak ~/.aerthos/characters/gandalf.json
```

---

## Testing

Run the verification tests to ensure both scripts work correctly:

```bash
python3 scripts/test_spell_slot_scripts.py
```

This will run unit tests verifying:
- ✓ `reset_characters.py --clear-spells` preserves slot structure
- ✓ `fix_character_spell_slots.py` adjusts slots intelligently
- ✓ Memorized spells are preserved where possible
- ✓ Non-casters have slots removed correctly

---

## Troubleshooting

### "Unknown class" warning
If you see `Warning: Unknown class 'ClassName'`, the class name doesn't match entries in `aerthos/data/classes.json`. Check spelling and capitalization (e.g., "Magic-User" not "magic user").

### Slots still wrong after running fix
1. Check the character's `char_class` field matches a class in `classes.json`
2. Verify the character's `level` is between 1-10
3. Look for backup files - you may have an older version
4. Run the script again (it's idempotent - safe to run multiple times)

### Lost memorized spells
Both scripts create backups! Restore from the `.bak` file:
```bash
cp <file>.json.<timestamp>.bak <file>.json
```

---

## Common Workflows

### After Leveling Up Characters

```bash
# 1. Fix spell slots to match new level
python3 scripts/fix_character_spell_slots.py

# 2. Give them a full rest
python3 scripts/reset_characters.py
```

### Preparing for Testing

```bash
# Full reset with empty spell slots
python3 scripts/reset_characters.py --clear-spells --clear-conditions
```

### Simulating a Long Rest

```bash
# Restore HP and spells, keep conditions
python3 scripts/reset_characters.py

# Or clear conditions too for a "healing rest"
python3 scripts/reset_characters.py --clear-conditions
```

### Importing Characters from External Source

```bash
# 1. Copy character files to ~/.aerthos/characters/
# 2. Fix their spell slots
python3 scripts/fix_character_spell_slots.py --characters-only
```

---

## Safety Features

Both scripts:
- ✓ Create backups before modifying files
- ✓ Support `--dry-run` mode (reset_characters.py)
- ✓ Show detailed output of what changed
- ✓ Are idempotent (safe to run multiple times)
- ✓ Skip backup files (`.bak`)
- ✓ Validate character data before modifying

---

## File Locations

Character data is stored in:
- **Saves:** `~/.aerthos/saves/*.json`
- **Characters:** `~/.aerthos/characters/*.json`
- **Parties:** `~/.aerthos/parties/*.json`

Where `~/.aerthos/` is defined in `aerthos/constants.py` as `_AERTHOS_HOME`.
