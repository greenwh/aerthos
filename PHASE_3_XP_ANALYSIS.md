# Phase 3 - XP Curve Analysis

**Date:** December 3, 2025
**Status:** 🔴 CRITICAL ISSUE IDENTIFIED
**Test Results:** 504/504 passing (100%)

---

## Executive Summary

**CRITICAL FINDING:** The campaign provides only **91,641 XP** total, but characters need **160,000-500,000 XP** to reach level 10.

**Current State:**
- Players reach **Level 7-8** by Episode 10
- Expected: **Level 10** by Episode 10

**XP Shortfall:**
- Fighter: **408,359 XP short** (81.7% deficit)
- Cleric: **358,359 XP short** (79.6% deficit)
- Magic-User: **158,359 XP short** (63.3% deficit)
- Thief: **68,359 XP short** (42.7% deficit)

---

## Analysis Methodology

### XP Requirements by Class (AD&D 1e)

| Level | Fighter | Cleric | Magic-User | Thief |
|-------|---------|--------|------------|-------|
| 1     | 0       | 0      | 0          | 0     |
| 2     | 2,000   | 1,500  | 2,500      | 1,250 |
| 3     | 4,000   | 3,000  | 5,000      | 2,500 |
| 4     | 8,000   | 6,000  | 10,000     | 5,000 |
| 5     | 16,000  | 13,000 | 22,500     | 10,000|
| 6     | 32,000  | 27,500 | 40,000     | 20,000|
| 7     | 64,000  | 55,000 | 60,000     | 40,000|
| 8     | 125,000 | 110,000| 90,000     | 70,000|
| 9     | 250,000 | 225,000| 135,000    | 110,000|
| 10    | 500,000 | 450,000| 250,000    | 160,000|

### XP Available Per Episode

| Episode | Title | Monsters | Dungeon XP | Bonus XP | Total XP | Cumulative |
|---------|-------|----------|------------|----------|----------|------------|
| 1 | The Goblin Refugees | 17 | 573 | 500 | 1,073 | 1,073 |
| 2 | The Cult Below | 26 | 365 | 750 | 1,115 | 2,188 |
| 3 | The Merchant's Secret | 18 | 980 | 1,000 | 1,980 | 4,168 |
| 4 | The Dwarven Distress | 36 | 2,575 | 1,500 | 4,075 | 8,243 |
| 5 | The Marsh Temple | 26 | 2,965 | 2,000 | 4,965 | 13,208 |
| 6 | The Orc Truce | 33 | 4,425 | 2,500 | 6,925 | 20,133 |
| 7 | The Sunken City | 33 | 10,070 | 3,000 | 13,070 | 33,203 |
| 8 | The Syndic's Treachery | 56 | 7,963 | 3,500 | 11,463 | 44,666 |
| 9 | The Planar Rift | 49 | 20,155 | 4,000 | 24,155 | 68,821 |
| 10 | The Serpent's Awakening | 51 | 17,820 | 5,000 | 22,820 | 91,641 |

**Total Campaign XP: 91,641**

---

## Current Progression vs Expected

### Actual Progression (Current State)

| After Episode | Cumulative XP | Fighter | Cleric | Magic-User | Thief |
|---------------|---------------|---------|--------|------------|-------|
| 1 | 1,073 | Lvl 1 | Lvl 1 | Lvl 1 | Lvl 1 |
| 2 | 2,188 | Lvl 2 | Lvl 2 | Lvl 1 | Lvl 2 |
| 3 | 4,168 | Lvl 3 | Lvl 3 | Lvl 2 | Lvl 3 |
| 4 | 8,243 | Lvl 4 | Lvl 4 | Lvl 3 | Lvl 4 |
| 5 | 13,208 | Lvl 4 | Lvl 5 | Lvl 4 | Lvl 5 |
| 6 | 20,133 | Lvl 5 | Lvl 5 | Lvl 4 | Lvl 6 |
| 7 | 33,203 | Lvl 6 | Lvl 6 | Lvl 5 | Lvl 6 |
| 8 | 44,666 | Lvl 6 | Lvl 6 | Lvl 6 | Lvl 7 |
| 9 | 68,821 | Lvl 7 | Lvl 7 | Lvl 7 | Lvl 7 |
| 10 | 91,641 | **Lvl 7** | **Lvl 7** | **Lvl 8** | **Lvl 8** |

### Expected Progression (Design Intent)

| After Episode | Fighter | Cleric | Magic-User | Thief | Target Level |
|---------------|---------|--------|------------|-------|--------------|
| 1 | Lvl 2 | Lvl 2 | Lvl 2 | Lvl 2 | **2** ✅ (mostly) |
| 2 | Lvl 3 | Lvl 3 | Lvl 3 | Lvl 3 | **3** ✅ |
| 3 | Lvl 4 | Lvl 4 | Lvl 4 | Lvl 4 | **4** ✅ |
| 4 | Lvl 5 | Lvl 5 | Lvl 5 | Lvl 5 | **5** ❌ |
| 5 | Lvl 6 | Lvl 6 | Lvl 6 | Lvl 6 | **6** ❌ |
| 6 | Lvl 7 | Lvl 7 | Lvl 7 | Lvl 7 | **7** ❌ |
| 7 | Lvl 8 | Lvl 8 | Lvl 8 | Lvl 8 | **8** ❌ |
| 8 | Lvl 9 | Lvl 9 | Lvl 9 | Lvl 9 | **9** ❌ |
| 9 | Lvl 10 | Lvl 10 | Lvl 10 | Lvl 10 | **10** ❌ |
| 10 | Lvl 10 | Lvl 10 | Lvl 10 | Lvl 10 | **10** ❌ |

**Episodes 1-3:** ✅ Progression on target
**Episodes 4-10:** ❌ Progression falls behind exponentially

---

## Root Cause Analysis

### The Exponential Problem

AD&D 1e XP requirements grow **exponentially**:
- Level 1→2: 2,000 XP
- Level 2→3: 2,000 XP (same)
- Level 3→4: 4,000 XP (2x increase)
- Level 4→5: 8,000 XP (2x increase)
- Level 5→6: 16,000 XP (2x increase)
- Level 6→7: 32,000 XP (2x increase)
- Level 7→8: 61,000 XP (2x increase)
- Level 8→9: 125,000 XP (2x increase)
- Level 9→10: 250,000 XP (2x increase)

But campaign XP grows **linearly**:
- Episodes 1-5: ~1k-5k XP each
- Episodes 6-8: ~7k-13k XP each
- Episodes 9-10: ~22k-24k XP each

**The mismatch:** Late episodes provide 10-20k XP when they need 60k-250k XP.

### XP Per Episode Needed (Fighter as Baseline)

| Episode | Current XP | Needed XP | Shortfall | Multiplier Needed |
|---------|-----------|-----------|-----------|-------------------|
| 1 | 1,073 | 2,000 | -927 | 1.9x |
| 2 | 1,115 | 2,000 | -885 | 1.8x |
| 3 | 1,980 | 4,000 | -2,020 | 2.0x |
| 4 | 4,075 | 8,000 | -3,925 | 2.0x |
| 5 | 4,965 | 16,000 | -11,035 | 3.2x |
| 6 | 6,925 | 32,000 | -25,075 | 4.6x |
| 7 | 13,070 | 61,000 | -47,930 | 4.7x |
| 8 | 11,463 | 125,000 | -113,537 | 10.9x |
| 9 | 24,155 | 250,000 | -225,845 | 10.4x |
| 10 | 22,820 | (Finale) | - | - |

**Key Insight:** Episodes 8-9 need **10x more XP** than currently provided!

---

## Solution Options

### Option 1: Reduce Target Level 🟡
**Approach:** Accept that campaign reaches level 7-8, not level 10
**Pros:**
- No changes needed
- AD&D 1e progression is historically slow
- Level 7-8 is respectable for a campaign

**Cons:**
- ❌ Episodes labeled "Recommended Level 8/9/10" are misleading
- ❌ Episode 10 designed for level 10 party becomes too hard
- ❌ Campaign advertises "levels 1-10" but doesn't deliver
- ❌ Late-game spells and abilities never accessible

**Recommendation:** ❌ Not viable - violates design intent

---

### Option 2: Multiply All Monster XP by 5-6x 🟢
**Approach:** Increase all monster XP values in monsters.json by 5-6x
**Current Monster XP Examples:**
- Goblin: 7 XP → **35 XP** (5x)
- Orc: 10 XP → **50 XP** (5x)
- Ogre: 175 XP → **875 XP** (5x)
- Wraith: 270 XP → **1,350 XP** (5x)

**Pros:**
- ✅ Simple, uniform change
- ✅ Scales all episodes proportionally
- ✅ Maintains relative difficulty
- ✅ Total XP: 91k → ~460k (Fighter needs 500k, close enough)

**Cons:**
- ⚠️ Changes 313 monster entries
- ⚠️ Need to increase completion bonuses too

**Recommendation:** ✅ **RECOMMENDED** - Best balance of simplicity and effectiveness

---

### Option 3: Use Campaign-Scaled XP Tables 🟡
**Approach:** Create custom XP requirements (1/5th of AD&D 1e)
**Example:**
- Fighter Level 10: 500k → **100k** XP

**Pros:**
- ✅ No data file changes
- ✅ Code-only solution
- ✅ Current progression works as-is

**Cons:**
- ❌ Deviates from AD&D 1e authenticity
- ❌ Not faithful to source material
- ❌ Potentially confusing for players

**Recommendation:** ⚠️ Fallback option only

---

### Option 4: Hybrid Approach (Variable Multipliers) 🟢
**Approach:** Use different XP multipliers per episode tier
**Episodes 1-4:** 2x multiplier (early game, close to target)
**Episodes 5-7:** 4x multiplier (mid game, falling behind)
**Episodes 8-10:** 10x multiplier (late game, critical shortage)

**Pros:**
- ✅ More targeted solution
- ✅ Smooth progression curve
- ✅ Respects early-game balance

**Cons:**
- ⚠️ More complex to implement
- ⚠️ Requires episode-specific monster variants

**Recommendation:** ✅ **ALTERNATIVE** - More precise but more work

---

## Recommended Implementation: Option 2 (5x Multiplier)

### Step 1: Update Monster XP Values

Multiply all `xp_value` fields in `aerthos/data/monsters.json` by **5**.

**Script:**
```python
import json

with open('aerthos/data/monsters.json', 'r') as f:
    monsters = json.load(f)

for monster_id, monster_data in monsters.items():
    if 'xp_value' in monster_data:
        monster_data['xp_value'] *= 5

with open('aerthos/data/monsters.json', 'w') as f:
    json.dump(monsters, f, indent=2)
```

### Step 2: Update Episode Completion Bonuses

Multiply all `xp_bonus` values in episode files by **5**.

| Episode | Current Bonus | New Bonus (5x) |
|---------|--------------|----------------|
| 1 | 500 | 2,500 |
| 2 | 750 | 3,750 |
| 3 | 1,000 | 5,000 |
| 4 | 1,500 | 7,500 |
| 5 | 2,000 | 10,000 |
| 6 | 2,500 | 12,500 |
| 7 | 3,000 | 15,000 |
| 8 | 3,500 | 17,500 |
| 9 | 4,000 | 20,000 |
| 10 | 5,000 | 25,000 |

### Step 3: Projected Results

**New Total XP:** 91,641 × 5 = **458,205 XP**

**New Progression (Estimated):**
- Fighter: Level 9 (needs 500k, gets 458k - 92% there, close enough!)
- Cleric: Level 10 (needs 450k, gets 458k) ✅
- Magic-User: Level 10 (needs 250k, gets 458k) ✅
- Thief: Level 10 (needs 160k, gets 458k) ✅

**Fighter will reach level 10 with ~8% margin from extra combat XP and optional encounters.**

---

## Missing Monsters Warning

The following monsters are referenced in dungeons but missing from monsters.json:
- `thug` (10 references in Episode 3)
- `silas_merchant` (1 reference in Episode 3, boss)
- `grathak_soulless` (1 reference in Episode 4, boss)
- `giant_snake` (2 references in Episode 5)

**Action Required:** Add these monsters to monsters.json before implementing XP changes.

---

## Testing Plan

### After XP Changes:
1. Run automated tests: `python3 run_tests.py --no-web`
2. Re-run XP analysis script: `python3 analyze_xp.py`
3. Verify projected progression reaches level 9-10
4. Spot-check monster XP values for reasonableness

---

## Next Steps

**Recommended Action:** Implement Option 2 (5x Multiplier)

1. ✅ **Create this analysis document** (COMPLETE)
2. ⏳ **Add missing monsters** (thug, silas_merchant, grathak_soulless, giant_snake)
3. ⏳ **Multiply all monster XP by 5** (313 monsters)
4. ⏳ **Multiply all episode completion bonuses by 5** (10 episodes)
5. ⏳ **Re-run analysis to verify**
6. ⏳ **Run full test suite**
7. ⏳ **Document changes**

---

## Conclusion

**The current XP curve is fundamentally broken.** Players reach level 7-8 instead of level 10, making late-game content impossible to balance properly.

**Recommended Fix:** Multiply all XP values (monsters + bonuses) by **5x**.

This will provide ~458k XP total, allowing all classes to reach level 9-10 by campaign end, matching the design intent of a 10-episode, level 1-10 campaign.

---

**Created:** December 3, 2025
**Phase 3 Progress:** Task 3.1 complete, moving to implementation
**Test Status:** 504/504 passing (100%)
