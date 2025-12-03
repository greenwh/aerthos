# AERTHOS CAMPAIGN - SESSION STARTUP ROADMAP

**Project:** Aerthos - AD&D 1e Text Adventure
**Location:** `/mnt/d/Development/aerthos`
**Last Updated:** December 2, 2025 - Session 11 Complete
**Status:** ✅ **PHASE 1 COMPLETE** | ✅ **PHASE 2: 80% COMPLETE** | ✅ **PHASE 4: TASK 1 COMPLETE (9/9 dungeons)**
**Test Status:** 504/504 tests passing (100%) ← All tests passing

**For detailed session histories:** See `SESSION_ARCHIVE.md`

---

## 🚀 **START HERE FOR NEW SESSION**

**If starting fresh (cold start), follow these steps:**

1. **Navigate to project:** `cd /mnt/d/Development/aerthos`
2. **Verify tests pass:** `python3 run_tests.py --no-web` (expect 504/504)
3. **Read this file:** You're doing it! Keep reading for context.
4. **Check "Next Session Goals"** (scroll to bottom for latest goals)
5. **Current task:** Phase 4 Task 1 COMPLETE - Decide next priority (Tasks 2-5 or Phase 3 balance)

**Quick Context:**
- ✅ Campaign fully playable (10 episodes, Episodes 1-10 fully expanded)
- ✅ Phase 1 complete (core gameplay working)
- ✅ Phase 2 80% complete (UI sync mostly done)
- ✅ Phase 4 Task 1 COMPLETE (content expansion: 9 of 9 dungeons complete)
- 📝 Next: Phase 4 Tasks 2-5 (side quests, reputation effects, multiple endings) or Phase 3 (balance & polish)

**Development Order:** Phase 2 → Phase 4 → Phase 3 (expand content before balancing)

---

## 📋 **QUICK STATUS CHECK**

Before starting work, verify project state:

```bash
# 1. Check you're in the right directory
pwd
# Should show: /mnt/d/Development/aerthos

# 2. Run tests to verify nothing is broken
python3 run_tests.py --no-web
# Should show: 504/504 tests passing (updated from 489 after playthrough tests)

# 3. Check git status (if using git)
git status
# Should show: clean working tree or known modifications
```

**If tests fail or unexpected errors occur:**
- Check `CLAUDE.md` for troubleshooting
- Verify Python version: `python3 --version` (should be 3.10+)
- Verify you're on correct branch

---

## 🎯 **CURRENT PROJECT STATUS**

### What's Complete ✅

**Core Systems (100%):**
- THAC0 combat system
- Vancian magic system (332 spells)
- Character creation (4 classes, 4 races, 9 alignments)
- Party management system
- Dungeon generation (procedural + hand-crafted)
- Natural language parser (45+ verb groups)
- Save/load system (5-tier persistence)
- Session management
- Campaign system architecture

**Campaign Content (Fully Expanded):**
- 10 Episodes created (Episode 1 - Episode 10)
- 5 City Hubs (Oakhaven, Ironfast Outpost, Mire's Edge, Coastal Haven, Eldoria)
- 11 Dungeons (ALL complete - 100% expansion done)
  - ✅ Episode 1: Goblin Caves (15 rooms, original)
  - ✅ Episode 2: Oakhaven Sewers (18 rooms, expanded)
  - ✅ Episode 3: Silas's Warehouse (18 rooms, expanded)
  - ✅ Episode 4: Duergar Hold (18 rooms, expanded)
  - ✅ Episode 5: Sunken Temple (18 rooms, expanded)
  - ✅ Episode 6: Scorched Fortress (18 rooms, expanded)
  - ✅ Episode 7: Drowned Ruins (18 rooms, expanded)
  - ✅ Episode 8: Eldoria Catacombs (18 rooms, expanded)
  - ✅ Episode 9: Elemental Chaos (18 rooms, expanded)
  - ✅ Episode 10: The Serpent Temple (18 rooms, expanded)
- Campaign progression system
- Hub interfaces (Shop, Inn, Temple)
- Episode completion tracking
- Reputation system (tracking only, no effects yet)

**Both Interfaces Working:**
- CLI (`main.py`) - Full campaign mode implemented
- Web UI (`web_ui/app.py`) - Campaign API and templates

### What's Incomplete ⚠️

**✅ Critical Blockers RESOLVED:**
- ~~30+ monster definitions missing~~ ← **FIXED Session 1** (32 monsters added)
- ~~20+ item definitions missing~~ ← **FIXED Session 1-2** (23 items added)
- ~~Waterbreathing mechanic not implemented~~ ← **FIXED Session 1** (full implementation + tests)
- ~~No full playthrough testing done yet~~ ← **FIXED Session 2** (automated test framework)

**Campaign is now fully playable from Episode 1 to Episode 10!**

**Content Depth:**
- ✅ **ALL dungeons expanded!** (Episodes 1-10: 15-18 rooms each)
- Rich descriptions across all episodes
- No optional side quests or bonus content (Phase 4 Tasks 2-5)

**Feature Gaps:**
- Reputation system doesn't affect gameplay (no discounts, faction support, etc.)
- Multiple endings system not implemented (Episode 10 has single ending)
- Auto-save not implemented (manual save only)
- Additional character classes not implemented (only 4 of 11 AD&D 1e classes)

---

## 🚀 **RECOMMENDED DEVELOPMENT PATH** (UPDATED)

This is the **optimal sequence** to get from current state to polished, playable campaign:

```
┌─────────────────────────────────────────────────────────────┐
│  ✅ PHASE 1: MAKE CAMPAIGN PLAYABLE (20 hours) - DONE      │
│  Priority: CRITICAL - Blocks actual gameplay               │
│  Document: CAMPAIGN_TODO.md (Priority 1)                   │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  🔄 PHASE 2: FIX UI SYNC ISSUES (10 hours) - 80% DONE      │
│  Priority: HIGH - UX consistency between CLI and Web UI    │
│  Document: cli_web_sync_issues.md (Priority 1)             │
│  Remaining: Task 3 - Cross-compatibility testing (2 hours) │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  🔄 PHASE 4: CONTENT EXPANSION (40+ hours) ← IN PROGRESS   │
│  Priority: HIGH - Add depth to existing campaign           │
│  Document: CAMPAIGN_TODO.md (Priority 3)                   │
│  Expand dungeons, add side quests, reputation effects      │
│  Progress: 7/9 dungeons complete (78%)                     │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: BALANCE & POLISH (15 hours) ← DO LAST            │
│  Priority: MEDIUM - Balance ALL content at once            │
│  Document: CAMPAIGN_TODO.md (Priority 2)                   │
│  Balance economy, combat, XP for all 10 episodes together  │
└─────────────────────────────────────────────────────────────┘
```

**Why This Order (Updated):**
1. ✅ **Playability First:** Campaign is now fully playable end-to-end (Phase 1 complete)
2. ✅ **Sync Second:** Both interfaces now offer consistent narrative experience (Phase 2: 80% complete)
3. 🆕 **Content Third (Phase 4 before Phase 3):** Add all content expansion BEFORE balancing
   - **Reason:** More efficient to balance everything together after all content exists
   - Expanding 9 dungeons now means we balance all 10 dungeons at once in Phase 3
   - Adding side quests, reputation effects, multiple endings together, then balance together
   - Prevents rebalancing work when new content is added
4. **Polish Last (Phase 3):** With ALL content in place, do comprehensive balance pass
   - Economy balance across all shops, all rewards
   - Combat difficulty across all 10 episodes
   - XP curve for full 1-10 progression
   - Test complete playthrough and adjust holistically

---

## 📖 **PHASE 1: MAKE CAMPAIGN PLAYABLE** ✅ **COMPLETE**

**Time Estimate:** 20 hours
**Goal:** Campaign completable end-to-end without errors
**Status:** ✅ **COMPLETED Session 1-2**

### Completed Tasks:

- [x] Task 1: Create Missing Monster Definitions (32/32 monsters) ← **DONE Session 1**
- [x] Task 2: Create Missing Item Definitions (23/23 items) ← **DONE Session 1-2**
- [x] Task 3: Implement Waterbreathing Mechanic (100%) ← **DONE Session 1**
- [x] Task 4: Automated Playthrough Tests (15/15 tests) ← **DONE Session 2**

**Outcome:** Campaign is now fully playable end-to-end. All 504/504 tests passing.

---

## 📖 **PHASE 2: FIX UI SYNC ISSUES** - 80% COMPLETE

**Time Estimate:** 10 hours
**Goal:** Both interfaces offer identical gameplay experience
**Status:** 🔄 **80% Complete** (Tasks 1-2 complete, Task 3 pending)

### Completed Tasks:

- [x] Task 1: Create Episode Narrative Templates ← **DONE Session 2**
  - Web UI episode intro and completion screens
  - Both interfaces show identical narrative content
- [x] Task 2: Add Manual Save to CLI ← **DONE Session 2**
  - CLI hub menu has 's' key for manual save
  - Both interfaces support manual save

### Remaining Tasks:

- [ ] Task 3: Test Cross-Compatibility (optional manual testing) ← **PENDING**
  - CLI ↔ Web UI campaign compatibility testing
  - Side-by-side gameplay verification
  - Note: Lower priority since both UIs use same core engine

**Note:** Task 3 requires manual testing which cannot be automated. This is lower priority since both interfaces use the same core engine and campaign/party data structures.

---

## 📖 **PHASE 3: BALANCE & POLISH** ⚠️ **DO THIS LAST (After Phase 4)**

**Time Estimate:** 15 hours
**Document Reference:** `CAMPAIGN_TODO.md` Priority 2 section
**Status:** Not started (waiting for Phase 4 completion)

**Why After Phase 4:**
- Balance all content together after all dungeons are expanded
- Prevents rebalancing work when new content is added
- More efficient to tune economy, combat, and XP as a whole

**Tasks:**
1. Economy balance (shop prices, loot drops, episode rewards)
2. Combat difficulty tuning for ALL dungeons (expanded + original)
3. XP curve verification for full 1-10 progression
4. Bug fixes from complete playthrough
5. Enhanced descriptions for all content

---

## 📖 **PHASE 4: CONTENT EXPANSION** ← **TASK 1 COMPLETE (100%)**

**Time Estimate:** 40+ hours
**Document Reference:** `CAMPAIGN_TODO.md` Priority 3 section
**Status:** ✅ **TASK 1 COMPLETE** - All 9 dungeons expanded (100%)

**⚠️ IMPORTANT:** Do this phase BEFORE Phase 3 (Balance & Polish) to balance all content together.

**Why Expand Before Balancing:**
- Adding 9 expanded dungeons after balancing means rebalancing everything
- Side quests, reputation effects, multiple endings affect economy/progression
- Balance once with all content in place rather than multiple balance passes

### Task 1: Expand Dungeons (9/9 complete = 100%) ✅ **COMPLETE**

**All Expansions Complete:**
- ✅ **Episode 2 (Oakhaven Sewers):** 5 → 18 rooms (+260%) ← Session 3
- ✅ **Episode 3 (Silas's Warehouse):** 6 → 18 rooms (+200%) ← Session 4
- ✅ **Episode 4 (Duergar Hold):** 6 → 18 rooms (+200%) ← Session 5
- ✅ **Episode 5 (Sunken Temple):** 6 → 18 rooms (+200%) ← Session 6
- ✅ **Episode 6 (Scorched Fortress):** 7 → 18 rooms (+157%) ← Session 7
- ✅ **Episode 7 (Drowned Ruins):** 6 → 18 rooms (+200%) ← Session 8
- ✅ **Episode 8 (Eldoria Catacombs):** 5 → 18 rooms (+260%) ← Session 9
- ✅ **Episode 9 (Elemental Chaos):** 7 → 18 rooms (+157%) ← Session 10
- ✅ **Episode 10 (The Serpent Temple):** 6 → 18 rooms (+200%) ← Session 11

**Session Work Summary (Sessions 3-11):**
- **Total Monsters Added:** +53 monsters (280 → 313 total)
- **Total Items Added:** +443 items across all categories
- **Total New Rooms:** +108 rooms (9 dungeons expanded)
- **Test Status:** 504/504 tests passing (no regressions)

**For detailed session histories:** See `SESSION_ARCHIVE.md`

### Task 2: Add Side Quests and Optional Content ← **NOT STARTED**

- Optional objectives within episodes
- Hidden treasures and secret areas
- NPC interactions and dialogue trees

### Task 3: Implement Reputation Effects ← **NOT STARTED**

- Reputation system is tracked but has no effects
- Add shop discounts, faction support, special rewards
- Reputation-gated content

### Task 4: Implement Multiple Endings ← **NOT STARTED**

- Episode 10 currently has single ending
- Add branching based on choices/reputation
- Different final confrontations

### Task 5: Add More Character Classes (Optional) ← **NOT STARTED**

- Currently only 4 classes (Fighter, Cleric, Magic-User, Thief)
- AD&D 1e has 11+ classes total
- Add Ranger, Paladin, Druid, etc.

---

## 🗺️ **DUNGEON EXPANSION WORKFLOW** (For Phase 4 Task 1)

**Goal:** Expand stub dungeons (5-7 rooms) to full dungeons (15-20 rooms) with thematic coherence.

**Standard Workflow (Used for Episodes 2-6):**

### Step 1: Analysis Phase

1. **Read episode configuration:** `aerthos/data/episodes/episode_XX.json`
   - Note the theme, boss, story context
2. **Read current dungeon:** `aerthos/data/dungeons/[dungeon_name].json`
   - Count current rooms (usually 5-7)
   - Identify theme and starting point
   - Note existing encounters and items
3. **Check episode location on roadmap:** Read the episode description in this file
   - Understand narrative arc and campaign position

### Step 2: Design Phase

1. **Design expansion layout** (target: 15-20 rooms total)
   - Create multiple wings/branches (3-4 distinct areas)
   - Plan exploration paths (linear, branching, optional areas)
   - Designate safe rest room location (usually mid-dungeon)
   - Plan boss approach (guardian encounters before boss chamber)
   - Include high-risk/high-reward optional areas
2. **Thematic areas** (Examples from Episodes 2-6):
   - Episode 2 (Sewers): Cultist facilities, sewer creatures, flooded passages
   - Episode 3 (Warehouse): Admin, shipping, cursed goods, smuggling
   - Episode 4 (Duergar Hold): Upper fortress, forge complex, deep cult horror
   - Episode 5 (Sunken Temple): Ritual chambers, knowledge wing, cultist facilities, crypt
   - Episode 6 (Scorched Fortress): Upper fortress, mid fortress, lower volcanic level
3. **Create ASCII map** for documentation purposes (save to SESSION_ARCHIVE.md)

### Step 3: Implementation Phase

**A. Expand dungeon JSON file:**
```bash
# Open dungeon file in editor
# Typical location: aerthos/data/dungeons/[name].json
# Expand from ~6 rooms to ~18 rooms
# Follow existing room schema (id, title, description, exits, encounters, items, light_level, safe_rest)
```

**B. Add new monsters** (typically 4-6 per expansion):
1. Open `aerthos/data/monsters.json`
2. Add monsters appropriate for dungeon theme and level
3. Balance HD (hit dice) for party level
4. Include variety: weak (2d8), medium (4d8), strong (6d8+)
5. Add special abilities relevant to theme

**C. Add new items** (typically 40-60 per expansion):
Categories to include:
- **Lore items** (6-10): Letters, journals, maps, texts that advance story
- **Treasure** (8-12): Gold pouches, gems, valuables
- **Quest items** (8-12): Keys, symbols, cultural artifacts
- **Equipment** (8-12): Tools, supplies, consumables
- **Magic items** (2-4): Weapons, armor, potions (rare, don't oversaturate)
- **Weapons/Armor** (4-8): New weapon types, shields if thematic

**D. Add new weapons** (if thematic):
- Open `aerthos/data/weapons.json`
- Add 4-8 thematic weapons (ceremonial, cultural, enemy equipment)

**E. Add new armor/shields** (if thematic):
- Open `aerthos/data/armor.json`
- Add shields or armor pieces relevant to faction/theme

### Step 4: Testing Phase

```bash
# Run full test suite
python3 run_tests.py --no-web

# Expected: 504/504 tests passing
# Fix any failures before continuing
```

### Step 5: Documentation Phase

1. **Update this file (SESSION_ROADMAP.md):**
   - Update Quick Context at top of file
   - Update Phase 4 progress tracker
   - Update "Next Session Goals" section

2. **Update SESSION_ARCHIVE.md:**
   - Add new "Session X Summary" section
   - Include dungeon overview, monster table, item list, files modified
   - Add ASCII dungeon map
   - Update cumulative content table

3. **Verify cold start readiness:**
   - Current task reflects next episode to expand
   - Quick Context shows correct episode count
   - Phase 4 progress percentage is accurate

**Expected Time per Dungeon:** 3-4 hours (analysis: 30min, design: 30min, implementation: 2hrs, testing: 15min, documentation: 45min)

**Quality Checklist:**
- [ ] Dungeon has 15-20 rooms (200-300% expansion from stub)
- [ ] Multiple exploration paths (3-4 distinct areas/wings)
- [ ] Thematic coherence (all rooms fit dungeon theme)
- [ ] Safe rest room included (usually mid-dungeon)
- [ ] Boss approach is interesting (guardians, challenges before boss)
- [ ] Optional high-risk areas for brave players
- [ ] 4-6 new monsters added and balanced
- [ ] 40-60 new items added across all categories
- [ ] Lore items advance the campaign narrative
- [ ] All 504/504 tests still passing
- [ ] SESSION_ROADMAP.md updated with progress
- [ ] SESSION_ARCHIVE.md updated with detailed session history

---

## 🧪 **TESTING PROTOCOL**

Before and after every work session:

```bash
# 1. Run full test suite
python3 run_tests.py --no-web

# 2. Expected output:
# ✓ 504/504 tests passing (or higher with new tests)
# ✓ 0 failures
# ✓ 0 errors

# 3. If tests fail:
# - Read error messages carefully
# - Check if you introduced the failure
# - Fix before continuing work
# - NEVER commit code with failing tests
```

### Manual Testing Checklist (After Major Changes):

- [ ] Create new character (CLI)
- [ ] Create new party (CLI)
- [ ] Create new campaign (CLI)
- [ ] Complete Episode 1 (CLI)
- [ ] Save and exit (CLI)
- [ ] Load same campaign (Web UI)
- [ ] Verify Episode 1 complete (Web UI)
- [ ] Complete Episode 2 (Web UI)
- [ ] Save (Web UI)
- [ ] Load in CLI (CLI)
- [ ] Verify Episodes 1-2 complete (CLI)

---

## 📚 **KEY REFERENCE DOCUMENTS**

Keep these documents open during work sessions:

1. **This Document (SESSION_ROADMAP.md)** - Current priorities and next steps
2. **SESSION_ARCHIVE.md** - Detailed session histories with monster/item tables
3. **CAMPAIGN_TODO.md** - Detailed task breakdowns for content work
4. **cli_web_sync_issues.md** - UI synchronization specifications
5. **CLAUDE.md** - Development rules, architecture, testing requirements
6. **ARCHITECTURE.md** - System architecture and component relationships

### Quick Document Navigation:

```bash
# View document in terminal
cat SESSION_ROADMAP.md | less

# Search for specific task
grep -n "Task 1:" SESSION_ROADMAP.md

# View just Phase 1 tasks
sed -n '/PHASE 1:/,/PHASE 2:/p' SESSION_ROADMAP.md

# View detailed session histories
cat SESSION_ARCHIVE.md | less
```

---

## ⚠️ **CRITICAL DEVELOPMENT RULES**

From `CLAUDE.md` - **NEVER violate these:**

### 1. ALWAYS Run Tests Before and After Changes

```bash
python3 run_tests.py --no-web
```

### 2. NEVER Hardcode User-Defined Data

- Use `aerthos/constants.py` for all paths and configuration
- Use JSON data files for game content
- No hardcoded save directories, item stats, etc.

### 3. Keep CLI and Web UI in Sync

- Both must use identical core APIs
- Changes to `aerthos/` affect both interfaces
- Test both interfaces after core changes
- Document any intentional UX differences

### 4. Complete Feature Implementation Required

- Don't create placeholder/stub implementations
- If you start a feature, finish it fully
- This includes CLI, Web UI, and tests

### 5. Testing is Mandatory

- Write tests for new features
- Don't commit failing tests
- 504/504 tests must pass before ending session

---

## 🎯 **SESSION START CHECKLIST**

At the beginning of each work session:

- [ ] Navigate to project directory: `cd /mnt/d/Development/aerthos`
- [ ] Run tests: `python3 run_tests.py --no-web` (expect 504/504 pass)
- [ ] Review this document (SESSION_ROADMAP.md)
- [ ] Identify which Phase/Task you're working on
- [ ] Read the detailed task description
- [ ] Open reference documents as needed
- [ ] Confirm you understand acceptance criteria

**Current Phase:** Phase 4 - Task 1 COMPLETE | Decision point for next phase
**Current Task:** Choose: Phase 4 Tasks 2-5 (side quests, reputation) OR Phase 3 (Balance & Polish)
**Last Completed:** Phase 4 Task 1 - Episode 10 Expansion (Session 11, December 2, 2025)
**Next Action:** Decide between Phase 4 (Tasks 2-5) or Phase 3 (recommended: start Phase 3)
**Development Order:** Phase 1 ✅ → Phase 2 (80%) → Phase 4 Task 1 ✅ → Phase 3 (recommended next)

---

## 🎯 **SESSION END CHECKLIST**

At the end of each work session:

- [ ] Run tests: `python3 run_tests.py --no-web` (must pass)
- [ ] Update SESSION_ROADMAP.md progress section
- [ ] Update SESSION_ARCHIVE.md with detailed session history
- [ ] Document any new content (monsters, items) in archive
- [ ] Verify todo list reflects current state
- [ ] Git commit if appropriate
- [ ] Document any blockers or issues in this file

**Critical:**
- Don't commit failing tests
- Don't leave half-finished features
- 504/504 tests must pass before ending session

---

## 📝 **PROGRESS TRACKING**

### ✅ Phase 1 Progress (100% COMPLETE):

- [x] Task 1: Create Missing Monster Definitions (32/32 monsters) ← **DONE Session 1**
- [x] Task 2: Create Missing Item Definitions (23/23 items) ← **DONE Session 1-2**
- [x] Task 3: Implement Waterbreathing Mechanic (100%) ← **DONE Session 1**
- [x] Task 4: Automated Playthrough Tests (15/15 tests) ← **DONE Session 2**

### Phase 2 Progress (80% Complete):

- [x] Task 1: Create Episode Narrative Templates ← **DONE Session 2**
- [x] Task 2: Add Manual Save to CLI ← **DONE Session 2**
- [ ] Task 3: Test Cross-Compatibility (optional manual testing) ← **PENDING**

### Phase 3 Progress:

- [ ] Not started (waiting for Phase 4 completion)

### Phase 4 Progress (Task 1: 100% Complete):

- [x] **Task 1: Expand dungeons (9/9 complete = 100%)** ✅ **COMPLETE (Session 11)**
  - ✅ Episode 2: Oakhaven Sewers (5 → 18 rooms, +260% content)
  - ✅ Episode 3: Silas's Warehouse (6 → 18 rooms, +200% content)
  - ✅ Episode 4: Duergar Hold (6 → 18 rooms, +200% content)
  - ✅ Episode 5: Sunken Temple (6 → 18 rooms, +200% content)
  - ✅ Episode 6: Scorched Fortress (7 → 18 rooms, +157% content)
  - ✅ Episode 7: Drowned Ruins (6 → 18 rooms, +200% content)
  - ✅ Episode 8: Eldoria Catacombs (5 → 18 rooms, +260% content)
  - ✅ Episode 9: Elemental Chaos (7 → 18 rooms, +157% content)
  - ✅ Episode 10: The Serpent Temple (6 → 18 rooms, +200% content)
- [ ] Task 2: Add side quests and optional content
- [ ] Task 3: Implement reputation effects
- [ ] Task 4: Implement multiple endings for Episode 10
- [ ] Task 5: Add more character classes (optional)

---

## 🎯 **NEXT SESSION GOALS**

**Primary Goal:** ✅ **PHASE 4 TASK 1 COMPLETE** - All dungeons expanded!

**Accomplishment (Session 11):**
- ✅ Expanded Episode 10 (The Serpent Temple) from 6 → 18 rooms (+200%)
- ✅ Added 6 new monsters (serpent cult theme, final bosses)
- ✅ Added 62 new items (lore, treasure, quest items, legendary rewards)
- ✅ All 504/504 tests passing (no regressions)
- ✅ Phase 4 Task 1 marked COMPLETE in SESSION_ROADMAP.md

**Decision Point for Next Session:**
Choose one of the following paths:

**Option A: Continue Phase 4 (Tasks 2-5) - Add Depth**
- Task 2: Add side quests and optional content within episodes
- Task 3: Implement reputation effects (shop discounts, faction support)
- Task 4: Implement multiple endings for Episode 10
- Task 5: Add more character classes (optional)

**Option B: Begin Phase 3 - Balance & Polish**
- Balance economy (shop prices, loot drops, episode rewards)
- Tune combat difficulty across all 10 episodes
- Verify XP curve for full 1-10 progression
- Comprehensive playthrough and bug fixes

**Recommendation:** Start Phase 3 (Balance & Polish) since all content is now in place. Side quests and reputation effects (Phase 4 Tasks 2-5) could come after balancing as additional polish.

---

## 🆘 **TROUBLESHOOTING**

### Tests Failing?

1. Check error message carefully
2. Look for "ModuleNotFoundError" → Install requirements: `pip install -r requirements.txt`
3. Look for "FileNotFoundError" → Check you're in correct directory
4. Look for JSON syntax errors → Validate JSON files
5. Check `CLAUDE.md` Troubleshooting section

### Campaign Not Loading?

1. Check `~/.aerthos/campaigns/` directory exists
2. Check campaign JSON files are valid
3. Try creating new campaign from scratch

### Web UI Not Starting?

1. Install Flask: `pip install Flask`
2. Check port 5000 is not in use: `lsof -i :5000`
3. Try different port: `python3 web_ui/app.py --port 5001`

### Monsters/Items Not Loading?

1. Validate JSON syntax: `python3 -m json.tool aerthos/data/monsters.json`
2. Check for trailing commas (not allowed in JSON)
3. Check for missing closing braces
4. Use `GameData.load_all()` to test loading

---

## 📞 **GETTING HELP**

If stuck:

1. **Read the error message carefully** - It usually tells you what's wrong
2. **Check CLAUDE.md** - Has troubleshooting section
3. **Check ARCHITECTURE.md** - Understand system design
4. **Check existing code** - Look for similar implementations
5. **Run tests in verbose mode** - `python3 run_tests.py --no-web --verbose`
6. **Check SESSION_ARCHIVE.md** - See patterns from previous expansions

**Don't:**
- Guess at solutions without understanding the problem
- Skip testing to "save time"
- Hardcode values instead of using proper systems
- Create placeholders instead of complete implementations

---

## 🎉 **SUCCESS CRITERIA**

You'll know the project is in good shape when:

✅ **All 504+ tests passing** (run before and after every session)
✅ **Campaign playable start to finish** (Episode 1 → Episode 10)
✅ **No "monster not found" errors**
✅ **No "item not found" errors**
✅ **Both CLI and Web UI work identically**
✅ **Campaigns cross-compatible** (CLI ↔ Web UI)
✅ **Episode narratives display correctly** (intro and completion)
✅ **Manual save works in both interfaces**

When all these are true, the campaign is **production-ready**.

---

**Remember:** Quality over speed. Take time to understand systems before modifying them. Test after every change. Keep CLI and Web UI synchronized.

**Good luck, adventurer!** 🎲⚔️

---

**Document Version:** 2.0
**Created:** December 1, 2025
**Last Updated:** December 2, 2025 - Session 7 Complete
**For:** Claude Code sessions working on Aerthos campaign
**Detailed Session Histories:** See SESSION_ARCHIVE.md
