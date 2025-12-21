#!/usr/bin/env python3
"""
Script to manually complete Episode 4 for campaign 329dac52-01e2-4bba-bfa0-0355b31d8ae8

This fixes the bug where episode completion in-dungeon didn't save the campaign file.
The XP and level-ups were already applied during gameplay, but the campaign state wasn't persisted.

This applies:
- Marks episode 4 as complete in campaign
- Unlocks episode 5 and Mires Edge hub
- Sets story flags: second_key_found, duergar_defeated, dwarven_alliance
- Updates reputation: dwarves_ironfast +50
- Clears the active session

Run from aerthos directory: python3 scripts/complete_episode_04.py
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
HOME = Path.home()
AERTHOS_DIR = HOME / '.aerthos'
CAMPAIGN_FILE = AERTHOS_DIR / 'campaigns' / '329dac52-01e2-4bba-bfa0-0355b31d8ae8.json'
SESSION_FILE = AERTHOS_DIR / 'sessions' / 'session_episode_329dac52-01e2-4bba-bfa0-0355b31d8ae8_episode_04_1766281320669.json'

# Episode 4 Rewards (from episode_04.json)
XP_BONUS = 7500
GOLD_BONUS = 400
UNLOCKS_EPISODES = ['episode_05']
UNLOCKS_HUBS = ['mires_edge']
STORY_FLAGS = ['second_key_found', 'duergar_defeated', 'dwarven_alliance']
REPUTATION_CHANGES = {'dwarves_ironfast': 50}


def main():
    print("=" * 70)
    print("EPISODE 4 COMPLETION SCRIPT")
    print("The Dwarven Distress - Campaign File Fix")
    print("=" * 70)
    print()
    print("This script fixes the bug where episode completion during gameplay")
    print("didn't save the campaign file. XP and level-ups were already applied.")
    print()

    # Verify files exist
    if not CAMPAIGN_FILE.exists():
        print(f"ERROR: Campaign file not found: {CAMPAIGN_FILE}")
        return False

    # Load campaign
    with open(CAMPAIGN_FILE, 'r') as f:
        campaign = json.load(f)

    print(f"Campaign: {campaign['name']}")
    print(f"Current Episode: {campaign['current_episode_id']}")
    print(f"Completed Episodes: {campaign['completed_episodes']}")
    print(f"Unlocked Episodes: {campaign['unlocked_episodes']}")
    print(f"Unlocked Hubs: {campaign['unlocked_hubs']}")
    print()

    # Check if already completed
    if 'episode_04' in campaign['completed_episodes']:
        print("Episode 04 is already marked as completed!")
        print("No changes needed.")
        return True

    print("=" * 70)
    print("UPDATING CAMPAIGN")
    print("=" * 70)
    print()

    # Mark episode complete
    campaign['completed_episodes'].append('episode_04')
    print(f"  + Added 'episode_04' to completed_episodes")

    # Unlock new episodes
    for ep_id in UNLOCKS_EPISODES:
        if ep_id not in campaign['unlocked_episodes']:
            campaign['unlocked_episodes'].append(ep_id)
            print(f"  + Unlocked episode: {ep_id}")

    # Unlock new hubs
    for hub_id in UNLOCKS_HUBS:
        if hub_id not in campaign['unlocked_hubs']:
            campaign['unlocked_hubs'].append(hub_id)
            print(f"  + Unlocked hub: {hub_id}")

    # Set story flags
    for flag in STORY_FLAGS:
        campaign['story_flags'][flag] = True
        print(f"  + Set story flag: {flag}")

    # Update reputation
    for faction, change in REPUTATION_CHANGES.items():
        old_rep = campaign['reputation'].get(faction, 0)
        campaign['reputation'][faction] = old_rep + change
        print(f"  + Reputation with {faction}: {old_rep} -> {old_rep + change}")

    # Update current episode (ready for next)
    campaign['current_episode_id'] = 'episode_05'
    print(f"  + Set current_episode_id to 'episode_05'")

    # Update current hub
    campaign['current_hub_id'] = 'mires_edge'
    print(f"  + Set current_hub_id to 'mires_edge'")

    # Clear active session
    campaign['active_session_id'] = None
    print(f"  + Cleared active_session_id")

    # Update last played
    campaign['last_played'] = datetime.now().isoformat()

    # Save campaign
    with open(CAMPAIGN_FILE, 'w') as f:
        json.dump(campaign, f, indent=2)
    print()
    print(f"  Saved campaign to: {CAMPAIGN_FILE}")

    # Update session file to mark as inactive
    if SESSION_FILE.exists():
        with open(SESSION_FILE, 'r') as f:
            session = json.load(f)
        session['is_active'] = False
        with open(SESSION_FILE, 'w') as f:
            json.dump(session, f, indent=2)
        print(f"  Marked session as inactive: {SESSION_FILE.name}")

    print()
    print("=" * 70)
    print("EPISODE 4 COMPLETE!")
    print("=" * 70)
    print()
    print("Grathak falls, his body fading to ash as the dark magic sustaining")
    print("him dissipates. The remaining duergar flee into the deep tunnels,")
    print("driven back by dwarven reinforcements.")
    print()
    print("In Grathak's chamber, you find a massive iron key inscribed with")
    print("serpent runes - 'The Second Key,' according to the cult's records.")
    print()
    print("Commander Thrain surveys the reclaimed hold: 'We've won today, but")
    print("at great cost. Take the key, warn the other settlements. Ironfast")
    print("Outpost stands with you against this darkness.'")
    print()
    print("=" * 70)
    print("CAMPAIGN STATE UPDATED")
    print("=" * 70)
    print(f"  Completed Episodes: {campaign['completed_episodes']}")
    print(f"  Unlocked Episodes: {campaign['unlocked_episodes']}")
    print(f"  Unlocked Hubs: {campaign['unlocked_hubs']}")
    print(f"  Current Hub: {campaign['current_hub_id']}")
    print(f"  Next Episode: {campaign['current_episode_id']}")
    print()
    print("You may now start Episode 5 from the campaign menu!")
    print("=" * 70)

    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
