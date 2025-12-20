#!/usr/bin/env python3
"""
Script to manually complete Episode 3 for campaign 329dac52-01e2-4bba-bfa0-0355b31d8ae8

This applies:
- 5000 XP to each party member
- 300 gold to party leader (Grim)
- Level-ups for characters who qualify
- Marks episode 3 as complete in campaign
- Unlocks episode 4 and Ironfast Outpost hub
- Sets story flags

Run from aerthos directory: python3 scripts/complete_episode_03.py
"""

import json
import random
from pathlib import Path
from datetime import datetime

# Paths
HOME = Path.home()
AERTHOS_DIR = HOME / '.aerthos'
CAMPAIGN_FILE = AERTHOS_DIR / 'campaigns' / '329dac52-01e2-4bba-bfa0-0355b31d8ae8.json'
SESSION_FILE = AERTHOS_DIR / 'sessions' / 'session_episode_329dac52-01e2-4bba-bfa0-0355b31d8ae8_episode_03_1766194415497.json'
PARTY_FILE = AERTHOS_DIR / 'parties' / 'guardians_c0dd5d91.json'
CHARACTERS_DIR = AERTHOS_DIR / 'characters'

# Character files (id -> filename)
CHARACTER_FILES = {
    'c1658b4c': 'grim_c1658b4c.json',
    'ba7be2d2': 'valorian_ba7be2d2.json',
    '54a51250': 'eryndor_54a51250.json',
    '469a5593': 'canon_469a5593.json',
    'f8ddd970': 'aether_f8ddd970.json',
    '93cc8188': 'pip_93cc8188.json'
}

# XP Tables (from level_progression.json)
XP_TABLES = {
    'Fighter': [0, 2000, 4000, 8000, 18000, 35000, 70000, 125000, 250000, 500000],
    'Paladin': [0, 2750, 5500, 12000, 24000, 45000, 95000, 175000, 350000, 700000],
    'Ranger': [0, 2250, 4500, 10000, 20000, 40000, 90000, 150000, 225000, 325000],
    'Cleric': [0, 1500, 3000, 6000, 13000, 27500, 55000, 110000, 225000, 450000],
    'Magic-User': [0, 2500, 5000, 10000, 22500, 40000, 60000, 90000, 135000, 250000],
    'Thief': [0, 1250, 2500, 5000, 10000, 20000, 42500, 70000, 110000, 160000]
}

# Hit dice for HP on level up
HIT_DICE = {
    'Fighter': 10,
    'Paladin': 10,
    'Ranger': 8,
    'Cleric': 8,
    'Magic-User': 4,
    'Thief': 6
}

# Episode 3 Rewards
XP_BONUS = 5000
GOLD_BONUS = 300

def roll_dice(sides):
    """Roll a die"""
    return random.randint(1, sides)

def check_level_up(char_class, current_level, xp):
    """Check if character qualifies for level up and return new level"""
    if char_class not in XP_TABLES:
        return current_level

    xp_table = XP_TABLES[char_class]
    new_level = current_level

    # Check each level
    while new_level < len(xp_table) - 1:
        xp_needed = xp_table[new_level]  # XP needed for next level
        if xp >= xp_needed:
            new_level += 1
        else:
            break

    return new_level

def level_up_character(char_data, old_level, new_level):
    """Apply level up bonuses to character"""
    char_class = char_data.get('class', 'Fighter')
    hit_die = HIT_DICE.get(char_class, 8)

    messages = []
    total_hp_gain = 0

    for level in range(old_level + 1, new_level + 1):
        hp_roll = roll_dice(hit_die)
        # Add CON modifier
        con_mod = 0
        con = char_data.get('con', 10)
        if con >= 15:
            con_mod = 1
        elif con >= 16:
            con_mod = 2
        elif con >= 17:
            con_mod = 3
        elif con >= 18:
            con_mod = 4

        hp_gain = max(1, hp_roll + con_mod)  # Minimum 1 HP
        total_hp_gain += hp_gain
        messages.append(f"  Level {level}: +{hp_gain} HP (rolled {hp_roll} + {con_mod} CON)")

    return total_hp_gain, messages

def main():
    print("=" * 70)
    print("EPISODE 3 COMPLETION SCRIPT")
    print("The Merchant's Secret - Manual Completion")
    print("=" * 70)
    print()

    # Verify files exist
    if not CAMPAIGN_FILE.exists():
        print(f"ERROR: Campaign file not found: {CAMPAIGN_FILE}")
        return
    if not SESSION_FILE.exists():
        print(f"ERROR: Session file not found: {SESSION_FILE}")
        return

    # Load campaign
    with open(CAMPAIGN_FILE, 'r') as f:
        campaign = json.load(f)

    print(f"Campaign: {campaign['name']}")
    print(f"Current Episode: {campaign['current_episode_id']}")
    print(f"Completed Episodes: {campaign['completed_episodes']}")
    print()

    # Check if already completed
    if 'episode_03' in campaign['completed_episodes']:
        print("WARNING: Episode 03 is already marked as completed!")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return

    # Load session
    with open(SESSION_FILE, 'r') as f:
        session = json.load(f)

    print("=" * 70)
    print("APPLYING REWARDS")
    print("=" * 70)
    print()
    print(f"XP Bonus: {XP_BONUS} per character")
    print(f"Gold Bonus: {GOLD_BONUS} gp (to party leader)")
    print()

    level_up_results = []

    # Process each character
    for i, (char_id, filename) in enumerate(CHARACTER_FILES.items()):
        char_file = CHARACTERS_DIR / filename
        if not char_file.exists():
            print(f"WARNING: Character file not found: {char_file}")
            continue

        with open(char_file, 'r') as f:
            char_data = json.load(f)

        name = char_data['name']
        char_class = char_data.get('class', 'Fighter')
        old_level = char_data['level']
        old_xp = char_data['xp']

        # Add XP
        new_xp = old_xp + XP_BONUS
        char_data['xp'] = new_xp

        # Check for level up
        new_level = check_level_up(char_class, old_level, new_xp)

        print(f"{name} ({char_class}):")
        print(f"  XP: {old_xp} → {new_xp}")

        if new_level > old_level:
            hp_gain, messages = level_up_character(char_data, old_level, new_level)
            char_data['level'] = new_level
            char_data['hp_max'] = char_data.get('hp_max', 10) + hp_gain
            char_data['hp_current'] = char_data.get('hp_current', 10) + hp_gain

            # Update THAC0 based on class
            thac0_improvement = new_level - old_level
            if char_class in ['Fighter', 'Paladin', 'Ranger']:
                char_data['thac0'] = max(1, char_data.get('thac0', 20) - thac0_improvement)
            else:
                # Other classes improve THAC0 every 2 levels
                char_data['thac0'] = max(1, char_data.get('thac0', 20) - (thac0_improvement // 2))

            print(f"  ✨ LEVEL UP! {old_level} → {new_level}")
            print(f"  HP: {char_data['hp_max'] - hp_gain} → {char_data['hp_max']} (+{hp_gain})")
            print(f"  THAC0: {char_data['thac0']}")
            for msg in messages:
                print(msg)

            level_up_results.append(f"{name} leveled up to {new_level}!")
        else:
            print(f"  Level: {old_level} (no change)")

        # Add gold to party leader (first character)
        if i == 0:
            old_gold = char_data.get('gold_pieces', 0)
            char_data['gold_pieces'] = old_gold + GOLD_BONUS
            print(f"  Gold: {old_gold} → {char_data['gold_pieces']} gp (+{GOLD_BONUS})")

        # Save character
        with open(char_file, 'w') as f:
            json.dump(char_data, f, indent=2)

        print()

    # Update session party state
    party_members = session.get('party_state', {}).get('members', [])
    for member in party_members:
        name = member['name']
        # Find matching character file
        for char_id, filename in CHARACTER_FILES.items():
            char_file = CHARACTERS_DIR / filename
            if char_file.exists():
                with open(char_file, 'r') as f:
                    char_data = json.load(f)
                if char_data['name'] == name:
                    member['xp'] = char_data['xp']
                    member['level'] = char_data['level']
                    member['hp_current'] = char_data['hp_current']
                    if name == 'Grim':
                        member['gold_pieces'] = char_data['gold_pieces']
                    break

    # Save session
    session['is_active'] = False  # Mark as completed
    with open(SESSION_FILE, 'w') as f:
        json.dump(session, f, indent=2)

    # Update campaign
    print("=" * 70)
    print("UPDATING CAMPAIGN")
    print("=" * 70)
    print()

    # Mark episode complete
    if 'episode_03' not in campaign['completed_episodes']:
        campaign['completed_episodes'].append('episode_03')

    # Unlock episode 4
    if 'episode_04' not in campaign['unlocked_episodes']:
        campaign['unlocked_episodes'].append('episode_04')

    # Unlock Ironfast Outpost hub
    if 'ironfast_outpost' not in campaign['unlocked_hubs']:
        campaign['unlocked_hubs'].append('ironfast_outpost')

    # Set story flags
    campaign['story_flags']['silas_captured'] = True
    campaign['story_flags']['oakhaven_secured'] = True
    campaign['story_flags']['cult_conspiracy_revealed'] = True

    # Clear active session
    campaign['active_session_id'] = None
    campaign['current_episode_id'] = None  # Ready to select next episode

    # Update last played
    campaign['last_played'] = datetime.now().isoformat()

    # Save campaign
    with open(CAMPAIGN_FILE, 'w') as f:
        json.dump(campaign, f, indent=2)

    print(f"Completed Episodes: {campaign['completed_episodes']}")
    print(f"Unlocked Episodes: {campaign['unlocked_episodes']}")
    print(f"Unlocked Hubs: {campaign['unlocked_hubs']}")
    print(f"Story Flags: silas_captured, oakhaven_secured, cult_conspiracy_revealed")
    print()

    # Print completion message
    print("=" * 70)
    print("EPISODE 3 COMPLETE!")
    print("=" * 70)
    print()
    print("Silas falls, wounded but alive. As the town guard takes him into")
    print("custody, he laughs—a bitter, hollow sound.")
    print()
    print("'You think you've won?' he rasps. 'You've merely cut off one finger.")
    print("The Serpent has many more. The cult spans all of Aerthos. Oakhaven")
    print("was just a test. The real work happens in the mountains, the marshes,")
    print("the cities. The ten keys are almost gathered. When the Serpent")
    print("awakens, your pitiful heroics will mean nothing.'")
    print()
    print("Searching his warehouse, you find ledgers documenting shipments to")
    print("multiple locations: Ironfast Outpost in the Shattered Peaks, Mire's")
    print("Edge in the Whispering Marshes, even the capital city of Eldoria.")
    print("The cult's reach is vast.")
    print()
    print("Oakhaven is saved, but the true threat has only just revealed itself.")
    print("You must leave this frontier town and pursue the cult to its sources.")
    print()
    print("=" * 70)
    print("REWARDS SUMMARY")
    print("=" * 70)
    print(f"  • XP Bonus: {XP_BONUS} (each party member)")
    print(f"  • Gold: {GOLD_BONUS} gp (Grim)")
    print(f"  • Unlocked: Episode 4 - Into the Mountains")
    print(f"  • Unlocked: Ironfast Outpost (new hub)")
    print()
    if level_up_results:
        print("LEVEL UPS:")
        for result in level_up_results:
            print(f"  ✨ {result}")
    print()
    print("You may now start Episode 4 from the campaign menu!")
    print("=" * 70)

if __name__ == '__main__':
    main()
