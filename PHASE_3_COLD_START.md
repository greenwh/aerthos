# PHASE 3: BALANCE & POLISH - COLD START GUIDE

**Project:** Aerthos - AD&D 1e Text Adventure
**Location:** `/mnt/d/Development/aerthos`
**Created:** December 2, 2025
**Status:** Ready to begin Phase 3 work
**Previous Work:** Phase 4 Task 1 COMPLETE (all 9 dungeons expanded)

---

## 🎯 **QUICK START - READ THIS FIRST**

**What You're Starting:**
Phase 3 - Balance & Polish work for the complete 10-episode Aerthos campaign.

**What Was Just Completed (Session 11):**
- ✅ Phase 4 Task 1: All 9 campaign dungeons fully expanded (Episodes 2-10)
- ✅ Episode 10 (The Serpent Temple) expanded from 6 → 18 rooms
- ✅ 313 total monsters, 520+ items, 108+ new rooms created
- ✅ All 504/504 tests passing

**Why Phase 3 Now:**
All content is in place. It's more efficient to balance the complete campaign together rather than balancing incrementally as content is added.

**What Phase 3 Does:**
Ensure the 10-episode campaign provides a balanced, polished experience from level 1 to level 10.

---

## 🚀 **HOW TO START (COLD START CHECKLIST)**

Follow these steps in order:

### 1. Navigate and Verify Environment

```bash
# Navigate to project
cd /mnt/d/Development/aerthos

# Verify Python version
python3 --version  # Should be 3.10+

# Run tests to establish baseline
python3 run_tests.py --no-web
# Expected: 504/504 tests passing
```

### 2. Review Context Documents

Read these files to understand current state:

```bash
# Read this document (you're doing it!)
cat PHASE_3_COLD_START.md | less

# Review project status
cat SESSION_ROADMAP.md | less

# Check recent session history
cat SESSION_ARCHIVE.md | tail -n 200

# Review development rules
cat CLAUDE.md | less
```

### 3. Understand What You Have

**Current Campaign State:**
- 10 episodes (Episodes 1-10)
- 11 dungeons (all fully expanded to 15-18 rooms each)
- 5 city hubs (Oakhaven, Ironfast, Mire's Edge, Coastal Haven, Eldoria)
- 313 monsters
- 520+ items
- 332 spells
- Complete progression system from level 1 to level 10

**What Works:**
- All core systems functional (combat, magic, skills, saves)
- Campaign playable end-to-end
- Both CLI and Web UI operational
- All tests passing

**What Needs Work (Phase 3):**
- Economy may not be balanced (shop prices, loot, rewards)
- Combat difficulty may not scale properly across 10 episodes
- XP progression may not feel natural
- Some descriptions may need enhancement
- Bugs may exist from full playthrough

---

## 📋 **PHASE 3 TASK BREAKDOWN**

### Task 1: Economy Analysis & Balance (5-6 hours)

**Goal:** Ensure gold economy works across full campaign (levels 1-10).

**Subtasks:**
1. Inventory current economy
   - List all shop prices (weapons, armor, items, spells)
   - List all loot drops by episode (treasure in dungeons)
   - List all episode completion rewards
   - Calculate typical gold income per episode

2. Analyze balance issues
   - Are shops affordable at appropriate levels?
   - Do players have too much/too little gold?
   - Are episode rewards proportional to difficulty?
   - Do prices scale with character level?

3. Make adjustments
   - Adjust shop prices if needed
   - Adjust treasure amounts in dungeons
   - Adjust episode completion rewards
   - Document all changes

**Files to Review:**
- `aerthos/data/shops.json` - Shop inventories and prices
- `aerthos/data/episodes/episode_*.json` - Episode rewards
- `aerthos/data/dungeons/*.json` - Dungeon loot (search for "gold_")
- `aerthos/data/equipment.json` - Item costs

**Success Criteria:**
- [ ] Players can afford basic equipment at level 1
- [ ] Players can upgrade equipment by level 5
- [ ] Players can afford high-end equipment by level 10
- [ ] Gold income feels rewarding but not excessive
- [ ] Shop prices feel fair relative to power level

---

### Task 2: Combat Difficulty Tuning (6-8 hours)

**Goal:** Ensure combat difficulty scales appropriately across all 10 episodes.

**Subtasks:**
1. Analyze current difficulty
   - Review monster stats by episode (HD, AC, damage, XP)
   - Check encounter sizes (number of monsters per fight)
   - Identify difficulty spikes or valleys
   - Review boss encounters

2. Create difficulty curve
   - Episode 1: Tutorial level (easy encounters)
   - Episodes 2-3: Easy-to-moderate
   - Episodes 4-6: Moderate
   - Episodes 7-9: Moderate-to-hard
   - Episode 10: Hard + epic finale

3. Make adjustments
   - Adjust monster HP (hit dice) if needed
   - Adjust monster damage if needed
   - Adjust encounter sizes (fewer/more monsters)
   - Adjust boss stats for appropriate challenge
   - Document all changes

**Files to Review:**
- `aerthos/data/monsters.json` - Monster stats
- `aerthos/data/dungeons/*.json` - Encounter compositions
- `aerthos/data/episodes/episode_*.json` - Recommended levels

**Testing Method:**
```bash
# Create test party at level X
# Run episode Y
# Observe:
# - Do characters survive most encounters?
# - Are fights too easy/hard?
# - Are bosses challenging but beatable?
# - Does difficulty feel appropriate for level?
```

**Success Criteria:**
- [ ] Level 1-2 party can complete Episode 1 with 1-2 deaths
- [ ] Difficulty increases gradually across episodes
- [ ] No sudden difficulty spikes
- [ ] Boss fights are challenging but winnable
- [ ] Players feel appropriately challenged at each level

---

### Task 3: XP Curve Verification (4-5 hours)

**Goal:** Ensure players reach appropriate levels for each episode naturally.

**Subtasks:**
1. Map expected progression
   - Episode 1: Level 1 → Level 2
   - Episode 2: Level 2 → Level 3
   - Episode 3: Level 3 → Level 4
   - Episode 4: Level 4 → Level 5
   - Episode 5: Level 5 → Level 6
   - Episode 6: Level 6 → Level 7
   - Episode 7: Level 7 → Level 8
   - Episode 8: Level 8 → Level 9
   - Episode 9: Level 9 → Level 10
   - Episode 10: Level 10 (finale)

2. Test XP progression
   - Simulate full campaign playthrough
   - Track XP gained per episode
   - Check if players level up at expected times
   - Identify XP shortfalls or surpluses

3. Make adjustments
   - Adjust monster XP values if needed
   - Adjust episode completion XP bonuses
   - Ensure progression feels natural
   - Document all changes

**Files to Review:**
- `aerthos/data/monsters.json` - Monster XP values
- `aerthos/data/episodes/episode_*.json` - Episode XP rewards
- `aerthos/data/classes.json` - XP requirements per level

**Testing Method:**
```bash
# Create level 1 party
# Track XP gain through each episode
# Record:
# - Starting level for each episode
# - Ending level for each episode
# - XP gained from monsters
# - XP gained from episode completion
# - Total XP vs. level-up requirements
```

**Success Criteria:**
- [ ] Players level up naturally between episodes
- [ ] Players don't outlevel content (too much XP)
- [ ] Players aren't underleveled (too little XP)
- [ ] Progression feels rewarding and steady
- [ ] Level 10 reached by end of Episode 9 or start of Episode 10

---

### Task 4: Quality Pass & Bug Fixes (3-4 hours)

**Goal:** Polish the campaign and fix any bugs found during testing.

**Subtasks:**
1. Comprehensive playthrough
   - Play through Episodes 1-10 in order
   - Take notes on bugs, typos, issues
   - Note any confusing descriptions
   - Check for broken encounters or items

2. Fix identified issues
   - Fix any crashes or errors
   - Fix typos and grammar issues
   - Enhance sparse descriptions
   - Fix broken item references
   - Fix encounter issues

3. Consistency checks
   - Consistent naming across files
   - Consistent formatting in JSON files
   - Consistent tone in descriptions
   - No duplicate IDs or references

**Testing Method:**
```bash
# Full playthrough test
python3 run_tests.py --no-web  # Start with passing tests
# Then manual play:
python3 main.py
# 1. Create character
# 2. Create party
# 3. Start campaign
# 4. Play through all 10 episodes
# 5. Note any issues
```

**Success Criteria:**
- [ ] No crashes or errors during playthrough
- [ ] No missing monsters or items
- [ ] All descriptions are clear and engaging
- [ ] No typos or grammar errors
- [ ] All 504/504 tests passing

---

## 🧪 **TESTING PROTOCOL FOR PHASE 3**

### Before Making Changes:

```bash
# Establish baseline
python3 run_tests.py --no-web
# Must show: 504/504 tests passing
```

### After Each Task:

```bash
# Verify no regressions
python3 run_tests.py --no-web
# Must show: 504/504 tests passing

# Manual testing
python3 main.py
# Test affected systems:
# - Task 1: Check shop prices, buy items
# - Task 2: Test combat in multiple episodes
# - Task 3: Track XP through progression
# - Task 4: Full playthrough
```

### Final Validation:

```bash
# Run full test suite
python3 run_tests.py --no-web
# Expected: 504/504 passing

# Full campaign playthrough
# - Create fresh party
# - Complete Episodes 1-10
# - Note completion time, difficulty, XP curve
# - Verify economy works throughout
# - Confirm final episode is satisfying
```

---

## 📊 **DATA COLLECTION TEMPLATE**

As you work through Phase 3, collect this data:

### Economy Data:

```
Episode | Gold from Loot | Episode Reward | Shop Prices | Can Afford?
--------|---------------|----------------|-------------|------------
1       | ???           | ???            | ???         | ???
2       | ???           | ???            | ???         | ???
...     | ...           | ...            | ...         | ...
10      | ???           | ???            | ???         | ???
```

### Combat Difficulty Data:

```
Episode | Avg Monster HD | Boss HD | Deaths | Difficulty Rating
--------|---------------|---------|--------|------------------
1       | ???           | ???     | ???    | Too Easy/Just Right/Too Hard
2       | ???           | ???     | ???    | ???
...     | ...           | ...     | ...    | ...
10      | ???           | ???     | ???    | ???
```

### XP Progression Data:

```
Episode | Starting Level | XP Gained | Ending Level | Expected Level
--------|---------------|-----------|--------------|---------------
1       | 1             | ???       | ???          | 2
2       | ???           | ???       | ???          | 3
...     | ...           | ...       | ...          | ...
10      | ???           | ???       | ???          | 10
```

---

## 📁 **KEY FILES FOR PHASE 3**

### Economy Files:
- `aerthos/data/shops.json` - Shop inventories and prices
- `aerthos/data/equipment.json` - Item costs (search for "cost": )
- `aerthos/data/episodes/episode_*.json` - Episode rewards (search for "gold_reward")
- `aerthos/data/dungeons/*.json` - Loot drops (search for "gold_")

### Combat Files:
- `aerthos/data/monsters.json` - Monster stats (HD, AC, damage, XP)
- `aerthos/data/dungeons/*.json` - Encounter compositions (search for "monsters": )
- `aerthos/data/episodes/episode_*.json` - Recommended levels

### Progression Files:
- `aerthos/data/classes.json` - XP requirements per level
- `aerthos/data/monsters.json` - Monster XP values
- `aerthos/data/episodes/episode_*.json` - Episode XP bonuses

### Testing Files:
- `run_tests.py` - Test runner
- `tests/` directory - All test files
- `main.py` - CLI entry point for manual testing

---

## 🎯 **RECOMMENDED WORK ORDER**

**Session 1 (4-5 hours):**
1. Complete Task 1: Economy Analysis & Balance
2. Document findings and changes
3. Run tests
4. Update progress in SESSION_ROADMAP.md

**Session 2 (4-5 hours):**
1. Complete Task 2: Combat Difficulty Tuning (Part 1: Episodes 1-5)
2. Test combat in Episodes 1-5
3. Document changes
4. Run tests

**Session 3 (4-5 hours):**
1. Complete Task 2: Combat Difficulty Tuning (Part 2: Episodes 6-10)
2. Test combat in Episodes 6-10
3. Document changes
4. Run tests

**Session 4 (4-5 hours):**
1. Complete Task 3: XP Curve Verification
2. Simulate full playthrough for XP tracking
3. Make adjustments
4. Run tests

**Session 5 (3-4 hours):**
1. Complete Task 4: Quality Pass & Bug Fixes
2. Full manual playthrough
3. Fix all identified issues
4. Final test run
5. Update all documentation

**Total Estimated Time:** 19-24 hours across 5 sessions

---

## ⚠️ **CRITICAL RULES FOR PHASE 3**

From `CLAUDE.md` - **NEVER violate these:**

### 1. ALWAYS Run Tests Before and After Changes

```bash
python3 run_tests.py --no-web
```

### 2. NEVER Hardcode Values

- Use JSON data files for all game content
- No hardcoded gold amounts, prices, XP values
- All balance changes go in JSON files

### 3. Document All Changes

- Track what you changed and why
- Update SESSION_ARCHIVE.md with session details
- Update SESSION_ROADMAP.md with progress

### 4. Test Both Interfaces

- CLI: `python3 main.py`
- Web UI: `python3 web_ui/app.py` (if Flask installed)
- Both must work after changes

### 5. Keep Backups

Before major changes:
```bash
# Backup key files
cp aerthos/data/monsters.json aerthos/data/monsters.json.backup
cp aerthos/data/shops.json aerthos/data/shops.json.backup
# etc.
```

---

## 📝 **SUCCESS CRITERIA FOR PHASE 3 COMPLETION**

Phase 3 is complete when ALL of these are true:

- [ ] **Economy:** Players can afford appropriate equipment at each level
- [ ] **Economy:** Gold income feels rewarding but not excessive
- [ ] **Economy:** Shop prices are balanced across all hubs
- [ ] **Combat:** Difficulty scales smoothly from Episode 1 to Episode 10
- [ ] **Combat:** Boss fights are challenging but winnable
- [ ] **Combat:** No sudden difficulty spikes or valleys
- [ ] **XP:** Players reach expected levels between episodes naturally
- [ ] **XP:** Level 10 reached by end of Episode 9 or start of Episode 10
- [ ] **Quality:** No crashes or errors in full playthrough
- [ ] **Quality:** All descriptions are clear and engaging
- [ ] **Quality:** No typos or grammar errors
- [ ] **Testing:** All 504/504 tests passing
- [ ] **Testing:** Full manual playthrough completed successfully
- [ ] **Docs:** SESSION_ROADMAP.md updated to mark Phase 3 complete
- [ ] **Docs:** SESSION_ARCHIVE.md updated with Phase 3 session details

---

## 🔧 **TROUBLESHOOTING**

### Tests Failing After Balance Changes?

```bash
# Check what broke
python3 run_tests.py --no-web --verbose

# Common issues:
# - Changed monster XP: Update test expectations
# - Changed item costs: Update test expectations
# - Changed encounter sizes: Update dungeon validation tests
```

### Economy Feels Wrong?

```bash
# Gather data first:
# 1. Play Episode 1, track gold earned
# 2. Visit shop, note prices
# 3. Calculate: Can player afford upgrades?
# 4. Adjust based on data, not guesses
```

### Combat Too Easy/Hard?

```bash
# Test with appropriate level party:
# Episode 1: Level 1-2 party
# Episode 5: Level 5-6 party
# Episode 10: Level 10 party

# Adjust:
# - Too easy: Increase monster HD or add more monsters
# - Too hard: Decrease monster HD or reduce encounter size
```

### XP Progression Off?

```bash
# Calculate expected vs actual:
# - AD&D 1e XP requirements: 0, 2000, 4000, 8000, 16000, 32000...
# - Track XP per episode
# - Adjust monster XP or episode bonuses
```

---

## 📚 **REFERENCE DOCUMENTS**

Keep these open during Phase 3 work:

1. **This Document** - Phase 3 work plan and guidance
2. **SESSION_ROADMAP.md** - Overall project status and priorities
3. **SESSION_ARCHIVE.md** - Detailed history of all sessions
4. **CLAUDE.md** - Development rules and architecture
5. **TESTING.md** - Testing guidelines (if exists)

---

## 🎮 **PLAYTESTING GUIDE**

### Quick Combat Test (20 minutes):

```bash
python3 main.py
# 1. Create level X character (appropriate for episode)
# 2. Create party of 4
# 3. Start episode Y
# 4. Fight 3-5 encounters
# 5. Note:
#    - How many deaths?
#    - Did party win easily/barely/lose?
#    - Was it fun or frustrating?
```

### Full Episode Test (1-2 hours):

```bash
python3 main.py
# 1. Create appropriate level party
# 2. Complete entire episode
# 3. Track:
#    - Gold earned
#    - XP earned
#    - Deaths/close calls
#    - Time to complete
#    - Overall difficulty rating
```

### Full Campaign Test (10-15 hours):

```bash
python3 main.py
# 1. Create fresh level 1 party
# 2. Play Episodes 1-10 in order
# 3. No cheating (don't reload on deaths)
# 4. Track everything:
#    - Level at start/end of each episode
#    - Gold earned/spent
#    - Equipment purchased
#    - Deaths
#    - Difficulty ratings
#    - Bugs/issues
# 5. This is the final validation test
```

---

## 💡 **HELPFUL COMMANDS**

### Search for Economy Data:

```bash
# Find all shop prices
grep -n '"cost":' aerthos/data/equipment.json | head -20

# Find all gold drops
grep -rn "gold_" aerthos/data/dungeons/

# Find episode rewards
grep -rn "gold_reward" aerthos/data/episodes/
```

### Search for Combat Data:

```bash
# Find monster stats
grep -A5 '"awakened_serpent":' aerthos/data/monsters.json

# Find encounters in Episode X
grep -n '"monsters":' aerthos/data/dungeons/serpent_temple.json

# Find boss encounters
grep -rn '"boss": true' aerthos/data/dungeons/
```

### Search for XP Data:

```bash
# Find monster XP values
grep -n '"xp_value":' aerthos/data/monsters.json | head -20

# Find episode XP bonuses
grep -rn "xp_reward" aerthos/data/episodes/
```

---

## 🚀 **FIRST STEPS WHEN YOU RESUME**

When you're ready to start Phase 3:

1. **Navigate to project:**
   ```bash
   cd /mnt/d/Development/aerthos
   ```

2. **Run tests to establish baseline:**
   ```bash
   python3 run_tests.py --no-web
   # Must show: 504/504 passing
   ```

3. **Read this document thoroughly:**
   ```bash
   cat PHASE_3_COLD_START.md | less
   ```

4. **Choose starting task:**
   - Recommended: Start with Task 1 (Economy Analysis & Balance)
   - It's foundational and affects the other tasks

5. **Begin work!**

---

**Good luck with Phase 3! This is the final polish that will make the campaign shine.** ✨

**Document Version:** 1.0
**Created:** December 2, 2025
**For:** Phase 3 (Balance & Polish) cold start
**Prerequisites:** Phase 4 Task 1 complete (all dungeons expanded)
