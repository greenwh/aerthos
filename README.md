# Aerthos - AD&D 1e Text Adventure

A faithful recreation of Advanced Dungeons & Dragons 1st Edition as a complete single-player campaign.

## Features

- **Authentic AD&D 1e Mechanics**
  - THAC0 combat system with descending AC
  - Vancian magic with spell memorization and 332 spells
  - 5-category saving throws
  - Thief skills with percentile rolls
  - Resource management (light sources, rations, encumbrance)
  - Nine-point alignment system with class restrictions

- **11 Character Classes**
  - **Warriors:** Fighter, Ranger, Paladin
  - **Priests:** Cleric, Druid
  - **Wizards:** Magic-User, Illusionist
  - **Rogues:** Thief, Assassin
  - **Special:** Monk, Bard

- **Four Classic Races**
  - Human - Versatile and balanced
  - Elf - Graceful and magical
  - Dwarf - Tough and resilient
  - Halfling - Small and nimble

- **10-Episode Campaign: "Rise of the Serpent Cult"**
  - 11 hand-crafted dungeons across 5 city hubs
  - Episodes 1-10 with narrative continuity
  - 280+ monsters with varied abilities
  - Progressive difficulty (levels 1-10)
  - 20 side quests with unique rewards
  - Underwater episodes with waterbreathing mechanics
  - Reputation system tracking your standing in each city

- **Comprehensive Game Systems**
  - Auto-mapping that reveals as you explore
  - Multiple save systems (quick save, character roster, party manager, session manager)
  - City hubs with shops, inns, temples, and guilds
  - Quest system with optional side content
  - Time tracking with resource depletion
  - Flexible natural language parser
  - CLI and Web UI interfaces
  - Character death is permanent (restore from saves)

## Installation

Requires Python 3.10 or higher.

```bash
# Clone the repository
git clone https://github.com/greenwh/aerthos.git
cd aerthos

# No additional dependencies needed - uses only Python standard library!
```

## How to Play

```bash
python main.py
```

### Basic Commands

- **Movement**: `go north`, `n`, `south`, `east`, `west`
- **Combat**: `attack orc`, `cast magic missile`
- **Items**: `take sword`, `equip longsword`, `use potion`, `drop torch`
- **Exploration**: `search`, `look`, `map`
- **Character**: `inventory`, `status`, `rest`
- **Game**: `save`, `help`, `quit`

### Tips for Survival

1. **Manage Your Light** - Torches burn out! Carry spares and watch for warnings.
2. **Rest When Safe** - Find safe rooms to restore HP and spells.
3. **Search Carefully** - Thieves can find and disarm traps; others might trigger them!
4. **Know Your Limits** - Combat is lethal. Retreat to safe rooms if wounded.
5. **Save Often** - Character death is permanent. Use save points wisely.

## The AD&D 1e Experience

This game recreates the feel of classic 1st Edition AD&D:

- **Lethal Combat** - Hit points are precious. A few bad rolls can end your adventure.
- **Resource Management** - Track light, food, and spell slots carefully.
- **Old School Challenge** - No hand-holding. Exploration and caution are rewarded.
- **Dice Control Your Fate** - Roll 3d6 in order for abilities. No re-rolls!

## Project Structure

```
aerthos/
├── engine/          # Core game systems (combat, parser, state)
├── entities/        # Character and monster classes
├── systems/         # Magic, skills, saving throws
├── world/           # Dungeon, rooms, encounters, auto-map
├── data/            # JSON data files (classes, monsters, items, spells)
├── ui/              # Display, character creation, save system
└── tests/           # Unit tests

main.py              # Game entry point
```

## Game Design

Aerthos follows these AD&D 1e principles:

- **THAC0**: Roll d20, hit if `roll >= (THAC0 - target AC)`
- **Saving Throws**: Roll d20, succeed if `roll <= save value`
- **Vancian Magic**: Memorize spells, cast once, restore on rest
- **Turn-Based Time**: 1 turn = 10 minutes, important for resource tracking
- **Side Initiative**: Whole party vs. monsters (d6 each side)

## Development Status

**Current Version**: 2.0 - Campaign Complete
**Status**: ✅ **READY FOR RELEASE**
**Test Coverage**: 541/541 tests passing (100%)

**Completed Features:**
- ✅ Full 10-episode campaign (Episodes 1-10)
- ✅ 11 character classes with unique abilities
- ✅ 11 hand-crafted dungeons (15-18 rooms each)
- ✅ 280+ monsters with varied abilities and behaviors
- ✅ 332 spells across all caster classes
- ✅ 20 side quests with unique rewards
- ✅ Reputation system tracking
- ✅ City hub system (5 cities with shops, inns, temples, guilds)
- ✅ Complete combat, magic, and skill systems
- ✅ Auto-mapping and navigation
- ✅ Comprehensive save/load systems
- ✅ CLI and Web UI interfaces
- ✅ Full test coverage (541 automated tests)

**Campaign Stats:**
- **XP Available**: 464,305 (main story) + 15,100 (side quests) = 479,405 total
- **Character Progression**: Level 1 → Level 9-10
- **Gold Available**: ~27,925 gp (main story) + quest rewards
- **Playtime**: 15-20 hours for full campaign completion

**Optional Future Enhancements:**
- Reputation effects (shop discounts, faction bonuses)
- Multiple endings for Episode 10 based on player choices
- Additional episodes expanding the campaign
- Wilderness/overworld map system

## License

This is a fan project created for educational and entertainment purposes.
Dungeons & Dragons is a trademark of Wizards of the Coast.

## Credits

Designed to capture the spirit of Gary Gygax and Dave Arneson's original Advanced Dungeons & Dragons.

Built with Python 3 and lots of nostalgia for those classic dice-rolling adventures!

---

**May your hits be critical and your saves be high!**
