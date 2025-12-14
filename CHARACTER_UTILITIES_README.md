# Character Utilities - Quick Reference

## Available Scripts

### 1. `reset_characters.py` - Character Reset Utility
**Location:** `/mnt/d/Development/aerthos/reset_characters.py`

**Purpose:** Reset characters to fresh state (HP, spells, conditions)

**Quick Commands:**
```bash
# Long rest simulation (HP + spell restore)
python3 reset_characters.py

# Full reset with condition clearing
python3 reset_characters.py --clear-conditions

# Nuclear option (clear everything)
python3 reset_characters.py --clear-spells --clear-conditions

# Preview changes (dry run)
python3 reset_characters.py --dry-run

# Process specific file
python3 reset_characters.py --file ~/.aerthos/saves/save_1.json
```

**What it does:**
- ✅ Always: Reset HP to max
- ✅ Always: Restore spell slots (clear `is_used` flags)
- 🔧 Optional: Clear memorized spells (`--clear-spells`)
- 🔧 Optional: Clear conditions (`--clear-conditions`)

**Documentation:** See `CHARACTER_RESET_GUIDE.md` for full details

---

### 2. `fix_character_spell_slots.py` - Spell Slot Migration Tool
**Location:** `/mnt/d/Development/aerthos/scripts/fix_character_spell_slots.py`

**Purpose:** One-time fix to update characters from old spell slot structure to new AD&D 1e progression

**Quick Command:**
```bash
python3 scripts/fix_character_spell_slots.py
```

**What it does:**
- Reads character class and level
- Applies correct AD&D 1e spell slot progression
- Creates `.bak` backups before modifying
- Processes saves, characters, and party files

**Note:** This was a one-time fix for the spell slot bug. Most users won't need to run this unless they have old character files created before 2025-12-14.

**Documentation:** See `SPELL_FIXES_SUMMARY.md` for background

---

## Quick Decision Guide

**Scenario:** "I want to start a new session fresh"
→ `python3 reset_characters.py --clear-conditions`

**Scenario:** "I'm testing combat and need to reset between tests"
→ `python3 reset_characters.py`

**Scenario:** "I want characters to re-memorize spells"
→ `python3 reset_characters.py --clear-spells`

**Scenario:** "I have old characters with broken spell slots"
→ `python3 scripts/fix_character_spell_slots.py`

**Scenario:** "I want to preview changes before applying them"
→ Add `--dry-run` to any command

---

## File Locations

Character data is stored in `/mnt/d/Development/aerthos/.aerthos/`:

```
/mnt/d/Development/aerthos/.aerthos/
├── saves/         # Active save files
├── characters/    # Character roster
├── parties/       # Saved party compositions
├── campaigns/     # Campaign progress
├── scenarios/     # Custom scenarios
└── sessions/      # Session snapshots
```

**Note:** The scripts automatically read this path from `aerthos/constants.py` lines 290-296.

Both utilities automatically process all relevant files in these directories.

---

## Backup Strategy

Both scripts create backups before modifying files:

**fix_character_spell_slots.py:**
- Creates `.bak` files (e.g., `save_1.json.bak`)
- Overwrites previous `.bak` on subsequent runs

**reset_characters.py:**
- Creates timestamped backups (e.g., `save_1.json.20251214_133857.bak`)
- Accumulates over time (safe to delete old backups)

**Cleanup old backups:**
```bash
# List all backups
find ~/.aerthos -name "*.bak" -ls

# Delete backups older than 7 days
find ~/.aerthos -name "*.bak" -mtime +7 -delete

# Delete all backups (use with caution!)
find ~/.aerthos -name "*.bak" -delete
```

---

## Common Issues

### Issue: "No files found"
**Solution:** Make sure `~/.aerthos/` exists with character data

### Issue: "Permission denied"
**Solution:** Check file permissions: `ls -la ~/.aerthos/`

### Issue: Changes not appearing in game
**Solution:** Exit game, run script, then reload save

### Issue: Too many backup files
**Solution:** Clean up old backups (see backup strategy above)

---

## For Developers

Both scripts are designed to be:
- **Safe**: Create backups before modifying
- **Transparent**: Show exactly what changed
- **Selective**: Target specific files or file types
- **Non-destructive**: Preserve character data

**Adding new functionality:**
1. Study existing code in `reset_characters.py` or `fix_character_spell_slots.py`
2. Follow the same backup/logging pattern
3. Test with `--dry-run` first
4. Document in this file

---

**Last Updated:** 2025-12-14
**Aerthos Version:** 1.0+
