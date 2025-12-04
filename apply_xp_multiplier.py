#!/usr/bin/env python3
"""
Apply 5x XP multiplier to all monsters and episode bonuses
"""

import json
import glob

MULTIPLIER = 5

print("=" * 80)
print("APPLYING 5X XP MULTIPLIER")
print("=" * 80)
print()

# Step 1: Update monster XP values
print("Step 1: Updating monster XP values...")
with open('aerthos/data/monsters.json', 'r') as f:
    monsters = json.load(f)

monsters_updated = 0
for monster_id, monster_data in monsters.items():
    if 'xp_value' in monster_data:
        old_xp = monster_data['xp_value']
        new_xp = old_xp * MULTIPLIER
        monster_data['xp_value'] = new_xp
        monsters_updated += 1

        if monsters_updated <= 5:  # Show first 5 as examples
            print(f"  {monster_id}: {old_xp} XP → {new_xp} XP")

print(f"  ... (showing first 5)")
print(f"✅ Updated {monsters_updated} monsters")
print()

# Save updated monsters
with open('aerthos/data/monsters.json', 'w') as f:
    json.dump(monsters, f, indent=2)

# Step 2: Update episode completion bonuses
print("Step 2: Updating episode completion bonuses...")
episode_files = sorted(glob.glob('aerthos/data/episodes/episode_*.json'))

episodes_updated = 0
for episode_file in episode_files:
    with open(episode_file, 'r') as f:
        episode = json.load(f)

    if 'rewards' in episode and 'xp_bonus' in episode['rewards']:
        old_bonus = episode['rewards']['xp_bonus']
        new_bonus = old_bonus * MULTIPLIER
        episode['rewards']['xp_bonus'] = new_bonus
        episodes_updated += 1

        episode_num = episode_file.split('_')[-1].replace('.json', '')
        print(f"  Episode {episode_num}: {old_bonus} XP → {new_bonus} XP")

        # Save updated episode
        with open(episode_file, 'w') as f:
            json.dump(episode, f, indent=2)

print(f"✅ Updated {episodes_updated} episodes")
print()

print("=" * 80)
print("XP MULTIPLIER APPLICATION COMPLETE")
print("=" * 80)
print()
print(f"✅ {monsters_updated} monsters updated (XP × {MULTIPLIER})")
print(f"✅ {episodes_updated} episode bonuses updated (XP × {MULTIPLIER})")
print()
print("Next step: Re-run XP analysis to verify changes")
print("  python3 analyze_xp.py")
