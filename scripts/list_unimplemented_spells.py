#!/usr/bin/env python3
"""
List all unimplemented spells organized by class and level
"""

import json
from pathlib import Path
from collections import defaultdict

# List of implemented spell handlers from magic.py
IMPLEMENTED_SPELLS = {
    'sleep', 'magic_missile', 'cure_light_wounds', 'cure_serious_wounds',
    'cure_critical_wounds', 'protection_from_evil', 'detect_magic',
    'burning_hands', 'charm_person', 'fireball', 'lightning_bolt',
    'cone_of_cold', 'heal', 'haste', 'slow', 'bless', 'web',
    'hold_person', 'invisibility', 'knock', 'find_traps', 'cloudkill',
    'chain_lightning', 'raise_dead', 'spiritual_hammer', 'prayer',
    'flame_strike', 'blade_barrier', 'ice_storm', 'disintegrate',
    'light', 'silence_15_radius', 'continual_light', 'locate_object',
    'clairvoyance', 'dispel_magic', 'dimension_door', 'teleport',
    'shield', 'enlarge', 'reduce', 'strength', 'slow_poison',
    'polymorph_self', 'polymorph_other', 'shocking_grasp', 'color_spray',
    'stinking_cloud', 'mirror_image', 'wall_of_fire', 'wall_of_ice',
    'cure_disease', 'cure_blindness', 'neutralize_poison', 'regenerate',
    'blur', 'barkskin'
}

def normalize_spell_name(name):
    """Convert spell name to handler key format"""
    return name.lower().replace(' ', '_').replace('-', '_')

def main():
    # Load spells.json
    project_root = Path(__file__).parent.parent
    spells_file = project_root / 'aerthos' / 'data' / 'spells.json'

    with open(spells_file, 'r') as f:
        all_spells = json.load(f)

    # Find unimplemented spells
    unimplemented = {}

    for spell_key, spell_data in all_spells.items():
        normalized_key = normalize_spell_name(spell_key)

        if normalized_key not in IMPLEMENTED_SPELLS:
            unimplemented[spell_key] = spell_data

    # Organize by class and level
    by_class = defaultdict(lambda: defaultdict(list))

    for spell_key, spell_data in unimplemented.items():
        level = spell_data.get('level', 0)
        classes = spell_data.get('class_availability', [])

        for char_class in classes:
            by_class[char_class][level].append({
                'key': spell_key,
                'name': spell_data.get('name', spell_key),
                'description': spell_data.get('description', 'No description'),
                'school': spell_data.get('school', 'unknown')
            })

    # Generate report
    output_file = project_root / 'unimplemented_spells.txt'

    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("AERTHOS - UNIMPLEMENTED SPELLS BY CLASS AND LEVEL\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total Spells: {len(all_spells)}\n")
        f.write(f"Implemented: {len(IMPLEMENTED_SPELLS)}\n")
        f.write(f"Unimplemented: {len(unimplemented)}\n\n")

        f.write("=" * 80 + "\n\n")

        # Sort classes alphabetically
        for char_class in sorted(by_class.keys()):
            f.write(f"\n{'='*80}\n")
            f.write(f"{char_class.upper()}\n")
            f.write(f"{'='*80}\n\n")

            levels = by_class[char_class]

            # Sort by level
            for level in sorted(levels.keys()):
                spells = levels[level]

                f.write(f"\nLevel {level} Spells ({len(spells)} unimplemented):\n")
                f.write("-" * 80 + "\n\n")

                # Sort spells alphabetically within each level
                for spell in sorted(spells, key=lambda x: x['name']):
                    f.write(f"  • {spell['name']} ({spell['school']})\n")
                    f.write(f"    {spell['description']}\n\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")

    print(f"Report generated: {output_file}")
    print(f"\nSummary:")
    print(f"  Total Spells: {len(all_spells)}")
    print(f"  Implemented: {len(IMPLEMENTED_SPELLS)}")
    print(f"  Unimplemented: {len(unimplemented)}")
    print(f"\nUnimplemented spells by class:")
    for char_class in sorted(by_class.keys()):
        total = sum(len(spells) for spells in by_class[char_class].values())
        print(f"  {char_class}: {total}")

if __name__ == "__main__":
    main()
