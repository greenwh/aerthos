# AERTHOS CAMPAIGN - COMPREHENSIVE TODO & INCOMPLETE FEATURES

**Last Updated:** December 1, 2025
**Campaign Status:** Episodes 1-10 created (functional stubs)
**Test Status:** 473/473 tests passing (100%)

---

## 📋 TABLE OF CONTENTS

1. [Functional Stubs - Dungeons](#functional-stubs---dungeons)
2. [Incomplete Features](#incomplete-features)
3. [Missing Systems](#missing-systems)
4. [Monster Definitions Needed](#monster-definitions-needed)
5. [Item Definitions Needed](#item-definitions-needed)
6. [Testing & Balance](#testing--balance)
7. [Polish & Enhancement](#polish--enhancement)
8. [Known Issues](#known-issues)

---

## 🏰 FUNCTIONAL STUBS - DUNGEONS

**What is a "Functional Stub"?**
A dungeon with 5-7 rooms that is **fully playable** but **minimal**. Has entrance, middle section, boss room with key item. Story beats work. Can be expanded to 15-30 rooms later.

### ❌ EPISODE 2: Oakhaven Sewers (STUB - 5 rooms)
**File:** `aerthos/data/dungeons/oakhaven_sewers.json`
**Current State:** Functional stub with 5 rooms
**Target State:** Full dungeon with 18-20 rooms

**Expansion Task:**
```
CONTEXT: Episode 2 takes place in sewers beneath Oakhaven where a cult
has been kidnapping townsfolk. Current dungeon has minimal rooms to tell
the story. Needs expansion for better exploration experience.

GOAL: Expand from 5 rooms to 18-20 rooms

WHAT TO ADD:
- More sewer tunnels with branching paths
- Rat warren side area (giant rats, loot)
- Collapsed section (requires climbing/strength check)
- Torture chamber (flavor, clues about cult)
- Secret cult altar (hidden passage, bonus loot)
- Lower level with escape route
- More varied encounters (not just combat - traps, puzzles)

HOW TO EXECUTE:
1. Read current file: aerthos/data/dungeons/oakhaven_sewers.json
2. Keep existing 5 rooms (entrance, main_tunnel, storage, prison, ritual)
3. Add new rooms between entrance and ritual chamber
4. Update "exits" fields to connect new rooms
5. Add variety:
   - 60% combat encounters
   - 20% traps/hazards
   - 20% empty (tension/exploration)
6. Place additional loot in side paths (not required for progression)
7. Test: Can still complete episode with minimal path (5 rooms)
8. Test: Full exploration yields better rewards

ACCEPTANCE CRITERIA:
- [ ] 18-20 total rooms
- [ ] Multiple paths to reach ritual chamber
- [ ] At least 2 optional side areas with bonus loot
- [ ] Boss fight unchanged (Cultist Fanatic)
- [ ] Episode 2 completion still works
```

---

### ❌ EPISODE 3: Silas's Warehouse (STUB - 6 rooms)
**File:** `aerthos/data/dungeons/silas_warehouse.json`
**Current State:** Functional stub with 6 rooms
**Target State:** Full dungeon with 15-18 rooms

**Expansion Task:**
```
CONTEXT: Silas's underground warehouse and smuggling operation. Should
feel like a criminal empire's lair - multiple levels, trapped vaults,
contraband storage, escape tunnels to sewers.

GOAL: Expand from 6 rooms to 15-18 rooms

WHAT TO ADD:
- Multiple warehouse sections (weapons, cursed goods, slaves)
- Guard patrols (make it feel like an active operation)
- Trapped treasure vaults (Silas is paranoid)
- Secret passages and escape routes
- Smuggling tunnel network connecting to sewers
- Silas's personal quarters (clues, lore, journal entries)
- False vault (trap for intruders)

HOW TO EXECUTE:
1. Read: aerthos/data/dungeons/silas_warehouse.json
2. Keep core path: hidden_entrance → main_warehouse → silas_hideout
3. Add warehouse wings (north/south/east expansions)
4. Add guard rotations (some rooms have patrols, others empty)
5. Add more traps (Silas is clever, would protect his assets)
6. Create multi-level layout (upper warehouse, lower tunnels, hidden vault)
7. Add environmental storytelling (ledgers, correspondencecult documents)

ACCEPTANCE CRITERIA:
- [ ] 15-18 total rooms
- [ ] At least 3 trapped rooms (poison darts, pits, alarms)
- [ ] Multiple paths through warehouse
- [ ] Silas boss fight unchanged
- [ ] Lore documents revealing cult conspiracy
```

---

### ❌ EPISODE 4: Duergar-Occupied Hold (STUB - 6 rooms)
**File:** `aerthos/data/dungeons/duergar_hold.json`
**Current State:** Functional stub with 6 rooms
**Target State:** Full dungeon with 20-25 rooms

**Expansion Task:**
```
CONTEXT: A dwarven fortress taken over by duergar (gray dwarves). Should
feel like a once-proud hold now corrupted. Dwarven architecture,
defenses, forges, but defiled by invaders.

GOAL: Expand from 6 rooms to 20-25 rooms

WHAT TO ADD:
- Dwarven great hall with clan histories
- Multiple forge levels (master forge, apprentice forges)
- Barracks for both dwarves (corpses) and duergar (active)
- Armory with dwarven weapons/armor (some trapped)
- Mining tunnels leading to Underdark (where duergar came from)
- Memorial hall (dwarven dead honored, now desecrated)
- Prison cells (captured dwarves waiting rescue)
- False vault (decoy to protect real vault)
- Throne room (clan leader's corpse, used by Grathak)

HOW TO EXECUTE:
1. Read: aerthos/data/dungeons/duergar_hold.json
2. Keep linear path to deep_vault
3. Add horizontal expansions at each level
4. Include dwarven flavor: stone carvings, clan symbols, work areas
5. Add tragedy: dead dwarves, signs of heroic last stands
6. Show duergar occupation: serpent symbols, dark magic corruption
7. Add rescued NPCs (surviving dwarves who join you temporarily)

ACCEPTANCE CRITERIA:
- [ ] 20-25 total rooms
- [ ] Dwarven cultural details throughout
- [ ] At least 5 rooms showing the battle (corpses, destroyed defenses)
- [ ] Optional: Rescue 2-3 imprisoned dwarves (side quest)
- [ ] Boss (Grathak) unchanged
- [ ] Second Key reward unchanged
```

---

### ❌ EPISODE 5: Sunken Temple (STUB - 6 rooms)
**File:** `aerthos/data/dungeons/sunken_temple.json`
**Current State:** Functional stub with 6 rooms
**Target State:** Full dungeon with 25-30 rooms

**Expansion Task:**
```
CONTEXT: Ancient temple rising from swamp, dedicated to forgotten gods,
now corrupted by Serpent Eye cult. Should feel alien, ancient, dangerous.
Water everywhere, serpent imagery, cultist activity.

GOAL: Expand from 6 rooms to 25-30 rooms

WHAT TO ADD:
- Multiple levels (ground floor, flooded lower levels, dry upper shrine)
- Serpent statue gallery (living statues that attack)
- Meditation chambers (empty, atmospheric)
- Sacrificial chambers (recent cult activity)
- Ancient library (waterlogged but some scrolls intact)
- Priest's quarters (ancient inhabitants, clues to temple's purpose)
- Crypt of high priests (undead guardians)
- Secret treasure vault (hidden behind puzzle)
- Flooded maze (navigation challenge)

HOW TO EXECUTE:
1. Read: aerthos/data/dungeons/sunken_temple.json
2. Design vertical layout (4 levels as specified)
3. Add water hazards (drowning checks, water elementals)
4. Include ancient lore (what was this place before?)
5. Show cult corruption (recent changes vs ancient design)
6. Add environmental puzzles (water flow, pressure plates, statues)
7. Include marsh creatures (not just cultists)

ACCEPTANCE CRITERIA:
- [ ] 25-30 total rooms
- [ ] 4 distinct levels with different themes
- [ ] At least 2 environmental puzzles
- [ ] Mix of ancient guardians and modern cultists
- [ ] Lore about temple's original purpose
- [ ] Boss (High Priest Korvash) unchanged
- [ ] Third Key reward unchanged
```

---

### ❌ EPISODE 6: Scorched Fortress (STUB - 7 rooms)
**File:** `aerthos/data/dungeons/scorched_fortress.json`
**Current State:** Functional stub with 7 rooms
**Target State:** Full dungeon with 18-22 rooms

**Expansion Task:**
```
CONTEXT: Orcish fortress built on volcanic rock, taken over by cult.
Should feel brutal—orc architecture, heat, lava, signs of the battle
where orcs were driven out. Alliance with orcs means rescued NPCs.

GOAL: Expand from 7 rooms to 18-22 rooms

WHAT TO ADD:
- Multiple courtyards and defensive walls
- Orc great hall with trophies and clan histories
- Volcanic caves beneath fortress (lava hazards)
- Prison cells with captured orcs (rescue opportunity)
- Armory with orcish weapons
- War room with battle plans (both orc and cult)
- Smithy (still burning, used by cult)
- Sleeping quarters for both orcs (corpses) and cultists
- Ritual chambers where cult prepared dark magic

HOW TO EXECUTE:
1. Read: aerthos/data/dungeons/scorched_fortress.json
2. Design fortress layout (walls, towers, keep)
3. Add environmental hazards (lava flows, heat damage, unstable ground)
4. Show orc culture (not just savage—organized, honor-based)
5. Add rescued orc NPCs who fight with you
6. Include cult corruption (serpent symbols over orcish ones)
7. Make it feel like a siege reclamation (Urgot's warriors help)

ACCEPTANCE CRITERIA:
- [ ] 18-22 total rooms
- [ ] Volcanic hazards (lava, heat, gases)
- [ ] At least 3 orc NPCs can be rescued (buff your party)
- [ ] Orcish cultural details (totems, trophies, murals)
- [ ] Boss (Cult General Malakar) unchanged
- [ ] Fourth Key reward unchanged
```

---

### ❌ EPISODE 7: Drowned Ruins of Ys'Thara (STUB - 6 rooms)
**File:** `aerthos/data/dungeons/drowned_ruins.json`
**Current State:** Functional stub with 6 rooms
**Target State:** Full dungeon with 30 rooms

**Expansion Task:**
```
CONTEXT: Underwater city ruins, ancient and cursed. Was sunk 1000 years
ago for dabbling in dark magic. Now rising due to cult activity. Requires
waterbreathing. Should feel alien, claustrophobic, haunted.

GOAL: Expand from 6 rooms to 30 rooms

WHAT TO ADD:
- Ruined city districts (residential, commercial, noble quarter)
- Collapsed buildings (navigation challenges)
- Coral-covered monuments and statues
- Ancient palace (pre-cult history, lore)
- Creature lairs (giant octopus, sharks, aberrations)
- Sunken ships (explorers who didn't return)
- Temple districts (multiple temples, not just Serpent)
- Ancient treasury (looted but still valuable)
- Aboleth lair (aberration that remembers the city's fall)

HOW TO EXECUTE:
1. Read: aerthos/data/dungeons/drowned_ruins.json
2. Design as underwater city (3D space, vertical movement)
3. Add visibility mechanics (murky water limits sight)
4. Include ancient lore (why did city sink? What was the crime?)
5. Add underwater combat challenges (movement penalties, special weapons)
6. Show cult operation (diving bells, excavation sites, recent disturbance)
7. Include aboleth subplot (ancient creature knows the truth)

ACCEPTANCE CRITERIA:
- [ ] 30 total rooms
- [ ] Underwater mechanics (movement, visibility, combat modifiers)
- [ ] Ancient city lore revealed through exploration
- [ ] Aboleth encounter (optional mini-boss with knowledge)
- [ ] Boss (High Priest Morvathis) unchanged
- [ ] Fifth Key + Serpent's Fang rewards unchanged
```

---

### ❌ EPISODE 8: Eldoria Catacombs (STUB - 5 rooms)
**File:** `aerthos/data/dungeons/eldoria_catacombs.json`
**Current State:** Functional stub with 5 rooms
**Target State:** Full dungeon with 20-25 rooms

**Expansion Task:**
```
CONTEXT: Ancient burial tunnels beneath capital city, used by corrupt
Syndic for devil-worship and dark rituals. Should feel like a necropolis
turned into a cult headquarters.

GOAL: Expand from 5 rooms to 20-25 rooms

WHAT TO ADD:
- Multiple burial chambers (noble tombs, mass graves)
- Ossuary (walls of bones)
- Cult living quarters (they've been here for years)
- Ritual chambers (multiple, showing progression of rituals)
- Devil summoning circles
- Underground river (connection to city sewers)
- Secret passages to Krane's estate
- Treasure vaults (Krane's stolen wealth)
- Trapped corridors (Krane is paranoid)

HOW TO EXECUTE:
1. Read: aerthos/data/dungeons/eldoria_catacombs.json
2. Design as multi-level catacombs (ancient → modern cult additions)
3. Show age layers (oldest sections vs recent construction)
4. Add undead encounters (ancient guardians vs cult necromancy)
5. Include devil-cult elements (pentagrams, infernal contracts, sacrifices)
6. Add political intrigue clues (who else in government is compromised?)
7. Make it feel like Krane's secret headquarters (not just a dungeon)

ACCEPTANCE CRITERIA:
- [ ] 20-25 total rooms
- [ ] Multiple levels showing different time periods
- [ ] Devil-worship elements throughout
- [ ] Evidence of Krane's political machinations
- [ ] Boss (Valerius Krane + Barbed Devil) unchanged
- [ ] Sixth + Seventh Keys unchanged
```

---

### ❌ EPISODE 9: Elemental Chaos (STUB - 7 rooms)
**File:** `aerthos/data/dungeons/elemental_chaos.json`
**Current State:** Functional stub with 7 rooms
**Target State:** Full dungeon with 20 rooms

**Expansion Task:**
```
CONTEXT: Pocket dimension where elements clash. Reality is unstable,
physics don't apply normally. Four keystones must be destroyed before
confronting the Herald. Should feel surreal, dangerous, otherworldly.

GOAL: Expand from 7 rooms to 20 rooms

WHAT TO ADD:
- Elemental transition zones (fire/water borders, paradoxes)
- Gravity-shifting areas
- Time-distorted chambers (speed up, slow down)
- Elemental creature lairs (genies, mephits, elementals)
- Elemental puzzles (use one element to reach another)
- Chaos rifts (random encounters, unstable terrain)
- Elemental throne rooms (where keystones are kept)
- Safe zones (pockets of stability)

HOW TO EXECUTE:
1. Read: aerthos/data/dungeons/elemental_chaos.json
2. Design four elemental quadrants (fire, water, earth, air)
3. Add transition zones where elements clash
4. Include physics-defying mechanics (gravity, time, space)
5. Make it disorienting but navigable
6. Add environmental hazards specific to each element
7. Ensure all 4 keystones must be destroyed before Herald appears

ACCEPTANCE CRITERIA:
- [ ] 20 total rooms
- [ ] Four distinct elemental zones
- [ ] Reality-warping mechanics (gravity, time, physics)
- [ ] Elemental-specific hazards and puzzles
- [ ] Herald chamber only accessible after 4 keystones destroyed
- [ ] Boss (Elemental Herald) unchanged
- [ ] Eighth + Ninth Keys unchanged
```

---

### ❌ EPISODE 10: Serpent Temple (STUB - 6 rooms)
**File:** `aerthos/data/dungeons/serpent_temple.json`
**Current State:** Functional stub with 6 rooms
**Target State:** Full dungeon with 35 rooms

**Expansion Task:**
```
CONTEXT: Final dungeon. Corrupted temple in burning Oakhaven where the
ultimate ritual is taking place. Should feel epic, desperate, climactic.
This is where it all ends.

GOAL: Expand from 6 rooms to 35 rooms

WHAT TO ADD:
- Multiple approach routes (frontal assault, stealth, underground)
- Burning town sections (environmental hazards)
- Cultist army staging areas
- Prisoner rescue (Oakhaven citizens)
- Temple levels (basement crypts, ground floor, upper shrine)
- Ritual preparation chambers
- Artifact storage (all the cult's accumulated power)
- Boss lieutenant chambers (multiple tough fights before final boss)
- Alternative endings chambers (different paths change outcome)
- Collapsing temple escape sequence (after defeating boss)

HOW TO EXECUTE:
1. Read: aerthos/data/dungeons/serpent_temple.json
2. Design as epic final dungeon (largest, hardest, most rewarding)
3. Include multiple difficulty spikes (mini-bosses before final boss)
4. Add alternative paths (different approaches, different challenges)
5. Include callbacks to earlier episodes (NPCs, items, locations)
6. Make environmental storytelling show the stakes (burning town, rituals)
7. Implement multiple ending possibilities (heroic, pyrrhic, dark bargain)

ACCEPTANCE CRITERIA:
- [ ] 35 total rooms (largest dungeon in campaign)
- [ ] Multiple approaches to final confrontation
- [ ] At least 3 lieutenant bosses before final boss
- [ ] NPCs from earlier episodes appear (Guide, rescued people, allies)
- [ ] Multiple endings based on choices/performance
- [ ] Boss (Serpent's Voice) unchanged
- [ ] All 10 keys destroyed, campaign complete
```

---

## ❌ INCOMPLETE FEATURES

### Character Creation - Limited Classes
**Current State:** 4 classes implemented (Fighter, Cleric, Magic-User, Thief)
**Missing:** 7 additional AD&D 1e classes
**Files:** `aerthos/data/classes.json`, `aerthos/ui/character_creation.py`

**Task:**
```
CONTEXT: AD&D 1e has 11 base classes. Currently only 4 are implemented.
Missing classes would add variety and replayability.

MISSING CLASSES:
1. Paladin (Fighter subclass, Lawful Good only, special abilities)
2. Ranger (Fighter subclass, any Good alignment, wilderness skills)
3. Druid (Cleric subclass, True Neutral only, nature magic)
4. Illusionist (Magic-User subclass, illusion spells)
5. Assassin (Thief subclass, Evil only, poison/disguise)
6. Monk (unique class, martial arts, ki powers)
7. Bard (multi-class, music magic, lore)

HOW TO EXECUTE:
1. Read: aerthos/data/classes.json (see existing class format)
2. For each missing class:
   - Add entry to classes.json with stats, restrictions, abilities
   - Update aerthos/ui/character_creation.py to show new classes
   - Add class-specific abilities to aerthos/systems/class_abilities.py
   - Update tests in tests/test_character_creation.py
3. Implement special mechanics:
   - Paladin: Lay on hands, detect evil, disease immunity
   - Ranger: Track, two-weapon fighting, woodland stealth
   - Druid: Wild shape, weather magic, animal companion
   - Monk: Unarmed damage, speed increase, stunning fist
   - Etc.

ACCEPTANCE CRITERIA:
- [ ] All 11 classes available in character creation
- [ ] Class restrictions enforced (alignment, race limitations)
- [ ] Special abilities implemented for each class
- [ ] Tests pass for all new classes
- [ ] Web UI shows all classes correctly
```

---

### Money System - Backward Compatibility Issues
**Current State:** New multi-coin system implemented, but old `.gold` attribute still exists for backward compatibility
**Issue:** Some code paths may still use `.gold` instead of new methods
**Files:** All campaign/hub interfaces, save/load system

**Task:**
```
CONTEXT: The money system was refactored from single "gold" to multi-coin
(copper, silver, electrum, gold, platinum). Some code still uses old ".gold"
attribute for backward compatibility, but this should be phased out.

GOAL: Remove backward compatibility, fully migrate to new system

HOW TO EXECUTE:
1. Search codebase for ".gold" usage:
   grep -r "\.gold" aerthos/ --include="*.py"
2. For each occurrence:
   - If setting gold: Use add_money(gp=amount)
   - If deducting gold: Use subtract_money(gp=amount) with check
   - If getting total: Use get_total_money()
3. Remove the "gold" field from PlayerCharacter dataclass
4. Update save/load to not save/load .gold field
5. Update all character creation to use add_money(gp=X) for starting gold
6. Run tests to ensure nothing breaks

ACCEPTANCE CRITERIA:
- [ ] No code uses ".gold" attribute
- [ ] All transactions use get_total_money(), add_money(), subtract_money()
- [ ] Old save files still load (with .gold converted to gold_pieces)
- [ ] All tests pass
```

---

### Campaign Save System - Missing Auto-Save
**Current State:** Manual save button exists in web UI
**Missing:** Auto-save on episode completion, periodic checkpoints
**Files:** `web_ui/app.py`, `aerthos/campaign/campaign_manager.py`

**Task:**
```
CONTEXT: Players can manually save via button, but there's no auto-save.
If they forget to save and crash/quit, they lose progress.

GOAL: Implement auto-save on key events

EVENTS THAT SHOULD AUTO-SAVE:
1. Episode completion
2. Entering a new city hub
3. Every 10 turns in dungeon
4. After boss defeat
5. On character level up

HOW TO EXECUTE:
1. Create auto-save function in campaign_manager.py:
   def auto_save_campaign(campaign, party, session, reason):
       # Save campaign, party, and session
       # Log: "Auto-saved: {reason}"
2. Add hooks in episode_runner.py:
   - After episode completion
   - After boss defeated
3. Add hooks in game_state.py:
   - Every 10 turns (track turn counter)
   - On level up
4. Add hooks in hub_menu.py:
   - When entering hub menu
5. Web UI: Show "Auto-saved" message (non-intrusive)

ACCEPTANCE CRITERIA:
- [ ] Auto-save on all key events listed
- [ ] Auto-save doesn't interrupt gameplay
- [ ] Web UI shows "Auto-saved" notification
- [ ] Manual save still works
- [ ] Auto-save files are marked (timestamp, reason)
```

---

### Web UI - Missing Campaign Selection on Home
**Current State:** Can create/load campaigns via API, but no UI for it on home screen
**Missing:** Campaign selection interface on main menu
**Files:** `web_ui/templates/index.html`, `web_ui/app.py`

**Task:**
```
CONTEXT: Web UI has basic game interface, but no campaign selection screen.
Users can't easily start or load campaigns from the UI.

GOAL: Add campaign management to home screen

WHAT TO ADD:
1. "Campaign Mode" section on index.html
2. "New Campaign" button (shows available templates)
3. "Continue Campaign" button (shows saved campaigns)
4. Campaign info display (name, progress, last played)

HOW TO EXECUTE:
1. Add API endpoints (if missing):
   - GET /api/campaigns/templates (list available campaigns)
   - GET /api/campaigns/saves (list saved campaigns)
2. Update web_ui/templates/index.html:
   - Add "Campaign Mode" section
   - Add buttons and JavaScript for campaign selection
3. Create campaign selection modal:
   - Shows template description
   - Shows recommended party size/level
   - "Start Campaign" button
4. Create campaign continue modal:
   - Shows campaign name, progress (X/10 episodes)
   - Shows last played time
   - "Continue" button loads campaign and redirects to hub

ACCEPTANCE CRITERIA:
- [ ] Home screen has "Campaign Mode" section
- [ ] Can start new campaign from UI
- [ ] Can continue existing campaign from UI
- [ ] Campaign info displayed clearly
- [ ] Redirects to hub menu on load
```

---

## ❌ MISSING SYSTEMS

### Reputation System - No Gameplay Effects
**Current State:** Reputation tracks numerically but doesn't affect anything
**Missing:** Discounts, quest unlocks, dialogue changes, faction support
**Files:** Campaign classes, hub interfaces, shop/inn/temple interfaces

**Task:**
```
CONTEXT: Factions track reputation (0-100 scale), but it's purely cosmetic.
High reputation should provide benefits; low reputation should have consequences.

GOAL: Implement reputation effects

REPUTATION TIERS:
- Hostile (<-50): Attacked on sight, no services
- Unfriendly (-50 to -1): Prices +50%, no special services
- Neutral (0-24): Normal prices, basic services only
- Friendly (25-49): Prices -10%, some special services
- Honored (50-74): Prices -20%, most special services, bonus quests
- Revered (75-99): Prices -30%, all services, faction aid in combat
- Exalted (100+): Prices -50%, unique rewards, permanent allies

HOW TO EXECUTE:
1. Update shop interfaces to check reputation:
   ```python
   def get_price_modifier(self, character):
       reputation = character.get_reputation(self.faction_id)
       if reputation < -50: return None  # Won't sell
       if reputation < 0: return 1.5
       if reputation < 25: return 1.0
       if reputation < 50: return 0.9
       if reputation < 75: return 0.8
       if reputation < 100: return 0.7
       return 0.5
   ```
2. Update temple/inn similarly
3. Add faction support in combat:
   - If reputation >= 75, faction sends reinforcements
   - Example: Bloodfang orcs join final battle if reputation high
4. Add reputation-gated quests (require friendly+ to unlock)
5. Add dialogue variations based on reputation

ACCEPTANCE CRITERIA:
- [ ] Shop prices modified by reputation
- [ ] Temple/inn prices modified by reputation
- [ ] Reputation >= 75 unlocks faction combat support
- [ ] Reputation-gated content works (quests, items, services)
- [ ] All reputation tiers implemented and tested
```

---

### Multiple Endings - Not Implemented
**Current State:** Episode 10 JSON has "multiple_endings" field but system doesn't use it
**Missing:** Ending logic based on player choices/performance
**Files:** `aerthos/campaign/episode_runner.py`, final dungeon logic

**Task:**
```
CONTEXT: Episode 10 defines multiple endings (heroic, pyrrhic, dark bargain)
but the system doesn't track conditions or show different endings.

GOAL: Implement multiple endings system

ENDINGS DEFINED:
1. Heroic Victory: All party alive, boss defeated quickly
2. Pyrrhic Victory: Party members died but won
3. Dark Bargain: Used Serpent's Fang artifact in final battle

HOW TO EXECUTE:
1. Create ending tracker in episode_runner.py:
   ```python
   class EndingTracker:
       def __init__(self):
           self.party_deaths = 0
           self.rounds_to_victory = 0
           self.artifacts_used = []

       def determine_ending(self, episode):
           if episode.get('multiple_endings'):
               # Check conditions
               if all party alive and rounds < 20:
                   return 'heroic_victory'
               elif 'serpents_fang' in artifacts_used:
                   return 'dark_bargain'
               else:
                   return 'pyrrhic_victory'
   ```
2. Track combat rounds in combat.py
3. Track party deaths during episode
4. Track artifact usage
5. At episode completion, check ending conditions
6. Display appropriate ending text
7. Award ending-specific rewards/titles

ACCEPTANCE CRITERIA:
- [ ] Combat rounds tracked during boss fight
- [ ] Party deaths tracked during episode
- [ ] Artifact usage tracked
- [ ] Correct ending displayed based on conditions
- [ ] Ending-specific rewards given
- [ ] Web UI shows ending cutscene/text
```

---

## ❌ MONSTER DEFINITIONS NEEDED

**Current State:** Episodes reference monsters that don't exist in `monsters.json`
**Impact:** Episodes will crash if played because monsters can't be spawned
**Files:** `aerthos/data/monsters.json`

### Missing Boss Monsters
```
CONTEXT: All episode dungeons reference boss monsters that need to be
defined in monsters.json with proper stats, abilities, and treasure.

MONSTERS TO CREATE:
1. cultist_fanatic (Episode 2 boss)
2. silas_merchant (Episode 3 boss)
3. grathak_soulless (Episode 4 boss)
4. high_priest_korvash (Episode 5 boss)
5. cult_general_malakar (Episode 6 boss)
6. morvathis_high_priest (Episode 7 boss)
7. valerius_krane (Episode 8 boss)
8. barbed_devil (Episode 8 ally)
9. elemental_herald (Episode 9 boss)
10. serpents_voice (Episode 10 final boss)

HOW TO EXECUTE:
1. Read: aerthos/data/monsters.json (see format)
2. For each boss, create entry:
   ```json
   "boss_id": {
       "name": "Boss Name",
       "hit_dice": "8+2",  // Boss level appropriate
       "ac": 2,  // Lower is better (harder to hit)
       "thac0": 12,  // Lower is better (hits more)
       "damage": "2d8+2",  // Boss-level damage
       "size": "M",
       "movement": 12,
       "xp_value": 1500,  // Episode-appropriate XP
       "ai_behavior": "aggressive",
       "special_abilities": ["spell_casting", "fear_aura"],
       "treasure_type": "E",  // Good treasure
       "description": "Flavor text...",
       "boss": true
   }
   ```
3. Balance HP, AC, damage for episode level:
   - Episode 2 (lvl 2): HD 3-4, AC 5-6, THAC0 17-18
   - Episode 5 (lvl 5): HD 6-7, AC 2-3, THAC0 13-14
   - Episode 10 (lvl 10): HD 12-15, AC -2, THAC0 8-9

ACCEPTANCE CRITERIA:
- [ ] All 10+ boss monsters defined
- [ ] Stats balanced for episode level
- [ ] Special abilities defined (if any)
- [ ] XP and treasure appropriate
- [ ] Tests can spawn all bosses
```

### Missing Regular Monsters
```
MONSTERS REFERENCED BUT NOT DEFINED:
- sahuagin (underwater humanoids, Episode 7)
- giant_octopus (Episode 7)
- cultist_diver (Episode 7)
- aboleth_spawn (Episode 7)
- cultist_guard (Episodes 3, 8)
- cultist_elite (Episodes 6, 8, 10)
- cultist_sorcerer (Episodes 8, 9)
- skeleton (Episode 8)
- zombie (Episode 8)
- marsh_zombie (Episode 5)
- imp (Episode 8)
- fire_elemental (Episodes 6, 9)
- water_elemental (Episodes 5, 9)
- earth_elemental (Episode 9)
- air_elemental (Episode 9)
- cult_pyromancer_transformed (Episode 9)
- cult_hydromancer_transformed (Episode 9)
- cult_geomancer_transformed (Episode 9)
- cult_aeromancer_transformed (Episode 9)
- summoned_demon (Episode 10)

Same process as bosses, but with lower stats for regular encounters.
```

---

## ❌ ITEM DEFINITIONS NEEDED

**Current State:** Episodes reward items that don't exist in item data files
**Impact:** Items won't appear in inventory, rewards will fail
**Files:** `aerthos/data/weapons.json`, `armor.json`, `equipment.json`, `magic_items.json`

### Missing Reward Items
```
CONTEXT: Episodes give unique rewards that need to be defined.

ITEMS TO CREATE:
1. dagger_plus_1 (Episode 1 reward)
2. mace_plus_1 (Episode 2 reward)
3. ring_protection_1 (Episode 3 reward)
4. dwarven_waraxe_plus_1 (Episode 4 reward)
5. staff_serpents (Episode 5 reward)
6. orcish_greataxe_plus_2 (Episode 6 reward)
7. serpents_fang (Episode 7 reward - major artifact)
8. amulet_waterbreathing (Episode 7 reward)
9. ring_spell_turning (Episode 8 reward)
10. cloak_protection_plus_2 (Episode 8 reward)
11. staff_elemental_mastery (Episode 9 reward)
12. boots_levitation (Episode 9 reward)
13. legendary_weapon_choice (Episode 10 reward - player chooses)

HOW TO EXECUTE:
1. For weapons, add to aerthos/data/weapons.json:
   ```json
   "dagger_plus_1": {
       "name": "Dagger +1",
       "type": "weapon",
       "damage_sm": "1d4+1",
       "damage_l": "1d3+1",
       "weight_gp": 10,
       "cost_gp": 1000,
       "magic_bonus": 1,
       "description": "A finely crafted dagger with a magical edge."
   }
   ```
2. For armor/accessories, add to armor.json or equipment.json
3. For major artifacts, add to magic_items.json with special powers:
   ```json
   "serpents_fang": {
       "name": "The Serpent's Fang",
       "type": "artifact",
       "slot": "weapon",
       "powers": [
           "Deals 3d6 damage (vorpal)",
           "Cast fear once per day",
           "Wielder gains poison immunity"
       ],
       "curse": "Each use drains 1 HP permanently",
       "description": "An ancient blade of terrible power..."
   }
   ```

ACCEPTANCE CRITERIA:
- [ ] All 13+ reward items defined
- [ ] Stats appropriate for episode level
- [ ] Magic items have powers defined
- [ ] Legendary weapon choice gives 3+ options
- [ ] Items appear correctly in inventory
```

---

## ❌ TESTING & BALANCE

### Episode Playtesting - None Done
**Current State:** Episodes created but never played through
**Risk:** Difficulty spikes, softlocks, broken progression
**Required:** Full playthrough testing

**Task:**
```
CONTEXT: All 10 episodes exist on paper but haven't been played. Need to
verify they're actually fun and balanced.

GOAL: Complete playthrough test of all 10 episodes

HOW TO EXECUTE:
1. Create test party (4 characters, mixed classes)
2. Start campaign from Episode 1
3. Play through each episode in order:
   - Note difficulty spikes
   - Check if rewards feel appropriate
   - Verify story makes sense
   - Test that progression unlocks work
4. Document issues:
   - Encounters too easy/hard
   - Rewards insufficient/excessive
   - Story gaps or confusion
   - Technical bugs (crashes, softlocks)
5. Balance adjustments:
   - Encounter difficulty
   - XP/gold rewards
   - Item placement
   - Monster stats

ACCEPTANCE CRITERIA:
- [ ] All 10 episodes completed in sequence
- [ ] No softlocks or progression blockers
- [ ] Difficulty curve feels appropriate
- [ ] Story flows logically episode-to-episode
- [ ] Rewards feel satisfying
- [ ] Document created with balance notes
```

---

### Economy Balance - Unchecked
**Current State:** Gold rewards and shop prices set arbitrarily
**Risk:** Too much gold (trivialize challenge) or too little (frustration)
**Required:** Economic balance pass

**Task:**
```
CONTEXT: Shops have prices, episodes give gold, but has this been balanced?
Do players have enough gold to buy needed items? Too much so it's meaningless?

GOAL: Balance the in-game economy

DATA TO COLLECT:
1. Total gold earned Episodes 1-10:
   - Episode rewards
   - Monster treasure
   - Found gold
2. Essential purchases:
   - Healing potions
   - Resurrections
   - Equipment upgrades
   - Inn/temple services
3. Optional purchases:
   - Magic items
   - High-end equipment
   - Convenience items

HOW TO EXECUTE:
1. Calculate total gold available (sum all episode rewards + average loot)
2. Calculate essential costs (healing, resurrections, basic equipment)
3. Ensure: Total Gold >= Essential Costs * 2
4. Adjust if needed:
   - Increase episode rewards if players are poor
   - Decrease shop prices if items are unaffordable
   - Add more loot to dungeons if gold-starved
5. Test with playthrough (track party gold at each episode)

ACCEPTANCE CRITERIA:
- [ ] Players can afford essential purchases at all times
- [ ] Players must choose between some optional purchases (scarcity)
- [ ] End-game players have moderate wealth (not swimming in gold)
- [ ] Economy feels balanced and fair
```

---

## ❌ POLISH & ENHANCEMENT

### Dungeon Descriptions - Minimal
**Current State:** Most rooms have 1-2 sentence descriptions
**Opportunity:** Rich, atmospheric descriptions enhance immersion
**Files:** All dungeon JSON files

**Task:**
```
CONTEXT: Current room descriptions are functional but sparse. Players
deserve evocative, atmospheric descriptions that bring dungeons to life.

GOAL: Enhance all room descriptions

WHAT TO ADD:
- Sensory details (sights, sounds, smells)
- Environmental storytelling (what happened here?)
- Mood and atmosphere
- Tactical information (cover, hazards, escape routes)

EXAMPLE TRANSFORMATION:
Before: "A dark room with goblins."
After: "The chamber reeks of unwashed bodies and rotting meat. Crude
bedrolls and scattered bones litter the floor. Three goblins hunker around
a dying fire, their yellow eyes gleaming in the darkness. They turn as you
enter, reaching for rusty blades with surprising speed. Exits: north, east."

HOW TO EXECUTE:
1. For each dungeon, read through all room descriptions
2. Expand each to 3-5 sentences:
   - First sentence: Visual overview
   - Second sentence: Atmospheric details
   - Third sentence: Interactive elements (enemies, loot, hazards)
   - Fourth sentence: Tactical layout (exits, cover, height)
3. Maintain consistency in tone per dungeon (sewers = filth, temple = grandeur)
4. Don't spoil surprises (don't mention hidden things in description)

ACCEPTANCE CRITERIA:
- [ ] All rooms have 3-5 sentence descriptions
- [ ] Descriptions evoke appropriate atmosphere
- [ ] Sensory details included (not just visual)
- [ ] Tactical information present
- [ ] Tone consistent within each dungeon
```

---

### NPC Dialogue - Basic
**Current State:** NPCs have 2-3 dialogue lines
**Opportunity:** Rich dialogue makes NPCs memorable
**Files:** All city hub JSON files

**Task:**
```
CONTEXT: NPCs give quests and services but feel flat. More dialogue
options would make them feel alive.

GOAL: Expand NPC dialogue trees

WHAT TO ADD:
- Greetings (vary based on reputation, story progress)
- About themselves (backstory, motivations)
- About the world (lore, rumors, hints)
- Reactions to player actions (completed quests, choices)
- Idle banter (personality, humor)

HOW TO EXECUTE:
1. For each NPC, add dialogue dictionary:
   ```json
   "dialogue": {
       "greeting_first": "First meeting dialogue...",
       "greeting_neutral": "Standard greeting...",
       "greeting_friendly": "High reputation greeting...",
       "about_self": "My backstory is...",
       "about_town": "This place is...",
       "rumors": ["Rumor 1", "Rumor 2", "Rumor 3"],
       "after_episode_X": "Reaction to episode completion..."
   }
   ```
2. Add personality to each NPC (gruff, cheerful, mysterious, etc.)
3. Include quest hooks and lore hints
4. Vary dialogue based on campaign progress

ACCEPTANCE CRITERIA:
- [ ] All NPCs have 5+ dialogue options
- [ ] Dialogue reflects NPC personality
- [ ] Dialogue changes based on campaign progress
- [ ] Lore and rumors provided
- [ ] NPCs feel distinct from each other
```

---

## ❌ KNOWN ISSUES

### Issue: Waterbreathing Not Implemented
**Location:** Episode 7 (Drowned Ruins)
**Severity:** CRITICAL - Episode unplayable without it
**Files:** Magic system, equipment system

**Task:**
```
CONTEXT: Episode 7 is entirely underwater. Players need waterbreathing
magic or alchemical gills. Neither is implemented.

SOLUTION OPTIONS:
1. Implement waterbreathing spell (Cleric/Magic-User level 3)
2. Implement alchemical gills item (consumable, 1 hour duration)
3. Implement Amulet of Waterbreathing (permanent, from Episode 7 reward)

HOW TO EXECUTE:
1. Add waterbreathing spell to aerthos/data/spells.json:
   ```json
   "waterbreathing": {
       "name": "Water Breathing",
       "level": 3,
       "school": "transmutation",
       "duration": "1 hour/level",
       "description": "Allows breathing underwater..."
   }
   ```
2. Add alchemical_gills to equipment.json:
   ```json
   "alchemical_gills": {
       "name": "Alchemical Gills",
       "type": "consumable",
       "cost_gp": 50,
       "effect": "Grants waterbreathing for 1 hour",
       "description": "A potion that temporarily allows breathing underwater."
   }
   ```
3. Implement effect in game_state.py:
   - Track "waterbreathing" status effect
   - Check before entering underwater rooms
   - Warn player if not protected

ACCEPTANCE CRITERIA:
- [ ] Waterbreathing spell works
- [ ] Alchemical gills work
- [ ] Amulet of Waterbreathing works (permanent)
- [ ] Game prevents underwater entry without protection
- [ ] Episode 7 is playable
```

---

### Issue: Episode Unlocking Logic Not Tested
**Location:** Campaign progression system
**Severity:** MEDIUM - May cause progression blockers
**Files:** `aerthos/campaign/campaign.py`

**Task:**
```
CONTEXT: Episodes unlock based on completing previous episodes. This
logic exists but hasn't been tested. May have bugs.

TEST SCENARIOS:
1. Complete Episode 1 → Episode 2 unlocks
2. Complete Episode 3 → Episode 4 unlocks AND Ironfast Outpost unlocks
3. Complete Episode 6 → Episode 7 unlocks
4. Try to play Episode 5 before completing Episode 4 → Should fail
5. Save/load campaign mid-progression → Unlocks preserved

HOW TO EXECUTE:
1. Write integration test:
   ```python
   def test_episode_unlocking():
       campaign = create_test_campaign()
       assert not campaign.is_episode_unlocked('episode_02')

       complete_episode(campaign, 'episode_01')
       assert campaign.is_episode_unlocked('episode_02')
   ```
2. Test all episode transitions
3. Test hub unlocking (Episodes 3, 4, 6 unlock new hubs)
4. Test save/load preserves unlock state
5. Fix any bugs found

ACCEPTANCE CRITERIA:
- [ ] All episode unlocks work correctly
- [ ] Hub unlocks work correctly
- [ ] Cannot play locked episodes
- [ ] Save/load preserves unlock state
- [ ] Integration tests pass
```

---

### Issue: Monster AI - All "Aggressive"
**Location:** Monster behavior system
**Severity:** LOW - Doesn't break game but reduces variety
**Files:** `aerthos/data/monsters.json`, `aerthos/entities/monster.py`

**Task:**
```
CONTEXT: All monsters have ai_behavior: "aggressive" (always attack).
AD&D has more variety: defensive, flee_low_hp, smart tactical. This would
make combat more interesting.

AI BEHAVIORS TO IMPLEMENT:
1. aggressive: Always attack (current default)
2. defensive: Attack only if attacked first
3. territorial: Attack if player enters certain rooms
4. flee_low_hp: Run when below 25% HP
5. smart: Target weak party members, focus fire
6. cowardly: Flee if outnumbered
7. berserk: Attack recklessly, ignore tactics

HOW TO EXECUTE:
1. Update combat.py to check monster.ai_behavior
2. Implement each behavior:
   ```python
   def get_monster_action(monster, party, combat_state):
       if monster.ai_behavior == "flee_low_hp":
           if monster.hp_current < monster.hp_max * 0.25:
               return "flee"
       # etc...
   ```
3. Update monsters.json with varied behaviors:
   - Goblins: cowardly (flee if losing)
   - Hobgoblins: aggressive
   - Ogres: berserk (reckless)
   - Cultists: smart (target casters)
   - Bosses: smart + never flee

ACCEPTANCE CRITERIA:
- [ ] All 7 AI behaviors implemented
- [ ] Combat.py uses monster AI behavior
- [ ] Monsters act according to their AI type
- [ ] Combat feels more varied and tactical
```

---

## 📊 SUMMARY STATISTICS

### Content Completion
- **Episodes:** 10/10 created (all functional stubs)
- **Dungeons:** 10/10 created (9 are stubs, 1 is full)
- **City Hubs:** 5/5 created
- **Monsters Defined:** ~15/50+ needed
- **Items Defined:** ~20/40+ needed
- **Systems Complete:** ~70%

### What Works Right Now
✅ Campaign infrastructure (create, save, load)
✅ Episode progression (unlocking, completion)
✅ City hub services (shops, inns, temples)
✅ Hub interfaces (gold system fixed)
✅ Save/checkpoint system (web UI button)
✅ Story arc (all 10 episodes written)
✅ All core tests passing (473/473)

### What Needs Work
❌ Dungeon expansion (9 stubs → full dungeons)
❌ Monster definitions (30+ missing)
❌ Item definitions (20+ missing)
❌ Testing/balance (no playtesting done)
❌ Special mechanics (waterbreathing, multiple endings, AI variety)
❌ Polish (descriptions, dialogue, atmosphere)

### Estimated Work Remaining
- **Dungeon Expansion:** 40-60 hours (4-6 hours per dungeon)
- **Monster/Item Creation:** 10-15 hours
- **Testing & Balance:** 20-30 hours
- **Polish & Enhancement:** 15-20 hours
- **Bug Fixes:** 10-15 hours

**Total:** 95-140 hours of work to reach "full campaign" state

---

## 🎯 RECOMMENDED PRIORITY ORDER

If continuing this project, recommended order of tasks:

### Phase 1: Make It Playable (20 hours)
1. ✅ Create all missing monster definitions
2. ✅ Create all missing item definitions
3. ✅ Implement waterbreathing mechanic
4. ✅ Fix episode unlock bugs (if any)
5. ✅ Full playthrough test (Episodes 1-10)

### Phase 2: Balance & Polish (15 hours)
1. Economy balance pass
2. Difficulty balance (encounter/boss tuning)
3. XP curve verification
4. Enhanced room descriptions (pick 2-3 favorite dungeons)
5. Bug fixes from playthrough

### Phase 3: Expansion (40 hours)
1. Expand Episode 10 dungeon (final dungeon priority)
2. Expand Episode 7 dungeon (underwater unique)
3. Expand Episode 5 dungeon (temple atmosphere)
4. Expand Episode 4 dungeon (dwarven fortress)
5. Others as time permits

### Phase 4: Enhancement (20 hours)
1. Reputation system effects
2. Multiple endings implementation
3. Monster AI variety
4. NPC dialogue expansion
5. Additional character classes

---

**END OF TODO DOCUMENT**

*This document contains enough context to execute any task "cold start"—no prior knowledge required.*
