#!/usr/bin/env python3
"""
Fix Episode 2 Completion

This script applies the Episode 2 completion rewards that were missed due to
the episode completion trigger bug. It:
1. Marks episode_02 as complete in the campaign
2. Applies XP bonus (3750) to all living party members
3. Applies gold bonus (150) split among party
4. Adds the mace_plus_1 reward item
5. Updates story flags
6. Unlocks episode_03
7. Checks for and applies level ups
"""

import json
from pathlib import Path
from datetime import datetime

# Configuration
CAMPAIGN_ID = "329dac52-01e2-4bba-bfa0-0355b31d8ae8"
AERTHOS_DIR = Path.home() / ".aerthos"

# Episode 2 rewards from episode_02.json
REWARDS = {
    "xp_bonus": 3750,
    "gold_bonus": 150,
    "items": ["mace_plus_1"],
    "unlocks": ["episode_03"],
    "story_flags": ["rescued_prisoners", "found_cult_evidence", "silas_implicated"]
}

# XP tables for level calculation (from level_progression.json)
XP_TABLES = {
    "Fighter": [0, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000],
    "Cleric": [0, 1500, 3000, 6000, 13000, 27500, 55000, 110000, 225000, 450000],
    "Magic-User": [0, 2500, 5000, 10000, 22500, 40000, 60000, 90000, 135000, 250000],
    "Thief": [0, 1250, 2500, 5000, 10000, 20000, 40000, 70000, 110000, 160000],
    "Ranger": [0, 2250, 4500, 9000, 18000, 36000, 75000, 150000, 300000, 600000],
    "Paladin": [0, 2750, 5500, 12000, 24000, 45000, 95000, 175000, 350000, 700000],
    "Druid": [0, 2000, 4000, 7500, 12500, 20000, 35000, 60000, 90000, 125000],
    "Illusionist": [0, 2250, 4500, 9000, 18000, 35000, 60000, 95000, 145000, 220000],
    "Assassin": [0, 1500, 3000, 6000, 12000, 25000, 50000, 100000, 200000, 300000],
    "Monk": [0, 2250, 4750, 10000, 22500, 47500, 98000, 200000, 350000, 500000],
    "Bard": [0, 2000, 4000, 8000, 16000, 25000, 40000, 60000, 85000, 110000]
}

# Hit dice for HP on level up
HIT_DICE = {
    "Fighter": 10, "Ranger": 8, "Paladin": 10,
    "Cleric": 8, "Druid": 8,
    "Magic-User": 4, "Illusionist": 4,
    "Thief": 6, "Assassin": 6, "Monk": 4, "Bard": 6
}

# THAC0 progression per level
THAC0_PROGRESSION = {
    "Fighter": -1, "Ranger": -1, "Paladin": -1,
    "Cleric": -0.67, "Druid": -0.67, "Bard": -0.67,
    "Magic-User": -0.33, "Illusionist": -0.33,
    "Thief": -0.5, "Assassin": -0.5, "Monk": -0.5
}


def get_level_for_xp(char_class: str, xp: int) -> int:
    """Calculate level based on XP and class"""
    table = XP_TABLES.get(char_class, XP_TABLES["Fighter"])
    level = 1
    for i, threshold in enumerate(table):
        if xp >= threshold:
            level = i + 1
        else:
            break
    return min(level, 10)  # Cap at level 10


def roll_dice(sides: int) -> int:
    """Roll a die"""
    import random
    return random.randint(1, sides)


def apply_level_up(char_data: dict, old_level: int, new_level: int) -> list:
    """Apply level up benefits and return messages"""
    messages = []
    char_class = char_data.get("class", "Fighter")

    for level in range(old_level + 1, new_level + 1):
        messages.append(f"  ✨ LEVEL UP! Now level {level}!")

        # HP gain
        hit_die = HIT_DICE.get(char_class, 6)
        hp_gain = roll_dice(hit_die)

        # CON bonus
        con = char_data.get("constitution", 10)
        if con >= 15:
            con_bonus = (con - 14) // 2
            hp_gain += con_bonus
        elif con <= 6:
            hp_gain = max(1, hp_gain - 1)

        char_data["hp_max"] = char_data.get("hp_max", 10) + hp_gain
        char_data["hp_current"] = char_data.get("hp_current", 10) + hp_gain
        messages.append(f"     HP: +{hp_gain} (now {char_data['hp_max']})")

        # THAC0 improvement
        progression = THAC0_PROGRESSION.get(char_class, -0.5)
        thac0_progress = char_data.get("thac0_progress", 0.0) + abs(progression)

        if thac0_progress >= 1.0:
            thac0_improvement = int(thac0_progress)
            char_data["thac0"] = char_data.get("thac0", 20) - thac0_improvement
            thac0_progress -= thac0_improvement
            messages.append(f"     THAC0: improved to {char_data['thac0']}")

        char_data["thac0_progress"] = thac0_progress
        char_data["level"] = level

    return messages


def create_mace_plus_1():
    """Create the mace +1 reward item"""
    return {
        "name": "Mace +1",
        "type": "weapon",
        "weight": 10.0,
        "damage_sm": "1d6",
        "damage_l": "1d6",
        "speed_factor": 7,
        "magic_bonus": 1,
        "properties": {
            "xp_value": 400,
            "gp_value": 2000
        },
        "description": "A magical mace with a +1 enchantment. Recovered from the cult's ritual chamber."
    }


def main():
    print("=" * 70)
    print("EPISODE 2 COMPLETION FIX")
    print("Applying missed rewards from 'The Cult Below'")
    print("=" * 70)

    # Load campaign
    campaign_file = AERTHOS_DIR / "campaigns" / f"{CAMPAIGN_ID}.json"
    with open(campaign_file) as f:
        campaign = json.load(f)

    print(f"\nCampaign: {campaign['name']}")
    print(f"Party ID: {campaign['party_id']}")

    # Update campaign state
    print("\n--- Updating Campaign State ---")

    if "episode_02" not in campaign["completed_episodes"]:
        campaign["completed_episodes"].append("episode_02")
        print("✓ Added episode_02 to completed_episodes")

    if "episode_03" not in campaign["unlocked_episodes"]:
        campaign["unlocked_episodes"].append("episode_03")
        print("✓ Unlocked episode_03")

    campaign["current_episode_id"] = "episode_03"
    print("✓ Set current episode to episode_03")

    # Add story flags
    for flag in REWARDS["story_flags"]:
        campaign["story_flags"][flag] = True
        print(f"✓ Added story flag: {flag}")

    campaign["last_played"] = datetime.now().isoformat()

    # Save campaign
    with open(campaign_file, 'w') as f:
        json.dump(campaign, f, indent=2)
    print("\n✓ Campaign file updated")

    # Load and update each character
    print("\n--- Applying Character Rewards ---")
    print(f"XP Bonus: {REWARDS['xp_bonus']} per character")
    print(f"Gold Bonus: {REWARDS['gold_bonus']} (split among party)")

    characters_dir = AERTHOS_DIR / "characters"
    party_members = ["grim", "valorian", "eryndor", "canon", "aether", "pip"]

    gold_per_member = REWARDS["gold_bonus"] // len(party_members)
    mace_given = False

    for member_name in party_members:
        # Find character file
        char_files = list(characters_dir.glob(f"{member_name}_*.json"))
        if not char_files:
            print(f"  ✗ Could not find character file for {member_name}")
            continue

        char_file = char_files[0]
        with open(char_file) as f:
            char_data = json.load(f)

        print(f"\n{char_data['name']} ({char_data['class']} level {char_data['level']}):")

        # Record old state
        old_xp = char_data.get("xp", 0)
        old_level = char_data.get("level", 1)

        # Apply XP bonus
        new_xp = old_xp + REWARDS["xp_bonus"]
        char_data["xp"] = new_xp
        print(f"  XP: {old_xp} → {new_xp} (+{REWARDS['xp_bonus']})")

        # Check for level up
        new_level = get_level_for_xp(char_data["class"], new_xp)
        if new_level > old_level:
            level_messages = apply_level_up(char_data, old_level, new_level)
            for msg in level_messages:
                print(msg)

        # Apply gold bonus
        old_gold = char_data.get("gold_pieces", 0)
        char_data["gold_pieces"] = old_gold + gold_per_member
        print(f"  Gold: {old_gold} → {char_data['gold_pieces']} (+{gold_per_member}gp)")

        # Give mace to first cleric (Canon)
        if not mace_given and char_data["class"] == "Cleric":
            mace = create_mace_plus_1()
            if "inventory" not in char_data:
                char_data["inventory"] = []
            char_data["inventory"].append(mace)
            print(f"  🎁 Received: Mace +1")
            mace_given = True

        # Save character
        with open(char_file, 'w') as f:
            json.dump(char_data, f, indent=2)

    # Display completion text
    print("\n" + "=" * 70)
    print("EPISODE 2 COMPLETION TEXT")
    print("=" * 70)
    completion_text = """
The cultist fanatic falls, his dying words a curse against you and a
prayer to the Serpent Eye. The captured townsfolk, emaciated and
terrified, huddle in their cages. You free them and guide them back
to the surface.

Among the cult's ritual chamber, you find disturbing evidence: maps
of the region marked with serpent symbols, letters from someone
called 'The Merchant,' and references to 'the awakening' and 'the
ten keys.' The cult was gathering sacrifices to power some dark
ritual.

You've stopped this cell, but the conspiracy runs deeper. The letters
mention Silas, the merchant whose shop you've been frequenting. Could
he be involved?
"""
    print(completion_text)

    print("=" * 70)
    print("READY FOR EPISODE 3: The Merchant's Secret")
    print("=" * 70)
    print("\nYour party is now positioned at the Oakhaven hub.")
    print("Start Episode 3 to investigate Silas the merchant.")
    print()


if __name__ == "__main__":
    main()
