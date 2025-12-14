# Character Reset Script Guide

## Overview

`reset_characters.py` is a utility script for resetting characters to a fresh state. It's useful for:
- **Testing**: Reset characters between test sessions
- **Long Rest Simulation**: Restore HP and spells as if characters rested
- **Condition Cleanup**: Remove lingering debuffs after adventures
- **Character Refresh**: Prepare characters for new campaigns

## What It Does

### Always Applied (Default Behavior)
1. **Reset HP to Maximum** - All characters restored to full health
2. **Restore Spell Slots** - Clear all `is_used` flags on memorized spells

### Optional Flags
3. **Clear Memorized Spells** (`--clear-spells`) - Remove all spell references from slots (keeps empty slots)
4. **Clear Conditions** (`--clear-conditions`) - Remove all status effects (poisoned, diseased, etc.)

## Basic Usage

### Reset HP and Restore Spells (Most Common)
```bash
python3 reset_characters.py
```
This simulates a "long rest" - characters wake up with full HP and all spell slots restored.

### Full Reset (HP + Spells + Conditions)
```bash
python3 reset_characters.py --clear-conditions
```
Perfect for starting a new session fresh - removes any lingering debuffs.

### Complete Character Wipe (HP + Clear Everything)
```bash
python3 reset_characters.py --clear-spells --clear-conditions
```
Nuclear option - characters are at full health but must re-memorize all spells.

## Advanced Usage

### Dry Run (Preview Changes)
```bash
python3 reset_characters.py --dry-run
```
Shows what would change **without modifying any files**. Use this to see what the script will do.

### Process Specific File
```bash
python3 reset_characters.py --file ~/.aerthos/saves/save_1.json
```

### Process Only Certain File Types
```bash
# Only process save files
python3 reset_characters.py --saves-only

# Only process character roster files
python3 reset_characters.py --characters-only

# Only process party files
python3 reset_characters.py --parties-only
```

### Disable Backups (Not Recommended)
```bash
python3 reset_characters.py --no-backup
```
⚠️ **Warning**: This prevents backup creation. Only use if you're absolutely sure.

## File Locations

The script automatically processes files in:
- `~/.aerthos/saves/*.json` - Active save files
- `~/.aerthos/characters/*.json` - Character roster
- `~/.aerthos/parties/*.json` - Saved parties

## Backups

By default, the script creates timestamped backups before modifying files:
```
save_1.json                    # Modified file
save_1.json.20251214_133857.bak  # Backup with timestamp
```

You can safely delete `.bak` files after verifying the reset worked correctly.

## Examples

### Example 1: Quick Reset Between Sessions
Your party just finished a dungeon and you want to start fresh:
```bash
python3 reset_characters.py --clear-conditions
```
**Result:**
- HP restored to max
- Spell slots restored (can cast again)
- Conditions cleared (no more poison/disease)
- Memorized spells kept (ready to cast)

### Example 2: New Campaign Starting
You want characters at full strength but need them to re-select spells:
```bash
python3 reset_characters.py --clear-spells --clear-conditions
```
**Result:**
- HP restored to max
- Spell slots empty (must memorize new spells)
- Conditions cleared
- Fresh start for new campaign

### Example 3: Testing a Specific Save
You're testing combat and want to reset one save file:
```bash
python3 reset_characters.py --file ~/.aerthos/saves/test_save.json --dry-run
python3 reset_characters.py --file ~/.aerthos/saves/test_save.json
```
**Result:**
- First command previews changes
- Second command applies them
- Only affects the specified file

### Example 4: Mass Character Refresh
You have multiple characters in your roster and want them all at full health:
```bash
python3 reset_characters.py --characters-only
```
**Result:**
- All characters in roster at max HP
- All spell slots restored
- Saves and parties untouched

## Output Explanation

When you run the script, you'll see output like this:

```
======================================================================
CHARACTER RESET SCRIPT
======================================================================

Settings:
  Reset HP to max:        YES (always)
  Restore spell slots:    YES (always)
  Clear memorized spells: NO
  Clear conditions:       YES
  Create backups:         YES
  Dry run:                NO

--- Save Files (/home/dad/.aerthos/saves) ---

save_1.json:
  HP: 3 → 10
  Cleared 2 condition(s): poisoned, weakened
  Backup: save_1.json.20251214_133857.bak

======================================================================
SUMMARY
======================================================================
Files processed: 1
Files modified:  1
Files unchanged: 0

✓ Characters have been reset!
✓ Original files backed up with timestamp
```

**Reading the Output:**
- **Settings section**: Shows what operations will be performed
- **Per-file section**: Lists specific changes for each character
- **Summary**: Total files processed and modified
- **Backup confirmation**: Lists backup files created

## Technical Details

### What Gets Reset

**Character HP:**
```json
// Before
"hp_current": 3,
"hp_max": 10

// After
"hp_current": 10,
"hp_max": 10
```

**Spell Slots (Default):**
```json
// Before
{
  "level": 1,
  "spell": {"name": "Magic Missile", ...},
  "is_used": true  // ← Spell was cast
}

// After (--clear-spells NOT used)
{
  "level": 1,
  "spell": {"name": "Magic Missile", ...},
  "is_used": false  // ← Spell restored, can cast again
}

// After (--clear-spells used)
{
  "level": 1,
  "spell": null,  // ← Spell reference removed
  "is_used": false
}
```

**Conditions:**
```json
// Before
"conditions": ["poisoned", "weakened", "diseased"]

// After (with --clear-conditions)
"conditions": []
```

### Safety Features

1. **Automatic Backups**: Creates timestamped backups before modifying files
2. **Dry Run Mode**: Preview changes without modifying anything
3. **Detailed Logging**: Shows exactly what changed for each character
4. **Selective Processing**: Target specific file types or individual files
5. **Preserves Data**: Only modifies HP, spell flags, and optionally conditions/spells

### Party File Handling

When processing party files, the script:
- Resets ALL members in the party
- Shows changes per member
- Creates one backup for the entire party file

Example output for parties:
```
party_heroes.json:
  Gandor (Wizard): HP: 4 → 8, Restored 3 spent spell slot(s)
  Thrain (Cleric): HP: 12 → 15, Cleared 1 condition(s): poisoned
  Backup: party_heroes.json.20251214_140000.bak
```

## Troubleshooting

### "No files found"
Make sure `~/.aerthos/` directory exists and contains character data.

### "Permission denied"
Ensure you have write access to the `.aerthos` directory:
```bash
ls -la ~/.aerthos/
```

### Changes not appearing in-game
If you have an active game session running, you may need to:
1. Exit the current game
2. Run the reset script
3. Load the game again

### Backup files piling up
Old `.bak` files can be safely deleted:
```bash
# Delete all backup files older than 7 days
find ~/.aerthos -name "*.bak" -mtime +7 -delete

# List all backups before deleting
find ~/.aerthos -name "*.bak" -ls
```

## Best Practices

1. **Always use dry-run first** when trying new options
2. **Keep backups enabled** unless you have a very good reason not to
3. **Test with a single file** before processing all files
4. **Document your use** - Note why you're resetting (e.g., "Starting Episode 2")

## Integration with Game

This script is designed to work alongside the game, not replace it. Use it for:
- ✅ Testing and development
- ✅ Campaign preparation
- ✅ Character maintenance
- ✅ Simulating long rests outside the game

**Don't use it for:**
- ❌ Cheating in active campaigns (defeats the purpose!)
- ❌ Replacing the in-game rest mechanic
- ❌ Avoiding consequences of poor choices

## See Also

- `fix_character_spell_slots.py` - Fix spell slot progression issues
- `SPELL_FIXES_SUMMARY.md` - Details on spell slot system
- `CLAUDE.md` - Main development documentation

---

**Version:** 1.0
**Created:** 2025-12-14
**Compatible with:** Aerthos v1.0+
