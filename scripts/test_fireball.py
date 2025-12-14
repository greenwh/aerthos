#!/usr/bin/env python3
"""
Quick test for Fireball spell implementation
"""

import sys
from pathlib import Path

# Add aerthos to path
sys.path.insert(0, str(Path(__file__).parent))

from aerthos.engine.game_state import GameData
from aerthos.ui.character_creation import CharacterCreator
from aerthos.systems.magic import MagicSystem
from aerthos.entities.monster import Monster


def main():
    print("=" * 70)
    print("FIREBALL SPELL TEST")
    print("=" * 70)
    print()

    # Load game data
    game_data = GameData.load_all()

    # Create a test Magic-User at level 10
    creator = CharacterCreator(game_data)
    mage = creator.quick_create("TestMage", "Human", "Magic-User")
    mage.level = 10  # Set to level 10

    # Give the mage Fireball spell
    fireball_data = game_data.spells['fireball']
    from aerthos.entities.player import Spell
    fireball = Spell(
        name=fireball_data['name'],
        level=fireball_data['level'],
        school=fireball_data['school'],
        casting_time=fireball_data['casting_time'],
        range=fireball_data['range'],
        duration=fireball_data['duration'],
        area_of_effect=fireball_data['area'],
        saving_throw=fireball_data['saving_throw'],
        components=fireball_data['components'],
        description=fireball_data['description'],
        class_availability=fireball_data['class_availability']
    )

    # Add spell to known spells and memorize it
    mage.spells_known.append(fireball)
    mage.add_spell_slot(3)  # Level 3 spell slot
    mage.memorize_spell(fireball)

    print(f"Caster: {mage.name} (Level {mage.level} Magic-User)")
    print(f"Spell: {fireball.name} (Level {fireball.level})")
    print(f"Expected Damage: 10d6 (10-60 damage, save for half)")
    print()

    # Create some target monsters
    goblin_data = game_data.monsters.get('goblin', {})
    targets = [
        Monster(
            name=f"Goblin {i+1}",
            race="Goblin",
            char_class="Monster",
            level=1,
            strength=11,
            dexterity=12,
            constitution=10,
            intelligence=8,
            wisdom=8,
            charisma=6,
            hp_current=7,
            hp_max=7,
            ac=6,
            thac0=20,
            save_poison=14,
            save_rod_staff_wand=16,
            save_petrify_paralyze=15,
            save_breath=17,
            save_spell=17
        )
        for i in range(5)
    ]

    print("Targets:")
    for t in targets:
        print(f"  - {t.name} (HP: {t.hp_current}, AC: {t.ac}, Spell Save: {t.save_spell})")
    print()

    # Cast Fireball
    magic_system = MagicSystem()
    print("Casting Fireball...")
    print()

    result = magic_system.cast_spell(mage, "Fireball", targets)

    print("-" * 70)
    if result['success']:
        print("✓ CAST SUCCESSFUL!")
        print()
        print(result['narrative'])
        print()
        print("-" * 70)
        print()
        print("Effect Results:")
        for key, value in result['effect_results'].items():
            print(f"  {key}: {value}")
        print()
        print("Surviving Targets:")
        for t in targets:
            if t.is_alive:
                print(f"  - {t.name} (HP: {t.hp_current}/{t.hp_max})")
            else:
                print(f"  - {t.name} (DEAD)")
    else:
        print("✗ CAST FAILED!")
        print(result['narrative'])

    print()
    print("=" * 70)
    print("✓ TEST COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
