#!/usr/bin/env python3
"""
Analyze XP progression across all 10 episodes
"""

import json
import os
from pathlib import Path

# XP requirements by class (Level 1-10)
XP_TABLES = {
    'Fighter': [0, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000],
    'Cleric': [0, 1500, 3000, 6000, 13000, 27500, 55000, 110000, 225000, 450000],
    'Magic-User': [0, 2500, 5000, 10000, 22500, 40000, 60000, 90000, 135000, 250000],
    'Thief': [0, 1250, 2500, 5000, 10000, 20000, 40000, 70000, 110000, 160000]
}

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def calculate_dungeon_xp(dungeon_file):
    """Calculate total XP from all monsters in a dungeon"""
    dungeon = load_json(dungeon_file)
    monsters_data = load_json('aerthos/data/monsters.json')

    total_xp = 0
    monster_count = 0

    for room_id, room in dungeon.get('rooms', {}).items():
        for encounter in room.get('encounters', []):
            if encounter.get('type') == 'combat':
                for monster_id in encounter.get('monsters', []):
                    if monster_id in monsters_data:
                        xp = monsters_data[monster_id].get('xp_value', 0)
                        total_xp += xp
                        monster_count += 1
                    else:
                        print(f"  WARNING: Monster '{monster_id}' not found in monsters.json")

    return total_xp, monster_count

def calculate_episode_xp(episode_num):
    """Calculate total XP for an episode (monsters + completion bonus)"""
    # Load episode config
    episode_file = f'aerthos/data/episodes/episode_{episode_num:02d}.json'
    if not os.path.exists(episode_file):
        print(f"Episode {episode_num}: File not found")
        return None

    episode = load_json(episode_file)

    # Get dungeon XP
    dungeon_data = episode.get('dungeon')
    if not dungeon_data:
        print(f"Episode {episode_num}: No dungeon specified")
        return None

    # Dungeon is an object with 'file' field
    dungeon_file_path = dungeon_data.get('file', '')
    dungeon_name = dungeon_data.get('name', 'Unknown')

    # Convert relative path to absolute
    dungeon_file = f'aerthos/data/{dungeon_file_path}'
    if not os.path.exists(dungeon_file):
        print(f"Episode {episode_num}: Dungeon file not found: {dungeon_file}")
        return None

    dungeon_xp, monster_count = calculate_dungeon_xp(dungeon_file)

    # Get completion bonus from rewards
    rewards = episode.get('rewards', {})
    completion_xp = rewards.get('xp_bonus', 0)

    total_xp = dungeon_xp + completion_xp

    return {
        'episode': episode_num,
        'name': episode.get('title', 'Unknown'),
        'dungeon': dungeon_name,
        'monster_count': monster_count,
        'dungeon_xp': dungeon_xp,
        'completion_xp': completion_xp,
        'total_xp': total_xp,
        'recommended_level': episode.get('recommended_level', 'Unknown')
    }

def main():
    print("=" * 80)
    print("AERTHOS CAMPAIGN - XP PROGRESSION ANALYSIS")
    print("=" * 80)
    print()

    # Analyze each episode
    episodes_xp = []
    for ep in range(1, 11):
        result = calculate_episode_xp(ep)
        if result:
            episodes_xp.append(result)
            print(f"Episode {ep}: {result['name']}")
            print(f"  Dungeon: {result['dungeon']}")
            print(f"  Recommended Level: {result['recommended_level']}")
            print(f"  Monsters: {result['monster_count']}")
            print(f"  Dungeon XP: {result['dungeon_xp']:,}")
            print(f"  Completion XP: {result['completion_xp']:,}")
            print(f"  Total XP: {result['total_xp']:,}")
            print()

    # Calculate cumulative XP
    print("=" * 80)
    print("CUMULATIVE XP PROGRESSION")
    print("=" * 80)
    print()

    cumulative_xp = 0
    for i, ep_data in enumerate(episodes_xp):
        cumulative_xp += ep_data['total_xp']

        # Determine expected level for each class
        levels = {}
        for char_class, xp_table in XP_TABLES.items():
            for level, xp_needed in enumerate(xp_table[1:], start=2):
                if cumulative_xp < xp_needed:
                    levels[char_class] = level - 1
                    break
            else:
                levels[char_class] = 10  # Max level

        print(f"After Episode {ep_data['episode']}: {cumulative_xp:,} XP")
        print(f"  Fighter: Level {levels['Fighter']}")
        print(f"  Cleric: Level {levels['Cleric']}")
        print(f"  Magic-User: Level {levels['Magic-User']}")
        print(f"  Thief: Level {levels['Thief']}")
        print()

    # Analysis summary
    print("=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print()
    print(f"Total Campaign XP: {cumulative_xp:,}")
    print()
    print("Expected Progression (Level 1 → 10):")
    print(f"  Fighter needs: {XP_TABLES['Fighter'][9]:,} XP")
    print(f"  Cleric needs: {XP_TABLES['Cleric'][9]:,} XP")
    print(f"  Magic-User needs: {XP_TABLES['Magic-User'][9]:,} XP")
    print(f"  Thief needs: {XP_TABLES['Thief'][9]:,} XP")
    print()

    # Check if progression is balanced
    slowest_class = 'Fighter'  # Needs most XP
    xp_needed = XP_TABLES[slowest_class][9]

    if cumulative_xp < xp_needed:
        deficit = xp_needed - cumulative_xp
        print(f"⚠️  XP DEFICIT: {deficit:,} XP short for {slowest_class} to reach level 10")
        print(f"   Campaign provides: {cumulative_xp:,}")
        print(f"   Fighter needs: {xp_needed:,}")
        print(f"   Shortfall: {(deficit / xp_needed * 100):.1f}%")
    elif cumulative_xp > xp_needed * 1.5:
        surplus = cumulative_xp - xp_needed
        print(f"⚠️  XP SURPLUS: {surplus:,} XP over minimum for level 10")
        print(f"   Campaign provides: {cumulative_xp:,}")
        print(f"   Fighter needs: {xp_needed:,}")
        print(f"   Surplus: {(surplus / xp_needed * 100):.1f}%")
    else:
        print("✅ XP PROGRESSION: Balanced for all classes to reach level 10")

    print()

if __name__ == '__main__':
    main()
