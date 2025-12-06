# Phase 4 Task 2: Side Quests & Optional Content - Design Document

**Date:** December 3, 2025
**Status:** 🔄 DESIGN PHASE
**Estimated Effort:** 8-10 hours implementation

---

## Executive Summary

Design and implement a side quest system that adds optional content to the Aerthos campaign without disrupting the main story progression. Side quests will provide:
- Additional XP and rewards for thorough exploration
- Character development and world-building
- Player agency and non-linear gameplay
- Replayability through optional paths

---

## Design Goals

### Primary Goals:
1. **Optional Content:** Side quests never block main story progression
2. **Meaningful Rewards:** XP, unique items, reputation bonuses
3. **Discoverable:** Hidden through exploration, NPC dialogue, lore items
4. **Episode-Scoped:** Side quests contained within episodes (don't span multiple episodes)
5. **Simple Implementation:** Extend existing systems, minimal new code

### Non-Goals:
- Complex branching quest chains (keep it simple)
- Multi-episode quests (too complex for current scope)
- Dynamic quest generation (hand-crafted only)
- Quest log UI (track completion in background)

---

## System Architecture

### Core Components:

```
SideQuest (Data Model)
    ├─ id: unique identifier
    ├─ title: quest name
    ├─ description: quest objective
    ├─ episode_id: which episode contains this quest
    ├─ trigger_type: how quest is discovered
    ├─ trigger_conditions: what activates the quest
    ├─ objectives: list of objectives to complete
    ├─ rewards: XP, gold, items, reputation
    └─ completion_flag: story flag when completed

QuestManager (Tracking System)
    ├─ active_quests: currently active side quests
    ├─ completed_quests: finished side quests
    ├─ check_triggers(): evaluate if new quests should activate
    ├─ update_objectives(): check if objectives completed
    └─ award_rewards(): give rewards when quest complete

Quest Integration Points:
    ├─ Episode intro: check for auto-start quests
    ├─ Room exploration: check for room-based triggers
    ├─ Item pickup: check for item-based triggers
    ├─ NPC dialogue: check for dialogue triggers
    ├─ Monster defeat: check for defeat triggers
    └─ Episode completion: complete any incomplete quests
```

---

## Quest Types

### Type 1: Exploration Quests
**Trigger:** Discover hidden room or area
**Objective:** Explore all rooms in optional wing
**Reward:** XP, treasure chest in final room

**Example (Episode 2 - Oakhaven Sewers):**
- **Quest:** "The Forgotten Cistern"
- **Trigger:** Enter room "old_cistern"
- **Objective:** Defeat the Otyugh and search the cistern
- **Reward:** +500 XP, Ring of Protection +1, +10 reputation

### Type 2: Collection Quests
**Trigger:** Find first collectible item
**Objective:** Collect all items of a set
**Reward:** Bonus when full set collected

**Example (Episode 3 - Silas's Warehouse):**
- **Quest:** "Silas's Ledgers"
- **Trigger:** Pick up first ledger (3 total hidden in warehouse)
- **Objective:** Find all 3 ledgers
- **Reward:** +750 XP, +25 reputation, unlock "evidence" ending variant

### Type 3: NPC Rescue Quests
**Trigger:** Find imprisoned NPC
**Objective:** Free NPC and escort to safe room
**Reward:** NPC gives reward item or information

**Example (Episode 4 - Duergar Hold):**
- **Quest:** "Rescue the Dwarven Smiths"
- **Trigger:** Discover prison cells with 2 imprisoned dwarves
- **Objective:** Defeat guards, free dwarves, lead to safe room
- **Reward:** +1000 XP, Dwarven Crafted Warhammer +2, +30 reputation

### Type 4: Mini-Boss Challenges
**Trigger:** Discover optional boss chamber
**Objective:** Defeat optional boss
**Reward:** Unique magic item, large XP reward

**Example (Episode 7 - Drowned Ruins):**
- **Quest:** "The Drowned King"
- **Trigger:** Find throne room (optional area)
- **Objective:** Defeat Drowned King (8 HD boss)
- **Reward:** +2000 XP, Trident of the Depths +2, +20 reputation

### Type 5: Puzzle/Mystery Quests
**Trigger:** Find cryptic clue or puzzle
**Objective:** Solve puzzle to unlock secret
**Reward:** Hidden treasure vault

**Example (Episode 8 - Eldoria Catacombs):**
- **Quest:** "The Crypt Keepers' Secret"
- **Trigger:** Read inscription in main crypt
- **Objective:** Activate 4 braziers in correct order
- **Reward:** +800 XP, Scroll of Raise Dead, +15 reputation

---

## Data Structure

### side_quests.json (New File)

```json
{
  "forgotten_cistern": {
    "id": "forgotten_cistern",
    "title": "The Forgotten Cistern",
    "description": "An ancient cistern holds a terrible secret beneath the sewers",
    "episode_id": "episode_02",
    "trigger_type": "enter_room",
    "trigger_conditions": {
      "room_id": "old_cistern"
    },
    "objectives": [
      {
        "id": "defeat_otyugh",
        "description": "Defeat the Otyugh",
        "type": "kill_monster",
        "target": "otyugh",
        "count": 1
      },
      {
        "id": "search_cistern",
        "description": "Search the cistern thoroughly",
        "type": "search_room",
        "room_id": "old_cistern"
      }
    ],
    "rewards": {
      "xp": 500,
      "items": ["ring_protection_1"],
      "reputation": 10,
      "gold": 100
    },
    "completion_flag": "cistern_explored",
    "optional": true
  }
}
```

### Episode Data Enhancement

Add to each episode JSON:
```json
{
  "side_quests": ["forgotten_cistern", "silas_ledgers"],
  "optional_rooms": ["old_cistern", "hidden_vault"],
  "optional_bosses": ["drowned_king"]
}
```

---

## Implementation Plan

### Phase 1: Core Quest System (3 hours)

**1.1 Create Quest Data Model**
- File: `aerthos/campaign/side_quest.py`
- Classes: `SideQuest`, `QuestObjective`, `QuestRewards`
- Methods: `is_triggered()`, `is_complete()`, `check_objectives()`

**1.2 Create Quest Manager**
- File: `aerthos/campaign/quest_manager.py`
- Class: `QuestManager`
- Methods: `check_triggers()`, `update_quests()`, `complete_quest()`

**1.3 Create Quest Data File**
- File: `aerthos/data/side_quests.json`
- Initial content: 2-3 quests per episode (20-30 quests total)

### Phase 2: Integration (2 hours)

**2.1 Integrate with Episode Runner**
- File: `aerthos/campaign/episode_runner.py`
- Add `quest_manager` to episode state
- Check quest triggers on room enter
- Update quest objectives on game events

**2.2 Integrate with Game State**
- File: `aerthos/engine/game_state.py`
- Hook quest checks into:
  - Room exploration
  - Monster defeat
  - Item pickup
  - Search actions

**2.3 Add Quest Notifications**
- File: `aerthos/ui/display.py`
- New method: `display_quest_notification()`
- Show when quest starts/completes

### Phase 3: Quest Content Creation (3 hours)

**3.1 Design Quests for Episodes 1-5**
- 2-3 quests per episode
- Mix of quest types
- Appropriate rewards for episode level

**3.2 Design Quests for Episodes 6-10**
- 2-3 quests per episode
- Higher difficulty, better rewards
- Tie into episode themes

**3.3 Balance Rewards**
- XP rewards: 10-15% of episode total
- Items: Unique but not overpowered
- Reputation: 10-30 per quest

### Phase 4: Testing (1 hour)

**4.1 Unit Tests**
- Test quest triggering
- Test objective completion
- Test reward distribution

**4.2 Integration Tests**
- Test quests within episodes
- Test quest persistence across saves
- Test edge cases (quest abandonment, etc.)

---

## Quest Design Guidelines

### Reward Balance:
- **XP:** 10-15% of episode total XP (helps Fighter reach level 10)
- **Gold:** 100-500 gp per quest (modest, not game-breaking)
- **Reputation:** 10-30 per quest (meaningful but not excessive)
- **Items:** Unique items not available in shops, +1/+2 magic items

### Difficulty:
- **Easy Quests:** 1-2 extra encounters, 30min gameplay
- **Medium Quests:** 3-4 extra encounters, 60min gameplay
- **Hard Quests:** Optional boss fight, 90min gameplay

### Discovery:
- **Obvious:** 50% of quests (clear markers in room descriptions)
- **Hidden:** 30% of quests (requires thorough exploration)
- **Obscure:** 20% of quests (requires careful reading/puzzle solving)

---

## Example Quest Implementations

### Episode 2: "The Forgotten Cistern" (Easy Exploration)

**Trigger:** Enter "old_cistern" room
**Narrative:** "The stench here is overwhelming. Something massive lurks in the water..."
**Objective:** Defeat Otyugh, search cistern
**Reward:** +500 XP, Ring of Protection +1, +10 reputation

### Episode 4: "Rescue the Dwarven Smiths" (Medium Rescue)

**Trigger:** Enter "prison_cells" room
**Narrative:** "Two dwarven prisoners call out from behind iron bars!"
**Objectives:**
  1. Defeat 2 Duergar Guards
  2. Find prison key (search guard corpses)
  3. Free dwarves
  4. Escort to "entrance_hall" (safe room)
**Reward:** +1000 XP, Dwarven Warhammer +2, +30 reputation

### Episode 7: "The Drowned King" (Hard Boss Challenge)

**Trigger:** Enter "sunken_throne_room" (optional room off main path)
**Narrative:** "A spectral figure sits upon a barnacle-encrusted throne..."
**Objective:** Defeat Drowned King (8 HD undead boss)
**Reward:** +2000 XP, Trident of the Depths +2, +20 reputation

---

## Quest Tracking in Campaign State

Add to campaign save data:
```python
{
  "active_quests": [
    {
      "quest_id": "forgotten_cistern",
      "started": True,
      "objectives_complete": ["defeat_otyugh"],
      "objectives_remaining": ["search_cistern"]
    }
  ],
  "completed_quests": [
    "silas_ledgers",
    "rescue_dwarves"
  ]
}
```

---

## User Interface Changes

### Quest Notifications:

**Quest Started:**
```
╔════════════════════════════════════════════════════════════════╗
║                    SIDE QUEST DISCOVERED                       ║
╠════════════════════════════════════════════════════════════════╣
║  Title: The Forgotten Cistern                                  ║
║                                                                ║
║  An ancient cistern holds a terrible secret beneath the        ║
║  sewers. Investigate this foul place and discover what lurks   ║
║  in the depths.                                                ║
╚════════════════════════════════════════════════════════════════╝
```

**Quest Objective Complete:**
```
[QUEST UPDATE] The Forgotten Cistern: Defeated the Otyugh (1/2)
```

**Quest Complete:**
```
╔════════════════════════════════════════════════════════════════╗
║                    SIDE QUEST COMPLETE!                        ║
╠════════════════════════════════════════════════════════════════╣
║  The Forgotten Cistern                                         ║
║                                                                ║
║  Rewards:                                                      ║
║  • +500 XP                                                     ║
║  • Ring of Protection +1                                       ║
║  • +10 Reputation (Oakhaven)                                   ║
║  • 100 gold pieces                                             ║
╚════════════════════════════════════════════════════════════════╝
```

### New Commands:

```
quests - Show active and completed quests
quest info <quest_name> - Show quest details
```

---

## Testing Strategy

### Unit Tests:
- `test_side_quest.py` - Quest data model
- `test_quest_manager.py` - Quest tracking logic
- `test_quest_triggers.py` - Trigger conditions
- `test_quest_rewards.py` - Reward distribution

### Integration Tests:
- `test_quest_episode_integration.py` - Quests within episodes
- `test_quest_persistence.py` - Quest save/load
- `test_quest_edge_cases.py` - Quest abandonment, partial completion

---

## Acceptance Criteria

- [ ] QuestManager class implemented and tested
- [ ] SideQuest data model created
- [ ] side_quests.json created with 20+ quests
- [ ] Quest triggers work for all trigger types
- [ ] Quest objectives track correctly
- [ ] Quest rewards distribute properly
- [ ] Quest UI notifications display
- [ ] All tests pass (504+new tests)
- [ ] Quests integrate with episode flow
- [ ] Quests save/load correctly
- [ ] Documentation updated

---

## Estimated Quest Distribution

| Episode | Main XP | Side Quest XP | Total XP | Side Quest % |
|---------|---------|---------------|----------|--------------|
| 1       | 5,365   | 750           | 6,115    | 14%          |
| 2       | 5,575   | 800           | 6,375    | 14%          |
| 3       | 12,300  | 1,500         | 13,800   | 12%          |
| 4       | 22,875  | 3,000         | 25,875   | 13%          |
| 5       | 26,025  | 3,500         | 29,525   | 13%          |
| 6       | 34,625  | 4,500         | 39,125   | 13%          |
| 7       | 65,350  | 8,000         | 73,350   | 12%          |
| 8       | 57,315  | 7,500         | 64,815   | 13%          |
| 9       | 120,775 | 15,000        | 135,775  | 12%          |
| 10      | 114,100 | 12,000        | 126,100  | 11%          |
| **Total** | **464,305** | **56,550** | **520,855** | **12.2%** |

**Impact:** Side quests add ~56k XP, pushing Fighter well past level 10 threshold if all completed.

---

## Next Steps

1. Create `aerthos/campaign/side_quest.py` (data model)
2. Create `aerthos/campaign/quest_manager.py` (tracking)
3. Create `aerthos/data/side_quests.json` (quest data)
4. Integrate with episode runner
5. Create quest UI notifications
6. Write tests
7. Create 20-30 quests across all episodes

---

**Created:** December 3, 2025
**Status:** Ready for implementation
**Estimated Time:** 8-10 hours
**Priority:** High (adds replayability and depth)
