# AERTHOS: Menu-Driven Campaign System Implementation Plan

## Document Purpose

This document provides a comprehensive implementation roadmap for adding a menu-driven campaign system to the Aerthos AD&D 1e text adventure game. It is designed to be consumed by Claude Code (Sonnet 4.5) across multiple work sessions while maintaining context and coherence.

**Project Location:** `/mnt/d/Development/aerthos`  
**Current State:** Core dungeon crawler complete (417/417 tests passing)  
**Goal:** Add narrative-driven campaign with city hubs, shops, and episode progression

---

## PART 1: PROJECT CONTEXT & ARCHITECTURE

### 1.1 What Already Exists (DO NOT REBUILD)

The following systems are **complete and working**. Reference them, integrate with them, but do not rewrite them:

| System | Location | Status | Notes |
|--------|----------|--------|-------|
| GameState | `aerthos/engine/game_state.py` | ✅ Complete | Central coordinator, 25+ command handlers |
| Combat | `aerthos/engine/combat.py` | ✅ Complete | THAC0 system, monster AI |
| Magic | `aerthos/systems/magic.py` | ✅ Complete | Vancian spells, 332 in database |
| Parser | `aerthos/engine/parser.py` | ✅ Complete | 45+ verb groups |
| Characters | `aerthos/entities/player.py` | ✅ Complete | Inventory, equipment, spells |
| Monsters | `aerthos/entities/monster.py` | ✅ Complete | AI behaviors, special abilities |
| Party | `aerthos/entities/party.py` | ✅ Complete | 4-6 members, formations |
| Dungeon | `aerthos/world/dungeon.py` | ✅ Complete | Navigation, rooms, encounters |
| MultiLevel | `aerthos/world/multilevel_dungeon.py` | ✅ Complete | Stair navigation |
| Generator | `aerthos/generator/dungeon_generator.py` | ✅ Complete | Procedural dungeons |
| **Village** | `aerthos/world/village.py` | ⚠️ Exists but disconnected | Has Shop, Inn, Guild classes |
| **Shop** | `aerthos/world/shop.py` | ⚠️ Exists but disconnected | Buy/sell mechanics |
| **Inn** | `aerthos/world/inn.py` | ⚠️ Exists but disconnected | Rest facilities |
| **Guild** | `aerthos/world/guild.py` | ⚠️ Exists but disconnected | Class services |
| CharacterRoster | `aerthos/storage/character_roster.py` | ✅ Complete | `~/.aerthos/characters/` |
| PartyManager | `aerthos/storage/party_manager.py` | ✅ Complete | `~/.aerthos/parties/` |
| SessionManager | `aerthos/storage/session_manager.py` | ✅ Complete | `~/.aerthos/sessions/` |
| ScenarioLibrary | `aerthos/storage/scenario_library.py` | ✅ Complete | `~/.aerthos/scenarios/` |

### 1.2 Architecture Layers (Top to Bottom)

```
┌─────────────────────────────────────────────────────────────┐
│  UI LAYER                                                   │
│  - main.py (CLI) - 1519 lines                              │
│  - web_ui/app.py (Flask) - 1938 lines                      │
│  RULE: Both must call identical core APIs                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  ENGINE LAYER (aerthos/engine/)                            │
│  - GameState: Central coordinator                          │
│  - CombatResolver: THAC0 combat                           │
│  - CommandParser: Natural language → Command objects       │
│  - TimeTracker: Turns, resources, light sources           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  SYSTEMS LAYER (aerthos/systems/) - 25+ subsystems         │
│  - magic.py, skills.py, saving_throws.py                   │
│  - ability_modifiers.py, monster_ai.py, narrator.py        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  ENTITY LAYER (aerthos/entities/)                          │
│  - Character, PlayerCharacter, Monster, Party              │
│  - Equipment (Weapon, Armor, Shield, Item)                 │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  WORLD LAYER (aerthos/world/)                              │
│  - Dungeon, MultiLevelDungeon, Room, Encounter             │
│  - Village, Shop, Inn, Guild (NEED INTEGRATION)            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  STORAGE LAYER (aerthos/storage/)                          │
│  - CharacterRoster, PartyManager, SessionManager           │
│  - ScenarioLibrary                                         │
│  - NEW: CampaignManager (to be created)                    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  DATA LAYER (aerthos/data/)                                │
│  - JSON files: monsters, spells, equipment, classes, races │
│  - NEW: campaigns/, cities/, episodes/ (to be created)     │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Critical Rules for Development

1. **ALWAYS run tests after changes:** `python3 run_tests.py --no-web`
2. **Keep CLI and Web UI in sync:** Both must use identical core APIs
3. **Data-driven design:** Game content in JSON, not hardcoded
4. **Use existing systems:** Don't recreate combat, magic, parsing, etc.
5. **Incremental implementation:** Each phase should be playable
6. **Preserve 417 passing tests:** Never break existing functionality

### 1.4 Why the Previous Campaign Attempt Failed

A previous attempt exists on branch `backup-before-rollback-20251121-214217`. It failed because:

1. **Hex-based overworld** required complex travel, weather, and visualization systems
2. **4-context UI panels** (dungeon/overworld/village/encounter) required major frontend refactoring
3. **Parser overhaul** needed to distinguish overworld vs dungeon commands
4. **Scope creep** - 7 phases, 10-15 weeks estimated

**This plan avoids those mistakes by:**
- Using **menu navigation** instead of hex travel
- **No parser changes** - menus use numbered options
- **Incremental integration** - each phase is standalone playable
- **Reusing existing code** - Village/Shop/Inn already exist

---

## PART 2: THE CAMPAIGN DESIGN

### 2.1 Core Concept: Menu-Driven Hub-and-Spoke

Instead of a complex overworld map, the player navigates through **menu choices**:

```
╔═══════════════════════════════════════════════════════════════╗
║  CAMPAIGN: The Serpent's Shadow                               ║
║  Episode 2 of 10: The Cult Below                              ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  OAKHAVEN - Border Town                                       ║
║  ─────────────────────────────────────────────                ║
║                                                               ║
║  1. The Dirty Mug (Inn/Tavern)                               ║
║     • Rest and recover (10gp/night)                          ║
║     • Hear rumors about current events                        ║
║                                                               ║
║  2. Silas's Equipment Shop                                    ║
║     • Buy weapons, armor, supplies                            ║
║     • Sell recovered treasure                                 ║
║                                                               ║
║  3. Temple of Light                                           ║
║     • Healing services (donation based)                       ║
║     • Remove curses, cure disease                             ║
║                                                               ║
║  4. The Town Gate                                             ║
║     • Travel to: Oakhaven Sewers [CURRENT QUEST]             ║
║     • Travel to: Keep of Kaldor [COMPLETED]                  ║
║     • [LOCKED] The Whispering Marshes                        ║
║                                                               ║
║  5. Party Management                                          ║
║                                                               ║
║  6. Campaign Journal                                          ║
║                                                               ║
║  0. Save & Exit Campaign                                      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
Enter choice (0-6): _
```

### 2.2 Campaign Structure: "The Serpent's Shadow"

A 10-episode campaign exploring all regions of Aerthos, following the Cult of the Serpent Eye threat:

#### Act I: Local Troubles (Episodes 1-3, Levels 1-3)
**Hub: Oakhaven**

| Ep | Title | Dungeon | Story | Region |
|----|-------|---------|-------|--------|
| 1 | The Goblin Refugees | Keep of Kaldor | Goblins displaced from mountains raid caravans. Discover cult symbol. | Heartlands |
| 2 | The Cult Below | Oakhaven Sewers | Missing townsfolk. Cult hideout beneath the town. | Heartlands |
| 3 | The Merchant's Secret | Silas's Warehouse | Silas is selling cursed items. Cult connection? | Heartlands |

#### Act II: Regional Threats (Episodes 4-6, Levels 4-6)
**Hubs: Oakhaven → Ironfast Outpost → Mire's Edge**

| Ep | Title | Dungeon | Story | Region |
|----|-------|---------|-------|--------|
| 4 | The Dwarven Distress | Duergar-Occupied Hold | Dwarves under siege. Duergar working with cult. | Shattered Peaks |
| 5 | The Marsh Temple | Sunken Temple | Cult gathering artifacts. Lizardfolk allies? | Whispering Marshes |
| 6 | The Orc Truce | Scorched Fortress | Orcs offer alliance against fire giants. Cult manipulating both. | Scarred Wastes |

#### Act III: Rising Darkness (Episodes 7-8, Levels 7-9)
**Hubs: Mire's Edge → Eldoria → Coastal Haven**

| Ep | Title | Dungeon | Story | Region |
|----|-------|---------|-------|--------|
| 7 | The Sunken City | Drowned Ruins of Ys'Thara | Cult seeks artifact in underwater city. | Sunken Coast |
| 8 | The Syndic's Treachery | Eldoria Catacombs | Cult has infiltrated the Syndics. Political intrigue. | Eldoria |

#### Act IV: The Serpent's Eye (Episodes 9-10, Levels 10-12)
**Hub: Eldoria → Final Confrontation**

| Ep | Title | Dungeon | Story | Region |
|----|-------|---------|-------|--------|
| 9 | The Planar Rift | Elemental Chaos | Cult opening rift to summon patron. Close it. | Shattered Peaks |
| 10 | The Serpent's Awakening | Serpent Temple | Final battle. Prevent the summoning. | Beneath Oakhaven |

### 2.3 City Hub Definitions

Each hub has a distinct character and available services:

#### Oakhaven (Starting Hub)
- **Theme:** Frontier town, adventurer economy, rough and ready
- **Services:** Basic shop (inflated prices), cheap inn, small temple, militia guild
- **NPCs:** Silas (merchant antagonist), The Guide (quest giver), Temple Priest
- **Special:** 5cp gate toll, 10% currency exchange on ancient coins

#### Ironfast Outpost (Mountain Hub)
- **Theme:** Dwarven military encampment, disciplined, suspicious of outsiders
- **Services:** Excellent weapons/armor (dwarven quality), no inn (barracks), forge
- **NPCs:** Commander Thrain, Master Smith Durin, Scout Brunhild
- **Special:** Must prove worth before full access (complete Episode 4)

#### Mire's Edge (Swamp Hub)
- **Theme:** Ramshackle village on stilts, swamp guides, herbalists
- **Services:** Rare herbs/potions, canoes for hire, swamp guide services
- **NPCs:** Elder Mirela (herbalist), Grok (lizardfolk neutral contact), Swamp Witch
- **Special:** Lizardfolk may become allies or enemies based on choices

#### Eldoria (Capital Hub)
- **Theme:** Grand city, guild politics, wealth and corruption
- **Services:** Best equipment, temples to all gods, multiple guilds, black market
- **NPCs:** The Three Syndics, Temple Hierarch, Thieves' Guild contact
- **Special:** Reputation matters, guild memberships available

#### Coastal Haven (Seaside Hub)
- **Theme:** Pirate town, smugglers, sailors, sea magic
- **Services:** Ships for hire, exotic goods, sea cleric temple
- **NPCs:** Captain Marlowe, Smuggler Queen, Sea Witch
- **Special:** Access to Sunken Coast dungeons

### 2.4 Episode Data Structure

Each episode is defined in JSON:

```json
{
    "id": "episode_01",
    "title": "The Goblin Refugees",
    "act": 1,
    "recommended_level": 1,
    "hub_id": "oakhaven",
    
    "intro_text": "The town of Oakhaven buzzes with worried whispers. For three weeks now, merchant caravans traveling the mountain road have been ambushed...",
    
    "briefing": {
        "quest_giver": "The Guide",
        "location": "The Dirty Mug tavern",
        "dialogue": "Word is, goblins have taken over the old Keep of Kaldor. Not your usual goblin raiders though—these ones seem desperate, organized. The caravans they hit? They take food, not gold. Strange, that."
    },
    
    "dungeon": {
        "type": "hand_crafted",
        "file": "dungeons/keep_of_kaldor.json",
        "theme": "ruins",
        "levels": 2,
        "boss": "Grukk the Hobgoblin Chief"
    },
    
    "completion_criteria": {
        "type": "boss_defeated",
        "target": "grukk_hobgoblin_chief"
    },
    
    "completion_text": "With Grukk defeated, the goblin threat ends. But among his possessions, you find something disturbing: a medallion bearing a serpent coiled around an eye. The goblins weren't just refugees—someone drove them here deliberately...",
    
    "rewards": {
        "xp_bonus": 500,
        "gold_bonus": 100,
        "items": ["dagger_plus_1"],
        "unlocks": ["episode_02"],
        "story_flags": ["found_serpent_medallion"]
    },
    
    "rumors": [
        "The goblins came from the High Pass. Something scared them out of their mountain homes.",
        "Old Kaldor fell to plague decades ago. The keep's been abandoned ever since.",
        "Silas has been buying goblin weapons lately. Strange business for an equipment merchant."
    ],
    
    "prerequisites": []
}
```

---

## PART 3: IMPLEMENTATION PHASES

### Phase 1: Campaign Infrastructure (Foundation)

**Goal:** Create the data structures and storage systems for campaigns.

**Files to Create:**
```
aerthos/
├── campaign/                    # NEW DIRECTORY
│   ├── __init__.py
│   ├── campaign.py             # Campaign class
│   ├── episode.py              # Episode class
│   ├── city_hub.py             # CityHub class
│   └── campaign_manager.py     # Persistence for campaigns
│
├── data/
│   ├── campaigns/              # NEW DIRECTORY
│   │   └── serpents_shadow.json
│   ├── cities/                 # NEW DIRECTORY
│   │   ├── oakhaven.json
│   │   ├── ironfast_outpost.json
│   │   ├── mires_edge.json
│   │   ├── eldoria.json
│   │   └── coastal_haven.json
│   ├── episodes/               # NEW DIRECTORY
│   │   ├── episode_01_goblin_refugees.json
│   │   ├── episode_02_cult_below.json
│   │   └── ... (10 total)
│   └── dungeons/               # NEW DIRECTORY
│       ├── keep_of_kaldor.json
│       ├── oakhaven_sewers.json
│       └── ... (10 total)
```

**Classes to Implement:**

```python
# aerthos/campaign/campaign.py
@dataclass
class Campaign:
    """Represents a campaign playthrough state"""
    id: str
    name: str
    description: str
    party_id: str                    # Reference to saved party
    current_episode_id: str
    current_hub_id: str
    completed_episodes: List[str]
    unlocked_episodes: List[str]
    unlocked_hubs: List[str]
    story_flags: Dict[str, bool]     # Track narrative choices
    reputation: Dict[str, int]       # Faction reputation scores
    play_time_minutes: int
    created_at: datetime
    last_played: datetime
    
    def is_episode_unlocked(self, episode_id: str) -> bool: ...
    def is_hub_unlocked(self, hub_id: str) -> bool: ...
    def complete_episode(self, episode_id: str, rewards: dict) -> None: ...
    def set_story_flag(self, flag: str, value: bool = True) -> None: ...
    def modify_reputation(self, faction: str, delta: int) -> None: ...
    def to_json(self) -> dict: ...
    @classmethod
    def from_json(cls, data: dict) -> 'Campaign': ...
```

```python
# aerthos/campaign/episode.py
@dataclass
class Episode:
    """Defines an episode's content and structure"""
    id: str
    title: str
    act: int
    recommended_level: int
    hub_id: str
    intro_text: str
    briefing: EpisodeBriefing
    dungeon_config: DungeonReference
    completion_criteria: CompletionCriteria
    completion_text: str
    rewards: EpisodeRewards
    rumors: List[str]
    prerequisites: List[str]
    
    @classmethod
    def load(cls, episode_id: str) -> 'Episode': ...
    def check_completion(self, game_state: 'GameState') -> bool: ...
    def get_dungeon(self) -> 'Dungeon': ...
```

```python
# aerthos/campaign/city_hub.py
@dataclass
class CityHub:
    """Represents a city/town the party can visit"""
    id: str
    name: str
    description: str
    theme: str
    region: str
    
    # Services (references to existing systems)
    shops: List[ShopConfig]
    inn: Optional[InnConfig]
    temple: Optional[TempleConfig]
    guild: Optional[GuildConfig]
    
    # NPCs and content
    npcs: Dict[str, NPC]
    available_quests: List[str]      # Episode IDs accessible from here
    special_rules: Dict[str, Any]    # Gate tolls, restrictions, etc.
    
    def get_menu_options(self, campaign: Campaign) -> List[MenuOption]: ...
    def get_available_dungeons(self, campaign: Campaign) -> List[Episode]: ...
    
    @classmethod
    def load(cls, hub_id: str) -> 'CityHub': ...
```

```python
# aerthos/campaign/campaign_manager.py
class CampaignManager:
    """Handles campaign persistence"""
    
    def __init__(self, save_dir: Optional[Path] = None):
        self.save_dir = save_dir or Path.home() / '.aerthos' / 'campaigns'
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def create_campaign(self, campaign_template_id: str, party_id: str) -> Campaign: ...
    def save_campaign(self, campaign: Campaign) -> str: ...
    def load_campaign(self, campaign_id: str) -> Campaign: ...
    def list_campaigns(self) -> List[CampaignSummary]: ...
    def delete_campaign(self, campaign_id: str) -> bool: ...
```

**Tests to Write:**
```
tests/
├── test_campaign.py              # Campaign state management
├── test_episode.py               # Episode loading and completion
├── test_city_hub.py              # City hub functionality
└── test_campaign_manager.py      # Campaign persistence
```

**Acceptance Criteria:**
- [ ] Campaign can be created, saved, and loaded
- [ ] Episodes load from JSON with all fields
- [ ] City hubs load from JSON with all services
- [ ] Story flags and reputation track correctly
- [ ] Episode unlock logic works
- [ ] All new tests pass
- [ ] Existing 417 tests still pass

---

### Phase 2: City Hub Integration

**Goal:** Connect existing Shop/Inn/Guild systems to playable city hubs.

**Files to Modify:**
```
aerthos/world/
├── village.py      # Enhance to work with CityHub
├── shop.py         # Ensure buy/sell works with party gold
├── inn.py          # Ensure rest works with party HP/spells
└── guild.py        # Add quest board functionality
```

**Key Integrations:**

```python
# Integration: Shop ↔ Party
# The shop needs to access party gold and inventory

class ShopInterface:
    """Bridge between Shop system and Party"""
    
    def __init__(self, shop: Shop, party: Party):
        self.shop = shop
        self.party = party
        self.active_character_index = 0
    
    @property
    def active_character(self) -> PlayerCharacter:
        return self.party.members[self.active_character_index]
    
    def get_party_gold(self) -> int:
        return sum(m.gold for m in self.party.members)
    
    def buy_item(self, item_id: str) -> Tuple[bool, str]:
        """Purchase item, deduct gold from active character"""
        item = self.shop.get_item(item_id)
        if not item:
            return False, "Item not found."
        
        if self.active_character.gold < item.price:
            return False, f"Not enough gold. Need {item.price}gp, have {self.active_character.gold}gp."
        
        if not self.active_character.inventory.can_carry(item.weight):
            return False, "Too heavy to carry."
        
        self.active_character.gold -= item.price
        self.active_character.inventory.add(item)
        self.shop.remove_stock(item_id)
        return True, f"Purchased {item.name} for {item.price}gp."
    
    def sell_item(self, item_id: str) -> Tuple[bool, str]:
        """Sell item from active character's inventory"""
        item = self.active_character.inventory.get(item_id)
        if not item:
            return False, "You don't have that item."
        
        sell_price = item.base_price // 2  # 50% buyback
        self.active_character.gold += sell_price
        self.active_character.inventory.remove(item_id)
        return True, f"Sold {item.name} for {sell_price}gp."
```

```python
# Integration: Inn ↔ Party
class InnInterface:
    """Bridge between Inn system and Party"""
    
    def __init__(self, inn: Inn, party: Party):
        self.inn = inn
        self.party = party
    
    def rest(self, nights: int = 1) -> Tuple[bool, str]:
        """Rest party at inn"""
        total_cost = self.inn.rate_per_night * nights * len(self.party.living_members)
        party_gold = sum(m.gold for m in self.party.members)
        
        if party_gold < total_cost:
            return False, f"Not enough gold. Need {total_cost}gp for {nights} night(s)."
        
        # Deduct gold proportionally
        cost_per_member = total_cost // len(self.party.living_members)
        for member in self.party.living_members:
            member.gold -= cost_per_member
        
        # Restore HP and spells
        for member in self.party.living_members:
            member.hp_current = member.hp_max
            member.restore_all_spells()
        
        return True, f"Rested for {nights} night(s). Party fully restored."
```

```python
# Integration: Temple ↔ Party
class TempleInterface:
    """Bridge between Temple services and Party"""
    
    SERVICES = {
        'cure_light': {'cost': 10, 'effect': 'heal', 'amount': '1d8'},
        'cure_serious': {'cost': 50, 'effect': 'heal', 'amount': '2d8+1'},
        'remove_curse': {'cost': 100, 'effect': 'remove_condition', 'condition': 'cursed'},
        'cure_disease': {'cost': 150, 'effect': 'remove_condition', 'condition': 'diseased'},
        'raise_dead': {'cost': 1000, 'effect': 'resurrect', 'requirements': 'body_present'},
    }
    
    def __init__(self, temple: Temple, party: Party):
        self.temple = temple
        self.party = party
    
    def get_available_services(self) -> List[dict]:
        """Return services this temple offers"""
        return [
            {**service, 'name': name}
            for name, service in self.SERVICES.items()
            if name in self.temple.offered_services
        ]
    
    def purchase_service(self, service_name: str, target_character_index: int) -> Tuple[bool, str]:
        """Purchase a temple service for a party member"""
        # Implementation...
```

**New File: City Hub Menu System**

```python
# aerthos/campaign/hub_menu.py
class HubMenuSystem:
    """Handles the menu-driven city hub interface"""
    
    def __init__(self, campaign: Campaign, party: Party):
        self.campaign = campaign
        self.party = party
        self.current_hub = CityHub.load(campaign.current_hub_id)
    
    def display_hub_menu(self) -> str:
        """Generate the hub menu display"""
        lines = [
            f"╔{'═' * 60}╗",
            f"║  CAMPAIGN: {self.campaign.name:<47}║",
            f"║  {self.get_episode_display():<57}║",
            f"╠{'═' * 60}╣",
            f"║  {self.current_hub.name.upper()} - {self.current_hub.theme:<42}║",
            f"║  {'─' * 56}  ║",
            f"║{'':^60}║",
        ]
        
        options = self.get_menu_options()
        for i, option in enumerate(options, 1):
            lines.append(f"║  {i}. {option.name:<54}║")
            if option.description:
                lines.append(f"║     • {option.description:<51}║")
            lines.append(f"║{'':^60}║")
        
        lines.extend([
            f"║  0. Save & Exit Campaign{'':35}║",
            f"║{'':^60}║",
            f"╚{'═' * 60}╝",
        ])
        
        return '\n'.join(lines)
    
    def get_menu_options(self) -> List[MenuOption]:
        """Build menu options based on hub and campaign state"""
        options = []
        
        # Add inn if available
        if self.current_hub.inn:
            options.append(MenuOption(
                id='inn',
                name=self.current_hub.inn.name,
                description=f"Rest and recover ({self.current_hub.inn.rate}gp/night)",
                action='enter_inn'
            ))
        
        # Add shops
        for shop in self.current_hub.shops:
            options.append(MenuOption(
                id=f'shop_{shop.id}',
                name=shop.name,
                description=shop.specialty,
                action='enter_shop',
                data={'shop_id': shop.id}
            ))
        
        # Add temple if available
        if self.current_hub.temple:
            options.append(MenuOption(
                id='temple',
                name=self.current_hub.temple.name,
                description="Healing services",
                action='enter_temple'
            ))
        
        # Add travel/dungeon options
        options.append(self._build_travel_option())
        
        # Add party management
        options.append(MenuOption(
            id='party',
            name='Party Management',
            description=None,
            action='manage_party'
        ))
        
        # Add journal
        options.append(MenuOption(
            id='journal',
            name='Campaign Journal',
            description=None,
            action='view_journal'
        ))
        
        return options
    
    def _build_travel_option(self) -> MenuOption:
        """Build the travel/dungeon option with available destinations"""
        available = self.current_hub.get_available_dungeons(self.campaign)
        completed = [e for e in available if e.id in self.campaign.completed_episodes]
        current = next((e for e in available if e.id == self.campaign.current_episode_id), None)
        locked = [e for e in available if e.id not in self.campaign.unlocked_episodes]
        
        return MenuOption(
            id='travel',
            name='Town Gate / Travel',
            description=f"{len(available)} destinations available",
            action='travel_menu',
            data={
                'current': current,
                'completed': completed,
                'locked': locked
            }
        )
    
    def handle_choice(self, choice: int) -> Tuple[str, Optional[str]]:
        """Process menu choice, return (result_message, next_state)"""
        if choice == 0:
            return "Saving campaign...", 'save_and_exit'
        
        options = self.get_menu_options()
        if choice < 1 or choice > len(options):
            return "Invalid choice.", None
        
        option = options[choice - 1]
        return self._execute_action(option)
    
    def _execute_action(self, option: MenuOption) -> Tuple[str, Optional[str]]:
        """Execute the selected menu action"""
        action_handlers = {
            'enter_inn': self._handle_inn,
            'enter_shop': self._handle_shop,
            'enter_temple': self._handle_temple,
            'travel_menu': self._handle_travel,
            'manage_party': self._handle_party,
            'view_journal': self._handle_journal,
        }
        
        handler = action_handlers.get(option.action)
        if handler:
            return handler(option.data)
        return "Unknown action.", None
```

**Acceptance Criteria:**
- [ ] Can enter shop from hub menu and buy/sell items
- [ ] Can rest at inn and restore HP/spells
- [ ] Can access temple services
- [ ] Can view available dungeons from travel menu
- [ ] Party gold correctly tracked across transactions
- [ ] Existing shop/inn/guild tests still pass
- [ ] New integration tests pass

---

### Phase 3: Episode & Dungeon System

**Goal:** Implement episode progression with narrative and dungeon integration.

**Key Features:**
1. Episode introduction narrative before dungeon
2. Hand-crafted dungeon loading (not just procedural)
3. Completion detection (boss killed, artifact found, etc.)
4. Episode completion narrative and rewards
5. Unlock next episodes

**Episode Flow:**

```
┌─────────────────┐
│  Hub Menu       │
│  Select Dungeon │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Episode Intro  │  "The town of Oakhaven buzzes with worried whispers..."
│  (Narrative)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Quest Briefing │  The Guide: "Word is, goblins have taken over..."
│  (NPC Dialogue) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Confirm Start  │  "Enter the Keep of Kaldor? [Y/N]"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DUNGEON        │  Normal GameState dungeon crawling
│  (Existing      │  Combat, exploration, treasure
│   System)       │
└────────┬────────┘
         │ (Boss defeated / objective complete)
         ▼
┌─────────────────┐
│  Episode        │  "With Grukk defeated, the goblin threat ends..."
│  Completion     │  "You found a serpent medallion..."
│  (Narrative)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Rewards        │  "+500 XP, Dagger +1, Episode 2 Unlocked"
│  Summary        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Return to Hub  │
└─────────────────┘
```

**Hand-Crafted Dungeon Format:**

```json
// data/dungeons/keep_of_kaldor.json
{
    "id": "keep_of_kaldor",
    "name": "The Ruined Keep of Kaldor",
    "description": "An abandoned fortress now home to desperate goblins.",
    "theme": "ruins",
    "recommended_level": 1,
    "levels": [
        {
            "level": 1,
            "name": "Ground Floor",
            "rooms": {
                "entrance": {
                    "id": "entrance",
                    "title": "Collapsed Gatehouse",
                    "description": "The keep's gatehouse has partially collapsed. Rubble blocks most of the entrance, but a narrow path winds through the debris. Goblin tracks are fresh in the dust.",
                    "light_level": "dim",
                    "exits": {"north": "courtyard"},
                    "items": [],
                    "encounter": null,
                    "is_safe_for_rest": false
                },
                "courtyard": {
                    "id": "courtyard",
                    "title": "Overgrown Courtyard",
                    "description": "Weeds push through cracked flagstones. A dry fountain stands at the center, its basin filled with leaves. The main keep looms to the north, while a collapsed tower lies to the east.",
                    "light_level": "bright",
                    "exits": {"south": "entrance", "north": "great_hall", "east": "collapsed_tower"},
                    "items": ["torch", "rope_50ft"],
                    "encounter": {
                        "type": "combat",
                        "trigger": "on_enter",
                        "monsters": ["goblin", "goblin"],
                        "narrative": "Two goblin sentries spot you and raise the alarm!"
                    },
                    "is_safe_for_rest": false
                },
                "great_hall": {
                    "id": "great_hall",
                    "title": "The Great Hall",
                    "description": "Once a grand feasting hall, now a goblin camp. Crude bedrolls surround a fire pit. The smell of roasted rat fills the air. A stairway descends into darkness.",
                    "light_level": "dim",
                    "exits": {"south": "courtyard", "west": "kitchen", "down": "cellar_stairs"},
                    "items": ["rations_3_days", "gold_coins_15"],
                    "encounter": {
                        "type": "combat",
                        "trigger": "on_enter",
                        "monsters": ["goblin", "goblin", "goblin", "goblin_archer"],
                        "narrative": "A pack of goblins scrambles to defend their camp!"
                    },
                    "is_safe_for_rest": false
                }
                // ... more rooms
            },
            "start_room": "entrance"
        },
        {
            "level": 2,
            "name": "Cellars",
            "rooms": {
                "cellar_stairs": {
                    "id": "cellar_stairs",
                    "title": "Cellar Stairway",
                    "description": "Stone steps descend into musty darkness. The walls are damp with condensation. Ahead, you hear guttural voices arguing.",
                    "light_level": "dark",
                    "exits": {"up": "great_hall", "north": "mushroom_farm"},
                    "items": [],
                    "encounter": null,
                    "is_safe_for_rest": false
                },
                "chiefs_chamber": {
                    "id": "chiefs_chamber",
                    "title": "Grukk's Chamber",
                    "description": "This wine cellar has been converted into a crude throne room. A hobgoblin sits on a chair made of barrels, a wickedly sharp dagger at his belt. A strange medallion glints on his chest—a serpent coiled around an eye.",
                    "light_level": "dim",
                    "exits": {"south": "mushroom_farm"},
                    "items": ["serpent_medallion", "gold_coins_50", "dagger_plus_1"],
                    "encounter": {
                        "type": "boss",
                        "trigger": "on_enter",
                        "monsters": ["grukk_hobgoblin_chief", "goblin_bodyguard", "goblin_bodyguard"],
                        "narrative": "Grukk rises from his makeshift throne. 'More food for my people!' he snarls, drawing his dagger.",
                        "boss_id": "grukk_hobgoblin_chief",
                        "on_defeat": {
                            "narrative": "Grukk falls, clutching the strange medallion. 'The Eye... the Eye will avenge...' he gasps before expiring.",
                            "set_flag": "grukk_defeated",
                            "complete_episode": true
                        }
                    },
                    "is_safe_for_rest": false
                }
                // ... more rooms
            },
            "start_room": "cellar_stairs"
        }
    ],
    "special_monsters": {
        "grukk_hobgoblin_chief": {
            "base": "hobgoblin",
            "name": "Grukk the Hobgoblin Chief",
            "hp_override": 18,
            "ac_override": 5,
            "equipment": ["dagger_plus_1", "leather_armor"],
            "is_boss": true
        }
    },
    "special_items": {
        "serpent_medallion": {
            "name": "Serpent Eye Medallion",
            "description": "A bronze medallion depicting a serpent coiled around a single eye. It pulses with faint, cold energy.",
            "type": "quest_item",
            "weight": 0.1,
            "value": 0,
            "story_flag": "found_serpent_medallion"
        }
    }
}
```

**Episode Runner Class:**

```python
# aerthos/campaign/episode_runner.py
class EpisodeRunner:
    """Manages the flow of an episode from intro to completion"""
    
    def __init__(self, campaign: Campaign, episode: Episode, party: Party, ui: 'UIAdapter'):
        self.campaign = campaign
        self.episode = episode
        self.party = party
        self.ui = ui
        self.game_state: Optional[GameState] = None
    
    def run(self) -> EpisodeResult:
        """Execute the full episode flow"""
        
        # 1. Show intro narrative
        self.ui.display_narrative(self.episode.intro_text)
        self.ui.wait_for_continue()
        
        # 2. Show quest briefing
        self._show_briefing()
        
        # 3. Confirm start
        if not self.ui.confirm(f"Enter {self.episode.dungeon_config.name}?"):
            return EpisodeResult(started=False)
        
        # 4. Load and run dungeon
        dungeon = self._load_dungeon()
        self.game_state = GameState(
            party=self.party,
            dungeon=dungeon,
            campaign_context=CampaignContext(
                episode_id=self.episode.id,
                completion_criteria=self.episode.completion_criteria,
                story_flags=self.campaign.story_flags
            )
        )
        
        # 5. Run dungeon (this is the main game loop)
        result = self._run_dungeon()
        
        # 6. Handle completion or retreat
        if result.completed:
            return self._handle_completion()
        elif result.party_wiped:
            return self._handle_party_wipe()
        else:
            return self._handle_retreat()
    
    def _load_dungeon(self) -> Dungeon:
        """Load dungeon from hand-crafted JSON or generate procedurally"""
        config = self.episode.dungeon_config
        
        if config.type == 'hand_crafted':
            return DungeonLoader.load_from_file(config.file)
        else:
            return DungeonGenerator.generate(
                num_rooms=config.num_rooms,
                theme=config.theme,
                party_level=self.party.average_level,
                seed=config.seed
            )
    
    def _run_dungeon(self) -> DungeonResult:
        """Main dungeon crawling loop - delegates to existing GameState"""
        while True:
            # Get player command
            command_str = self.ui.get_command()
            
            # Check for retreat command
            if command_str.lower() in ['retreat', 'flee', 'escape']:
                if self._at_entrance():
                    return DungeonResult(retreated=True)
                else:
                    self.ui.display("You must reach the entrance to retreat.")
                    continue
            
            # Execute command through existing GameState
            result = self.game_state.execute_command(command_str)
            self.ui.display_result(result)
            
            # Check completion criteria
            if self._check_completion():
                return DungeonResult(completed=True)
            
            # Check party wipe
            if self.party.is_wiped():
                return DungeonResult(party_wiped=True)
    
    def _check_completion(self) -> bool:
        """Check if episode completion criteria is met"""
        criteria = self.episode.completion_criteria
        
        if criteria.type == 'boss_defeated':
            return self.game_state.is_boss_defeated(criteria.target)
        elif criteria.type == 'item_found':
            return self.party.has_item(criteria.target)
        elif criteria.type == 'room_reached':
            return self.game_state.current_room_id == criteria.target
        elif criteria.type == 'all_cleared':
            return self.game_state.dungeon.all_encounters_cleared()
        
        return False
    
    def _handle_completion(self) -> EpisodeResult:
        """Process successful episode completion"""
        # Show completion narrative
        self.ui.display_narrative(self.episode.completion_text)
        self.ui.wait_for_continue()
        
        # Apply rewards
        rewards = self.episode.rewards
        
        # XP bonus
        for member in self.party.living_members:
            member.xp += rewards.xp_bonus // len(self.party.living_members)
        
        # Gold bonus
        gold_per_member = rewards.gold_bonus // len(self.party.living_members)
        for member in self.party.living_members:
            member.gold += gold_per_member
        
        # Items go to party leader
        for item_id in rewards.items:
            item = ItemFactory.create(item_id)
            self.party.leader.inventory.add(item)
        
        # Update campaign state
        self.campaign.complete_episode(self.episode.id, rewards)
        
        # Show rewards summary
        self._show_rewards_summary(rewards)
        
        return EpisodeResult(
            completed=True,
            rewards_applied=rewards,
            unlocked_episodes=rewards.unlocks
        )
```

**Acceptance Criteria:**
- [ ] Hand-crafted dungeons load from JSON correctly
- [ ] Episode intro and briefing display properly
- [ ] Dungeon runs using existing GameState system
- [ ] Boss/objective completion detected correctly
- [ ] Episode completion narrative and rewards work
- [ ] New episodes unlock after completion
- [ ] Story flags set correctly
- [ ] Can retreat from dungeon mid-episode

---

### Phase 4: CLI Integration

**Goal:** Integrate campaign system into `main.py` CLI interface.

**Changes to main.py:**

```python
# Add campaign menu option to main menu
def show_main_menu():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                        A E R T H O S                          ║
║           Advanced Dungeons & Dragons 1e Text Adventure       ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  QUICK PLAY                                                   ║
║    1. New Game (Random Party & Dungeon)                       ║
║    2. Load Quick Save                                         ║
║                                                               ║
║  CAMPAIGN MODE                                                ║
║    3. New Campaign                                            ║
║    4. Continue Campaign                                       ║
║                                                               ║
║  MANAGEMENT                                                   ║
║    5. Character Roster                                        ║
║    6. Party Manager                                           ║
║    7. Scenario Library                                        ║
║                                                               ║
║    0. Quit                                                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")

def handle_new_campaign():
    """Start a new campaign"""
    campaign_manager = CampaignManager()
    party_manager = PartyManager()
    
    # List available campaigns
    print("\nAvailable Campaigns:")
    print("  1. The Serpent's Shadow (10 episodes, levels 1-12)")
    # Future: more campaigns
    
    choice = input("\nSelect campaign (1): ").strip() or "1"
    campaign_template = "serpents_shadow"  # Currently only one
    
    # Select or create party
    print("\nSelect Party:")
    print("  1. Create new party")
    print("  2. Use existing party")
    
    party_choice = input("Choice: ").strip()
    if party_choice == "1":
        party = create_party_interactive()
        party_id = party_manager.save_party(party)
    else:
        parties = party_manager.list_parties()
        for i, p in enumerate(parties, 1):
            print(f"  {i}. {p.name} ({len(p.members)} members)")
        idx = int(input("Select party: ")) - 1
        party_id = parties[idx].id
        party = party_manager.load_party(party_id)
    
    # Create campaign
    campaign = campaign_manager.create_campaign(campaign_template, party_id)
    print(f"\nCampaign '{campaign.name}' created!")
    
    # Start campaign loop
    run_campaign(campaign, party)

def run_campaign(campaign: Campaign, party: Party):
    """Main campaign loop"""
    campaign_manager = CampaignManager()
    
    while True:
        # Load current hub
        hub = CityHub.load(campaign.current_hub_id)
        hub_menu = HubMenuSystem(campaign, party)
        
        # Display hub menu
        print(hub_menu.display_hub_menu())
        
        try:
            choice = int(input("\nEnter choice: "))
        except ValueError:
            print("Please enter a number.")
            continue
        
        # Handle choice
        result, next_state = hub_menu.handle_choice(choice)
        print(result)
        
        if next_state == 'save_and_exit':
            campaign_manager.save_campaign(campaign)
            print("Campaign saved. Returning to main menu.")
            break
        elif next_state == 'enter_dungeon':
            # Run episode
            episode = Episode.load(campaign.current_episode_id)
            runner = EpisodeRunner(campaign, episode, party, CLIAdapter())
            episode_result = runner.run()
            
            if episode_result.completed:
                # Save progress
                campaign_manager.save_campaign(campaign)
        elif next_state == 'shop':
            run_shop_interface(hub_menu.current_shop, party)
        elif next_state == 'inn':
            run_inn_interface(hub.inn, party)
        elif next_state == 'temple':
            run_temple_interface(hub.temple, party)
        # ... handle other states

def handle_continue_campaign():
    """Continue an existing campaign"""
    campaign_manager = CampaignManager()
    party_manager = PartyManager()
    
    # List saved campaigns
    campaigns = campaign_manager.list_campaigns()
    
    if not campaigns:
        print("\nNo saved campaigns found.")
        return
    
    print("\nSaved Campaigns:")
    for i, c in enumerate(campaigns, 1):
        print(f"  {i}. {c.name}")
        print(f"     Episode {c.current_episode} | {c.play_time} played")
        print(f"     Last played: {c.last_played}")
    
    choice = int(input("\nSelect campaign: ")) - 1
    campaign = campaign_manager.load_campaign(campaigns[choice].id)
    party = party_manager.load_party(campaign.party_id)
    
    run_campaign(campaign, party)
```

**Acceptance Criteria:**
- [ ] Campaign option appears in main menu
- [ ] Can create new campaign with party selection
- [ ] Can continue saved campaign
- [ ] Hub menu displays correctly in terminal
- [ ] Can navigate to shops, inn, temple, dungeons
- [ ] Episode runs with intro/completion narratives
- [ ] Campaign progress saves correctly
- [ ] All existing CLI functionality still works

---

### Phase 5: Web UI Integration

**Goal:** Add campaign support to Flask web UI (`web_ui/app.py`).

**New Routes:**

```python
# Campaign routes
@app.route('/campaign')
def campaign_menu():
    """Campaign management page"""
    campaign_manager = CampaignManager()
    campaigns = campaign_manager.list_campaigns()
    return render_template('campaign_menu.html', campaigns=campaigns)

@app.route('/campaign/new', methods=['GET', 'POST'])
def new_campaign():
    """Create new campaign"""
    if request.method == 'POST':
        campaign_template = request.form['template']
        party_id = request.form['party_id']
        
        campaign_manager = CampaignManager()
        campaign = campaign_manager.create_campaign(campaign_template, party_id)
        
        session['campaign_id'] = campaign.id
        return redirect(url_for('campaign_hub'))
    
    # GET: Show campaign creation form
    party_manager = PartyManager()
    parties = party_manager.list_parties()
    return render_template('new_campaign.html', parties=parties)

@app.route('/campaign/continue/<campaign_id>')
def continue_campaign(campaign_id):
    """Continue existing campaign"""
    session['campaign_id'] = campaign_id
    return redirect(url_for('campaign_hub'))

@app.route('/campaign/hub')
def campaign_hub():
    """City hub interface"""
    campaign_id = session.get('campaign_id')
    if not campaign_id:
        return redirect(url_for('campaign_menu'))
    
    campaign_manager = CampaignManager()
    party_manager = PartyManager()
    
    campaign = campaign_manager.load_campaign(campaign_id)
    party = party_manager.load_party(campaign.party_id)
    hub = CityHub.load(campaign.current_hub_id)
    
    # Get current episode info
    current_episode = None
    if campaign.current_episode_id:
        current_episode = Episode.load(campaign.current_episode_id)
    
    return render_template('campaign_hub.html',
        campaign=campaign,
        party=party,
        hub=hub,
        current_episode=current_episode
    )

@app.route('/campaign/shop/<shop_id>')
def campaign_shop(shop_id):
    """Shop interface within campaign"""
    campaign_id = session.get('campaign_id')
    # ... load campaign, party, shop
    return render_template('campaign_shop.html', ...)

@app.route('/api/campaign/shop/buy', methods=['POST'])
def api_shop_buy():
    """API endpoint for buying items"""
    data = request.json
    item_id = data['item_id']
    character_index = data['character_index']
    
    # ... process purchase
    return jsonify({'success': True, 'message': '...'})

@app.route('/campaign/episode/start/<episode_id>')
def start_episode(episode_id):
    """Start an episode - show intro, then dungeon"""
    campaign_id = session.get('campaign_id')
    # ... load everything
    
    episode = Episode.load(episode_id)
    session['active_episode_id'] = episode_id
    
    return render_template('episode_intro.html',
        episode=episode,
        campaign=campaign
    )

@app.route('/campaign/dungeon')
def campaign_dungeon():
    """Dungeon interface during episode"""
    # This uses the existing game interface but with campaign context
    campaign_id = session.get('campaign_id')
    episode_id = session.get('active_episode_id')
    
    # ... load game state with campaign context
    return render_template('game.html',  # Reuse existing template
        campaign_mode=True,
        episode=episode,
        campaign=campaign
    )
```

**New Templates:**

```
web_ui/templates/
├── campaign_menu.html        # List campaigns, new/continue buttons
├── new_campaign.html         # Campaign creation form
├── campaign_hub.html         # City hub with menu options
├── campaign_shop.html        # Shop interface
├── campaign_inn.html         # Inn interface
├── campaign_temple.html      # Temple interface
├── campaign_travel.html      # Travel/dungeon selection
├── episode_intro.html        # Episode intro narrative
├── episode_briefing.html     # Quest briefing
└── episode_complete.html     # Completion screen
```

**Acceptance Criteria:**
- [ ] Campaign menu accessible from web UI main page
- [ ] Can create and continue campaigns via web UI
- [ ] Hub menu renders correctly with all options
- [ ] Shop/Inn/Temple interfaces work via web UI
- [ ] Episode intro and completion screens display
- [ ] Dungeon gameplay works within campaign context
- [ ] Campaign state persists across browser sessions
- [ ] Web UI campaign behavior matches CLI behavior

---

### Phase 6: Content Creation - Episodes 1-3

**Goal:** Create complete content for Act I (Episodes 1-3).

**Episode 1: The Goblin Refugees**

Files to create:
- `data/episodes/episode_01_goblin_refugees.json`
- `data/dungeons/keep_of_kaldor.json` (hand-crafted, ~15 rooms)

Dungeon design:
- Level 1: Gatehouse, courtyard, great hall, kitchen, tower
- Level 2: Cellars, mushroom farm, prison, chief's chamber
- Boss: Grukk the Hobgoblin Chief
- Key item: Serpent Eye Medallion
- Treasure: ~200gp total, Dagger +1

**Episode 2: The Cult Below**

Files to create:
- `data/episodes/episode_02_cult_below.json`
- `data/dungeons/oakhaven_sewers.json` (hand-crafted, ~20 rooms)

Dungeon design:
- Level 1: Sewer entrance, main tunnels, rat warrens
- Level 2: Cult hideout, ritual chamber, prison cells
- Level 3: Flooded passages, ancient shrine
- Boss: Cult Fanatic (cleric level 3)
- Key items: Cult robes, ritual notes, kidnapped townsfolk
- Treasure: ~400gp total, Mace +1

**Episode 3: The Merchant's Secret**

Files to create:
- `data/episodes/episode_03_merchants_secret.json`
- `data/dungeons/silas_warehouse.json` (hand-crafted, ~12 rooms)

Dungeon design:
- Level 1: Warehouse (trapped), hidden basement entrance
- Level 2: Underground workshop, cursed item storage
- Level 3: Escape tunnel to outside Oakhaven
- Boss: Silas (Fighter 4) + hired thugs
- Revelation: Silas was middleman, not cult leader
- Treasure: ~600gp total, choice of cursed item (cleansed)

**Oakhaven City Data:**

```json
// data/cities/oakhaven.json
{
    "id": "oakhaven",
    "name": "Oakhaven",
    "description": "A fortified wooden palisade town at the foot of the Shattered Peaks. The gateway to adventure—and exploitation.",
    "theme": "Frontier Town",
    "region": "Verdant Heartlands",
    
    "special_rules": {
        "gate_toll": 5,
        "currency_exchange_rate": 0.9,
        "inflation_multiplier": 1.5
    },
    
    "shops": [
        {
            "id": "silas_shop",
            "name": "Silas's Equipment Emporium",
            "type": "general",
            "specialty": "Adventuring supplies at 'fair' prices",
            "buy_rate": 0.4,
            "inventory": ["longsword", "chain_mail", "shield", "torch", "rope_50ft", "rations_1_week", "backpack", "lantern", "oil_flask"],
            "price_modifier": 1.5
        }
    ],
    
    "inn": {
        "id": "dirty_mug",
        "name": "The Dirty Mug",
        "description": "A rough tavern catering to adventurers. The ale is watered, the beds are lumpy, but the rumors are priceless.",
        "rate_per_night": 10,
        "services": ["rest", "rumors", "hirelings"],
        "rumors_by_episode": {
            "episode_01": [
                "The goblins came from the High Pass. Something scared them out of their mountain homes.",
                "Old Kaldor fell to plague decades ago. The keep's been abandoned ever since.",
                "Silas has been buying goblin weapons lately. Strange business."
            ],
            "episode_02": [
                "Three more people went missing last week. The watch says nothing.",
                "Old Marta saw hooded figures near the old well at midnight.",
                "There's something wrong with the new temple acolyte. His eyes..."
            ]
        }
    },
    
    "temple": {
        "id": "temple_of_light",
        "name": "Temple of Light",
        "deity": "Pelor (equivalent)",
        "alignment": "Lawful Good",
        "services": ["cure_light", "cure_serious", "remove_curse"],
        "donation_suggested": true
    },
    
    "npcs": {
        "silas": {
            "name": "Silas",
            "role": "Merchant",
            "alignment": "Lawful Evil",
            "description": "An immaculately dressed man with cold, calculating eyes. He buys low and sells high—always.",
            "dialogue": {
                "greeting": "Ah, more heroes seeking their fortune. I'm sure we can come to a... mutually beneficial arrangement.",
                "haggle_fail": "I'm afraid that's my final offer. Take it or leave it.",
                "episode_03_confrontation": "You've uncovered my little side business. But I'm just a middleman! The real power lies elsewhere..."
            }
        },
        "the_guide": {
            "name": "The Guide",
            "role": "Quest Giver",
            "alignment": "True Neutral",
            "description": "A weathered man who knows every trail and ruin within a hundred miles. Information has a price.",
            "dialogue": {
                "greeting": "Looking for work? Danger? Both? I know a few places...",
                "episode_01_hook": "Word is, goblins have taken over the old Keep of Kaldor. Desperate ones—they're taking food, not gold.",
                "episode_02_hook": "People are vanishing from the streets at night. The militia's useless. Might be coin in solving that mystery."
            }
        }
    }
}
```

**Acceptance Criteria:**
- [ ] Episode 1 fully playable from hub to completion
- [ ] Episode 2 fully playable from hub to completion
- [ ] Episode 3 fully playable from hub to completion
- [ ] All Oakhaven shops, inn, temple functional
- [ ] Rumors change based on current episode
- [ ] NPCs have appropriate dialogue
- [ ] Story flags track correctly across episodes
- [ ] Episode 2 unlocks after Episode 1
- [ ] Episode 3 unlocks after Episode 2

---

### Phase 7: Content Creation - Episodes 4-6

**Goal:** Create Act II content with new city hubs.

**Episode 4: The Dwarven Distress**
- New hub: Ironfast Outpost
- Dungeon: Duergar-Occupied Hold (~25 rooms, 3 levels)
- Boss: Duergar Warlord
- Introduces dwarven faction reputation

**Episode 5: The Marsh Temple**
- New hub: Mire's Edge
- Dungeon: Sunken Temple (~20 rooms, underwater sections)
- Boss: Lizardfolk High Shaman OR Cult Archpriest (choice matters)
- Lizardfolk can become allies

**Episode 6: The Orc Truce**
- Hub: Mire's Edge (return)
- Dungeon: Scorched Fortress (~22 rooms, fire hazards)
- Boss: Fire Giant Champion
- Orc alliance possible (affects later episodes)

**New City Hubs:**

```json
// data/cities/ironfast_outpost.json
{
    "id": "ironfast_outpost",
    "name": "Ironfast Outpost",
    "description": "A dwarven military encampment carved into the mountainside. Discipline is absolute.",
    "theme": "Military Fortress",
    "region": "Shattered Peaks",
    
    "special_rules": {
        "entry_requirements": ["episode_04_in_progress"],
        "full_access_requirements": ["episode_04_complete"],
        "no_non_dwarves_in_barracks": true
    },
    
    "shops": [
        {
            "id": "dwarven_forge",
            "name": "Master Durin's Forge",
            "type": "weapons_armor",
            "specialty": "Dwarven-quality arms and armor",
            "inventory": ["dwarven_waraxe", "dwarven_plate", "dwarven_shield"],
            "price_modifier": 1.2,
            "quality_bonus": "+1 durability"
        }
    ],
    
    "inn": null,
    
    "barracks": {
        "id": "outpost_barracks",
        "name": "Soldier's Rest",
        "description": "Austere but clean. Dwarves only, unless you've proven yourself.",
        "rate_per_night": 0,
        "requirements": ["is_dwarf OR episode_04_complete"]
    }
}
```

---

### Phase 8: Content Creation - Episodes 7-10

**Goal:** Complete the campaign with Acts III and IV.

**Episode 7: The Sunken City**
- New hub: Coastal Haven
- Dungeon: Drowned Ruins of Ys'Thara (~30 rooms, mostly underwater)
- Boss: Aboleth or Cult High Priest
- Major artifact: The Serpent's Fang

**Episode 8: The Syndic's Treachery**
- New hub: Eldoria (capital city)
- Dungeon: Eldoria Catacombs (~25 rooms)
- Boss: Corrupted Syndic + Devil ally
- Political intrigue, multiple paths

**Episode 9: The Planar Rift**
- Hub: Eldoria
- Dungeon: Elemental Chaos (~20 rooms, elemental hazards)
- Boss: Elemental Prince servant
- Closes the rift

**Episode 10: The Serpent's Awakening**
- Hub: Return to Oakhaven (under siege)
- Dungeon: Serpent Temple (~35 rooms, final dungeon)
- Final boss: The Serpent Eye avatar
- Multiple endings based on choices

---

### Phase 9: Polish & Balance

**Goal:** Final testing, balance adjustments, bug fixes.

**Tasks:**
- [ ] Full playthrough testing (all 10 episodes)
- [ ] Economy balance (gold income vs prices)
- [ ] XP curve balance (levels should match recommendations)
- [ ] Combat difficulty tuning
- [ ] Narrative consistency check
- [ ] All tests pass (original 417 + new campaign tests)
- [ ] CLI/Web UI parity verification
- [ ] Save/load stress testing
- [ ] Edge case handling (party wipes, mid-episode saves, etc.)

---

## PART 4: DATA FILE SPECIFICATIONS

### Campaign Template Schema

```json
{
    "$schema": "campaign_template_v1",
    "id": "string",
    "name": "string",
    "description": "string",
    "author": "string",
    "version": "1.0",
    "recommended_party_size": [4, 6],
    "level_range": [1, 12],
    "episodes": ["episode_01", "episode_02", ...],
    "starting_hub": "hub_id",
    "starting_episode": "episode_id",
    "factions": {
        "faction_id": {
            "name": "string",
            "description": "string",
            "starting_reputation": 0
        }
    }
}
```

### Episode Schema

```json
{
    "$schema": "episode_v1",
    "id": "string",
    "title": "string",
    "act": "integer",
    "recommended_level": "integer",
    "hub_id": "string",
    "intro_text": "string (supports \\n for paragraphs)",
    "briefing": {
        "quest_giver": "string",
        "location": "string",
        "dialogue": "string"
    },
    "dungeon": {
        "type": "hand_crafted | procedural",
        "file": "path/to/dungeon.json (if hand_crafted)",
        "config": { ... } // (if procedural)
    },
    "completion_criteria": {
        "type": "boss_defeated | item_found | room_reached | all_cleared",
        "target": "string"
    },
    "completion_text": "string",
    "rewards": {
        "xp_bonus": "integer",
        "gold_bonus": "integer",
        "items": ["item_id", ...],
        "unlocks": ["episode_id", ...],
        "story_flags": ["flag_name", ...]
    },
    "rumors": ["string", ...],
    "prerequisites": ["episode_id", ...]
}
```

### City Hub Schema

```json
{
    "$schema": "city_hub_v1",
    "id": "string",
    "name": "string",
    "description": "string",
    "theme": "string",
    "region": "string",
    "special_rules": { ... },
    "shops": [ { ... } ],
    "inn": { ... } | null,
    "temple": { ... } | null,
    "guild": { ... } | null,
    "npcs": { "npc_id": { ... } }
}
```

### Hand-Crafted Dungeon Schema

```json
{
    "$schema": "dungeon_v1",
    "id": "string",
    "name": "string",
    "description": "string",
    "theme": "string",
    "recommended_level": "integer",
    "levels": [
        {
            "level": "integer",
            "name": "string",
            "rooms": {
                "room_id": {
                    "id": "string",
                    "title": "string",
                    "description": "string",
                    "light_level": "bright | dim | dark",
                    "exits": { "direction": "room_id", ... },
                    "items": ["item_id", ...],
                    "encounter": { ... } | null,
                    "is_safe_for_rest": "boolean"
                }
            },
            "start_room": "room_id"
        }
    ],
    "special_monsters": { "monster_id": { ... } },
    "special_items": { "item_id": { ... } }
}
```

---

## PART 5: TESTING REQUIREMENTS

### New Test Files

```
tests/
├── test_campaign.py
│   ├── test_campaign_creation
│   ├── test_campaign_serialization
│   ├── test_episode_unlock_logic
│   ├── test_story_flag_management
│   └── test_reputation_tracking
│
├── test_episode.py
│   ├── test_episode_loading
│   ├── test_completion_criteria_boss
│   ├── test_completion_criteria_item
│   ├── test_completion_criteria_room
│   ├── test_rewards_application
│   └── test_prerequisite_checking
│
├── test_city_hub.py
│   ├── test_hub_loading
│   ├── test_menu_generation
│   ├── test_shop_integration
│   ├── test_inn_integration
│   ├── test_temple_integration
│   └── test_travel_options
│
├── test_campaign_manager.py
│   ├── test_save_campaign
│   ├── test_load_campaign
│   ├── test_list_campaigns
│   └── test_delete_campaign
│
├── test_hand_crafted_dungeons.py
│   ├── test_dungeon_loading
│   ├── test_room_connections
│   ├── test_special_monsters
│   ├── test_special_items
│   └── test_encounter_triggers
│
├── test_episode_runner.py
│   ├── test_full_episode_flow
│   ├── test_intro_display
│   ├── test_completion_detection
│   ├── test_retreat_handling
│   └── test_party_wipe_handling
│
└── test_campaign_integration.py
    ├── test_full_episode_1_playthrough
    ├── test_episode_progression
    ├── test_shop_transactions
    ├── test_inn_rest
    └── test_temple_services
```

### Test Commands

```bash
# Run all tests (should still be 417+ passing)
python3 run_tests.py --no-web

# Run only campaign tests
python3 -m pytest tests/test_campaign*.py -v

# Run specific test
python3 -m pytest tests/test_campaign.py::test_episode_unlock_logic -v
```

---

## PART 6: DEVELOPMENT WORKFLOW

### Session Start Checklist

Before starting any work session:

1. **Pull latest changes** (if applicable)
2. **Run tests:** `python3 run_tests.py --no-web`
3. **Verify all 417+ tests pass**
4. **Read this document's current phase**
5. **Check for TODO comments in code**

### Session End Checklist

Before ending any work session:

1. **Run tests:** `python3 run_tests.py --no-web`
2. **Verify no test regressions**
3. **Add TODO comments for incomplete work**
4. **Update this document if design changed**
5. **Commit with descriptive message**

### Commit Message Format

```
[Phase X] Brief description

- Specific change 1
- Specific change 2
- Tests: X new, Y total passing
```

Example:
```
[Phase 1] Implement Campaign and Episode base classes

- Created aerthos/campaign/ module
- Added Campaign dataclass with serialization
- Added Episode dataclass with loading from JSON
- Tests: 15 new, 432 total passing
```

---

## PART 7: QUICK REFERENCE

### Key File Locations

| Component | Location |
|-----------|----------|
| Campaign classes | `aerthos/campaign/` (NEW) |
| Campaign data | `aerthos/data/campaigns/` (NEW) |
| Episode data | `aerthos/data/episodes/` (NEW) |
| City data | `aerthos/data/cities/` (NEW) |
| Dungeon data | `aerthos/data/dungeons/` (NEW) |
| Existing Village | `aerthos/world/village.py` |
| Existing Shop | `aerthos/world/shop.py` |
| Existing Inn | `aerthos/world/inn.py` |
| CLI Entry | `main.py` |
| Web Entry | `web_ui/app.py` |
| Tests | `tests/` |

### Existing APIs to Use

```python
# Character/Party
from aerthos.entities.player import PlayerCharacter, Inventory
from aerthos.entities.party import Party

# Dungeon
from aerthos.world.dungeon import Dungeon
from aerthos.world.room import Room
from aerthos.generator.dungeon_generator import DungeonGenerator

# Game State
from aerthos.engine.game_state import GameState
from aerthos.engine.parser import CommandParser

# Storage
from aerthos.storage.character_roster import CharacterRoster
from aerthos.storage.party_manager import PartyManager
from aerthos.storage.session_manager import SessionManager
```

### Command to Run Game

```bash
# CLI
python main.py

# Web UI
python web_ui/app.py
# Then open http://localhost:5000
```

---

## APPENDIX A: NARRATIVE CONTENT GUIDELINES

### Writing Style

- **Tone:** Gritty, grounded fantasy. Not grimdark, but consequences matter.
- **Voice:** Second person ("You enter the chamber...") for gameplay, third person for cutscenes
- **Length:** Intro paragraphs 3-5 sentences. Room descriptions 2-3 sentences.
- **Show don't tell:** "The air smells of rot" not "This is a dangerous place"

### Episode Intro Template

```
[Setting the scene - 2-3 sentences establishing location/atmosphere]

[The problem - 2-3 sentences explaining what's wrong]

[The hook - 1-2 sentences drawing player in]

[Optional: Foreshadowing larger plot]
```

### Room Description Template

```
[Visual description - what you see first]

[Sensory details - smell, sound, temperature]

[Interactive elements - exits, items, notable features]
```

### NPC Dialogue Guidelines

- Each NPC has distinct voice/vocabulary
- Silas: Formal, calculating, slightly condescending
- The Guide: Laconic, practical, mercenary
- Temple Priest: Earnest, hopeful, naive
- Dwarves: Gruff, honorable, suspicious of outsiders
- Lizardfolk: Alien thought patterns, cold logic

---

## APPENDIX B: MONSTER ENCOUNTER GUIDELINES

### Encounter Difficulty by Level

| Party Level | Easy | Medium | Hard | Deadly |
|-------------|------|--------|------|--------|
| 1 | 2 goblins | 4 goblins | 6 goblins + leader | 8 goblins + hobgoblin |
| 2-3 | 4 goblins | 2 orcs | 4 orcs | Ogre |
| 4-5 | 2 orcs | Ogre | Ogre + orcs | Hill giant |
| 6-7 | Ogre | Hill giant | 2 hill giants | Fire giant |

### Boss Design

- HP: 50% more than standard for type
- Special ability or magic item
- Lair has tactical features
- Minions appropriate to boss level
- Death triggers narrative/completion

---

## APPENDIX C: ECONOMY BALANCE

### Gold Income by Episode

| Episode | Dungeon Treasure | Quest Reward | Total |
|---------|-----------------|--------------|-------|
| 1 | ~200gp | 100gp | 300gp |
| 2 | ~400gp | 150gp | 550gp |
| 3 | ~600gp | 200gp | 800gp |
| 4 | ~1000gp | 300gp | 1300gp |
| 5 | ~1200gp | 400gp | 1600gp |
| 6 | ~1500gp | 500gp | 2000gp |
| ... | ... | ... | ... |

### Price Reference (Oakhaven, with 1.5x inflation)

| Item | Base Price | Oakhaven Price |
|------|------------|----------------|
| Longsword | 15gp | 23gp |
| Chain mail | 75gp | 113gp |
| Torch | 1cp | 2cp |
| Rations (1 week) | 3gp | 5gp |
| Healing potion | 50gp | 75gp |

---

*End of Implementation Plan*

**Document Version:** 1.0  
**Last Updated:** November 2024  
**Target Completion:** 8-10 weeks of development
