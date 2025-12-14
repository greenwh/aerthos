# Path Configuration - IMPORTANT!

## Why This Keeps Happening

### The Problem
Scripts keep defaulting to `~/.aerthos/` (which is `/home/dad/.aerthos/`) instead of the actual data location `/mnt/d/Development/aerthos/.aerthos/`.

### The Root Cause
Most applications follow the Unix convention of storing user data in the home directory (`~/.appname/`). This is so common that developers (including AI assistants) automatically assume this pattern.

**However, aerthos uses a different approach:**
- Data is stored in `.aerthos/` **within the project directory**
- This is defined in `aerthos/constants.py` lines 290-296

### Why Aerthos Does This
```python
# From aerthos/constants.py
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_AERTHOS_HOME = _PROJECT_ROOT / ".aerthos"
```

**Benefits of this approach:**
1. ✅ **Portable** - All game data travels with the project
2. ✅ **Multiple instances** - Can have different game data per project copy
3. ✅ **Development friendly** - Data alongside code for testing
4. ✅ **WSL2 compatible** - Works on Windows filesystem via `/mnt/d/`

**Trade-offs:**
1. ⚠️ Non-standard location confuses developers/tools
2. ⚠️ Must explicitly use `constants.py` paths
3. ⚠️ Can't easily share data between project copies

## The Solution

### For All New Scripts

**ALWAYS start with:**
```python
from pathlib import Path
from aerthos.constants import _AERTHOS_HOME

aerthos_dir = Path(_AERTHOS_HOME)
saves_dir = aerthos_dir / 'saves'
characters_dir = aerthos_dir / 'characters'
parties_dir = aerthos_dir / 'parties'
```

**NEVER hardcode:**
```python
# ❌ WRONG - Hardcoded path
home = Path.home()
aerthos_dir = home / '.aerthos'

# ❌ WRONG - Absolute path
aerthos_dir = Path('/home/dad/.aerthos')

# ❌ WRONG - Assuming home directory
aerthos_dir = Path('~/.aerthos').expanduser()
```

### Verification Checklist

Before running any script that touches character data:

1. **Check the path import:**
   ```bash
   grep -n "aerthos_dir\|AERTHOS_HOME" your_script.py
   ```

2. **Verify it imports from constants:**
   ```bash
   grep "from aerthos.constants import" your_script.py
   ```

3. **Test with dry run first:**
   ```bash
   python3 your_script.py --dry-run
   # Check that paths show /mnt/d/Development/aerthos/.aerthos/
   ```

## Quick Path Check

Run this to verify your data location:
```bash
python3 -c "from aerthos.constants import _AERTHOS_HOME; print(_AERTHOS_HOME)"
```

**Expected output:**
```
/mnt/d/Development/aerthos/.aerthos
```

**NOT:**
```
/home/dad/.aerthos  # ❌ WRONG!
```

## Current State

### Scripts Fixed (2025-12-14)
- ✅ `reset_characters.py` - Now uses `_AERTHOS_HOME` from constants
- ✅ `fix_character_spell_slots.py` - Now uses `_AERTHOS_HOME` from constants
- ✅ **Both scripts work from any directory** - Can be run from scripts/, project root, or anywhere else

### Your Actual Data
```
/mnt/d/Development/aerthos/.aerthos/
├── characters/    # 10 character files ✅
├── parties/       # 3 party files ✅
├── saves/         # Save files ✅
├── campaigns/     # Campaign data ✅
├── scenarios/     # Scenario data ✅
└── sessions/      # Session data ✅
```

### Test Data (Cleaned Up)
```
/home/dad/.aerthos/
├── characters/    # Test characters (removed) ✅
└── parties/       # Test parties (removed) ✅
```

## For AI Assistants / Future Development

**When creating any script that accesses aerthos data:**

1. **First action:** Read `aerthos/constants.py` lines 280-297
2. **Import paths:** Use `from aerthos.constants import _AERTHOS_HOME`
3. **Never assume:** `~/.aerthos/` or any home directory pattern
4. **Verify immediately:** Show the user what path you're using
5. **Ask if uncertain:** "Should I use the path from constants.py?"

## Environment Context

**System:** WSL2 on Windows
- Windows filesystem mounted at `/mnt/d/`
- Development directory: `/mnt/d/Development/aerthos/`
- Data directory: `/mnt/d/Development/aerthos/.aerthos/`

**Why this matters:**
- `~` expands to `/home/dad/` (Linux home directory)
- But the project is on Windows filesystem (`/mnt/d/`)
- Using `~/.aerthos/` creates data in **two different places**

## Common Mistakes & Fixes

### Mistake 1: Assuming Home Directory
```python
# ❌ WRONG
aerthos_dir = Path.home() / '.aerthos'

# ✅ CORRECT
from aerthos.constants import _AERTHOS_HOME
aerthos_dir = Path(_AERTHOS_HOME)
```

### Mistake 2: Hardcoding Absolute Path
```python
# ❌ WRONG - Not portable
aerthos_dir = Path('/mnt/d/Development/aerthos/.aerthos')

# ✅ CORRECT - Uses constants
from aerthos.constants import _AERTHOS_HOME
aerthos_dir = Path(_AERTHOS_HOME)
```

### Mistake 3: Manual Path Construction
```python
# ❌ WRONG - Fragile
import os
project_root = os.path.dirname(os.path.abspath(__file__))
aerthos_dir = os.path.join(project_root, '.aerthos')

# ✅ CORRECT - Uses constants
from aerthos.constants import _AERTHOS_HOME
aerthos_dir = Path(_AERTHOS_HOME)
```

## Testing Path Configuration

Create a simple test script:
```python
#!/usr/bin/env python3
from pathlib import Path
from aerthos.constants import _AERTHOS_HOME

print("Aerthos data directory:", _AERTHOS_HOME)
print("\nContents:")
for subdir in ['saves', 'characters', 'parties', 'campaigns']:
    path = Path(_AERTHOS_HOME) / subdir
    if path.exists():
        files = list(path.glob('*.json'))
        print(f"  {subdir}: {len(files)} files")
    else:
        print(f"  {subdir}: (does not exist)")
```

Save as `test_paths.py` and run:
```bash
python3 test_paths.py
```

Expected output:
```
Aerthos data directory: /mnt/d/Development/aerthos/.aerthos

Contents:
  saves: 0 files
  characters: 10 files
  parties: 3 files
  campaigns: 1 files
```

---

**Last Updated:** 2025-12-14
**Scripts Fixed:** reset_characters.py, fix_character_spell_slots.py
**Lesson Learned:** ALWAYS use constants.py for paths!
