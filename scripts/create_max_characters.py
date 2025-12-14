#!/usr/bin/env python3
"""
Create max-level test characters for testing high-level content
Creates: MaxF, MaxC, MaxM, MaxT (Fighter, Cleric, Magic-User, Thief)
All level 10, max stats (18 across the board), Human, True Neutral
"""

import sys
from pathlib import Path

# Add aerthos to path
sys.path.insert(0, str(Path(__file__).parent))

from aerthos.engine.game_state import GameData
from aerthos.entities.player import PlayerCharacter, XP_TABLES
from aerthos.storage.character_roster import CharacterRoster
from aerthos.ui.character_creation import CharacterCreator


def calculate_max_hp(char_class: str, level: int, constitution: int = 18) -> int:
    """Calculate maximum HP for a character"""
    hit_dice = {
        'Fighter': 10,
        'Cleric': 8,
        'Magic-User': 4,
        'Thief': 6
    }

    die_size = hit_dice.get(char_class, 6)

    # CON bonus for 18 CON is +4 HP per level (AD&D 1e)
    con_bonus = 4

    # Max HP: max die roll for each level + CON bonus per level
    max_hp = (die_size * level) + (con_bonus * level)

    return max_hp


def calculate_thac0(char_class: str, level: int) -> int:
    """Calculate THAC0 for a character at given level"""
    # AD&D 1e THAC0 progression
    if char_class in ['Fighter', 'Ranger', 'Paladin']:
        # Warriors: Start at 20, -1 per level
        return 20 - level
    elif char_class in ['Cleric', 'Druid']:
        # Priests: Start at 20, -2 every 3 levels
        return 20 - ((level - 1) // 3) * 2
    elif char_class in ['Magic-User', 'Illusionist']:
        # Wizards: Start at 20, -1 every 3 levels
        return 20 - ((level - 1) // 3)
    elif char_class in ['Thief', 'Assassin']:
        # Rogues: Start at 20, -1 every 2 levels
        return 20 - ((level - 1) // 2)
    else:
        return 20 - level


def calculate_saves(char_class: str, level: int, base_saves: dict) -> dict:
    """Calculate saving throws for a character at given level"""
    # AD&D 1e saving throw progression (simplified)
    # Generally improve by 1 every 3-5 levels

    saves = base_saves.copy()

    # Improvement per 3 levels
    improvement = (level - 1) // 3

    for save_type in saves:
        saves[save_type] = max(1, base_saves[save_type] - improvement)

    return saves


def create_max_character(name: str, char_class: str, game_data: GameData) -> PlayerCharacter:
    """Create a max-level character"""

    level = 10
    race = "Human"
    alignment = "True Neutral"

    # Max stats (18 for everything)
    strength = 18
    dexterity = 18
    constitution = 18
    intelligence = 18
    wisdom = 18
    charisma = 18

    # Exceptional strength for Fighter
    strength_percentile = 100 if char_class == 'Fighter' else 0

    # Calculate HP
    hp_max = calculate_max_hp(char_class, level, constitution)
    hp_current = hp_max

    # Get class data
    class_data = game_data.classes[char_class]

    # Calculate THAC0
    thac0 = calculate_thac0(char_class, level)

    # Calculate saves
    base_saves = class_data['saves']
    saves = calculate_saves(char_class, level, base_saves)

    # XP (set to minimum for level 10)
    xp_table = XP_TABLES.get(char_class, [0] * 11)
    xp = xp_table[level - 1] if level <= len(xp_table) else xp_table[-1]

    # Create character
    player = PlayerCharacter(
        name=name,
        race=race,
        char_class=char_class,
        level=level,
        strength=strength,
        dexterity=dexterity,
        constitution=constitution,
        intelligence=intelligence,
        wisdom=wisdom,
        charisma=charisma,
        strength_percentile=strength_percentile,
        hp_current=hp_current,
        hp_max=hp_max,
        ac=10,  # Will be recalculated with equipment
        thac0=thac0,
        save_poison=saves['poison'],
        save_rod_staff_wand=saves['rod_staff_wand'],
        save_petrify_paralyze=saves['petrify_paralyze'],
        save_breath=saves['breath'],
        save_spell=saves['spell'],
        xp=xp,
        alignment=alignment
    )

    # Use CharacterCreator to assign equipment
    creator = CharacterCreator(game_data)

    # Assign starting equipment based on class
    creator._add_starting_equipment(player, char_class)

    # Assign spells for casters at appropriate level
    if char_class in ['Cleric', 'Magic-User']:
        assign_high_level_spells(player, char_class, level, class_data, game_data)

    return player


def assign_high_level_spells(player: PlayerCharacter, char_class: str, level: int,
                              class_data: dict, game_data: GameData):
    """Assign spell slots and known spells for high-level casters"""
    from aerthos.entities.player import Spell

    # AD&D 1e Spell Progression Tables (spell level slots by character level)
    # Format: [1st, 2nd, 3rd, 4th, 5th, 6th, 7th, 8th, 9th level spells]
    CLERIC_SPELL_SLOTS = {
        1: [1, 0, 0, 0, 0, 0, 0],
        2: [2, 0, 0, 0, 0, 0, 0],
        3: [2, 1, 0, 0, 0, 0, 0],
        4: [3, 2, 0, 0, 0, 0, 0],
        5: [3, 3, 1, 0, 0, 0, 0],
        6: [3, 3, 2, 0, 0, 0, 0],
        7: [3, 3, 2, 1, 0, 0, 0],
        8: [3, 3, 3, 2, 0, 0, 0],
        9: [4, 4, 3, 2, 1, 0, 0],
        10: [4, 4, 3, 3, 2, 0, 0]
    }

    MAGIC_USER_SPELL_SLOTS = {
        1: [1, 0, 0, 0, 0, 0, 0, 0, 0],
        2: [2, 0, 0, 0, 0, 0, 0, 0, 0],
        3: [2, 1, 0, 0, 0, 0, 0, 0, 0],
        4: [3, 2, 0, 0, 0, 0, 0, 0, 0],
        5: [4, 2, 1, 0, 0, 0, 0, 0, 0],
        6: [4, 2, 2, 0, 0, 0, 0, 0, 0],
        7: [4, 3, 2, 1, 0, 0, 0, 0, 0],
        8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
        9: [4, 3, 3, 2, 1, 0, 0, 0, 0],
        10: [4, 4, 3, 2, 2, 0, 0, 0, 0]
    }

    # Get spell slot progression for this class and level
    spell_slots = None
    if char_class == 'Cleric':
        spell_slots = CLERIC_SPELL_SLOTS.get(level, [0])
    elif char_class == 'Magic-User':
        spell_slots = MAGIC_USER_SPELL_SLOTS.get(level, [0])

    if not spell_slots:
        print(f"  ⚠ No spell progression defined for {char_class} level {level}")
        return

    # Add spell slots for each spell level
    max_spell_level = 0
    for spell_level_idx, num_slots in enumerate(spell_slots):
        if num_slots > 0:
            spell_level = spell_level_idx + 1  # Convert 0-indexed to 1-indexed
            for _ in range(num_slots):
                player.add_spell_slot(spell_level)
            max_spell_level = spell_level

    # Add all spells up to max_spell_level
    for spell_id, spell_data in game_data.spells.items():
        if char_class in spell_data.get('class_availability', []):
            spell_level = spell_data.get('level', 1)
            # Only add spells the character can actually cast
            if spell_level <= max_spell_level:
                spell = Spell(
                    name=spell_data['name'],
                    level=spell_data['level'],
                    school=spell_data['school'],
                    casting_time=spell_data['casting_time'],
                    range=spell_data['range'],
                    duration=spell_data['duration'],
                    area_of_effect=spell_data['area'],
                    saving_throw=spell_data['saving_throw'],
                    components=spell_data['components'],
                    description=spell_data['description'],
                    class_availability=spell_data['class_availability']
                )
                player.spells_known.append(spell)

    print(f"  ✓ Added {len(player.spells_known)} spells (levels 1-{max_spell_level})")
    print(f"  ✓ Added {len(player.spells_memorized)} spell slots")


def main():
    """Create and save max-level test characters"""

    print("═" * 70)
    print("Creating Max-Level Test Characters")
    print("═" * 70)
    print()

    # Load game data
    print("Loading game data...")
    game_data = GameData.load_all()

    # Initialize roster
    roster = CharacterRoster()

    # Characters to create
    characters = [
        ('MaxF', 'Fighter'),
        ('MaxC', 'Cleric'),
        ('MaxM', 'Magic-User'),
        ('MaxT', 'Thief')
    ]

    created_ids = []

    for name, char_class in characters:
        print(f"\nCreating {name} ({char_class}, Level 10)...")

        # Create character
        character = create_max_character(name, char_class, game_data)

        # Save to roster
        char_id = roster.save_character(character)
        created_ids.append((name, char_class, char_id))

        print(f"✓ Created {name}:")
        print(f"  - Level: {character.level}")
        print(f"  - HP: {character.hp_current}/{character.hp_max}")
        print(f"  - THAC0: {character.thac0}")
        print(f"  - AC: {character.ac}")
        print(f"  - STR: {character.strength}{f'/{character.strength_percentile}' if character.strength_percentile else ''}")
        print(f"  - XP: {character.xp:,}")

        if char_class in ['Cleric', 'Magic-User']:
            print(f"  - Spells Known: {len(character.spells_known)}")
            print(f"  - Spell Slots: {len(character.spells_memorized)}")

    print()
    print("═" * 70)
    print("✓ All characters created successfully!")
    print("═" * 70)
    print()
    print("Character IDs:")
    for name, char_class, char_id in created_ids:
        print(f"  {name} ({char_class}): {char_id}")
    print()
    print("You can now:")
    print("  1. Create a party with these characters using the Party Manager")
    print("  2. Use them to test high-level content (spells, combat, etc.)")
    print()


if __name__ == '__main__':
    main()
